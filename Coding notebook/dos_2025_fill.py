# ===== DOS 2025: FILL Ô THIẾU + DOS MỖI KHO + BẢN CHO MẸ =====
# Input : Raw Data/Facility_ProductGroupID_DOS.parquet (DOS lịch sử 2025, kho × nhóm sản phẩm)
#         Raw Data/0,1_Baseline2025/ENO_ShareLastMileB2B + ENO_ShareTransfer (lượng xuất 2025, trọng số)
#         Model - Data used/ facility_master, demand_b2b, product_master, dos (DOS 2030 cũ, để so sánh)
# Output: Model - Data used/dos_2025_fill.parquet (35 kho giữ hàng × 124 nhóm có cầu, đã fill)
#         Model - Data used/dos_2025.parquet      (53 kho, 1 DOS/kho, cùng dạng với dos.parquet)
#         Model Outputs/Mẹ/dos_2025.csv            (bản dễ đọc cho mẹ)
import numpy as np
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent          # thư mục Data/
RAW, IN, MOM = BASE / "Raw Data", BASE / "Model - Data used", BASE / "Model Outputs" / "Mẹ"
DAYS = 360                                              # cùng số ngày với mô hình (Decision_Log 4.4)

# ===== 1. ĐỌC DỮ LIỆU =====
dh = pd.read_parquet(RAW / "Facility_ProductGroupID_DOS.parquet")                 # DOS 2025 kho × nhóm
fac = pd.read_parquet(IN / "facility_master.parquet",
                      columns=["LocationID", "FacilityType", "MainIsland", "CapacityInPallet"])
kho_giu = fac[fac["FacilityType"] != "DEPO"]                                       # 35 kho có giữ hàng

# Pallet và số cái theo nhóm sản phẩm (để đổi lượng xuất từ cái sang pallet)
dm = pd.read_parquet(IN / "demand_b2b.parquet", columns=["ProductGroupID", "ProductID", "DemandInPCS"])
pm = pd.read_parquet(IN / "product_master.parquet", columns=["ProductID", "QuantityPiecesPerPallet"])
pm["ProductID"] = pm["ProductID"].astype(str)
dm = dm.merge(pm, on="ProductID", how="left", validate="many_to_one")
dm["Pallet"] = dm["DemandInPCS"] / dm["QuantityPiecesPerPallet"]                  # pallet theo từng sản phẩm
pg = dm.groupby("ProductGroupID").agg(PCS=("DemandInPCS", "sum"), Pallet=("Pallet", "sum"))
pg["PcsPerPallet"] = pg["PCS"] / pg["Pallet"]                                      # cái/pallet bình quân của nhóm
NHOM = pg.index.tolist()                                                           # 124 nhóm có cầu

# ===== 2. FILL: lưới đủ 35 kho × 124 nhóm =====
luoi = pd.MultiIndex.from_product([kho_giu["LocationID"], NHOM],
                                  names=["LocationID", "ProductGroupID"]).to_frame(index=False)
luoi = luoi.merge(dh, on=["LocationID", "ProductGroupID"], how="left").merge(
    kho_giu[["LocationID", "FacilityType"]], on="LocationID")
luoi["IsFilled"] = luoi["DOS"].isna()                                              # True = ô bị thiếu, sẽ fill

# Quy tắc fill theo thứ tự: (a) trung vị của nhóm ở các kho cùng loại; (b) trung vị của nhóm ở mọi kho
med_loai = luoi.groupby(["ProductGroupID", "FacilityType"])["DOS"].transform("median")
med_nhom = luoi.groupby("ProductGroupID")["DOS"].transform("median")
luoi["FillRule"] = np.where(~luoi["IsFilled"], "goc",
                    np.where(med_loai.notna(), "trungvi_cung_loai_kho", "trungvi_moi_kho"))
luoi["DOS"] = luoi["DOS"].fillna(med_loai).fillna(med_nhom)
# DOS = 0 ở NDC (3 nhóm, có xuất nhưng không tồn kho cuối tháng) được giữ nguyên: là số thật

assert len(luoi) == len(kho_giu) * len(NHOM)
assert luoi["DOS"].notna().all() and (luoi["DOS"] >= 0).all()

# ===== 3. DOS MỖI KHO = trung bình có trọng số pallet xuất 2025 =====
sh = pd.read_parquet(RAW / "0,1_Baseline2025" / "ENO_ShareLastMileB2B.parquet")
st = pd.read_parquet(RAW / "0,1_Baseline2025" / "ENO_ShareTransfer.parquet")
xuat = (pd.concat([sh, st])[["OriginID", "ProductGroupID", "VolumeInPCS"]]
        .groupby(["OriginID", "ProductGroupID"], as_index=False)["VolumeInPCS"].sum()
        .rename(columns={"OriginID": "LocationID"}))
xuat["Pallet2025"] = xuat["VolumeInPCS"] / xuat["ProductGroupID"].map(pg["PcsPerPallet"])   # cái -> pallet
luoi = luoi.merge(xuat[["LocationID", "ProductGroupID", "Pallet2025"]],
                  on=["LocationID", "ProductGroupID"], how="left")
luoi["Pallet2025"] = luoi["Pallet2025"].fillna(0)

def dos_tb(g):
    w = g["Pallet2025"]
    return np.average(g["DOS"], weights=w) if w.sum() > 0 else g["DOS"].median()

dos_kho = luoi.groupby("LocationID").apply(dos_tb, include_groups=False).rename("DOS").reset_index()
dos_2025 = fac[["LocationID", "FacilityType"]].merge(dos_kho, on="LocationID", how="left")
dos_2025["DOS"] = dos_2025["DOS"].fillna(0.0)                                       # DEPO: cross-dock, DOS = 0
dos_2025 = dos_2025[["LocationID", "DOS", "FacilityType"]]                         # cùng cột với dos.parquet
assert len(dos_2025) == len(fac) == 53
assert ((dos_2025["DOS"] > 0) | (dos_2025["FacilityType"] == "DEPO")).all()

# ===== 4. XUẤT FILE =====
luoi[["LocationID", "ProductGroupID", "FacilityType", "DOS", "IsFilled", "FillRule", "Pallet2025"]].to_parquet(
    IN / "dos_2025_fill.parquet", index=False)
dos_2025.to_parquet(IN / "dos_2025.parquet", index=False)

cu = pd.read_parquet(IN / "dos.parquet")[["LocationID", "DOS"]].rename(columns={"DOS": "DOS_2030"})
me = (fac.merge(cu, on="LocationID").merge(dos_2025[["LocationID", "DOS"]].rename(columns={"DOS": "DOS_2025"}),
                                           on="LocationID"))
cap = lambda d: np.where(d > 0, me["CapacityInPallet"] * DAYS / d.where(d > 0), np.inf)
me["SucChuaNam_2030"], me["SucChuaNam_2025"] = cap(me["DOS_2030"]), cap(me["DOS_2025"])
me = me.rename(columns={"LocationID": "Kho", "FacilityType": "LoaiKho", "MainIsland": "Dao",
                        "CapacityInPallet": "ChoChua"})
MOM.mkdir(parents=True, exist_ok=True)
me.round(2).to_csv(MOM / "dos_2025.csv", index=False, encoding="utf-8-sig")

# ===== 5. KIỂM TRA (in ra để đọc) =====
if __name__ == "__main__":
    pd.set_option("display.width", 250)
    print(f"Ô fill: {luoi['IsFilled'].sum()} / {len(luoi):,} | theo quy tắc: {luoi['FillRule'].value_counts().to_dict()}")
    print("\n10 ô đã fill:"); print(luoi[luoi["IsFilled"]].head(10).round(1).to_string(index=False))
    print("\nDOS mỗi kho, 2030 (cũ) vs 2025 (mới, trọng số pallet):")
    print(me[me["LoaiKho"] != "DEPO"][["Kho", "LoaiKho", "Dao", "ChoChua", "DOS_2030", "DOS_2025",
                                      "SucChuaNam_2030", "SucChuaNam_2025"]].round(1).to_string(index=False))
    # Kiểm tra nhanh theo đảo: sức chứa thông lượng (bỏ NDC) so với cầu của đảo
    dem = pd.read_parquet(BASE / "Model Outputs" / "demand.parquet", columns=["MainIsland", "DemandPallet"])
    dao = me[(me["LoaiKho"] != "DEPO") & (me["LoaiKho"] != "NDC")].groupby("Dao")[["SucChuaNam_2030", "SucChuaNam_2025"]].sum()
    dao = dao.join(dem.groupby("MainIsland")["DemandPallet"].sum().rename("CauDao"), how="outer")
    print("\nTheo đảo (không tính NDC): tổng sức chứa thông lượng vs cầu của đảo, pallet/năm")
    print(dao.round(0).to_string())
