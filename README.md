# CC1 — App dự toán local và bộ thiết kế quản trị WBS–CBS (bản công khai)

*Bản công khai, đóng gói ngày 26/10/2026 từ workspace dự án số hóa dự toán CC1.*

> **Phạm vi bản công khai:** repo chỉ gồm **mã nguồn app**, **tài liệu thiết kế** và **văn bản pháp lý đã công bố**. Đã loại bỏ hợp đồng AB/BB′, PAKD, BM02 phân khai, dữ liệu xuất từ ERP, CSDL làm việc và mọi dữ liệu dự án thật. Không có file nào ở đây là hồ sơ đã phát hành hay phê duyệt định mức hoặc giá.

## 1. Nội dung

| Đường dẫn | Nội dung |
|---|---|
| [`handover/local_app/`](handover/local_app/) | **App dự toán chạy local** (Python, cổng 8765). Luồng **BOQ → WBS/mã liên quan → định mức TT38 → hao phí → đơn giá → CBS → dự toán → chia thầu AB/BB′ → PAKD**. Mỗi bước có câu hỏi và server gate; thiếu input thì không đi tiếp. Hướng dẫn chi tiết: [`local_app/README.md`](handover/local_app/README.md) |
| `handover/runs_brian/…` | Một số dữ liệu tham chiếu mà app cần để chạy: từ điển bộ mã (`dictionary.json`), chỉ mục TT38 (`tt38-index.json`), thư viện mã TT38 dạng Excel |
| [`CC1_WBS_CBS_Bo_tai_lieu_trien_khai.md`](CC1_WBS_CBS_Bo_tai_lieu_trien_khai.md) | Bộ tài liệu thiết kế quản trị tích hợp WBS/CBS/OBS/RBS/PBS/LBS: governance, RACI, control account, EVM, quy trình hợp đồng đến bàn giao, ERD, tích hợp ERP/PMIS/BIM |
| `handover/01`–`04`, `06` | Mục tiêu và phạm vi, cấu trúc WBS/CBS, kiến trúc EA3, yêu cầu đơn giá/định mức, tiêu chí nghiệm thu |
| `handover/PIPELINE.md`, `RUNBOOK_WBS.md`, `DoD_WBS.md` | Quy trình, runbook, Definition of Done |
| [`docs/index.html`](docs/index.html) | **Từ điển bộ mã CC1 V2.3, chạy trên trình duyệt**: tra cứu 36 họ mã, 75 sheet, 358.453 dòng; rà soát và ghi ý kiến phòng ban, lưu offline. Mở trực tuyến: **https://binhho0505.github.io/WBS-SEP-HUAN-Public/**. Bản công khai đã bỏ 4 sheet rà soát hồ sơ thật (`BO_SUNG_V2_1`, `MAP_PAKD_V2_2`, `QS_DUYET_V2_3`, `RA_SOAT_AB_BB`) và che số hợp đồng/tên nhà thầu phụ |
| [`VAN_BAN_PHAP_LY/`](VAN_BAN_PHAP_LY/) | Văn bản pháp lý công khai: Luật Xây dựng 135/2025, Luật Giá 16/2023, Luật Đầu tư công 58/2024, NĐ 206/2026 và 210/2026, TT36/37/38/2026-BXD cùng phụ lục, đính chính, văn bản hợp nhất, đấu thầu |

## 2. Chạy app

Yêu cầu: Windows 10/11, **Python 3.11 hoặc 3.12**. Không cần Node, cloud hay AI key.

```cmd
git clone https://github.com/Binhho0505/WBS-SEP-HUAN-Public.git
cd WBS-SEP-HUAN-Public\handover\local_app
StartApp.cmd
```

Mở **http://127.0.0.1:8765**. Lần chạy đầu, script tạo `.venv` trong `handover/` và cài `openpyxl 3.1.5`. Thư viện AI (`requirements-ai.txt`) là tùy chọn. Nếu cổng bận: `python -X utf8 local_app\server.py --port 8767`. Dừng bằng `StopApp.cmd`. Không mở app ra mạng LAN.

**Giới hạn của bản công khai**
- App khởi động với **CSDL trống**. Thư viện định mức, giá và hồ sơ cần được nạp lại bằng chức năng *Thư viện dữ liệu* (CSV/XLSX).
- Chức năng *nạp snapshot dự án mẫu* (AB/BB/PAKD có sẵn) **không hoạt động**, vì dữ liệu dự án thật đã được loại bỏ.
- Xuất theo mẫu nguồn TPL03 không chạy được, vì mẫu nội bộ không có trong repo.
- Phần bóc khối lượng bản vẽ (CERP-QTO) là dịch vụ riêng, không có trong repo; app dự toán vẫn chạy khi không có nó.
- Một số tài liệu và README nhắc tới thư mục `runs_brian/...` dùng trong quá trình phát triển. Phần lớn các thư mục đó không có trong bản công khai.

Test native: `handover/local_app/test_app.py`. Kịch bản E2E trình duyệt: `browser_*.cjs`.

## 3. Nguyên tắc dữ liệu của app

- Không thay null bằng 0. Ô trống nghĩa là chưa có thông tin.
- Mã định mức TT38 do máy trích từ PDF chỉ là **ứng viên** (`table_verified=false`). QS phải kiểm bảng gốc trước khi dùng.
- Gợi ý mã TT38 cho dòng BOQ chỉ là đề xuất; người lập phải ghi căn cứ chọn.
- Mỗi bước thiếu input sẽ được lưu ở trạng thái OPEN. Sửa input thì các bước phụ thuộc mở lại. App giữ raw/hash, basis, revision và lineage.
- App chỉ hỗ trợ lập và review dự toán ở máy local. App không ghi vào ERP và không thay thế quyền phê duyệt.

## 4. Văn bản pháp lý

Các văn bản trong `VAN_BAN_PHAP_LY/` là bản sao văn bản quy phạm pháp luật đã công bố, chỉ giữ để tham chiếu. Khi áp dụng, luôn đối chiếu bản chính thức mới nhất trên Công báo hoặc cổng thông tin của cơ quan ban hành.
