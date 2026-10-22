"""Grid figure (Fig. 3 in the trimmed paper) + Table I from the read-supply grid with extracted line capacitance and C_MIM = 10 fF
(1t1r-exp/runs/pim/pc_*, 40-cycle precharge, settle-drain) and the confirming transients (gcf_*):
(a) BL crossing time vs k at the best points with the +10 ns window; (b) simulated codes vs k.
The (c), (d) heat maps (best NOR / majority margin over Vdrain x Vgate) were dropped from the paper on 22.10.26;
heat() is kept for reference. Falls back to paper/results/ when the SPICE run directory is absent."""
import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import style as S

RUNS = S.PIM_RUNS
_PAPER = Path(__file__).resolve().parent.parent / "paper" / "results"
if not RUNS.exists():  # backup copies: gcf_* in table1_grid/, pc_* in grid/
    class _Fallback:
        def __truediv__(self, name):
            for d in ("table1_grid", "grid"):
                if (_PAPER / d / name).exists():
                    return _PAPER / d / name
            return _PAPER / "grid" / name
    RUNS = _Fallback()
VD = [0.8, 0.9, 1.0]
VG = [0.8, 0.9, 1.0]


def load(tag):
    return sorted(csv.DictReader(open(RUNS / f"{tag}.csv")), key=lambda r: int(r["k"]))


def col(d, key):
    return [float(r[key]) if r[key] not in ("", None) else float("inf") for r in d]


def grid_rows():
    rows = list(csv.DictReader(open(RUNS / "pc_sweep_codes.csv")))
    for r in rows:
        for k in ("vdrain", "vgate", "vdel"):
            r[k] = float(r[k])
        for k in ("nor", "maj", "offset_ns"):
            r[k] = int(r[k])
    return rows


def heat(ax, rows, key, rh, title, vmax=8):
    M = np.zeros((3, 3))
    for i, vd in enumerate(VD):
        for j, vg in enumerate(VG):
            M[i, j] = max(r[key] for r in rows if r["rh"] == rh and r["vdrain"] == vd and r["vgate"] == vg)
    ax.imshow(M, cmap=ListedColormap(S.SEQ_BLUE), vmin=0, vmax=vmax, origin="lower", aspect="auto")
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


CONF = [  # tag, label, colour, marker, line style
    ("gcf_nor_200k", r"200 k$\Omega$, 0.9/0.8 V", S.BLUE, "s", "-"),
    ("gcf_maj_200k", r"200 k$\Omega$, 1.0/0.8 V", S.BLUE, "o", (0, (3, 1.5))),
    ("gcf_nor_1M", r"1 M$\Omega$ (deep reset), 0.8/0.8 V", S.ORANGE, "^", (0, (3, 1.5))),
    ("gcf_maj_1M", r"1 M$\Omega$ (deep reset), 1.0/0.8 V", S.ORANGE, "D", "-"),
]


def main():
    S.setup()
    rows = grid_rows()
    fig, axs = plt.subplots(1, 2, figsize=(S.COL_W, 1.45), gridspec_kw=dict(width_ratios=[1.15, 1.0]))
    ax, bx = axs
    ks = list(range(9))
    for tag, lab, c, m, ls in CONF:
        d = load(tag)
        ax.plot(ks, col(d, "bl_cross_after_drain_ns"), color=c, marker=m, ms=2.8, lw=1.2, ls=ls, label=lab)
        bx.plot(ks, [int(r["ones"]) for r in d], color=c, marker=m, ms=2.8, lw=1.2, ls=ls, label=lab)
    t = [float(x) for x in load("gcf_maj_200k")[0]["taps_after_edge_ns"].split()]
    ax.axhspan(20 + t[0], 20 + t[-1], color=S.MUTED, alpha=0.22, lw=0)
    ax.text(8.2, 20 + t[-1] + 0.3, "window +10 ns", fontsize=5.2, color=S.INK2, ha="right", va="bottom")
    ax.set_xlabel(r"LRS cells $k$ of 8 open rows")
    ax.set_ylabel("BL crossing time (ns)")
    ax.set_xticks(range(0, 9, 2)), ax.set_ylim(17, 48)
    ax.legend(loc="upper right", fontsize=5.0, handlelength=1.8, borderaxespad=0.2, title=r"HRS, $V_\mathrm{drain}/V_\mathrm{gate}$",
              title_fontsize=5.2)
    ax.set_title("(a)", loc="left", x=-0.22, fontsize=8, weight="bold")
    bx.axvline(4.5, color=S.INK2, lw=0.6, ls=(0, (1, 1.5)))
    bx.text(4.6, 1.4, "maj.", fontsize=5.2, color=S.INK2, va="top")
    bx.set_xlabel(r"LRS cells $k$")
    bx.set_ylabel("TDC code (taps high)")
    bx.set_ylim(-0.5, 8.8), bx.set_yticks(range(0, 9, 2)), bx.set_xticks(range(0, 9, 2))   # legend shared with (a)
    bx.set_title("(b)", loc="left", x=-0.25, fontsize=8, weight="bold")
    fig.tight_layout(w_pad=0.8)
    S.save(fig, "grid")

    # Table I: best point per operation, simulated codes (gcf_*)
    T = [("read, 1 row", "gcf_read_200k", "200\\,k", "0.8/0.8/0.8", 20, "read"),
         ("NOR, 8 rows", "gcf_nor_200k", "200\\,k", "0.9/0.8/1.0", 10, "nor"),
         ("majority, 8 rows", "gcf_maj_200k", "200\\,k", "1.0/0.8/1.0", 10, "maj"),
         ("NOR, 8 rows", "gcf_nor_1M", "1\\,M$^\\dagger$", "0.8/0.8/0.9", 10, "nor"),
         ("majority, 8 rows", "gcf_maj_1M", "1\\,M$^\\dagger$", "1.0/0.8/1.0", 10, "maj")]
    L = [r"\begin{tabular}{@{}lccclcc@{}}", r"\toprule",
         r"op. & HRS & $\Vd/\Vg/\Vdel$ & off. & codes $c(k)$ & margin & $V_\mathrm{RRAM}$/$I_\mathrm{cell}$\\",
         r" & ($\Omega$) & (V) & (ns) & $k=0\ldots8$ & (taps) & (V/\si{\micro\ampere})\\", r"\midrule"]
    for op, tag, rh, sup, off, key in T:
        d = load(tag)
        c = [int(r["ones"]) for r in d]
        vr = max(float(r["vrram_max_V"]) for r in d)
        ic = max(float(r["icell_max_uA"]) for r in d)
        if key == "read":
            codes, m = f"{c[0]}, {c[1]} (HRS, LRS)", c[0] - c[1]
        elif key == "nor":
            codes, m = " ".join(map(str, c)), c[0] - c[1]
        elif key == "maj":
            codes, m = " ".join(map(str, c)), c[4] - c[5]
        else:
            codes, m = " ".join(map(str, c)), f"{len(set(c))} codes"
        L.append(f"{op} & {rh} & {sup} & {off} & {codes} & {m} & {vr:.2f}/{ic:.1f}\\\\")
    L += [r"\midrule",
          r"\multicolumn{7}{@{}l}{direct transients, $C_\mathrm{MIM}=10$\,fF, extracted line capacitance; $^\dagger$deep-reset state; $V_\mathrm{RRAM}$, $I_\mathrm{cell}$: largest cell voltage and current over the row's runs (different cells and instants)}\\",
          r"\bottomrule", r"\end{tabular}"]
    (Path(__file__).resolve().parent.parent / "paper" / "tab_pim.tex").write_text("\n".join(L) + "\n")
    print("\n".join(L[5:-4]))


if __name__ == "__main__":
    main()
