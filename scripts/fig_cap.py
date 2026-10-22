"""Fig. 4 + Table I with the extracted line capacitance and the MEMRES MIM capacitance
(1t1r-exp/runs/pim/cap_*.csv, 40-cycle precharge, settle-drain):
(a) BL crossing time vs k at C_MIM = 10 fF, HRS 1 M (ideal) and 200 k, with the TDC window positions;
(b) codes vs k at the window positions READ_SAMPLE / the read offset can reach;
(c) margins vs C_MIM; (d) single-row read: HRS / LRS crossing vs C_MIM against the window.
Codes at offsets other than the simulated one follow from the crossing times and the tap table
(+0.2 ns calibration, exact on the 270-run calibration set); capcf_*.csv are direct transients."""
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import style as S

RUNS = S.PIM_RUNS
CM = [0, 5, 10, 15]
PTS = {"nor1M": dict(rh="1 M", sup="1.0/0.8/0.8", taps="sw1_vd10_vg08_vdel08_rh1M"),
       "nor200k": dict(rh="200 k", sup="0.8/1.0/0.8", taps="sw1_vd08_vg10_vdel08_rh250k"),
       "rd200k": dict(rh="200 k", sup="0.8/0.8/0.8", taps="sw1_vd08_vg08_vdel08_rh250k")}


def load(tag):
    return sorted(csv.DictReader(open(RUNS / f"{tag}.csv")), key=lambda r: int(r["k"]))


def fnum(v):
    return float(v) if v not in ("", None) else float("inf")


def taps(tag):
    return [float(x) for x in load(tag)[0]["taps_after_edge_ns"].split()]


def tcross(tag):
    return [fnum(r["bl_cross_after_drain_ns"]) for r in load(tag)]


def codes(tc, tp, off):
    return [sum(1 for t in tp if 10 + off + t < c + 0.6) for c in tc]   # 0.6 ns: fit on capcf_* transients


def sim_codes(tag):
    p = RUNS / f"{tag}.csv"
    return [int(r["ones"]) for r in load(tag)] if p.exists() else None


def best(tc, tp, key):
    out = []
    for off in (0, 10, 20, 30, 40):
        c = codes(tc, tp, off)
        m = {"nor": c[0] - c[1], "maj": (c[4] - c[5]) if len(c) == 9 else 0, "lev": len(set(c)),
             "read": c[0] - c[1]}[key]
        out.append((m, off, c))
    return max(out, key=lambda x: (x[0], -x[1]))


def main():
    S.setup()
    fig, axs = plt.subplots(1, 4, figsize=(S.PAGE_W, 1.9), gridspec_kw=dict(width_ratios=[1.3, 1.1, 1.0, 1.0]))
    ax, bx, cx, dx = axs
    tp1 = taps(PTS["nor1M"]["taps"])
    tp2 = taps(PTS["nor200k"]["taps"])

    # (a)
    t1 = tcross("cap_nor1M_cm10"); t2 = tcross("cap_nor200k_cm10"); t1o = tcross("sw8_vd10_vg08_rh1M")
    ks = list(range(9))
    ax.plot(ks, t1, color=S.ORANGE, marker="o", ms=2.8, lw=1.2, label=r"1 M$\Omega$ (ideal), extracted C")
    ax.plot(ks, t1o, color=S.ORANGE, marker="o", ms=2.4, lw=0.9, ls=(0, (2, 1.5)), alpha=0.7,
            label=r"1 M$\Omega$, lumped 20 fF (old)")
    ax.plot(ks, t2, color=S.BLUE, marker="s", ms=2.8, lw=1.2, label=r"200 k$\Omega$, extracted C")
    for off in (10, 20, 30):
        ax.axhspan(10 + off + tp1[0], 10 + off + tp1[-1], color=S.MUTED, alpha=0.18, lw=0)
        ax.text(5.6, 10 + off + tp1[-1] + 0.3, f"+{off} ns", fontsize=5.2, color=S.INK2, ha="left", va="bottom")
    ax.set_xlabel(r"LRS cells $k$ of 8 open rows")
    ax.set_ylabel("BL crossing time (ns)")
    ax.set_xticks(range(0, 9, 2))
    ax.set_ylim(10, 58)
    ax.legend(loc="upper right", fontsize=5.0, handlelength=1.8, borderaxespad=0.2)
    ax.set_title("(a)", loc="left", x=-0.22, fontsize=8, weight="bold")

    # (b) codes
    for off, col, m, ls, lab in ((10, S.ORANGE, "o", "-", r"1 M$\Omega$, +10 ns"),
                                 (20, S.ORANGE, "D", (0, (3, 1.5)), r"1 M$\Omega$, +20 ns")):
        sc = sim_codes(f"capcf_nor1M_cm10_d{off // 10}")
        c = sc if sc else codes(t1, tp1, off)
        bx.plot(ks, c, color=col, marker=m, ms=2.8, lw=1.2, ls=ls, label=lab + ("" if sc else " (calc.)"))
    bx.plot(ks, codes(t2, tp2, 0), color=S.BLUE, marker="s", ms=2.8, lw=1.2, label=r"200 k$\Omega$, +0 ns")
    bx.axvline(4.5, color=S.INK2, lw=0.6, ls=(0, (1, 1.5)))
    bx.text(4.6, 1.6, "maj.", fontsize=5.2, color=S.INK2, va="top")
    bx.set_xlabel(r"LRS cells $k$")
    bx.set_ylabel("TDC code (taps high)")
    bx.set_ylim(-0.5, 12.8), bx.set_yticks(range(0, 9, 2)), bx.set_xticks(range(0, 9, 2))
    bx.legend(loc="upper right", fontsize=5.0, handlelength=1.8, borderaxespad=0.2)
    bx.set_title("(b)", loc="left", x=-0.25, fontsize=8, weight="bold")

    # (c) margins vs C_MIM
    rows = {"NOR 1 M$\\Omega$": ("nor1M", "nor", tp1, S.ORANGE, "o", "-"),
            "majority 1 M$\\Omega$": ("nor1M", "maj", tp1, S.ORANGE, "D", (0, (3, 1.5))),
            "NOR 200 k$\\Omega$": ("nor200k", "nor", tp2, S.BLUE, "s", "-")}
    for lab, (pt, key, tp, col, m, ls) in rows.items():
        cx.plot(CM, [best(tcross(f"cap_{pt}_cm{c}"), tp, key)[0] for c in CM], color=col, marker=m, ms=3,
                lw=1.2, ls=ls, label=lab)
    cx.set_xlabel(r"$C_\mathrm{MIM}$ per cell (fF)")
    cx.set_ylabel("margin (taps)")
    cx.set_xticks(CM), cx.set_ylim(-0.5, 8.6), cx.set_yticks(range(0, 9, 2))
    cx.legend(loc="center right", fontsize=5.0, handlelength=1.8, borderaxespad=0.2)
    cx.set_title("(c)", loc="left", x=-0.28, fontsize=8, weight="bold")

    # (d) single-row read
    tp3 = taps(PTS["rd200k"]["taps"])
    th = [tcross(f"cap_rd200k_cm{c}")[0] for c in CM]
    tl = [tcross(f"cap_rd200k_cm{c}")[1] for c in CM]
    dx.plot(CM, th, color=S.ORANGE, marker="o", ms=3, lw=1.2, label=r"HRS 200 k$\Omega$")
    dx.plot(CM, tl, color=S.BLUE, marker="s", ms=3, lw=1.2, label=r"LRS 9 k$\Omega$")
    for off in (20, 30):
        dx.axhspan(10 + off + tp3[0], 10 + off + tp3[-1], color=S.MUTED, alpha=0.18, lw=0)
        dx.text(0.2, 10 + off + tp3[-1] + 0.4, f"+{off} ns", fontsize=5.2, color=S.INK2, ha="left", va="bottom")
    dx.set_xlabel(r"$C_\mathrm{MIM}$ per cell (fF)")
    dx.set_ylabel("BL crossing, single row (ns)")
    dx.set_xticks(CM), dx.set_ylim(20, 56)
    dx.legend(loc="lower right", fontsize=5.0, handlelength=1.6, borderaxespad=0.2)
    dx.set_title("(d)", loc="left", x=-0.28, fontsize=8, weight="bold")
    fig.tight_layout(w_pad=0.8)
    S.save(fig, "cap")

    # Table: margins vs C_MIM at the evaluated points
    L = [r"\begin{tabular}{@{}llcccc@{}}", r"\toprule",
         r"operation & HRS, $\Vd/\Vg/\Vdel$ (V) & \multicolumn{4}{c}{$C_\mathrm{MIM}$ (fF)}\\",
         r"\cmidrule(l){3-6}", r" & & 0 & 5 & 10 & 15\\", r"\midrule"]
    def cells(pt, key, tp, fmt=lambda b: f"{b[0]}"):
        return " & ".join(fmt(best(tcross(f"cap_{pt}_cm{c}"), tp, key)) for c in CM)
    L.append(r"read, 1 row & 200\,k, 0.8/0.8/0.8 & " + cells("rd200k", "read", tp3) + r"\\")
    L.append(r"NOR, 8 rows & 200\,k, 0.8/1.0/0.8 & " + cells("nor200k", "nor", tp2) + r"\\")
    L.append(r"popcount & 200\,k, 0.8/1.0/0.8 & " + cells("nor200k", "lev", tp2, lambda b: f"{b[0]} c.") + r"\\")
    L.append(r"NOR, 8 rows & 1\,M$^\dagger$, 1.0/0.8/0.8 & " + cells("nor1M", "nor", tp1) + r"\\")
    L.append(r"majority-8 & 1\,M$^\dagger$, 1.0/0.8/0.8 & " + cells("nor1M", "maj", tp1) + r"\\")
    L.append(r"popcount & 1\,M$^\dagger$, 1.0/0.8/0.8 & " + cells("nor1M", "lev", tp1, lambda b: f"{b[0]} c.") + r"\\")
    L += [r"\midrule",
          r"\multicolumn{6}{@{}l}{margins in taps at the best READ\_SAMPLE position; c.: distinct codes; $^\dagger$ideal HRS}\\",
          r"\bottomrule", r"\end{tabular}"]
    (Path(__file__).resolve().parent.parent / "paper" / "tab_cap.tex").write_text("\n".join(L) + "\n")
    print("\n".join(L[6:-4]))


if __name__ == "__main__":
    main()
