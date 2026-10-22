"""Fig. 1 (column width): macro + controller architecture; with --layout also (b) the memory_1T1R layout from its GDS with
the functional blocks outlined (block boxes from the top-level instance placements)."""
import sys
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.collections import PolyCollection
import style as S

GDS = S.BACKEND / "macros/memory_1T1R/memory_1T1R.gds"
LW = 0.7
BLOCKS = [  # name in GDS, label, colour
    ("memory_1t1r_8x8_CB_PWR", "column drivers\nTS_LS ($V_\\mathrm{drain}$)", S.ORANGE),
    ("memory_1t1r_1T1RCB_8x8", "64$\\times$64\n1T1R array", S.BLUE),
    ("memory_1t1r_8x8_CB_PWR_WL", "WL flops\n+ LS\n($V_\\mathrm{gate}$)", S.VIOLET),
    ("memory_1t1r_8x8_CB_DRAIN_BUF", "drain switches, BL buffers", S.INK2),
    ("memory_1t1r_TDC_SAMPLE", "TDC samplers\n64$\\times$8 flops", S.AQUA),
    ("memory_1t1r_TDC_DELAY", "", S.AQUA),
]


FS = 6.0                       # box text size (column-width figure)


def rbox(ax, x, y, w, h, text, fc="white", ec=S.INK2, fs=None, color=S.INK, weight="normal"):
    fs = FS if fs is None else fs
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06", fc=fc, ec=ec, lw=LW))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, weight=weight,
            linespacing=1.1)


def arrow(ax, a, b, color=S.INK2, text=None, side="right"):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", lw=LW, color=color, shrinkA=0, shrinkB=0,
                                                     mutation_scale=5))
    if text:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ax.text(mx + (0.06 if side == "right" else -0.06), my, text, fontsize=5.2, color=S.INK2,
                ha="left" if side == "right" else "right", va="center")


def arch(ax):
    ax.set_xlim(-0.3, 4.75), ax.set_ylim(0, 6.4), ax.axis("off")
    blue_fc, or_fc, aq_fc, vi_fc = "#dbe8f8", "#fbe3d9", "#d4f0e5", "#e4e0f8"
    rbox(ax, 0.0, 5.55, 4.6, 0.8, "host (UART / I$^2$C) $\\rightarrow$ 8 registers: CTRL, CELLS (row mask),\nWORD (64 b), TIMINGS, STATUS, DATA",
         fc="#f1f0ec")
    rbox(ax, 0.0, 4.45, 4.6, 0.8, "controller FSM: 21 states, 12 operations\nprecharge $\\cdot$ settle(-drain) $\\cdot$ signed offset $\\cdot$ READ_SAMPLE",
         fc=blue_fc, ec=S.BLUE)
    arrow(ax, (2.3, 5.55), (2.3, 5.25))
    # macro
    ax.add_patch(Rectangle((0.0, 0.0), 4.6, 4.15, fc="none", ec=S.BLUE, lw=0.9, ls=(0, (3, 2))))
    ax.text(2.25, 4.08, "memory_1T1R macro", fontsize=6.2, color=S.BLUE, va="top", weight="bold")
    rbox(ax, 0.25, 3.05, 2.8, 0.6, "column drivers TS_LS ($V_\\mathrm{drain}$)", fc=or_fc, ec=S.ORANGE)
    rbox(ax, 0.25, 1.6, 2.8, 1.2, "64$\\times$64 1T1R array\nmulti-row: $\\Sigma G$ on each BL", fc=S.BLUE, ec=S.BLUE,
         color="white", weight="bold")
    rbox(ax, 3.3, 1.6, 0.85, 1.2, "WL flops\n+ LS\n($V_\\mathrm{gate}$)", fc=vi_fc, ec=S.VIOLET)
    rbox(ax, 0.25, 1.15, 2.8, 0.3, "drain switches, BL buffers", fc="white")
    rbox(ax, 0.25, 0.2, 2.8, 0.75, "TDC samplers: 64 $\\times$ 8 taps", fc=aq_fc, ec=S.AQUA)
    rbox(ax, 3.3, 0.1, 0.85, 0.85, "READ LS +\ndelay line\n($V_\\mathrm{DEL}$)", fc=aq_fc, ec=S.AQUA, fs=5.6)
    arrow(ax, (1.0, 4.45), (1.0, 3.65))
    ax.text(1.06, 3.8, "PWR_EN, DIN", fontsize=5.2, color=S.INK2, va="center")
    arrow(ax, (3.72, 4.45), (3.72, 2.8))
    ax.text(3.66, 3.3, "WLS[63:0]", fontsize=5.2, color=S.INK2, va="center", ha="right")
    arrow(ax, (3.3, 2.2), (3.05, 2.2))
    arrow(ax, (1.65, 3.05), (1.65, 2.8))
    arrow(ax, (1.65, 1.6), (1.65, 1.45))
    arrow(ax, (1.65, 1.15), (1.65, 0.95))
    arrow(ax, (3.3, 0.57), (3.05, 0.57))
    arrow(ax, (4.38, 4.45), (4.38, 0.95))
    ax.text(4.42, 3.3, "READ", fontsize=5.2, color=S.INK2, rotation=90, va="center", ha="left")
    ax.annotate("", xy=(0.12, 4.45), xytext=(0.12, 0.57),
                arrowprops=dict(arrowstyle="-|>", lw=LW, color=S.AQUA, shrinkA=0, shrinkB=0, mutation_scale=5,
                                connectionstyle="arc3,rad=0"))
    ax.plot([0.12, 0.25], [0.57, 0.57], color=S.AQUA, lw=LW)
    ax.text(-0.06, 2.2, "MEM_OUT[511:0]", fontsize=5.2, color=S.AQUA, rotation=90, va="center", ha="right")


def layout(ax):
    # LEF_NOTE: dimension labels use the LEF size (226.53 x 547.355); the GDS bbox is 226.8 wide with boundary markers
    import gdstk  # only the layout panel needs it
    lib = gdstk.read_gds(str(GDS))
    top = lib.top_level()[0]
    (x0, y0), (x1, y1) = top.bounding_box()
    style = {(1, 0): ("#c9c4b8", 0.55), (5, 0): ("#d98a7e", 0.35), (10, 0): ("#8fb2d9", 0.30),
             (30, 0): ("#9fcfb3", 0.25), (50, 0): ("#c7b8e8", 0.30), (143, 0): ("#1f4f8f", 0.9)}
    polys = {k: [] for k in style}
    for p in top.get_polygons():
        key = (p.layer, p.datatype)
        if key in polys:
            polys[key].append(p.points)
    for key, pts in polys.items():
        col, a = style[key]
        ax.add_collection(PolyCollection(pts, facecolors=col, edgecolors="none", alpha=a, rasterized=True))
    boxes = {}
    for r in top.references:
        n = r.cell.name
        if "CDNS" in n:
            continue
        (a0, b0), (a1, b1) = r.bounding_box()
        b = boxes.get(n)
        boxes[n] = (a0, b0, a1, b1) if b is None else (min(b[0], a0), min(b[1], b0), max(b[2], a1), max(b[3], b1))
    for name, lab, col in BLOCKS:
        if name not in boxes:
            continue
        a0, b0, a1, b1 = boxes[name]
        ax.add_patch(Rectangle((a0, b0), a1 - a0, b1 - b0, fc="none", ec=col, lw=0.9))
    ax.set_xlim(x0 - 2, x1 + 30), ax.set_ylim(y0 - 14, y1 + 2)
    ax.set_aspect("equal"), ax.axis("off")
    ax.annotate("", xy=(x0, y0 - 6), xytext=(x1, y0 - 6), arrowprops=dict(arrowstyle="<->", lw=0.5, color=S.INK2))
    ax.text((x0 + x1) / 2, y0 - 8, "226.5 µm", fontsize=5.6, ha="center", va="top", color=S.INK2)
    ax.annotate("", xy=(x1 + 6, y0), xytext=(x1 + 6, y1), arrowprops=dict(arrowstyle="<->", lw=0.5, color=S.INK2))
    ax.text(x1 + 9, (y0 + y1) / 2, "547.4 µm", fontsize=5.6, rotation=90, ha="left", va="center", color=S.INK2)
    labels = [("memory_1t1r_8x8_CB_PWR", "TS_LS"), ("memory_1t1r_1T1RCB_8x8", "array"),
              ("memory_1t1r_8x8_CB_PWR_WL", "WL"), ("memory_1t1r_TDC_SAMPLE", "TDC")]
    for name, lab in labels:
        a0, b0, a1, b1 = boxes[name]
        ax.text((a0 + a1) / 2, (b0 + b1) / 2, lab, fontsize=6.0, ha="center", va="center", color=S.INK, weight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.8))


def main():
    S.setup()
    if "--arch" in sys.argv:            # Fig. 1(a) alone, sans-serif (paper since 22.10.26; (b) is clipped from macro.pdf)
        mpl.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                             "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic"})
        fig = plt.figure(figsize=(0.655 * S.COL_W, 2.2))
        ax1 = fig.add_axes([0.05, 0.0, 0.95, 0.955])
        arch(ax1)
        for t in ax1.texts:               # Arial runs wider than Times: scale every label down
            t.set_fontsize(t.get_fontsize() * 0.84)
        fig.text(0.0, 0.995, "(a)", fontsize=8, weight="bold", va="top")
        S.save(fig, "macro_arch")
        return
    if "--layout" in sys.argv:          # full-width two-panel version (not in the paper)
        fig = plt.figure(figsize=(S.PAGE_W, 2.55))
        ax1 = fig.add_axes([0.03, 0.0, 0.66, 0.96])
        ax2 = fig.add_axes([0.73, 0.0, 0.27, 0.96])
        arch(ax1)
        layout(ax2)
        fig.text(0.0, 0.995, "(a)", fontsize=11.2, weight="bold", va="top")
        fig.text(0.71, 0.995, "(b)", fontsize=11.2, weight="bold", va="top")
        S.save(fig, "macro_layout")
        return
    # column width: (a) architecture, (b) the tape-out-ready layout beside it
    fig = plt.figure(figsize=(S.COL_W, 2.2))
    ax1 = fig.add_axes([0.035, 0.0, 0.655, 0.955])
    ax2 = fig.add_axes([0.715, 0.0, 0.285, 0.955])
    arch(ax1)
    layout(ax2)
    fig.text(0.0, 0.995, "(a)", fontsize=8, weight="bold", va="top")
    fig.text(0.705, 0.995, "(b)", fontsize=8, weight="bold", va="top")
    S.save(fig, "macro")


if __name__ == "__main__":
    main()
