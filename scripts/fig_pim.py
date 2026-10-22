"""Fig. 4 (full width): multi-row (PiM) read on the slice, n rows open, k LRS (9 k) + n-k HRS cells.
(a) BL crossing time vs k; (b) TDC code vs k at Vgate 1.5 V for several VDEL; (c) codes at Vgate 1.0 V
and at HRS 1 M; (d) fan-in 4 vs 8 (majority decision)."""
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import style as S

RUNS = S.PIM_RUNS


def load(tag):
    p = RUNS / f"{tag}.csv"
    if not p.exists():
        return []
    with open(p) as f:
        return sorted(csv.DictReader(f), key=lambda r: int(r["k"]))


def fnum(v):
    return float(v) if v not in ("", None) else float("nan")


def codes(ax, tag, color, marker, label, ls="-"):
    d = load(tag)
    if d:
        ax.plot([int(r["k"]) for r in d], [int(r["ones"]) for r in d], color=color, marker=marker,
                ms=3, lw=1.2, ls=ls, label=label)


def code_axes(ax, n=8):
    ax.set_xlabel(r"LRS cells $k$")
    ax.set_ylabel("TDC code (taps high)")
    ax.set_ylim(-0.5, 8.6)
    ax.set_yticks(range(0, 9, 2))
    ax.set_xticks(range(0, n + 1, 2 if n == 8 else 1))
    ax.set_xlim(-0.3, n + 0.3)


def main():
    S.setup()
    fig, axs = plt.subplots(1, 4, figsize=(S.PAGE_W, 1.85))
    ax, bx, cx, dx = axs

    # (a) analog crossing time vs k
    series = [("vg15_rh250k", S.ORANGE, "-", "o", r"HRS 250\,k, $V_\mathrm{g}$ 1.5 V"),
              ("vg15_rh25k", S.BLUE, "-", "o", r"HRS 25\,k, $V_\mathrm{g}$ 1.5 V"),
              ("vg10_rh250k", S.ORANGE, (0, (3, 1.5)), "s", r"HRS 250\,k, $V_\mathrm{g}$ 1.0 V"),
              ("vg10_rh25k", S.BLUE, (0, (3, 1.5)), "s", r"HRS 25\,k, $V_\mathrm{g}$ 1.0 V")]
    for tag, c, ls, m, lab in series:
        d = load(tag)
        if d:
            ax.plot([int(r["k"]) for r in d], [fnum(r["bl_cross_after_drain_ns"]) for r in d],
                    color=c, ls=ls, marker=m, ms=3, lw=1.2, label=lab)
    ax.set_xlabel(r"LRS cells $k$ of 8 open rows")
    ax.set_ylabel("BL crossing time (ns)")
    ax.set_xticks(range(0, 9, 2))
    for x, y, t, c in ((0.35, 7.75, "250k, 1.0 V", S.ORANGE), (0.35, 5.5, "25k, 1.0 V", S.BLUE),
                       (0.35, 3.45, "250k, 1.5 V", S.ORANGE), (3.0, 1.75, "25k, 1.5 V", S.BLUE)):
        ax.text(x, y, t, fontsize=5.6, color=c, va="center")
    ax.text(8, 7.75, r"HRS, $V_\mathrm{gate}$", fontsize=5.6, color=S.INK2, ha="right", va="center")
    ax.set_ylim(1.4, 8.3)
    ax.set_title("(a)", loc="left", x=-0.3, fontsize=8, weight="bold")

    # (b) codes vs k, Vgate 1.5 V, HRS 250 k, VDEL sweep
    codes(bx, "vg15_rh250k", S.MUTED, "^", "1.2 V")
    codes(bx, "vg15_rh250k_vdel08", S.BLUE, "o", "0.8 V")
    codes(bx, "vg15_rh250k_vdel075", S.AQUA, "D", "0.75 V")
    codes(bx, "vg15_rh250k_vdel07", S.ORANGE, "s", "0.7 V")
    code_axes(bx)
    bx.legend(title=r"$V_\mathrm{DEL}$", loc="lower left", fontsize=5.4, title_fontsize=5.6,
              borderaxespad=0.2, handlelength=1.4)
    bx.text(0.97, 0.04, r"HRS 250 k$\Omega$, $V_\mathrm{gate}$ 1.5 V", transform=bx.transAxes,
            fontsize=5.6, ha="right", va="bottom", color=S.INK2)
    bx.set_title("(b)", loc="left", x=-0.3, fontsize=8, weight="bold")

    # (c) codes at Vgate 1.0 V (long discharge) and at HRS 1 M
    codes(cx, "vg08_rh250k_vdel07_d1", S.BLUE, "o", r"250 k$\Omega$, +10 ns")
    codes(cx, "vg08_rh1M_vdel07_d1", S.ORANGE, "s", r"1 M$\Omega$, +10 ns")
    codes(cx, "vg08_rh1M_vdel07_d2", S.ORANGE, "D", r"1 M$\Omega$, +20 ns", ls=(0, (3, 1.5)))
    code_axes(cx)
    cx.axvline(4.5, color=S.INK2, lw=0.6, ls=(0, (1, 1.5)))
    cx.text(4.6, 2.3, "maj.\n$n$=8", fontsize=5.2, color=S.INK2, va="top")
    cx.legend(title="HRS, read offset", loc="center right", fontsize=5.2, title_fontsize=5.4,
              borderaxespad=0.2, handlelength=1.6)
    cx.text(0.97, 0.97, r"$V_\mathrm{gate}$ 0.8 V, $V_\mathrm{DEL}$ 0.7 V", transform=cx.transAxes, fontsize=5.6,
            ha="right", va="top", color=S.INK2)
    cx.set_title("(c)", loc="left", x=-0.3, fontsize=8, weight="bold")

    # (d) fan-in 4 vs 8 at Vgate 1.5, HRS 250k, VDEL 0.8: majority decision
    codes(dx, "vg15_rh250k_vdel08", S.BLUE, "o", r"$n=8$, 0.8 V")
    codes(dx, "n4_vg15_rh250k_vdel08", S.ORANGE, "s", r"$n=4$, 0.8 V")
    codes(dx, "n4_vg15_rh250k_vdel07", S.ORANGE, "D", r"$n=4$, 0.7 V", ls=(0, (3, 1.5)))
    code_axes(dx)
    dx.axvline(4.5, color=S.BLUE, lw=0.6, ls=(0, (2, 2)))
    dx.axvline(2.5, color=S.ORANGE, lw=0.6, ls=(0, (2, 2)))
    dx.text(4.6, 7.4, "maj.\n$n$=8", fontsize=5.2, color=S.BLUE, va="top")
    dx.text(2.6, 7.4, "maj.\n$n$=4", fontsize=5.2, color=S.ORANGE, va="top")
    dx.legend(title=r"fan-in, $V_\mathrm{DEL}$", loc="lower right", fontsize=5.2, title_fontsize=5.4,
              borderaxespad=0.2, handlelength=1.6)
    dx_unused_text = lambda *a, **k: None
    dx_unused_text(0.97, 0.04, r"HRS 250 k$\Omega$, $V_\mathrm{gate}$ 1.5 V", transform=dx.transAxes,
            fontsize=5.6, ha="right", va="bottom", color=S.INK2)
    dx.set_title("(d)", loc="left", x=-0.3, fontsize=8, weight="bold")

    fig.tight_layout(w_pad=1.0)
    S.save(fig, "pim")


if __name__ == "__main__":
    main()
