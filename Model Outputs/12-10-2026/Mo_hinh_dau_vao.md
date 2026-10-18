# Mô hình: giả định, tham số, biến và công thức (đầu vào) — bản 12/10/2026

Tài liệu này mô tả đầu vào của mô hình tối ưu mạng lưới phân phối trong khóa luận, **bản dùng cho lần chạy ngày 12/10/2026**. Kết quả nằm ở `README.md` và các file `.csv` cùng thư mục. Dữ liệu đã ẩn danh: kho chỉ ghi bằng mã, không có tên công ty hay tên kho.

Những chỗ **khác bản 11/10/2026** được đánh dấu **[MỚI]** hoặc **[ĐỔI]**. Tóm tắt các thay đổi nằm ở `README.md`, mục "Khác gì so với bản 11/10/2026".

---

## 1. Giả định

| # | Giả định |
|---|---|
| 1 | **Một kỳ = một năm**, dữ liệu năm 2025. Cầu, chi phí, sức chứa đều tính theo năm. Không dự báo tương lai |
| 2 | **Một sản phẩm gộp**, đo bằng **pallet**. Mỗi sản phẩm được đổi từ số cái sang pallet trước khi cộng |
| 3 | Chỉ kênh **B2B**, chỉ **Indonesia** |
| 4 | **Cầu cố định**: mỗi nhóm khách một con số pallet/năm. Phải giao đủ 100% cầu, không cho thiếu hàng |
| 5 | Nhà máy nằm cạnh NDC: chặng nhà máy → NDC **phí 0, không giới hạn** lượng hàng |
| 6 | Chỉ xét **kho đang có**, không xây kho mới. 53 kho trong phạm vi |
| 7 | **NDC và 9 RDC luôn mở**. 43 kho còn lại (7 DC Direct, 18 DC Satellite, 18 DEPO) do mô hình chọn mở / đóng |
| 8 | **Luồng hàng theo phân tầng**: NDC → RDC, NDC → DC Direct, NDC → DEPO (≤ 150 km), RDC → DC Satellite, RDC → DEPO (≤ 200 km), DC Direct → DEPO (≤ 200 km), DC Satellite → DEPO (≤ 200 km). Không có luồng ngang hay ngược. Tuyến thật đang chạy dài hơn 200 km vẫn được giữ (ví dụ D31 → DEPO01, 290 km) |
| 9 | **[MỚI] RDC → DC Satellite chỉ trong cùng đảo.** Mỗi DC Satellite chỉ nhận hàng từ RDC cùng đảo. DC Satellite ở đảo không có RDC (Bali – Nusra, Maluku) chỉ nhận hàng từ **RDC gần nhất** (tính theo đường chim bay) |
| 10 | **Chặng cuối (kho → khách) chỉ trong cùng đảo**. Ngoại lệ: nhóm khách ở đảo không có kho nào (Papua) được nhận hàng từ đảo khác. Mọi kho được giao cho khách cùng đảo, riêng NDC chỉ giao cho khách trong bán kính 150 km |
| 11 | Một nhóm khách **có thể nhận hàng từ nhiều kho** |
| 12 | **DEPO** là kho trung chuyển (cross-dock): không giữ tồn kho, không giới hạn sức chứa. Khách của DEPO phải chờ cả chặng **vào** DEPO lẫn chặng DEPO → khách |
| 13 | **[MỚI] Hàng vào DEPO đi gửi ghép (LTL).** Lượng hàng vào DEPO nhỏ (82% số tuyến chở dưới 1 tấn/ngày), nên giả định hàng được gửi chung xe với hàng của người khác, xe vẫn chạy đầy. Vì vậy chặng RDC/DC → DEPO dùng hệ số CO2 của xe tải chặng giữa (360.83). Hệ số xe van (756) dùng làm kịch bản độ nhạy |
| 14 | Mọi chi phí ở **mặt bằng giá 2025**. Chi phí là chi phí vận hành (OPEX), không có chi phí đầu tư (CAPEX) |
| 15 | Không có biến tồn kho. Số ngày hàng nằm kho (DOS) chỉ dùng để đổi chỗ chứa thành sức chứa thông lượng năm |

---

## 2. Tập hợp và chỉ số

| Tập | Chỉ số | Gồm những gì | Số phần tử |
|---|---|---|---|
| $J$ | $i, j, l$ | Tất cả kho (NDC, RDC, DC Direct, DC Satellite, DEPO) | 53 |
| $J^{fix}$ | | Kho luôn mở: NDC + 9 RDC | 10 |
| $J^{dec} = J \setminus J^{fix}$ | $j$ | Kho mô hình chọn mở / đóng | 43 |
| $J^{DEPO} \subset J$ | | Các DEPO | 18 |
| $K$ | $k$ | Nhóm khách B2B (mỗi nhóm = các điểm giao trong cùng một quận / huyện) | 3,346 |
| $A^{tr} \subset J \times J$ | $(i, j)$ | Tuyến kho → kho được phép (giả định 8 và 9). **[ĐỔI]** Trước: 216 tuyến | **96** |
| | | trong đó: RDC → DC Satellite. **[ĐỔI]** Trước: 161 | 41 |
| | | trong đó: tuyến vào DEPO | 39 |
| $A^{lm} \subset J \times K$ | $(j, k)$ | Tuyến kho → khách được phép (cùng đảo, giả định 10) | 52,981 |
| $J^{vao}_j,\ J^{ra}_j$ | | Các kho chở được vào / ra khỏi kho $j$ | |
| $K_j,\ J_k$ | | Các nhóm khách kho $j$ giao được / các kho giao được cho nhóm $k$ | |

---

## 3. Tham số

| Ký hiệu | Ý nghĩa | Đơn vị | Nguồn / cách tính |
|---|---|---|---|
| $d_k$ | Cầu của nhóm khách $k$. Tổng $D = \sum_k d_k$ = 72,624 pallet/năm (khoảng 18,721 tấn) | pallet/năm | Cầu B2B năm 2025 của công ty, đổi số cái → pallet theo từng sản phẩm |
| $F_j$ | Tiền thuê kho $j$ cả năm (trả đủ nếu mở, bất kể lượng hàng) | IDR/năm | Bảng thông tin kho của công ty (= 12 × tiền thuê tháng) |
| $h_j$ | Phí bốc xếp 1 pallet xuất khỏi kho $j$ | IDR/pallet | Bảng thông tin kho của công ty |
| $c^{tr}_{ij}$ | Phí chở 1 pallet từ kho $i$ sang kho $j$ | IDR/pallet | Bảng giá của công ty; tuyến không có giá được ước lượng bằng hồi quy theo khoảng cách |
| $c^{lm}_{jk}$ | Phí chở 1 pallet từ kho $j$ tới nhóm $k$ | IDR/pallet | Như trên |
| $DOS_j$ | Số ngày hàng nằm trong kho $j$, **riêng cho từng kho** (trung vị theo nhóm sản phẩm). Trung vị theo loại kho: NDC 7; RDC 11.2 (8.4–23.8); DC Direct 9.8 (7–28); DC Satellite 9.8 (7–29.4); DEPO 0 | ngày | Dữ liệu của công ty |
| $Cap_j$ | Sức chứa thông lượng năm $= \dfrac{\text{chỗ chứa}_j \times 360}{DOS_j}$; DEPO dùng $1.5 \times D$ (coi như không giới hạn) | pallet/năm | Chỗ chứa (pallet cùng lúc) lấy từ bảng thông tin kho |
| $LT_{jk}$ | Số ngày giao trên tuyến kho $j$ → khách $k$ = km ÷ tốc độ xe (45 hoặc 20 km/h tùy tuyến) ÷ 24 + thời gian đi biển. **[ĐỔI]** Chỉ là chặng cuối, không cộng sẵn chặng vào DEPO nữa | ngày | Bảng lead time của công ty; tuyến thiếu được ước lượng theo khoảng cách |
| $LT^{tr}_{ij}$ | **[MỚI]** Số ngày giao trên tuyến kho $i$ → DEPO $j$ (chặng vào DEPO). Trung vị 2.7 giờ; dài nhất D31 → DEPO01: 4.98 ngày (tuyến thật Sulawesi → Maluku, 254 km đường biển) | ngày | Bảng lead time của công ty |
| $w$ | Số tấn trên 1 pallet: trung bình 0.258 cho tuyến kho → kho; riêng từng nhóm khách cho tuyến kho → khách | tấn/pallet | Từ cầu theo sản phẩm |
| $e^{tr}_{ij},\ e^{lm}_{jk}$ | CO2 của 1 pallet trên tuyến (mục 5.3) | tấn CO2e/pallet | GLEC Framework |

---

## 4. Biến quyết định

| Biến | Miền | Ý nghĩa | Đơn vị |
|---|---|---|---|
| $Y_j$ | $\{0, 1\}$ với $j \in J^{dec}$; $Y_j = 1$ với $j \in J^{fix}$ | 1 = mở kho $j$, 0 = đóng | — |
| $T_{ij}$ | $\ge 0$ | Số pallet chở từ kho $i$ sang kho $j$ | pallet/năm |
| $X_{jk}$ | $\ge 0$ | Số pallet kho $j$ giao cho nhóm khách $k$ | pallet/năm |

Biểu thức phụ: hàng xuất khỏi kho $j$, $\;Out_j = \sum_{l \in J^{ra}_j} T_{jl} + \sum_{k \in K_j} X_{jk}$.

Kích thước: 43 biến nhị phân, khoảng 53 nghìn biến liên tục (96 biến $T$ + 52,981 biến $X$).

---

## 5. Hàm mục tiêu (cả 3 đều min)

### 5.1 `f1` – Tổng chi phí (tỷ IDR/năm)

Tiền thuê kho mở + phí chở kho → kho + phí chở kho → khách + phí bốc xếp hàng xuất kho.

$$f_1 = \sum_{j \in J} F_j\,Y_j + \sum_{(i,j) \in A^{tr}} c^{tr}_{ij}\,T_{ij} + \sum_{(j,k) \in A^{lm}} c^{lm}_{jk}\,X_{jk} + \sum_{j \in J} h_j\,Out_j$$

(Kết quả chia cho $10^9$ để đọc theo tỷ IDR.)

### 5.2 `f2` – Thời gian giao trung bình (ngày/pallet) **[ĐỔI]**

Trung bình số ngày giao của một pallet. Số hạng thứ nhất là chặng cuối của mọi pallet. Số hạng thứ hai cộng thêm **chặng vào DEPO**, tính theo **đúng kho đang cấp hàng** cho DEPO đó.

$$f_2 = \frac{1}{D}\left[\sum_{(j,k) \in A^{lm}} LT_{jk}\,X_{jk} \;+ \sum_{(i,j) \in A^{tr},\ j \in J^{DEPO}} LT^{tr}_{ij}\,T_{ij}\right]$$

Vì DEPO nhận vào bao nhiêu thì giao ra bấy nhiêu (ràng buộc 2), mỗi pallet giao từ DEPO được cộng đúng một lần chặng vào.

*Bản 11/10 cộng sẵn chặng vào **nhanh nhất** cho mọi khách của DEPO, kể cả khi kho đó đóng hoặc hàng thật đi từ kho khác, nên `f2` bị tính nhanh hơn thực tế, và mô hình không thấy cái giá thời gian khi DEPO lấy hàng từ kho xa.*

### 5.3 `f3` – CO2 (tấn CO2e/năm)

Tổng phát thải của mọi pallet trên mọi tuyến.

$$f_3 = \sum_{(i,j) \in A^{tr}} e^{tr}_{ij}\,T_{ij} + \sum_{(j,k) \in A^{lm}} e^{lm}_{jk}\,X_{jk}$$

CO2 của 1 pallet trên một tuyến = vận chuyển + kho xuất hàng:

$$e = w \times \frac{km_{bộ} \times EF_{bộ} + km_{biển} \times 22.35}{10^6} + w \times \frac{EF_{kho}}{1000}$$

| Chặng | Phương tiện (GLEC) | $EF_{bộ}$ (g CO2e/tấn-km) |
|---|---|---|
| NDC → kho | Xe tải 20 tấn | 79 |
| Kho → kho (không từ NDC), **kể cả RDC/DC → DEPO** (giả định 13) | Xe tải 4 tấn | 360.83 |
| NDC → khách | Xe tải 20 tấn | 79 |
| Kho → khách | Xe van 3 tấn | 756 |
| Phần đi biển của mọi chặng | Tàu container | 22.35 |

$EF_{kho}$ = 5.6 kg CO2e / tấn hàng xuất (kho thường), 1.3 (DEPO). Hệ số GLEC theo tấn đã gồm cả điện nền của tòa nhà kho, nên **không cộng thêm** phát thải cố định khi mở kho (tránh tính trùng). Km biển lấy từ dữ liệu lead time; tuyến khác đảo thiếu dữ liệu dùng tỉ lệ km biển trung vị của các tuyến thật cùng cặp đảo.

---

## 6. Ràng buộc

**(1) Đáp ứng cầu:** mỗi nhóm khách nhận ít nhất đủ cầu của mình.
$$\sum_{j \in J_k} X_{jk} \ge d_k \qquad \forall k \in K$$

**(2) Cân bằng luồng:** mỗi kho trừ NDC nhận vào bao nhiêu thì xuất ra bấy nhiêu. NDC là nguồn hàng duy nhất.
$$\sum_{i \in J^{vao}_j} T_{ij} = Out_j \qquad \forall j \in J \setminus \{NDC\}$$

**(3) Sức chứa và mở kho:** kho mở không xuất quá sức chứa thông lượng; kho đóng không xuất gì.
$$Out_j \le Cap_j\,Y_j \qquad \forall j \in J$$

**(4) Chỉ kho mở mới giao cho khách** (làm chặt mô hình để giải nhanh, không đổi nghiệm).
$$X_{jk} \le d_k\,Y_j \qquad \forall (j,k) \in A^{lm},\ j \in J^{dec}$$

**(5) Miền giá trị:** $Y_j \in \{0,1\}$ cho $j \in J^{dec}$, $Y_j = 1$ cho $j \in J^{fix}$, $T_{ij} \ge 0$, $X_{jk} \ge 0$.

Luật cùng đảo (giả định 9, 10) và luật bán kính (giả định 8) không viết thành ràng buộc: các tuyến không được phép được **bỏ khỏi tập tuyến** $A^{tr}, A^{lm}$ trước khi dựng mô hình.

---

## 7. Phương pháp giải

**Bước 1 – Payoff table (lexicographic).** Với mỗi mục tiêu: tối ưu nó; giữ nguyên mức đó rồi tối ưu mục tiêu thứ hai; giữ cả hai rồi tối ưu mục tiêu thứ ba. Được 3 phương án "cực đoan" và khoảng [tốt nhất, tệ nhất] của mỗi mục tiêu (Mavrotas, 2009). **[ĐỔI]** Mỗi bước tối đa **60 phút**, sai số tối ưu (gap) **0.5%**.

**Bước 2 – AUGMECON2** (Mavrotas & Florios, 2013). Giữ `f1` làm mục tiêu chính, đặt trần cho `f2` và `f3`, có biến slack $s_2, s_3$:

$$\min\; f_1 - 10^{-3}\left(\frac{s_2}{r_2} + 0.1\,\frac{s_3}{r_3}\right) \quad \text{với} \quad f_2 + s_2 = \varepsilon_2,\;\; f_3 + s_3 = \varepsilon_3,\;\; s_2, s_3 \ge 0$$

$r_2, r_3$ = khoảng giá trị của `f2`, `f3` từ payoff table. Mỗi khoảng chia 10 đoạn (11 mức trần), tối đa 121 lần giải; bỏ qua mức thừa (bypass) và dừng sớm khi vô nghiệm. **[ĐỔI]** Mỗi lần giải tối đa **30 phút**, gap **0.5%**, gap của từng lần được ghi lại (cột `Gap_%`). Solver HiGHS, Pyomo.

**Bước 3 – Lọc Pareto.** Gộp nghiệm AUGMECON2 với 3 góc của payoff table; bỏ phương án trùng, gần trùng (chi phí chênh trong 0.5%, thời gian giao chênh dưới 0.0001 ngày, CO2 chênh dưới 1 tấn) và phương án bị trội.

**Bước 4 – TOPSIS** (Hwang & Yoon, 1981). Chuẩn hoá vector từng tiêu chí, nhân trọng số, điểm lý tưởng = giá trị nhỏ nhất mỗi tiêu chí, điểm tệ nhất = lớn nhất, điểm TOPSIS = $d^- / (d^+ + d^-)$ (càng gần 1 càng tốt). 4 kịch bản trọng số (chi phí, thời gian giao, CO2):

| Kịch bản | Trọng số | Ý nghĩa |
|---|---|---|
| Cost-driven | 0.50, 0.25, 0.25 | Ưu tiên chi phí |
| Service-driven | 0.25, 0.50, 0.25 | Ưu tiên tốc độ giao |
| Green-driven | 0.25, 0.25, 0.50 | Ưu tiên môi trường |
| Balanced | 1/3, 1/3, 1/3 | Trung lập |

Tiêu chí ưu tiên có trọng số 0.50, tức nặng bằng hai tiêu chí còn lại cộng lại.
