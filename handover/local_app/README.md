# CC1 local estimate app — schema 0.2.0

Chạy `StartApp.cmd` trong thư mục này, mở http://127.0.0.1:8765. Cần Python 3.11/3.12 và openpyxl 3.1.5; lần đầu script tạo venv trong handover và cài dependency. Thư viện AI (`anthropic`, file `requirements-ai.txt`) là tùy chọn: cài lỗi hoặc máy không có mạng thì app dự toán vẫn chạy. Không cần Node hoặc dịch vụ cloud để lập dự toán. Port bận thì dùng `python -X utf8 local_app/server.py --port 8767`; không tự dừng service khác. Dừng bằng `StopApp.cmd`.

App này là component mới của handover, không thay current_executor hoặc những run đã freeze. Runtime mặc định ở `local_app/runtime/app.sqlite`; giữ cả thư mục runtime để tiếp tục trên cùng máy. Export snapshot ở runtime/exports. Dùng Tải/Nạp hồ sơ JSON để chuyển hồ sơ giữa máy; restore tạo hồ sơ mới giữ input/lineage, yêu cầu xác nhận lại các bước, không nhập quyền phê duyệt từ JSON. Backup 0.1.0 được nhận và tự chuyển sang 0.2.0.

## Thay đổi 0.2.0 (D27, BL24–BL31)

- **Ghép định mức (L1):** một normalized item có nhiều dòng *áp dụng định mức* (`applications`), mỗi dòng có `qty_factor` = khối lượng định mức trên 1 đơn vị item (ví dụ 1 m³ bê tông → 1; cốt thép 0,12 t/m³ → 0,12). Hệ số khác 1 cần `factor_ref`; UOM khác cần `conversion_ref`. Tách item (partition) chỉ dùng khi một dòng BOQ thuộc nhiều WBS.
- **Dòng hao phí % (L2):** `line_type=PERCENT`, `percent` trên nhóm `percent_of` (C10/C30…) của cùng recipe, ví dụ "vật liệu khác 2%". Không cần giá.
- **Bảng giá theo nguồn lực master (L3):** giá khóa theo `resource_code + spec + uom + location(vùng giá)` cùng kỳ/tiền tệ hồ sơ. Vùng giá lấy từ `price_zone` của WBS occurrence, trống thì dùng địa bàn mặc định. Nút *Tạo dòng giá còn thiếu* sinh dòng giá trống cho đúng các key cần.
- **WBS occurrence (L4):** khai báo một lần Work Result/LBS/vùng giá/scope/acceptance/CA/CAM; item chỉ trỏ `wbs_id`. Profile `ESTIMATE_MIN` không bắt buộc 8 mã PBS…GL; `FULL` thì bắt buộc. *Điền hàng loạt* áp một giá trị cho mọi dòng đang lọc.
- **Tổng hợp (L5):** khi thiếu, hiện *đã biết* + % phủ + danh sách thiếu, không công bố tổng. Basis rule có thể là `DIRECT`, nhóm CBS (`C20`) hoặc tổng các rule trước. Phân bổ COST/CONTINGENCY xuống item (`DIRECT_PRORATA`) chỉ để so sánh với đơn giá BOQ nguồn (sheet `SO_SANH_HOP_DONG`). Làm tròn `TOTAL` hoặc `LINE`.
- **Mục đích (L6):** `STATE_NORM_CHECK` hoặc `INTERNAL_COST`; trộn loại định mức khác mục đích cần `norm_mix_ref`.
- **Thư viện dữ liệu:** nút ▤ ở thanh bên. Nạp CSV/XLSX bộ NORMS / RESOURCES / PRICES dùng chung cho mọi hồ sơ; mỗi lần nạp là phiên bản mới bất biến, có SHA256; chỉ *lưu trữ*, không xóa. Ở bước định mức/giá dùng *Lấy từ thư viện*; dòng lấy về giữ `library_dataset`/`library_sha256`.
- **Trợ lý AI:** panel bên phải mỗi bước và nút ✦ *Cài đặt AI*. Xem mục AI bên dưới.

## Dữ liệu nhà nước và thị trường đã nạp (D28)

Thư viện dữ liệu trên máy này đã có sẵn:
- **TT38/2026 PL1–PL6:** 9.012 mã định mức và hao phí, dạng ứng viên, `table_verified=false`.
- **TT36:** 117 tỷ lệ chi phí, xem qua nút *Tham khảo tỷ lệ TT36* ở bước 7.
- **TT37:** thông số 779 máy.
- **Giá công bố Hưng Yên:** VL 09/2026, nhân công nhóm 2026, ca máy 2025.
- **Giá công bố Hà Nội:** VL 12/2025, 03/2026, 04/2026, quý II/2026.
- **Register nguồn công bố giá 34 tỉnh/thành.**
- **241 điểm thị trường** (MARKET_REFERENCE).

Cách dùng: ở bước Định mức bấm *Lấy từ thư viện* và nhập mã (ví dụ AF.65120). Ở bước Đơn giá bấm *Tìm & gán giá thư viện*, chọn nguồn lực, tìm (gõ không dấu, "phi14" cho Ø14), rồi gán. Giá khác kỳ hồ sơ cần ghi *căn cứ kỳ giá*. Giá tại bãi/kho để `delivery=UNRESOLVED`, phải quy đổi về chân công trình. Chi tiết, cờ và giới hạn: `runs_brian/norm_library_20261017/QA_REPORT.md`, `runs_brian/state_market_prices_20261017/RUN_SUMMARY.md`.

## Thư viện mã TT38 trong app (D30)

- Nút **⌗ Thư viện mã TT38** ở thanh bên: tìm theo mã (AF.651) hoặc tên công tác (gõ không dấu được). Màn hình chi tiết hiện dòng hao phí, mã danh mục nguồn lực CC1 (NC.Nk / M1xx / VL.* / MTC.* / PCT.*) và trạng thái map. Có link tải Excel thư viện mã 19 sheet.
- Ở bước **Chọn định mức**, bấm *Thêm mã này vào hồ sơ*: recipe và dòng hao phí được thêm với mã danh mục làm khóa giá; lưu bước này lưu cả dòng hao phí.
- Ở bước **Đơn giá**, bấm *Gán giá tự động theo mã*:
  - Nhân công và máy khớp theo mã, đơn vị và vùng giá.
  - Vật tư khớp theo ứng viên STRONG/PROPOSED.
  - Không có giá đúng kỳ thì lấy kỳ trước gần nhất, và phải ghi căn cứ kỳ giá.
  - Có nhiều giá khác nhau hoặc map yếu thì app không đoán; dùng *Tìm & gán giá*.
  - Ô "Căn cứ kiểm và dùng giá" luôn để trống cho người lập điền; dùng *Điền hàng loạt* để điền nhanh.

## Gợi ý mã TT38 cho dòng BOQ (D31)

- Ở bước **Chọn định mức**, tab *Ghép định mức*, bấm **Gợi ý mã TT38**. App xếp ứng viên theo mô tả BOQ, đường dẫn tiêu đề (mã cha 1 › 1.2 › 1.2.1) và đơn vị. Mỗi dòng là một bảng định mức; các nút nhỏ là từng cột (điều kiện, ví dụ đường kính). Tối đa 40 item mỗi lần; dùng ô lọc để chọn nhóm.
- Ứng viên khác đơn vị, khác điều kiện (trên cạn/dưới nước), có động từ phá dỡ/vận chuyển/sửa chữa…, hoặc thuộc PL1 khảo sát/PL5 thí nghiệm/PL6 sửa chữa bị hạ điểm, nhưng vẫn hiện để QS thấy.
- Bấm một cột sẽ thêm recipe và dòng hao phí từ thư viện, rồi ghép vào item với hệ số 1. Gợi ý không xác nhận bước: vẫn phải ghi căn cứ chọn, kiểm bảng gốc và hệ số khối lượng.
- Dòng trọn gói/TG/khoản không có gợi ý (định mức hao phí không áp dụng). Dòng thí nghiệm (siêu âm, nén tĩnh, PDA…) ưu tiên mã thí nghiệm PL1/PL5. Một số cách gọi trong BOQ được quy về tên TT38 theo danh sách đồng nghĩa `SYN` trong `codelib.py` (ví dụ gối chậu → gối cầu); QS rà danh sách này (BL57).
- Ô **Biện pháp bê tông** trong dialog (Bơm AF.3 / Cần cẩu AF.2 / Thủ công AF.1) ưu tiên bảng bê tông đúng biện pháp; để trống thì không ưu tiên. Ứng viên được gộp theo nhóm tiêu đề TT38 (ví dụ AD.23270 BTNC16 tách khỏi AD.23240). Độ đúng đo trên mẫu mới (D34): bảng đúng hạng 1 khoảng 55%, top 3 khoảng 75% — luôn kiểm trước khi chọn.
- **Từ điển BOQ→TT38** (thư viện REFERENCE "Từ điển BOQ→TT38…", bản nháp AI-QS proxy, có phiên bản): luật đưa mã ưu tiên lên và gắn cờ ADJ/COMPOSITE/NO_TT38; dialog hiện nhãn "Từ điển <id>". QS sửa bằng cách nạp phiên bản mới (bản cũ được lưu trữ). Độ đúng đo trên mẫu thứ ba Mễ Sở (D35): hạng 1 ≈63%, top 3 ≈80%.
- **Ghi nhớ lựa chọn QS (D37):** khi bước Chọn định mức được xác nhận, app nhớ mã TT38 QS đã chọn cho từng dòng (bảng qs_choices, chỉ thêm, không sửa). Ở hồ sơ sau, nút *Áp dụng lựa chọn QS đã nhớ* tự ghép recipe cho dòng **giống hệt** (cùng mô tả + đơn vị) chưa có recipe, kèm căn cứ "theo lựa chọn QS đã nhớ: hồ sơ…". Quy cách, biện pháp và căn cứ đối chiếu của item vẫn phải nhập. Nếu các lần chọn trước khác nhau → XUNG ĐỘT, không áp dụng.
- Tiêu chí chấp nhận gợi ý (AC-SUG trong 06): bảng đúng trong 5 ứng viên đầu ≥85%; QS chọn trong 5 ứng viên.
- **Xuất/sửa từ điển:** `runs_brian/norm_library_20261017/bl60/export_dictionary_excel.py <bản sao DB> <out.xlsx>` xuất đầy đủ; QS sửa sheet `10_SUA_TU_DIEN` rồi chạy `dictionary_from_excel.py <xlsx> <out.json>` và `load_library.py <runtime.sqlite> <out.json>` để tạo phiên bản mới.
- **Gói pilot cho QS:** `runs_brian/norm_library_20261017/bl32/build_pilot_bl32.py <bản sao DB> <out.xlsx> [mã hạng mục]`.
- Hai bảng cùng điểm thường khác biện pháp (ví dụ AF.643 cần trục tháp / AF.651 cần cẩu). QS chọn theo biện pháp thực tế.
- Chạy hàng loạt ra Excel cho QS: `runs_brian/norm_library_20261017/suggest_me_so.py <bản sao DB> <out.xlsx> AB`. Luôn chạy trên bản sao DB.

## Luồng sử dụng

1. Hồ sơ: dự án/pháp nhân/hợp đồng/baseline, mục đích dự toán, owner/reviewer, địa bàn/kỳ/tiền tệ, cost basis, profile mã liên quan, legal applicability và chính sách làm tròn.
2. BOQ: nạp CSV UTF-8 hoặc XLSX, chọn sheet/header/cột; hoặc nạp snapshot Mễ Sở theo AB, BB, PAKD_GT hoặc PAKD_TT. Không gộp các basis. Giữ raw cells/hash; loại trừ phải có căn cứ. Tối đa 20.000 dòng/25 MB.
   **Sửa tay (D73):** mã công việc, mô tả hạng mục, đơn giá BOQ, khối lượng, đơn vị đều sửa được; giá trị gốc giữ ở `original_*` (server ghi), raw/hash/nguồn không đổi, sửa khác gốc phải có *Căn cứ sửa tay*. **＋ Thêm dòng** tạo dòng nhập tay (`source_ref` MANUAL…, server tự tính hash, bắt buộc căn cứ); chỉ dòng tay mới xóa được, dòng từ file muốn bỏ thì chọn EXCLUDED kèm căn cứ. Thêm/sửa/bỏ dòng giữ nguyên mapping WBS và ghép định mức của các dòng khác.
3. WBS: tab *WBS occurrence* khai báo occurrence; tab *Normalized item* gán `wbs_id` (lọc + điền hàng loạt), tách item khi cần. MASTER V1.20; I7010.50 và mã HOLD bị chặn.
4. Định mức: tab *Recipe* (mã nguyên tử/edition/denominator/UOM/điều kiện/nguồn), tab *Ghép định mức* (nút *Ghép recipe cho nhiều item*), tab *Quy cách & biện pháp* của item.
5. Hao phí: dòng QTY (resource_code, spec, UOM, hệ số, CBS) và dòng PERCENT. Xác nhận đủ bảng hao phí.
6. Giá: lấy từ thư viện hoặc tạo dòng giá còn thiếu rồi nhập; EX_VAT tại công trường; giá thiếu để trống, giá 0 cần căn cứ.
7. CBS/dự toán: scheme/boundary/tax/completeness, driver phân bổ, các khoản bổ sung. Không có tỷ lệ mặc định.
8. Kiểm và xuất: Excel 19 sheet (composition kế thừa + DU_TOAN, SO_SANH_HOP_DONG, HAO_PHI_DON_GIA, DINH_MUC, DINH_MUC_AP_DUNG, HAO_PHI_GOC, DON_GIA, CBS_CC1, CHI_PHI_BO_SUNG, TONG_HOP, WBS_OCCURRENCE, LIEN_KET_MA, BOQ_NGUON, HO_SO, KIEM_TRA, AUDIT, DOI_SOAT, NGUON_VA_GIOI_HAN). Luôn ghi DỰ THẢO LOCAL.

Sửa bước trước làm mất xác nhận các bước sau, nhưng giữ dữ liệu để review lại. Các nút không phải chữ ký điện tử/DOA; không có Odoo write, ERP import hoặc phát hành chính thức CC1.

## Trợ lý AI (tùy chọn)

Hãng hỗ trợ: Anthropic Claude (Anthropic SDK chính thức; mặc định `claude-opus-5-5`, bật server-side fallback), OpenAI, Google Gemini, endpoint OpenAI-compatible (DeepSeek, Mistral, Groq, Azure, LM Studio…) và Ollama chạy trên máy. Model của các hãng ngoài Anthropic chọn bằng *Tải danh sách model* từ chính provider; không gán sẵn ID.

- AI chỉ trả **AI_PROPOSAL_NOT_APPLIED**, lưu riêng (bảng `ai_proposals`), không đổi revision, không xác nhận bước, không ghi giá/định mức. Người dùng tự kiểm và nhập.
- Prompt chỉ gồm context hồ sơ (bỏ tên người), câu hỏi còn mở của bước và — nếu tick — tối đa 30 dòng (bỏ raw cells). Provider ngoài máy cần tick đồng ý từng lượt. Ollama/endpoint 127.0.0.1 giữ dữ liệu trong máy.
- API key nhập trong *Cài đặt AI* được lưu tại `runtime/ai_settings.json` (hoặc dùng biến môi trường `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`). Key không trả về trình duyệt, không vào backup/Excel/audit, không đóng gói chuyển máy. File chưa mã hóa (I12).
- Chính sách dữ liệu khi gửi ra AI ngoài của CC1 chưa có (I11): dữ liệu hợp đồng/giá nhạy cảm nên dùng Ollama hoặc endpoint nội bộ.

## File đầu vào

Tải header CSV ngay tại từng bảng (WBS occurrence, item, ghép định mức, recipe, hao phí, giá, rule) hoặc trong Thư viện dữ liệu. Header là machine key, không đổi tên; số dùng dấu chấm thập phân. Nạp CSV/XLSX ở một bảng thay dữ liệu bảng đó, phải review lại. ID tự tạo nếu trống. CSV giá dạng 0.1.0 (cột `resource_id`) cần đổi sang `resource_code`; backup JSON 0.1.0 tự chuyển.

Mẫu source: `../MAU WBS MINH & TONG HOP/CC1-LBS-WBS-BOQ-XL-NS-02-02-CAU-ME-SO-V0.2.0-DRAFT.xlsx`, sheet10. App tìm relative từ handover để chạy sau chuyển máy; giữ nguyên cấu trúc ba thư mục trong ZIP.

## Kiểm kỹ thuật

Tại handover: `.venv/Scripts/python.exe -X utf8 local_app/test_app.py` (28 test, gồm migrate 0.1→0.2, ghép định mức, dòng %, vùng giá, so sánh hợp đồng, thư viện, AI không lộ key, Anthropic SDK request qua mock loopback). Browser QA (Playwright từ kit, chỉ dependency phát triển): `node local_app/browser_smoke.cjs` và `node local_app/browser_finish.cjs` với `CC1_TEST_URL` trỏ tới một server dùng DB tạm; kết quả ghi `runs_brian/app_v020_20261017/qa/`. Các fixture/giá chỉ là TEST ONLY.

Kit check báo BLOCKED missing/unsupported Python adapter. Successor Odoo alignment 0.2.0 ở `runs_brian/app_v020_20261017/` (draft PASS, design HOLD). Chỉ hỗ trợ local trusted desktop; không dùng server stdlib này cho LAN/production, không có xác thực đa người dùng hoặc chữ ký phê duyệt.

## Đánh dấu và xử lý lỗi đầu vào (D55)

Các điểm chưa PASS được tô đỏ tại ô nhập, dòng, tab và bước đang mở, kèm lý do từ server. Bấm **Đến chỗ cần sửa** để app mở đúng tab, trang và dòng, kể cả field cần quay về bước trước. Lỗi theo nhóm hiện ở cảnh báo phía trên bảng. Chọn **Chỉ dòng lỗi** để lọc các dòng có locator lỗi.

Sau khi sửa, bấm **Lưu nháp** để server kiểm tra lại; đánh dấu đỏ trước đó giữ nguyên với thông báo chờ kiểm tra. Đầu vào đủ vẫn cần bấm xác nhận bước. Không thay đổi điều kiện xác nhận hoặc phê duyệt.

Browser regression: `CC1_TEST_URL` phải trỏ tới server dùng DB QA riêng (không :8765), `CC1_QA_OUT` trỏ tới thư mục fixture có `ids.json`, rồi chạy `node local_app/browser_validation.cjs`. Evidence và cách tạo fixture: `runs_brian/validation_ui_20261019/`.

## Gói thầu con, thư viện CC1, bản vẽ, mô hình QLDA, hồ sơ xuất (D59, E10–E16)

Tài liệu BMAD/TEA: `../planning/E10_GOI_THAU_THU_VIEN/` (PRD FR-1…27, kiến trúc, epics/stories, test design). Không đổi 8 bước;
thêm hai mục điều hướng:

- **Gói thầu & giao thầu** (cần xác nhận bước 3): chọn mô hình QLDA; tạo gói `GT-nn` và gói `CC1` (tự làm); thêm dòng BB theo
  nhánh mã WBS, Work Result, mô tả/đơn vị hoặc chọn dòng; mỗi dòng BB giữ nguyên mã WBS (ERP), Work Result, LBS của dòng AB.
  Phủ khối lượng phải đủ 100% mỗi dòng AB (gói + CC1). Hình thức giao thầu GỘP/TÁCH (bên cấp VL/NC/M), hình thức giá, phí +
  căn cứ, nguồn lực dùng chung. Giá giao gợi ý ba căn cứ: A = đơn giá AB × K chung; B = chi phí CC1 các thành phần NTP chịu ×
  K × (1+phí); C = báo giá hợp lệ thấp nhất — thiếu đầu vào thì để trống kèm lý do (không chia tỷ lệ VL/NC/M từ đơn giá AB,
  D58). Tải BOQ BB gửi NTP, nạp báo giá (XLSX/CSV theo mẫu) → thẩm định (thiếu dòng, sai đơn vị, giá trống chặn; dòng thêm,
  lệch khối lượng, giá lệch gợi ý cảnh báo). Đề xuất giao thầu là DỰ THẢO. Ghi khối lượng hoàn thành theo dòng BB → % theo mã
  WBS cho chủ đầu tư. Tab Bản vẽ: PDF có lớp chữ / DXF ASCII → ứng viên khối lượng, QS gán dòng AB + hệ số + căn cứ (BOQ không
  đổi). Tab Xuất hồ sơ: ZIP phòng Đấu thầu (lập dự toán) và ZIP phòng Chào thầu (chọn thầu, giao thầu, giá giao), có MANIFEST.
- **Từ điển mã & bộ CC1**: xuất Excel mọi bộ mã (Work Result chỉ đọc, CBS, LBS, họ mã, nguồn lực, BOQ→TT38, biện pháp, mô hình
  QLDA, dữ liệu hồ sơ); nhập lại sheet đã sửa → xem khác biệt → lưu phiên bản mới (bản cũ lưu trữ). Tạo bộ CC1 từ bộ giá/hao
  phí nhà nước bằng hệ số chung/VL/NC/M/tiền tố mã và chỉnh tay có lý do (lineage từng dòng). Kích hoạt lại phiên bản cũ.
  Bộ giá mới nạp ở Thư viện dữ liệu được kiểm cột, giá dương, kỳ YYYY-MM, trùng khóa.

Mô hình QLDA (Việt Nam NĐ 175/2024, FIDIC Red/Yellow, PRINCE2, PMBOK 6, PMBOK 8 — không dùng PMBOK 7, D71) là DRAFT_NEEDS_LEGAL_REVIEW; PMBOK 8 còn CẦN BỔ SUNG nội dung từ văn bản gốc. Odoo alignment
successor `runs_brian/subcontract_e10_20261020/` draft PASS, design HOLD, không ghi ERP.

Kiểm: `.venv/Scripts/python.exe -X utf8 local_app/test_subcontract.py` (18 test) cùng `test_app.py` (40 test).

**Toàn chuỗi (D73):** `local_app/browser_full_chain.cjs` trên server QA DB TRỐNG (không :8765): nạp bộ định mức/hao phí/giá CC1 vào Thư viện → hồ sơ + hợp đồng AB → nạp BOQ AB CSV + sửa tay mô tả/giá/khối lượng/mã + dòng thêm tay → WBS → định mức CC1 từ thư viện + sửa recipe → sửa hệ số hao phí → giá CC1 từ thư viện + sửa giá → CBS (tổng tính tay 750.778.875) → xuất Excel → chia thầu PMBOK 6 (GT-01 60% / CC1 40%, GT-02, dòng tay về CC1) + giá giao nhập tay → ZIP → tải lại giữ nguyên. Lệnh: `CC1_TEST_URL=http://127.0.0.1:8768/ CC1_QA_OUT=<thư mục> node local_app/browser_full_chain.cjs`. Trình duyệt: tạo DB QA
riêng `python runs_brian/subcontract_e10_20261020/seed_qa.py <qa.sqlite mới> <thư mục>`, chạy server QA trên cổng khác
8765, rồi `CC1_TEST_URL=… CC1_QA_OUT=<thư mục> node local_app/browser_subcontract.cjs`.

## PAKD thi công · BM01 (E17, D76)

Tab **PAKD · BM01** trong *Gói thầu & giao thầu*: B doanh thu = Σ KL × đơn giá BOQ AB; C.1.4 VT CC1 cấp, C.1.5/C.1.6 giao NTP (giá theo căn cứ chọn từng gói: đề xuất DRAFT / A / B / C), C.1.6b CC1 tự thực hiện, C.1.7 chưa giao (dự toán CC1); C.1.1–C.1.3, C.1.8–C.1.10, C.2–C.5 do người lập nhập kèm căn cứ, không có tỷ lệ mặc định; D = B − C. Thiếu dữ liệu → để trống, hiện phần đã biết và danh sách thiếu. Nhiều kịch bản và bảng so sánh; chốt phiên bản chỉ thêm (digest đầu vào, không ghi đè, báo khi dữ liệu đổi). Excel: `/api/projects/<id>/pakd.xlsx?scenario=…` hoặc `?version=…`. Test: `local_app/test_pakd.py`; E2E `browser_full_chain.cjs` có bước PAKD. Thiết kế và phạm vi chưa làm: `../planning/E17_PAKD/README.md`.

- D77: chia một gói thành nhiều phần theo nhóm công tác (tiêu đề BOQ AB), dòng tiền FR22 nháp (điều khoản do người lập nhập, không mặc định), Excel PAKD (đang lập + bản chốt) trong ZIP Chào thầu. Chi tiết `planning/E17_PAKD/README.md`.

## Hồ sơ hợp đồng NTP trên BB′ (E18, D78)
Tab "Hợp đồng BB′" ở màn Gói thầu & giao thầu: hồ sơ nháp 15 mục FR29 + form pin SHA-256 + back-to-back AB, trạng thái đến trình ký / ghi bằng chứng ký / phụ lục / đóng, yêu cầu thay đổi AB/NTP, số liệu nghiệm thu NTP / CĐT / thanh toán. DỰ THẢO local, không sinh văn bản HĐ, không ký thay. Test `test_contracts.py`. Chi tiết `planning/E18_HOP_DONG_BB_PRIME/README.md`; gap review `planning/R0_GAP_REVIEW_20261021/REVIEW_R0.md`.

## Trải nghiệm làm việc (E19, D82)
Cửa sổ có ← quay lại / thu nhỏ / phóng to; nút ← Trang trước ở header (và Back của trình duyệt); sửa nhanh cột số trên bảng; ＋ Hạng mục tay; Cập nhật giá hàng loạt có lịch sử giá; xóa gói nháp. Test `browser_ux.cjs` (seed `seed_ux_qa.py`). Chi tiết `planning/E19_UX_D81/README.md`.

## Menu ⋮ bộ hồ sơ (D84)
Ở thanh bên, mỗi hồ sơ có nút ⋮: Mở, Đổi tên, Nhân bản (không chép hợp đồng / nghiệm thu / thanh toán / phiên bản PAKD đã chốt), Ẩn, Tải JSON, Xóa (vào Thùng rác, khôi phục được; xóa vĩnh viễn phải gõ đúng tên). Test `test_projects_admin.py`, `browser_ux.cjs`.

## Một giao diện với CERP-QTO (E21, D85)
8765 là cửa duy nhất: proxy `/v1/*`, `/qto/ui/*` sang CERP-QTO 8770 với token lưu ở `runtime/qto_settings.json` (dán một lần ở "Cài đặt bóc khối lượng"). Màn "Bản vẽ & bóc khối lượng" nhúng CERP-QTO và thẩm định khối lượng bản vẽ ↔ BOQ Tư vấn; màn "Luồng làm việc" dẫn 5 luồng. Cần PostgreSQL 5434 + API 8770 + worker đang chạy. Test `test_qto_bridge.py`, `browser_qto.cjs` (seed `seed_qto_qa.py`, CERP-QTO `tests/qa_server.py`). Chi tiết `planning/E21_MOT_GIAO_DIEN/README.md`.

## Luồng theo Quy trình PAKD Thi công v1.0 (E22, D86)
Màn "Luồng làm việc" theo 7 pha / 18 bước (đầu ra, owner/gate, mức app đáp ứng, trạng thái sống). Chốt PAKD cần dòng tiền; PAKD có bảng quy chiếu A–I (sheet QUY_TRINH_A_I); Hồ sơ có Scope Register. Review: `planning/E22_QUY_TRINH_18_BUOC/REVIEW_LUONG.md`.

## Hồ sơ demo từ ERP (E23, D88)
80 hồ sơ "DEMO ERP · …" dựng bằng `runs_brian/erp_demo_20261022/build_erp_demo.py` từ 4 workbook ERP (AB thật, khung WBS, tham chiếu BB′/PAKD). Nút "Tạo gói từ BB′ ERP" (sau khi xác nhận WBS) và "Nhập gián tiếp từ PAKD_GT ERP". Báo cáo: `runs_brian/erp_demo_20261022/report/`. Chi tiết `planning/E23_HO_SO_DEMO_ERP/README.md`.
