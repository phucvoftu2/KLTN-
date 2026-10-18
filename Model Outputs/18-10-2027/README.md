# Kết quả mô hình — bản chạy đêm 18/10

Thư mục này gom kết quả của **lần chạy đêm 18/10** (notebook `Multi-Objective Optimization v2.ipynb`). Bản này **thay cho** bản 12/10/2026 (thư mục `12-10-2026`, vẫn giữ nguyên để so sánh). Dữ liệu đã ẩn danh: kho chỉ ghi bằng mã (ví dụ `D20`, `MWH_D39`, `DEPO01`, `NDC`).

> **Trạng thái:** payoff table đã xong. **AUGMECON2, tập Pareto và TOPSIS đang chạy / chưa chạy.** Các mục đánh dấu *(chờ kết quả)* sẽ được điền sau khi có số thật.

---

## Khác gì so với bản 12/10/2026

### 1. Sức chứa kho dùng DOS thực tế 2025 theo nhóm sản phẩm
**Trước:** mỗi kho một con số DOS (số ngày hàng nằm kho), lấy từ **mục tiêu năm 2030** của công ty (đã cộng 40% dự phòng). Con số này giống nhau cho mọi sản phẩm.
**Giờ:** dùng **DOS thực tế năm 2025** cho từng kho × **124 nhóm sản phẩm**. Mỗi nhóm khách có một **giỏ hàng** (tỷ lệ các nhóm sản phẩm khách đó mua). Pallet giao cho khách nào nằm kho bao lâu tính theo đúng giỏ hàng của khách đó.
**Tác động:** DOS 2025 cao hơn DOS 2030 khoảng 1.3–4 lần, nên kho chứa được ít hàng hơn mỗi năm. **Sức chứa giờ có tác dụng thật**: trong phương án rẻ nhất, kho D20 đầy 100%.

### 2. NDC không giao thẳng cho khách B2B
NDC chỉ cấp hàng cho RDC, DC Direct và DEPO. Trong dữ liệu chỉ có 6 tuyến NDC → khách bị bỏ.

### 3. CO2 tuyến xuyên đảo tính theo 3 đoạn: bộ – biển – bộ
Mỗi tuyến đi tàu được tách: **kho → cảng (đường bộ) → cảng (đường biển) → khách (đường bộ)**, lấy từ bảng lead time của công ty. 456 tuyến Java → Papua chưa có trong bảng được **ghép từ các mảnh có sẵn** (cảng và km của từng đầu). Chặng tới khách đi qua cảng: đoạn ra cảng tính bằng xe tải 4 tấn, đoạn giao khách bằng xe van.

### Những gì không đổi
Phạm vi, cầu (72,624 pallet/năm), chi phí, các loại kho, luật phân tầng, `f1`, `f2`, phương pháp (payoff → AUGMECON2 lưới 10 × 10 → lọc Pareto → TOPSIS 4 kịch bản).

Chi tiết từng giả định, tham số, công thức: xem `Mo_hinh_dau_vao.md` (chỗ đổi được đánh dấu **[MỚI]** / **[ĐỔI]**).

---

## Kết quả

### Payoff table (3 phương án "cực đoan") — đã xong

Cả 9 bước giải đều `optimal` (gap tối đa 0.48%).

| Phương án | Chi phí (tỷ IDR/năm) | Giao TB | CO2 (tấn/năm) | Số kho mở |
|---|---|---|---|---|
| **Rẻ nhất** (ưu tiên chi phí) | **306.06** | 0.209 ngày (5.0 giờ) | 2,781 | 35 |
| **Giao nhanh nhất** (ưu tiên thời gian giao) | 341.54 | **0.128 ngày (3.1 giờ)** | 2,645 | 51 |
| **Ít CO2 nhất** (ưu tiên môi trường) | 355.96 | 0.160 ngày (3.8 giờ) | **2,496** | 50 |

So với bản 12/10:

| Phương án | Bản 12/10 | Bản 18/10 |
|---|---|---|
| Rẻ nhất | 301.98 tỷ · 5.0 giờ · 2,749 tấn · 36 kho | 306.06 tỷ · 5.0 giờ · 2,781 tấn · 35 kho |
| Giao nhanh nhất | 342.33 tỷ · 3.0 giờ · 2,645 tấn · 49 kho | 341.54 tỷ · 3.1 giờ · 2,645 tấn · 51 kho |
| Ít CO2 nhất | 329.44 tỷ · 3.7 giờ · 2,465 tấn · 50 kho | 355.96 tỷ · 3.8 giờ · 2,496 tấn · 50 kho |

Điểm khác lớn nhất: **phương án ít CO2 nhất đắt hơn 26.5 tỷ/năm** so với bản cũ, và giờ là phương án đắt nhất trong ba. Đánh đổi giữa chi phí và CO2 mạnh hơn bản cũ.

### Tập Pareto *(chờ kết quả AUGMECON2)*

### Xếp hạng TOPSIS *(chờ kết quả)*

---

## Các file trong thư mục (sau khi chạy xong)

| File | Nội dung |
|---|---|
| `README.md` | File này |
| `Mo_hinh_dau_vao.md` | Mô hình: giả định, tập, tham số, biến, công thức, cách giải |
| `payoff.csv` | 3 phương án "cực đoan" |
| `augmecon_runs.csv` | Nhật ký từng lần giải AUGMECON2 |
| `pareto.csv` | Tập phương án Pareto (P01, P02, …), xếp theo chi phí tăng dần |
| `pareto_flows.csv` | Luồng hàng của từng phương án: từ kho nào tới đâu, bao nhiêu pallet/năm |
| `pareto_front.png`, `pareto_3d.html` | Hình đánh đổi giữa 3 mục tiêu (2D và 3D) |
| `network_map.html` | Bản đồ mạng lưới tương tác của từng phương án |
| `network_structure.png` | Sơ đồ các tầng kho |
| `*.parquet`, `figures/` | Bản gốc cho máy đọc (notebook TOPSIS dùng) |

Cột trong các file CSV giống bản 12/10 (xem `README.md` của thư mục `12-10-2026`).

## Giả định và hạn chế cần biết
- Luồng hàng vẫn là **một sản phẩm gộp**; 124 nhóm sản phẩm chỉ đi vào sức chứa và CO2 qua giỏ hàng. Mô hình không tự chọn "kho nào giữ nhóm sản phẩm nào".
- DOS 2025: ô thiếu được lấp bằng trung vị cùng loại kho; DOS của RDC có thể chưa được công ty tính lại đầy đủ.
- CO2: đoạn phà RoRo tính như đường bộ; chưa tính phát thải bốc xếp tại cảng.
- Phí chở trên tuyến không có giá thật là ước lượng theo khoảng cách. Thời gian giao là thời gian vận chuyển, chưa gồm thời gian xử lý đơn.
- Mỗi lần giải dừng ở sai số 0.5%.
