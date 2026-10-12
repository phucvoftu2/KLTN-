# Kết quả mô hình — Khóa luận "Trade-off Analysis for Personal Care Distribution Networks: An Indonesian Case Study"

Thư mục này gom các kết quả chính của mô hình (bản chụp ngày 11/10/2026). Dữ liệu từ một công ty hàng chăm sóc cá nhân ở Indonesia, đã ẩn tên: kho chỉ ghi bằng mã (vd. `MWH_D17`, `DEPO03`, `NDC`), không có tên công ty hay tên kho.

## Bài toán

Chọn mở / đóng kho trong mạng lưới phân phối B2B ở Indonesia và chọn tuyến chở hàng, cân bằng 3 mục tiêu (đều càng nhỏ càng tốt):

| Mục tiêu | Ý nghĩa | Đơn vị |
|---|---|---|
| `f1` | Tổng chi phí vận hành một năm: tiền thuê kho + phí chở kho → kho + phí chở kho → khách + phí bốc xếp | tỷ IDR / năm |
| `f2` | Thời gian giao trung bình mỗi pallet (trung bình có trọng số theo số pallet trên mỗi tuyến) | ngày / pallet (`f2_gio` = giờ / pallet) |
| `f3` | Phát thải CO2 một năm (vận chuyển + kho, theo GLEC Framework) | tấn CO2e / năm |

Mạng có 53 kho: 1 NDC + 9 RDC luôn mở; 43 kho còn lại (7 DC Direct, 18 DC Satellite, 18 DEPO) do mô hình chọn. Hàng đi theo phân tầng NDC → RDC → DC Satellite → DEPO → khách, hoặc NDC → DC Direct → DEPO → khách. Cầu: 3,346 nhóm khách B2B, 72,624 pallet / năm.

Chuỗi phương pháp: mô hình MILP 3 mục tiêu → payoff table (lexicographic) → AUGMECON2 (lưới 10 × 10) → tập Pareto (39 phương án) → TOPSIS (4 kịch bản trọng số).

## Hướng dẫn đọc từng file

**Nên đọc theo thứ tự 1 → 11.** File `.md` mở bằng Notepad / VS Code (hoặc đưa thẳng cho AI). File `.csv` mở bằng Excel. File `.png` là ảnh, mở bằng trình xem ảnh. File `.html` mở bằng Chrome hoặc Edge (cần có mạng).

### Phần 1 – Hiểu mô hình

**1. `README.md`** (file này)
Giới thiệu bài toán, hướng dẫn đọc các file, giải thích các cột và tóm tắt kết quả chính.

**2. `Mo_hinh_dau_vao.md`** – *Mô hình được xây như thế nào*
Toàn bộ đầu vào của mô hình: các giả định (ví dụ: tính theo 1 năm, giao đủ 100% cầu, chỉ dùng kho đang có), các tập hợp (bao nhiêu kho, bao nhiêu nhóm khách, bao nhiêu tuyến), các tham số (chi phí, sức chứa, thời gian giao, hệ số CO2 – kèm đơn vị và nguồn), các biến, công thức của 3 mục tiêu, các ràng buộc và 4 bước giải. Đọc file này để hiểu các con số trong kết quả từ đâu ra.

**3. `network_structure.png`** – *Sơ đồ mạng lưới*
Hình minh họa: hàng đi từ nhà máy → NDC → RDC / DC → DEPO → khách. Chỉ là sơ đồ, không có số liệu.

### Phần 2 – Kết quả chính

**4. `pareto.csv`** – *39 phương án mạng lưới tốt nhất (quan trọng nhất)*
Mỗi dòng là một phương án mạng lưới (P01 đến P39), xếp từ rẻ nhất đến đắt nhất. Mỗi phương án cho biết: chi phí (`f1`), thời gian giao trung bình (`f2_gio`, tính bằng giờ), CO2 (`f3`), số kho mở và danh sách kho mở. Không có phương án nào "tốt nhất mọi mặt": muốn rẻ hơn thì giao chậm hơn hoặc thải nhiều CO2 hơn, và ngược lại. Đó là ý nghĩa của "tập Pareto".

**5. `pareto_front.png`** – *Hình đánh đổi giữa 3 mục tiêu*
3 khung hình, mỗi chấm là một phương án: (a) chi phí – thời gian giao, (b) chi phí – CO2, (c) thời gian giao – CO2. Nhìn để thấy: tốn thêm bao nhiêu tiền thì giao nhanh hơn / ít CO2 hơn bao nhiêu.

**6. `pareto_3d.html`** – *Hình 3D của 39 phương án*
Cùng nội dung như file 5 nhưng 3 chiều cùng lúc. Kéo chuột để xoay, rê chuột vào chấm để xem số.

**7. `topsis_ranking.csv`** – *Xếp hạng phương án theo 4 quan điểm*
Mỗi phương án được chấm điểm (`DiemTOPSIS`, từ 0 đến 1, càng cao càng tốt) và xếp hạng (`Hang`, 1 = tốt nhất) theo 4 quan điểm: ưu tiên chi phí (Cost-driven), ưu tiên tốc độ giao (Service-driven), ưu tiên môi trường (Green-driven), cân bằng (Balanced). Lọc cột `Hang = 1` để xem mỗi quan điểm chọn phương án nào.

**8. `topsis_choices.png`** – *Hình: mỗi quan điểm chọn phương án nào*
Các chấm xám là 39 phương án; chấm có màu là phương án đứng hạng 1 của từng quan điểm.

### Phần 3 – Chi tiết (khi cần tra cứu)

**9. `network_map.html`** – *Bản đồ mạng lưới tương tác*
Bản đồ Indonesia vẽ mạng của từng phương án: biểu tượng nhà kho (màu theo loại kho; kho đóng là nhà kho viền xám), đường kho → kho và kho → khách (đường càng dày = càng nhiều hàng). Chọn phương án ở ô góc trái trên, hoặc bấm phím ← → để chuyển nhanh; rê chuột lên đường / kho / khách để xem số pallet. File có tọa độ thật của kho và khách (phía công ty chỉ yêu cầu ẩn tên, không cần ẩn tọa độ). File nặng (khoảng 2.4 MB) nên mở bằng trình duyệt sẽ tiện hơn đưa cho AI.

**10. `pareto_flows.csv`** – *Luồng hàng chi tiết của từng phương án*
Mỗi dòng là một tuyến có hàng đi: phương án nào, từ kho nào (`Tu`), đến kho / nhóm khách nào (`Den`), bao nhiêu pallet mỗi năm (`Pallet`). File lớn (khoảng 132 nghìn dòng); dùng khi cần biết một kho cụ thể giao cho ai. Đây là dữ liệu của bản đồ ở file 9, dạng bảng.

**11. `payoff.csv` và `augmecon_runs.csv`** – *Nhật ký tính toán*
`payoff.csv`: 3 phương án "cực đoan" (rẻ nhất / giao nhanh nhất / ít CO2 nhất), dùng để biết giới hạn của từng mục tiêu. `augmecon_runs.csv`: nhật ký 67 lần máy tính giải bài toán để tìm ra 39 phương án. Hai file này chủ yếu để kiểm tra cách tính, không cần đọc nếu chỉ quan tâm kết quả.

## Giải thích cột

**`pareto.csv`**
- `PhuongAn`: mã phương án (P01 = rẻ nhất).
- `f1`, `f2`, `f3`: 3 mục tiêu (đơn vị ở bảng trên); `f2_gio` = `f2` × 24.
- `SoKhoMo`: số kho mở (gồm 10 kho luôn mở). `DC Direct`, `DC Satellite`, `DEPO`: số kho mở theo loại.
- `KhoMo`: danh sách mã kho mở, cách nhau bằng dấu phẩy.
- `TrangThai`: trạng thái solver (`optimal` = tối ưu trong sai số 0.1%; `maxTimeLimit` = dừng ở giới hạn 5 phút, nghiệm tốt nhưng chưa chứng minh tối ưu).
- `Nguon`: phương án đến từ AUGMECON2 hay từ payoff table.

**`pareto_flows.csv`**: `PhuongAn`; `Chang` = `kho->kho` hoặc `kho->khach`; `Tu`, `Den` = mã nút đi / đến; `Pallet` = pallet / năm.

**`topsis_ranking.csv`**: `KichBan` = kịch bản trọng số; `DiemTOPSIS` = điểm từ 0 đến 1 (càng gần 1 càng tốt); `Hang` = hạng (1 = tốt nhất); các cột còn lại như `pareto.csv`.

**`augmecon_runs.csv`**: `i3`, `i2` = vị trí trên lưới (mức trần CO2, mức trần thời gian giao); `e2`, `e3` = giá trị trần; `s2`, `s3` = phần trần còn dư; `Bypass` = số mức lưới được bỏ qua; `Giay` = thời gian giải (giây); `G2`, `G3`, `max2`, `max3` = thông số lưới.

## Kịch bản trọng số TOPSIS (chi phí, thời gian giao, CO2)

| Kịch bản | Trọng số |
|---|---|
| Cost-driven | 0.50, 0.25, 0.25 |
| Service-driven | 0.25, 0.50, 0.25 |
| Green-driven | 0.25, 0.25, 0.50 |
| Balanced | 1/3, 1/3, 1/3 |

## Một số con số chính

- Tập Pareto: chi phí 300.20 → 362.83 tỷ IDR / năm; thời gian giao 2.97 → 4.81 giờ / pallet; CO2 1,875 → 2,516 tấn / năm; 37 → 52 kho mở.
- Phương án hạng 1 theo TOPSIS:

| Kịch bản | Phương án | Chi phí (tỷ IDR/năm) | Giao TB (giờ) | CO2 (tấn/năm) | Kho mở |
|---|---|---|---|---|---|
| Cost-driven | P22 | 317.25 | 3.34 | 2,067 | 49 |
| Service-driven | P31 | 329.96 | 3.16 | 2,003 | 51 |
| Green-driven | P35 | 340.06 | 3.16 | 1,939 | 51 |
| Balanced | P31 | 329.96 | 3.16 | 2,003 | 51 |

## Giả định và hạn chế cần biết

- Một kỳ = một năm, dữ liệu năm 2025; một sản phẩm gộp, đo bằng pallet; cầu cố định, giao đủ 100%.
- Chỉ xét kho đang có, không xây kho mới. Chặng cuối chỉ giao trong cùng đảo (trừ Papua, không có kho).
- CO2 kho tính theo tấn hàng xuất, không có phát thải cố định cho mỗi kho mở, nên mô hình không "phạt" CO2 khi mở thêm kho. Phương án ít CO2 nhất vì thế mở gần hết kho (đang kiểm tra lại).
- Nhiều lần giải AUGMECON2 dừng ở giới hạn 5 phút: phương án rất tốt nhưng chưa chắc tối ưu tuyệt đối.
