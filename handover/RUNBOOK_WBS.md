# RUNBOOK_WBS — Chạy end-to-end ra WBS final

> File điều phối cho Codex. Đặt ở thư mục gốc `handover/`, cùng cấp với `AGENTS.md`.
> Codex thực hiện tuần tự 5 chặng, tự ghi tiến độ vào `PROGRESS.md` để có thể resume nếu bị ngắt.

---

## 0. Nguyên tắc chạy

- **Chế độ chạy**: tự động, không dừng hỏi giữa chừng. Chỉ dừng lại khi gặp **STOP condition** (mục 6).
- **Không phá dữ liệu gốc**: `references/`, `objects/`, `demo_runs/`, `development_runs/` là READ-ONLY.
- **Mọi output** ghi vào `runs_brian/` và `final/`; không ghi đè run cũ.
- **Giả định**: khi thiếu thông tin, chọn phương án hợp lý nhất, **ghi rõ vào `05_QuyetDinh_GiaDinh_VanDe`** (mục "Giả định mới — Brian review") rồi đi tiếp.
- **Git**: commit sau mỗi chặng và sau mỗi gap đã đóng (`git add -A && git commit -m "..."`).
- **Resume**: đầu mỗi phiên, đọc `PROGRESS.md` và tiếp tục từ bước dở dang, không làm lại từ đầu.
- Ngôn ngữ báo cáo: tiếng Việt, giữ thuật ngữ kỹ thuật tiếng Anh.

---

## Chặng 1 — Definition of Done (DoD)

**Input**: `01_MucTieu_PhamVi`, `02_WBS_CBS_CauTruc`, `03_KienTruc_EA3`, `04_YeuCau_DonGia_DinhMuc`, `06_NghiemThu_KeHoach`.

**Việc làm**: định nghĩa WBS cuối cùng phải đạt gì.

**Output**: `DoD_WBS.md`, gồm:
1. Định dạng file final (Excel/CSV/JSON) và tên file.
2. Danh sách cột bắt buộc, kiểu dữ liệu, ví dụ.
3. Số cấp WBS và quy tắc đánh mã (độ dài, ký tự phân cách, không trùng, không nhảy cấp).
4. Mapping bắt buộc: WBS ↔ CBS, WBS ↔ định mức/đơn giá (ghi rõ văn bản/phiên bản nguồn).
5. Bảng tiêu chí nghiệm thu **đo được**: mã tiêu chí `AC-xx`, mô tả, cách kiểm tra (script/thủ công), ngưỡng Đạt.

**Done khi**: mọi tiêu chí trong `06` đều có `AC-xx` tương ứng. Commit: `"Chang 1: DoD"`.

---

## Chặng 2 — Hiểu pipeline

**Input**: `current_executor/` (catalog, templates, wbs, qa, officeqa, examples), `08_BanDo_Nguon`, `FILE_ERRORS.json`, `09_Backlog_TiepTuc`.

**Output**: `PIPELINE.md`, gồm:
1. Sơ đồ các bước input → output (dạng danh sách hoặc Mermaid).
2. Entry point và lệnh chạy end-to-end chính xác.
3. Yêu cầu môi trường (Python version, requirements, biến môi trường).
4. Bước nào đang lỗi/chưa làm, đối chiếu `FILE_ERRORS` và backlog `09`.

**Việc làm thêm**: setup môi trường (`python -m venv .venv`, cài requirements). Nếu không có `requirements.txt` thì tự suy ra từ import và tạo file.

**Done khi**: lệnh chạy end-to-end được xác định và môi trường cài xong. Commit: `"Chang 2: pipeline + env"`.

---

## Chặng 3 — Chạy v1 và lập bảng gap

**Việc làm**:
1. Chạy 1 demo cũ trong `demo_runs/` để xác nhận executor hoạt động (output ra `runs_brian/demo_check/`); so với output cũ.
2. Chạy pipeline end-to-end ra `runs_brian/v1/`. Nếu một bước lỗi: ghi log, bỏ qua được thì bỏ qua và chạy tiếp tối đa.
3. Kiểm tra output v1 theo từng `AC-xx` trong `DoD_WBS.md` (dùng `qa/`, `officeqa/` nếu có).

**Output**: `GAP_v1.md` — bảng: `AC-xx` | Trạng thái (Đạt/Chưa) | Bằng chứng | Nguyên nhân | Task cần làm | Ưu tiên (P1/P2/P3).

**Done khi**: mọi `AC-xx` đã có trạng thái. Commit: `"Chang 3: v1 + gap"`.

---

## Chặng 4 — Đóng gap (vòng lặp)

Với từng gap theo thứ tự ưu tiên P1 → P3:
1. Ghi plan ngắn vào `PROGRESS.md`.
2. Sửa code/cấu hình (không sửa dữ liệu READ-ONLY).
3. Chạy lại pipeline ra `runs_brian/vN/` (N tăng dần).
4. Chạy lại toàn bộ kiểm tra AC (tránh regression).
5. Cập nhật `GAP_vN.md`; nếu tốt hơn bản trước → commit `"Gap AC-xx: done"`; nếu tệ hơn → `git checkout .` và thử cách khác (tối đa 3 lần/gap, quá 3 lần thì đánh dấu BLOCKED và chuyển gap tiếp theo).

**Kiểm tra bắt buộc mỗi vòng** (ngoài AC):
- Mã WBS: không trùng, không nhảy cấp, đúng quy tắc DoD.
- Tính cộng dồn: tổng cấp cha = tổng cấp con (khối lượng/chi phí).
- Mapping định mức/đơn giá: xuất file `SAMPLE_MAPPING_vN.xlsx` gồm 30 dòng ngẫu nhiên để Brian soát tay.

**Done khi**: mọi AC Đạt, hoặc phần còn lại đều BLOCKED có lý do rõ ràng.

---

## Chặng 5 — Đóng gói và nghiệm thu

**Output** trong `final/`:
1. File WBS final đúng định dạng DoD.
2. `BaoCao_NghiemThu.md`: từng `AC-xx` → Đạt/Chưa → bằng chứng (đường dẫn file/run).
3. `TOM_TAT_CHO_BRIAN.md` (tối đa 1 trang): kết quả, số giả định mới đã ghi vào `05`, danh sách BLOCKED, 3 việc Brian cần quyết.
4. Cập nhật `09_Backlog_TiepTuc` (trạng thái mới) và điền biên nhận theo `10_BienNhan_Mau`.

Commit: `"Chang 5: WBS final"`.

---

## 6. STOP conditions — dừng lại và báo Brian

- Tài liệu `01`/`02`/`04`/`06` **mâu thuẫn nhau** ở điểm ảnh hưởng tới cấu trúc WBS (số cấp, quy tắc mã, nguồn định mức).
- Thiếu dữ liệu nguồn bắt buộc mà không thể giả định hợp lý (ví dụ không có bảng định mức/đơn giá).
- Cần cài phần mềm ngoài Python package, cần mạng ngoài, hoặc cần quyền ghi ngoài thư mục `handover/`.
- Một thao tác sẽ xoá/ghi đè dữ liệu READ-ONLY.

Khi dừng: ghi lý do và các phương án vào `PROGRESS.md`, rồi báo ngắn gọn.

---

## 7. Mẫu PROGRESS.md

```markdown
# PROGRESS
| Thời điểm | Chặng | Việc | Trạng thái | Ghi chú/Commit |
|---|---|---|---|---|
```
