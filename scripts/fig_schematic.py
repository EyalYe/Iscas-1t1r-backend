"""Column schematic of the memory_1T1R macro (from memory_1T1R.cdl) and the read timing concept."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch
import style as S

LW = 0.8
C = S.INK


def line(ax, pts, color=C, lw=LW, **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="butt", **kw)


def dot(ax, x, y, color=C):
    ax.plot([x], [y], "o", ms=2.2, color=color, mec=color)


def box(ax, x, y, w, h, text, fc="white", ec=C, fs=5.5, color=C, lw=LW):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color)


def buf(ax, x, y, s=0.22, fc="white", ec=C):
    ax.add_patch(Polygon([(x, y - s), (x, y + s), (x + 1.6 * s, y)], closed=True, fc=fc, ec=ec, lw=LW))


def nmos_v(ax, x, ytop, ybot, gate_side="left", color=C):
    """vertical nmos: drain at ytop, source at ybot, channel at x; returns gate (x, y)."""
    ym = (ytop + ybot) / 2
    h = (ytop - ybot) * 0.32
    line(ax, [(x, ytop), (x, ym + h)], color)
    line(ax, [(x, ym - h), (x, ybot)], color)
    sgn = -1 if gate_side == "left" else 1
    xc = x + sgn * 0.0
    line(ax, [(xc, ym + h), (xc + sgn * 0.12, ym + h)], color)
    line(ax, [(xc, ym - h), (xc + sgn * 0.12, ym - h)], color)
    line(ax, [(xc + sgn * 0.12, ym + h * 1.15), (xc + sgn * 0.12, ym - h * 1.15)], color, lw=1.2)
    line(ax, [(xc + sgn * 0.2, ym + h * 1.15), (xc + sgn * 0.2, ym - h * 1.15)], color, lw=LW)
    return xc + sgn * 0.2, ym


def memres(ax, x, ytop, ybot, color=C):
    ym = (ytop + ybot) / 2
    h = (ytop - ybot) * 0.3
    line(ax, [(x, ytop), (x, ym + h)], color)
    line(ax, [(x, ym - h), (x, ybot)], color)
    ax.add_patch(Rectangle((x - 0.09, ym - h), 0.18, 2 * h, fc="white", ec=color, lw=LW))
    ax.add_patch(Rectangle((x - 0.09, ym - h), 0.18, 0.35 * h, fc=color, ec=color, lw=LW))


def gnd(ax, x, y):
    line(ax, [(x, y), (x, y - 0.12)])
    for i, w in enumerate((0.14, 0.09, 0.04)):
        line(ax, [(x - w, y - 0.12 - i * 0.05), (x + w, y - 0.12 - i * 0.05)], lw=0.6)


def schematic(ax):
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-0.25, 7.25)
    ax.set_aspect("equal")
    ax.axis("off")
    xsl, xbl = 3.0, 4.2
    blue, orange, aqua = S.BLUE, S.ORANGE, S.AQUA

    # column driver (TS_LS) in the Vdrain domain
    box(ax, 2.6, 6.2, 2.0, 0.75, "TS_LS\n" + r"($V_\mathrm{drain}$)", fc="#fbe3d9", ec=orange)
    line(ax, [(1.3, 6.75), (2.6, 6.75)])
    line(ax, [(1.3, 6.42), (2.6, 6.42)])
    ax.text(1.25, 6.75, "PWR_EN[c]", ha="right", va="center", fontsize=5.5)
    ax.text(1.25, 6.42, "DIN[c]", ha="right", va="center", fontsize=5.5)
    line(ax, [(xsl, 6.2), (xsl, 1.2)])
    line(ax, [(xbl, 6.2), (xbl, 1.2)])
    ax.text(xsl - 0.08, 5.95, "SL[c]", ha="right", va="center", fontsize=5.5)
    ax.text(xbl + 0.08, 5.95, "BL[c]", ha="left", va="center", fontsize=5.5)

    # 1T1R cell: MEMRES TE = SL, BE = drain of HV nmos, source = BL, gate = WL
    xc = 3.6
    ax.add_patch(FancyBboxPatch((2.75, 3.05), 1.7, 2.35, boxstyle="round,pad=0.02", fc="none",
                                ec=blue, lw=0.6, ls=(0, (3, 2))))
    ax.text(2.7, 5.15, "1T1R\n×64 rows", ha="right", va="center", fontsize=5.2, color=blue)
    line(ax, [(xsl, 4.9), (xc, 4.9)]); dot(ax, xsl, 4.9)
    memres(ax, xc, 4.9, 4.2)
    gx, gy = nmos_v(ax, xc, 4.2, 3.4, "left")
    line(ax, [(xc, 3.4), (xc, 3.25), (xbl, 3.25)]); dot(ax, xbl, 3.25)
    ax.text(xc + 0.16, 4.55, "RRAM", fontsize=5, va="center")
    ax.text(xc + 0.16, 3.8, "HV\n300/450", fontsize=4.6, va="center", linespacing=0.9)

    # word-line path: WLS -> DFF -> LS(Vgate) -> WL
    box(ax, 0.0, 3.55, 0.55, 0.5, "DFF", fs=5)
    box(ax, 0.85, 3.55, 0.75, 0.5, "LS\n" + r"$V_\mathrm{gate}$", fs=5, fc="#dbe8f8", ec=blue)
    line(ax, [(0.55, 3.8), (0.85, 3.8)])
    line(ax, [(1.6, 3.8), (gx, 3.8)], color=blue)
    ax.text(2.25, 3.9, "WL[r]", fontsize=5.5, color=blue, ha="center", va="bottom")
    line(ax, [(0.27, 4.05), (0.27, 4.35)])
    ax.text(0.27, 4.4, "WLS[r]", fontsize=5.5, ha="center", va="bottom")

    # drain switches
    gsl = nmos_v(ax, xsl, 2.2, 1.4, "left")
    gbl = nmos_v(ax, xbl, 2.2, 1.4, "right")
    line(ax, [(xsl, 1.4), (xsl, 1.2)]); gnd(ax, xsl, 1.2)
    line(ax, [(xbl, 1.4), (xbl, 1.2)]); gnd(ax, xbl, 1.2)
    line(ax, [(1.6, gsl[1]), gsl])
    ax.text(1.55, gsl[1], r"DRAIN$_\mathrm{SL}$", ha="right", va="center", fontsize=5.5)
    line(ax, [gbl, (gbl[0] + 0.3, gbl[1])])
    ax.text(gbl[0] + 0.35, gbl[1], r"DRAIN$_\mathrm{BL}$", ha="left", va="center", fontsize=5.2)

    # sensing: BL -> BUF (1.2 V) -> BLD bus -> 8 TDC_SAMPLE flops
    yb = 2.75
    line(ax, [(xbl, yb), (4.85, yb)]); dot(ax, xbl, yb)
    buf(ax, 4.85, yb)
    ax.text(5.05, yb + 0.33, "BUF", fontsize=5, ha="center")
    line(ax, [(5.2, yb), (9.75, yb)], color=aqua)
    ax.text(9.8, yb, "BLD", fontsize=5.5, va="center", color=aqua)
    xs = [6.1, 6.95, 7.8, 9.1]
    for i, x in enumerate(xs):
        box(ax, x - 0.33, 1.55, 0.66, 0.6, "D  Q", fs=4.8)
        line(ax, [(x - 0.18, yb), (x - 0.18, 2.15)], color=aqua); dot(ax, x - 0.18, yb, aqua)
        line(ax, [(x + 0.18, 2.15), (x + 0.18, 2.45)])
        k = ["0", "1", "2", "7"][i]
        ax.text(x + 0.22, 2.48, f"$k$={k}", fontsize=4.6, ha="left", va="bottom")
        line(ax, [(x, 1.55), (x, 0.95)], color=orange)
    ax.text(8.45, 1.85, "···", fontsize=8, ha="center", va="center")
    ax.text(7.6, 3.0, "MEM_OUT[8c+k] (TDC_SAMPLE ×8)", fontsize=5.2, ha="center", va="bottom")

    # delay line: READ -> LS(Vgate) -> 9 buffers on VDEL, 8 taps
    y0 = 0.6
    box(ax, 3.3, y0 - 0.25, 0.75, 0.5, "LS\n" + r"$V_\mathrm{gate}$", fs=5, fc="#dbe8f8", ec=blue)
    line(ax, [(2.6, y0), (3.3, y0)])
    ax.text(2.55, y0, "READ", fontsize=5.5, ha="right", va="center")
    line(ax, [(4.05, y0), (4.6, y0)], color=blue)
    bx = [4.6, 5.4, 6.3, 7.15, 8.6]
    for x in bx:
        buf(ax, x, y0, s=0.18, fc="#fbe3d9", ec=orange)
    for a, b in zip(bx[:-1], bx[1:]):
        line(ax, [(a + 0.29, y0), (b, y0)], color=orange)
    for x in xs:
        line(ax, [(x, y0), (x, 0.95)], color=orange); dot(ax, x, y0, orange)
    ax.text(8.15, y0, "···", fontsize=8, ha="center", va="center", color=orange)
    ax.text(6.6, y0 - 0.32, r"TDC_DELAY ($V_\mathrm{DEL}$), CLK_IN[7:0]", fontsize=5.2, ha="center",
            va="top", color=S.INK)
    ax.text(0.75, 7.1, "column c (×64)", fontsize=6, weight="bold", va="center")


def timing(ax):
    """Idealised read sequence: precharge -> settle -> DRAIN_SL -> READ, LRS vs HRS bitline."""
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.4, 6.4)
    ax.axis("off")
    rows = [("PWR_EN", [(0, 0), (0.6, 1), (2.6, 0)]),
            ("WLS→WL", [(0, 0), (2.8, 1)]),
            (r"DRAIN$_\mathrm{SL}$", [(0, 1), (0.6, 0), (5.2, 1)]),
            ("READ", [(0, 0), (6.4, 1)])]
    y = 5.6
    for name, ev in rows:
        xs, ys = [], []
        for i, (t, v) in enumerate(ev):
            if i:
                xs.append(t); ys.append(ys[-1])
            xs.append(t); ys.append(v)
        xs.append(9.8); ys.append(ys[-1])
        ax.plot(xs, [y + 0.55 * v for v in ys], color=S.INK, lw=0.9, drawstyle="default")
        ax.text(-0.1, y + 0.25, name, fontsize=5.5, ha="right", va="center")
        y -= 0.95
    # bitline
    t = np.linspace(0, 9.8, 400)
    def bl(tau):
        v = np.where(t < 0.6, 0.0, np.where(t < 2.6, 1.0, 1.0))
        v = np.where(t >= 2.8, 1.0 - 0.15 * (1 - np.exp(-(t - 2.8) / 3)), v)
        d = t >= 5.2
        v[d] = v[d][0] * np.exp(-(t[d] - 5.2) / tau)
        return v
    yb = 0.0
    ax.plot(t, yb + 1.6 * bl(0.35), color=S.BLUE, lw=1.1)
    ax.plot(t, yb + 1.6 * bl(4.0), color=S.ORANGE, lw=1.1)
    ax.text(-0.1, yb + 0.8, "BL", fontsize=5.5, ha="right", va="center")
    ax.axhline(yb + 0.8, xmin=0.5, xmax=0.98, color=S.INK2, lw=0.5, ls=(0, (3, 2)))
    ax.axvspan(6.6, 7.3, ymin=0.0, ymax=0.97, color=S.AQUA, alpha=0.35, lw=0)
    ax.text(6.95, 6.25, "taps", fontsize=5.2, ha="center", va="bottom")
    ax.text(7.4, yb + 0.15, "LRS → 00000000", fontsize=5.2, color=S.BLUE, va="bottom")
    ax.text(7.4, yb + 1.22, "HRS → 11111111", fontsize=5.2, color=S.ORANGE, va="bottom")
    for x0, x1, lab in ((0.6, 2.6, "precharge"), (2.8, 5.2, "settle"), (5.2, 6.4, "offset")):
        ax.annotate("", xy=(x0, -0.3), xytext=(x1, -0.3),
                    arrowprops=dict(arrowstyle="<->", lw=0.5, color=S.INK2))
        ax.text((x0 + x1) / 2, -0.38, lab, fontsize=5, ha="center", va="top", color=S.INK2)


def main():
    S.setup()
    fig = plt.figure(figsize=(S.COL_W, 2.75))
    ax1 = fig.add_axes([0.0, 0.27, 1.0, 0.73])
    ax2 = fig.add_axes([0.17, 0.02, 0.8, 0.235])
    schematic(ax1)
    timing(ax2)
    fig.text(0.0, 0.985, "(a)", fontsize=8, weight="bold", va="top")
    fig.text(0.0, 0.265, "(b)", fontsize=8, weight="bold", va="top")
    S.save(fig, "schematic")


if __name__ == "__main__":
    main()
