# Vẽ sơ đồ mạng lưới phân phối (Multi-Objective Optimization.ipynb, mục 2.1.1)
# Chạy: python draw_network.py "<đường dẫn PNG>"
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch, Circle, FancyBboxPatch

out = sys.argv[1] if len(sys.argv) > 1 else "network_structure.png"
fig, ax = plt.subplots(figsize=(16, 8.4), dpi=200)
ax.set_xlim(0, 16); ax.set_ylim(-0.5, 7.9); ax.set_aspect("equal"); ax.axis("off")

INK = "#1f2937"; MUTED = "#6b7280"; WHITE = "#ffffff"; SOFT = "#9ca3af"
BLUE, BLUE_D = "#93c5fd", "#1d4ed8"       # cố định
AMB, AMB_D = "#fcd34d", "#b45309"         # kho mô hình chọn mở/đóng
GRN, GRN_D = "#86efac", "#15803d"         # khách hàng
ROOF = "#475569"
NL = "\n"


# ---------- icon ----------
def warehouse(cx, by, w, h, fill, edge, label, sub=None):
    """Nhà kho: thân chữ nhật, mái dốc, cửa cuốn có vạch ngang."""
    x0 = cx - w / 2
    ax.add_patch(Rectangle((x0, by), w, h, fc=fill, ec=edge, lw=1.6, zorder=3))
    ax.add_patch(Polygon([(x0 - w * 0.08, by + h), (cx, by + h + h * 0.55), (x0 + w * 1.08, by + h)],
                         closed=True, fc=edge, ec=edge, lw=1.6, zorder=3))
    dw, dh = w * 0.42, h * 0.62
    ax.add_patch(Rectangle((cx - dw / 2, by), dw, dh, fc=WHITE, ec=edge, lw=1.2, zorder=4))
    for k in range(1, 5):
        yy = by + dh * k / 5
        ax.plot([cx - dw / 2, cx + dw / 2], [yy, yy], color=edge, lw=0.8, zorder=5)
    ax.text(cx, by - 0.14, label, ha="center", va="top", fontsize=10.5, weight="bold", color=INK, zorder=6)
    if sub:
        ax.text(cx, by - 0.44, sub, ha="center", va="top", fontsize=8.3, color=MUTED, zorder=6, linespacing=1.3)


def factory(cx, by, w, h):
    """Nhà máy: mái răng cưa, ống khói có khói."""
    x0 = cx - w / 2
    ax.add_patch(Rectangle((x0, by), w, h, fc=BLUE, ec=BLUE_D, lw=1.6, zorder=3))
    n = 3; tw = w / n
    for i in range(n):
        ax.add_patch(Polygon([(x0 + i * tw, by + h), (x0 + i * tw, by + h + h * 0.45), (x0 + (i + 1) * tw, by + h)],
                             closed=True, fc=BLUE_D, ec=BLUE_D, zorder=3))
    ax.add_patch(Rectangle((x0 + w * 0.72, by + h), w * 0.14, h * 0.95, fc=ROOF, ec=ROOF, zorder=2))
    for k, r in enumerate([0.09, 0.12, 0.15]):
        ax.add_patch(Circle((x0 + w * 0.79 + k * 0.12, by + h * 2.05 + k * 0.16), r, fc="#cbd5e1", ec="none", zorder=1))
    for i in range(3):
        ax.add_patch(Rectangle((x0 + w * (0.12 + i * 0.27), by + h * 0.45), w * 0.16, h * 0.28, fc=WHITE, ec=BLUE_D, lw=1, zorder=4))
    ax.text(cx, by - 0.14, "Factories", ha="center", va="top", fontsize=10.5, weight="bold", color=INK)
    ax.text(cx, by - 0.44, "next to the NDC", ha="center", va="top", fontsize=8.3, color=MUTED)


def store(cx, by, w=0.58, h=0.4):
    """Cửa hàng: mái hiên sọc."""
    x0 = cx - w / 2
    ax.add_patch(Rectangle((x0, by), w, h, fc=WHITE, ec=GRN_D, lw=1.3, zorder=3))
    n = 4; sw = (w * 1.1) / n
    for i in range(n):
        ax.add_patch(Polygon([(x0 - w * 0.05 + i * sw, by + h), (x0 - w * 0.05 + (i + 1) * sw, by + h),
                              (x0 - w * 0.05 + (i + 1) * sw, by + h + h * 0.38), (x0 - w * 0.05 + i * sw, by + h + h * 0.38)],
                             closed=True, fc=GRN if i % 2 == 0 else GRN_D, ec=GRN_D, lw=0.8, zorder=4))
    ax.add_patch(Rectangle((cx - w * 0.14, by), w * 0.28, h * 0.62, fc=GRN, ec=GRN_D, lw=1, zorder=4))


def arrow(p1, p2, rad=0.0, ls="-", lw=1.6, ms=14, color=INK):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color,
                                 linestyle=ls, connectionstyle=f"arc3,rad={rad}", shrinkA=5, shrinkB=5, zorder=2))


def note(x, y, t, color=INK, size=8.8):
    ax.text(x, y, t, ha="center", va="center", fontsize=size, color=color, style="italic", zorder=6,
            bbox=dict(boxstyle="round,pad=0.18", fc=WHITE, ec="none"))


# ---------- vị trí (tâm x, đáy y) ----------
F = (1.0, 3.4)          # nhà máy
N = (3.5, 3.25)         # NDC
R = (6.2, 5.3)          # RDC
S = (9.0, 5.3)          # DC Satellite
D = (7.6, 1.6)          # DC Direct
L = (11.4, 3.45)        # DEPO = last-mile hub
WW, WH = 1.05, 0.72     # cỡ kho vừa

factory(F[0], F[1], 1.4, 0.9)
warehouse(N[0], N[1], 1.7, 1.2, BLUE, BLUE_D, "NDC", "1 · always open")
warehouse(R[0], R[1], WW, WH, AMB, AMB_D, "RDC", "9 sites")
warehouse(S[0], S[1], WW, WH, AMB, AMB_D, "DC Satellite", "18 sites")
warehouse(D[0], D[1], WW, WH, AMB, AMB_D, "DC Direct", "7 sites")
warehouse(L[0], L[1], WW, WH, AMB, AMB_D, "DEPO", "last-mile hub" + NL + "18 sites · cross-dock")

# khách hàng: lưới 6 hàng × 3 cột
CX0, CY0 = 13.6, 1.3
for r in range(6):
    for c in range(3):
        store(CX0 + c * 0.85, CY0 + r * 0.9)
ax.text(CX0 + 0.85, 0.95, "B2B customer groups", ha="center", va="top", fontsize=10.5, weight="bold", color=INK)
ax.text(CX0 + 0.85, 0.63, "3,346 demand nodes · 72,624 pallets/year", ha="center", va="top", fontsize=8.3, color=MUTED)

mid = lambda p, h=WH: (p[0], p[1] + h / 2)          # điểm giữa thân kho
right = lambda p, w=WW, h=WH: (p[0] + w / 2 + 0.08, p[1] + h / 2)
left = lambda p, w=WW, h=WH: (p[0] - w / 2 - 0.08, p[1] + h / 2)

# ---------- luồng chính (theo sơ đồ mạng của công ty) ----------
arrow((F[0] + 0.75, F[1] + 0.45), (N[0] - 0.95, F[1] + 0.45), lw=2.2, ms=16)          # nhà máy -> NDC
note(2.25, 4.3, "supply" + NL + "cost 0")
arrow((N[0] + 0.9, N[1] + 0.9), left(R))                                              # NDC -> RDC
arrow(right(R), left(S))                                                              # RDC -> DC Satellite
arrow((S[0] + 0.45, S[1] - 0.05), (L[0] - 0.35, L[1] + WH + 0.45))                    # DC Satellite -> DEPO
arrow((N[0] + 0.9, N[1] + 0.2), left(D))                                              # NDC -> DC Direct
arrow((D[0] + 0.45, D[1] + WH + 0.05), (L[0] - 0.62, L[1] + 0.2))                     # DC Direct -> DEPO
arrow(right(L), (CX0 - 0.45, L[1] + 0.36), lw=2.0, ms=15)                              # DEPO -> khách

note(4.55, 4.95, "first mile")
note(7.6, 5.95, "mid mile")
note(9.8, 4.5, "mid mile" + NL + "≤ 200 km")
note(9.95, 2.8, "mid mile")
note(12.55, 4.15, "last mile")

# last-mile cũng có thể đi thẳng từ RDC / DC (tuyến có trong bảng giá công ty)
for p, tgt in [(R, (CX0 - 0.45, 5.95)), (S, (CX0 - 0.45, 5.3)), (D, (CX0 - 0.45, 1.6))]:
    arrow(right(p) if p is not R else (R[0] + 0.3, R[1] + WH + 0.5), tgt, lw=1.0, ms=10, color=SOFT, ls="--",
          rad=-0.12 if p is R else 0.0)
note(12.4, 6.65, "last mile also possible" + NL + "directly from RDC / DC", color=MUTED, size=8.2)

# NDC giao thẳng cho khách lớn ở gần
arrow((N[0] + 0.6, N[1] - 0.05), (CX0 - 0.35, CY0 + 0.15), rad=0.38, lw=1.3)
note(8.2, 0.12, "direct from NDC: large customers within 150 km")

# ---------- chú thích ----------
lx, ly = 0.3, -0.3
for fc, ec, t in [(BLUE, BLUE_D, "fixed, always open"), (AMB, AMB_D, "open / close decided by the model"),
                  (GRN, GRN_D, "demand met in full")]:
    ax.add_patch(FancyBboxPatch((lx, ly - 0.1), 0.3, 0.22, boxstyle="round,pad=0.01,rounding_size=0.04", fc=fc, ec=ec, lw=1.2))
    ax.text(lx + 0.42, ly + 0.01, t, va="center", fontsize=8.8, color=MUTED)
    lx += 0.8 + len(t) * 0.085

plt.savefig(out, bbox_inches="tight", facecolor="white")
print("saved", out)
