"""E15 (D59): project-management model profiles chosen per estimate file.

DRAFT_NEEDS_LEGAL_REVIEW: content written from the names of the frameworks only (no clause numbers are quoted, because the
source texts are not in this repository). CC1 legal/PMO must review before any official use. A REFERENCE dataset named
'Mô hình QLDA CC1' in the data library, once loaded, replaces these built-in drafts.

PMI models (user decision 21/10/2026, D71): PMBOK 6 and PMBOK 8 — PMBOK 7 is NOT used. PMBOK 6 content is the well-known
process structure (5 process groups × 10 knowledge areas, 49 processes). The PMBOK 8 text is not in this repository: its
basis/stages/roles/procurement methods are left [CẦN BỔ SUNG] (content NEEDS_SOURCE) instead of being guessed; the gate asks
for them before a package can rely on the model.
"""
RETIRED={'PMBOK7_ISO21502':'PMBOK 7 / ISO 21502 — không dùng nữa (người dùng chọn PMBOK 6 và PMBOK 8, 21/10/2026)'}
NEEDS='[CẦN BỔ SUNG từ văn bản PMBOK 8 chính thức]'
import json
STATUS='DRAFT_NEEDS_LEGAL_REVIEW'
def _c(code,stage,name,check):return {'code':code,'stage':stage,'name':name,'check':check}
COMMON=[_c('HS-01','Lập dự toán','Hồ sơ dự án (pháp nhân, hợp đồng, kỳ giá, căn cứ)','step0'),_c('HS-02','Lập dự toán','BOQ AB nguyên trạng có mã băm','step1'),
        _c('HS-03','Lập dự toán','WBS/kết quả công việc/LBS gắn mọi dòng BOQ','step2'),_c('HS-04','Lập dự toán','Định mức + hao phí có căn cứ','step4'),
        _c('HS-05','Lập dự toán','Đơn giá có căn cứ, kỳ, vùng giá','step5'),_c('HS-06','Lập dự toán','CBS và tổng dự toán đủ','step6'),
        _c('GT-01','Giao thầu','Kế hoạch gói thầu con (phạm vi, hình thức giao thầu)','packages'),_c('GT-02','Giao thầu','Phủ khối lượng AB = Σ BB + CC1 tự làm','coverage'),
        _c('GT-03','Giao thầu','Báo giá nhà thầu phụ + thẩm định','quotes'),_c('GT-04','Giao thầu','Đề xuất giao thầu + giá giao có lý do','award'),
        _c('TH-01','Thực hiện','Khối lượng hoàn thành theo dòng BB/WBS có căn cứ','progress')]
MODELS={
 'VN_ND175':{'name':'Việt Nam — Luật Xây dựng, NĐ 175/2024/NĐ-CP, Luật Đấu thầu 2023','family':'VN',
   'basis':'Luật Xây dựng (sửa đổi), Nghị định 175/2024/NĐ-CP về quản lý hoạt động xây dựng, Luật Đấu thầu số 22/2023/QH15; chi phí theo TT36/37/38/2026 như hồ sơ đang dùng. Luật Đấu thầu ràng buộc khi gói dùng vốn nhà nước; giao thầu phụ của CC1 theo quy chế nội bộ và hợp đồng chính.',
   'stages':['Chuẩn bị dự án','Thực hiện dự án (thiết kế, lựa chọn nhà thầu, thi công)','Kết thúc xây dựng, bàn giao đưa vào sử dụng'],
   'roles':['Chủ đầu tư','Ban QLDA/Tư vấn QLDA','Tư vấn giám sát','Nhà thầu chính (CC1)','Nhà thầu phụ'],
   'procurement_methods':{'CHI_DINH_THAU':'Chỉ định thầu','CHAO_HANG_CANH_TRANH':'Chào hàng cạnh tranh','DAU_THAU_HAN_CHE':'Đấu thầu hạn chế','DAU_THAU_RONG_RAI':'Đấu thầu rộng rãi','NOI_BO':'Giao nội bộ / đơn vị thành viên'},
   'change':'Điều chỉnh, phát sinh khối lượng theo hợp đồng và quy định quản lý chi phí','measurement':'Nghiệm thu khối lượng hoàn thành theo hạng mục/WBS, thanh toán theo hợp đồng',
   'checklist':COMMON+[_c('VN-01','Thực hiện','Biên bản nghiệm thu khối lượng nhà thầu phụ theo WBS','progress'),_c('VN-02','Giao thầu','Mô hình QLDA đã chọn cho hồ sơ','pm_model')]},
 'FIDIC_RED':{'name':'FIDIC Red Book (Conditions of Contract for Construction)','family':'FIDIC',
   'basis':'Hợp đồng thi công do Chủ đầu tư thiết kế; đo lường lại khối lượng thực tế theo BOQ.',
   'stages':['Đấu thầu (Tender)','Trao hợp đồng (Contract award)','Thi công (Construction)','Nghiệm thu bàn giao (Taking-over)','Thời hạn thông báo sai sót (Defects notification period)'],
   'roles':['Chủ đầu tư (Employer)','Kỹ sư (Engineer)','Nhà thầu (Contractor, CC1)','Nhà thầu phụ (Subcontractor)'],
   'procurement_methods':{'DOMESTIC':'Nhà thầu phụ do nhà thầu chọn (Domestic subcontractor; cần chấp thuận khi hợp đồng yêu cầu)','NOMINATED':'Nhà thầu phụ được chỉ định (Nominated subcontractor; Chủ đầu tư/Kỹ sư chỉ định)'},
   'change':'Thay đổi (Variation) theo chỉ dẫn của Kỹ sư','measurement':'Đo lại khối lượng (Re-measurement) theo BOQ, thanh toán tạm (interim payment) theo khối lượng đo',
   'checklist':COMMON+[_c('FD-01','Giao thầu','Danh sách nhà thầu phụ và phạm vi (để xin chấp thuận khi cần)','packages'),_c('FD-02','Giao thầu','Mô hình QLDA đã chọn cho hồ sơ','pm_model')]},
 'FIDIC_YELLOW':{'name':'FIDIC Yellow Book (Plant and Design-Build)','family':'FIDIC',
   'basis':'Hợp đồng thiết kế-thi công; giá trọn gói theo mốc/lịch thanh toán (schedule of payments) là chủ yếu.',
   'stages':['Đấu thầu (Tender)','Trao hợp đồng (Contract award)','Thiết kế (Design)','Thi công (Construction)','Thử nghiệm khi hoàn thành (Tests on completion)','Nghiệm thu bàn giao (Taking-over)','Thời hạn thông báo sai sót (Defects notification period)'],
   'roles':['Chủ đầu tư (Employer)','Kỹ sư (Engineer)','Nhà thầu (Contractor, CC1, gồm thiết kế)','Nhà thầu phụ (Subcontractor)'],
   'procurement_methods':{'DOMESTIC':'Nhà thầu phụ do nhà thầu chọn (Domestic subcontractor)','NOMINATED':'Nhà thầu phụ được chỉ định (Nominated subcontractor)'},
   'change':'Thay đổi (Variation) / tối ưu giá trị (value engineering)','measurement':'Trọn gói (lump sum) theo lịch thanh toán / mốc',
   'checklist':COMMON+[_c('FY-01','Giao thầu','Mô hình QLDA đã chọn cho hồ sơ','pm_model')]},
 'PRINCE2':{'name':'PRINCE2 (quản lý theo giai đoạn)','family':'PRINCE2',
   'basis':'Quản lý theo giai đoạn, luận chứng kinh doanh (business case) liên tục, quản lý theo ngoại lệ với dung sai (tolerances); nhà thầu phụ nhận gói công việc (Work Package).',
   'stages':['Khởi động dự án (Starting up a project)','Khởi tạo dự án (Initiating a project)','Kiểm soát giai đoạn / Quản lý bàn giao sản phẩm (Controlling a stage / Managing product delivery)','Quản lý chuyển giai đoạn (Managing a stage boundary)','Kết thúc dự án (Closing a project)'],
   'roles':['Ban dự án (Project Board: Executive, Senior User, Senior Supplier)','Giám đốc dự án (Project Manager)','Trưởng nhóm thực hiện (Team Manager, nhà thầu phụ)','Đảm bảo dự án (Project Assurance)'],
   'procurement_methods':{'WORK_PACKAGE':'Giao gói công việc (Work Package) cho Trưởng nhóm thực hiện','COMPETITIVE':'Chọn cạnh tranh','DIRECT':'Giao trực tiếp'},
   'change':'Kiểm soát vấn đề/thay đổi (Issue/Change control), dung sai theo giai đoạn','measurement':'Báo cáo điểm kiểm tra (Checkpoint report) / nghiệm thu theo sản phẩm theo WBS',
   'checklist':COMMON+[_c('P2-01','Giao thầu','Mô hình QLDA đã chọn cho hồ sơ','pm_model')]},
 'PMBOK6':{'name':'PMBOK Guide 6th Edition (PMI) — quản lý theo quy trình','family':'PMI','content':'DRAFT',
   'basis':'5 nhóm quy trình × 10 lĩnh vực kiến thức (49 quy trình). Đường cơ sở phạm vi (Scope baseline) = tuyên bố phạm vi + WBS + từ điển WBS; đường cơ sở chi phí (cost baseline) và quản lý giá trị thu được (EVM); mua sắm theo Plan / Conduct / Control Procurements; thay đổi qua Perform Integrated Change Control.',
   'stages':['Khởi tạo (Initiating)','Lập kế hoạch (Planning)','Thực hiện (Executing)','Giám sát và kiểm soát (Monitoring and Controlling)','Kết thúc (Closing)'],
   'knowledge_areas':['Tích hợp (Integration)','Phạm vi (Scope)','Tiến độ (Schedule)','Chi phí (Cost)','Chất lượng (Quality)','Nguồn lực (Resource)','Truyền thông (Communications)','Rủi ro (Risk)','Mua sắm (Procurement)','Bên liên quan (Stakeholder)'],
   'roles':['Nhà tài trợ dự án (Project Sponsor)','Giám đốc dự án (Project Manager)','PMO','Hội đồng kiểm soát thay đổi (Change Control Board, CCB)','Người phụ trách tài khoản kiểm soát chi phí (Control Account Manager, CAM)','Bên bán (Seller) / nhà thầu phụ'],
   'procurement_methods':{'LEAST_COST':'Giá thấp nhất (Least cost)','QUALIFICATIONS_ONLY':'Chỉ theo năng lực (Qualifications only)',
     'QUALITY_BASED':'Theo chất lượng / điểm kỹ thuật cao nhất (Quality-based / highest technical proposal score)','QUALITY_AND_COST':'Kết hợp kỹ thuật và giá (Quality and cost-based)',
     'SOLE_SOURCE':'Nguồn duy nhất (Sole source)','FIXED_BUDGET':'Ngân sách cố định (Fixed budget)'},
   'contract_types':{'FFP':'Giá cố định trọn gói (Firm Fixed Price)','FPIF':'Giá cố định có thưởng khuyến khích (Fixed Price Incentive Fee)','FP_EPA':'Giá cố định có điều chỉnh giá (Fixed Price with Economic Price Adjustment)',
     'CPFF':'Chi phí cộng phí cố định (Cost Plus Fixed Fee)','CPIF':'Chi phí cộng phí khuyến khích (Cost Plus Incentive Fee)','CPAF':'Chi phí cộng phí thưởng (Cost Plus Award Fee)','TM':'Theo thời gian và vật tư (Time and Material)'},
   'change':'Kiểm soát thay đổi tích hợp (Perform Integrated Change Control): yêu cầu thay đổi → CCB → cập nhật đường cơ sở và kế hoạch',
   'measurement':'Giá trị thu được (Earned Value: PV, EV, AC; CV, SV, CPI, SPI) theo tài khoản kiểm soát chi phí/WBS; xác nhận phạm vi (Validate Scope) để nghiệm thu sản phẩm bàn giao',
   'checklist':COMMON+[_c('PM6-01','Giao thầu','Mô hình QLDA đã chọn cho hồ sơ','pm_model')]},
 'PMBOK8':{'name':'PMBOK Guide 8th Edition (PMI)','family':'PMI','content':'NEEDS_SOURCE',
   'basis':NEEDS+' — văn bản PMBOK 8 chưa có trong kho dữ liệu; không suy diễn nội dung.',
   'stages':[NEEDS],'roles':[NEEDS],
   'procurement_methods':{},
   'change':NEEDS,'measurement':NEEDS,
   'checklist':COMMON+[_c('PM8-01','Giao thầu','Mô hình QLDA đã chọn cho hồ sơ','pm_model')]},
}
for _m in MODELS.values():_m['status']=STATUS
def models(store=None):
    """Active library dataset 'Mô hình QLDA CC1' (rows: {code, json}) if loaded, else the built-in drafts."""
    if store is not None:
        for d in store.library_list():
            if d['kind']=='REFERENCE' and d['status']=='ACTIVE' and d['name'].startswith('Mô hình QLDA CC1'):
                out={}
                for r in store.library_rows(d['id']):
                    try:m=json.loads(r['json']) if isinstance(r.get('json'),str) else r.get('json')
                    except ValueError:continue
                    if isinstance(m,dict) and r.get('code'):out[r['code']]=dict(m,status=m.get('status') or STATUS,dataset=d['id'])
                if out:return out
    return MODELS
def checklist(s,model,stages,sub=None):
    """Evaluate a model checklist against the project: DONE / MISSING per document."""
    done={f'step{i}':st['confirmed'] for i,st in enumerate(stages)}
    pk=s.get('packages') or [];sub=sub or {}
    done.update(packages=bool(pk),coverage=bool(pk) and (sub.get('coverage') or {}).get('UNDER',1)==0 and (sub.get('coverage') or {}).get('OVER',1)==0 and (sub.get('coverage') or {}).get('INVALID',1)==0,
                quotes=bool(s.get('quotes')),award=any(p.get('award') for p in pk),progress=bool(s.get('progress')),pm_model=bool(s['context'].get('pm_model')))
    return [dict(c,state='DONE' if done.get(c['check']) else 'MISSING') for c in model.get('checklist',[])]
