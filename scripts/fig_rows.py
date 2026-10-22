"""Rows figure (column width; Fig. 4 in the trimmed paper): row-count sweep (1t1r-exp/runs/pim/rw_n*, rwx_*, rows_summary.csv).
(a) best NOR / majority margin vs rows open at Vgate 0.8 V, 200 k and 1 M (ideal); hollow markers beyond
8 rows (written to 1t1r-exp/runs/pim/rows_summary_vg08.csv).
(b) crossing-time separation behind each decision vs rows open (largest over the simulated
supplies at Vgate 0.8 V), with the tap pitch of the delay line."""
import csv
from collections import defaultdict
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import style as S
sys.path.insert(0, str(S.EXP / "pim"))
import rows_analyze as A  # noqa: E402  (the experiment repo's analysis)

RUNS = S.PIM_RUNS
NS = [2, 3, 4, 5, 6, 7, 8, 16, 24, 32, 48, 64]
HRS = [("200k", r"200 k$\Omega$", "-", "o"), ("1M", r"1 M$\Omega$ (ideal)", (0, (3, 1.5)), "D")]
OPS = [("nor", "NOR", S.BLUE), ("maj", "majority", S.ORANGE)]


def summary():
    """(op, rh, n) -> best margin over the runs at Vgate 0.8 V (rows_analyze arithmetic)."""
    taps = A.tap_tables()
    best = {}
    for p in sorted(RUNS.glob("rw_n*.csv")) + sorted(RUNS.glob("rwx_*.csv")):
        run = A.load(p)
        if run["vg"] != 0.8:
            continue
        for op, (mg, (vdel, off, codes)) in A.margins(run, taps).items():
            key = (op, run["rh"], run["n"])
            if mg > best.get(key, (-99,))[0]:
                best[key] = (mg, run["vd"], vdel, off, codes, run["tag"])
    with open(RUNS / "rows_summary_vg08.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["op", "rh", "n", "margin", "vd", "vdel", "off", "codes", "tag"])
        for (op, rh, n), v in sorted(best.items()):
            w.writerow([op, rh, n, *v])
    return {k: v[0] for k, v in best.items()}


def separations():
    """(op, rh, n) -> largest crossing-time step (ns) behind the decision, over runs at Vgate 0.8 V."""
    sep = defaultdict(float)
    for p in sorted(RUNS.glob("rw_n*.csv")) + sorted(RUNS.glob("rwx_*.csv")):
        rows = list(csv.DictReader(open(p)))
        if float(rows[0]["vgate"]) != 0.8:
            continue
        t = {int(r["k"]): float(r["bl_cross_after_drain_ns"]) for r in rows}
        n, rh = int(rows[0]["nrows"]), rows[0]["rh"]
        h = n // 2
        if n >= 2 and 0 in t and 1 in t:
            sep[("nor", rh, n)] = max(sep[("nor", rh, n)], t[0] - t[1])
        if n >= 2 and h in t and h + 1 in t:
            sep[("maj", rh, n)] = max(sep[("maj", rh, n)], t[h] - t[h + 1])
    return sep


def main():
    S.setup()
    m, sep = summary(), separations()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(S.COL_W, 1.45))
    for op, olab, c in OPS:
        for rh, rlab, ls, mk in HRS:
            ns = [n for n in NS if (op, rh, n) in m]
            ax.plot(ns, [m[(op, rh, n)] for n in ns], color=c, ls=ls, lw=1.0)
            for n in ns:
                ax.plot(n, m[(op, rh, n)], marker=mk, ms=2.8, color=c, mfc=c if n <= 8 else "white", mew=0.7)
            ns = [n for n in NS if sep.get((op, rh, n), 0) > 0]
            bx.plot(ns, [sep[(op, rh, n)] for n in ns], color=c, ls=ls, lw=1.0, marker=mk, ms=2.4,
                    label=f"{olab}, {rlab}")
    for a in (ax, bx):
        a.set_xscale("log", base=2)
        a.set_xticks([2, 4, 8, 16, 32, 64]), a.set_xticklabels(["2", "4", "8", "16", "32", "64"])
        a.minorticks_off()
        a.axvspan(8.6, 70, color=S.MUTED, alpha=0.12, lw=0)
        a.set_xlabel(r"rows open $n$")
    ax.set_ylim(-0.4, 8.6), ax.set_yticks(range(0, 9, 2))
    ax.set_ylabel("best margin (taps)")
    ax.text(26, 8.3, "beyond\n8 rows", fontsize=5.4, color=S.INK2, ha="center", va="top")
    ax.set_title("(a)", loc="left", x=-0.3, fontsize=8, weight="bold")
    bx.set_yscale("log")
    bx.axhspan(0.17, 0.35, color=S.GREEN, alpha=0.15, lw=0)
    bx.text(2.1, 0.245, "tap pitch", fontsize=5.4, color=S.INK2, va="center")
    bx.set_ylabel("crossing-time step (ns)")
    bx.set_title("(b)", loc="left", x=-0.33, fontsize=8, weight="bold")
    h, l = bx.get_legend_handles_labels()
    fig.tight_layout(w_pad=0.6, rect=(0, 0, 1, 0.92))
    fig.legend(h, l, loc="upper center", ncol=4, fontsize=5.0, handlelength=2.0, columnspacing=0.8,
               labelspacing=0.1, borderaxespad=0.05)
    S.save(fig, "rows")
    for op, _, _ in OPS:
        for rh, *_ in HRS:
            print(op, rh, " ".join(f"{n}:{m.get((op, rh, n))}/{sep.get((op, rh, n), 0):.3f}" for n in NS))


if __name__ == "__main__":
    main()
