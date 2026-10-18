# Mô hình: giả định, tham số, biến và công thức (đầu vào) — bản 18/10

Tài liệu này mô tả đầu vào của mô hình tối ưu mạng lưới phân phối trong khóa luận, **bản dùng cho lần chạy đêm 18/10** (notebook `Multi-Objective Optimization v2.ipynb`). Kết quả nằm ở `README.md` và các file `.csv` cùng thư mục. Dữ liệu đã ẩn danh: kho chỉ ghi bằng mã, không có tên công ty hay tên kho.

Những chỗ **khác bản 12/10/2026** được đánh dấu **[MỚI]** hoặc **[ĐỔI]**. Tóm tắt các thay đổi nằm ở `README.md`, mục "Khác gì so với bản 12/10/2026".

---

## 1. Giả định

| # | Giả định |
|---|---|
| 1 | **Một kỳ = một năm**, dữ liệu năm 2025. Cầu, chi phí, sức chứa đều tính theo năm. Không dự báo tương lai |
| 2 | **[ĐỔI] Luồng hàng là một sản phẩm gộp**, đo bằng **pallet** (mỗi sản phẩm đổi từ số cái sang pallet trước khi cộng). **Khác biệt giữa 124 nhóm sản phẩm** của công ty đi vào mô hình qua **giỏ hàng** của từng nhóm khách: sức chứa dùng số ngày nằm kho (DOS) của từng nhóm sản phẩm, CO2 dùng tấn/pallet theo cơ cấu hàng của khách. Giả định: pallet giao cho khách nào mang đúng cơ cấu hàng khách đó mua |
| 3 | Chỉ kênh **B2B**, chỉ **Indonesia** |
| 4 | **Cầu cố định**: mỗi nhóm khách một con số pallet/năm. Phải giao đủ 100% cầu, không cho thiếu hàng. Không xét độ nhạy cầu |
| 5 | Nhà máy nằm cạnh NDC: chặng nhà máy → NDC **phí 0, không giới hạn** lượng hàng |
| 6 | Chỉ xét **kho đang có**, không xây kho mới. 53 kho trong phạm vi |
| 7 | **NDC và 9 RDC luôn mở**. 43 kho còn lại (7 DC Direct, 18 DC Satellite, 18 DEPO) do mô hình chọn mở / đóng |
| 8 | **Luồng hàng theo phân tầng**: NDC → RDC, NDC → DC Direct, NDC → DEPO (≤ 150 km), RDC → DC Satellite, RDC → DEPO (≤ 200 km), DC Direct → DEPO (≤ 200 km), DC Satellite → DEPO (≤ 200 km). Không có luồng ngang hay ngược. Tuyến thật đang chạy dài hơn 200 km vẫn được giữ (ví dụ D31 → DEPO01, 290 km) |
| 9 | RDC → DC Satellite chỉ trong cùng đảo. DC Satellite ở đảo không có RDC (Bali – Nusra, Maluku) nhận hàng từ **RDC gần nhất** |
| 10 | **Chặng cuối (kho → khách) chỉ trong cùng đảo**. Ngoại lệ: nhóm khách ở đảo không có kho nào (Papua) được nhận hàng từ đảo khác |
| 11 | **[MỚI] NDC không giao thẳng cho khách B2B.** NDC chỉ cấp hàng cho RDC, DC Direct và DEPO trong 150 km. (Bản 12/10: NDC được giao thẳng cho khách trong 150 km; trong dữ liệu chỉ có 6 tuyến như vậy) |
| 12 | Một nhóm khách **có thể nhận hàng từ nhiều kho** |
| 13 | **DEPO** là kho trung chuyển (cross-dock): không giữ tồn kho, không giới hạn sức chứa. Khách của DEPO phải chờ cả chặng **vào** DEPO lẫn chặng DEPO → khách |
| 14 | Hàng vào DEPO đi gửi ghép (LTL), nên chặng RDC/DC → DEPO dùng hệ số CO2 xe tải chặng giữa (360.83) |
| 15 | Mọi chi phí ở **mặt bằng giá 2025**. Chi phí là chi phí vận hành (OPEX), không có chi phí đầu tư (CAPEX) |
| 16 | **[ĐỔI] Sức chứa tính theo tồn kho**: tồn kho trung bình = lượng xuất × DOS ÷ 360, không vượt số chỗ chứa. **DOS là số liệu thực tế năm 2025** theo kho × nhóm sản phẩm (bản 12/10 dùng DOS mục tiêu năm 2030, một số cho mỗi kho, thấp hơn thực tế khoảng 1.3–4 lần). Ô thiếu (kho không giữ nhóm đó năm 2025) được lấp bằng trung vị của nhóm đó ở các kho cùng loại |
| 17 | **[ĐỔI] Mỗi tuyến xuyên đảo = đoạn bộ ra cảng + đoạn biển + đoạn bộ từ cảng** (xem 5.3). Đoạn phà RoRo (Java – Sumatra, Java – Bali) tính như đường bộ. Chưa tính phát thải bốc xếp tại cảng |

---

## 2. Tập hợp và chỉ số

| Tập | Chỉ số | Gồm những gì | Số phần tử |
|---|---|---|---|
| $J$ | $i, j, l$ | Tất cả kho (NDC, RDC, DC Direct, DC Satellite, DEPO) | 53 |
| $J^{fix}$ | | Kho luôn mở: NDC + 9 RDC | 10 |
| $J^{dec} = J \setminus J^{fix}$ | $j$ | Kho mô hình chọn mở / đóng | 43 |
| $J^{giu}$ | | **[MỚI]** Kho có giữ hàng (mọi kho trừ DEPO) | 35 |
| $K$ | $k$ | Nhóm khách B2B (mỗi nhóm = các điểm giao trong cùng một quận / huyện) | 3,346 |
| $G$ | $g$ | **[MỚI]** Nhóm sản phẩm của công ty. Chỉ dùng để tính tham số giỏ hàng, **không có biến riêng** | 124 |
| $A^{tr} \subset J \times J$ | $(i, j)$ | Tuyến kho → kho được phép (giả định 8, 9) | 96 |
| $A^{lm} \subset J \times K$ | $(j, k)$ | Tuyến kho → khách được phép (giả định 10, 11). **[ĐỔI]** Trước: 52,981 | **52,975** |

---

## 3. Tham số

| Ký hiệu | Ý nghĩa | Đơn vị | Nguồn / cách tính |
|---|---|---|---|
| $d_k$ | Cầu của nhóm khách $k$. Tổng $D$ = 72,624 pallet/năm | pallet/năm | Cầu B2B năm 2025 của công ty, đổi số cái → pallet theo từng sản phẩm, rồi cộng |
| $F_j$ | Tiền thuê kho $j$ cả năm | IDR/năm | Bảng thông tin kho của công ty |
| $h_j$ | Phí bốc xếp 1 pallet xuất khỏi kho $j$ | IDR/pallet | Bảng thông tin kho của công ty |
| $c^{tr}_{ij},\ c^{lm}_{jk}$ | Phí chở 1 pallet trên tuyến | IDR/pallet | Bảng giá của công ty; tuyến không có giá ước lượng bằng hồi quy theo khoảng cách |
| $C_j$ | **[MỚI]** Số chỗ chứa của kho $j$ (pallet cùng lúc) | pallet | Bảng thông tin kho của công ty |
| $DOS_{jg}$ | **[MỚI]** Số ngày nhóm sản phẩm $g$ nằm trong kho $j$, **năm 2025** | ngày | Số liệu DOS lịch sử 2025 của công ty |
| $a_{kg}$ | **[MỚI]** Giỏ hàng: tỷ lệ pallet của nhóm $g$ trong tổng pallet khách $k$ mua | — | Từ cầu theo sản phẩm |
| $DOS_{jk}$ | **[MỚI]** Số ngày một pallet giao cho khách $k$ nằm trong kho $j$ $= \sum_g a_{kg}\,DOS_{jg}$ | ngày | Tính từ hai dòng trên |
| $DOS^{tr}_j$ | **[MỚI]** Như trên, cho hàng chuyển sang kho khác, theo cơ cấu cầu toàn quốc | ngày | Tính |
| $LT_{jk},\ LT^{tr}_{ij}$ | Số ngày giao trên tuyến kho → khách / kho → DEPO | ngày | Bảng lead time của công ty |
| $w$ | Tấn / pallet: 0.258 cho kho → kho; riêng từng nhóm khách (theo giỏ hàng) cho kho → khách | tấn/pallet | Từ cầu theo sản phẩm |
| $km^{bộ,1}, km^{biển}, km^{bộ,3}$ | **[MỚI]** Ba đoạn của mỗi tuyến (xem 5.3) | km | Bảng lead time của công ty |

---

## 4. Biến quyết định

| Biến | Miền | Ý nghĩa | Đơn vị |
|---|---|---|---|
| $Y_j$ | $\{0, 1\}$ với $j \in J^{dec}$; $Y_j = 1$ với $j \in J^{fix}$ | 1 = mở kho $j$, 0 = đóng | — |
| $T_{ij}$ | $\ge 0$ | Số pallet chở từ kho $i$ sang kho $j$ | pallet/năm |
| $X_{jk}$ | $\ge 0$ | Số pallet kho $j$ giao cho nhóm khách $k$ | pallet/năm |

Kích thước: 43 biến nhị phân, khoảng 53 nghìn biến liên tục (96 biến $T$ + 52,975 biến $X$). **Không có biến theo nhóm sản phẩm**: đã thử mô hình 124 nhóm sản phẩm có luồng riêng (khoảng 3.2 triệu biến), không giải được trên máy cá nhân.

---

## 5. Hàm mục tiêu (cả 3 đều min)

### 5.1 `f1` – Tổng chi phí (tỷ IDR/năm)

$$f_1 = \sum_{j} F_j\,Y_j + \sum_{(i,j) \in A^{tr}} c^{tr}_{ij}\,T_{ij} + \sum_{(j,k) \in A^{lm}} c^{lm}_{jk}\,X_{jk} + \sum_{j} h_j\,Out_j$$

### 5.2 `f2` – Thời gian giao trung bình (ngày/pallet)

$$f_2 = \frac{1}{D}\left[\sum_{(j,k) \in A^{lm}} LT_{jk}\,X_{jk} \;+ \sum_{(i,j) \in A^{tr},\ j \in J^{DEPO}} LT^{tr}_{ij}\,T_{ij}\right]$$

### 5.3 `f3` – CO2 (tấn CO2e/năm) **[ĐỔI]**

$$f_3 = \sum_{(i,j) \in A^{tr}} e^{tr}_{ij}\,T_{ij} + \sum_{(j,k) \in A^{lm}} e^{lm}_{jk}\,X_{jk}$$

CO2 của 1 pallet trên một tuyến = vận chuyển **3 đoạn** + kho xuất hàng:

$$e = w \times \frac{km^{bộ,1}\,EF^{bộ,1} + km^{biển} \times 22.35 + km^{bộ,3}\,EF^{bộ,3}}{10^6} + w \times \frac{EF_{kho}}{1000}$$

**Ba đoạn lấy từ đâu:**
- Tuyến đi tàu có trong bảng lead time: lấy thẳng km ra cảng, km biển, km từ cảng.
- Tuyến đường bộ (cùng đảo, hoặc xe lên phà Java – Sumatra / Java – Bali): toàn bộ quãng đường là đoạn bộ 1.
- 456 tuyến Java → Papua không có trong bảng: **ghép từ các mảnh có sẵn** (cảng quen của kho + km ra cảng, km biển giữa hai cảng, cảng gần khách + km tới khách). Kho không có tuyến qua cảng nào trong bảng: chọn cảng cùng đảo có tuyến biển tới cảng đích, km ra cảng = đường chim bay × hệ số đường vòng của đảo (Java 1.27, Sumatra 1.38, Sulawesi 1.41, Kalimantan 1.20).

| Chặng | Đoạn bộ 1 | Đoạn bộ 3 |
|---|---|---|
| NDC → kho | Xe tải 20 tấn (79) | Xe tải 20 tấn (79) |
| Kho → kho | Xe tải 4 tấn (360.83) | Xe tải 4 tấn (360.83) |
| Kho → khách, đi qua cảng | **Xe tải 4 tấn (360.83)** ra cảng | Xe van 3 tấn (756) giao khách |
| Kho → khách, đường bộ | Xe van 3 tấn (756) | — |
| Đoạn biển | Tàu container: 22.35 | |

Đơn vị hệ số: g CO2e / tấn-km. $EF_{kho}$ = 5.6 kg CO2e / tấn (kho thường), 1.3 (DEPO).

---

## 6. Ràng buộc

**(1) Đáp ứng cầu:** $\sum_{j} X_{jk} \ge d_k \quad \forall k$. Vì pallet mang đúng giỏ hàng của khách, đủ tổng pallet cũng là đủ từng nhóm sản phẩm.

**(2) Cân bằng luồng:** $\sum_{i} T_{ij} = Out_j \quad \forall j \ne NDC$.

**(3) Sức chứa và mở kho [ĐỔI]:**
- Kho giữ hàng: $\dfrac{1}{360}\Big(\sum_k DOS_{jk}\,X_{jk} + DOS^{tr}_j \sum_l T_{jl}\Big) \le C_j\,Y_j$ — tồn kho trung bình không vượt số chỗ chứa.
- DEPO: $Out_j \le 1.5\,D\,Y_j$ (cận trên, không chặn luồng).

**(4) Chỉ kho mở mới giao cho khách:** $X_{jk} \le d_k\,Y_j \quad \forall (j,k),\ j \in J^{dec}$.

**(5) Miền giá trị:** $Y_j \in \{0,1\}$, $T_{ij}, X_{jk} \ge 0$.

---

## 7. Phương pháp giải (không đổi so với bản 12/10)

**Bước 1 – Payoff table (lexicographic):** mỗi bước tối đa 60 phút, gap 0.5%.

**Bước 2 – AUGMECON2:** $\min\; f_1 - 10^{-3}\left(\dfrac{s_2}{r_2} + 0.1\,\dfrac{s_3}{r_3}\right)$ với $f_2 + s_2 = \varepsilon_2$, $f_3 + s_3 = \varepsilon_3$. Lưới 10 × 10 (tối đa 121 lần giải), mỗi lần tối đa 30 phút, gap 0.5%. Pyomo + HiGHS.

**Bước 3 – Lọc Pareto:** bỏ phương án trùng, gần trùng và bị trội.

**Bước 4 – TOPSIS:** 4 kịch bản trọng số (chi phí, thời gian giao, CO2): Cost-driven 0.50/0.25/0.25, Service-driven 0.25/0.50/0.25, Green-driven 0.25/0.25/0.50, Balanced 1/3 mỗi tiêu chí.
