# Definition of Done — WBS cầu, v0.1.0

Trạng thái: **DRAFT / READY_FOR_REVIEW**. Chặng 1 định nghĩa tiêu chí, không xác nhận các tiêu chí đã đạt. Phạm vi: business WBS ngành cầu theo D08/D11; không trộn delivery WBS của EPSMS hoặc baseline CCIP/DST. Owner/chuyên gia/người nghiệm thu chưa được bổ nhiệm: OPEN.

## 1. Sản phẩm và định danh

Output Chặng 5: `final/WBS_final.xlsx`, `final/WBS_final.csv`, `final/WBS_final.json`, `final/COST_MAPPING.csv`, `final/SOURCES.csv`, `final/BaoCao_NghiemThu.md`, `final/TOM_TAT_CHO_BRIAN.md`, `final/BienNhan.md` và manifest SHA256. Đây là contract đề xuất, chưa phải các file đã được tạo.

Excel có các sheet WBS, COST_MAPPING, SOURCES, AC_RESULTS. CSV UTF-8, header ổn định, decimal không dùng dấu phân cách hàng nghìn; JSON UTF-8 giữ `null`, số decimal lưu chuỗi để tránh lỗi float. Workbook phải phân biệt dữ liệu giả lập với nguồn thật. Sheet AC_RESULTS dùng đúng sáu cột của bảng AC tại mục 5, không ẩn dữ liệu hay field gửi hệ thống khác.

Grain WBS: một node của một project/revision; khóa `(project_id, revision, node_id)`. Grain COST_MAPPING: một dòng chi phí/hao phí của leaf, khóa `(project_id, revision, mapping_id)`; mapping nhiều-nhiều qua các dòng riêng. Grain SOURCES: một file snapshot/phiên bản, khóa `source_id + sha256`. Một mã nghiệp vụ không phải Odoo record ID.

## 2. Cột và kiểu dữ liệu bắt buộc

Header bắt buộc; `?` là giá trị có thể null nhưng phải kèm trạng thái/ngoại lệ. Ví dụ chỉ minh họa định dạng, không phải dữ liệu công trình thật. Inventory đầy đủ và mapping Odoo: `runs_brian/chang1_20261016/field-mapping.json`.

### WBS

| Cột | Kiểu | Ví dụ / quy tắc |
|---|---|---|
| project_id | string | SIM-BRIDGE-01; mã EPSMS, không phải project.project.id |
| revision | string | r000002 |
| node_id | UUID | ID ổn định, không đổi khi đổi tên |
| parent_id | UUID? | null duy nhất tại root |
| wbs_code | string | 01.02.01; mã trình bày riêng ID |
| level | integer | 1–6, suy từ parent |
| name | string | Kết cấu trụ P1 |
| is_leaf | boolean | true nếu không có child |
| deliverable | string? | Bắt buộc ở leaf |
| acceptance | array[string] | Bắt buộc ở leaf; CSV dùng JSON array trong ô |
| owner_ref | string? | null nếu chưa bổ nhiệm; chặn nghiệm thu nghiệp vụ |
| location_refs | array[string] | Không nhân tiền khi có nhiều location |
| quantity | decimal-string? | null nếu chưa có khối lượng/cơ sở cộng |
| uom | string? | m3; bắt buộc khi quantity có giá trị |
| known_cost | decimal-string | Phần đã biết; 0 không có nghĩa đầy đủ |
| total_cost | decimal-string? | null khi có bất kỳ thành phần bắt buộc thiếu |
| currency | string | VND; không cộng khác tiền tệ chưa có FX pin |
| source_refs | array[string] | ID nguồn, locator nằm ở SOURCES/COST_MAPPING |
| status | enum | DRAFT / SYNTHETIC / REVIEWED / ACCEPTED; không tự cấp ACCEPTED |

### COST_MAPPING

| Cột | Kiểu | Ví dụ / quy tắc |
|---|---|---|
| project_id | string | Như WBS |
| revision | string | Như WBS |
| mapping_id | string | CM-000001 |
| wbs_node_id | UUID | Chỉ tới leaf tồn tại |
| cbs_code | string | MATERIAL; 5 nhóm kỹ thuật, không gọi là phân loại pháp định |
| cost_basis | enum | ESTIMATE / BUDGET / COMMITTED / ACTUAL / PAID / EV; không cộng lẫn |
| norm_code | string? | Mã đọc từ dòng định mức, không tự suy từ tên công tác |
| norm_source_id | string? | NORM-38-PL2-REPLACEMENT |
| norm_locator | string? | PDF page + mã/bảng/dòng/cột |
| price_code | string? | Mã giá từ bảng nguồn |
| price_source_id | string? | PRICE-REGION-PERIOD |
| price_locator | string? | Sheet/row/column hoặc PDF page/table/row |
| quantity | decimal-string? | Theo BOQ, giữ nguồn và đơn vị |
| uom | string? | Không quy đổi ngầm |
| unit_price | decimal-string? | Theo vùng/thời điểm đã chọn |
| amount | decimal-string? | Decimal quantity × unit_price cho dòng giá trực tiếp; hao phí phải có bước phân tích riêng |
| currency | string | VND |
| applicability | enum | CONFIRMED / OPEN / NOT_APPLICABLE; N/A có lý do ở review_note |
| review_note | string? | Lý do chọn/không chọn mã, reviewer/decision ref |

### SOURCES

| Cột | Kiểu | Ví dụ / quy tắc |
|---|---|---|
| source_id | string | NORM-38-PL2-REPLACEMENT |
| path | string | Đường dẫn snapshot hoặc nguồn đã bind |
| sha256 | hex64 | Hash bytes; không thay xác minh nội dung/pháp lý |
| document_no | string? | 38/2026/TT-BXD theo nội dung file |
| version | string | Bản phụ lục thay thế theo CV 9947; không dùng mtime |
| issued_date | ISO-date? | Đọc từ văn bản; chưa chứng thực pháp lý |
| effective_from | ISO-date? | OPEN nếu chưa xác minh; không đoán bằng ngày ban hành |
| effective_to | ISO-date? | null nếu chưa xác minh, không suy vô thời hạn |
| region | string? | Tỉnh/khu vực theo nguồn giá |
| price_period | string? | Tháng/quý/năm của bảng giá |
| source_class | enum | NORM / PRICE / BOQ / CONTRACT / METHOD / CORRECTION / SYNTHETIC |
| approval_status | enum | LOCAL_CANDIDATE / VERIFIED_FOR_SCOPE / OPEN / SUPERSEDED |
| locator | string | Trang/bảng/mục; không chỉ tên thư mục |
| supersedes_ref | string? | Liên kết bản trước; không xóa bản cũ |

## 3. Cây WBS và mã — giả định thiết kế A04 để Brian review

- Đề xuất 3–6 cấp: project → nhóm deliverable → WP; phân rã thêm theo công tác/vị trí khi có căn cứ. Không ép toàn bộ leaf cùng độ sâu, không tạo scope để lấp cây.
- Root `01`; mỗi cạnh thêm một segment hai chữ số `01`–`99`, dấu `.`; tối đa 17 ký tự ở 6 cấp. Pattern `^[0-9]{2}(\.[0-9]{2}){0,5}$`, cấm segment `00`. Hơn 99 child phải thiết kế successor, không tự kéo dài mã.
- Một root/project/revision, không vòng, không orphan, mã không trùng; parent code là prefix trực tiếp, level child = level parent + 1. Không yêu cầu số sibling liền nhau vì mã đã nghỉ phải được bảo toàn.
- Recode có crosswalk/CR, giữ node_id. Quy tắc này là đề xuất output adapter, **chưa phải hành vi code hiện tại**; Chặng 3 phải ghi gap nếu khác.
- Tổng cha = tổng child trực tiếp cùng cost_basis/currency, chỉ cộng mỗi leaf một lần. Quantity chỉ cộng nếu cùng UOM và cùng ý nghĩa đại lượng; khác loại giữ null hoặc bảng riêng, không cộng m3 bê tông với tấn thép. Total thiếu giữ null; known subtotal vẫn đối chiếu được.

## 4. Nguồn mapping định mức/đơn giá

Nguồn mới: `D:/WBS SEP HUAN/ĐINH MUC & DON GIA`. Đã kiểm kê/hash **191 file**, đọc hai trang đầu **113 PDF**; không tuyên bố đã rà toàn bộ nội dung hay xác thực chữ ký số. Inventory/extract tại `runs_brian/chang1_20261016/`.

- NORM-38-PL2-REPLACEMENT: `Phụ lục thay thế/Công văn 9947BXD-VPB ngày 29062026/Phụ lục thay thế TT 38/PL2-TT-38.pdf`, trang 1: Phụ lục II, định mức dự toán xây dựng, kèm TT 38/2026/TT-BXD ngày 26/06/2026 theo bản local.
- METHOD-38: `Cốt lõi/Thông tư 382026TT-BXD/38-bxd.signed.pdf`, trang 1; nội dung file tự ghi TT 38/2026/TT-BXD.
- REPLACEMENT-9947: `Phụ lục thay thế/Công văn 9947BXD-VPB ngày 29062026/CV-9947.pdf`, trang 1, ghi thay thế PL I–VIII của TT38 và PL V của TT36. Bản thay thế là candidate để tra cứu; giữ cả bản gốc để đối chiếu, chưa tự kết luận hiệu lực pháp lý.
- METHOD-36: file `Cốt lõi/Luật Xây dựng số 1352025QH15/36-bxd.signed.pdf` có nội dung TT36; thư mục `Cốt lõi/Thông tư 362026TT-BXD/luat135-2025.pdf` chứa file luật. **Tên folder không khớp loại văn bản**: route theo nội dung/hash, không đổi/xóa nguồn.
- CORRECTION-36: `Đính chính/Quyết định 1538QĐ-BXD ngày 28082026/dinh-chinh-tt36-bxd.signed.pdf`, trang 1; đối chiếu đính chính khi dùng TT36.
- PRICE: đã có bảng giá vật liệu theo nhiều tỉnh/kỳ trong `Bảng giá sở xây dựng/Giá vật liệu/`. Chưa chọn tỉnh/kỳ cho dự án giả lập hoặc thật; không ghép bảng giá khác vùng/ngày tùy ý. Nhân công/máy/thuế/hệ số nếu thiếu vẫn OPEN. ERP exports/giá hợp đồng là nguồn riêng, không mặc nhiên thay bảng công bố hoặc làm định mức.

Mỗi leaf phải liên kết CBS; mỗi dòng có mã định mức/giá hoặc OPEN/N/A có giải thích. Chỉ chốt `CONFIRMED` khi mã, UOM, điều kiện thi công, revision/hiệu lực, địa bàn/kỳ giá và locator đã đối chiếu. Không bắt mọi leaf (quản lý, bàn giao...) phải có một mã định mức giả. Không lấy bảng giá vật liệu làm định mức hao phí. Thử mẫu dùng synthetic basis riêng, không đổi nhãn thành giá thật.

**STOP thiếu toàn bộ nguồn đã được khắc phục ở mức intake/định nghĩa DoD.** Việc áp mã/giá cụ thể và nghiệm thu nguồn chưa hoàn tất; các AC liên quan phải ghi Chưa/BLOCKED tới khi đủ evidence. Không có mâu thuẫn cấu trúc giữa 01/02/04/06 được xác định trong lượt đọc này. Không truy cập mạng để xác nhận pháp lý ở Chặng 1; đây là danh mục nguồn local, không phải tư vấn tuân thủ.

## 5. Tiêu chí nghiệm thu đo được

“Ngưỡng Đạt” là điều kiện tương lai, không phải kết quả phiên này. Tool/script chưa có được ghi là cần triển khai Chặng 3–4. Review thủ công phải có người và decision ref, agent self-check không thay independent review.

| AC-xx | Nguồn 06 / phạm vi | Mô tả | Cách kiểm tra | Ngưỡng Đạt | Evidence bắt buộc |
|---|---|---|---|---|---|
| AC-01 | Nghiệm thu gói | Index, 10 nhóm nội dung, file sửa được, inventory/hash | Script inventory + link check; review 10 nhóm | 10/10 nhóm; 0 broken link/thiếu file bắt buộc | Index + inventory + report |
| AC-02 | G0 | ZIP CRC/SHA256, số file/bytes, snapshot khôi phục | verify_package.py theo CLI thực đọc ở Chặng 2; restore vào thư mục mới | 0 CRC/hash mismatch; count/bytes khớp; restore kiểm hash | Log mới, hash ZIP, manifest; không tái dùng claim cũ |
| AC-03 | G0 | Phạm vi/owner/biên nhận | Review theo 10_BienNhan_Mau | Tất cả trường cần ký được điền/xác nhận có thẩm quyền; ngoại lệ có disposition | Biên nhận version/hash + quyết định |
| AC-04 | G1 | Phân biệt WBS/CBS và 31/35 scope, thiếu/thừa | So expected do chuyên gia lập độc lập | 0 thiếu/thừa chưa có disposition; reviewer xác nhận | Expected/hash + reconciliation + decision |
| AC-05 | G1 + Chặng 1 | Schema/header/type và định dạng final | CSV/JSON validator + đọc Excel + so row/key | 100% required header; 0 key/type mismatch; 3 format cùng dữ liệu | Schema pin + log + workbook QA |
| AC-06 | G1 + Chặng 4 | Cây/mã/ID ổn định | Graph/code checks; test update/crosswalk | 0 duplicate/orphan/cycle/skipped level; đúng mục 3 | Validation và changes/crosswalk |
| AC-07 | G1/G2 | WBS↔CBS/định mức/giá truy vết | Join theo leaf + kiểm source/version/locator/UOM/applicability | 100% leaf có CBS; 100% dòng có disposition; 0 OPEN bắt buộc khi nghiệm thu thật | COST_MAPPING + SOURCES + chuyên gia ký |
| AC-08 | G2 | Dữ liệu thật được phép dùng và snapshot | So input manifest, data authority và tên dự án | Có data approval đúng scope và hash 100% file input | Manifest + quyền + owner; synthetic không đạt pilot thật |
| AC-09 | G2 | Actual vs expected và holdout | Đối soát độc lập scope/quantity/amount/contracts | 0 sai lệch không có disposition; holdout do reviewer chọn và duyệt | Report đối soát và reviewer |
| AC-10 | G2/04 | Decimal/UOM/null/cộng dồn và phân biệt cost basis | Tests missing/unit conversion/rounding/double count/replay | 0 sai lệch vượt precision/rule pin; 0 invented total; cha=con đúng basis | Test logs + calculation/replay pins |
| AC-11 | G3 | Tải/SLA/RPO/RTO | Chốt threshold trước đo; benchmark và restore | Mọi threshold được duyệt đều đạt; thiếu threshold = Chưa | NFR contract + raw measurements |
| AC-12 | G3 | ACL/input độc hại/concurrency/crash/DR | Positive/negative tests, kill/restore trên môi trường được phép | 0 unauthorized write/read hoặc mất transaction không được disposition; restore đạt ngưỡng | Security/DR report, host, logs |
| AC-13 | G3 AI | Pin model/prompt/tool và đánh giá nguồn | Nếu có AI: holdout/citation/injection/ACL; nếu không: exclusion có scope | Threshold được duyệt đạt; N/A chỉ khi không đưa AI vào accepted scope | AI eval hoặc quyết định exclusion |
| AC-14 | G4 | Pháp lý/edition/license/hiệu lực và applicability | Chuyên gia kiểm nguồn chính thức; không suy từ tên file | 100% nguồn áp dụng được xác nhận; conflict có quyết định | Source review và authority |
| AC-15 | G4 | Người lập/kiểm/duyệt/phát hành/DOA/tách nhiệm vụ | So appointment/authority cho đúng artifact digest | 0 vai trò bắt buộc thiếu; không coi Codex là người ký | RACI/DOA + decisions |
| AC-16 | G5 | Schema/API sandbox, mapping/roundtrip/idempotency/rollback | Adapter contract + positive/negative sandbox tests | 100% mapping bắt buộc design gate đạt; mọi test bắt buộc đạt | Odoo matrix + gate report + API evidence |
| AC-17 | G5 | UAT/backup/đào tạo/monitoring/quyền ghi thật | UAT + restore rehearsal + read-back quyền | Mọi mục vận hành bắt buộc có evidence và người duyệt; chưa có = Chưa | Runbook, training, monitoring, UAT/write approval |
| AC-18 | Mỗi gate G0–G5 | Owner, hash input, expected, actual, evidence, reviewer, decision | Kiểm hồ sơ từng gate và dependency | 6/6 gate có đủ record; HOLD tiền nhiệm chặn hậu nhiệm; không gộp gate CCIP/DST | Gate register + crosswalk lịch sử |
| AC-19 | Chặng 4 | Mẫu mapping soát tay | Random sample 30 dòng khác nhau, lưu seed và population hash | 30 dòng nếu đủ population; <30 phải ghi thiếu và kiểm toàn bộ, không nhân bản để đủ | SAMPLE_MAPPING_vN.xlsx + reviewer |
| AC-20 | 06 ưu tiên/kế hoạch | MVP/owner/SoR→pilot→lỗi→NFR/pháp lý/tích hợp→UAT | Review DAG + kế hoạch nguồn lực | Không mở ghi thật trước gate; ngày/effort/kinh phí chỉ điền khi có căn cứ | Plan/dependencies và quyết định |

Crosswalk 06 đầy đủ: nghiệm thu gói→AC01–02; G0→AC02–03; G1→AC04–07; G2→AC08–10; G3→AC11–13; G4→AC14–15; G5→AC16–17; yêu cầu mỗi gate→AC18; thứ tự/nguồn lực→AC20. AC19 bổ sung yêu cầu runbook. Không thay ngưỡng để làm PASS.

## 6. Gate thiết kế và giới hạn Chặng 1

Odoo **APPLICABLE** vì DoD định nghĩa field output nghiệp vụ. Ma trận inventory phải bao phủ cả field hiển thị, derived và metadata ở mục 2 và AC_RESULTS. Source Git/schema đã pin trong evidence. Đầu ra này là report EPSMS local; model Odoo liên quan chỉ là candidate tham khảo, không biến node_id thành project.task.id hoặc project_id thành integer Odoo ID. Mapping tích hợp thực vẫn UNVERIFIED/HOLD ở AC16, không có write permission.

Chặng 1 hoàn thành **định nghĩa/crosswalk tiêu chí**; không phải design approval của Form/API ERP, nghiệm thu nghiệp vụ, chứng thực văn bản hay release. A04 (cây/mã) và A05 (format/cột adapter) là đề xuất để Brian review. Giữ mọi pin lịch sử, không sửa source thư mục mới, không chuyển tên văn bản theo tên folder. Phát hành chính thức cần gate nguồn, content approval và destination/ACL riêng. Lượt này chỉ thực hiện Chặng 1 theo yêu cầu mới nhất.
