"""Fig. 4 (full width), supply sweep at Vdrain/Vgate/VDEL in 0.8-1.0 V with settle_drain:
(a) BL crossing time vs k at Vdrain 1.0 V for three Vgate (HRS 1 M solid, 200 k dashed) with the
    TDC window positions of Vgate 0.8 V; (b) NOR margin over (Vdrain, Vgate), HRS 1 M, best VDEL/offset;
(c) popcount levels, same; (d) read disturb (V_RRAM, I_cell) vs Vgate.
Also writes paper/tab_pim.tex: best operating point per operation."""
import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import style as S

RUNS = S.PIM_RUNS
VD = [0.8, 0.9, 1.0]
VG = [0.8, 0.9, 1.0]
VGC = {0.8: S.BLUE, 0.9: S.AQUA, 1.0: S.ORANGE}


def load_codes():
    rows = list(csv.DictReader(open(RUNS / "sweep_codes.csv")))
    for r in rows:
        for k in ("vdrain", "vgate", "vdel", "vrram_max_V", "icell_max_uA", "t0_ns", "t8_ns"):
            r[k] = float(r[k])
        for k in ("nor", "maj", "levels", "offset_ns"):
            r[k] = int(r[k])
        r["read"] = int(r["read"]) if r["read"] != "" else None
    return rows


def sw8(vd, vg, rh):
    tag = f"sw8_vd{vd:.1f}_vg{vg:.1f}_rh{rh}".replace(".", "")
    tag = f"sw8_vd{str(vd).replace('.', '')}_vg{str(vg).replace('.', '')}_rh{rh}"
    return sorted(csv.DictReader(open(RUNS / f"{tag}.csv")), key=lambda r: int(r["k"]))


def taps(vg, vdel, rh="1M", vd=1.0):
    tag = f"sw1_vd{str(vd).replace('.', '')}_vg{str(vg).replace('.', '')}_vdel{str(vdel).replace('.', '')}_rh{rh}"
    r = next(csv.DictReader(open(RUNS / f"{tag}.csv")))
    return [float(t) for t in r["taps_after_edge_ns"].split()]


def best(rows, key, rh=None):
    c = [r for r in rows if r[key] is not None and (rh is None or r["rh"] == rh)]
    return max(c, key=lambda r: (r[key], -r["vrram_max_V"], -r["icell_max_uA"]))


def heat(ax, rows, key, rh, title, vmax):
    M = np.zeros((3, 3))
    for i, vd in enumerate(VD):
        for j, vg in enumerate(VG):
            M[i, j] = max(r[key] for r in rows if r["rh"] == rh and r["vdrain"] == vd and r["vgate"] == vg)
    cmap = ListedColormap(S.SEQ_BLUE)
    ax.imshow(M, cmap=cmap, vmin=0, vmax=vmax, origin="lower", aspect="auto")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{int(M[i, j])}", ha="center", va="center", fontsize=7,
                    color="white" if M[i, j] > vmax * 0.55 else S.INK)
    ax.set_xticks(range(3)), ax.set_xticklabels([f"{v:.1f}" for v in VG])
    ax.set_yticks(range(3)), ax.set_yticklabels([f"{v:.1f}" for v in VD])
    ax.set_xlabel(r"$V_\mathrm{gate}$ (V)")
    ax.set_ylabel(r"$V_\mathrm{drain}$ (V)")
    ax.grid(False)
    ax.text(0.58, 1.02, title, transform=ax.transAxes, ha="center", va="bottom", fontsize=6.2, color=S.INK2)


def main():
    S.setup()
    rows = load_codes()
    fig, axs = plt.subplots(1, 4, figsize=(S.PAGE_W, 1.9), gridspec_kw=dict(width_ratios=[1.35, 0.85, 0.85, 1.1]))
    ax, bx, cx, dx = axs

    # (a) crossing time vs k at Vdrain 1.0 V
    for vg in VG:
        for rh, ls in (("1M", "-"), ("200k", (0, (3, 1.5)))):
            d = sw8(1.0, vg, rh)
            ax.plot([int(r["k"]) for r in d], [float(r["bl_cross_after_drain_ns"]) for r in d],
                    color=VGC[vg], ls=ls, marker="o" if rh == "1M" else "s", ms=2.6, lw=1.1)
    for off, lab in ((0, "window +0"), (10, "+10 ns")):
        t = taps(0.8, 0.8)
        ax.axhspan(10 + off + t[0], 10 + off + t[-1], color=S.MUTED, alpha=0.18, lw=0)
        ax.text(0.1 if off else 8.1, 10 + off + t[0] + 0.2, lab, fontsize=5.2, color=S.INK2,
                ha="left" if off else "right", va="bottom")
    for vg in VG:
        ax.plot([], [], color=VGC[vg], lw=1.4, label=rf"$V_\mathrm{{gate}}$ {vg:.1f} V")
    ax.plot([], [], color=S.INK2, ls="-", marker="o", ms=2.6, lw=1.1, label=r"HRS 1 M$\Omega$ (ideal)")
    ax.plot([], [], color=S.INK2, ls=(0, (3, 1.5)), marker="s", ms=2.6, lw=1.1, label=r"HRS 200 k$\Omega$")
    ax.legend(loc="upper right", fontsize=5.2, handlelength=2.0, borderaxespad=0.2, ncol=1)
    ax.set_xlabel(r"LRS cells $k$ of 8 open rows")
    ax.set_ylabel("BL crossing time (ns)")
    ax.set_xticks(range(0, 9, 2))
    ax.set_title("(a)", loc="left", x=-0.22, fontsize=8, weight="bold")

    heat(bx, rows, "nor", "1M", r"NOR margin (taps), HRS 1 M$\Omega$, ideal", 8)
    bx.set_title("(b)", loc="left", x=-0.3, fontsize=8, weight="bold")
    heat(cx, rows, "nor", "200k", r"NOR margin (taps), HRS 200 k$\Omega$", 8)
    cx.set_title("(c)", loc="left", x=-0.3, fontsize=8, weight="bold")

    # (d) disturb vs Vgate (max over k, Vdrain 1.0 V)
    for rh, ls, m in (("1M", "-", "o"), ("200k", (0, (3, 1.5)), "s")):
        vr = [max(r["vrram_max_V"] for r in rows if r["rh"] == rh and r["vgate"] == vg and r["vdrain"] == 1.0) for vg in VG]
        ic = [max(r["icell_max_uA"] for r in rows if r["rh"] == rh and r["vgate"] == vg and r["vdrain"] == 1.0) for vg in VG]
        dx.plot(VG, vr, color=S.BLUE if rh == "1M" else S.ORANGE, ls="-", marker=m, ms=3, lw=1.2,
                label=r"HRS 1 M$\Omega$ (ideal)" if rh == "1M" else r"HRS 200 k$\Omega$")
    dx.axhline(0.2, color=S.INK2, lw=0.6, ls=(0, (2, 2)))
    dx.text(0.995, 0.205, "IHP read 0.2 V", fontsize=5.4, color=S.INK2, va="bottom", ha="right")
    dx.set_xlabel(r"$V_\mathrm{gate}$ (V)")
    dx.set_ylabel(r"peak $V_\mathrm{RRAM}$ during read (V)")
    dx.set_xticks(VG)
    dx.set_ylim(0, 0.3)
    dx.legend(loc="upper left", fontsize=5.4, handlelength=1.6, borderaxespad=0.2)
    dx.text(0.97, 0.03, r"$I_\mathrm{cell}$ 0.8–3 µA", transform=dx.transAxes, fontsize=5.6, color=S.INK2,
            ha="right", va="bottom")
    dx.set_title("(d)", loc="left", x=-0.3, fontsize=8, weight="bold")

    fig.tight_layout(w_pad=0.9)
    S.save(fig, "sweep")

    # Table: best operating point per operation; 200 k = top of IHP's HRS range, 1 M = ideal case.
    # Rows carry simulated codes when a confirming transient cf_<tag> exists, else computed (marked *).
    rows = [r for r in rows if r["rh"] in ("200k", "1M")]
    lines = [r"\begin{tabular}{@{}lccclcc@{}}", r"\toprule",
             r"op. & $\Vd/\Vg/\Vdel$ & off. & codes $c(k)$ & margin & $V_\mathrm{RRAM}$/$I_\mathrm{cell}$\\",
             r" & (V) & (ns) & $k=0\ldots8$ & (taps) & (V/\si{\micro\ampere})\\"]
    def fmt(op, r, margin, codes):
        return (f"{op} & {r['vdrain']:.1f}/{r['vgate']:.1f}/{r['vdel']:.1f} & {r['offset_ns']} & "
                f"{codes} & {margin} & {r['vrram_max_V']:.2f}/{r['icell_max_uA']:.1f}\\\\")
    def cf_tag(r):
        f = lambda v: str(v).replace(".", "")
        return f"cf_vd{f(r['vdrain'])}_vg{f(r['vgate'])}_vdel{f(r['vdel'])}_rh{r['rh']}_o{r['offset_ns']}"
    missing = []
    def row(op, key, rh, nrows8=True):
        b = best(rows, key, rh)
        if not nrows8:
            return fmt(op, b, b["read"], sw1_codes(b) + " (H,L)")
        cf = RUNS / f"{cf_tag(b)}.csv"
        if cf.exists():
            c = [int(x["ones"]) for x in sorted(csv.DictReader(open(cf)), key=lambda x: int(x["k"]))]
            star = ""
        else:
            c = [int(v) for v in b["codes"].split()]
            star = "*"
            missing.append(b)
        m = {"nor": c[0] - c[1], "maj": c[4] - c[5], "levels": f"{len(set(c))} codes"}[key]
        return fmt(op, b, f"{m}{star}", " ".join(map(str, c)))
    for rh, head in (("200k", r"\multicolumn{6}{@{}l}{\textit{HRS 200\,k$\Omega$ (top of IHP's range)}}\\"),
                     ("1M", r"\multicolumn{6}{@{}l}{\textit{HRS 1\,M$\Omega$ (ideal case)}}\\")):
        lines += [r"\midrule", head]
        if rh == "200k":
            lines.append(row("read, 1 row", "read", rh, nrows8=False))
        lines.append(row("NOR", "nor", rh))
        lines.append(row("majority", "maj", rh))
        lines.append(row("popcount", "levels", rh))
    for b in missing:
        f = lambda v: str(v)
        print(f"NEED CF: --tag {cf_tag(b)} --rh {b['rh']} --vdrain {b['vdrain']} --vgate {b['vgate']} "
              f"--vdel {b['vdel']} --drain-first {b['offset_ns'] // 10}")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (Path(__file__).resolve().parent.parent / "paper" / "tab_pim.tex").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[5:-2]))


def sw1_codes(r):
    """single-row codes (HRS, LRS) at the row's setting: recompute from the sw1 crossing and taps."""
    tag = f"sw1_vd{str(r['vdrain']).replace('.', '')}_vg{str(r['vgate']).replace('.', '')}_vdel{str(r['vdel']).replace('.', '')}_rh{r['rh']}"
    d = sorted(csv.DictReader(open(RUNS / f"{tag}.csv")), key=lambda x: int(x["k"]))
    t = [float(x) for x in d[0]["taps_after_edge_ns"].split()]
    out = []
    for x in d:
        tc = float(x["bl_cross_after_drain_ns"])
        out.append(sum(1 for tt in t if 10 + r["offset_ns"] + tt < tc + 0.6))
    return f"{out[0]}, {out[1]}"


if __name__ == "__main__":
    main()
