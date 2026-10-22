"""Read-path characterisation from the 8x8 Spectre slice:
(a) level-shifter delay vs Vgate, (b) TDC blinding at Vgate = 4 V, (c) BL discharge vs R at 1.5 V,
(d) bitline crossing time vs cell resistance (TDC read and discharge-length test)."""
import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter
import style as S

DATA = Path(__file__).resolve().parent.parent / "data"
VTH = 0.6          # BUFJIX1 threshold used by the extraction scripts


def rows(name):
    with open(S.RESULTS / name) as f:
        return list(csv.DictReader(f))


def eng(r):
    return f"{r/1e6:g}M" if r >= 1e6 else f"{r/1e3:g}k"


def panel_ls(ax):
    d = rows("ls_delay_vs_vgate.csv")
    vg = [float(r["vgate_V"]) for r in d]
    ax.semilogy(vg, [float(r["wl_ls_ns"]) for r in d], "o-", color=S.BLUE, ms=3.5, label="WL path")
    ax.semilogy(vg, [float(r["read_ls_ns"]) for r in d], "s-", color=S.ORANGE, ms=3.5, label="READ path")
    ax.axhline(10, color=S.INK2, lw=0.7, ls=(0, (3, 2)))
    ax.text(1.2, 11.5, "1 clock (10 ns)", fontsize=6, color=S.INK2, va="bottom")
    ax.axvspan(3.3, 4.15, color="#f3d9cf", lw=0, zorder=0)
    ax.text(3.72, 0.32, "> HV\nlimit", fontsize=6, color=S.INK2, ha="center", va="bottom")
    ax.set_xlim(1.1, 4.15)
    ax.set_ylim(0.3, 300)
    ax.set_xlabel(r"$V_\mathrm{gate}$ (V)")
    ax.set_ylabel("level-shifter delay (ns)")
    ax.legend(loc="upper left", handlelength=1.6)
    ax.set_title("(a)", loc="left", x=-0.22, fontsize=8, weight="bold")


def panel_blind(ax):
    z = np.load(DATA / "read_code_vgate.npz")
    vals = list(z["values"])
    i = vals.index(4.0)
    t = (z[f"t_{i}"] * 1e9) - 140.0          # READ edge at 140 ns
    m = (t > -5) & (t < 190)
    ax.plot(t[m], z[f"READ_DELAYED_{i}"][m], color=S.ORANGE)
    ax.plot(t[m], z[f"WL_0_{i}"][m], color=S.BLUE)
    ax.plot(t[m], z[f"BL_0_{i}"][m], color=S.INK, lw=1.2)
    ax.axvspan(91.2, 92.2, color=S.AQUA, alpha=0.5, lw=0)
    ax.text(89, 2.55, "TDC taps", fontsize=6, color=S.INK, ha="right", va="center")
    ax.annotate("WL > 0.6 V\nat 126 ns", xy=(126.5, 0.62), xytext=(150, 2.3), fontsize=6, ha="center",
                color=S.INK, arrowprops=dict(arrowstyle="->", lw=0.6, color=S.INK2))
    ax.text(30, 1.32, "BL", fontsize=6.5, color=S.INK)
    ax.text(103, 3.6, "READ_DLY", fontsize=6.5, color=S.ORANGE, ha="right")
    ax.text(162, 3.6, "WL", fontsize=6.5, color=S.BLUE, ha="left")
    ax.set_xlim(-5, 190)
    ax.set_ylim(-0.1, 4.4)
    ax.set_xlabel("time after READ edge (ns)")
    ax.set_ylabel("voltage (V)")
    ax.text(0.02, 0.98, r"$V_\mathrm{gate}=4$ V", transform=ax.transAxes,
            fontsize=6.5, va="top", color=S.INK2)
    ax.set_title("(b)", loc="left", x=-0.22, fontsize=8, weight="bold")


def panel_bl(ax):
    z = np.load(DATA / "read_code_r_vg15_d1.npz")
    vals = list(z["values"])
    for j, r in enumerate(vals):
        t = z[f"t_{j}"] * 1e9 - 150.0         # DRAIN_SL on at 150 ns, READ edge at 160 ns
        m = (t > -4) & (t < 70)
        ax.plot(t[m], z[f"BL_0_{j}"][m], color=S.SEQ_BLUE[j], lw=1.2)
        if r >= 3e5:
            y = float(np.interp(70, t, z[f"BL_0_{j}"]))
            ax.text(71, y, eng(r), fontsize=6, color=S.INK2, va="center")
    ax.text(5.5, 0.08, "3k–100k", fontsize=6, color=S.INK2, va="bottom")
    w0, w1 = 10 + 0.575, 10 + 1.356
    ax.axvspan(w0, w1, color=S.AQUA, alpha=0.6, lw=0)
    ax.text(13, 1.24, "TDC window", fontsize=6, color=S.INK, va="center")
    ax.axhline(VTH, color=S.INK2, lw=0.7, ls=(0, (3, 2)))
    ax.text(26, VTH + 0.02, r"$V_\mathrm{th}$", fontsize=6.5, color=S.INK2, va="bottom")
    ax.set_xlim(-4, 80)
    ax.set_ylim(-0.05, 1.3)
    ax.set_xlabel(r"time after DRAIN$_\mathrm{SL}$ on (ns)")
    ax.set_ylabel("BL voltage (V)")
    ax.set_title("(c)", loc="left", x=-0.22, fontsize=8, weight="bold")


def panel_cross(ax):
    d = rows("read_code_r_vgate1p5_drainfirst1.csv")
    r1 = [float(r["value"]) for r in d]
    t1 = [float(r["bl_fall_after_drain_ns"]) for r in d]
    l = rows("lod_r_vgate1p5.csv")
    r2 = [float(r["value"]) for r in l]
    t2 = [float(r["bl_fall_ns"]) for r in l]
    cyc = [int(r["cycles_to_zero"]) for r in l]
    ax.loglog(r1, t1, "o-", color=S.BLUE, ms=3.5, label="TDC read")
    ax.loglog(r2, t2, "s-", color=S.ORANGE, ms=3.5, label="LOD test")
    for r, t, c in zip(r2, t2, cyc):
        ax.text(r * 1.35, t * 0.8, f"{c}", fontsize=6, color=S.ORANGE, ha="left", va="top")
    ax.text(4.5e7, 2.2, "labels: LOD\ncount (cycles)", fontsize=5.8, color=S.INK2, ha="right")
    ax.axhline(0.46, xmin=0.0, xmax=0.45, color=S.INK2, lw=0.6, ls=(0, (1, 1.5)))
    ax.text(2.2e3, 0.36, "drain-switch floor 0.46 ns", fontsize=5.6, color=S.INK2, va="top")
    ax.axhline(10, color=S.INK2, lw=0.7, ls=(0, (3, 2)))
    ax.text(2.2e3, 12, "READ edge (+10 ns)", fontsize=6, color=S.INK2, va="bottom")
    ax.set_xlim(2e3, 5e7)
    ax.set_ylim(0.2, 3000)
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel(r"cell resistance $R$ ($\Omega$)")
    ax.set_ylabel("BL crossing time (ns)")
    ax.legend(loc="upper left", handlelength=1.6)
    ax.set_title("(d)", loc="left", x=-0.22, fontsize=8, weight="bold")


def main():
    S.setup()
    fig, axs = plt.subplots(1, 4, figsize=(S.PAGE_W, 2.05))
    panel_ls(axs[0])
    panel_blind(axs[1])
    panel_bl(axs[2])
    panel_cross(axs[3])
    fig.tight_layout(w_pad=1.0)
    S.save(fig, "read_char")


if __name__ == "__main__":
    main()
