"""Copy every result CSV the paper shows into paper/results/ and write paper/results/MANIFEST.md
(file -> figure/table/text it feeds, source path, md5). Re-run whenever the paper's data changes.

  python backup_results.py"""
import hashlib
import re
import shutil
from pathlib import Path
import style as S

ROOT = Path(__file__).resolve().parent.parent
RUNS = S.PIM_RUNS
OUT = ROOT / "paper" / "results"
PEX = S.WS / "PEX/memory_1T1R/spice/memory_1T1R_RCC_default.sp"

# (destination subdir, source glob, what it feeds)
ITEMS = [
    ("sec4b_single_row", S.RESULTS / "ls_delay_vs_vgate.csv", "Sec. IV-B text: level-shifter delay 89/126 ns at 4 V, 3.7 ns at 0.8 V"),
    ("sec4b_single_row", S.RESULTS / "read_code_r_vgate1p5_drainfirst1.csv", "single-row read at Vgate 1.5 V (no longer shown; a figure in earlier drafts)"),
    ("sec4b_single_row", S.RESULTS / "lod_r_vgate1p5.csv", "LOD test at Vgate 1.5 V (no longer shown)"),
    ("sec4b_single_row", S.RESULTS / "read_code_vgate0p8-1p5_r100k_drainfirst1.csv", "Sec. IV-B text: 1.1 MOhm access resistance at Vgate 0.8 V"),
    ("table1_grid", RUNS / "gcf_*.csv", "Table I rows and grid figure (a),(b): direct transients at the best points"),
    ("grid", RUNS / "pc_sweep_codes.csv", "grid figure (c),(d): codes/margins for every supply, VDEL and window (computed)"),
    ("grid", RUNS / "pc_sw8_*.csv", "grid raw data, 8 rows open (crossing times)"),
    ("grid", RUNS / "pc_sw1_*.csv", "grid raw data, single row, and the tap tables"),
    ("calibration", RUNS / "capcf_*.csv", "direct transients that fix the 0.6 ns comparison offset"),
    ("cap_sensitivity", RUNS / "cap_*.csv", "Setup text: C_MIM 0-15 fF sensitivity at fixed points"),
    ("precharge", RUNS / "old_pc10_cap_*.csv", "Setup text: 10-cycle precharge leaves BL at 0.5 V (bl_at_drain_V)"),
    ("rows", RUNS / "rw_n*.csv", "rows figure / rows text: 1-8 rows open, every supply (crossing times); 2-row popcount"),
    ("rows", RUNS / "rwx_*.csv", "rows figure / rows text: 16-64 rows open at the best 8-row supplies"),
    ("rows", RUNS / "rows_summary.csv", "best margin per operation, HRS and row count over all supplies (computed)"),
    ("rows", RUNS / "rows_summary_vg08.csv", "rows figure (a) and rows text: best margin at Vgate 0.8 V (computed)"),
    ("rows", RUNS / "rows_points.txt", "phase-2 operating points chosen from phase 1"),    ("spread", RUNS / "mc_spread.csv", "spread text: decision error vs HRS/LRS sigma at the Table I points (mc_spread.py)"),
    ("energy", RUNS / "en_*.csv", "Setup text / Table II: energy per phase and supply, Table I points (pim_popcount --energy)"),
    ("energy", RUNS / "en_summary.csv", "Setup text / Table II: energy per slice access and scaled to the macro (energy_summary.py)"),
    ("hrs_median", RUNS / "hm_sw8_*.csv", "Sec. IV-B text: k-sweeps at HRS 30/60/120 k (contrast at the real HRS)"),
    ("hrs_median", RUNS / "hm_sw1_*.csv", "single-row runs at HRS 30/60/120 k"),
    ("hrs_median", RUNS / "hm_summary.csv", "Sec. IV-B text: margins, contrast, R_acc fit and spread limits per supply and HRS (hrs_analyze.py)"),
    ("hrs_median", RUNS / "_racc" / "deck.scs", "Sec. IV-B text: DC sweep of the access transistor with the cell (3.6:1 contrast)"),
    ("spread_spice", RUNS / "mc_*_s??.csv", "spread text: SPICE Monte Carlo on the cell resistances, NOR-2 and MAJ-4 (stages.py mc)"),
    ("corners", RUNS / "cr_*.csv", "Sec. IV-C text: PSP corners x temperature at the three 200 k points (stages.py corners)"),
    ("corners", RUNS / "hot_*.csv", "hot-storage state (HRS 40 k, LRS 11 k, 125 C)"),
    ("tcad_cmim", S.EXP / "runs/tcad_cmim" / "cmim_e*_des_des.plt", "Setup text: Sentaurus C_MIM 6.8-11.0 fF, TE charge vs voltage (1t1r-exp/tcad)"),
    ("write_energy", RUNS / "wr_*" / "write.csv", "read-disturb text: refresh write energy per pulse (exp_write.py --energy)"),
    ("retune", RUNS / "rt_*.csv", "Fig. 5: per-temperature tap tables and 8-row points at Vgate 0.9/1.0 and other Vdrain (stages.py retune, retune_vd.sh)"),
    ("retune", RUNS / "retune_summary.csv", "Fig. 5: margin fixed vs re-tuned per temperature (fig_retune.py)"),
    ("compact_model_check", RUNS / "va_*.csv", "Setup text: Table I settings with the IHP Verilog-A cell at its two end states (pim_popcount --va)"),
    ("compact_model_check", RUNS / "vr_*.csv", "Setup text: the same settings with resistors of the model's end-state values"),
    ("spread", RUNS / "mc_rows.csv", "spread text: allowed HRS sigma vs rows open, 0.18/sqrt(n) (mc_spread.py --rows)"),
]


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def extracted_caps(dest):
    """BL/SL interconnect capacitance per column from the Quantus netlist (text: 47-62 / 21-36 fF)."""
    unit = {"f": 1e-15, "a": 1e-18, "p": 1e-12, "n": 1e-9}
    want = {f"{w}L{c}M" for w in ("BL", "SL") for c in (0, 31, 63)}
    tot = {k: 0.0 for k in want}
    txt = re.sub(r"\n\+", " ", PEX.read_text())
    for line in txt.split("\n"):
        if not line or line[0] not in "Cc":
            continue
        t = line.split()
        if len(t) < 4:
            continue
        m = re.match(r"([0-9.eE+-]+)([a-zA-Z]*)", t[3])
        v = float(m.group(1)) * unit.get(m.group(2)[:1].lower(), 1)
        for n in (t[1].split("#")[0], t[2].split("#")[0]):
            if n in tot:
                tot[n] += v
    rows = ["net,column,C_fF"] + [f"{k[:2]},{k[3:-1]},{tot[k] * 1e15:.2f}" for k in sorted(tot)]
    dest.write_text("\n".join(rows) + "\n")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    lines = ["# Paper result data (backup)", "",
             "Copies of every CSV behind a figure, table or number in the paper. Regenerate with",
             "`scripts/backup_results.py`. md5 is of the copy.", "",
             "| file | feeds | source | md5 |", "|---|---|---|---|"]
    n = 0
    for sub, src, what in ITEMS:
        files = sorted(src.parent.glob(src.name)) if any(c in src.name for c in "*?") else [src]
        (OUT / sub).mkdir(parents=True, exist_ok=True)
        for f in files:
            if not f.exists():
                print("missing", f)
                continue
            d = OUT / sub / f.name
            shutil.copy2(f, d)
            lines.append(f"| {sub}/{f.name} | {what} | {f} | {md5(d)} |")
            n += 1
    (OUT / "extraction").mkdir(parents=True, exist_ok=True)
    d = OUT / "extraction" / "line_capacitance.csv"
    extracted_caps(d)
    lines.append(f"| extraction/line_capacitance.csv | Setup text: 47-62 fF BL, 21-36 fF SL | {PEX} | {md5(d)} |")
    n += 1
    (OUT / "MANIFEST.md").write_text("\n".join(lines) + "\n")
    print(f"backed up {n} files into {OUT}")


if __name__ == "__main__":
    main()
