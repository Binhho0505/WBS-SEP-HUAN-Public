# Bộ tài liệu triển khai quản trị tích hợp WBS CBS cho CC1

*Thiết kế nghiệp vụ dữ liệu và hệ thống phục vụ triển khai thực tế*

WBS CBS OBS RBS PBS LBS Hợp đồng Rủi ro Tài sản Dữ liệu

Phiên bản 1.0 | Ngày 09 tháng 10 năm 2026

Trạng thái Thiết kế đề xuất để thẩm định và thí điểm

Tài liệu này cung cấp bộ khung có thể chuyển thành yêu cầu triển khai cho PMO, ban dự án, tài chính kế toán, kỹ thuật, quản trị dữ liệu và đơn vị tích hợp của CC1. Mục tiêu là liên kết phạm vi công việc, ngân sách, tiến độ, khối lượng, hợp đồng và chi phí thực tế bằng dữ liệu có chủ sở hữu và bằng chứng kiểm soát.

Thiết kế ưu tiên một dự án cầu thí điểm trong 90 ngày, sau đó đánh giá mở rộng đến ngày 180. Các vai trò, mã, số liệu và ngưỡng nghiệm thu trong phần thiết kế là đề xuất, chưa phải quy chế đã được CC1 phê duyệt. Không có dữ liệu nội bộ CC1 được cung cấp để xác nhận cấu hình hiện hữu.

Nguồn hình thành Hội thoại được cung cấp và các nguồn sơ cấp được kiểm tra ngày 09 tháng 10 năm 2026. Không truy cập được tệp nhị phân Word cũ; bản này là bản mở rộng tái dựng có kiểm soát, không phải bản so sánh thay đổi trực tiếp với tệp cũ.

Đối tượng sử dụng Ban lãnh đạo dự án chuyển đổi, PMO, BQLDA, QS, tài chính kế toán, mua sắm, kỹ thuật BIM, CNTT, dữ liệu và kiểm soát nội bộ.

# Mục lục

[Mở mục lục chi tiết](#mục-lục-chi-tiết) để chọn từng tiểu mục và mẫu biểu. Bấm liên kết để đi tới nội dung; trong Word có thể cần giữ Ctrl hoặc Command khi bấm. Chân mỗi trang có liên kết quay lại menu.

- [1 Cách sử dụng và phạm vi triển khai](#1-cách-sử-dụng-và-phạm-vi-triển-khai)
- [2 Nền tảng lý thuyết và cách chuyển thành thiết kế](#2-nền-tảng-lý-thuyết-và-cách-chuyển-thành-thiết-kế)
- [3 Kiến trúc các cấu trúc quản trị](#3-kiến-trúc-các-cấu-trúc-quản-trị)
- [4 Dictionary mã hóa và crosswalk](#4-dictionary-mã-hóa-và-crosswalk)
- [5 Governance và RACI](#5-governance-và-raci)
- [6 Control accounts và baseline tích hợp](#6-control-accounts-và-baseline-tích-hợp)
- [7 EVM và kiểm soát chi phí tiến độ](#7-evm-và-kiểm-soát-chi-phí-tiến-độ)
- [8 Quy trình nghiệp vụ từ hợp đồng đến bàn giao](#8-quy-trình-nghiệp-vụ-từ-hợp-đồng-đến-bàn-giao)
- [9 ERD logic và kiến trúc dữ liệu](#9-erd-logic-và-kiến-trúc-dữ-liệu)
- [10 ERP Odoo PMIS BIM và Power BI](#10-erp-odoo-pmis-bim-và-power-bi)
- [11 API sự kiện và vận hành tích hợp](#11-api-sự-kiện-và-vận-hành-tích-hợp)
- [12 Chất lượng dữ liệu và AI](#12-chất-lượng-dữ-liệu-và-ai)
- [13 Ví dụ xuyên suốt dự án cầu BR01](#13-ví-dụ-xuyên-suốt-dự-án-cầu-br01)
- [14 Roadmap 30 60 90 180 ngày](#14-roadmap-30-60-90-180-ngày)
- [15 KPI acceptance criteria và nghiệm thu](#15-kpi-acceptance-criteria-và-nghiệm-thu)
- [16 Change control versioning và quản lý phát hành](#16-change-control-versioning-và-quản-lý-phát-hành)
- [Phụ lục A Danh mục nguồn và giới hạn sử dụng](#phụ-lục-a-danh-mục-nguồn-và-giới-hạn-sử-dụng)
- [Phụ lục B Bộ biểu mẫu triển khai](#phụ-lục-b-bộ-biểu-mẫu-triển-khai)
- [Phụ lục C Data contract và quy tắc tính](#phụ-lục-c-data-contract-và-quy-tắc-tính)
- [Phụ lục D Ví dụ API và sự kiện](#phụ-lục-d-ví-dụ-api-và-sự-kiện)
- [Phụ lục E Checklist workshop và backlog](#phụ-lục-e-checklist-workshop-và-backlog)
- [Phụ lục F Thuật ngữ thống nhất](#phụ-lục-f-thuật-ngữ-thống-nhất)
- [Phụ lục G Sổ giả định và quyết định còn mở](#phụ-lục-g-sổ-giả-định-và-quyết-định-còn-mở)
- [Phụ lục H Lưu vết hội thoại truy cập được](#phụ-lục-h-lưu-vết-hội-thoại-truy-cập-được)
- [Phụ lục I Quy tắc tiếp nhận và cập nhật tài liệu](#phụ-lục-i-quy-tắc-tiếp-nhận-và-cập-nhật-tài-liệu)
# 1 Cách sử dụng và phạm vi triển khai

## 1.1 Quyết định triển khai đề xuất

CC1 nên bắt đầu bằng một chu trình khép kín trên một dự án cầu: phê duyệt phạm vi và ngân sách, cấp mã, giao trách nhiệm, ghi nhận khối lượng có bằng chứng, thu thập chi phí, đối chiếu cuối kỳ và công bố báo cáo. Chỉ mở rộng khi có hai kỳ chốt số liên tiếp đáp ứng tiêu chí nghiệm thu. Đây là phương án thiết kế trong tài liệu, không phải mô tả tổ chức hoặc hệ thống đang vận hành tại CC1.

Đơn vị triển khai phải cấu hình quy trình và chứng minh bằng dữ liệu mẫu trước khi chuyển dữ liệu thật. Mỗi yêu cầu trong tài liệu được chuyển thành backlog có ID, người chịu trách nhiệm, tiêu chí kiểm thử và bằng chứng. Phụ lục biểu mẫu dùng trực tiếp để mở hồ sơ; không coi các ô trống là dữ liệu đã được phê duyệt.

## 1.2 Bốn lớp nội dung và mức tin cậy

| **Nhãn**     | **Ý nghĩa**                                             | **Cách sử dụng**                                                                 |
|--------------|---------------------------------------------------------|----------------------------------------------------------------------------------|
| NGUỒN        | Mô tả ngắn có mã Sxx tới nguồn sơ cấp                   | Kiểm tra tên tài liệu, phiên bản và phạm vi; không suy thành chứng nhận tuân thủ |
| THIẾT KẾ CC1 | Đề xuất nghiệp vụ, dữ liệu, quy trình và ngưỡng         | Phải được chủ quy trình thẩm định; mặc định áp dụng cho mọi chương triển khai    |
| MINH HỌA     | Mã và số liệu giả định của dự án BR01                   | Dùng học, thử nghiệm và đối soát; không dùng lập cam kết thương mại              |
| LƯU VẾT      | Nội dung hội thoại nguyên văn hoặc ghi chú khuyết thiếu | Không sửa lại lịch sử bằng kiến thức mới; xem Phụ lục H                          |

Các nguồn ISO trong bản này được xác minh qua trang danh mục và mô tả công khai; chưa đối chiếu toàn văn có bản quyền ở cấp điều khoản. Các nguồn mở của nhà phát hành hỗ trợ nguyên lý và tính năng được nêu. Nội dung thiết kế chi tiết là tổng hợp và đề xuất riêng, không sao chép yêu cầu thành điều khoản giả của ISO, PMI hay cơ quan nhà nước.

## 1.3 Ranh giới nghiệp vụ

Phạm vi trước mắt là góc nhìn nhà thầu thi công: chi phí thực hiện, hợp đồng đầu ra với chủ đầu tư, hợp đồng đầu vào với thầu phụ và nhà cung cấp, khối lượng, tiến độ và lợi nhuận dự kiến. Nếu CC1 tham gia với vai trò chủ đầu tư, liên danh hoặc đơn vị vận hành tài sản, phải mở lớp vai trò và phạm vi riêng. Không trộn tổng mức đầu tư của chủ đầu tư với giá trị hợp đồng nhà thầu hoặc BAC của EVM.

Ngoài phạm vi phê duyệt của tài liệu là lựa chọn nhà cung cấp, mua giấy phép, cam kết giá, điều chỉnh hợp đồng, chính sách kế toán thuế, tiêu chuẩn kỹ thuật thiết kế cầu và chứng nhận tuân thủ. Bộ phận pháp chế, tài chính và kỹ thuật xác nhận quy định áp dụng trước vận hành; tài liệu chỉ thiết kế nơi lưu và cơ chế kiểm soát các yêu cầu đó.

## 1.4 Điều kiện đầu vào cần thu thập trong 10 ngày đầu

| **Hồ sơ cần có**                      | **Chủ trì đề xuất**        | **Kết quả cần xác nhận**                                  |
|---------------------------------------|----------------------------|-----------------------------------------------------------|
| Sơ đồ pháp nhân và quyền quyết định   | Ban chỉ đạo cùng tài chính | Phạm vi công ty, liên danh, dự án và thẩm quyền           |
| Hợp đồng chính và BOQ được duyệt      | Thương mại và QS           | Phạm vi, đơn vị đo, điều kiện thanh toán, thay đổi        |
| Dự toán nội bộ và tiến độ gốc         | PMO cùng BQLDA             | Cùng phạm vi và mốc chốt, danh sách loại trừ              |
| Danh mục tài khoản và dữ liệu chi phí | Kế toán                    | Cơ sở ghi nhận, accrual, tiền tệ, kỳ kế toán              |
| Danh sách hệ thống và phiên bản       | CNTT                       | Odoo có hay chưa, bản triển khai, quyền API, PMIS và CDE  |
| Mô hình BIM và hồ sơ chất lượng       | Kỹ thuật                   | Quyền khai thác, phiên bản, đối tượng và hồ sơ nghiệm thu |
| Quy chế bảo mật và lưu trữ            | CNTT cùng pháp chế         | Phân loại dữ liệu, thời hạn lưu, quyền truy cập           |

Thiếu một hồ sơ không làm đình trệ việc dựng mẫu; tuy nhiên hồ sơ thiếu phải được gắn trạng thái Pending và không được dùng làm căn cứ phê duyệt baseline thật. Quyết định giả định ghi rõ hạn xác minh và người chịu trách nhiệm.

## 1.5 Bản đồ đọc theo vai trò

Lãnh đạo đọc chương 1, 5, 14 và 15 để quyết định phạm vi thí điểm và điều kiện mở rộng. PMO và BQLDA dùng chương 3 đến 8 và 13 để thiết lập chu trình kiểm soát. Nhóm dữ liệu và tích hợp dùng chương 4, 9 đến 12 cùng Phụ lục B đến E. Người nghiệm thu dùng chương 15 và mẫu F12 để lập hồ sơ bằng chứng. Phụ lục H luôn giữ độc lập với các phần được biên soạn mới.

# 2 Nền tảng lý thuyết và cách chuyển thành thiết kế

## 2.1 Bản chất của hệ thống quản trị tích hợp

WBS trả lời phạm vi nào cần hoàn thành; CBS trả lời bản chất chi phí nào được quản lý; OBS trả lời đơn vị nào chịu trách nhiệm. Những góc nhìn này cùng mô tả dự án nhưng không thay thế nhau. Một cây không biểu diễn đầy đủ các quan hệ nhiều nhiều giữa công việc, địa điểm, sản phẩm và hợp đồng. Vì vậy thiết kế sử dụng cây cho quan hệ cha con, danh mục cho phân loại và bảng quan hệ có hiệu lực cho các liên kết.

Nguồn S01 mô tả ISO 21511 như hướng dẫn về khái niệm, đặc điểm và quan hệ của WBS. Nguồn S03 của NASA hỗ trợ cách nhìn hệ thống xuyên vòng đời. Từ đó, thiết kế CC1 đặt mỗi work package trong một phạm vi xác định, có sản phẩm đầu ra, tiêu chí hoàn thành và dấu vết về yêu cầu. Đây là lựa chọn thiết kế, không phải diễn giải toàn văn tiêu chuẩn.

## 2.2 Hai mươi bốn nhóm lý thuyết liên quan

### 1 Lý thuyết hệ thống

Một dự án là tập hợp bộ phận có quan hệ với nhau và với môi trường. Tối ưu riêng năng suất một đội có thể làm tăng tồn kho hoặc chặn mặt bằng đội khác. Thiết kế CC1 phải ghi giao diện giữa gói công việc, chủ sở hữu giao diện và điều kiện bàn giao; kết quả đo ở cấp dự án, không chỉ cấp đội. Liên hệ học thuật và thực hành: S03.

### 2 Phân rã và tính mô đun

Chia phạm vi thành đơn vị đủ nhỏ để lập kế hoạch và giao trách nhiệm, nhưng không phân rã đến mức chi phí quản lý vượt giá trị kiểm soát. Điểm dừng đề xuất là gói có đầu ra nghiệm thu được, một người quản lý và phương pháp đo tiến độ rõ. Độ sâu WBS không bắt buộc giống nhau ở mọi nhánh. Cơ sở tham chiếu: S01.

### 3 Kỹ nghệ yêu cầu

Yêu cầu của chủ đầu tư cần liên kết tới sản phẩm, công việc tạo ra sản phẩm và phép kiểm chứng. Thiếu liên kết làm phát sinh phạm vi không có chủ hoặc sản phẩm làm xong nhưng không đáp ứng mục đích. Tại CC1, requirement_id nối PBS, WBS và acceptance_record; mỗi yêu cầu có nguồn, người duyệt, phương pháp kiểm tra và trạng thái. Liên hệ: S03.

### 4 Quản lý cấu hình và baseline

Baseline là trạng thái đã chấp thuận để so sánh, không phải bản mới nhất đang sửa. Một bộ hồ sơ cấu hình gồm phạm vi, ngân sách, tiến độ, cách đo và các mapping tương ứng. Nếu thay đổi phạm vi mà giữ cách đo cũ, chỉ số mất ý nghĩa. CC1 cần baseline_id thống nhất và lịch sử thay đổi bất biến. Liên hệ: S03.

### 5 Quản trị dự án tích hợp

Phạm vi, thời gian, chi phí, chất lượng, nguồn lực và rủi ro tương tác. Quyết định đổi biện pháp thi công cần xem đồng thời khả năng thiết bị, mặt bằng và hợp đồng. Thiết kế buộc change request có phân tích tác động đa chiều, thay vì duyệt riêng ngân sách rồi mới phát hiện chậm mốc bàn giao. S04 cung cấp khung thực hành ước tính và kiểm soát chi phí.

### 6 Ước tính chi phí và cơ sở ước tính

Một con số dự toán cần lượng, đơn giá, điều kiện thi công, nguồn giá, thời điểm và bất định. CC1 lưu Basis of Estimate theo từng nhóm WBS và CBS. Đơn giá bán, đơn giá chi phí và đơn giá kế toán không dùng chung một trường. Cập nhật forecast phải nêu nguyên nhân thay đổi năng suất, giá hoặc lượng. Tham chiếu S04.

### 7 Kiểm soát phản hồi bằng EVM

Kế hoạch, đầu ra đạt được và chi phí đã phát sinh tạo thành ba tín hiệu khác nhau. EVM đưa phạm vi hoàn thành về đơn vị ngân sách để so với kế hoạch và thực tế. CC1 chỉ dùng EV có bằng chứng và cùng ngày chốt với AC, không dùng tiền đã thanh toán để suy ra tiến độ. S02 là hướng dẫn ISO về EVM; ví dụ tính ở chương 7 là do tài liệu thiết kế.

### 8 Mạng tiến độ và đường găng

Danh sách công việc không cho thấy quan hệ phụ thuộc. Mạng tiến độ thể hiện điều kiện trước sau, lịch làm việc và đường quyết định ngày hoàn thành. Một SPI tốt không bảo đảm đường găng đúng kế hoạch. CC1 kiểm tra logic mạng, mốc ràng buộc và dự báo ngày hoàn thành bên cạnh EVM. S05 là hướng dẫn đánh giá tiến độ.

### 9 Lean Construction và độ tin cậy kế hoạch

Cam kết ngắn hạn cần dựa trên điều kiện sẵn sàng như bản vẽ, vật tư, thiết bị và mặt bằng. Thiết kế đề xuất lookahead sáu tuần, sổ ràng buộc và kế hoạch tuần. PPC đo việc hoàn thành cam kết, không thay EV hay chất lượng. Nguồn S06 giới thiệu Last Planner System; chu kỳ và ngưỡng trong tài liệu do CC1 quyết định.

### 10 Tối ưu ràng buộc và dòng công việc

Nút thắt thay đổi theo thời gian: máy khoan có thể là ràng buộc tuần này, phê duyệt bản vẽ là ràng buộc tuần sau. Quy tắc thực hành đề xuất là nhận diện công đoạn giới hạn sản lượng, bảo đảm đầu vào cho nó rồi cân bằng phần còn lại. Đây là phân tích vận hành trong thiết kế, không tuyên bố thuộc một tiêu chuẩn WBS cụ thể.

### 11 Quản trị tổ chức ma trận

Một kỹ sư có thể thuộc phòng kỹ thuật nhưng được giao công việc của dự án. OBS biểu diễn đơn vị; RACI biểu diễn trách nhiệm trên quyết định; phân quyền hệ thống biểu diễn hành động được phép. Không dùng ba thứ này thay cho nhau. Mỗi hồ sơ cần một A chịu trách nhiệm cuối cùng và người R thực hiện; các tên vai trò phải ánh xạ người thật.

### 12 Phân tách nhiệm vụ và kiểm soát nội bộ

Người tạo nhà cung cấp không nên đồng thời phê duyệt thanh toán cho chính hồ sơ đó. Tại CC1, quyền tạo, kiểm tra, duyệt, đăng sổ và công bố phải có nhật ký; các trường hợp kiêm nhiệm cần người rà soát độc lập. Đây là kiểm soát thiết kế, phải khớp phân cấp ủy quyền thực tế.

### 13 Hợp đồng và phân bổ trách nhiệm

Hợp đồng xác định nghĩa vụ thương mại; WBS xác định phạm vi quản trị; BOQ xác định các dòng đo và tính giá theo hợp đồng. Một BOQ có thể trải nhiều vị trí và gói WBS. Thiết kế dùng mapping riêng và giữ quyền lợi, notice, thay đổi, bảo lãnh, retention ở sổ hợp đồng; không suy quyền thanh toán từ EV.

### 14 Rủi ro và quyết định dưới bất định

Risk là điều kiện chưa chắc xảy ra; issue là vấn đề đã xảy ra. Phân loại nguyên nhân giúp tổng hợp rủi ro, nhưng mỗi sự kiện cần xác suất, tác động, chủ sở hữu và phản ứng. S07 cung cấp hướng dẫn quản trị rủi ro. CC1 đề xuất tách dự phòng được phân bổ trong phạm vi với quỹ quản lý ngoài PMB để tránh che khuất sai lệch.

### 15 Chất lượng và kiểm chứng

Hoàn thành thi công chưa đồng nghĩa chấp nhận sản phẩm. Cần nối yêu cầu, điểm dừng kiểm tra, kết quả thí nghiệm, nonconformity và hồ sơ đóng. Phân biệt verification kiểm tra yêu cầu xác định với validation kiểm tra phù hợp mục đích sử dụng; tham chiếu khái niệm S03. CC1 quy định bằng chứng đủ điều kiện ghi nhận EV theo loại công việc.

### 16 Quản lý tài sản theo vòng đời

PBS của dự án tạo ra các tài sản bàn giao, còn máy thi công là nguồn lực sử dụng để tạo chúng. Tài sản bàn giao cần hồ sơ vận hành, bảo hành, lịch sử lắp đặt và vị trí; không mặc nhiên thuộc sổ tài sản CC1. S08 xác nhận ISO 55001:2024 là tiêu chuẩn yêu cầu về hệ thống quản lý tài sản, không phải bảng mã thiết bị.

### 17 Kiến trúc doanh nghiệp

Thiết kế nghiệp vụ phải có dữ liệu, ứng dụng và hạ tầng hỗ trợ nhất quán. S09 giới thiệu TOGAF như phương pháp và khung kiến trúc doanh nghiệp. CC1 áp dụng nguyên tắc xác định chủ dữ liệu và ranh giới hệ thống trước khi chọn công nghệ, đồng thời lưu quyết định kiến trúc và phương án thay thế.

### 18 Quản lý quy trình và trạng thái

Một trạng thái Published cần điều kiện chuyển, quyền thao tác và hồ sơ đầu vào. Sơ đồ quy trình đẹp nhưng không có điều kiện chặn không tạo kiểm soát. CC1 thiết kế state machine cho mã, baseline, nghiệm thu, change request và kỳ chốt; không cho API bỏ qua điều kiện mà giao diện người dùng bắt buộc.

### 19 Mô hình quan hệ và chuẩn hóa

Khóa định danh ổn định giải quyết việc tên hoặc mã hiển thị thay đổi. Quan hệ nhiều nhiều cần bảng nối. Dữ liệu vận hành hạn chế lặp thuộc tính chủ để tránh cập nhật mâu thuẫn; dữ liệu phân tích có thể phi chuẩn hóa có kiểm soát. ERD chương 9 là mô hình logic đề xuất, chưa phải lược đồ cài đặt đã chạy.

### 20 Mô hình chiều và số liệu cộng gộp

Một fact phải có grain rõ. Chi phí theo dòng chứng từ khác tiến độ lũy kế theo gói và kỳ; join trực tiếp gây nhân bản. S10 giải thích vai trò fact và dimension trong Power BI. CC1 dùng các fact riêng, dimension dùng chung và measure theo đúng quy tắc cộng, snapshot và tỷ lệ.

### 21 Ontology và đồ thị tri thức

Taxonomy phân loại, hierarchy biểu diễn cấp bậc, ontology định nghĩa ý nghĩa quan hệ. Graph giúp truy vấn “rủi ro nào ảnh hưởng tài sản nào qua hợp đồng nào”, nhưng không thay sổ kế toán. Thiết kế bắt đầu bằng khóa và quan hệ đáng tin cậy; chỉ tạo graph khi có câu hỏi không giải quyết tốt bằng mô hình quan hệ.

### 22 Provenance và quản trị dữ liệu

Một con số cần biết sinh ra từ hồ sơ nào, qua phép biến đổi nào và người nào công bố. W3C PROV-O \[S11\] cung cấp mô hình biểu diễn nguồn gốc. CC1 đề xuất giữ source_record_id, transform_version, snapshot_id và người duyệt để truy từ dashboard về chứng từ, kể cả khi nguồn sửa sau kỳ khóa.

### 23 Hệ phân tán và nhất quán cuối cùng

Thông điệp có thể trễ, trùng hoặc sai thứ tự. Thiết kế tích hợp cần idempotency, retry, hàng lỗi và đối soát. OpenAPI \[S12\] mô tả giao diện; CloudEvents \[S13\] mô tả phong bì sự kiện. Chúng không tự bảo đảm nghiệp vụ đúng hoặc exactly once; bảo đảm phải nằm trong khóa giao dịch và kiểm soát ứng dụng.

### 24 AI và quản trị quyết định

AI phù hợp tra cứu hồ sơ, đề xuất phân loại và phát hiện bất thường; phê duyệt tài chính cần quy trình có thẩm quyền. NIST AI RMF \[S14\] tổ chức quản trị rủi ro AI theo Govern, Map, Measure, Manage. CC1 đề xuất AI dẫn chứng từng kết luận, kiểm tra quyền trước truy xuất và dùng bộ kiểm thử nghiệp vụ trước phát hành.

## 2.3 Những đánh đồng cần loại bỏ

Không đồng nhất WBS với lịch tiến độ; CBS với chart of accounts; ngân sách với giá trị hợp đồng; AC với thanh toán; EV với doanh thu; phần trăm BIM dựng xong với phần trăm công việc hoàn thành; OBS với danh sách tài khoản đăng nhập; risk category với một risk event. ABS, FBS, SBS và RBS có nhiều nghĩa trong thực hành; giao tiếp tích hợp phải dùng tên trường đầy đủ hoặc tiền tố quy ước.

## 2.4 Cách chọn mức áp dụng tiêu chuẩn

Mỗi tiêu chuẩn trong register cần mục đích áp dụng, phiên bản, bản quyền, owner và bằng chứng đối chiếu. Không đưa “tuân thủ ISO” vào nghiệm thu chỉ vì có một bảng WBS. Nếu hợp đồng yêu cầu tuân thủ tiêu chuẩn, nhóm phụ trách phải lập ma trận điều khoản từ bản được cấp phép, chỉ ra hồ sơ chứng minh và ký xác nhận. Các quy tắc mã hóa và ngưỡng KPI trong tài liệu này là tiêu chuẩn nội bộ đề xuất.

# 3 Kiến trúc các cấu trúc quản trị

## 3.1 Nguyên tắc thiết kế chung

Mỗi cây có một mục tiêu, một owner, một phạm vi pháp nhân và một quy tắc phân rã được mô tả. Trong một phiên bản cây, mỗi nút có tối đa một cha và không được tạo vòng lặp. Nút có giao dịch không được xóa; đổi cấu trúc phải tạo phiên bản hiệu lực. Cấu trúc báo cáo thay thế dùng mapping riêng, không sửa cha lịch sử để làm đẹp báo cáo.

WBS áp dụng kiểm tra bao phủ toàn bộ phạm vi và không trùng giữa các nhánh cùng cấp. Không cộng các cây khác bản chất. CBS có thể tổ chức theo nguồn lực chi phí, OBS theo tổ chức, LBS theo không gian. Việc ghép chúng thành mã quá dài khiến đổi đơn vị phụ trách kéo theo đổi mã công việc; tài liệu tránh cách đó.

## 3.2 WBS và work package

WBS cấp dự án BR01 gồm quản lý và chuẩn bị, thiết kế triển khai, kết cấu dưới, kết cấu trên, đường dẫn, hệ thống phụ trợ và hoàn thành bàn giao. Trong kết cấu dưới, có thể chia theo mố trụ rồi theo sản phẩm như cọc, bệ, thân trụ. Tên gói mô tả đầu ra “Cọc khoan nhồi trụ P01 hoàn thành” tốt hơn tên hoạt động mơ hồ “Thi công”.

Work package là đơn vị thấp nhất được lập kế hoạch và kiểm soát theo cách triển khai này. Nó cần phạm vi vào ra, lượng, đơn vị, CAM phụ trách, phương pháp EV, quan hệ tiến độ và tiêu chí chấp nhận. Activity thuộc tiến độ có thể nhỏ hơn work package. Planning package dành cho phạm vi chưa đủ chi tiết và phải phân rã trước khi được phép thực hiện.

Không bắt buộc số cấp cố định. Gói quá lớn khiến không phát hiện chậm; gói quá nhỏ tăng chi phí cập nhật. Mức đề xuất ban đầu là công việc có thể theo dõi hàng tuần và đánh giá hoàn thành trong một hoặc vài kỳ báo cáo, sau đó hiệu chỉnh trên pilot. Công tác quản lý thường xuyên dùng LOE có giới hạn, không áp phương pháp đó cho sản lượng thi công rời rạc.

## 3.3 CBS theo góc nhìn nhà thầu

| **Mã CBS** | **Nhóm**                       | **Quy tắc phạm vi**                                                      |
|------------|--------------------------------|--------------------------------------------------------------------------|
| C10        | Vật liệu                       | Vật liệu tiêu hao hoặc cấu thành công trình theo chính sách chi phí      |
| C20        | Nhân công                      | Giờ công và khoản phân bổ được tài chính chấp thuận                      |
| C30        | Máy và thiết bị thi công       | Thuê, nhiên liệu hoặc phân bổ nội bộ; tránh tính trùng đơn giá ca máy    |
| C40        | Thầu phụ                       | Khối lượng nhận thầu phụ; không bóc lại vật tư đã nằm trong giá thầu phụ |
| C50        | Chi phí công trường            | Điều hành, lán trại, tiện ích dùng chung theo driver                     |
| C60        | Dịch vụ kỹ thuật và thử nghiệm | Thiết kế thuê ngoài, khảo sát, thí nghiệm theo phạm vi                   |
| C70        | Chi phí khác thuộc phạm vi     | Phải có mô tả và owner; không dùng như tài khoản treo vô hạn             |

Một dòng chi phí nguồn sau phân bổ có đúng một CBS lá trong từng phương án phân loại. Các góc nhìn khác như trực tiếp gián tiếp, cố định biến đổi, CAPEX OPEX là thuộc tính hoặc mapping riêng. Dự phòng không được tự động tính là AC. Management reserve không đưa vào EV hay PV khi chưa được phân bổ và phê duyệt.

CBS nhà thầu phải ánh xạ tài khoản kế toán qua quy tắc có điều kiện: tài khoản, loại vật tư, dự án, nội dung chứng từ. Không áp tỷ lệ một một mặc định. Kế toán sở hữu mapping tài chính, QS kiểm tra mapping phục vụ quản trị. Khoản chưa xác định đưa vào suspense riêng, hiển thị rõ và có hạn xử lý trước kỳ chốt.

## 3.4 OBS và trách nhiệm

OBS có cấp tập đoàn hoặc pháp nhân, ban dự án, bộ phận dự án và đội thi công tùy phạm vi. Lưu org_unit_id, parent_id, legal_entity_id, manager_role và ngày hiệu lực. Nhân sự nằm trong bảng assignment theo thời gian; khi đổi người, mã tổ chức không đổi. Nhà thầu phụ là đối tác ngoài, không giả làm phòng ban nội bộ; có bảng trách nhiệm hợp đồng liên quan.

Một control account có một CAM chịu trách nhiệm điều phối phạm vi, ngân sách và giải trình. CAM không mặc nhiên có quyền duyệt chi hoặc ký nghiệm thu kỹ thuật. Các quyền đó lấy từ RACI và phân cấp ủy quyền. Chi nhánh và dự án của pháp nhân khác không được nhìn dữ liệu chỉ vì có cùng tên đội.

## 3.5 RBS nguồn lực

Quy ước RES cho Resource Breakdown Structure: nhân lực theo kỹ năng, máy theo chủng loại và vật liệu theo nhóm. Danh mục loại nguồn lực khác danh sách cá thể. RES-EQ-DRILL là loại máy khoan, EQ0007 là máy cụ thể; resource_type và resource_instance liên kết nhưng không dùng chung khóa.

Mỗi nguồn lực có đơn vị cơ sở, hệ số quy đổi được duyệt, lịch khả dụng, đơn giá hiệu lực và điều kiện tính chi phí. Người lập kế hoạch cần thời lượng, định mức và năng lực, không chỉ số lượng. Một ngày máy chưa chắc bằng tám giờ nếu hợp đồng khác; conversion phải có ngữ cảnh và phiên bản.

## 3.6 PBS và LBS

PBS mô tả sản phẩm vật lý hoặc bộ hồ sơ bàn giao: cầu, móng, trụ, nhịp, hệ thống thoát nước, bộ hồ sơ hoàn công. LBS mô tả vị trí: tuyến, đoạn lý trình, mố trụ, nhịp, khu vực. Một sản phẩm kéo dài nhiều vị trí có bảng liên kết nhiều nhiều. Một LBS có tọa độ hoặc lý trình và hệ quy chiếu khi cần, không ép mọi vị trí thành tọa độ điểm.

PBS không chứa hoạt động “mua”, “lắp”, “kiểm tra”; đó là công việc tạo sản phẩm. LBS không chứa tên nhà thầu; đổi nhà thầu không đổi vị trí. IFC GlobalId hỗ trợ liên kết đối tượng BIM nhưng cần model_id và model_revision, vì dữ liệu xuất lại có thể đổi định danh; asset_id nội bộ vẫn ổn định.

## 3.7 Contract và BOQ

Hợp đồng đầu ra dùng loại CUSTOMER; đầu vào dùng SUPPLIER hoặc SUBCONTRACT. Mỗi dòng hợp đồng có contract_line_id, BOQ code, mô tả, UOM, lượng, giá, tiền tệ, phiên bản và quy tắc thanh toán. Purchase order, thay đổi và hồ sơ thanh toán có khóa riêng. Một work package có thể mua từ nhiều hợp đồng; một dòng hợp đồng có thể phục vụ nhiều work package.

Không gọi CBS cho cả chi phí và hợp đồng trong API. Dùng CST cho cost, CTR cho contract. Mapping BOQ sang WBS là để phân tích; không sửa nội dung hợp đồng đã ký. Bảo lãnh, tạm ứng, giữ lại, điều chỉnh giá, notice và claim có sổ riêng và liên kết tới mốc, không ghi là phần trăm EV.

## 3.8 Risk và hazard

Dùng RSK cho sự kiện rủi ro và RCT cho nhóm nguyên nhân. Đề xuất nhóm địa chất, thiết kế, mặt bằng, cung ứng, thi công, thương mại, tài chính, an toàn môi trường và dữ liệu công nghệ. Một rủi ro có thể ảnh hưởng nhiều WBS; risk_impact_link lưu loại tác động và mức ước tính. Không cộng xác suất của các rủi ro phụ thuộc như thể độc lập.

Hazard là nguồn gây hại cần kiểm soát an toàn, có quy trình đánh giá chuyên môn riêng. Một rủi ro chi phí cao không được phép đánh đổi kiểm soát an toàn. Khi rủi ro xảy ra, tạo issue liên kết sự kiện gốc và hồ sơ hành động; không xóa risk chỉ để giảm chỉ số tồn đọng.

## 3.9 Asset và data

AST-DLV là tài sản dự kiến bàn giao cho chủ đầu tư; AST-OWN là tài sản thuộc phạm vi quản lý của CC1. Liên kết tài sản với PBS, serial, vị trí, ngày lắp, ngày bàn giao, bảo hành và tài liệu bảo trì. Quyền sở hữu pháp lý, đơn vị vận hành và đơn vị bảo trì là ba thuộc tính riêng.

Dữ liệu được phân loại thành master, reference, transaction, document, model và analytical. Data domain là phạm vi trách nhiệm, không phải thư mục tệp. Mỗi data product như “Chi phí dự án đã chốt” có hợp đồng dữ liệu, owner, grain, chu kỳ, mức chất lượng và quyền truy cập. Không dùng Data Breakdown Structure như một tên tiêu chuẩn quốc tế đã thống nhất.

# 4 Dictionary mã hóa và crosswalk

## 4.1 Từ điển dữ liệu chung

Dictionary là hợp đồng về ý nghĩa dữ liệu, không chỉ danh sách cột. Mỗi trường cần định nghĩa, kiểu, độ dài hoặc độ chính xác, bắt buộc theo trạng thái nào, giá trị cho phép, nguồn chuẩn, owner, kiểm tra chất lượng và mức bảo mật. Giá trị Unknown, Not applicable và chưa nhập phải phân biệt; không dùng số 0 để đại diện dữ liệu thiếu.

| **Trường chung**                  | **Kiểu và điều kiện**            | **Quy tắc kiểm soát**                                             |
|-----------------------------------|----------------------------------|-------------------------------------------------------------------|
| entity_id                         | UUID bất biến, bắt buộc          | Khóa kỹ thuật; không tái sử dụng sau khi ngừng hoạt động          |
| business_code                     | Chuỗi tối đa 64 ký tự            | Duy nhất theo loại và phạm vi; chữ hoa không dấu cho mã           |
| name và description               | Unicode                          | Tên ngắn để tra cứu; mô tả đủ ranh giới nghiệp vụ                 |
| parent_id                         | UUID tùy loại                    | Cùng loại cây và phiên bản; kiểm tra không vòng lặp               |
| legal_entity_id và project_id     | UUID theo phạm vi                | Không suy pháp nhân từ tiền tố mã                                 |
| status                            | Draft Review Approved Retired    | Chuyển trạng thái theo vai trò, không sửa trực tiếp tùy ý         |
| valid_from và valid_to            | Ngày hoặc timestamp              | Khoảng hiệu lực nửa mở từ đầu đến trước cuối; cuối rỗng là vô hạn |
| revision và schema_version        | Số nguyên hoặc phiên bản         | Revision hồ sơ khác phiên bản định nghĩa cấu trúc                 |
| owner_role và steward_id          | Khóa vai trò và người            | Không để owner là tên phòng mơ hồ không có đại diện               |
| source_system và source_record_id | Chuỗi có namespace               | Duy nhất cùng source_instance; hỗ trợ nhiều công ty Odoo          |
| created_by approved_by            | ID người hoặc service            | Dấu vết người phê duyệt không thay bằng tài khoản tích hợp        |
| approved_at change_request_id     | Thời gian và FK                  | Bắt buộc khi phát hành thay đổi sau baseline                      |
| security_class                    | Internal Confidential Restricted | Có quy tắc truy cập và xuất dữ liệu tương ứng                     |

## 4.2 Dictionary WBS có thể dùng làm cấu hình

| **Trường**               | **Định nghĩa**                           | **Bắt buộc khi Approved**                                  |
|--------------------------|------------------------------------------|------------------------------------------------------------|
| wbs_id và wbs_version_id | ID ổn định và bản ghi phiên bản          | Có                                                         |
| wbs_type                 | Summary WorkPackage PlanningPackage      | Có; Summary không ghi chi phí trực tiếp trong thiết kế này |
| scope_in scope_out       | Việc thuộc và không thuộc gói            | Có; không chỉ ghi “theo hợp đồng”                          |
| deliverable_ids          | PBS hoặc tài liệu đầu ra                 | Có ít nhất một liên kết được kiểm tra                      |
| acceptance_rule_id       | Quy tắc nghiệm thu và bằng chứng         | Có đối với WorkPackage                                     |
| quantity_baseline uom_id | Lượng kế hoạch và đơn vị                 | Có nếu phương pháp EV theo lượng                           |
| control_account_id       | Nhóm kiểm soát chịu trách nhiệm          | Có đúng một CA hoạt động trong baseline                    |
| ev_method                | Quantity WeightedMilestone 0_100 LOE     | Có; khóa theo baseline                                     |
| budget_cost              | Giá trị chi phí kế hoạch                 | Nằm ở dòng ngân sách; WBS chỉ hiển thị tổng tính ra        |
| schedule_link            | Các activity thuộc gói                   | Có cho gói được phép thực hiện                             |
| readiness_rule           | Điều kiện bản vẽ mặt bằng vật tư an toàn | Có trước WorkAuthorized                                    |

## 4.3 Dictionary bổ sung theo đối tượng

| **Đối tượng** | **Trường nghiệp vụ riêng**                                | **Quy tắc bắt buộc**                                    |
|---------------|-----------------------------------------------------------|---------------------------------------------------------|
| CBS           | cost_nature, direct_indirect, capitalization_rule_ref     | Có mapping tài chính; không tự quyết chính sách vốn hóa |
| OBS           | org_type, manager_assignment, delegation_ref              | Có đơn vị chủ quản và người đại diện hiệu lực           |
| RES           | resource_class, base_uom, calendar_id, rate_version       | Giá phải có tiền tệ, kỳ hiệu lực và thành phần bao gồm  |
| PBS           | product_type, requirement_ids, handover_scope             | Có đầu ra đo được; phân biệt sản phẩm và hoạt động      |
| LBS           | location_type, chainage_from_to, coordinate_system        | Lý trình đầu không lớn hơn cuối; hệ quy chiếu rõ        |
| CTR line      | contract_id, line_no, quantity, unit_price, currency      | Duy nhất contract và revision và line_no                |
| RSK           | cause_event_effect, probability, impact, owner, response  | Có ngày đánh giá, ngưỡng và hành động tiếp theo         |
| AST           | asset_class, serial, owner_entity, operator, warranty_end | Serial bắt buộc theo loại; hồ sơ bàn giao phải liên kết |
| DATA          | domain, grain, sensitivity, retention_rule, lineage       | Có data owner và hợp đồng chất lượng                    |

## 4.4 Quy tắc mã hóa đề xuất

Khóa UUID dùng trong lưu trữ và API; mã hiển thị dùng trong hồ sơ và giao tiếp. Mã gợi nhớ không mang toàn bộ chiều phân tích. Đề xuất BR01-WBS-00320 cho work package; WBS path 03.01.01 lưu riêng và có thể thay theo phiên bản. Nếu đổi vị trí trong cây, giữ wbs_id và phát hành bản path mới. Mã cũ chuyển thành alias, không gán cho đối tượng khác.

| **Loại**        | **Mã minh họa**   | **Quy tắc**                                       |
|-----------------|-------------------|---------------------------------------------------|
| Dự án           | BR01              | Registry cấp tập đoàn; không suy tên cầu thật     |
| WBS             | BR01-WBS-00320    | Số tuần tự không chứa OBS hoặc CBS                |
| CBS             | CST-C10           | Dùng chung toàn tổ chức nếu định nghĩa thống nhất |
| Tổ chức         | ORG-BR01-SUB      | OBS riêng, liên kết pháp nhân                     |
| Vị trí          | BR01-LOC-P01      | P01 là trụ; thuộc taxonomy vị trí                 |
| Sản phẩm        | BR01-PBS-P01-PILE | Cụm cọc trụ P01                                   |
| Control account | BR01-CA-030       | Không dùng mã tài khoản kế toán                   |
| Hợp đồng        | BR01-CTR-SC01     | Loại đầu vào hoặc đầu ra lưu thuộc tính           |
| Rủi ro          | BR01-RSK-0001     | ID ổn định qua các lần đánh giá                   |
| Tài sản         | BR01-AST-0001     | Không dùng GlobalId BIM làm mã duy nhất xuyên đời |

Các mã trên là quy ước nội bộ đề xuất, không phải chuẩn ISO bắt buộc. Tiếng Việt đầy đủ dấu được giữ trong tên và mô tả. Mã không dấu nhằm trao đổi giữa hệ thống; không loại dấu khỏi nội dung nghiệp vụ. Số lượng, giá trị và ngày tháng truyền bằng dạng máy đọc, không gửi chuỗi đã định dạng như “1.000,5 triệu”.

## 4.5 Quy trình cấp và đổi mã

Người đề nghị tìm trùng trước, điền định nghĩa và phạm vi, steward kiểm tra, owner duyệt, registry cấp ID, sau đó phát sự kiện tạo mới. Hệ thống đích xác nhận đồng bộ. Chỉ cho dùng trong giao dịch khi mã Approved và đang hiệu lực. Nếu cần mã khẩn, dùng trạng thái tạm có hạn; giao dịch vẫn phải bị chặn trước công bố kỳ chính thức nếu chưa duyệt.

Đổi tên không đổi ID. Tách một gói thành hai tạo hai ID mới, lưu successor link và quyết định phân bổ phần việc còn lại. Giao dịch quá khứ giữ ID cũ; báo cáo theo cấu trúc mới dùng mapping tái trình bày riêng và nêu rõ. Gộp mã không được xóa chứng từ lịch sử.

## 4.6 Crosswalk theo mục đích

Crosswalk không chỉ là cặp mã; phải nói liên kết dùng để tra cứu, phân bổ chi phí, phân bổ ngân sách hay đo khối lượng. Một liên kết tham khảo có thể nhiều nhiều và không có trọng số. Một liên kết phân bổ cộng tiền phải có nhóm phân bổ, cơ sở tính và tổng trọng số bằng một trên từng đối tượng nguồn, phiên bản và kỳ hiệu lực.

| **Quan hệ**        | **Bản chất**                      | **Cơ sở kiểm soát**                                      |
|--------------------|-----------------------------------|----------------------------------------------------------|
| WBS với PBS        | Tạo ra sản phẩm, nhiều nhiều      | Có scope role; không tự sinh phân bổ tiền                |
| WBS với LBS        | Thực hiện tại vị trí, nhiều nhiều | Lượng theo vị trí hoặc liên kết tham chiếu               |
| WBS với OBS        | Phụ trách theo thời gian          | Một CAM chính tại CA; người hỗ trợ ở RACI                |
| WBS với CBS        | Ngân sách và actual phân loại     | Quan hệ hình thành qua dòng ngân sách hoặc chi phí       |
| BOQ với WBS        | Phạm vi hoặc lượng đo             | Dùng hệ số lượng có UOM; không lấy tỷ lệ tiền thay lượng |
| WBS với activity   | Phạm vi tiến độ                   | Mỗi activity thực thi thuộc một WP trong pilot           |
| GL với CBS         | Phân loại quản trị                | Điều kiện ưu tiên và ngày hiệu lực; xử lý ngoại lệ       |
| BIM với PBS và LBS | Biểu diễn đối tượng               | model_id, revision, object_id và quy tắc nhận diện       |

## 4.7 Ví dụ phân bổ không cộng trùng

MINH HỌA: dòng dịch vụ máy khoan có chi phí 120 triệu VND phục vụ P01 và P02. Nhật ký giờ máy được duyệt ghi 60 giờ và 40 giờ. allocation_set A01 có hai dòng 0,60 và 0,40; chi phí phân bổ là 72 và 48 triệu, tổng 120. Nếu không có nhật ký giờ máy, dùng driver tạm phải được duyệt và có hạn thay thế, không ghi như lượng đo thật.

Nếu dòng BOQ bê tông 100 m³ liên kết 60 m³ P01 và 40 m³ P02, đó là quantity mapping B01. Không nhân tiếp 0,60 vào khoản 72 triệu đã phân bổ; như vậy sẽ phân bổ hai lần. Fact cost lưu allocation_status và allocation_set_id; dashboard chỉ dùng allocated fact hoặc original fact tùy trang, không union cả hai rồi cộng.

Một amount 100 có thể có một chiều Project 100% và một chiều Department 100%. Tổng tỷ lệ giữa hai chiều là 200% không phải lỗi; quy tắc tổng 100% áp dụng trong từng kế hoạch phân bổ và từng basis. Đặc biệt khi dùng Odoo analytic plans, phải kiểm thử cấu trúc phân phối thực tế, không cộng tất cả phần trăm giữa các plan.

## 4.8 Kiểm thử crosswalk

Kiểm tra ID nguồn và đích tồn tại, hiệu lực bao phủ ngày nghiệp vụ, không chồng khoảng hiệu lực cho cùng quy tắc ưu tiên, tổng phân bổ đúng, đơn vị tương thích, không link chéo công ty trái quyền và có người duyệt. Tolerance trọng số đề xuất 0,000001; phần dư tiền do làm tròn phân về một dòng đã quy định và lưu lại, không làm biến mất khỏi tổng đối soát.

# 5 Governance và RACI

## 5.1 Cơ cấu ra quyết định đề xuất

Ban chỉ đạo sở hữu kết quả và quyết định mở rộng. PMO sở hữu phương pháp WBS, CA, baseline và kỳ kiểm soát. Tài chính kế toán sở hữu actual, chính sách kế toán và đối soát. QS và thương mại sở hữu BOQ, lượng hợp đồng và sổ thay đổi. Kỹ thuật cùng QA/QC sở hữu chất lượng bằng chứng. Ban dữ liệu sở hữu chuẩn dùng chung; CNTT sở hữu vận hành kỹ thuật và bảo mật. Các tên gọi là vai trò, cần CC1 ánh xạ phòng ban thực tế.

Hội đồng thay đổi CCB quyết định trong phạm vi được ủy quyền; không thay thế người có thẩm quyền ký hợp đồng hoặc duyệt ngân sách. Trong cấu hình, một yêu cầu có approval_policy_id xác định ai có quyền theo loại tác động. Chưa xác minh phân cấp ủy quyền thì không mặc định giám đốc dự án được duyệt mọi mức tiền.

## 5.2 Ma trận RACI thực thi

R là thực hiện, A là chịu trách nhiệm cuối cùng, C là tham vấn, I là nhận thông tin. Mỗi dòng dưới đây có đúng một A. Vai trò QA gồm chuyên môn nghiệm thu; tài chính không phê duyệt thay chất lượng.

| **Hoạt động**                     | **A**                                | **R**                         | **C và I**                                  |
|-----------------------------------|--------------------------------------|-------------------------------|---------------------------------------------|
| Phê duyệt phạm vi pilot           | Sponsor                              | PMO                           | C BQLDA, tài chính, CNTT; I đơn vị tham gia |
| Phát hành WBS dictionary          | PMO lead                             | Planner, QS                   | C BQLDA, kỹ thuật; I kế toán                |
| Phát hành CBS và mapping GL       | Kế toán trưởng được phân công        | Finance steward               | C QS, PMO; I CNTT                           |
| Phê duyệt baseline tích hợp       | Người có thẩm quyền theo ủy quyền    | PMO và CAM                    | C tài chính, QS, kỹ thuật; I các đội        |
| Xác nhận lượng đạt điều kiện EV   | QA lead được giao                    | Kỹ sư hiện trường, QS         | C CAM; I PMO                                |
| Ghi nhận actual và accrual        | Finance lead                         | Kế toán dự án                 | C QS, CAM; I PMO                            |
| Chốt báo cáo quản trị kỳ          | Giám đốc dự án được giao             | PMO controller                | C Finance, QA; I Sponsor                    |
| Phê duyệt change request          | Chủ thẩm quyền trong approval policy | Change manager                | C các owner bị ảnh hưởng; I CNTT            |
| Sửa định nghĩa dữ liệu dùng chung | Data owner                           | Data steward                  | C PMO, Finance, CNTT; I người dùng          |
| Phát hành tích hợp                | IT service owner                     | Nhóm phát triển và vận hành   | C data owner, security; I PMO               |
| Nghiệm thu nghiệp vụ hệ thống     | Business owner                       | Nhóm UAT độc lập với xây dựng | C các owner; I nhà triển khai               |
| Cho phép go live                  | Sponsor                              | Release manager               | C nghiệp vụ, CNTT, kiểm soát; I người dùng  |

## 5.3 Nhịp điều hành và escalation

Hằng ngày: đội thi công ghi tiến độ và chứng từ, steward kiểm tra lỗi mới, vận hành theo dõi hàng lỗi. Hằng tuần: CAM và planner cập nhật lookahead, forecast và rủi ro, PMO giải quyết mapping chưa rõ. Hằng tháng: finance và PMO chốt cùng cutoff, duyệt variance narrative và snapshot. Mỗi quý: ban chỉ đạo đánh giá lợi ích, chi phí vận hành và mức sẵn sàng nhân rộng.

Đề xuất SLA: lỗi gây sai số công bố hoặc lộ dữ liệu xử lý như sự cố P1, xác nhận tiếp nhận trong 30 phút ở giờ hỗ trợ đã cam kết; lỗi chặn chốt kỳ trong 4 giờ; lỗi mã không ảnh hưởng báo cáo trong hai ngày làm việc. Đây là mức mục tiêu cần xác nhận nguồn lực, không phải dịch vụ đã được cung cấp. Khi quá hạn, tự động chuyển owner cấp trên kèm phạm vi ảnh hưởng.

## 5.4 Phân quyền và kiểm toán

Quyền theo vai trò kết hợp phạm vi công ty, dự án và loại dữ liệu. Người nhập lượng không tự duyệt lượng của mình. Người thay mapping không được âm thầm công bố lại báo cáo đã khóa. Tài khoản tích hợp tách theo môi trường và chức năng, không dùng tài khoản admin chung. Nhật ký cần người, hành động, trước sau, thời gian, correlation_id và lý do.

Thực hiện rà soát quyền khi điều chuyển hoặc nghỉ việc và rà soát định kỳ theo lịch được CC1 chấp thuận. Dữ liệu lương cá nhân, giá dự thầu và tranh chấp có lớp Restricted; dashboard tổng hợp không được phép drill-through tới dữ liệu hạn chế nếu người xem không có quyền. Kiểm thử cả xuất Excel, API và AI retrieval.

# 6 Control accounts và baseline tích hợp

## 6.1 Cách thiết kế control account

CA là điểm giao quản trị giữa phạm vi WBS và đơn vị OBS chịu trách nhiệm; không phải mọi ô giao nhau đều tạo CA. CA cần đủ giá trị và rủi ro để một CAM giải trình, đồng thời không quá lớn để che sai lệch. Trong pilot, mỗi WorkPackage thuộc một CA ở một baseline. Một CA có thể chứa nhiều WP và planning package; không đếm ngân sách CA và ngân sách WP như hai khoản.

Hồ sơ CA gồm ca_id, scope_wbs_id, obs_id, cam_assignment_id, start_finish, BAC, WP list, PP list, EV methods, cost collection rules, risk links, baseline_id và approval. Ngân sách CA bằng tổng dòng ngân sách các gói trong CA. Ngân sách dự án bằng tổng CA cộng ngân sách chưa phân bổ được quản lý tách biệt, nếu chính sách pilot cho phép.

## 6.2 Cấu phần bộ baseline

| **Cấu phần** | **Nội dung khóa**                           | **Bằng chứng kiểm tra**                          |
|--------------|---------------------------------------------|--------------------------------------------------|
| Phạm vi      | WBS dictionary, PBS và yêu cầu              | Bao phủ phạm vi và danh sách loại trừ            |
| Tiến độ      | Activity, logic, lịch, mốc, baseline dates  | Không vòng lặp; đường găng và ràng buộc có lý do |
| Ngân sách    | Lượng, giá chi phí, phân kỳ theo WP CBS     | Tổng phân kỳ bằng BAC và cân với CA              |
| Đo lường     | EV method, milestone weights, acceptance    | Có bằng chứng độc lập và không đo hai lần        |
| Mapping      | BOQ, GL CBS, LBS, contract và BIM cần thiết | Có phiên bản và hiệu lực phù hợp                 |
| Tổ chức      | CAM, RACI, quyền phê duyệt                  | Không thiếu A và không xung đột nhiệm vụ         |

## 6.3 Trình tự phê duyệt baseline

Bước 1 chốt yêu cầu và phạm vi; bước 2 phân rã WBS và xác định CA; bước 3 xây mạng tiến độ; bước 4 lập chi phí và phân kỳ; bước 5 kiểm thử cách đo; bước 6 review tích hợp bởi PMO, Finance, kỹ thuật và thương mại; bước 7 người có thẩm quyền phê duyệt; bước 8 phát snapshot và quyền WorkAuthorized. Mỗi bước có checklist và nhật ký kết quả, không chấp nhận ký một trang tổng mà thiếu dữ liệu nền.

Tại Integrated Baseline Review, CAM phải giải thích công việc làm thế nào, nguồn lực nào, ràng buộc nào, đo ra sao và chi phí ghi nhận từ đâu. Các khoản chưa rõ có owner và ngày giải quyết. Công việc tương lai trong PP không được phát lệnh thực hiện cho tới khi có WP và cơ sở ngân sách.

## 6.4 Dự phòng và forecast

Chính sách đề xuất phân biệt ngân sách phạm vi được duyệt trong PMB, dự phòng rủi ro nằm trong phạm vi đã phân bổ và management reserve do cấp quản lý giữ ngoài PMB. Tổng ngân sách quản lý có thể bằng PMB cộng MR theo chính sách nội bộ. Giá trị hợp đồng còn có biên lợi nhuận, thuế và điều kiện khác, nên không lấy nó làm BAC.

Forecast EAC được cập nhật khi có bằng chứng mới dù chưa duyệt đổi baseline. Tách estimate_change với baseline_change: biết dự án sẽ vượt chi phí không có nghĩa được nâng BAC để xóa CV. Mỗi forecast có phương pháp, ngày đánh giá, giả định, owner và khoảng bất định khi phù hợp.

# 7 EVM và kiểm soát chi phí tiến độ

## 7.1 Định nghĩa vận hành

PV là giá trị ngân sách của công việc theo kế hoạch phải hoàn thành tới ngày chốt. EV là giá trị ngân sách của công việc đã đạt điều kiện đo tới ngày chốt. AC là chi phí tương ứng đã phát sinh theo cơ sở chi phí quản trị thống nhất. BAC là ngân sách khi hoàn thành của phạm vi đang xét. Toàn bộ phải dùng cùng phạm vi, cutoff và baseline. Phương pháp tính sau là thiết kế áp dụng thông dụng; tham chiếu phạm vi EVM ở S02 và hướng dẫn chi phí S04.

| **Chỉ số**                | **Công thức**                            | **Diễn giải và giới hạn**                                           |
|---------------------------|------------------------------------------|---------------------------------------------------------------------|
| CV                        | EV trừ AC                                | Âm là vượt chi phí so với giá trị đạt được                          |
| SV                        | EV trừ PV                                | Là chênh lệch theo tiền ngân sách, không phải ngày chậm             |
| CPI                       | EV chia AC                               | Không tính khi AC bằng 0; không lấy trung bình CPI của các gói      |
| SPI                       | EV chia PV                               | Không tính khi PV bằng 0; cuối dự án có thể về 1 dù trễ             |
| EAC theo CPI              | BAC chia CPI                             | Chỉ khi hiệu suất chi phí quá khứ đại diện phần còn lại             |
| EAC theo kế hoạch còn lại | AC cộng BAC trừ EV                       | Khi sai lệch đã phát sinh là ngoại lệ và phần còn lại theo kế hoạch |
| EAC kết hợp               | AC cộng (BAC trừ EV) chia (CPI nhân SPI) | Chỉ dùng nếu tác động chi phí và tiến độ có cơ sở, tránh mặc định   |
| EAC từ dưới lên           | AC cộng ETC đánh giá lại                 | Ưu tiên khi có thay đổi biện pháp, năng suất hoặc phạm vi           |
| VAC                       | BAC trừ EAC                              | Dự báo dư hoặc thiếu ngân sách                                      |
| TCPI theo BAC             | (BAC trừ EV) chia (BAC trừ AC)           | Mẫu số không dương phải đánh giá lại, không báo tỷ lệ đẹp giả       |

Ở cấp dự án, CPI bằng tổng EV chia tổng AC và SPI bằng tổng EV chia tổng PV, trên cùng kỳ và baseline. Không cộng hoặc lấy trung bình số học các tỷ lệ. Dữ liệu cumulative chỉ lấy snapshot của ngày chốt, không cộng lũy kế các tháng. Dữ liệu periodic có thể cộng theo thời gian nếu không trùng phạm vi.

## 7.2 Phương pháp earned value

| **Phương pháp**    | **Áp dụng đề xuất**                | **Điều kiện kiểm soát**                                           |
|--------------------|------------------------------------|-------------------------------------------------------------------|
| Quantity           | Sản phẩm đồng nhất có đơn vị đo    | EV bằng lượng đạt điều kiện nhân đơn giá ngân sách; giới hạn BAC  |
| Weighted milestone | Hồ sơ hoặc kết cấu có giai đoạn rõ | Trọng số duyệt trước, tổng 100%; milestone có bằng chứng          |
| 0_100              | Gói ngắn và nhỏ                    | Chỉ ghi EV khi hoàn tất, không dùng cho gói dài che khuất tiến độ |
| LOE                | Điều hành hỗ trợ theo thời gian    | Hiển thị tách khỏi sản lượng; không dùng để che trễ thi công      |

Ví dụ milestone cọc: chuẩn bị hồ sơ 10%, khoan đạt 30%, lắp cốt thép 20%, đổ bê tông 25%, kiểm tra chấp nhận 15%. Đây chỉ là minh họa cách phân trọng số, không phải quy định kỹ thuật hoặc khuyến nghị nhận EV cọc cụ thể. Dự án phải chọn giữa EV theo cọc đã đủ điều kiện và milestone có bằng chứng; không ghi cả hai cho cùng phạm vi.

## 7.3 Actual và các khoản dễ nhầm

AC cần bao gồm chi phí phát sinh tương ứng với phạm vi EV, kể cả phần chưa nhận hóa đơn nếu có accrual được duyệt. Tiền tạm ứng, tiền thanh toán và retention là dòng tiền hoặc nghĩa vụ khác, không tự động là chi phí cùng kỳ. Vật tư mua về kho chưa sử dụng không được tự động ghi AC của WP theo cùng cách vật tư đã lắp; tài chính xác nhận chính sách áp dụng và nhất quán với phương pháp EV.

Ví dụ có hóa đơn ghi nhận 18 triệu và accrual 4 triệu chưa hóa đơn thì AC quản trị là 22 triệu. Kỳ sau nhận hóa đơn 4 triệu, phải đảo hoặc bù accrual theo quy tắc, tránh cộng thành 26 triệu. Giao dịch đảo có reversal_of_id; số chốt kỳ cũ giữ nguyên trừ khi quy trình mở kỳ được phê duyệt.

Open commitment là nghĩa vụ đã cam kết nhưng chưa được phản ánh trong actual hoặc accrual theo cùng phạm vi. Để ước tính rủi ro ngân sách, dùng actual cộng cam kết còn lại cộng dự báo chưa đặt hàng. Không cộng full PO vào AC khi PO đã có hóa đơn một phần. Mỗi contract line cần đối chiếu committed, received, invoiced, accrued và paid theo cơ sở riêng.

## 7.4 Close calendar đề xuất

| **Mốc tương đối** | **Hoạt động**                              | **Người chịu trách nhiệm**           |
|-------------------|--------------------------------------------|--------------------------------------|
| D ngày cuối kỳ    | Chốt cutoff hiện trường và thời gian nguồn | BQLDA và PMO                         |
| D cộng 1          | Nộp lượng, nhật ký, hồ sơ nghiệm thu       | Kỹ thuật, QS, QA                     |
| D cộng 2          | Đối chiếu chi phí, accrual và phân bổ      | Finance và CAM                       |
| D cộng 3          | Chạy DQ, so tổng, kiểm tra variance        | Steward và PMO controller            |
| D cộng 4          | CAM giải trình và forecast                 | CAM, planner, QS                     |
| D cộng 5          | Phê duyệt snapshot và công bố              | Giám đốc dự án và Finance theo quyền |

Nếu bằng chứng chưa đủ, báo cáo phải ghi provisional và danh sách thiếu; không tô màu đạt khi dữ liệu chậm. Công bố chính thức cần snapshot_id, baseline_id, cutoff, phiên bản mô hình và chữ ký người duyệt. Khoản đến muộn được ghi kỳ sau có đánh dấu late adjustment hoặc mở lại kỳ qua change control.

## 7.5 Phân tích sai lệch và hành động

Mỗi sai lệch trọng yếu phải tách nguyên nhân do lượng, đơn giá, năng suất, thời gian, phân bổ hay lỗi dữ liệu. Narrative cần mô tả sự kiện, tác động kỳ và lũy kế, tác động forecast, hành động, owner và ngày hoàn thành. “Chậm do khách quan” không đủ để đóng báo cáo. Ngưỡng đề xuất là CV hoặc SV vượt 5% BAC của CA hoặc vượt mức tuyệt đối do dự án duyệt; không xem ngưỡng đó như chuẩn bắt buộc quốc tế.

Hành động phục hồi không được sửa số EV quá khứ để làm biến mất sai lệch. Nếu phát hiện sai đo, tạo correction có bằng chứng, phê duyệt và báo cáo tác động. Thay đổi kế hoạch thực hiện không luôn là thay đổi baseline; cần phân biệt forecast và lịch tác nghiệp.

# 8 Quy trình nghiệp vụ từ hợp đồng đến bàn giao

## 8.1 Khởi tạo dự án và giao công việc

Đầu vào là hợp đồng hoặc quyết định giao việc, scope statement, danh mục yêu cầu và kế hoạch huy động. PMO tạo dự án, pháp nhân và calendar; QS tạo BOQ cùng WBS; Finance duyệt CBS mapping; kỹ thuật xác nhận PBS LBS. Đầu ra là charter, dictionary, baseline và CA. Chặn WorkAuthorized nếu thiếu CAM, ngân sách, điều kiện an toàn hoặc hồ sơ thiết kế cần thiết theo quy trình chuyên môn.

## 8.2 Mua sắm và thầu phụ

Purchase requisition phải chỉ ra phạm vi, WP hoặc CA, CBS dự kiến, thời điểm cần và hợp đồng liên quan. Kiểm tra ngân sách tại lúc đề nghị và lúc cam kết, vì hai mốc có thể khác. Khi chọn thầu phụ, giữ line mapping cho phạm vi đo; nhận khối lượng có bằng chứng trước xử lý hóa đơn. Đối chiếu đơn hàng, nhận hàng hoặc xác nhận dịch vụ, và hóa đơn theo loại giao dịch.

Thay đổi PO phải lưu revision và lý do. Hủy phần còn lại giải phóng commitment nhưng không xóa nhận hàng hoặc hóa đơn đã có. Nếu một line phục vụ nhiều WBS, phân bổ theo driver được duyệt từ thời điểm kế hoạch và điều chỉnh theo actual có kiểm soát.

## 8.3 Hiện trường và nghiệm thu khối lượng

Đội thi công ghi daily log gồm WP, vị trí, tài nguyên, lượng, thời gian và vướng mắc. QS tổng hợp measurement record; QA xác nhận bằng chứng theo inspection plan; CAM nhận tiến độ đã kiểm tra. Đầu ra gồm accepted_quantity và acceptance_record_id. Khối lượng đã thi công, đã nghiệm thu nội bộ, đã được chủ đầu tư chấp nhận và đã thanh toán là bốn trạng thái riêng.

EV dùng trạng thái nào phải quy định trước trong dictionary. Nghiệm thu nội bộ có thể đủ cho EV quản trị nhưng chưa tạo quyền xuất hóa đơn. Rework lưu chi phí vào phạm vi đúng và mã nguyên nhân; khối lượng làm lại không được cộng thêm EV nếu không làm tăng đầu ra đạt yêu cầu.

## 8.4 Thanh toán và cash flow

QS lập hồ sơ thanh toán theo contract line, lượng được chấp nhận và điều kiện hợp đồng. Tài chính theo dõi hóa đơn, thu tiền, giữ lại, tạm ứng và hoàn ứng. Báo cáo cần phân biệt earned progress, certified revenue hoặc billing theo chính sách, cash in, cash out. Chính sách ghi nhận doanh thu và thuế phải do chuyên môn CC1 xác nhận; tài liệu không quy định thay.

Cash forecast theo ngày dự kiến thu chi, điều khoản và lịch nghiệm thu. EAC chi phí không đủ để suy dòng tiền; cần thời gian thanh toán và nghĩa vụ hợp đồng. Nếu có ngoại tệ, lưu nguyên tệ, tỷ giá nguồn, ngày tỷ giá và giá trị quy đổi; báo cáo constant-currency chỉ là góc nhìn phân tích riêng.

## 8.5 Bàn giao công trình và tài sản

Hồ sơ bàn giao liên kết PBS, asset_id, vị trí, bản vẽ hoàn công, chứng chỉ, hướng dẫn vận hành, bảo hành và danh sách tồn tại. BQLDA xác nhận nghĩa vụ hợp đồng, kỹ thuật xác nhận sản phẩm, đơn vị vận hành xác nhận thông tin sử dụng. Không đóng dự án chỉ vì chi phí đã đăng sổ; cần kiểm tra nghĩa vụ bảo hành, claim, retention và hồ sơ chưa đóng.

# 9 ERD logic và kiến trúc dữ liệu

## 9.1 Các lớp lưu trữ đề xuất

Lớp nguồn giữ giao dịch nghiệp vụ. Lớp landing nhận dữ liệu nguyên trạng với batch_id và hash, không sửa lại nguồn. Lớp chuẩn hóa kiểm tra ID, UOM, thời gian, trạng thái và mapping. Lớp dữ liệu quản trị tạo fact và dimension theo grain xác định. Lớp semantic công bố measure thống nhất. Hồ sơ và mô hình BIM nằm trong CDE hoặc kho tài liệu có version; warehouse lưu khóa và metadata, không bắt buộc sao chép mọi tệp lớn.

Một source of truth được xác định cho từng đối tượng và thuộc tính. ERP là nguồn chuẩn cho bút toán đã đăng; PMIS cho baseline và EV đã duyệt; CDE cho phiên bản tài liệu và mô hình phát hành. Nếu cùng một tên dự án tồn tại ở ba hệ thống, registry sở hữu project_id, còn tên hiển thị có quy tắc đồng bộ. Không cho tích hợp hai chiều tự cập nhật một thuộc tính không có quy tắc ưu tiên.

## 9.2 ERD logic theo quan hệ và lực lượng

Ký hiệu 1 tới N nghĩa là một bản ghi cha có nhiều con, mỗi con chỉ thuộc một cha theo quan hệ đó. N tới N được triển khai qua bảng nối; một đường nối không mặc nhiên cho phép cộng tiền.

| **Quan hệ**                           | **Lực lượng**                               | **Khóa và điều kiện**                                           |
|---------------------------------------|---------------------------------------------|-----------------------------------------------------------------|
| LegalEntity tới Project               | 1 tới N cho pháp nhân quản lý               | project.managing_entity_id; đối tác liên danh qua project_party |
| Project tới WBSNode                   | 1 tới N                                     | wbs.project_id; hierarchy theo wbs_version                      |
| WBSNode tới WBSNode                   | 1 tới N cha con                             | hierarchy_edge với baseline/version; không vòng                 |
| ControlAccount tới WorkPackage        | 1 tới N trong baseline                      | wp_ca_assignment; không gán hai CA cùng hiệu lực                |
| OBSUnit tới ControlAccount            | 1 tới N theo hiệu lực                       | ca.obs_id; cam_assignment lưu người                             |
| WorkPackage tới ScheduleActivity      | 1 tới N trong pilot                         | activity.wbs_id; summary activity không ghi EV                  |
| WorkPackage tới PBS và LBS            | N tới N                                     | wbs_product_link và wbs_location_link                           |
| Contract tới ContractLine             | 1 tới N                                     | contract_line.contract_id và revision                           |
| ContractLine tới WorkPackage          | N tới N                                     | contract_wbs_link có purpose và quantity_basis                  |
| CostEntry tới CostAllocation          | 1 tới N                                     | allocation.cost_entry_id; bảo toàn tổng                         |
| WorkPackage và CBS tới BudgetLine     | Mỗi chiều 1 tới N                           | budget_line có baseline, period, amount                         |
| WorkPackage tới ProgressRecord        | 1 tới N                                     | quantity hoặc milestone, acceptance FK                          |
| Risk tới WorkPackage                  | N tới N                                     | risk_impact_link không dùng để cộng actual                      |
| PBS tới Asset                         | 1 tới N hoặc N tới N theo thiết kế bàn giao | product_asset_link nếu cấu phần lắp ghép phức tạp               |
| DocumentRevision tới AcceptanceRecord | N tới N                                     | evidence_link; lưu revision bất biến                            |

## 9.3 Danh mục thực thể và grain

| **Thực thể**        | **Grain và khóa chính**                  | **Thuộc tính quan trọng**                                      |
|---------------------|------------------------------------------|----------------------------------------------------------------|
| project             | Một dự án, project_id                    | code, managing_entity, currency, timezone, status              |
| structure_node      | Một ID khái niệm, node_id                | structure_type, project_id, business_code                      |
| node_version        | Một phiên bản nút                        | version_id, node_id, name, valid_from_to, status               |
| hierarchy_edge      | Một quan hệ cha con trong version        | tree_version, parent_version, child_version                    |
| control_account     | Một CA ổn định                           | ca_id, project_id, code                                        |
| ca_version          | Một CA trong baseline                    | ca_version_id, baseline_id, scope, obs, CAM                    |
| baseline            | Một bộ được phê duyệt                    | baseline_id, type, revision, effective_date, approval_ref      |
| budget_line         | Một WP CBS kỳ baseline tiền tệ           | budget_line_id, wbs_version_id, cbs_id, period_id, amount      |
| schedule_activity   | Một hoạt động trong schedule version     | activity_id, wbs_id, calendar_id, planned_actual_dates         |
| dependency          | Một cung logic                           | predecessor_id, successor_id, type, lag, version               |
| cost_entry          | Một dòng nguồn hoặc accrual              | source_instance, source_model, source_id, revision, cost_basis |
| cost_allocation     | Một phần của dòng chi phí                | allocation_id, cost_entry_id, allocation_set, WP, CBS, amount  |
| progress_record     | Một lượng tăng thêm hoặc milestone event | progress_id, WP, date, quantity, UOM, evidence, reversal       |
| ev_snapshot         | Một WP kỳ baseline phương pháp           | snapshot_id, WP, period, baseline, PV, EV, AC                  |
| contract_line       | Một dòng ở phiên bản hợp đồng            | contract_line_id, contract_revision, UOM, quantity, price      |
| commitment_snapshot | Một dòng hợp đồng tại kỳ                 | line_id, period, committed_remaining, basis                    |
| acceptance_record   | Một kết quả kiểm tra được ký             | id, type, status, signer, accepted_date, evidence_links        |
| change_request      | Một đề nghị thay đổi                     | id, type, impact, decision, effective_at, approval_ref         |
| mapping_rule        | Một quy tắc ánh xạ có phiên bản          | rule_id, source_target_type, purpose, priority, validity       |
| document_revision   | Một bản tài liệu bất biến                | doc_id, revision_id, URI, hash, classification                 |
| model_object        | Một đối tượng trong phiên bản mô hình    | model_revision_id, object_id, GlobalId, PBS, LBS               |

Lược đồ này là logic để thiết kế vật lý. Nhóm phát triển được tách bảng theo miền nhưng phải giữ grain và tính truy vết. Không dùng JSON tự do thay tất cả FK rồi bỏ kiểm tra. Kiểu decimal cho tiền và khối lượng cần độ chính xác theo hợp đồng; UTC cho thời điểm hệ thống, ngày địa phương cho cutoff nghiệp vụ.

## 9.4 Ràng buộc logic cần hiện thực

Khóa ngoại bắt buộc tại Approved; không có FK mồ côi. Unique nguồn gồm source_instance, source_model, source_record_id và source_revision; chỉ source_id không đủ khi có nhiều cơ sở dữ liệu. Dòng allocation cộng về original amount trong cùng currency và basis. Baseline Approved không được update in place. Progress quantity có thể âm khi là reversal có tham chiếu, nhưng tổng được chấp nhận không vượt lượng được duyệt nếu chưa có thay đổi.

Số phiên bản tăng không chứng minh thứ tự nghiệp vụ nếu dữ liệu đến muộn. Lưu event_time, received_time và accounting_date riêng. Soft delete nguồn chuyển thành trạng thái retired hoặc reversal tùy loại; không cascade delete lịch sử chi phí. Thao tác gộp hoặc tách phải có lineage.

## 9.5 Lịch sử hiệu lực và lịch sử ghi nhận

Valid time mô tả khi sự thật nghiệp vụ có hiệu lực; system time mô tả khi hệ thống biết sự thật đó. Khi đội phụ trách thay đổi hiệu lực ngày 1 nhưng được nhập ngày 5, báo cáo hiện tại có thể dùng ngày 1, còn báo cáo “đã biết tại ngày 3” vẫn phải tái dựng được. Snapshot kỳ khóa và audit_log giúp thực hiện yêu cầu này ngay cả khi chưa triển khai cơ sở dữ liệu bitemporal đầy đủ.

Trong warehouse dùng SCD Type 2 cho thuộc tính cần giữ lịch sử như tổ chức hoặc nhóm báo cáo. Fact trỏ version key có hiệu lực phù hợp. Một bản đồ “cơ cấu hiện tại” có thể được cung cấp riêng, nhưng phải gắn nhãn tái trình bày để tránh thay số lịch sử không thông báo.

## 9.6 Mô hình sao cho Power BI

FactCostAllocation có grain dòng nguồn đã phân bổ, ngày, WP, CBS, công ty và tiền tệ. FactBudget có grain WP CBS kỳ baseline. FactProgressEvent giữ lượng tăng thêm và bằng chứng. FactEVSnapshot có grain WP ngày chốt baseline snapshot. FactContractSnapshot theo line và kỳ. DimProject, DimWBSVersion, DimCBS, DimOBSVersion, DimDate, DimCurrency và DimBaseline dùng chung theo quan hệ được định nghĩa.

Không nối FactCost trực tiếp với FactProgress qua WBS rồi cộng tiền: một dòng cost có thể bị lặp cho từng progress event. Dùng dimension trung gian với lọc một chiều mặc định. Bridge chỉ dùng trong measure có quy tắc allocation hoặc cho lựa chọn phạm vi; không bật quan hệ hai chiều hàng loạt. Các chỉ tiêu cumulative lấy kỳ mới nhất trong ngữ cảnh được chọn, không SUM qua nhiều snapshot.

# 10 ERP Odoo PMIS BIM và Power BI

## 10.1 Phân công hệ thống

| **Miền**              | **Nguồn chuẩn đề xuất**          | **Dữ liệu xuất và nhận**                                                 |
|-----------------------|----------------------------------|--------------------------------------------------------------------------|
| Kế toán và công nợ    | ERP                              | Xuất posted actual, currency, reversal; nhận project và mapping đã duyệt |
| Mua sắm và kho        | ERP                              | Xuất PO, receipt, material issue; nhận mã và nhu cầu                     |
| Phạm vi ngân sách EVM | PMIS hoặc dịch vụ quản trị riêng | Xuất baseline, WP, CA, EV; nhận actual và commitments                    |
| Tiến độ               | Công cụ lập tiến độ kết nối PMIS | Xuất activity, logic, dates, progress version                            |
| Hồ sơ và mô hình      | CDE và BIM                       | Xuất metadata, revision, status, object link                             |
| Danh mục dùng chung   | Registry MDM                     | Xuất ID, version, alias, hierarchy và mapping                            |
| Báo cáo               | Warehouse và Power BI            | Nhận dữ liệu đã kiểm soát; không sửa trực tiếp sổ nguồn                  |
| AI                    | Lớp truy xuất được phân quyền    | Nhận dữ liệu và hồ sơ được phép; chỉ trả đề xuất có dẫn chứng            |

## 10.2 Thiết kế Odoo có điều kiện theo phiên bản

Nguồn S15 xác nhận Odoo 19 có analytic accounts, analytic plans và phân phối chi phí; plan có thể đặt applicability bắt buộc. Nguồn S16 mô tả External JSON-2 API của Odoo 19. Tài liệu dùng Odoo 19 làm tham chiếu thiết kế, không khẳng định CC1 đang chạy bản này hoặc đây là bản mới nhất. Trước xây dựng phải xác nhận Community hay Enterprise, hosting, gói quyền API, module cài và phiên bản patch.

Đề xuất analytic plan cho Project và Control Account hoặc nhóm chi phí quản trị phù hợp. Không tạo ngay mọi WP thành analytic account nếu số lượng quá lớn; thử hai phương án trên mẫu thật: analytic account tới CA và trường WP riêng, hoặc analytic account tới WP khi quy mô cho phép. Quyết định dựa trên tốc độ nhập liệu, khả năng bắt buộc phân loại và đối soát, không chỉ tính linh hoạt.

| **Nghiệp vụ**       | **Đối tượng Odoo tham chiếu**       | **Cách thiết kế và giới hạn**                                           |
|---------------------|-------------------------------------|-------------------------------------------------------------------------|
| Pháp nhân           | res.company                         | Mapping tới legal_entity_id; kiểm tra record rules                      |
| Dự án và công việc  | project.project, project.task       | Không mặc nhiên coi mọi task là WBS đã duyệt                            |
| Tài khoản phân tích | account.analytic.account và plan    | Mapping CA hoặc WP tùy fit gap; kiểm thử nhiều plan                     |
| Dòng bút toán       | account.move.line                   | Chỉ lấy trạng thái và cost basis được duyệt; tránh lặp journal lines    |
| Đơn mua             | purchase.order và line              | Dòng commitment liên kết contract, CA, WP                               |
| Kho                 | stock.move và valuation theo module | Quyết định lúc ghi chi phí, không cộng receipt và GL trùng nhau         |
| Nhân công           | timesheet theo module               | Giờ công và valuation cần nguồn rate và duyệt                           |
| Cấu trúc riêng      | Module mở rộng hoặc dịch vụ MDM     | WBS version, CA baseline, evidence và change control thường cần fit gap |

Tên model là tham chiếu cần kiểm tra trong database đích; không coi bảng này là cam kết tính năng sẵn có cho mọi bản Odoo. Thiết kế chứng minh bằng sandbox có module đúng, bằng chứng UI, export và API. Các yêu cầu EVM, baseline bất biến, contract claims và mapping nhiều chiều không được mặc định đáp ứng chỉ nhờ cài Project.

## 10.3 Nguyên tắc cấu hình và mở rộng Odoo

Ưu tiên cấu hình trường, analytic applicability và quyền trước khi viết module. Nếu cần custom module, có migration scripts, kiểm thử quyền, dữ liệu nhiều công ty và kế hoạch nâng cấp. Không ghi trực tiếp bảng kế toán qua database để tránh bỏ qua business rules. Giao dịch financial được tạo qua giao diện hoặc API hỗ trợ, và duyệt theo người có quyền.

Khi dùng JSON-2, adapter phải kiểm tra khả năng API và phương thức thực tế của bản cài. Mỗi lời gọi có phạm vi giao dịch riêng theo tài liệu Odoo; các thao tác phải nguyên tử cần phương thức server được thiết kế và kiểm thử. Không đóng đinh lịch ngừng RPC cũ khi chưa kiểm tra bản phát hành mục tiêu. Chìa khóa API nằm trong secret store và không ghi vào hồ sơ Word hoặc payload ví dụ.

## 10.4 Fit gap cần nhà triển khai trả lời

| **Yêu cầu**                            | **Minh chứng phải nộp**                     | **Quyết định nếu chưa đáp ứng**             |
|----------------------------------------|---------------------------------------------|---------------------------------------------|
| Bắt buộc Project và CA khi ghi chi phí | Thử giao dịch thiếu mã bị chặn              | Bổ sung validation hoặc workflow kiểm soát  |
| Phân phối nhiều plan                   | Một giao dịch được đối soát không nhân tiền | Chọn lại mô hình analytic                   |
| Chốt baseline và snapshot EVM          | Thử sửa bản duyệt bị chặn                   | Module hoặc dịch vụ PMIS riêng              |
| Multi company và liên danh             | Tài khoản công ty A không xem B             | Sửa quyền và kiểm thử lại                   |
| Accrual đảo kỳ sau                     | Đối soát chứng từ gốc và reversal           | Bổ sung liên kết accrual và close checklist |
| Upgrade                                | Chạy bộ regression trên bản đích            | Chưa nâng production khi chưa đạt           |

## 10.5 PMIS và lập tiến độ

PMIS quản lý baseline, CA, readiness, progress, risk và thay đổi. Công cụ tiến độ giữ logic mạng và calendar, không dùng bảng Excel thiếu logic làm nguồn dự báo đường găng. Export phải chứa activity_id ổn định, schedule_version, wbs_id, predecessor, relationship_type, lag, calendar, baseline dates và current forecast dates.

Thay ID activity khi cập nhật sẽ làm mất lịch sử. Nếu phải tách activity, tạo predecessor successor lineage giữa các bản. Mốc đã hoàn thành chỉ được đảo qua correction. Update tiến độ phải kiểm tra actual start trước actual finish, phần trăm trong miền cho phép và việc bắt đầu có điều kiện sẵn sàng; ngoại lệ được ghi nhận, không tự sửa ngày thực tế cho hợp lịch.

## 10.6 BIM và quản lý thông tin

S17 mô tả ISO 19650-1 về quản lý thông tin xuyên vòng đời. S18 là nguồn buildingSMART cho IFC và các tiêu chuẩn trao đổi. Thiết kế CC1 đề xuất yêu cầu thông tin cụ thể trước khi đòi mọi mô hình đạt một mức chi tiết chung: đối tượng nào, thuộc tính nào, mục đích nào, thời điểm nào và ai chấp thuận. Định dạng IFC phải thử khả năng xuất nhập của công cụ dự án; tham chiếu IFC 4.3 cho hạ tầng không bảo đảm mọi phần mềm hỗ trợ đủ.

Mỗi package mô hình có model_id, revision, status, author, coordinate_system, classification và hash. Đối tượng cần PBS, LBS, loại cấu kiện, lượng cùng UOM và mapping WP khi dùng cho 4D hoặc 5D. Quantity takeoff là nguồn hỗ trợ; QS kiểm tra quy tắc đo, openings, deductions và đơn vị trước khi dùng cho thanh toán hoặc ngân sách.

4D liên kết mô hình với activity; 5D liên kết lượng và giá. Không dùng số đối tượng mô hình đã tô màu hoàn thành làm EV nếu đối tượng có giá trị khác nhau hoặc chưa nghiệm thu. IDS có thể mô tả yêu cầu thông tin máy kiểm tra được, nhưng nội dung yêu cầu vẫn do chủ nghiệp vụ định nghĩa. Hồ sơ kiểm tra lỗi hình học, phân loại và thuộc tính phải tách với nghiệm thu kết cấu.

## 10.7 Power BI và hợp đồng chỉ số

Mỗi measure có tên, công thức, grain, nguồn, baseline, cutoff, bộ lọc và người sở hữu. Trang tổng quan cần hiển thị thời điểm làm mới, ngày chốt nghiệp vụ và trạng thái provisional hoặc final. Drill-through đi từ dự án tới CA, WP, cost allocation và chứng từ nguồn có quyền xem. Cùng một KPI không được định nghĩa khác trên báo cáo lãnh đạo và dự án.

Nguồn S19 mô tả RLS và các giới hạn liên quan vai trò workspace. Thiết kế yêu cầu người tiêu thụ dữ liệu sử dụng vai trò phù hợp, kiểm thử tài khoản thật và cả chức năng export; không giả định RLS chặn người có quyền quản trị workspace. Tách workspace dev test prod và danh mục người được phép phát hành semantic model.

Ví dụ measure CPI dùng DIVIDE của tổng EV và tổng AC sau khi chọn một snapshot hợp lệ. Measure lượng hoàn thành dùng tổng quantity theo UOM tương thích, không cộng mét dài với mét khối. Chênh lệch tỷ giá được tách khỏi chênh lệch hiệu suất khi báo cáo quản trị cần phân tích.

# 11 API sự kiện và vận hành tích hợp

## 11.1 Mô hình giao tiếp

Đồng bộ danh mục bằng API và sự kiện phát hành; đồng bộ actual bằng batch hoặc incremental có đối soát; đồng bộ hồ sơ nghiệm thu bằng event sau phê duyệt. API là giao tiếp yêu cầu phản hồi; event thông báo sự kiện đã xảy ra. Thông điệp “hãy duyệt chi phí” là command cần quyền, không được đặt tên như sự kiện đã duyệt để bỏ qua workflow.

Luồng đề xuất: nguồn nghiệp vụ ghi giao dịch và outbox trong cùng transaction khi có khả năng mở rộng; publisher chuyển outbox tới broker; consumer xác thực schema, khóa idempotency và hiệu lực; xử lý dữ liệu cùng inbox marker trong một transaction; phát ack; job đối soát kiểm tra đủ và đúng. Nếu nguồn không hỗ trợ outbox, dùng incremental watermark kèm cửa sổ đọc lặp và dedup, đồng thời công bố giới hạn độ trễ.

## 11.2 Danh mục giao diện cần bàn giao

| **ID** | **Hướng và đối tượng**                         | **SLA mục tiêu và kiểm soát**                              |
|--------|------------------------------------------------|------------------------------------------------------------|
| INT01  | Registry tới ERP PMIS CDE về mã duyệt          | Dưới 15 phút; receipt xác nhận; dùng khi Approved          |
| INT02  | ERP tới landing về actual và reversal          | Hằng ngày, trước chốt; count và total theo kỳ công ty      |
| INT03  | ERP tới warehouse về commitments               | Hằng ngày; snapshot line và trạng thái hủy                 |
| INT04  | PMIS tới warehouse về baseline và EV           | Sau duyệt; baseline checksum và snapshot bất biến          |
| INT05  | CDE tới registry về model và document revision | Sau phát hành; hash, trạng thái và quyền truy cập          |
| INT06  | Nghiệm thu tới PMIS về lượng đủ điều kiện      | Dưới 15 phút; acceptance ID và chống ghi lặp               |
| INT07  | Warehouse tới Power BI                         | Theo lịch công bố; kiểm tra DQ gate trước refresh          |
| INT08  | Kho tri thức tới AI index                      | Theo revision; xóa quyền và tài liệu thu hồi được phản ánh |

## 11.3 Hợp đồng API đề xuất

API nội bộ GET /v1/projects/{id}/work-packages hỗ trợ cursor, page_size, modified_since và next_cursor. POST /v1/progress-records yêu cầu idempotency key, version, WP, lượng tăng thêm, UOM, ngày nghiệp vụ và evidence. PATCH đối tượng được phép dùng If-Match hoặc revision để chống lost update. API không được cho update baseline Approved; dùng endpoint tạo change request.

Status đề xuất: 400 sai schema; 401 thiếu xác thực; 403 thiếu quyền; 404 không thấy trong phạm vi được phép; 409 xung đột revision hoặc idempotency khác nội dung; 422 vi phạm nghiệp vụ; 429 quá giới hạn; 5xx lỗi tạm. Error response có code, message, field_errors và correlation_id, không chứa token hay dữ liệu nhạy cảm. OpenAPI 3.1.1 \[S12\] là bản đặc tả tham chiếu, không khẳng định là bản mới nhất.

Payload tối thiểu ở Phụ lục D là giao diện nội bộ đề xuất, không phải endpoint có sẵn của Odoo. Adapter chịu trách nhiệm dịch sang API hệ thống đích và giữ source ID. Pagination phải ổn định dưới thay đổi dữ liệu; dùng snapshot token hoặc khoảng watermark cố định, không lấy offset mù trên dữ liệu đang biến động.

## 11.4 Event contract và thứ tự

Phong bì lấy cảm hứng từ CloudEvents \[S13\]: specversion, id, source, type, subject, time và data. Bổ sung schema_version, aggregate_id, aggregate_version, project_id, correlation_id và causation_id khi cần. Tên event như cc1.progress.accepted.v1 biểu diễn nghiệp vụ, không mô tả bảng database.

Khóa dedup gồm source cộng event id. Cùng khóa và cùng hash trả thành công không xử lý lại; cùng khóa khác hash đưa lỗi xung đột. Nếu aggregate_version đến 5 khi mới có 3, giữ chờ hoặc tải lại trạng thái nguồn để xử lý khoảng trống; không mặc nhiên bỏ 4. Thứ tự đảm bảo theo aggregate khi broker hỗ trợ, không đòi trật tự toàn hệ thống.

## 11.5 Retry lỗi và replay

Retry lỗi mạng và lỗi tạm với exponential backoff cùng jitter; đề xuất tối đa 8 lần trong 30 phút trước DLQ, điều chỉnh theo SLA thực tế. Lỗi schema hoặc quyền không retry vô hạn. DLQ lưu reason, source reference, first_last_seen, retry_count và owner. Cảnh báo khi tồn tại thông điệp ảnh hưởng kỳ chốt, không chỉ khi queue dài.

Replay phải chọn phạm vi, dry run kiểm tra count tổng, xác nhận người vận hành và lưu batch_id mới; consumer idempotent bảo đảm không cộng lại. Khi sửa dữ liệu nguồn, phát correction hoặc revision mới thay vì đổi nội dung event cũ. Đối soát hằng ngày so count, tổng số tiền theo nguyên tệ, tổng lượng theo UOM, min max thời gian và danh sách record thiếu; count đúng không đủ chứng minh tiền đúng.

## 11.6 Bảo mật và khả năng phục hồi

Sử dụng TLS, service identity riêng, secret rotation, least privilege và audit. Dữ liệu Restricted chỉ truyền tới hệ thống được phép. API phải kiểm tra project scope từ token và bản ghi, không tin project_id do client gửi. Log che dữ liệu cá nhân và khóa. Thiết lập backup, restore rehearsal và runbook lỗi nguồn, broker hoặc warehouse.

Mục tiêu pilot đề xuất RPO 24 giờ và RTO 8 giờ cho nền tảng báo cáo, còn ERP theo chính sách vận hành đã được CC1 phê duyệt. Không áp ngưỡng này cho điều khiển thiết bị hoặc an toàn công trường. Phải kiểm thử khôi phục bằng dữ liệu, quyền và đối soát sau restore; có bản backup không đồng nghĩa khôi phục được.

# 12 Chất lượng dữ liệu và AI

## 12.1 Data quality gate

| **Mã** | **Quy tắc**                              | **Mức xử lý**                                    |
|--------|------------------------------------------|--------------------------------------------------|
| DQ01   | Không trùng khóa nguồn và event id       | Chặn ingest nếu khác nội dung; dedup nếu giống   |
| DQ02   | FK tới WP CBS công ty còn hiệu lực       | Quarantine; không công bố vào fact chính         |
| DQ03   | Tổng phân bổ bằng nguồn                  | Chặn công bố; sai số làm tròn có dòng giải thích |
| DQ04   | Ngân sách phân kỳ cộng đúng BAC          | Chặn duyệt baseline                              |
| DQ05   | EV không vượt BAC khi chưa đổi scope     | Chặn snapshot và điều tra phương pháp đo         |
| DQ06   | EV có bằng chứng đúng trạng thái         | Chặn phần EV không đủ bằng chứng                 |
| DQ07   | Actual đối soát ERP và accrual           | Chặn final snapshot nếu có chênh chưa giải thích |
| DQ08   | Cutoff baseline currency thống nhất      | Chặn so sánh KPI nếu không cùng cơ sở            |
| DQ09   | Hierarchy không vòng và không mồ côi     | Chặn phát hành dictionary                        |
| DQ10   | UOM và hệ số quy đổi được duyệt          | Chặn lượng không tương thích                     |
| DQ11   | Hồ sơ nguồn không quá hạn cập nhật       | Cảnh báo hoặc provisional theo mức trọng yếu     |
| DQ12   | Người duyệt có quyền tại thời điểm duyệt | Chặn và điều tra nếu sai thẩm quyền              |

Score DQ là tỷ lệ bản ghi đạt trên tập đã kiểm tra, kèm mẫu số và loại rule. Không trộn tỷ lệ thiếu mã với tỷ lệ lỗi tiền rồi lấy trung bình để tạo điểm xanh. Các rule critical phải đạt tuyệt đối theo tiêu chí nghiệm thu; một điểm tổng 99% không bù được một lỗ hổng phân quyền hoặc sai số tổng chi phí.

## 12.2 Quản lý lỗi dữ liệu

Một data issue có issue_id, rule_id, record set, amount affected, severity, owner, opened_at, due_at, cause và fix evidence. Steward xác minh, owner quyết định sửa nguồn hay mapping, CNTT sửa pipeline nếu là lỗi hệ thống. Sau sửa chạy lại rule và đối soát phạm vi ảnh hưởng. Không sửa trực tiếp warehouse để che lỗi nguồn trừ lớp adjustment được duyệt và có ngày hết hiệu lực.

Đối với dữ liệu di trú, giữ raw copy và bảng mapping nguồn đích. Rejected records có số tiền tổng và lý do. Không bỏ dòng lỗi khỏi mẫu số khi báo tỷ lệ hoàn tất migration. Các giá trị mặc định cần được đánh dấu inferred hoặc defaulted và được owner phê duyệt.

## 12.3 Danh mục AI triển khai theo rủi ro

| **Use case**                    | **Đầu vào và đầu ra**                    | **Điều kiện cho phép**                       |
|---------------------------------|------------------------------------------|----------------------------------------------|
| Tra cứu dictionary và quy trình | Tài liệu duyệt tới câu trả lời dẫn nguồn | Chỉ đọc; dẫn section và revision             |
| Gợi ý mã WBS CBS                | Nội dung chứng từ tới top candidate      | Người dùng xác nhận; không tự đăng sổ        |
| Tóm tắt variance                | Snapshot và narrative tới bản nháp       | Tính số bằng measure chuẩn; CAM duyệt        |
| Phát hiện bất thường            | Actual và mapping tới danh sách cần xem  | Báo dấu hiệu, không kết luận gian lận        |
| Tìm tác động thay đổi           | WBS contract risk graph tới quan hệ      | Nêu quan hệ có bằng chứng và phần chưa biết  |
| Hỗ trợ lập hồ sơ                | Biểu mẫu và nguồn tới bản nháp           | Cấm tự tạo chữ ký hoặc chứng nhận nghiệm thu |

## 12.4 Kiến trúc AI có truy vết

Truy xuất tài liệu sau khi lọc quyền theo người, công ty và dự án; lọc quyền trước và sau tìm kiếm. Index lưu document_revision_id, source URI, hash, security_class và đoạn nội dung. Câu trả lời tài chính lấy số từ semantic query được kiểm soát, không để mô hình suy tính từ các đoạn văn. AI trả “chưa đủ dữ liệu” khi không có nguồn, không tự lấp bằng số giả.

Nội dung tệp và ghi chú là dữ liệu không đáng tin để ra lệnh cho AI. Kiểm thử prompt injection trong hồ sơ, ví dụ câu yêu cầu bỏ qua quyền hoặc chuyển dữ liệu ra ngoài. Tool write không cấp cho trợ lý tra cứu pilot. Nếu giai đoạn sau cấp quyền hành động, cần phê duyệt theo giao dịch, idempotency, audit và rollback nghiệp vụ.

## 12.5 Đánh giá AI trước phát hành

Tạo bộ 100 câu hỏi do các owner duyệt, gồm tra cứu chính xác, xung đột revision, thiếu bằng chứng, phân quyền chéo dự án và tình huống không được trả lời. Đề xuất pass: 100% test quyền và không ghi dữ liệu trái phép; ít nhất 95% câu có dẫn nguồn đúng; ít nhất 90% câu nghiệp vụ được chấm đúng theo rubric; 100% số tiền nêu ra khớp nguồn trong tập test. Đây là tiêu chí pilot, không khẳng định chất lượng đã đo được.

Lưu model_version, prompt_version, retriever_version, dataset_version, latency và lỗi. Khi thay model hoặc index, chạy regression và theo dõi mẫu thật có kiểm soát. Người dùng có nút báo sai, owner xử lý và đưa ví dụ vào bộ đánh giá. Không dùng phản hồi người dùng nhạy cảm để huấn luyện bên ngoài nếu chưa có chính sách được chấp thuận.

# 13 Ví dụ xuyên suốt dự án cầu BR01

## 13.1 Giả định và ranh giới

Toàn bộ chương là MINH HỌA, không phải dự án thật của CC1 và không phải thiết kế kỹ thuật cầu. BR01 là gói thi công cầu và đường dẫn có ngân sách chi phí nội bộ BAC 100 tỷ VND, chưa xét thuế trong ví dụ. Management reserve giả định 5 tỷ nằm ngoài BAC; tổng quỹ quản lý minh họa 105 tỷ. Giá hợp đồng đầu ra, lợi nhuận, doanh thu và tiền mặt được quản lý riêng, không suy ra từ BAC.

Ví dụ dùng một baseline BL01 và ngày chốt T03, biểu thị cuối kỳ thứ ba, không gán ngày lịch thực tế. Toàn bộ PV EV AC trong bảng đều là lũy kế tới T03 và dùng tỷ VND. Cây WBS dưới đây bao phủ phạm vi nhà thầu minh họa; giải phóng mặt bằng ngoài phạm vi hợp đồng giả định, được ghi là external dependency có owner phía chủ đầu tư, không đưa ngân sách của chủ đầu tư vào BAC nhà thầu.

## 13.2 WBS và ngân sách kiểm soát

| **WBS** | **Phạm vi đầu ra**             | **CA và OBS phụ trách**       | **BAC tỷ VND** |
|---------|--------------------------------|-------------------------------|----------------|
| 01      | Quản lý và công trình tạm      | CA010 Ban dự án               | 8              |
| 02      | Hồ sơ thiết kế triển khai      | CA020 Kỹ thuật                | 5              |
| 03      | Kết cấu dưới gồm mố trụ        | CA030 Đội kết cấu dưới        | 30             |
| 04      | Kết cấu trên                   | CA040 Đội kết cấu trên        | 35             |
| 05      | Đường dẫn                      | CA050 Đội đường               | 12             |
| 06      | Hệ thống phụ trợ và hoàn thiện | CA060 Đội hoàn thiện          | 5              |
| 07      | Kiểm định hồ sơ và bàn giao    | CA070 Ban dự án và QA         | 5              |
| Tổng    | Phạm vi nhà thầu BR01          | Không cộng dòng tổng vào fact | 100            |

WBS 03 phân rã thành 03.01 trụ P01, 03.02 trụ P02 và 03.03 các phần kết cấu dưới còn lại. BAC tương ứng 10, 10 và 10 tỷ. WBS 03.01 tiếp tục gồm gói cọc 6 tỷ, bệ 2 tỷ và thân trụ 2 tỷ. Dòng gói và dòng tổng chỉ là hai mức hiển thị của cùng ngân sách, không phải hai nguồn ngân sách độc lập.

## 13.3 Dictionary đã điền cho gói cọc P01

| **Thuộc tính**        | **Giá trị minh họa**                                                              |
|-----------------------|-----------------------------------------------------------------------------------|
| ID và mã              | wbs_id được hệ thống cấp; BR01-WBS-00320; path 03.01.01                           |
| Phạm vi vào           | Hoàn thành 20 cọc đồng nhất trong ví dụ, gồm hồ sơ và kiểm tra theo yêu cầu dự án |
| Phạm vi ra            | Bệ, thân trụ, xử lý thay đổi địa chất ngoài phạm vi được duyệt                    |
| PBS và LBS            | BR01-PBS-P01-PILE; BR01-LOC-P01                                                   |
| CA và người phụ trách | BR01-CA-030; CAM kết cấu dưới do dự án bổ nhiệm                                   |
| Ngân sách và lượng    | 6 tỷ; 20 cọc; giá ngân sách bình quân 0,3 tỷ mỗi cọc                              |
| EV method             | Quantity; chỉ cọc đủ điều kiện nghiệm thu nội bộ đã quy định                      |
| Bằng chứng            | Nhật ký, kết quả kiểm tra, phiếu xác nhận lượng và acceptance ID                  |
| Tiến độ               | ACT-P01-PILE linked tới WP; calendar và logic trong schedule version              |
| Điều kiện sẵn sàng    | Bản vẽ duyệt, mặt bằng, biện pháp, vật tư và kiểm soát an toàn phù hợp            |
| Nguyên tắc rework     | Chi phí làm lại tăng AC; không ghi thêm EV cho cùng cọc                           |

Đơn giá bình quân 0,3 tỷ chỉ dùng vì 20 cọc được giả định đồng nhất. Nếu cọc khác chiều sâu, đường kính hoặc công nghệ, phải chia nhóm hoặc dùng giá ngân sách theo từng đơn vị phù hợp, không đếm số cọc ngang giá để đo tiến độ.

## 13.4 CBS của gói cọc và crosswalk đã điền

| **CBS**               | **Ngân sách tỷ VND** | **Nguồn cơ sở ước tính**                 |
|-----------------------|----------------------|------------------------------------------|
| C10 vật liệu          | 2,4                  | Lượng vật liệu và giá kế hoạch giả định  |
| C20 nhân công         | 0,9                  | Giờ công và rate giả định                |
| C30 máy               | 1,2                  | Ca máy theo biện pháp giả định           |
| C40 thầu phụ          | 0,9                  | Phạm vi dịch vụ tách khỏi vật tư đã tính |
| C60 kiểm tra kỹ thuật | 0,6                  | Dịch vụ thử nghiệm giả định              |
| Tổng                  | 6,0                  | Đối chiếu BAC của WP                     |

| **Nguồn**             | **Đích**          | **Purpose và cơ sở**                                     |
|-----------------------|-------------------|----------------------------------------------------------|
| BOQ-PILE-P01          | BR01-WBS-00320    | Quantity 20 cọc; không phải giá trị hợp đồng chung       |
| BR01-WBS-00320        | BR01-PBS-P01-PILE | Creates; tham chiếu không cộng tiền                      |
| BR01-WBS-00320        | BR01-LOC-P01      | LocatedAt; một vị trí trong ví dụ                        |
| BR01-CTR-SC01-L01     | BR01-WBS-00320    | Phạm vi dịch vụ thầu phụ; mapping theo lượng             |
| MODEL01 R03 OBJECT001 | PBS P01 PILE      | Represents; lưu GlobalId từ mô hình thật khi có          |
| BR01-RSK-0001         | BR01-WBS-00320    | Affects; nguy cơ địa chất, không phân bổ chi phí tự động |

## 13.5 EV của gói cọc

Tại T03, kế hoạch có 12 cọc đủ điều kiện, thực tế có 10 cọc đủ điều kiện và 2 cọc đang kiểm tra. PV bằng 12 nhân 0,3 là 3,6 tỷ; EV bằng 10 nhân 0,3 là 3,0 tỷ. Hai cọc đang kiểm tra chưa có EV theo phương pháp đã chọn. AC tương ứng phạm vi gói là 3,3 tỷ đã đối soát, kể cả phần chi phí của công việc dở dang theo cơ sở quản trị được duyệt.

CV âm 0,3 tỷ; SV âm 0,6 tỷ; CPI 0,9091; SPI 0,8333. Số cọc thực tế đã thi công là 12 nhưng số đạt điều kiện EV là 10; hai chỉ tiêu được hiển thị riêng. Nếu một cọc trong số 10 bị thu hồi chấp nhận sau đó, tạo reversal progress và đánh giá ảnh hưởng; không xóa hồ sơ cũ.

## 13.6 Đối soát EVM toàn dự án

| **CA** | **BAC** | **PV T03** | **EV T03** | **AC T03** |
|--------|---------|------------|------------|------------|
| CA010  | 8       | 4          | 4          | 4,2        |
| CA020  | 5       | 4          | 3,5        | 3,8        |
| CA030  | 30      | 15         | 12         | 13,5       |
| CA040  | 35      | 10         | 8          | 9          |
| CA050  | 12      | 5          | 5          | 5,2        |
| CA060  | 5       | 1          | 0,5        | 0,8        |
| CA070  | 5       | 1          | 1          | 1,5        |
| Tổng   | 100     | 40         | 34         | 38         |

AC 38 tỷ giả định gồm 35 tỷ chi phí nguồn ERP đã chuẩn hóa theo cùng cost basis và 3 tỷ accrual được duyệt chưa trùng với chứng từ ERP. Gói cọc P01 có EV 3 nằm trong EV 12 của CA030; AC 3,3 nằm trong 13,5. Không cộng gói cọc lần nữa vào tổng dự án.

Kết quả: CV bằng 34 trừ 38 là âm 4 tỷ; SV bằng 34 trừ 40 là âm 6 tỷ. CPI bằng 34 chia 38 là 0,8947; SPI bằng 34 chia 40 là 0,85. Phần trăm hoàn thành theo ngân sách EV/BAC là 34%; đây không phải tỷ lệ số cấu kiện hay tỷ lệ ngày đã trôi qua.

EAC theo CPI bằng 100 chia 0,8947368 là 111,7647 tỷ; VAC âm 11,7647 tỷ. EAC theo giả định phần còn lại đúng ngân sách bằng 38 cộng 100 trừ 34 là 104 tỷ. EAC kết hợp CPI SPI bằng 38 cộng 66 chia (0,8947368 nhân 0,85) xấp xỉ 124,7820 tỷ. Ba con số là ba giả định khác nhau, không lấy trung bình để tạo forecast chính thức.

TCPI theo BAC bằng 66 chia 62 là 1,0645: phần việc còn lại phải đạt hiệu suất cao hơn 1 để giữ ngân sách 100. CAM đánh giá từ dưới lên giả định ETC là 72 tỷ, nên EAC được đề xuất là 110 tỷ. Báo cáo giữ cả forecast bottom up 110 và chỉ báo CPI 111,76 để giải thích, không sửa BAC 100.

## 13.7 Tiến độ minh họa và hành động

Giả sử đường găng hiện đi qua nghiệm thu cọc P01, thi công bệ P01, lắp kết cấu trên và kiểm định. Hai cọc chờ kiểm tra có thể tác động mốc bệ dù SPI của một số gói khác tốt. Planner phải tính lại mạng tiến độ và nguồn lực; không chuyển SV âm 6 tỷ thành sáu ngày chậm. Hành động đề xuất là xác định nguyên nhân chậm kiểm tra, bổ sung năng lực phù hợp và cập nhật lịch dự báo có owner.

Kế hoạch tuần ghi 10 cam kết, hoàn thành đúng tiêu chí 8, PPC là 80%. Con số này không thay SPI 0,85. Nếu hai việc thất bại đều trên đường găng thì ưu tiên khác trường hợp hai việc không ảnh hưởng mốc. CAM báo tác động ngày dự kiến và chi phí phục hồi từ biện pháp, không chỉ báo màu đỏ.

## 13.8 Rủi ro và thay đổi minh họa

RSK0001 mô tả điều kiện địa chất khác giả định có thể làm tăng thời gian khoan và chi phí. Đánh giá giả định xác suất 30%, tác động nếu xảy ra 4 tỷ, EMV đơn giản 1,2 tỷ. EMV là chỉ báo kỳ vọng cho kịch bản một rủi ro, không phải khoản tự động được duyệt, không đại diện phân phối tổng rủi ro dự án. Khi có quan hệ phụ thuộc, phân tích tổng phải xử lý tương quan và cơ sở dữ liệu phù hợp.

CR0001 giả định được duyệt bổ sung phạm vi 2 tỷ và kéo dài mốc liên quan sau T03. BL01 và snapshot T03 giữ nguyên. BL02 có BAC 102 tỷ, ngân sách tăng được phân kỳ vào phần còn lại và liên kết change decision. EV quá khứ không tự tăng 2 tỷ. Báo cáo so sánh BL01 và BL02 nêu rõ scope change, không kết luận hiệu suất cải thiện chỉ vì BAC tăng.

Nếu đây chỉ là dự báo vượt chi phí của cùng phạm vi, không phải scope change được duyệt, BAC vẫn 100 và EAC tăng. Nếu chủ đầu tư chưa chấp nhận thay đổi hợp đồng, sổ commercial ghi pending hoặc disputed, không coi giá trị đó là doanh thu chắc chắn. Thẩm quyền và quyền lợi thực tế do hồ sơ hợp đồng và người có trách nhiệm xác nhận.

## 13.9 Chuỗi dữ liệu từ hiện trường tới báo cáo

Kỹ sư lập PRG0001 cho 10 cọc đạt điều kiện, QA duyệt ACC0001 gắn hồ sơ R03. PMIS kiểm tra WP Approved và lượng chưa ghi trước đó, tạo progress accepted event. Warehouse giữ event ID và evidence revision; tính EV 3 tỷ theo BL01. ERP cung cấp 3,0 tỷ posted actual và Finance bổ sung 0,3 tỷ accrual cho gói; AC là 3,3 tỷ. DQ so tổng, PMO duyệt snapshot, Power BI hiển thị con số với khả năng truy ngược tới ACC0001 và cost entries.

Gửi lại event PRG0001 không làm EV thành 6 tỷ. Hóa đơn thay thế accrual kỳ sau không làm chi phí tăng thêm 0,3 tỷ một lần nữa. Đổi mã hiển thị WP không làm mất liên kết vì ID ổn định. Ba tình huống này là test bắt buộc trước go live.

# 14 Roadmap 30 60 90 180 ngày

## 14.1 Điều kiện tính ngày và nguồn lực

Ngày 0 là ngày Sponsor phê duyệt charter pilot, chỉ định owner và cấp quyền dữ liệu, không mặc định là ngày tài liệu được tạo. Các mốc là mục tiêu triển khai đề xuất. Nếu hồ sơ nguồn chưa sẵn sàng, phải điều chỉnh đường găng và ghi quyết định; không ép nghiệm thu để giữ lịch hình thức.

Nhóm lõi đề xuất gồm PMO product owner, data steward, Finance SME, QS SME, kỹ thuật QA BIM, integration lead, BI developer, kiểm thử UAT và vận hành. Một người có thể kiêm nhiệm nếu không xung đột kiểm soát. Sponsor bảo đảm thời gian tham gia của SME; thuê phần mềm không thay trách nhiệm owner dữ liệu.

## 14.2 Ngày 1 đến 30 chốt nền tảng

| **Gói việc**        | **Sản phẩm**                                       | **A và điều kiện hoàn tất**                          |
|---------------------|----------------------------------------------------|------------------------------------------------------|
| Khảo sát hiện trạng | Danh mục hệ thống, pháp nhân, dữ liệu, pain points | PMO; owner xác nhận đủ phạm vi pilot                 |
| Thiết kế taxonomy   | Dictionary và mã v0.9, cây BR01                    | Data owner; không trùng ID, không vòng, rõ ranh giới |
| Mapping ban đầu     | BOQ WBS CBS GL OBS LBS trên mẫu                    | Finance cùng PMO theo từng miền; giải trình ngoại lệ |
| Kiến trúc và quyền  | ERD, source of truth, role scope, fit gap          | IT owner; nghiệp vụ đồng thuận đường đi dữ liệu      |
| Kế hoạch kiểm thử   | Requirement và test matrix, dataset mẫu            | Business owner; có expected result định lượng        |

Gate 30: Sponsor duyệt phạm vi, danh mục giả định và backlog; không cho phát triển mở rộng nếu chưa chốt grain actual, phương pháp EV và cấp analytic Odoo. Bằng chứng gồm workshop minutes, dataset profile, dictionary và decision log đã ký.

## 14.3 Ngày 31 đến 60 xây và kiểm thử tích hợp

| **Gói việc**         | **Sản phẩm**                       | **Tiêu chí gate**                               |
|----------------------|------------------------------------|-------------------------------------------------|
| Registry và cấu hình | Mã, workflow, baseline version     | Các kiểm tra DQ critical chạy được              |
| ERP adapter          | Actual, accrual, commitment sample | Đối soát count và total, không trùng khi replay |
| PMIS và tiến độ      | CA, EV, baseline, link activity    | Tính lại ví dụ BR01 đúng kết quả chương 13      |
| Warehouse và BI      | Fact dimension và dashboard v1     | Không nhân tiền, drill-through có quyền         |
| UAT vòng 1           | Test evidence và defect log        | Không còn lỗi chặn chu trình end to end         |

Gate 60: owner nghiệp vụ xác nhận các luồng chính trên test environment; CNTT xác nhận deployment, secrets và logs. Những gap pháp nhân, quyền hoặc cost basis chưa giải quyết là lý do no go, không đưa vào danh sách cải tiến sau một cách tùy tiện.

## 14.4 Ngày 61 đến 90 thí điểm có kiểm soát

Chạy song song quy trình hiện hữu và hệ thống mới trên phạm vi được duyệt. Thực hiện ít nhất hai kỳ chốt theo lịch được thống nhất, có thể dùng kỳ báo cáo tuần cho kiểm thử nhưng phải có một lần chốt theo cơ sở tài chính tháng nếu mục tiêu là báo cáo tháng. Đối soát khác biệt, diễn tập reversal accrual, change baseline và outage integration. Đào tạo theo vai trò trên hồ sơ thực tế được phép dùng.

Gate 90 yêu cầu các tiêu chí chương 15, owner ký UAT, tài liệu vận hành đủ và tồn tại không critical có owner cùng deadline. Sponsor quyết định pilot production hoặc kéo dài pilot. AI chỉ mở tra cứu có nguồn khi quyền và chất lượng tài liệu đạt; không để AI là điều kiện bắt buộc nếu nền dữ liệu chưa chín.

## 14.5 Ngày 91 đến 180 mở rộng theo đợt

Đợt 1 chuẩn hóa template từ bài học pilot và chọn thêm một dự án có điều kiện khác, không nhân rộng đồng loạt. Đợt 2 mở thêm hợp đồng, BIM và asset handover theo use case đã chứng minh giá trị. Đợt 3 bổ sung forecast, cảnh báo và AI có kiểm thử. Mỗi đợt có data readiness assessment, migration rehearsal, training và go no go.

Gate 180 đánh giá thời gian chốt, tỷ lệ mã hóa, độ tin cậy forecast, mức sử dụng và chi phí vận hành so với baseline đo tại ngày 30. Quyết định mở rộng phải dựa trên lợi ích đo được, không dựa vào số dashboard hoặc số tài khoản tạo ra. Chỉ tiêu giảm thời gian là mục tiêu tương đối đề xuất, cần có số gốc để chứng minh.

## 14.6 Ước lượng nguồn lực và ngân sách triển khai

Không có báo giá hoặc dữ liệu nhân sự CC1 nên tài liệu không đưa tổng mức tiền như số xác thực. Cách lập ngân sách đề xuất: effort từng workstream theo ngày người nhân rate được duyệt, cộng license, hosting, thiết bị, đào tạo, migration, kiểm thử, vận hành và dự phòng có cơ sở. Tách chi phí xây dựng một lần khỏi chi phí duy trì hằng năm và nâng cấp.

Sizing phải tính số dự án, số WP, dòng actual mỗi kỳ, số tài liệu, dung lượng mô hình, người dùng đồng thời và tần suất refresh. Đo trên pilot rồi lập dự toán mở rộng theo tải và mức hỗ trợ. Chi phí sở hữu bao gồm duy trì mapping và owner, không chỉ chi phí máy chủ.

# 15 KPI acceptance criteria và nghiệm thu

## 15.1 Bộ KPI có chủ sở hữu

| **KPI**               | **Công thức và kỳ đo**                                            | **Mục tiêu pilot đề xuất**                                  | **Owner**        |
|-----------------------|-------------------------------------------------------------------|-------------------------------------------------------------|------------------|
| Mã hóa chi phí hợp lệ | Giá trị actual có WP CA CBS hợp lệ chia tổng actual trong phạm vi | 100% trước final close; ngoại lệ treo không che khỏi mẫu số | Finance          |
| Bằng chứng EV         | EV có evidence đủ điều kiện chia tổng EV                          | 100% tại chốt                                               | QA và PMO        |
| Đối soát chi phí      | Nguồn theo cost basis trừ tổng allocated fact                     | 0 chênh không giải thích; rounding được duyệt               | Finance          |
| Kịp thời actual       | Dòng đến trong SLA chia dòng phải đến                             | Ít nhất 98% mỗi ngày; không thiếu trọng yếu tại chốt        | IT và data owner |
| Chốt kỳ đúng hạn      | Số kỳ final trước D cộng 5 chia số kỳ                             | Hai kỳ liên tiếp đạt trước mở rộng                          | PMO              |
| Mapping backlog       | Số issue critical quá hạn                                         | 0 tại gate                                                  | Data steward     |
| Chất lượng forecast   | Giá trị tuyệt đối forecast trừ actual tại cùng mốc chia actual    | Thiết lập baseline; mục tiêu cải thiện sau đủ lịch sử       | CAM              |
| PPC                   | Cam kết hoàn tất đúng định nghĩa chia cam kết tuần                | Mục tiêu thí điểm 80%, phân tích nguyên nhân                | Planner          |
| Sử dụng quy trình     | Hồ sơ thuộc phạm vi đi đúng workflow chia tổng hồ sơ              | Ít nhất 95%, không có critical bypass                       | Business owner   |
| Khôi phục             | Thời gian phục hồi và mức mất dữ liệu đo được                     | Đạt RTO RPO đã duyệt trong diễn tập                         | IT service owner |

Mục tiêu pilot là tiêu chí đề xuất để thương thảo nghiệm thu, không phải mức KPI CC1 hiện đạt. Forecast accuracy cần so đúng ngày dự báo và phạm vi; không đo EAC mới nhất sát ngày kết thúc rồi tuyên bố dự báo tốt. Không đưa CPI càng cao càng tốt thành mục tiêu thưởng đơn lẻ vì có thể khuyến khích ghi thiếu AC.

## 15.2 Ma trận yêu cầu và test chấp nhận

| **Test ID** | **Tình huống**                                     | **Kết quả chấp nhận**                                          |
|-------------|----------------------------------------------------|----------------------------------------------------------------|
| UAT01       | Duyệt WBS có nhánh thiếu owner hoặc vòng cha con   | Bị chặn; log nêu rule và record                                |
| UAT02       | Phân bổ 120 triệu theo 60 và 40 giờ                | 72 và 48 triệu; tổng đúng 120                                  |
| UAT03       | Gửi lại 100 lần cùng event                         | Một tác động nghiệp vụ; 99 lần dedup có log                    |
| UAT04       | Cùng idempotency key khác payload                  | Bị từ chối xung đột; không ghi thêm                            |
| UAT05       | Nhận event version 5 trước 4                       | Chờ hoặc resync có kiểm soát; kết quả cuối đúng                |
| UAT06       | Thiếu mã CBS hoặc sai UOM                          | Quarantine; không vào final report                             |
| UAT07       | BR01 tại T03                                       | PV 40 EV 34 AC 38; CPI 0,8947 SPI 0,85                         |
| UAT08       | Accrual 0,3 được thay bằng hóa đơn                 | AC không tăng trùng; reversal truy vết được                    |
| UAT09       | Thêm CR 2 tỷ sau T03                               | BL02 BAC 102; BL01 và snapshot T03 nguyên trạng                |
| UAT10       | Join BOQ nhiều dòng với cost                       | Tổng cost không nhân theo số dòng BOQ                          |
| UAT11       | Người dự án A truy dữ liệu B bằng UI API export AI | Bị từ chối hoặc không trả dữ liệu B; audit đầy đủ              |
| UAT12       | Thu hồi tài liệu hoặc quyền                        | Search và AI không trả nội dung trái quyền sau SLA đã duyệt    |
| UAT13       | Mất kết nối nguồn và replay                        | Không mất hoặc nhân giao dịch; đối soát đạt                    |
| UAT14       | Khôi phục backup                                   | Đạt RTO RPO; dữ liệu, quyền và báo cáo đối soát                |
| UAT15       | Người không có thẩm quyền duyệt baseline           | Bị chặn, không có event phát hành giả                          |
| UAT16       | Snapshot cumulative của 3 kỳ                       | Báo kỳ cuối, không cộng ba số lũy kế                           |
| UAT17       | Đổi mã WP và OBS theo hiệu lực                     | Lịch sử truy được; ID và số chốt không mất                     |
| UAT18       | Có rework và thu hồi acceptance                    | Chi phí tăng đúng; EV không ghi trùng và correction có dấu vết |

## 15.3 Nghiệm thu hiệu năng và dữ liệu di trú

Tải tham chiếu đề xuất để nhà triển khai ước tính: 10 dự án, 20.000 WP, 1 triệu cost allocation, 100 người xem đồng thời; cần đo lại theo sizing thực tế. Mục tiêu thử ban đầu P95 mở trang tổng hợp dưới 5 giây trên hạ tầng, mạng và cache được ghi rõ; API tra danh mục P95 dưới 2 giây; refresh batch hằng ngày hoàn tất trong cửa sổ chốt đã duyệt. Không chấp nhận con số đo trên mẫu 100 dòng làm bằng chứng cho tải mục tiêu.

Migration pass khi 100% dòng trong phạm vi được phân loại loaded hoặc rejected có lý do, tổng tiền nguồn bằng loaded cộng rejected theo từng nguyên tệ, critical rejected bằng 0 trước go live và các khác biệt được owner ký. Phải thử rollback migration hoặc restore trên môi trường kiểm thử. Dữ liệu staging và production có access control riêng.

## 15.4 Phân loại lỗi và go no go

Critical là sai hoặc lộ dữ liệu có tác động trọng yếu, bỏ qua phê duyệt, mất giao dịch, cộng trùng tiền, mất khả năng khôi phục. Major là luồng nghiệp vụ chính không thực hiện được hoặc báo cáo sai nhưng có phạm vi xác định. Minor là bất tiện hoặc trình bày không làm sai nghiệp vụ. Gate production yêu cầu không còn critical và major trong phạm vi cam kết; minor có workaround, owner và hạn sửa được chấp nhận.

Hồ sơ nghiệm thu gồm requirement traceability, test cases với expected actual result, evidence URI và hash, defect log, biên bản đối soát hai kỳ, quyền và bảo mật, diễn tập khôi phục, đào tạo, cấu hình, runbook và danh sách tồn tại. Người ký gồm business owner, data owner, IT owner và cấp quyết định triển khai theo thẩm quyền CC1. Nhà triển khai không tự ký thay chủ nghiệp vụ.

## 15.5 Nghiệm thu không đồng nghĩa hoàn tất công tác quản trị

Sau go live có thời gian hypercare đề xuất 30 ngày, trực hỗ trợ kỳ chốt đầu, theo dõi lỗi và khả năng sử dụng. Cuối hypercare đánh giá SLA và chuyển quyền sở hữu vận hành. Mỗi thay đổi lớn phải chạy regression subset phù hợp; không đòi chạy mọi test khi chỉ sửa nhãn, nhưng thay grain, mapping, quyền hoặc cost basis cần kiểm thử tích hợp đầy đủ phạm vi ảnh hưởng.

# 16 Change control versioning và quản lý phát hành

## 16.1 Phân biệt các loại thay đổi

| **Loại**                   | **Ví dụ**                               | **Cách xử lý**                                                  |
|----------------------------|-----------------------------------------|-----------------------------------------------------------------|
| Sửa dữ liệu sai            | Gán nhầm CBS trên một chứng từ          | Correction có dấu vết và đối soát; không mặc nhiên đổi baseline |
| Đổi dự báo                 | Giá máy tăng cho phần chưa thi công     | Cập nhật ETC EAC và giả định; BAC giữ nguyên                    |
| Đổi phạm vi được duyệt     | Bổ sung cấu kiện theo yêu cầu           | Change request, tác động, approval và baseline mới              |
| Đổi cấu trúc báo cáo       | Gộp hai nhóm CBS để xem                 | Mapping view mới; giữ phân loại gốc và lịch sử                  |
| Đổi tổ chức                | Chuyển CAM hoặc đội phụ trách           | Assignment theo hiệu lực; không đổi ID công việc                |
| Đổi giao diện dữ liệu      | Đổi ý nghĩa trường amount               | Schema major version và kế hoạch migration                      |
| Đổi cấu hình hoặc phần mềm | Nâng phiên bản Odoo hoặc semantic model | Release có kiểm thử, rollback và approver                       |

## 16.2 Quy trình thay đổi có điểm kiểm soát

Người yêu cầu tạo CR với nguyên nhân, tài liệu căn cứ, phạm vi đối tượng, ngày cần hiệu lực và độ khẩn. Change manager kiểm tra đủ thông tin, phân loại và chỉ định các owner đánh giá. PMO đánh giá WBS, CA, tiến độ, EV; Finance đánh giá chi phí và đối soát; QS đánh giá hợp đồng và BOQ; kỹ thuật đánh giá sản phẩm, BIM và nghiệm thu; CNTT đánh giá schema, quyền và tích hợp.

Người có thẩm quyền quyết định Approve, Reject hoặc Defer kèm điều kiện. Sau Approve, đội thực hiện tạo phiên bản mới ở môi trường phù hợp, chạy test tác động, phát hành theo ngày hiệu lực và kiểm tra hệ thống đích đã nhận. CR chỉ Closed khi có bằng chứng triển khai và số liệu đối soát, không đóng ngay sau chữ ký.

Trạng thái đề xuất: Draft → ImpactReview → PendingApproval → Approved → Implemented → Verified → Closed. Rejected kết thúc yêu cầu bị từ chối; Defer quay về chờ thông tin có hạn xử lý. Emergency change có quy trình rút gọn được CC1 duyệt trước, vẫn phải ghi lý do, người quyết định, kiểm soát tạm và post review; không phải lối tắt cho sửa số liệu.

## 16.3 Quy tắc phiên bản và tương thích

Dictionary version 1.1 bổ sung thuộc tính tùy chọn không đổi ý nghĩa dữ liệu cũ. Version 2.0 dùng khi đổi grain hoặc ngữ nghĩa bắt buộc; cần kế hoạch chuyển đổi và thời gian hỗ trợ song song. Baseline revision BL02 là phiên bản nghiệp vụ khác schema_version của API. Document revision R03 là phiên bản hồ sơ khác với model revision. Không gom các khái niệm này vào một trường version không định nghĩa.

Event cũ phải vẫn đọc được theo schema khi nó được tạo. Không phát event v1 với kiểu dữ liệu đã đổi. Nếu bổ sung enum, consumer phải có cơ chế nhận giá trị chưa biết và đưa hàng lỗi có kiểm soát. Release notes ghi thay đổi, tác động, backward compatibility, migration và rollback. Mapping rules được phát hành như cấu hình có test, không sửa trực tiếp production bằng bảng tính không kiểm soát.

## 16.4 Mở lại kỳ và tái trình bày

Mở lại kỳ cần lý do trọng yếu, phạm vi correction, phê duyệt Finance và người công bố theo quyền. Giữ snapshot cũ với trạng thái Superseded, phát snapshot mới với restatement_reason và liên kết bản thay thế. Dashboard cho biết đang xem bản nào. Không xóa bản cũ hoặc âm thầm chạy refresh làm số đã ký thay đổi.

Nếu chỉ cần xem lịch sử theo cơ cấu tổ chức mới, tạo report view restated riêng, giữ nguyên bản as reported. Hai góc nhìn phải có nhãn và cùng truy về giao dịch gốc. Khi thay luật phân bổ, phải nói áp dụng prospectively cho tương lai hay retrospectively có phê duyệt cho quá khứ.

## 16.5 Cutover và rollback

Trước cutover: chốt phạm vi dữ liệu, freeze cấu hình, sao lưu, chạy migration cuối, đối soát, kiểm tra quyền, thông báo lịch và chuẩn bị kênh hỗ trợ nội bộ theo kế hoạch đã duyệt. Tại go no go, kiểm tra các blocker và chữ ký owner. Sau chuyển: kiểm tra giao dịch nhỏ có kiểm soát, báo cáo smoke test và theo dõi queue.

Rollback kích hoạt khi có critical defect không thể xử lý trong cửa sổ cho phép: dừng ghi ở luồng bị ảnh hưởng, bảo toàn nhật ký, xác định giao dịch phát sinh sau cutover, phục hồi hoặc bù giao dịch theo nghiệp vụ, đối soát và thông báo owner. Không chỉ phục hồi database cũ rồi bỏ giao dịch mới. Chạy diễn tập trước khi đưa hệ thống vào vận hành thật.

# Phụ lục A Danh mục nguồn và giới hạn sử dụng

## A1 Nguyên tắc trích dẫn

Các mã S01 đến S19 dẫn tới nguồn sơ cấp đã được kiểm tra ở mức trang công khai ngày 09 tháng 10 năm 2026. Phần tóm tắt nguồn được viết ngắn; toàn bộ quy trình, trường dữ liệu, biểu mẫu, ngưỡng và ví dụ gắn CC1 là thiết kế đề xuất, trừ nơi nói rõ khác. Nguồn không được dùng để tuyên bố toàn bộ giải pháp đã tuân thủ tiêu chuẩn hoặc sản phẩm đáp ứng mọi yêu cầu.

## A2 Tiêu chuẩn hướng dẫn và khung phương pháp

S01 — ISO 21511:2018, Work breakdown structures for project and programme management. Loại: hướng dẫn tiêu chuẩn quốc tế về WBS. Trang công khai nêu khái niệm và quan hệ WBS, không cung cấp quy trình công cụ chi tiết. Trang tham chiếu có thông báo bản thay thế đang được chuẩn bị; CC1 cần kiểm tra trạng thái trước ban hành quy chế. URL: https://www.iso.org/standard/69702.html

S02 — ISO 21508:2026, Project programme and portfolio management — Earned value management. Loại: hướng dẫn tiêu chuẩn quốc tế. Trang ISO xác nhận xuất bản tháng 02 năm 2026 và trang bản 2018 ghi withdrawn. Dùng làm tham chiếu phạm vi EVM; không trích điều khoản toàn văn. URL: https://www.iso.org/standard/87899.html ; lịch sử: https://www.iso.org/standard/63582.html

S03 — NASA Systems Engineering Handbook, NASA SP-2016-6105 Rev2, các trang Fundamentals và tài liệu Handbook. Loại: sổ tay phương pháp của NASA, không phải quy định bắt buộc cho CC1. Hỗ trợ nhìn vòng đời, quan hệ yêu cầu sản phẩm và kiểm chứng. URL: https://www.nasa.gov/reference/2-0-fundamentals-of-systems-engineering/ ; bản Handbook: https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf

S04 — GAO-20-195G, Cost Estimating and Assessment Guide, công bố 12 tháng 03 năm 2020. Loại: hướng dẫn thực hành ước tính và quản lý chi phí của GAO. Dùng để chọn chủ đề cơ sở ước tính, bất định, WBS và cập nhật actual; không phải nghĩa vụ pháp lý tại Việt Nam. URL: https://www.gao.gov/products/gao-20-195g

S05 — GAO-16-89G, Schedule Assessment Guide, công bố 22 tháng 12 năm 2015. Loại: hướng dẫn thực hành đánh giá tiến độ. Dùng làm tài liệu tham khảo về chất lượng lịch và mạng tiến độ. URL: https://www.gao.gov/products/gao-16-89g

S06 — Lean Construction Institute, Last Planner System. Loại: phương pháp thực hành Lean Construction. Dùng tham khảo kế hoạch và cam kết đáng tin cậy; lookahead sáu tuần và mục tiêu PPC trong tài liệu là đề xuất nội bộ. URL: https://leanconstruction.org/lean-topics/last-planner-system/

S07 — ISO 31000:2018, Risk management — Guidelines. Loại: hướng dẫn quản trị rủi ro, không phải tiêu chuẩn yêu cầu để chứng nhận hệ thống. CC1 dùng làm tham chiếu quản trị rủi ro, không xem một bảng risk register là đủ. URL: https://www.iso.org/standard/31000

S08 — ISO 55001:2024, Asset management — Asset management system — Requirements. Loại: tiêu chuẩn yêu cầu về hệ thống quản lý tài sản. Tài liệu này chỉ đề xuất liên kết dữ liệu vòng đời, chưa đánh giá phù hợp toàn bộ yêu cầu. URL: https://www.iso.org/standard/83054.html

S09 — The Open Group, TOGAF Standard. Loại: tiêu chuẩn và khung kiến trúc doanh nghiệp. Tham khảo cách tổ chức kiến trúc; không triển khai đầy đủ ADM hoặc tuyên bố chứng nhận TOGAF. URL: https://www.opengroup.org/togaf

## A3 Đặc tả kỹ thuật và tài liệu sản phẩm

S10 — Microsoft Learn, Understand star schema and the importance for Power BI. Loại: tài liệu sản phẩm và hướng dẫn mô hình dữ liệu. Hỗ trợ phân biệt fact dimension và thiết kế quan hệ; grain và measure cụ thể của CC1 do tài liệu đề xuất. URL: https://learn.microsoft.com/en-us/power-bi/guidance/star-schema

S11 — W3C PROV-O, The PROV Ontology, W3C Recommendation 30 April 2013. Loại: đặc tả mô hình provenance. Dùng làm tham chiếu nguồn gốc dữ liệu; không bắt buộc CC1 triển khai RDF ngay trong pilot. URL: https://www.w3.org/TR/prov-o/

S12 — OpenAPI Specification 3.1.1. Loại: đặc tả mô tả API. Phiên bản được chọn làm tham chiếu kỹ thuật, không tuyên bố là phiên bản mới nhất. URL: https://spec.openapis.org/oas/v3.1.1.html

S13 — CloudEvents. Loại: đặc tả mô tả sự kiện. Tham khảo phong bì sự kiện; không bảo đảm giao hàng đúng một lần hoặc ngữ nghĩa nghiệp vụ. URL: https://cloudevents.io/

S14 — NIST AI 100-1, Artificial Intelligence Risk Management Framework 1.0, 2023. Loại: khung quản trị rủi ro AI tự nguyện. Các tiêu chí test AI của CC1 là đề xuất riêng. URL: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf

S15 — Odoo 19.0 documentation, Analytic accounting. Loại: tài liệu sản phẩm theo phiên bản. Xác nhận analytic accounts, plans và distribution; tính năng thực tế tùy cấu hình và module của bản đích. URL: https://www.odoo.com/documentation/19.0/applications/finance/accounting/reporting/analytic_accounting.html

S16 — Odoo 19.0 documentation, External JSON-2 API. Loại: tài liệu API theo phiên bản. Nội dung được kiểm tra qua kết quả nguồn chính thức được lập chỉ mục; yêu cầu truy xuất trực tiếp trang có lúc lỗi trong phiên tra cứu. Cần kiểm tra lại quyền API và phương thức với bản cài thực tế trước triển khai. URL: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html

S17 — ISO 19650-1:2018, Information management using building information modelling — Concepts and principles. Loại: tiêu chuẩn khái niệm và nguyên tắc quản lý thông tin. Trang công khai cho thấy bản này được xác nhận năm 2024 và có tiến trình sửa đổi; tài liệu không suy nội dung bản dự thảo thành nghĩa vụ. URL: https://committee.iso.org/standard/68078.html?browse=tc

S18 — buildingSMART International Standards Server và IFC overview. Loại: tiêu chuẩn trao đổi thông tin số, gồm IFC và IDS. Cần chọn phiên bản và thử khả năng hỗ trợ công cụ. URL: https://standards.buildingsmart.org/ ; https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/?lang=en

S19 — Microsoft Learn, Row level security with Power BI. Loại: tài liệu bảo mật sản phẩm. Tham khảo kiểm soát theo vai trò; thiết kế quyền cụ thể phải được kiểm thử trên tenant và workspace thực tế. URL: https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security

## A4 Register tiêu chuẩn và pháp lý cần hoàn thiện

Không có bộ hợp đồng, tiêu chuẩn kỹ thuật, chính sách kế toán và hồ sơ pháp lý CC1 trong đầu vào. Vì vậy không đưa số hiệu văn bản pháp luật Việt Nam chưa được đối chiếu thành yêu cầu bắt buộc. Pháp chế và kỹ thuật cần lập register theo từng dự án gồm cơ quan ban hành, số hiệu, phiên bản, ngày hiệu lực, phạm vi áp dụng, điều khoản hợp đồng dẫn chiếu, owner, bằng chứng tuân thủ và trạng thái kiểm tra. Tài liệu này là nền quản trị dữ liệu, không thay thiết kế cầu, biện pháp thi công hoặc tư vấn pháp lý kế toán.

Các tài liệu PMI, hệ thống EIA về EVM, ISO 21502, ISO 12006 và các chuẩn khác có thể được đưa vào danh mục nghiên cứu tiếp theo khi CC1 quyết định áp dụng. Bản này không tuyên bố đã kiểm chứng nội dung hoặc phiên bản của các tài liệu đó và không gắn điều khoản giả cho chúng.

# Phụ lục B Bộ biểu mẫu triển khai

## B1 Hướng dẫn dùng biểu mẫu

Mỗi biểu mẫu dưới đây có thể sao chép thành hồ sơ làm việc. Ký hiệu \[điền\] là dữ liệu cần cung cấp, không phải một giá trị mặc định. Dữ liệu nhạy cảm được lưu ở nơi phân quyền; Word chỉ chứa URI hoặc ID hồ sơ nếu không cần lưu nội dung chi tiết. Hồ sơ phát hành cần ID, revision, status, owner, approver và ngày hiệu lực.

## F01 Phiếu khởi tạo phạm vi pilot

Mã hồ sơ \[điền\] Phiên bản \[điền\] Ngày \[điền\] Sponsor \[điền\]

Mục tiêu kinh doanh và vấn đề cần giải quyết \[điền thành kết quả đo được\]. Pháp nhân và dự án trong phạm vi \[điền\]. Quy trình bao gồm \[điền\]. Ngoài phạm vi \[điền\]. Ngày 0 và các gate \[điền\].

Hệ thống nguồn và người cấp quyền \[điền\]. Dữ liệu phải sẵn sàng \[điền\]. Ràng buộc nguồn lực và lịch \[điền\]. Tiêu chí thành công \[điền\]. Ngân sách và thẩm quyền \[điền theo hồ sơ được duyệt\].

Chấp thuận của Sponsor \[tên vai trò ngày và tham chiếu phê duyệt\]. Owner nghiệp vụ \[điền\]. Owner dữ liệu \[điền\]. Owner vận hành \[điền\].

## F02 WBS dictionary record

ID \[điền\] Mã \[điền\] Path \[điền\] Parent \[điền\] Baseline \[điền\]

Tên đầu ra \[điền\]. Scope in \[điền\]. Scope out \[điền\]. Giả định \[điền\]. PBS LBS requirement liên quan \[điền ID\].

Loại Summary WP PP \[chọn\]. Lượng và UOM \[điền\]. CA và CAM \[điền\]. BAC từ dòng ngân sách \[điền\]. EV method và điều kiện bằng chứng \[điền\]. Activity links \[điền\].

Acceptance criteria \[điền điều kiện đo được\]. Hồ sơ nguồn \[URI revision hash\]. Readiness \[điền\]. Risk links \[điền\]. Owner soạn \[điền\]. Reviewer \[điền\]. Approver \[điền\]. Hiệu lực \[điền\].

## F03 CBS và mapping tài chính

CBS ID \[điền\] Mã \[điền\] Parent \[điền\] Owner \[điền\]

Định nghĩa loại chi phí \[điền\]. Bao gồm \[điền\]. Loại trừ \[điền\]. Cost basis \[điền\]. Nguyên tắc trực tiếp gián tiếp \[điền\].

| **Rule ID** | **Điều kiện nguồn**              | **CBS đích** | **Hiệu lực và ưu tiên** |
|-------------|----------------------------------|--------------|-------------------------|
| \[điền\]    | GL product document type company | \[điền\]     | \[điền\]                |

Test case vào đúng \[điền\]. Test case loại trừ \[điền\]. Dòng chưa mapping \[điền cách xử lý\]. Finance phê duyệt \[điền\].

## F04 Yêu cầu cấp hoặc thay đổi mã

Loại đối tượng \[điền\] Request ID \[điền\] Người yêu cầu \[điền\]

Tên đề nghị \[điền\]. Định nghĩa \[điền\]. Phạm vi công ty dự án \[điền\]. Kết quả tìm mã trùng \[điền\]. Lý do không dùng mã có sẵn \[điền\]. Parent hoặc liên kết \[điền\]. Ngày cần hiệu lực \[điền\].

Nếu thay đổi: ID cũ \[điền\], đổi tên hoặc tách gộp \[điền\], ảnh hưởng giao dịch \[điền\], alias và successor \[điền\], test mapping \[điền\]. Steward kiểm tra \[điền\]. Owner phê duyệt \[điền\]. Registry phát hành \[điền\].

## F05 Crosswalk và allocation set

Mapping ID \[điền\] Version \[điền\] Purpose \[tra cứu hoặc phân bổ cụ thể\]

Đối tượng nguồn \[type ID revision\]. Đối tượng đích \[type ID revision\]. Basis \[lượng giờ giá trị hoặc quy tắc\]. UOM currency \[điền\]. Hiệu lực \[điền\].

| **Nguồn** | **Đích** | **Driver và weight** | **Giá trị kết quả** |
|-----------|----------|----------------------|---------------------|
| \[điền\]  | \[điền\] | \[điền\]             | \[điền\]            |

Tổng driver \[điền\]. Tổng weight \[điền\]. Chênh lệch nguồn đích \[điền\]. Quy tắc rounding \[điền\]. Chứng từ driver \[điền\]. Người duyệt \[điền\].

## F06 Control account plan

CA ID \[điền\] Scope WBS \[điền\] OBS \[điền\] CAM \[điền\]

Phạm vi chịu trách nhiệm \[điền\]. Work packages \[danh sách ID\]. Planning packages \[danh sách ID và hạn phân rã\]. BAC \[điền\]. Phân kỳ ngân sách \[tham chiếu\]. Calendar và mốc \[điền\].

Phương pháp EV theo từng WP \[điền\]. Quy tắc thu thập AC \[điền\]. Risk và contingency liên quan \[điền\]. Forecast basis \[điền\]. Ngưỡng variance \[điền\]. Hồ sơ IBR và phê duyệt \[điền\].

## F07 Phiếu lượng và bằng chứng nghiệm thu

Record ID \[điền\] Ngày nghiệp vụ \[điền\] WP PBS LBS \[điền\]

Lượng tăng thêm \[điền\]. UOM \[điền\]. Lượng lũy kế trước và sau \[điền\]. Trạng thái thi công \[điền\]. Trạng thái nghiệm thu nội bộ \[điền\]. Trạng thái chấp nhận hợp đồng \[điền riêng\].

Bằng chứng \[document ID revision URI\]. Tiêu chí áp dụng \[rule ID\]. Kết quả kiểm tra \[đạt không đạt có điều kiện\]. NCR hoặc tồn tại \[điền\]. Người lập \[điền\]. Người xác nhận kỹ thuật \[điền\]. Người duyệt theo quyền \[điền\]. EV eligible \[có không và lý do\].

Nếu correction, tham chiếu record gốc \[điền\], lượng đảo \[điền\], lý do \[điền\], người phê duyệt \[điền\].

## F08 Phiếu accrual và đối soát

Accrual ID \[điền\] Kỳ \[điền\] Cutoff \[điền\] Công ty \[điền\]

Nguồn nghĩa vụ \[contract PO receipt ID\]. WP CA CBS \[điền\]. Phần đã ghi actual \[điền\]. Phần chưa hóa đơn ước tính \[điền\]. Cơ sở lượng và giá \[điền\]. Người xác nhận dịch vụ \[điền\].

Amount nguyên tệ \[điền\]. Currency \[điền\]. Tỷ giá và nguồn \[điền\]. Amount quy đổi \[điền\]. Cách tránh trùng \[điền\]. Ngày dự kiến nhận hóa đơn \[điền\]. Reversal rule \[điền\]. Finance duyệt \[điền\].

## F09 Báo cáo sai lệch CA

Kỳ \[điền\] CA \[điền\] Baseline và snapshot \[điền\]

BAC PV EV AC \[điền\]. CV SV CPI SPI \[điền\]. ETC EAC VAC \[điền\]. Phương pháp forecast \[điền\].

Nguyên nhân gốc \[điền lượng giá năng suất thời gian dữ liệu\]. Tác động kỳ này \[điền\]. Tác động khi hoàn thành \[điền\]. Hành động \[điền\]. Owner \[điền\]. Due date \[điền\]. Bằng chứng hoàn tất \[điền\]. CAM ký \[điền\].

## F10 Change request

CR ID \[điền\] Loại thay đổi \[điền\] Người đề nghị \[điền\]

Lý do và nguồn yêu cầu \[điền\]. Phạm vi đối tượng bị ảnh hưởng \[điền ID và revision\]. Hiện trạng \[điền\]. Phương án đề nghị \[điền\]. Phương án thay thế \[điền\].

Tác động scope cost schedule contract risk quality data security \[điền từng mục, nếu không ảnh hưởng nêu căn cứ\]. Ngày hiệu lực \[điền\]. Kế hoạch migration và test \[điền\]. Rollback \[điền\].

Quyết định \[Approve Reject Defer\]. Approval policy và người có quyền \[điền\]. Điều kiện kèm theo \[điền\]. Phiên bản phát hành \[điền\]. Bằng chứng verified \[điền\].

## F11 Risk register và response

Risk ID \[điền\] Category \[điền\] Owner \[điền\] Ngày đánh giá \[điền\]

Nguyên nhân \[điền\]. Sự kiện bất định \[điền\]. Tác động tới mục tiêu \[điền\]. WBS contract asset liên quan \[điền\]. Xác suất và căn cứ \[điền\]. Tác động tiền ngày hoặc chất lượng \[điền\].

Phản ứng \[tránh giảm chuyển giao chấp nhận hoặc khai thác cơ hội tùy loại\]. Hành động trigger owner due date \[điền\]. Residual risk \[điền\]. Contingency link \[điền\]. Nếu xảy ra, issue_id \[điền\].

## F12 Biên bản UAT và nghiệm thu

Đợt \[điền\] Environment \[điền\] Build version \[điền\] Dataset version \[điền\]

| **Test ID** | **Expected và actual result** | **Evidence**                  | **Trạng thái**    |
|-------------|-------------------------------|-------------------------------|-------------------|
| \[điền\]    | \[điền\]                      | URI hash thời gian người chạy | Pass Fail Blocked |

Tổng test trong phạm vi \[điền\]. Passed failed blocked not run \[điền đầy đủ\]. Critical major minor còn mở \[điền\]. Giới hạn chưa kiểm thử \[điền\]. Quyết định \[Accept Conditional Reject\]. Điều kiện và hạn hoàn tất \[điền\]. Chữ ký business data IT và cấp quyết định \[điền theo quyền\].

## F13 Sổ lỗi chất lượng dữ liệu

Issue ID \[điền\] Rule ID \[điền\] Severity \[điền\]

Record set và kỳ ảnh hưởng \[điền\]. Số bản ghi \[điền\]. Amount affected \[điền theo currency\]. Nguyên nhân \[điền\]. Owner \[điền\]. Due date \[điền\]. Sửa tại nguồn mapping hay pipeline \[điền\]. Kết quả retest \[điền\]. Người xác nhận đóng \[điền\].

## F14 Hợp đồng tích hợp và runbook

Interface ID \[điền\] Source owner \[điền\] Target owner \[điền\]

Entity grain schema version \[điền\]. Auth scope \[điền, không ghi secret\]. Trigger frequency cutoff SLA \[điền\]. Idempotency key \[điền\]. Ordering và late data \[điền\]. Retry DLQ replay \[điền\]. Reconciliation \[count totals basis\].

Dashboard vận hành \[URI\]. Alert routing \[vai trò\]. Hướng dẫn incident \[điền\]. RTO RPO \[điền\]. Restore test \[evidence\]. Deploy rollback \[điền\]. Support handover \[điền\].

## F15 Hồ sơ bàn giao tài sản và dữ liệu

Asset ID \[điền\] PBS LBS \[điền\] Owner operator \[điền\]

Serial class manufacturer nếu có \[điền\]. Ngày lắp và nghiệm thu \[điền\]. Document revisions hoàn công vận hành bảo hành \[điền\]. Model object links \[điền\]. Yêu cầu thông tin đã kiểm tra \[điền\]. Tồn tại và trách nhiệm đóng \[điền\].

Dữ liệu bàn giao gồm schema dictionary mapping và quyền sử dụng \[điền\]. Người nhận kiểm tra khả năng mở và truy xuất \[điền\]. Chấp nhận hoặc từ chối kèm lý do \[điền\]. Nghĩa vụ sau bàn giao \[điền\].

# Phụ lục C Data contract và quy tắc tính

## C1 Data product chi phí dự án đã chốt

Owner Finance; steward kế toán dự án; consumer PMO và Power BI theo scope. Grain một dòng cost allocation trong một basis, một snapshot và một nguyên tệ. Khóa allocation_id cộng snapshot_id. Trường tối thiểu gồm project_id, company_id, wbs_id, cbs_id, cost_entry_id, accounting_date, amount_original_currency, currency, amount_reporting_currency, rate_id, accrual_flag, reversal_of_id, mapping_version và lineage.

SLA công bố theo close calendar. Critical quality gồm bảo toàn tổng, FK hợp lệ, không trùng và source reconciliation. Phạm vi loại trừ phải nêu khoản không thuộc cost basis. Khi owner đổi basis, tạo phiên bản data product và giải thích khác biệt; không đổi định nghĩa silently dưới tên measure cũ.

## C2 Data product EVM snapshot

Grain một WP tại một cutoff, baseline và snapshot. PV EV AC là cumulative cùng cơ sở. Khóa duy nhất project_id, wp_id, cutoff, baseline_id, snapshot_id. status là Provisional Final Superseded. Snapshot Final bất biến. Chọn một bản Final được công bố cho kỳ báo cáo; nếu người dùng chọn nhiều kỳ, measure trả xu hướng từng kỳ hoặc lấy kỳ cuối theo định nghĩa, không cộng cumulative.

Validation gồm EV không vượt BAC khi không có adjustment được duyệt, PV tổng các kỳ bằng BAC khi đã phân kỳ toàn bộ, AC khớp data product cost, evidence coverage đạt và không chia cho zero. Giá trị không xác định hiển thị N A kèm lý do; không biến thành 0 vì có thể khiến dashboard hiểu nhầm không có sai lệch.

## C3 Pseudocode kiểm soát

CONTROL allocation: nhóm theo source_entry_id, currency, cost_basis và allocation_version; tính total_allocated; so với source_amount; chặn khi vượt tolerance rounding được duyệt. Không nhóm lẫn analytic plans khác mục đích.

CONTROL ev: lấy quantity accepted cumulative sau reversal; giới hạn phạm vi được duyệt; nhân budget unit cost tương ứng baseline; so EV với BAC; lưu evidence và calculation_version. Với milestone dùng tổng trọng số mốc đạt nhân BAC, không cộng EV quantity trên cùng phạm vi.

CONTROL reconciliation: source total theo công ty kỳ currency cost basis bằng loaded approved total cộng quarantined total cộng explained exclusions. Báo cáo official chỉ được phát khi quarantined trọng yếu bằng 0 và exclusions được ký.

CONTROL period close: nếu critical DQ failed hoặc approval thiếu hoặc source watermark chưa tới cutoff thì status không thể là Final. Quyền bypass khẩn nếu có phải đi qua quy trình đã duyệt và hiển thị exception, không giấu khỏi người đọc.

# Phụ lục D Ví dụ API và sự kiện

## D1 Payload ghi nhận lượng nội bộ

Ví dụ cấu trúc dưới đây là thiết kế giao diện CC1, không phải API đã triển khai. ID ngắn chỉ để minh họa; khi cài đặt dùng UUID hoặc khóa đã quy định.

{

"schema_version": "1.0",

"progress_id": "PRG0001",

"project_id": "BR01",

"wbs_id": "WP00320",

"baseline_id": "BL01",

"business_date": "2026-09-30",

"quantity_delta": "10.000",

"uom": "pile",

"acceptance_record_id": "ACC0001",

"evidence_revision_ids": \["DOC01-R03"\],

"source_revision": 1

}

Ngày ở payload là ngày giả định kỹ thuật cho test, độc lập với T03 minh họa. API gateway xác thực người gọi; server kiểm tra WP, lượng trước đó, quyền, acceptance state và khả năng trùng. Client không truyền EV tùy ý để thay kết quả tính của server.

## D2 Event sau phê duyệt

{

"specversion": "1.0",

"id": "EVENT0001",

"source": "/cc1/pmis/pilot",

"type": "cc1.progress.accepted.v1",

"subject": "progress/PRG0001",

"time": "2026-09-30T10:00:00Z",

"datacontenttype": "application/json",

"data": {

"progress_id": "PRG0001",

"aggregate_version": 1,

"project_id": "BR01",

"acceptance_record_id": "ACC0001",

"schema_version": "1.0"

}

}

Đây là ví dụ phong bì; trường data phải được đặc tả đầy đủ trong data contract hoặc consumer có quyền tải resource theo ID. Event reference chỉ dùng khi tài nguyên nguồn giữ được revision tương ứng; nếu nguồn luôn trả bản mới nhất thì phải gửi snapshot hoặc revision URI để tránh sai lịch sử.

## D3 Bảng lỗi và quyền

| **Error code**          | **Ý nghĩa**                       | **Hành động consumer**                              |
|-------------------------|-----------------------------------|-----------------------------------------------------|
| INVALID_SCHEMA          | Sai kiểu hoặc thiếu trường        | Không retry mù; sửa producer và replay có kiểm soát |
| UNKNOWN_WBS             | Chưa có mã hoặc sai scope         | Kiểm tra registry và hiệu lực; không tự tạo mã      |
| ACCEPTANCE_NOT_APPROVED | Bằng chứng chưa được duyệt        | Chờ nghiệp vụ; không ghi EV                         |
| IDEMPOTENCY_CONFLICT    | Cùng khóa khác nội dung           | Dừng và điều tra                                    |
| STALE_REVISION          | Update trên phiên bản cũ          | Tải lại và xác nhận ý định thay đổi                 |
| SOURCE_UNAVAILABLE      | Nguồn tạm gián đoạn               | Retry theo policy và cảnh báo khi quá SLA           |
| FORBIDDEN_SCOPE         | Không có quyền dự án hoặc công ty | Dừng; không thử tài khoản quyền cao hơn tự động     |

# Phụ lục E Checklist workshop và backlog

## E1 Workshop nghiệp vụ

Trong workshop scope, hỏi ai quyết định công việc hoàn thành, hợp đồng đo theo gì, phần việc nào ngoài phạm vi và sản phẩm bàn giao nào hay bị thiếu. Trong workshop cost, hỏi chi phí xuất hiện ở đâu trước hóa đơn, vật tư và máy ghi nhận lúc nào, accrual ai duyệt và khoản nào thường bị phân bổ lại. Trong workshop schedule, hỏi logic đường găng, calendar, thời gian cập nhật và điều kiện sẵn sàng.

Trong workshop data, hỏi khóa nào ổn định, cột nào chứa nhiều ý nghĩa, mã nào bị tái sử dụng, ai có quyền sửa và báo cáo nào thường không khớp. Trong workshop IT, hỏi phiên bản thật, module, API, hosting, backup, quyền tenant và ràng buộc nâng cấp. Mỗi câu trả lời phải có ví dụ hồ sơ hoặc minh chứng, không chỉ mô tả mong muốn.

## E2 Backlog khởi động có thứ tự

| **ID** | **Deliverable**                   | **Phụ thuộc và điều kiện done**                           |
|--------|-----------------------------------|-----------------------------------------------------------|
| BLG01  | Charter pilot                     | Sponsor, phạm vi, owner và nguồn lực được duyệt           |
| BLG02  | Source inventory và data profile  | BLG01; có mẫu thực tế được phép sử dụng                   |
| BLG03  | Dictionary và registry            | BLG02; kiểm tra trùng, vòng và owner                      |
| BLG04  | WBS CA baseline mẫu               | BLG03; QA Finance PMO đồng ý cách đo                      |
| BLG05  | ERD và data contracts             | BLG04; grain, FK và source of truth rõ                    |
| BLG06  | ERP fit gap và analytic prototype | BLG05; kiểm thử cost basis và multi plan                  |
| BLG07  | Actual và progress integration    | BLG06; dedup, reversal, reconciliation đạt                |
| BLG08  | BI semantic model                 | BLG07; số BR01 đúng và RLS đạt                            |
| BLG09  | UAT migration và restore          | BLG08; critical major bằng 0                              |
| BLG10  | Pilot close và handover           | BLG09; hai kỳ đạt, owner ký và runbook đủ                 |
| BLG11  | AI retrieval có nguồn             | BLG10 hoặc data gate tương đương; test quyền và nguồn đạt |
| BLG12  | Rollout wave 2                    | BLG10; đánh giá lợi ích và readiness dự án mới            |

# Phụ lục F Thuật ngữ thống nhất

| **Thuật ngữ** | **Ý nghĩa sử dụng trong tài liệu**                                          |
|---------------|-----------------------------------------------------------------------------|
| WBS           | Cấu trúc phạm vi công việc; không phải danh sách activity                   |
| CBS hoặc CST  | Cấu trúc chi phí; CST dùng trong mã để tránh nhầm contract                  |
| OBS           | Cấu trúc đơn vị tổ chức, khác người dùng và phân quyền                      |
| RBS hoặc RES  | Nguồn lực; trong API dùng RES để phân biệt risk                             |
| PBS           | Cấu trúc sản phẩm và đầu ra bàn giao                                        |
| LBS hoặc LOC  | Cấu trúc vị trí                                                             |
| CTR           | Hợp đồng; BOQ là các dòng lượng và giá trong ngữ cảnh hợp đồng              |
| RSK và RCT    | Sự kiện rủi ro và nhóm phân loại rủi ro                                     |
| AST           | Tài sản; phân biệt tài sản bàn giao và tài sản sở hữu                       |
| CA và CAM     | Control account và người quản lý CA                                         |
| WP và PP      | Work package và planning package                                            |
| PMB           | Performance measurement baseline, cơ sở đo hiệu suất                        |
| MR            | Management reserve ngoài PMB theo chính sách đề xuất                        |
| PV EV AC BAC  | Giá trị kế hoạch, giá trị đạt được, actual cost và ngân sách khi hoàn thành |
| ETC EAC VAC   | Chi phí còn lại, ước tính khi hoàn thành và chênh ngân sách dự báo          |
| CDE           | Môi trường dữ liệu chung cho thông tin được quản lý                         |
| MDM           | Quản trị dữ liệu chủ và danh mục dùng chung                                 |
| Grain         | Mức chi tiết mà một bản ghi đại diện                                        |
| Crosswalk     | Liên kết mã có mục đích, cơ sở và hiệu lực                                  |
| Snapshot      | Bản chụp dữ liệu tại cutoff và trạng thái phát hành xác định                |
| RACI          | Thực hiện, chịu trách nhiệm cuối, tham vấn, nhận thông tin                  |
| UAT           | Kiểm thử chấp nhận bởi nghiệp vụ                                            |
| RPO RTO       | Mức mất dữ liệu và thời gian phục hồi mục tiêu                              |

# Phụ lục G Sổ giả định và quyết định còn mở

| **ID** | **Giả định hoặc quyết định cần xác minh**                                   | **Owner đề xuất và hạn**                              |
|--------|-----------------------------------------------------------------------------|-------------------------------------------------------|
| ASM01  | CC1 tham gia pilot với vai trò nhà thầu                                     | Sponsor xác nhận trước ngày 10                        |
| ASM02  | Một dự án cầu đủ dữ liệu được chọn                                          | PMO xác nhận trước ngày 10                            |
| ASM03  | Odoo chỉ là phương án tham chiếu, chưa biết phiên bản thật                  | CNTT xác nhận trước ngày 10                           |
| ASM04  | Cost basis và accrual có thể thống nhất giữa Finance PMO                    | Finance xác nhận trước gate 30                        |
| ASM05  | Quyền ký và ngưỡng thay đổi chưa được cung cấp                              | Sponsor và pháp chế trước gate 30                     |
| ASM06  | BIM CDE có thể cung cấp revision và object IDs                              | Kỹ thuật kiểm tra trước gate 60                       |
| ASM07  | KPI và SLA trong tài liệu là mục tiêu đề xuất                               | Business và IT owner chốt trước UAT                   |
| ASM08  | Tài liệu chuẩn có bản quyền cần mua hoặc cấp quyền nếu đối chiếu điều khoản | Owner tiêu chuẩn trước ban hành quy chế               |
| ASM09  | Word cũ không truy cập được trong phiên này                                 | Document owner đối chiếu nếu nhận lại tệp             |
| ASM10  | Số liệu BR01 hoàn toàn giả định                                             | Không dùng cho quyết định đầu tư hoặc thanh toán thật |

Mỗi quyết định kiến trúc mới ghi ADR ID, vấn đề, phương án, tiêu chí lựa chọn, quyết định, người duyệt, ngày và điều kiện xem xét lại. Các quyết định phải ưu tiên chốt là cấp analytic Odoo, nơi quản lý baseline, cost basis, bằng chứng EV, chủ registry và cơ chế công bố snapshot.

# Phụ lục H Lưu vết hội thoại truy cập được

Nguồn CHAT01 Lý thuyết WBS CBS liên quan conversationId 6ac88118-9430-83ec-80f6-0b03faf7a7b9. Đọc 6 lượt theo công cụ ngày 09 tháng 10 năm 2026, hasMore=false, không có tệp đính kèm. Dưới đây giữ nguyên văn nội dung thông điệp lấy được, kể cả dấu Markdown và đường dẫn cũ không còn là liên kết tải khả dụng trong phiên này. Chỉ bổ sung nhãn vai trò để phân biệt. Các tuyên bố trong chat là lịch sử, không được coi tự động là dữ kiện đã xác minh.

## Lượt 1

### Người dùng

wbs, cbs và nhưng cái gì có liên quan, toàn bộ lý thuyết

### Trợ lý

\# HỆ THỐNG LÝ THUYẾT TOÀN DIỆN VỀ WBS, CBS, OBS, RBS, PBS, ABS VÀ CÁC CẤU TRÚC QUẢN TRỊ LIÊN QUAN

\## Từ quản lý dự án đến quản trị doanh nghiệp, ERP, BIM, dữ liệu và trí tuệ nhân tạo

Trong quản trị dự án và quản trị doanh nghiệp hiện đại, \*\*WBS (Work Breakdown Structure)\*\* và \*\*CBS (Cost Breakdown Structure)\*\* chỉ là hai thành phần của một hệ thống lớn hơn, được gọi chung là \*\*hệ thống cấu trúc phân rã, phân loại và liên kết quản trị (Breakdown Structures & Management Taxonomies)\*\*.

Đối với một tập đoàn hoạt động trong lĩnh vực xây dựng, hạ tầng, bất động sản, sản xuất và đầu tư như CC1, cần nghiên cứu toàn bộ hệ thống này chứ không chỉ riêng WBS và CBS.

Đặc biệt, phải phân biệt ba vấn đề:

1\. \*\*Breakdown Structure:\*\* Phân rã một đối tượng thành các thành phần có cấu trúc.

2\. \*\*Classification Structure:\*\* Phân loại các đối tượng theo một hệ thống mã và tiêu chuẩn thống nhất.

3\. \*\*Relationship & Integration Model:\*\* Liên kết các cấu trúc để quản trị đồng bộ công việc, chi phí, tiến độ, nguồn lực, hợp đồng, rủi ro và kết quả.

Một hệ thống quản trị hoàn chỉnh cần cả ba.

---

\# PHẦN I. BẢN ĐỒ TỔNG THỂ CÁC CẤU TRÚC QUẢN TRỊ

\## 1. Các cấu trúc cốt lõi

| STT \| Viết tắt \| Tên tiếng Anh \| Tên tiếng Việt \| Trả lời câu hỏi \|

\|---\|---\|---\|---\|---\|

\| 1 \| WBS \| Work Breakdown Structure \| Cấu trúc phân rã công việc \| Phải làm những gì? \|

\| 2 \| CBS \| Cost Breakdown Structure \| Cấu trúc phân rã chi phí \| Chi phí gồm những gì? \|

\| 3 \| OBS \| Organizational Breakdown Structure \| Cấu trúc phân rã tổ chức \| Đơn vị nào chịu trách nhiệm? \|

\| 4 \| RBS \| Resource Breakdown Structure \| Cấu trúc phân rã nguồn lực \| Cần những nguồn lực nào? \|

\| 5 \| PBS \| Product Breakdown Structure \| Cấu trúc phân rã sản phẩm \| Phải tạo ra những sản phẩm gì? \|

\| 6 \| ABS \| Activity Breakdown Structure \| Cấu trúc phân rã hoạt động \| Các hoạt động được phân chia thế nào? \|

\| 7 \| SBS \| Schedule Breakdown Structure \| Cấu trúc phân rã tiến độ \| Tiến độ được tổ chức thế nào? \|

\| 8 \| Risk BS \| Risk Breakdown Structure \| Cấu trúc phân rã rủi ro \| Rủi ro đến từ đâu? \|

\| 9 \| Contract BS \| Contract Breakdown Structure \| Cấu trúc phân rã hợp đồng \| Công việc được chia thành những hợp đồng nào? \|

\| 10 \| POBS \| Project Organizational Breakdown Structure \| Cấu trúc tổ chức dự án \| Bộ máy dự án được tổ chức ra sao? \|

\| 11 \| FBS \| Functional Breakdown Structure \| Cấu trúc phân rã chức năng \| Hệ thống cần thực hiện những chức năng gì? \|

\| 12 \| SBS \| System Breakdown Structure \| Cấu trúc phân rã hệ thống \| Hệ thống gồm những thành phần nào? \|

\| 13 \| EBS \| Equipment Breakdown Structure \| Cấu trúc phân rã thiết bị \| Thiết bị được tổ chức thế nào? \|

\| 14 \| LBS \| Location Breakdown Structure \| Cấu trúc phân rã vị trí \| Công việc diễn ra ở đâu? \|

\| 15 \| DBS \| Deliverable Breakdown Structure \| Cấu trúc phân rã sản phẩm bàn giao \| Phải bàn giao những gì? \|

\| 16 \| BBS \| Budget Breakdown Structure \| Cấu trúc phân rã ngân sách \| Ngân sách được phân bổ thế nào? \|

\| 17 \| FBS \| Financial Breakdown Structure \| Cấu trúc phân rã tài chính \| Dòng vốn và nghĩa vụ tài chính gồm những gì? \|

\| 18 \| QBS \| Quality Breakdown Structure \| Cấu trúc phân rã chất lượng \| Các yêu cầu chất lượng gồm những gì? \|

\| 19 \| HBS \| Hazard Breakdown Structure \| Cấu trúc phân rã mối nguy \| Có những mối nguy nào? \|

\| 20 \| IBS \| Information Breakdown Structure \| Cấu trúc phân rã thông tin \| Cần quản lý những nhóm thông tin nào? \|

\*\*Lưu ý quan trọng:\*\* Các chữ viết tắt không phải lúc nào cũng có một ý nghĩa thống nhất trên toàn thế giới. Chẳng hạn, RBS có thể là Resource Breakdown Structure hoặc Risk Breakdown Structure; SBS có thể chỉ Schedule Breakdown Structure hoặc System Breakdown Structure.

WBS, OBS, RBS và Risk Breakdown Structure có cơ sở sử dụng rộng rãi trong quản lý dự án. Nhiều tên gọi khác trong bảng là các cấu trúc được sử dụng theo ngành hoặc do doanh nghiệp tự thiết kế. Không nên coi tất cả là những chuẩn độc lập được PMI hay ISO chính thức định nghĩa.

Để triển khai trong CC1, tôi đề xuất quy định một bộ thuật ngữ nội bộ thống nhất, tránh một chữ viết tắt có nhiều nghĩa.

---

\# PHẦN II. LÝ THUYẾT NỀN TẢNG

\## 2. Breakdown Structure là gì?

\*\*Breakdown Structure là mô hình phân rã có thứ bậc, trong đó một đối tượng tổng thể được chia thành các thành phần nhỏ hơn theo những nguyên tắc xác định.\*\*

Ví dụ, một dự án xây dựng cầu có thể được phân rã:

\*\*Dự án cầu\*\*

\- Công tác chuẩn bị

\- Thiết kế

\- Giải phóng mặt bằng

\- Thi công nền móng

\- Thi công kết cấu dưới

\- Thi công kết cấu trên

\- Thi công đường dẫn

\- Hoàn thiện

\- Kiểm tra, nghiệm thu và bàn giao

Đây là một cách nhìn theo phạm vi công việc.

Cũng dự án đó, nếu phân rã theo chi phí:

\*\*Tổng chi phí dự án\*\*

\- Chi phí xây dựng

\- Chi phí thiết bị

\- Chi phí quản lý dự án

\- Chi phí tư vấn

\- Chi phí bồi thường, hỗ trợ, tái định cư

\- Chi phí khác

\- Chi phí dự phòng

Đây là cách nhìn theo chi phí đầu tư.

Hai cấu trúc mô tả cùng một dự án nhưng có mục đích khác nhau.

\### 2.1. Năm nguyên tắc quan trọng

\*\*Nguyên tắc 1 — Phân rã theo một logic rõ ràng\*\*

Mỗi cấu trúc phải xác định đối tượng, mục đích và tiêu chí phân rã.

Ví dụ:

\- WBS phân rã phạm vi công việc.

\- CBS phân rã chi phí.

\- OBS phân rã trách nhiệm tổ chức.

\- PBS phân rã sản phẩm.

\- LBS phân rã vị trí.

\*\*Nguyên tắc 2 — Quy tắc 100%\*\*

Đặc biệt quan trọng đối với WBS.

Tổng phạm vi của các thành phần cấp dưới phải bao phủ 100% phạm vi của thành phần cấp trên, không thiếu và không tính trùng.

\*\*Nguyên tắc 3 — Không chồng chéo\*\*

Một đối tượng không nên bị tính hai lần trong cùng một phép phân rã cộng gộp.

Tuy nhiên, cùng một đối tượng có thể được liên kết với nhiều cấu trúc khác nhau.

Ví dụ: Một hạng mục móng cầu có thể đồng thời liên kết với WBS, CBS, OBS, LBS và hợp đồng thi công.

\*\*Nguyên tắc 4 — Có khả năng truy vết\*\*

Mỗi thành phần phải có mã định danh, mô tả, cấp cha, trạng thái và quan hệ với các đối tượng liên quan.

\*\*Nguyên tắc 5 — Có khả năng tổng hợp và kiểm soát\*\*

Hệ thống phải tổng hợp được từ cấp chi tiết lên cấp quản trị.

Ví dụ:

Khối lượng thi công → Hạng mục → Gói thầu → Dự án → Danh mục dự án → Tập đoàn.

---

\## 3. Phân biệt Hierarchy, Taxonomy, Ontology và Graph

Đây là phần rất quan trọng nếu CC1 muốn ứng dụng AI vào quản trị.

\| Khái niệm \| Bản chất \| Ví dụ \|

\|---\|---\|---\|

\| Hierarchy \| Cấu trúc thứ bậc \| Dự án → Hạng mục → Công việc \|

\| Taxonomy \| Hệ thống phân loại \| Danh mục loại chi phí \|

\| Ontology \| Mô hình khái niệm và quan hệ \| Công việc sử dụng nguồn lực, phát sinh chi phí \|

\| Graph \| Mạng lưới các đối tượng và quan hệ \| WBS liên kết CBS, OBS, hợp đồng, tiến độ \|

\| Master Data \| Dữ liệu chủ được quản trị thống nhất \| Danh mục dự án, đơn vị, vật tư \|

\| Reference Data \| Dữ liệu tham chiếu \| Loại công việc, loại chi phí, trạng thái \|

\| Metadata \| Dữ liệu mô tả dữ liệu \| Mã, nguồn, phiên bản, chủ sở hữu \|

\| Knowledge Graph \| Đồ thị tri thức \| Mạng quan hệ dự án phục vụ truy vấn và AI \|

Điểm cần nhấn mạnh:

\*\*WBS là một cấu trúc phân rã. Nhưng khi kết nối WBS với CBS, OBS, RBS, hợp đồng, tiến độ và dữ liệu thực tế, chúng ta bắt đầu hình thành mô hình quản trị đa chiều.\*\*

Đây là nền tảng cho quản trị bằng dữ liệu và AI.

## Lượt 2

### Người dùng

những cái này liên quan đến những lý thuyết nào

Ghi chú lưu vết do bản triển khai bổ sung Không có câu trả lời trợ lý trong lượt truy cập được này. Không phục dựng nội dung đã mất.

## Lượt 3

### Người dùng

những cái này liên quan đến những lý thuyết nào

Ghi chú lưu vết do bản triển khai bổ sung Không có câu trả lời trợ lý trong lượt truy cập được này. Không phục dựng nội dung đã mất.

## Lượt 4

### Người dùng

tại sao hiện nội dung ra rồi lại mất

### Trợ lý

Có thể ứng dụng ChatGPT đang gặp lỗi hiển thị hoặc đồng bộ nội dung, khiến câu trả lời \*\*đã xuất hiện rồi lại biến mất\*\*. Tôi không xem được trực tiếp màn hình của anh nên chưa xác định chính xác nguyên nhân.

Có ba khả năng thường gặp: ứng dụng tự tải lại cuộc trò chuyện, kết nối mạng bị gián đoạn trong lúc câu trả lời đang hiển thị, hoặc hệ thống gặp lỗi khi cập nhật nội dung.

Anh thử \*\*đóng rồi mở lại cuộc trò chuyện\*\*. Nếu vẫn không thấy, anh có thể thoát và mở lại ứng dụng ChatGPT.

Về nội dung anh đang hỏi, tôi vẫn nắm được chủ đề: \*\*WBS, CBS, OBS, RBS và toàn bộ các lý thuyết nền tảng liên quan\*\*, bao gồm quản trị dự án, lý thuyết hệ thống, phân rã cấu trúc, quản trị doanh nghiệp, kiến trúc doanh nghiệp, dữ liệu và AI.

Tôi có thể trình bày lại đầy đủ, theo hệ thống từ lý thuyết nền tảng đến các phương pháp và tiêu chuẩn quốc tế, thay vì chỉ liệt kê các chữ viết tắt.

\*\*Anh cho tôi biết thêm một chút: nội dung biến mất ngay khi tôi đang trả lời, hay đã hiển thị đầy đủ rồi sau đó mới mất?\*\*

## Lượt 5

### Người dùng

hỏi những cái này liên quan đến những lý thuyết nào

2 lần. bây gười mày xuât toàn bộ những cái tra lời trong chat này ra và nhưng kiến thức và lý thuyên có liên qua ra file word

### Trợ lý

Tôi đã tạo file Word tổng hợp nội dung cuộc trò chuyện và hệ thống kiến thức, lý thuyết liên quan đến \*\*WBS, CBS, OBS, RBS, PBS và các cấu trúc quản trị khác\*\*.

📄 \*\*:chatgpt-content-reference{index="0"}\[Tải file Word – WBS, CBS và Hệ thống lý thuyết tổng hợp\](sandbox:/mnt/data/WBS_CBS_He_thong_ly_thuyet_tong_hop.docx)\*\*

Tài liệu gồm 8 phần, bao quát:

1\. Nội dung cuộc trò chuyện hiện còn truy cập được.

2\. \*\*24 nhóm lý thuyết nền tảng\*\*, từ lý thuyết hệ thống, phân rã cấu trúc đến quản trị dự án và doanh nghiệp.

3\. Các cấu trúc WBS, CBS, OBS, RBS, PBS và những cấu trúc liên quan.

4\. Lý thuyết liên kết các cấu trúc để quản trị đa chiều.

5\. Ví dụ ứng dụng trong dự án xây dựng cầu.

6\. Kiến trúc tích hợp ERP, PMIS, BIM, BI và AI.

7\. Nguyên tắc quản trị dữ liệu và lộ trình triển khai.

8\. Các tiêu chuẩn và tài liệu quốc tế để nghiên cứu chuyên sâu.

\*\*Một điểm tôi cần nói rõ:\*\* Hai lần anh hỏi về các lý thuyết liên quan không có nội dung trả lời chuyên môn còn truy cập được. Vì vậy, tôi đã ghi nhận điều này trong tài liệu và bổ sung phần kiến thức mới, thay vì tự dựng lại câu trả lời rồi coi là nguyên văn.

File Word có thể tiếp tục chỉnh sửa, mở rộng và phát triển thành \*\*bộ lý thuyết nền tảng về kiến trúc quản trị dự án và doanh nghiệp CC1\*\*.

## Lượt 6

### Người dùng

đầy đủ và chi tiết nhất có thể để triển khai

### Trợ lý

Tôi đã chuyển yêu cầu sang \*\*Work\*\* để xây dựng bộ tài liệu Word chuyên sâu, đầy đủ và có thể sử dụng làm cơ sở triển khai thực tế tại CC1.

Tài liệu sẽ không dừng ở việc giải thích WBS, CBS, OBS, RBS, PBS mà mở rộng thành \*\*hệ thống kiến trúc quản trị tích hợp\*\*, bao gồm:

1\. \*\*Nền tảng lý thuyết:\*\* Lý thuyết hệ thống, quản trị dự án, kỹ nghệ hệ thống, kiến trúc doanh nghiệp, quản trị quy trình, dữ liệu và AI.

2\. \*\*Hệ thống cấu trúc quản trị:\*\* Định nghĩa, nguyên tắc phân rã, mã hóa, phân cấp, quan hệ và phương pháp xây dựng từng cấu trúc.

3\. \*\*Mô hình tích hợp:\*\* Liên kết WBS–CBS–OBS–RBS–PBS với tiến độ, ngân sách, hợp đồng, nguồn lực, rủi ro, chất lượng và tài sản.

4\. \*\*Kiến trúc công nghệ:\*\* Tích hợp ERP/Odoo, PMIS, BIM, Power BI, Data Warehouse, Knowledge Graph và AI.

5\. \*\*Quy trình triển khai:\*\* Phân quyền, trách nhiệm, kiểm soát thay đổi, quản trị phiên bản, chất lượng dữ liệu và nghiệm thu.

6\. \*\*Biểu mẫu và ví dụ:\*\* WBS Dictionary, CBS Dictionary, RACI, Control Account, mô hình dữ liệu, KPI và các tình huống dự án cầu.

7\. \*\*Lộ trình thực hiện:\*\* Kế hoạch 30–60–90–180 ngày, sản phẩm bàn giao, đơn vị chịu trách nhiệm và tiêu chí nghiệm thu.

\*\*Mục tiêu cuối cùng:\*\* Tạo ra một bộ tài liệu có thể dùng để giao nhiệm vụ cho Ban Chuyển đổi số, Ban Quản lý dự án, Tài chính, Kế toán, Kỹ thuật và các đơn vị triển khai ERP/AI của CC1.

Yêu cầu đã được chuyển sang cuộc làm việc chuyên sâu để tiếp tục xây dựng file Word hoàn chỉnh.

# Phụ lục I Quy tắc tiếp nhận và cập nhật tài liệu

Bản 1.0 được tạo từ hội thoại truy cập được và thiết kế mới. Nếu nhận lại Word gốc, người quản lý tài liệu lưu hash tệp, đối chiếu mục lục và nội dung, đưa phần còn thiếu vào nhật ký chênh lệch; không ghi đè phụ lục nguyên văn. Mỗi thay đổi sau thẩm định phải có mã yêu cầu, người duyệt, ngày hiệu lực và bản phát hành thay thế.

Hồ sơ bàn giao tối thiểu khi triển khai thật gồm tài liệu đã duyệt, nguồn dữ liệu và mapping đã duyệt, bản cấu hình, mã nguồn tích hợp, bộ kiểm thử và bằng chứng chạy, runbook, quyền sở hữu và quyền sử dụng, bản sao lưu, biên bản đào tạo và biên bản nghiệm thu. Tài liệu Word này cung cấp thiết kế và mẫu hồ sơ; không chứng minh hệ thống đã được cài đặt hoặc kiểm thử tại CC1.

# Mục lục chi tiết

Chọn tên mục để mở nội dung. Các số trang theo bản phát hành. Menu này bổ sung khả năng tra cứu, giữ nguyên nội dung chuyên môn và lưu vết hội thoại. [Về mục lục tổng quan](#mục-lục)

- [**1 Cách sử dụng và phạm vi triển khai**](#1-cách-sử-dụng-và-phạm-vi-triển-khai)
> [1.1 Quyết định triển khai đề xuất](#11-quyết-định-triển-khai-đề-xuất) 3
>
> [1.2 Bốn lớp nội dung và mức tin cậy](#12-bốn-lớp-nội-dung-và-mức-tin-cậy) 3
>
> [1.3 Ranh giới nghiệp vụ](#13-ranh-giới-nghiệp-vụ) 3
>
> [1.4 Điều kiện đầu vào cần thu thập trong 10 ngày đầu](#14-điều-kiện-đầu-vào-cần-thu-thập-trong-10-ngày-đầu) 3
>
> [1.5 Bản đồ đọc theo vai trò](#15-bản-đồ-đọc-theo-vai-trò) 4

- [**2 Nền tảng lý thuyết và cách chuyển thành thiết kế**](#2-nền-tảng-lý-thuyết-và-cách-chuyển-thành-thiết-kế)
> [2.1 Bản chất của hệ thống quản trị tích hợp](#21-bản-chất-của-hệ-thống-quản-trị-tích-hợp) 4
>
> [2.2 Hai mươi bốn nhóm lý thuyết liên quan](#22-hai-mươi-bốn-nhóm-lý-thuyết-liên-quan) 4
>
> [1 Lý thuyết hệ thống](#1-lý-thuyết-hệ-thống) 4
>
> [2 Phân rã và tính mô đun](#2-phân-rã-và-tính-mô-đun) 5
>
> [3 Kỹ nghệ yêu cầu](#3-kỹ-nghệ-yêu-cầu) 5
>
> [4 Quản lý cấu hình và baseline](#4-quản-lý-cấu-hình-và-baseline) 5
>
> [5 Quản trị dự án tích hợp](#5-quản-trị-dự-án-tích-hợp) 5
>
> [6 Ước tính chi phí và cơ sở ước tính](#6-ước-tính-chi-phí-và-cơ-sở-ước-tính) 5
>
> [7 Kiểm soát phản hồi bằng EVM](#7-kiểm-soát-phản-hồi-bằng-evm) 5
>
> [8 Mạng tiến độ và đường găng](#8-mạng-tiến-độ-và-đường-găng) 5
>
> [9 Lean Construction và độ tin cậy kế hoạch](#9-lean-construction-và-độ-tin-cậy-kế-hoạch) 5
>
> [10 Tối ưu ràng buộc và dòng công việc](#10-tối-ưu-ràng-buộc-và-dòng-công-việc) 6
>
> [11 Quản trị tổ chức ma trận](#11-quản-trị-tổ-chức-ma-trận) 6
>
> [12 Phân tách nhiệm vụ và kiểm soát nội bộ](#12-phân-tách-nhiệm-vụ-và-kiểm-soát-nội-bộ) 6
>
> [13 Hợp đồng và phân bổ trách nhiệm](#13-hợp-đồng-và-phân-bổ-trách-nhiệm) 6
>
> [14 Rủi ro và quyết định dưới bất định](#14-rủi-ro-và-quyết-định-dưới-bất-định) 6
>
> [15 Chất lượng và kiểm chứng](#15-chất-lượng-và-kiểm-chứng) 6
>
> [16 Quản lý tài sản theo vòng đời](#16-quản-lý-tài-sản-theo-vòng-đời) 6
>
> [17 Kiến trúc doanh nghiệp](#17-kiến-trúc-doanh-nghiệp) 6
>
> [18 Quản lý quy trình và trạng thái](#18-quản-lý-quy-trình-và-trạng-thái) 6
>
> [19 Mô hình quan hệ và chuẩn hóa](#19-mô-hình-quan-hệ-và-chuẩn-hóa) 7
>
> [20 Mô hình chiều và số liệu cộng gộp](#20-mô-hình-chiều-và-số-liệu-cộng-gộp) 7
>
> [21 Ontology và đồ thị tri thức](#21-ontology-và-đồ-thị-tri-thức) 7
>
> [22 Provenance và quản trị dữ liệu](#22-provenance-và-quản-trị-dữ-liệu) 7
>
> [23 Hệ phân tán và nhất quán cuối cùng](#23-hệ-phân-tán-và-nhất-quán-cuối-cùng) 7
>
> [24 AI và quản trị quyết định](#24-ai-và-quản-trị-quyết-định) 7
>
> [2.3 Những đánh đồng cần loại bỏ](#23-những-đánh-đồng-cần-loại-bỏ) 7
>
> [2.4 Cách chọn mức áp dụng tiêu chuẩn](#24-cách-chọn-mức-áp-dụng-tiêu-chuẩn) 7

- [**3 Kiến trúc các cấu trúc quản trị**](#3-kiến-trúc-các-cấu-trúc-quản-trị)
> [3.1 Nguyên tắc thiết kế chung](#31-nguyên-tắc-thiết-kế-chung) 8
>
> [3.2 WBS và work package](#32-wbs-và-work-package) 8
>
> [3.3 CBS theo góc nhìn nhà thầu](#33-cbs-theo-góc-nhìn-nhà-thầu) 8
>
> [3.4 OBS và trách nhiệm](#34-obs-và-trách-nhiệm) 9
>
> [3.5 RBS nguồn lực](#35-rbs-nguồn-lực) 9
>
> [3.6 PBS và LBS](#36-pbs-và-lbs) 9
>
> [3.7 Contract và BOQ](#37-contract-và-boq) 9
>
> [3.8 Risk và hazard](#38-risk-và-hazard) 9
>
> [3.9 Asset và data](#39-asset-và-data) 10

- [**4 Dictionary mã hóa và crosswalk**](#4-dictionary-mã-hóa-và-crosswalk)
> [4.1 Từ điển dữ liệu chung](#41-từ-điển-dữ-liệu-chung) 10
>
> [4.2 Dictionary WBS có thể dùng làm cấu hình](#42-dictionary-wbs-có-thể-dùng-làm-cấu-hình) 11
>
> [4.3 Dictionary bổ sung theo đối tượng](#43-dictionary-bổ-sung-theo-đối-tượng) 11
>
> [4.4 Quy tắc mã hóa đề xuất](#44-quy-tắc-mã-hóa-đề-xuất) 12
>
> [4.5 Quy trình cấp và đổi mã](#45-quy-trình-cấp-và-đổi-mã) 13
>
> [4.6 Crosswalk theo mục đích](#46-crosswalk-theo-mục-đích) 13
>
> [4.7 Ví dụ phân bổ không cộng trùng](#47-ví-dụ-phân-bổ-không-cộng-trùng) 13
>
> [4.8 Kiểm thử crosswalk](#48-kiểm-thử-crosswalk) 14

- [**5 Governance và RACI**](#5-governance-và-raci)
> [5.1 Cơ cấu ra quyết định đề xuất](#51-cơ-cấu-ra-quyết-định-đề-xuất) 14
>
> [5.2 Ma trận RACI thực thi](#52-ma-trận-raci-thực-thi) 14
>
> [5.3 Nhịp điều hành và escalation](#53-nhịp-điều-hành-và-escalation) 15
>
> [5.4 Phân quyền và kiểm toán](#54-phân-quyền-và-kiểm-toán) 15

- [**6 Control accounts và baseline tích hợp**](#6-control-accounts-và-baseline-tích-hợp)
> [6.1 Cách thiết kế control account](#61-cách-thiết-kế-control-account) 15
>
> [6.2 Cấu phần bộ baseline](#62-cấu-phần-bộ-baseline) 16
>
> [6.3 Trình tự phê duyệt baseline](#63-trình-tự-phê-duyệt-baseline) 16
>
> [6.4 Dự phòng và forecast](#64-dự-phòng-và-forecast) 16

- [**7 EVM và kiểm soát chi phí tiến độ**](#7-evm-và-kiểm-soát-chi-phí-tiến-độ)
> [7.1 Định nghĩa vận hành](#71-định-nghĩa-vận-hành) 16
>
> [7.2 Phương pháp earned value](#72-phương-pháp-earned-value) 17
>
> [7.3 Actual và các khoản dễ nhầm](#73-actual-và-các-khoản-dễ-nhầm) 17
>
> [7.4 Close calendar đề xuất](#74-close-calendar-đề-xuất) 18
>
> [7.5 Phân tích sai lệch và hành động](#75-phân-tích-sai-lệch-và-hành-động) 18

- [**8 Quy trình nghiệp vụ từ hợp đồng đến bàn giao**](#8-quy-trình-nghiệp-vụ-từ-hợp-đồng-đến-bàn-giao)
> [8.1 Khởi tạo dự án và giao công việc](#81-khởi-tạo-dự-án-và-giao-công-việc) 18
>
> [8.2 Mua sắm và thầu phụ](#82-mua-sắm-và-thầu-phụ) 19
>
> [8.3 Hiện trường và nghiệm thu khối lượng](#83-hiện-trường-và-nghiệm-thu-khối-lượng) 19
>
> [8.4 Thanh toán và cash flow](#84-thanh-toán-và-cash-flow) 19
>
> [8.5 Bàn giao công trình và tài sản](#85-bàn-giao-công-trình-và-tài-sản) 19

- [**9 ERD logic và kiến trúc dữ liệu**](#9-erd-logic-và-kiến-trúc-dữ-liệu)
> [9.1 Các lớp lưu trữ đề xuất](#91-các-lớp-lưu-trữ-đề-xuất) 19
>
> [9.2 ERD logic theo quan hệ và lực lượng](#92-erd-logic-theo-quan-hệ-và-lực-lượng) 20
>
> [9.3 Danh mục thực thể và grain](#93-danh-mục-thực-thể-và-grain) 20
>
> [9.4 Ràng buộc logic cần hiện thực](#94-ràng-buộc-logic-cần-hiện-thực) 22
>
> [9.5 Lịch sử hiệu lực và lịch sử ghi nhận](#95-lịch-sử-hiệu-lực-và-lịch-sử-ghi-nhận) 22
>
> [9.6 Mô hình sao cho Power BI](#96-mô-hình-sao-cho-power-bi) 22

- [**10 ERP Odoo PMIS BIM và Power BI**](#10-erp-odoo-pmis-bim-và-power-bi)
> [10.1 Phân công hệ thống](#101-phân-công-hệ-thống) 22
>
> [10.2 Thiết kế Odoo có điều kiện theo phiên bản](#102-thiết-kế-odoo-có-điều-kiện-theo-phiên-bản) 23
>
> [10.3 Nguyên tắc cấu hình và mở rộng Odoo](#103-nguyên-tắc-cấu-hình-và-mở-rộng-odoo) 23
>
> [10.4 Fit gap cần nhà triển khai trả lời](#104-fit-gap-cần-nhà-triển-khai-trả-lời) 24
>
> [10.5 PMIS và lập tiến độ](#105-pmis-và-lập-tiến-độ) 24
>
> [10.6 BIM và quản lý thông tin](#106-bim-và-quản-lý-thông-tin) 24
>
> [10.7 Power BI và hợp đồng chỉ số](#107-power-bi-và-hợp-đồng-chỉ-số) 25

- [**11 API sự kiện và vận hành tích hợp**](#11-api-sự-kiện-và-vận-hành-tích-hợp)
> [11.1 Mô hình giao tiếp](#111-mô-hình-giao-tiếp) 25
>
> [11.2 Danh mục giao diện cần bàn giao](#112-danh-mục-giao-diện-cần-bàn-giao) 25
>
> [11.3 Hợp đồng API đề xuất](#113-hợp-đồng-api-đề-xuất) 26
>
> [11.4 Event contract và thứ tự](#114-event-contract-và-thứ-tự) 26
>
> [11.5 Retry lỗi và replay](#115-retry-lỗi-và-replay) 26
>
> [11.6 Bảo mật và khả năng phục hồi](#116-bảo-mật-và-khả-năng-phục-hồi) 26

- [**12 Chất lượng dữ liệu và AI**](#12-chất-lượng-dữ-liệu-và-ai)
> [12.1 Data quality gate](#121-data-quality-gate) 27
>
> [12.2 Quản lý lỗi dữ liệu](#122-quản-lý-lỗi-dữ-liệu) 27
>
> [12.3 Danh mục AI triển khai theo rủi ro](#123-danh-mục-ai-triển-khai-theo-rủi-ro) 27
>
> [12.4 Kiến trúc AI có truy vết](#124-kiến-trúc-ai-có-truy-vết) 28
>
> [12.5 Đánh giá AI trước phát hành](#125-đánh-giá-ai-trước-phát-hành) 28

- [**13 Ví dụ xuyên suốt dự án cầu BR01**](#13-ví-dụ-xuyên-suốt-dự-án-cầu-br01)
> [13.1 Giả định và ranh giới](#131-giả-định-và-ranh-giới) 28
>
> [13.2 WBS và ngân sách kiểm soát](#132-wbs-và-ngân-sách-kiểm-soát) 28
>
> [13.3 Dictionary đã điền cho gói cọc P01](#133-dictionary-đã-điền-cho-gói-cọc-p01) 29
>
> [13.4 CBS của gói cọc và crosswalk đã điền](#134-cbs-của-gói-cọc-và-crosswalk-đã-điền) 30
>
> [13.5 EV của gói cọc](#135-ev-của-gói-cọc) 30
>
> [13.6 Đối soát EVM toàn dự án](#136-đối-soát-evm-toàn-dự-án) 30
>
> [13.7 Tiến độ minh họa và hành động](#137-tiến-độ-minh-họa-và-hành-động) 31
>
> [13.8 Rủi ro và thay đổi minh họa](#138-rủi-ro-và-thay-đổi-minh-họa) 31
>
> [13.9 Chuỗi dữ liệu từ hiện trường tới báo cáo](#139-chuỗi-dữ-liệu-từ-hiện-trường-tới-báo-cáo) 32

- [**14 Roadmap 30 60 90 180 ngày**](#14-roadmap-30-60-90-180-ngày)
> [14.1 Điều kiện tính ngày và nguồn lực](#141-điều-kiện-tính-ngày-và-nguồn-lực) 32
>
> [14.2 Ngày 1 đến 30 chốt nền tảng](#142-ngày-1-đến-30-chốt-nền-tảng) 32
>
> [14.3 Ngày 31 đến 60 xây và kiểm thử tích hợp](#143-ngày-31-đến-60-xây-và-kiểm-thử-tích-hợp) 32
>
> [14.4 Ngày 61 đến 90 thí điểm có kiểm soát](#144-ngày-61-đến-90-thí-điểm-có-kiểm-soát) 33
>
> [14.5 Ngày 91 đến 180 mở rộng theo đợt](#145-ngày-91-đến-180-mở-rộng-theo-đợt) 33
>
> [14.6 Ước lượng nguồn lực và ngân sách triển khai](#146-ước-lượng-nguồn-lực-và-ngân-sách-triển-khai) 33

- [**15 KPI acceptance criteria và nghiệm thu**](#15-kpi-acceptance-criteria-và-nghiệm-thu)
> [15.1 Bộ KPI có chủ sở hữu](#151-bộ-kpi-có-chủ-sở-hữu) 33
>
> [15.2 Ma trận yêu cầu và test chấp nhận](#152-ma-trận-yêu-cầu-và-test-chấp-nhận) 34
>
> [15.3 Nghiệm thu hiệu năng và dữ liệu di trú](#153-nghiệm-thu-hiệu-năng-và-dữ-liệu-di-trú) 35
>
> [15.4 Phân loại lỗi và go no go](#154-phân-loại-lỗi-và-go-no-go) 35
>
> [15.5 Nghiệm thu không đồng nghĩa hoàn tất công tác quản trị](#155-nghiệm-thu-không-đồng-nghĩa-hoàn-tất-công-tác-quản-trị) 35

- [**16 Change control versioning và quản lý phát hành**](#16-change-control-versioning-và-quản-lý-phát-hành)
> [16.1 Phân biệt các loại thay đổi](#161-phân-biệt-các-loại-thay-đổi) 36
>
> [16.2 Quy trình thay đổi có điểm kiểm soát](#162-quy-trình-thay-đổi-có-điểm-kiểm-soát) 36
>
> [16.3 Quy tắc phiên bản và tương thích](#163-quy-tắc-phiên-bản-và-tương-thích) 36
>
> [16.4 Mở lại kỳ và tái trình bày](#164-mở-lại-kỳ-và-tái-trình-bày) 37
>
> [16.5 Cutover và rollback](#165-cutover-và-rollback) 37

- [**Phụ lục A Danh mục nguồn và giới hạn sử dụng**](#phụ-lục-a-danh-mục-nguồn-và-giới-hạn-sử-dụng)
> [A1 Nguyên tắc trích dẫn](#a1-nguyên-tắc-trích-dẫn) 38
>
> [A2 Tiêu chuẩn hướng dẫn và khung phương pháp](#a2-tiêu-chuẩn-hướng-dẫn-và-khung-phương-pháp) 38
>
> [A3 Đặc tả kỹ thuật và tài liệu sản phẩm](#a3-đặc-tả-kỹ-thuật-và-tài-liệu-sản-phẩm) 38
>
> [A4 Register tiêu chuẩn và pháp lý cần hoàn thiện](#a4-register-tiêu-chuẩn-và-pháp-lý-cần-hoàn-thiện) 39

- [**Phụ lục B Bộ biểu mẫu triển khai**](#phụ-lục-b-bộ-biểu-mẫu-triển-khai)
> [B1 Hướng dẫn dùng biểu mẫu](#b1-hướng-dẫn-dùng-biểu-mẫu) 40
>
> [F01 Phiếu khởi tạo phạm vi pilot](#f01-phiếu-khởi-tạo-phạm-vi-pilot) 40
>
> [F02 WBS dictionary record](#f02-wbs-dictionary-record) 40
>
> [F03 CBS và mapping tài chính](#f03-cbs-và-mapping-tài-chính) 40
>
> [F04 Yêu cầu cấp hoặc thay đổi mã](#f04-yêu-cầu-cấp-hoặc-thay-đổi-mã) 40
>
> [F05 Crosswalk và allocation set](#f05-crosswalk-và-allocation-set) 41
>
> [F06 Control account plan](#f06-control-account-plan) 41
>
> [F07 Phiếu lượng và bằng chứng nghiệm thu](#f07-phiếu-lượng-và-bằng-chứng-nghiệm-thu) 41
>
> [F08 Phiếu accrual và đối soát](#f08-phiếu-accrual-và-đối-soát) 41
>
> [F09 Báo cáo sai lệch CA](#f09-báo-cáo-sai-lệch-ca) 41
>
> [F10 Change request](#f10-change-request) 41
>
> [F11 Risk register và response](#f11-risk-register-và-response) 42
>
> [F12 Biên bản UAT và nghiệm thu](#f12-biên-bản-uat-và-nghiệm-thu) 42
>
> [F13 Sổ lỗi chất lượng dữ liệu](#f13-sổ-lỗi-chất-lượng-dữ-liệu) 42
>
> [F14 Hợp đồng tích hợp và runbook](#f14-hợp-đồng-tích-hợp-và-runbook) 42
>
> [F15 Hồ sơ bàn giao tài sản và dữ liệu](#f15-hồ-sơ-bàn-giao-tài-sản-và-dữ-liệu) 42

- [**Phụ lục C Data contract và quy tắc tính**](#phụ-lục-c-data-contract-và-quy-tắc-tính)
> [C1 Data product chi phí dự án đã chốt](#c1-data-product-chi-phí-dự-án-đã-chốt) 43
>
> [C2 Data product EVM snapshot](#c2-data-product-evm-snapshot) 43
>
> [C3 Pseudocode kiểm soát](#c3-pseudocode-kiểm-soát) 43

- [**Phụ lục D Ví dụ API và sự kiện**](#phụ-lục-d-ví-dụ-api-và-sự-kiện)
> [D1 Payload ghi nhận lượng nội bộ](#d1-payload-ghi-nhận-lượng-nội-bộ) 43
>
> [D2 Event sau phê duyệt](#d2-event-sau-phê-duyệt) 44
>
> [D3 Bảng lỗi và quyền](#d3-bảng-lỗi-và-quyền) 44

- [**Phụ lục E Checklist workshop và backlog**](#phụ-lục-e-checklist-workshop-và-backlog)
> [E1 Workshop nghiệp vụ](#e1-workshop-nghiệp-vụ) 45
>
> [E2 Backlog khởi động có thứ tự](#e2-backlog-khởi-động-có-thứ-tự) 45

- [**Phụ lục F Thuật ngữ thống nhất**](#phụ-lục-f-thuật-ngữ-thống-nhất)
- [**Phụ lục G Sổ giả định và quyết định còn mở**](#phụ-lục-g-sổ-giả-định-và-quyết-định-còn-mở)
- [**Phụ lục H Lưu vết hội thoại truy cập được**](#phụ-lục-h-lưu-vết-hội-thoại-truy-cập-được)
> [Lượt 1](#lượt-1) 48
>
> [Người dùng](#người-dùng) 48
>
> [Trợ lý](#trợ-lý) 48
>
> [Lượt 2](#lượt-2) 51
>
> [Người dùng](#người-dùng-1) 51
>
> [Lượt 3](#lượt-3) 51
>
> [Người dùng](#người-dùng-2) 51
>
> [Lượt 4](#lượt-4) 51
>
> [Người dùng](#người-dùng-3) 51
>
> [Trợ lý](#trợ-lý-1) 52
>
> [Lượt 5](#lượt-5) 52
>
> [Người dùng](#người-dùng-4) 52
>
> [Trợ lý](#trợ-lý-2) 52
>
> [Lượt 6](#lượt-6) 53
>
> [Người dùng](#người-dùng-5) 53
>
> [Trợ lý](#trợ-lý-3) 53

- [**Phụ lục I Quy tắc tiếp nhận và cập nhật tài liệu**](#phụ-lục-i-quy-tắc-tiếp-nhận-và-cập-nhật-tài-liệu)