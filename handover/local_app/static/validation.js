'use strict';
// Presentation of server validation only. No client-side business rules or confirmations.
let errorOnly=false;
let validationProjectRef,validationStagesRef,validationCachedIssues=[];
let validationTargets=new WeakMap();
const validationSteps={context:0,boq:1,wbs:2,mapping:2,assign:3,norms:3,applications:3,resources:4,prices:5,adjustments:6,rules:6,export:7};
function validationIssues(){if(validationProjectRef!==project||validationStagesRef!==stages){validationProjectRef=project;validationStagesRef=stages;validationTargets=new WeakMap();validationCachedIssues=stages.flatMap(s=>(s.questions||[]).map((q,n)=>({...q,origin:s.step,key:s.step+'-'+n})));}return validationCachedIssues;}
function validationTarget(q){
 if(validationTargets.has(q))return validationTargets.get(q);
 const path=q.field||'';let g,idx=-1,field='',m;
 if((m=path.match(/^adjustments\.rules\[(\d+)\](?:\.(.+))?$/))){g='rules';idx=+m[1];field=m[2]||'';}
 else if((m=path.match(/^(\w+)\[(\d+)\](?:\.(.+))?$/))){g=m[1];idx=+m[2];field=m[3]||'';}
 else if(path.startsWith('mapping.')){g='assign';idx=project.mapping.findIndex(r=>path.startsWith('mapping.'+r.id+'.'));if(idx>=0)field=path.slice(('mapping.'+project.mapping[idx].id+'.').length);}
 else if(path.startsWith('prices.')){g='prices';field='';}
 else {const parts=path.split('.');g=parts[0];field=parts.slice(1).join('.');}
 if(g==='resources'&&path==='resources'&&q.question.startsWith('Xác nhận bảng hao phí'))return {g,idx:-1,field:'resource_completeness_ref',step:4,special:true};
 const target={g,idx,field,step:validationSteps[g]??q.origin};validationTargets.set(q,target);return target;
}
function validationRowIssues(g,i){return validationIssues().filter(q=>{const t=validationTarget(q);return t.g===g&&t.idx===i||(g==='prices'&&q.field==='prices.'+project.prices[i]?.resource_code);});}
function validationRowHasError(g,i){return validationRowIssues(g,i).length>0;}
function validationSummary(){
 validationStagesRef=null; // Rebuild once for this render, including in-memory QA/state refreshes.
 const qs=stages[step]?.questions||[],waiting=dirty?' · CÓ THAY ĐỔI CHƯA KIỂM TRA LẠI':'';
 $('#question-title').textContent=(qs.length?qs.length+' điểm CHƯA ĐẠT':'Không còn lỗi đầu vào')+waiting;
 $('#questions').innerHTML=(dirty?'<p class="validation-pending" role="status">Đã sửa dữ liệu. Bấm Lưu nháp để máy chủ kiểm tra lại; đánh dấu đỏ đang theo lần kiểm tra gần nhất.</p>':'')+(qs.length?qs.map((q,n)=>`<div class="question validation-question"><strong>! CHƯA ĐẠT</strong><p>${esc(q.question)}</p><code>${esc(q.field)}</code><button class="issue-jump quiet" data-issue="${step}-${n}">Đến chỗ cần sửa →</button></div>`).join(''):`<div class="good">✓ ${stages[step]?.confirmed?'Đã xác nhận trên máy.':'Đầu vào không còn lỗi. Bấm xác nhận để tiếp tục.'}</div>`);
 document.querySelectorAll('[data-issue]').forEach(b=>b.onclick=()=>validationJump(b.dataset.issue));
 validationDecorate();
}
function validationDecorate(){
 const content=$('#stage-content');if(!content)return;
 content.querySelectorAll('.field-error-text,.row-error-text,.validation-group-notice').forEach(e=>e.remove());
 content.querySelectorAll('[aria-invalid]').forEach(e=>{e.removeAttribute('aria-invalid');e.removeAttribute('aria-describedby');});
 content.querySelectorAll('.validation-invalid').forEach(e=>e.classList.remove('validation-invalid'));
 const all=validationIssues();
 content.querySelectorAll('[data-field]').forEach(el=>{
  const g=el.dataset.group,i=+el.dataset.index,f=el.dataset.field;
  const qs=all.filter(q=>{const t=validationTarget(q);return t.g===g&&t.idx===i&&t.field===f;});
  if(!qs.length)return;
  if(el.classList.contains('cell')){el.setAttribute('aria-invalid','true');el.classList.add('cell-invalid');el.title=qs.map(q=>q.question).join(' · ');return;}  // D81 quick-edit cell: mark only, the text goes with the detail form
  const id=el.id+'-error';el.setAttribute('aria-invalid','true');el.setAttribute('aria-describedby',id);const lb=el.closest('label');if(lb)lb.classList.add('validation-invalid');
  el.insertAdjacentHTML('afterend',`<span class="field-error-text" id="${esc(id)}">! ${qs.map(q=>esc(q.question)).join('<br>')}</span>`);
 });
 const completeness=$('#completeness');const completenessIssues=all.filter(q=>validationTarget(q).special);
 if(completeness&&completenessIssues.length){completeness.setAttribute('aria-invalid','true');completeness.setAttribute('aria-describedby','completeness-error');completeness.closest('label').classList.add('validation-invalid');completeness.insertAdjacentHTML('afterend','<span id="completeness-error" class="field-error-text">! '+completenessIssues.map(q=>esc(q.question)).join('<br>')+'</span>');}
 content.querySelectorAll('[data-validation-row]').forEach(tr=>{const i=+tr.dataset.validationRow,qs=validationRowIssues(group(),i);tr.classList.toggle('validation-row-error',qs.length>0);if(qs.length){tr.title=qs.map(q=>q.question).join('\n');tr.querySelector('td').insertAdjacentHTML('beforeend',`<span class="row-error-text">! ${qs.length} lỗi</span>`);}});
 content.querySelectorAll('[data-sub]').forEach(b=>{const count=all.filter(q=>validationTarget(q).g===b.dataset.sub).length;b.classList.toggle('validation-tab-error',count>0);if(count)b.insertAdjacentHTML('beforeend',`<span class="row-error-text">! ${count}</span>`);});
 const g=group(),broad=all.filter(q=>{const t=validationTarget(q);return t.g===g&&t.idx<0&&!t.field&&!t.special;});
 if(broad.length){const host=content.querySelector('.table-wrap')||content;host.insertAdjacentHTML('beforebegin',`<div class="validation-group-notice" tabindex="-1">${broad.map(q=>'<p>! '+esc(q.question)+'</p>').join('')}</div>`);}
 if(selected>=0){const wide=validationRowIssues(g,selected).filter(q=>!validationTarget(q).field);const editor=content.querySelector('.editor');if(editor&&wide.length)editor.insertAdjacentHTML('afterbegin','<div class="row-error-text">'+wide.map(q=>'! '+esc(q.question)).join('<br>')+'</div>');}
 const state=$('#stage-state'),current=stages[step];state.classList.toggle('validation-state-error',!!current?.questions.length);state.textContent=dirty?'CHỜ KIỂM TRA LẠI':current?.questions.length?'CHƯA ĐẠT · '+current.questions.length+' ĐIỂM':current?.confirmed?'ĐÃ XÁC NHẬN TRÊN MÁY':'ĐỦ ĐẦU VÀO · CHỜ XÁC NHẬN';
 document.querySelectorAll('#steps [data-step]').forEach(b=>{const s=stages[+b.dataset.step];b.querySelector('.validation-step-count')?.remove();b.classList.toggle('validation-step-error',s.available&&s.questions.length>0);if(s.questions.length)b.insertAdjacentHTML('beforeend',`<small class="validation-step-count">${s.available?'! '+s.questions.length+' lỗi':'Chờ bước trước'}</small>`);});
}
async function validationJump(key){
 try{
  const q=validationIssues().find(x=>x.key===key);if(!q)return;
  if(dirty)await save(false);
  const t=validationTarget(q);if(!stages[t.step]?.available){message('Cần xác nhận các bước trước khi sửa phần này.',true);return;}
  step=t.step;if(subs[step])sub[step]=t.g;search='';errorOnly=false;selected=t.idx;page=t.idx<0?0:Math.floor(t.idx/15);render();
  const hit=Array.from(document.querySelectorAll('#stage-content [data-field]')).filter(e=>e.dataset.group===t.g&&+e.dataset.index===t.idx&&e.dataset.field===t.field);
  let el=t.special?$('#completeness'):hit.find(e=>!e.classList.contains('cell'))||hit[0];  // D81: the detail form field before the quick cell
  el=el||$('#stage-content .editor')||$('#stage-content .validation-group-notice')||$('#stage-content .toolbar')||$('#stage-content');
  el.scrollIntoView({block:'center',behavior:'instant'});if(!el.matches('input,select,textarea,button'))el.tabIndex=-1;el.focus({preventScroll:true});
  message(q.question,true);
 }catch(e){message(e.message,true);}
}
document.addEventListener('change',e=>{if(e.target.closest('#stage-content')&&(e.target.matches('[data-field]')||e.target.id==='completeness'))queueMicrotask(()=>validationSummary());});
