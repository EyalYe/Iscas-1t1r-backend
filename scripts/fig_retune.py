"""Retune figure (column width): decision margin vs temperature (tt) for the single-row read, the 8-row
NOR and the 8-row majority at 200 k, (i) at the Table I setting fixed at 27 C and (ii) after the host's
search over Vgate, VDEL and the window offset at each temperature (1t1r-exp/runs/pim: cr_*_tt_* and
rt_* at -40 / 125 C, the pc_ grid at 27 C). Cell resistances follow Zanotti's TCR / Ea with temperature."""
import csv
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import style as S

RUNS = S.PIM_RUNS
DELTA = 0.6
TEMPS = [-40, 27, 125]
VG = ["0.8", "0.9", "1.0"]
VDEL = ["0.8", "0.9", "1.0"]
OPS = [("read", 1, "0.8", (0, 1), "0.8", 20), ("nor8", 8, "0.9", (0, 1), "1.0", 10), ("maj8", 8, "1.0", (4, 5), "1.0", 10)]


def f(v):
    return v.replace(".", "")


def ts(T):
    return "t27" if T == 27 else f"t{T:+d}".replace("+", "p").replace("-", "m")


def load(tag):
    p = RUNS / f"{tag}.csv"
    if not p.exists():
        return None
    rows = sorted(csv.DictReader(open(p)), key=lambda r: int(r["k"]))
    return {int(r["k"]): (float(r["bl_cross_after_drain_ns"] or "nan"), [float(x) for x in r["taps_after_edge_ns"].split()], int(r["ones"]))
            for r in rows if r["bl_cross_after_drain_ns"]}


def code(t, taps, off):
    return sum(1 for x in taps if 10 + off + x < t + DELTA)


def taps_at(T, vg, vdel):
    d = load(f"pc_sw1_vd08_vg{f(vg)}_vdel{f(vdel)}_rh200k" if T == 27 else f"rt_sw1_vg{f(vg)}_vdel{f(vdel)}_{ts(T)}")
    return d[0][1] if d and 0 in d else None


def times(op, n, vd, T, vg):
    """list of crossing-time dicts {k: t} of the op's runs at (T, vg): at 27 C the pc_ grid over Vdrain,
    at -40 / 125 C the cr_ (Vg 0.8, the op's Vdrain) and rt_ runs (Vg 0.9 / 1.0, and Vdrain alternatives at Vg 0.8)."""
    out = []
    if n == 1:
        d = load(f"pc_sw1_vd08_vg{f(vg)}_vdel10_rh200k" if T == 27 else f"rt_sw1_vg{f(vg)}_vdel10_{ts(T)}")
        return [{k: v[0] for k, v in d.items()}] if d else []
    if T == 27:
        tags = [f"pc_sw8_vd{f(v)}_vg{f(vg)}_rh200k" for v in [vd] + [x for x in ("0.8", "0.9", "1.0") if x != vd]]
    elif vg == "0.8":
        tags = [f"cr_{op}_tt_{ts(T)}"] + [f"rt_{op}_vd{f(v)}_{ts(T)}" for v in ("0.8", "0.9", "1.0")]
    else:
        tags = [f"rt_{op}_vg{f(vg)}_{ts(T)}"]
    for tag in tags:
        d = load(tag)
        if d:
            out.append({k: v[0] for k, v in d.items()})
    return out


def main():
    S.setup()
    res = {}
    for op, n, vd, (k0, k1), vdel_fix, off_fix in OPS:
        for T in TEMPS:
            # fixed: Table I setting (Vg 0.8, its VDEL and offset) with this temperature's tap table
            tl = times(op, n, vd, T, "0.8"); taps = taps_at(T, "0.8", vdel_fix)
            # fixed: the Table I run (first candidate: the op's own Vdrain) at the fixed VDEL and offset
            t = tl[0] if tl else None
            fixed = code(t[k0], taps, off_fix) - code(t[k1], taps, off_fix) if t and taps and k0 in t and k1 in t else float("nan")
            best = 0
            for vg in VG:
                for t in times(op, n, vd, T, vg):
                    if k0 not in t or k1 not in t:
                        continue
                    for vdel in VDEL:
                        taps = taps_at(T, vg, vdel)
                        if not taps:
                            continue
                        for off in range(-30, 101, 10):
                            best = max(best, code(t[k0], taps, off) - code(t[k1], taps, off))
            res[(op, T)] = (max(fixed, 0) if fixed == fixed else float("nan"), best)
            print(f"{op:5s} {T:>4} C: fixed {res[(op, T)][0]}  retuned {best}")
    fig, ax = plt.subplots(figsize=(S.COL_W, 1.25))
    labs = {"read": "read, 1 row", "nor8": "NOR, 8 rows", "maj8": "majority, 8 rows"}
    cols = {"read": S.GREEN, "nor8": S.BLUE, "maj8": S.ORANGE}
    for op, *_ in OPS:
        ax.plot(TEMPS, [res[(op, T)][1] for T in TEMPS], color=cols[op], marker="o", ms=3, lw=1.2, label=f"{labs[op]}, re-tuned")
        ax.plot(TEMPS, [res[(op, T)][0] for T in TEMPS], color=cols[op], marker="x", ms=3.5, lw=0.8, ls=(0, (2, 1.5)), label=f"{labs[op]}, fixed")
    ax.set_xticks(TEMPS), ax.set_xlabel("temperature (°C)"), ax.set_ylabel("margin (taps)")
    ax.set_ylim(-0.4, 8.6), ax.set_yticks(range(0, 9, 2))
    ax.legend(ncol=1, fontsize=5.4, loc="center left", bbox_to_anchor=(1.01, 0.5), handlelength=1.8,
              labelspacing=0.25, borderaxespad=0.0, frameon=False)
    ax.set_xlim(-55, 140)
    fig.tight_layout(rect=(0, 0, 0.72, 1))
    S.save(fig, "retune")
    with open(RUNS / "retune_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["op", "T_C", "margin_fixed", "margin_retuned"])
        for (op, T), (a, b) in res.items():
            w.writerow([op, T, a, b])


if __name__ == "__main__":
    main()
