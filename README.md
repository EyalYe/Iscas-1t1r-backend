# ISCAS 2027 paper: RERGON 1T1R RRAM PiM macro

| path | contents |
| --- | --- |
| `paper/` | IEEEtran conference source (`main.tex`, `sec*.tex`, `refs.bib`), `main.pdf`, `build.sh` |
| `figs/` | figures (PDF for LaTeX, PNG previews) |
| `scripts/` | figure generators (`fig_*.py`), result backup (`backup_results.py`), artifact page (`build_artifact.py`), waveform cache (`extract_waves.py`); the SPICE experiments are in `../1t1r-exp/pim/` |
| `1t1r-exp/runs/pim/` | multi-row (PiM) SPICE runs, one dir per tag, CSV per tag; `sweep_codes.csv` + `sweep_best.csv` (supply sweep, `pim_sweep_analyze.py`) |
| `data/` | cached .npz waveforms from `frontend/rergon/runspace/spice_1t1r` |
| `template_dl/` | downloaded IEEEtran template (CTAN) |

Rebuild: `cd paper && ./build.sh` (tectonic in ~/.local/bin; any TeX Live/Overleaf works too).
Figures: run `scripts/fig_*.py` with `~/.local/venvs/paper/bin/python` (needs matplotlib, gdstk, pymupdf):
Fig. 1 = fig_macro.py (`--layout` adds the GDS render, not in the paper), Fig. 2 = fig_schematic.py, Fig. 3 and Table III = fig_grid.py, Fig. 4 = fig_rows.py; fig_read2.py drew the single-row figure of earlier drafts.
`backup_results.py` refreshes paper/results/.
Limits (ISCAS 2027): 4 pages of content + 1 optional page of references only; not double-blind;
deadline 22 Oct 2026 23:59 UTC-5.

## Caveats

- **Omitted from this repository.** The reference PDFs (`paper/refs/`), the internal fact sheet and the working
  notes (`docs/`) are kept out because they quote IHP's confidential MEMRES documentation and publisher PDFs.
  The paper source, figures, figure scripts and every result CSV the paper uses (`paper/results/`) are included.
- **Row-count sweep finished (Fig. 4).** `1t1r-exp/pim/run_rows.sh` ran 1–8 rows open over the full supply grid, then
  16–64 rows at the best 8-row supplies (754 transients). Its results (`rw_*`, `rwx_*`, `rows_summary.csv`) are
  backed up in `paper/results/rows/`; `scripts/fig_rows.py` draws Fig. 4.
