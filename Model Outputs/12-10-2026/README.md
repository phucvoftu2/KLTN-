# Kết quả mô hình — Khóa luận "Trade-off Analysis in Personal Care Supply Chain Distribution Network: An Indonesian Case Study"

Thư mục này gom các kết quả chính của mô hình, **bản chạy ngày 12/10/2026**. Bản này **thay cho** bản 11/10/2026 (thư mục `11-10-2026`, vẫn giữ nguyên để so sánh). Dữ liệu từ một công ty hàng chăm sóc cá nhân ở Indonesia, đã ẩn tên: kho chỉ ghi bằng mã (ví dụ `MWH_D17`, `DEPO03`, `NDC`), không có tên công ty hay tên kho.

---

## Khác gì so với bản 11/10/2026

Sau khi xem bản đồ và kết quả bản 11/10, phát hiện **ba chỗ cần sửa** trong mô hình và **một chỗ cần sửa** trong cách giải. Cả bốn đã được sửa, rồi chạy lại toàn bộ.

### 1. Luồng hàng vô lý giữa các đảo → thêm luật "RDC chỉ giao cho DC Satellite cùng đảo"

**Vấn đề.** Trên bản đồ bản cũ có những luồng hàng rất lạ: RDC ở Sulawesi chở hàng cho DC Satellite ở Kalimantan, trong khi Kalimantan có RDC riêng. Ở phương án ít CO2 nhất còn có RDC Sulawesi chở hàng sang tận Sumatra.

**Nguyên nhân.** Mô hình cũ chỉ quy định *loại kho nào* được giao cho *loại kho nào*, chưa quy định *đảo nào*. Vì vậy 161 trên 162 cặp RDC → DC Satellite đều được phép. Thêm vào đó, tàu biển thải rất ít CO2 trên mỗi tấn-km (22 g, so với 361 g của xe tải). Kết quả là chở hàng **vòng qua biển 2,000 km** lại ít CO2 hơn chở **đường bộ 200 km**. Mô hình cứ thế chọn đường biển xa.

**Đã sửa.** Mỗi DC Satellite chỉ nhận hàng từ RDC **cùng đảo**. Đảo không có RDC (Bali – Nusra, Maluku) thì nhận từ **RDC gần nhất**. Số tuyến kho → kho giảm từ 216 xuống 96.

### 2. Thời gian giao của khách DEPO bị tính nhanh hơn thực tế → sửa cách tính `f2`

**Vấn đề.** DEPO không giữ hàng, nên khách của DEPO phải chờ cả chặng **vào** DEPO. Mô hình cũ luôn cộng chặng vào **nhanh nhất có thể**, kể cả khi kho gần nhất đang đóng, hoặc khi hàng thật ra đi từ một kho xa hơn.

**Đã sửa.** Chặng vào DEPO giờ được tính theo **đúng kho đang cấp hàng** cho DEPO đó. Nếu DEPO lấy hàng từ kho xa, thời gian giao của khách tăng theo, và mô hình "thấy" được cái giá này khi chọn kho.

### 3. Hệ số CO2 chặng vào DEPO → giữ nguyên, nhưng ghi rõ giả định

**Câu hỏi đặt ra.** Hàng vào DEPO rất ít (82% số tuyến chở dưới 1 tấn mỗi ngày, không tuyến nào đầy một xe 4 tấn). Vậy có hợp lý khi tính CO2 theo xe tải chở đầy (360.83 g/tấn-km) không?

**Quyết định.** Giả định hàng vào DEPO được **gửi ghép (LTL)**: gửi chung xe với hàng của nhiều chủ hàng khác, nên xe vẫn chạy đầy. Vì vậy vẫn dùng hệ số 360.83. Hệ số của xe van (756) sẽ dùng làm **kịch bản kiểm tra độ nhạy**. Mô hình không đổi ở điểm này, chỉ ghi rõ giả định.

### 4. Nhiều lần giải chưa chắc là tốt nhất → đổi thiết lập giải

**Vấn đề.** Bản cũ cho mỗi lần giải tối đa 5 phút. Kết quả: **27/39 phương án** dừng giữa chừng (`maxTimeLimit`), trong đó có cả các phương án TOPSIS chọn, và không biết chúng cách tốt nhất bao xa.

**Đã sửa.** Mỗi lần giải tối đa **30 phút** (bảng payoff: 60 phút). Máy dừng khi chứng minh được phương án cách tốt nhất **dưới 0.5%**. Sai số còn lại (**gap**) của từng lần giải được ghi lại.

**Kết quả.** **Không còn lần giải nào phải dừng giữa chừng.** 72 lần giải đều đạt `optimal` (trong sai số 0.5%), gap lớn nhất 0.50%, trung vị 0.39%. Toàn bộ AUGMECON2 chạy hết 133 phút.

### Những gì **không** đổi

- Phạm vi, dữ liệu, cầu, chi phí, sức chứa, các loại kho: giữ nguyên.
- Bán kính tuyến vào DEPO: giữ 200 km (NDC: 150 km).
- Không thêm phát thải cố định cho mỗi kho mở (hệ số GLEC theo tấn đã gồm điện nền của kho).
- Không thêm kho mới.
- Phương pháp: payoff → AUGMECON2 (lưới 10 × 10) → lọc Pareto → TOPSIS (4 kịch bản trọng số), giữ nguyên.

### Kết quả thay đổi thế nào

**Bảng payoff (3 phương án "cực đoan"):**

| Phương án | Bản 11/10 | Bản 12/10 |
|---|---|---|
| **Rẻ nhất** | 300.20 tỷ · 4.81 giờ · 2,516 tấn · 37 kho | 301.98 tỷ · 5.02 giờ · 2,749 tấn · 36 kho |
| **Giao nhanh nhất** | 337.11 tỷ · 2.97 giờ · 2,251 tấn · 49 kho | 342.33 tỷ · 2.97 giờ · 2,645 tấn · 49 kho |
| **Ít CO2 nhất** | 361.73 tỷ · 3.48 giờ · **1,875 tấn** · 52 kho | 329.44 tỷ · 3.66 giờ · **2,465 tấn** · 50 kho |
| Trạng thái giải | 2 bước dừng giữa chừng | cả 9 bước `optimal` |

Thay đổi lớn nhất nằm ở **phương án ít CO2 nhất**. Bản cũ đạt 1,875 tấn nhờ các tuyến biển vòng vèo. Khi chặn các tuyến này, CO2 thấp nhất có thể là 2,465 tấn (cao hơn khoảng 590 tấn), nhưng phương án này lại **rẻ hơn 32 tỷ/năm**. Tức là bức tranh "xanh thì rất đắt" của bản cũ phần lớn do các tuyến vô lý tạo ra.

**Tập Pareto:**

| | Bản 11/10 | Bản 12/10 |
|---|---|---|
| Số phương án | 39 | 39 |
| Chi phí | 300.20 → 362.83 tỷ | 301.98 → 343.06 tỷ |
| Thời gian giao TB | 2.97 → 4.81 giờ | 2.97 → 5.02 giờ |
| CO2 | 1,875 → 2,516 tấn | 2,465 → 2,749 tấn |
| Số kho mở | 37 → 52 | 36 → 52 |

**Phương án hạng 1 theo TOPSIS:**

| Kịch bản | Bản 11/10 | Bản 12/10 |
|---|---|---|
| Cost-driven | P22 · 317.25 tỷ · 3.34 giờ · 2,067 tấn · 49 kho | **P32** · 323.54 tỷ · 3.18 giờ · 2,605 tấn · 47 kho |
| Service-driven | P31 · 329.96 tỷ · 3.16 giờ · 2,003 tấn · 51 kho | **P38** · 342.17 tỷ · 2.97 giờ · 2,644 tấn · 49 kho |
| Green-driven | P35 · 340.06 tỷ · 3.16 giờ · 1,939 tấn · 51 kho | **P35** · 326.10 tỷ · 3.18 giờ · 2,550 tấn · 50 kho |
| Balanced | P31 · 329.96 tỷ · 3.16 giờ · 2,003 tấn · 51 kho | **P35** · 326.10 tỷ · 3.18 giờ · 2,550 tấn · 50 kho |

*Lưu ý: mã P01, P02… được đánh lại theo chi phí tăng dần ở mỗi bản. P35 của bản 12/10 **không phải** cùng một mạng lưới với P35 của bản 11/10.*

---

## Bài toán

Chọn mở / đóng kho trong mạng lưới phân phối B2B ở Indonesia và chọn tuyến chở hàng, cân bằng 3 mục tiêu (đều càng nhỏ càng tốt):

| Mục tiêu | Ý nghĩa | Đơn vị |
|---|---|---|
| `f1` | Tổng chi phí vận hành một năm: tiền thuê kho + phí chở kho → kho + phí chở kho → khách + phí bốc xếp | tỷ IDR / năm |
| `f2` | Thời gian giao trung bình mỗi pallet (trung bình có trọng số theo số pallet; khách của DEPO tính cả chặng vào DEPO) | ngày / pallet (`f2_gio` = giờ / pallet) |
| `f3` | Phát thải CO2 một năm (vận chuyển + kho, theo GLEC Framework) | tấn CO2e / năm |

Mạng có 53 kho: 1 NDC + 9 RDC luôn mở; 43 kho còn lại (7 DC Direct, 18 DC Satellite, 18 DEPO) do mô hình chọn. Hàng đi theo phân tầng NDC → RDC → DC Satellite → DEPO → khách, hoặc NDC → DC Direct → DEPO → khách. Cầu: 3,346 nhóm khách B2B, 72,624 pallet / năm.

Chuỗi phương pháp: mô hình MILP 3 mục tiêu → payoff table (lexicographic) → AUGMECON2 (lưới 10 × 10) → tập Pareto (39 phương án) → TOPSIS (4 kịch bản trọng số).

## Hướng dẫn đọc từng file

**Nên đọc theo thứ tự 1 → 11.** File `.md` mở bằng Notepad / VS Code (hoặc đưa thẳng cho AI). File `.csv` mở bằng Excel. File `.png` là ảnh. File `.html` mở bằng Chrome hoặc Edge (cần có mạng).

### Phần 1 – Hiểu mô hình

**1. `README.md`** (file này): những gì đã thay đổi, hướng dẫn đọc, giải thích các cột, các con số chính.

**2. `Mo_hinh_dau_vao.md`** – *Mô hình được xây như thế nào*. Toàn bộ giả định, tập hợp, tham số, biến, 3 công thức mục tiêu, ràng buộc và 4 bước giải. Các chỗ khác bản cũ được đánh dấu **[MỚI]** / **[ĐỔI]**.

**3. `network_structure.png`** – *Sơ đồ mạng lưới*: hàng đi từ nhà máy → NDC → RDC / DC → DEPO → khách. Chỉ là sơ đồ, không có số liệu.

### Phần 2 – Kết quả chính

**4. `pareto.csv`** – *39 phương án mạng lưới tốt nhất (quan trọng nhất)*. Mỗi dòng là một phương án (P01 đến P39), xếp từ rẻ nhất đến đắt nhất. Không có phương án nào "tốt nhất mọi mặt": muốn rẻ hơn thì giao chậm hơn hoặc thải nhiều CO2 hơn, và ngược lại. Đó là ý nghĩa của "tập Pareto".

**5. `pareto_front.png`** – *Hình đánh đổi giữa 3 mục tiêu*: 3 khung, mỗi chấm là một phương án.

**6. `pareto_3d.html`** – *Hình 3D của 39 phương án*. Kéo chuột để xoay, rê chuột vào chấm để xem số.

**7. `topsis_ranking.csv`** – *Xếp hạng phương án theo 4 quan điểm*. Lọc cột `Hang = 1` để xem mỗi quan điểm chọn phương án nào.

**8. `topsis_choices.png`** – *Hình: mỗi quan điểm chọn phương án nào*. Chấm xám là 39 phương án; chấm màu là phương án hạng 1 của từng quan điểm.

### Phần 3 – Chi tiết (khi cần tra cứu)

**9. `network_map.html`** – *Bản đồ mạng lưới tương tác*. Chọn phương án ở góc trái trên, hoặc bấm phím ← → để chuyển nhanh; rê chuột lên đường / kho / khách để xem số pallet. File có tọa độ thật của kho và khách (phía công ty chỉ yêu cầu ẩn tên). File nặng (khoảng 2.5 MB).

**10. `pareto_flows.csv`** – *Luồng hàng chi tiết của từng phương án*: từ kho nào (`Tu`), đến kho / nhóm khách nào (`Den`), bao nhiêu pallet mỗi năm (`Pallet`). File lớn (khoảng 10.7 MB).

**11. `payoff.csv` và `augmecon_runs.csv`** – *Nhật ký tính toán*. `payoff.csv`: 3 phương án "cực đoan". `augmecon_runs.csv`: nhật ký 78 lần máy giải bài toán để tìm ra 39 phương án (72 lần có nghiệm, 6 lần vô nghiệm).

## Giải thích cột

**`pareto.csv`**
- `PhuongAn`: mã phương án (P01 = rẻ nhất).
- `f1`, `f2`, `f3`: 3 mục tiêu (đơn vị ở bảng trên); `f2_gio` = `f2` × 24.
- `SoKhoMo`: số kho mở (gồm 10 kho luôn mở). `DC Direct`, `DC Satellite`, `DEPO`: số kho mở theo loại.
- `KhoMo`: danh sách mã kho mở, cách nhau bằng dấu phẩy.
- `TrangThai`: trạng thái solver. `optimal` = đã chứng minh phương án cách tốt nhất không quá 0.5%.
- **`Gap_%` [MỚI]**: sai số còn lại, tính bằng %. Ví dụ 0.30 nghĩa là chi phí của phương án này cao hơn mức tốt nhất có thể **tối đa 0.30%**.
- `Nguon`: phương án đến từ AUGMECON2 hay từ payoff table.

**`payoff.csv`**: `UuTien` = mục tiêu được ưu tiên; `Gap_%` = sai số lớn nhất trong 3 bước giải; `Giay` = tổng thời gian giải (giây).

**`pareto_flows.csv`**: `PhuongAn`; `Chang` = `kho->kho` hoặc `kho->khach`; `Tu`, `Den` = mã nút đi / đến; `Pallet` = pallet / năm.

**`topsis_ranking.csv`**: `KichBan` = kịch bản trọng số; `DiemTOPSIS` = điểm từ 0 đến 1 (càng gần 1 càng tốt); `Hang` = hạng (1 = tốt nhất); các cột còn lại như `pareto.csv`.

**`augmecon_runs.csv`**: `i3`, `i2` = vị trí trên lưới (mức trần CO2, mức trần thời gian giao); `e2`, `e3` = giá trị trần; `s2`, `s3` = phần trần còn dư; `Bypass` = số mức lưới được bỏ qua; `Giay` = thời gian giải (giây); `G2`, `G3`, `max2`, `max3` = thông số lưới; **`TL`, `GAP` [MỚI]** = giới hạn thời gian (giây) và sai số cho phép của lần chạy; **`Gap_%` [MỚI]** = sai số còn lại của từng lần giải.

## Kịch bản trọng số TOPSIS (chi phí, thời gian giao, CO2)

| Kịch bản | Trọng số |
|---|---|
| Cost-driven | 0.50, 0.25, 0.25 |
| Service-driven | 0.25, 0.50, 0.25 |
| Green-driven | 0.25, 0.25, 0.50 |
| Balanced | 1/3, 1/3, 1/3 |

## Một số con số chính

- Tập Pareto: chi phí 301.98 → 343.06 tỷ IDR / năm; thời gian giao 2.97 → 5.02 giờ / pallet; CO2 2,465 → 2,749 tấn / năm; 36 → 52 kho mở.
- Đánh đổi chi phí – thời gian giao: giảm thời gian giao từ khoảng 4.6 xuống 4.0 giờ chỉ tốn thêm khoảng 2 tỷ / năm, nhưng giảm tiếp từ 3.2 xuống 3.0 giờ tốn thêm khoảng 19 tỷ / năm.
- Phương án giao nhanh nhất **không phải** phương án ít CO2 nhất: ba mục tiêu thật sự xung đột.
- Phương án hạng 1 theo TOPSIS:

| Kịch bản | Phương án | Chi phí (tỷ IDR/năm) | Giao TB (giờ) | CO2 (tấn/năm) | Kho mở | Gap |
|---|---|---|---|---|---|---|
| Cost-driven | P32 | 323.54 | 3.18 | 2,605 | 47 | 0.50% |
| Service-driven | P38 | 342.17 | 2.97 | 2,644 | 49 | 0.00% |
| Green-driven | P35 | 326.10 | 3.18 | 2,550 | 50 | 0.28% |
| Balanced | P35 | 326.10 | 3.18 | 2,550 | 50 | 0.28% |

## Giả định và hạn chế cần biết

- Một kỳ = một năm, dữ liệu năm 2025; một sản phẩm gộp, đo bằng pallet; cầu cố định, giao đủ 100%.
- Chỉ xét kho đang có, không xây kho mới. Ở phía "xanh" nhất của tập Pareto, mạng lưới đã dùng gần hết các kho hiện có.
- Chặng cuối chỉ giao trong cùng đảo (trừ Papua, không có kho). DC Satellite chỉ nhận hàng từ RDC cùng đảo (hoặc RDC gần nhất).
- Phí chở trên các tuyến không có giá thật là **phí ước lượng** theo khoảng cách. Thời gian giao phần lớn cũng là ước lượng (khoảng cách ÷ tốc độ xe), chỉ là thời gian vận chuyển, chưa tính thời gian xử lý đơn hàng.
- CO2 theo hệ số chuẩn của GLEC: giả định xe chở đầy 85%; hàng vào DEPO giả định đi gửi ghép (LTL). Hệ số kho dựa trên lưới điện Anh, chưa đổi sang lưới điện Indonesia. Không tính chuyến giao nhiều điểm (multi-drop).
- Mỗi phương án được giải trong sai số 0.5% (khoảng 1.5 tỷ IDR / năm), không phải tốt nhất tuyệt đối.
- **Điểm đang xem xét:** kịch bản Cost-driven (ưu tiên chi phí) lại chọn P32, một phương án chi phí ở mức khá cao (323.54 tỷ), chứ không phải một phương án rẻ. Một lý do có thể là cách TOPSIS so sánh theo tỷ lệ: giữa các phương án, chi phí chỉ chênh tối đa khoảng 14% (302 → 343 tỷ), còn thời gian giao chênh tới khoảng 69% (2.97 → 5.02 giờ). Tiêu chí chênh lệch nhiều có sức nặng lớn hơn, kể cả khi trọng số nhỏ hơn. Ngoài ra, điểm TOPSIS của 3 phương án đầu bảng Cost-driven rất sát nhau (0.762, 0.761, 0.761). Điểm này sẽ được kiểm tra thêm.
