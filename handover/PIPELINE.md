# Pipeline EPSMS — Chặng 2, 16/10/2026

1. Input JSON đã khai báo → `epsms.py validate` → kiểm schema/graph/template.
2. `generate` → revisions/r000001/{input,template,structures,dictionary,validation,changes,CSV,report,manifest}; brief dùng `execute` và planner trước generate.
3. `verify` → checksum, graph, deterministic replay. `update` tạo revision mới; không sửa run cũ.
4. Adapter report local (gap Chặng 4) → WBS/COST_MAPPING/SOURCES theo DoD và Excel snapshot. Không ghi ngược ERP hoặc input JSON.
5. AC checks và report gap → sample mapping → package DRAFT + biên nhận chưa ký. Nghiệp vụ/pháp lý/ERP/owner chưa đủ evidence giữ BLOCKED.

## Môi trường đã kiểm

- Python 3.12.10 trong `.venv`, đáp ứng Python 3.10+ của core. Venv đã có từ bước tiếp nhận, không tạo lại.
- Core chỉ dùng stdlib. Report Excel dùng openpyxl 3.1.5 đã cài sẵn, pin trong `requirements.txt`; kiểm import thành công, không cần mạng.
- Dùng `-X utf8 -B`, `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`. Không cần activate, không đổi execution policy.
- Xuất Office gốc là optional: python-docx/Node/@oai/artifact-tool; adapter Excel local dùng openpyxl thay cho nhánh đó. Word không nằm trong DoD. Không tuyên bố nhánh Office gốc đã được setup/chạy.
- PDF intake Chặng 1 đã dùng PyMuPDF trong Python hệ thống; Chặng 2–5 dùng inventory đã pin, không cần cài package hoặc parse lại nguồn pháp lý.

## Lệnh chạy chính xác từ handover

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
.venv/Scripts/python.exe -X utf8 -B current_executor/epsms.py validate runs_brian/sim_pilot/run_01/inputs/sim_bridge_r2_cr01.json
.venv/Scripts/python.exe -X utf8 -B current_executor/epsms.py generate runs_brian/sim_pilot/run_01/inputs/sim_bridge_r2_cr01.json --out runs_brian/v1
.venv/Scripts/python.exe -X utf8 -B current_executor/epsms.py verify --out runs_brian/v1
```

Thư mục output phải mới. Demo check: `execute current_executor/examples/bridge_brief.json --out runs_brian/demo_check`, rồi `verify` và so revision với `current_executor/demo_runs/bridge_brief`. Chặng 4 sẽ bổ sung lệnh adapter đã triển khai, không giả định core tự xuất schema DoD.

## Trạng thái và giới hạn

`FILE_ERRORS.json=[]` là không có lỗi kiểm kê được ghi, không phải AC toàn bộ đạt. BL09/BL12 đã có fix; bản source hiện tại được pin bằng hash trong run. BL01/03/04/05/06/07/08 còn phụ thuộc owner/nguồn thật/nghiệm thu.

Core chưa có hierarchical display code đúng A04, export theo 58 field của DoD, mapping norm/price có xác nhận, kiểm mọi AC hay package final. Chặng 3 đo gap trước sửa. Input hiện chọn là SIM-BRIDGE-01 theo D11, không giả định là dự án thật.

Kiểm toàn gói lịch sử: `python verify_package.py <ZIP>` cần ZIP chưa có ở thư mục cha; không tự fetch hoặc tái tạo ZIP 49GB để đánh PASS. Nguồn mới đã có nhưng chọn mã, vùng/kỳ, hiệu lực và quyền dùng cần review. Các phần này được báo BLOCKED, không bịa mapping.

Kit binding hiện có, Python native adapter của kit còn thiếu; dùng các lệnh test thật trong README. Không coi kit self-test là app test. Chỉ localhost, không push/deploy/mạng ngoài.

## Adapter đã triển khai ở Chặng 4

```powershell
.venv/Scripts/python.exe -X utf8 -B current_executor/epsms.py generate runs_brian/sim_pilot/run_01/inputs/sim_bridge_r2_cr01.json --out runs_brian/v3
.venv/Scripts/python.exe -X utf8 -B current_executor/epsms.py verify --out runs_brian/v3
.venv/Scripts/python.exe -X utf8 -B runs_brian/wbs_report.py --run runs_brian/v3 --out runs_brian/v3/report --boq runs_brian/sim_pilot/run_01/inputs/sim_boq_r2_cr01.json
.venv/Scripts/python.exe -X utf8 -B runs_brian/test_wbs_report.py
```

v3 đã tồn tại; khi chạy lại chọn v4/report mới và giữ v2 để chạy regression tests đã pin. Adapter chỉ nhận synthetic fixture, không phải giao diện ERP; các output mang status SYNTHETIC. Mẫu Excel 30 dòng và snapshot workbook không có công thức thực thi từ chuỗi nguồn. Không có claim đã render/kiểm Excel native mới; QA hiện là schema/value parity và kiểm cell/formula, giao diện cần Brian review.
