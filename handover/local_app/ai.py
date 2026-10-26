"""Optional AI assistant: multi-provider, proposal-only (BL31).

AI output is stored as AI_PROPOSAL_NOT_APPLIED outside project state; it never confirms a step, fills a price
or changes a revision. API keys stay in runtime/ai_settings.json (or environment variables) on this machine and
are never returned to the browser, written to backups, exports or audit events.
Claude uses the official Anthropic SDK; other providers use their documented REST endpoints via stdlib.
"""
import json,os,urllib.error,urllib.request
from pathlib import Path
from urllib.parse import urlparse,quote
from domain import STEPS,KEYS,digest,questions
class AIError(Exception):pass
PROVIDERS={
    'anthropic':{'label':'Anthropic · Claude','key_env':'ANTHROPIC_API_KEY','base_url':None,'models':['claude-opus-5-5','claude-sonnet-5-5','claude-haiku-5-5','claude-fable-5-1'],'default_model':'claude-opus-5-5','needs_key':True},
    'openai':{'label':'OpenAI','key_env':'OPENAI_API_KEY','base_url':'https://api.openai.com/v1','models':[],'default_model':None,'needs_key':True},
    'gemini':{'label':'Google · Gemini','key_env':'GEMINI_API_KEY','base_url':'https://generativelanguage.googleapis.com/v1beta','models':[],'default_model':None,'needs_key':True},
    'openai_compatible':{'label':'Tương thích OpenAI (DeepSeek, Mistral, Groq, Azure, LM Studio…)','key_env':None,'base_url':'','models':[],'default_model':None,'needs_key':False},
    'ollama':{'label':'Ollama · chạy trên máy','key_env':None,'base_url':'http://127.0.0.1:11434','models':[],'default_model':None,'needs_key':False},
}
FALLBACK_MODELS={'claude-opus-5-5','claude-opus-5','claude-fable-5-1','claude-sonnet-5-5'}
EFFORT_MODELS=FALLBACK_MODELS|{'claude-haiku-5-5','claude-sonnet-5','claude-fable-5','claude-opus-4-8','claude-opus-4-7','claude-opus-4-6','claude-sonnet-4-6'}
SYSTEM=('Bạn là trợ lý dự toán xây dựng cho CC1 (nhà thầu thi công Việt Nam), hỗ trợ người lập dự toán trong app local '
'theo luồng BOQ → WBS → định mức → hao phí → đơn giá → CBS → dự toán. Trả lời bằng tiếng Việt, giữ thuật ngữ kỹ thuật tiếng Anh.\n'
'Quy tắc bắt buộc:\n- Mọi nội dung bạn đưa ra là ĐỀ XUẤT để người có thẩm quyền kiểm tra; không tuyên bố đã phê duyệt.\n'
'- Không bịa đơn giá, hệ số hao phí, mã định mức TT38, mã Work Result hay căn cứ pháp lý. Nếu dữ liệu đầu vào không có, nói rõ cần QS/owner cung cấp và gợi ý nguồn tra cứu.\n'
'- Không thay giá trị thiếu bằng 0; không cộng các basis khác nhau (AB, BB, PAKD).\n'
'- Khi gợi ý mã định mức, ghi rõ là ứng viên cần kiểm bảng gốc (mã nguyên tử, đơn vị, điều kiện, đủ cột hao phí).\n'
'- Trả lời ngắn gọn, có cấu trúc, chỉ ra field cụ thể (ví dụ applications[0].qty_factor) khi đề xuất sửa.')
def is_loopback(url):
    try:return urlparse(url).hostname in ['127.0.0.1','localhost','::1']
    except ValueError:return False
class Settings:
    def __init__(self,path):self.path=Path(path)
    def load(self):
        try:return json.loads(self.path.read_text(encoding='utf-8'))
        except (FileNotFoundError,json.JSONDecodeError):return {'providers':{},'active':None}
    def save(self,data):
        self.path.parent.mkdir(parents=True,exist_ok=True);tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,self.path)
    def resolved(self,name):
        if name not in PROVIDERS:raise AIError('Nhà cung cấp không được hỗ trợ: '+str(name))
        meta=PROVIDERS[name];saved=self.load()['providers'].get(name,{});key=saved.get('api_key') or (os.environ.get(meta['key_env']) if meta['key_env'] else None)
        return {'name':name,'api_key':key,'key_source':'saved' if saved.get('api_key') else 'env' if key else None,'base_url':(saved.get('base_url') or meta['base_url'] or '').rstrip('/'),'model':saved.get('model') or meta['default_model']}
    def public(self):
        """Provider list for the browser: never includes a key, only whether one is available."""
        data=self.load();out=[]
        for name,meta in PROVIDERS.items():
            r=self.resolved(name);saved=data['providers'].get(name,{})
            out.append({'id':name,'label':meta['label'],'models':meta['models'],'model':r['model'],'saved_models':saved.get('models',[]),'base_url':r['base_url'],'needs_key':meta['needs_key'],'key_set':bool(r['api_key']),'key_source':r['key_source'],'key_hint':('…'+r['api_key'][-4:]) if r['api_key'] and len(r['api_key'])>8 else None,'key_env':meta['key_env'],'external':not is_loopback(r['base_url']) if name!='anthropic' else True})
        return {'providers':out,'active':data.get('active')}
    def update(self,body):
        name=body.get('provider')
        if name not in PROVIDERS:raise AIError('Nhà cung cấp không được hỗ trợ.')
        data=self.load();entry=data['providers'].setdefault(name,{})
        if body.get('clear_key'):entry.pop('api_key',None)
        elif isinstance(body.get('api_key'),str) and body['api_key'].strip():entry['api_key']=body['api_key'].strip()
        if isinstance(body.get('base_url'),str):
            url=body['base_url'].strip()
            if url and urlparse(url).scheme not in ['http','https']:raise AIError('Địa chỉ gốc (Base URL) phải bắt đầu bằng http(s)://')
            if url and urlparse(url).scheme=='http' and not is_loopback(url):raise AIError('Địa chỉ dịch vụ ngoài máy phải dùng https.')
            entry['base_url']=url
        if isinstance(body.get('model'),str):entry['model']=body['model'].strip()[:200]
        if isinstance(body.get('models'),list):entry['models']=[str(m)[:200] for m in body['models'][:300]]
        data['active']=name;self.save(data);return self.public()
def http_json(url,payload=None,headers=None,timeout=120):
    req=urllib.request.Request(url,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json',**(headers or {})},method='GET' if payload is None else 'POST')
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
    except urllib.error.HTTPError as e:
        detail=e.read().decode('utf-8','replace')[:400]
        raise AIError(f'Nhà cung cấp trả lỗi HTTP {e.code}: {detail}')
    except (urllib.error.URLError,TimeoutError,OSError) as e:raise AIError('Không kết nối được nhà cung cấp: '+str(getattr(e,'reason',e)))
def anthropic_client(cfg):
    try:import anthropic
    except ImportError:raise AIError('Chưa cài thư viện anthropic. Chạy: .venv\\Scripts\\python.exe -m pip install -r local_app\\requirements-ai.txt')
    try:return anthropic,(anthropic.Anthropic(api_key=cfg['api_key'],timeout=180.0) if cfg['api_key'] else anthropic.Anthropic(timeout=180.0))
    except anthropic.AnthropicError:raise AIError('Chưa có thông tin xác thực Anthropic: nhập khóa API trong Cài đặt AI, đặt ANTHROPIC_API_KEY hoặc chạy `ant auth login`.')
def call_anthropic(cfg,model,system,user):
    anthropic,client=anthropic_client(cfg)
    kwargs=dict(model=model,max_tokens=16000,system=system,messages=[{'role':'user','content':user}])
    if model in EFFORT_MODELS:kwargs['output_config']={'effort':'medium'}
    try:
        if model in FALLBACK_MODELS:response=client.beta.messages.create(betas=['server-side-fallback-2026-07-01'],fallbacks='default',**kwargs)
        else:response=client.messages.create(**kwargs)
    except anthropic.AuthenticationError:raise AIError('Khóa API Anthropic không hợp lệ.')
    except anthropic.PermissionDeniedError:raise AIError('Khóa API Anthropic không có quyền dùng mô hình này.')
    except anthropic.NotFoundError:raise AIError('Mô hình không tồn tại hoặc không khả dụng: '+model)
    except anthropic.RateLimitError:raise AIError('Anthropic đang giới hạn tốc độ; thử lại sau.')
    except anthropic.BadRequestError as e:raise AIError('Yêu cầu không hợp lệ: '+str(e.message))
    except anthropic.APIStatusError as e:raise AIError(f'Anthropic lỗi {e.status_code}: {e.message}')
    except anthropic.APIConnectionError:raise AIError('Không kết nối được Anthropic API.')
    if response.stop_reason=='refusal':raise AIError('Mô hình từ chối yêu cầu này ('+str(getattr(response.stop_details,'category',None))+').')
    text=''.join(b.text for b in response.content if b.type=='text')
    return text+('\n\n[Cắt ngắn do giới hạn max_tokens]' if response.stop_reason=='max_tokens' else ''),response.model
def models_anthropic(cfg):
    anthropic,client=anthropic_client(cfg)
    try:return [m.id for m in client.models.list(limit=100)]
    except anthropic.AuthenticationError:raise AIError('Khóa API Anthropic không hợp lệ.')
    except (anthropic.APIStatusError,anthropic.APIConnectionError) as e:raise AIError('Không tải được danh sách mô hình: '+str(e))
def bearer(cfg):return {'Authorization':'Bearer '+cfg['api_key']} if cfg['api_key'] else {}
def call_openai(cfg,model,system,user):
    if not cfg['base_url']:raise AIError('Nhập địa chỉ gốc (Base URL) của dịch vụ tương thích OpenAI.')
    d=http_json(cfg['base_url']+'/chat/completions',{'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':user}]},bearer(cfg))
    try:return d['choices'][0]['message']['content'] or '',d.get('model',model)
    except (KeyError,IndexError,TypeError):raise AIError('Phản hồi không đúng định dạng hội thoại (chat completions).')
def models_openai(cfg):
    if not cfg['base_url']:raise AIError('Nhập địa chỉ gốc (Base URL) trước.')
    return sorted(m['id'] for m in http_json(cfg['base_url']+'/models',headers=bearer(cfg),timeout=30).get('data',[]))
def call_gemini(cfg,model,system,user):
    d=http_json(cfg['base_url']+'/models/'+quote(model,safe='')+':generateContent',{'systemInstruction':{'parts':[{'text':system}]},'contents':[{'role':'user','parts':[{'text':user}]}]},{'x-goog-api-key':cfg['api_key'] or ''})
    try:return ''.join(p.get('text','') for p in d['candidates'][0]['content']['parts']),model
    except (KeyError,IndexError,TypeError):raise AIError('Gemini không trả nội dung (có thể bị chặn bởi bộ lọc an toàn).')
def models_gemini(cfg):
    d=http_json(cfg['base_url']+'/models?pageSize=1000',headers={'x-goog-api-key':cfg['api_key'] or ''},timeout=30)
    return sorted(m['name'].split('/',1)[-1] for m in d.get('models',[]) if 'generateContent' in m.get('supportedGenerationMethods',[]))
def call_ollama(cfg,model,system,user):
    d=http_json(cfg['base_url']+'/api/chat',{'model':model,'stream':False,'messages':[{'role':'system','content':system},{'role':'user','content':user}]},timeout=600)
    return d.get('message',{}).get('content',''),model
def models_ollama(cfg):return sorted(m['name'] for m in http_json(cfg['base_url']+'/api/tags',timeout=10).get('models',[]))
CALLERS={'anthropic':call_anthropic,'openai':call_openai,'openai_compatible':call_openai,'gemini':call_gemini,'ollama':call_ollama}
LISTERS={'anthropic':models_anthropic,'openai':models_openai,'openai_compatible':models_openai,'gemini':models_gemini,'ollama':models_ollama}
PRIVATE={'raw','owner','reviewer','prepared_by','checked_by'}
def trim(row):return {k:v for k,v in row.items() if k not in PRIVATE and v not in [None,'']}
def build_prompt(s,step,question,include_rows):
    """Data-minimised prompt: context without personal names, open questions and at most 30 rows of the step."""
    ctx=trim(s['context']);qs=questions(s,step)[:40]
    data=[] if not include_rows else (s['adjustments'].get('rules',[]) if step==6 else [s[KEYS[step]]] if step in [0,7] else s[KEYS[step]])[:30]
    extra={2:{'wbs_occurrences':[trim(w) for w in s['wbs'][:30]]},3:{'applications':[trim(a) for a in s['applications'][:30]]}}.get(step,{}) if include_rows else {}
    user=json.dumps({'project':s['name'],'context':ctx,'step':{'number':step+1,'title':STEPS[step]},'open_questions':qs,'rows_sample':[trim(r) for r in data if isinstance(r,dict)],**extra,'user_question':question},ensure_ascii=False,indent=1)
    return SYSTEM,user
def ask(settings,s,step,provider,model,question,include_rows,consent):
    cfg=settings.resolved(provider);external=provider=='anthropic' or not is_loopback(cfg['base_url'])
    if not model:raise AIError('Chọn mô hình trước khi hỏi.')
    if PROVIDERS[provider]['needs_key'] and not cfg['api_key'] and provider!='anthropic':raise AIError('Chưa có khóa API cho '+PROVIDERS[provider]['label']+' (nhập trong Cài đặt AI hoặc biến môi trường '+str(PROVIDERS[provider]['key_env'])+').')
    if external and consent is not True:raise AIError('Cần xác nhận đồng ý gửi dữ liệu bước này ra dịch vụ AI bên ngoài.')
    if not isinstance(question,str) or not question.strip() or len(question)>4000:raise AIError('Nhập câu hỏi 1–4000 ký tự.')
    system,user=build_prompt(s,step,question.strip(),include_rows is True)
    text,served=CALLERS[provider](cfg,model,system,user)
    return {'text':text,'model':served,'prompt_digest':digest({'system':system,'user':user,'model':model,'provider':provider}),'external':external}
def list_models(settings,provider):
    cfg=settings.resolved(provider);models=LISTERS[provider](cfg)
    settings.update({'provider':provider,'models':models});return models
