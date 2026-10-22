"""Build the shareable paper page: artifact/index.html + artifact/page-N.png from paper/main.pdf,
with the abstract as text and the simulation status from 1t1r-exp/runs/pim/. Re-run after every rebuild
of the PDF, then republish artifact/index.html with its page images."""
import datetime as dt
import html
import re
import subprocess
from pathlib import Path
import style as S
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "artifact"
PDF = ROOT / "paper" / "main.pdf"
RUNS = S.PIM_RUNS


def pages():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("page-*.png"):
        old.unlink()
    doc = pymupdf.open(PDF)
    names = []
    for i, p in enumerate(doc):
        name = f"page-{i + 1}.png"
        p.get_pixmap(dpi=170).save(OUT / name)
        names.append(name)
    text = doc[0].get_text()
    m = re.search(r"Abstract\s*[—-]\s*(.*?)Index Terms", text, re.S)
    abstract = " ".join(m.group(1).split()) if m else ""
    abstract = abstract.replace("- ", "-")         # rejoin words broken at line ends (keeps compound hyphens)
    t = re.search(r"^(.*?)\n(?:Eyal|\[)", text, re.S)
    title = " ".join(t.group(1).split()) if t else "RERGON 1T1R PiM macro"
    return names, abstract, title, len(doc)


def status():
    def count(pattern, text):
        return len(re.findall(pattern, text, re.M))
    log = (RUNS / "pim_sweep_pc.log").read_text() if (RUNS / "pim_sweep_pc.log").exists() else ""
    ok, failed = count(r" ok$", log), count(r"FAILED", log)
    out = subprocess.run("grep -l 'completes with 0 errors' " + str(RUNS) + "/pc_*/k*/spectre.out 2>/dev/null | wc -l",
                         shell=True, capture_output=True, text=True).stdout.strip()
    trans = int(out or 0)
    def done(glob):
        o = subprocess.run(f"grep -l 'completes with 0 errors' {RUNS}/{glob}/k*/spectre.out 2>/dev/null | wc -l",
                           shell=True, capture_output=True, text=True).stdout.strip()
        return int(o or 0)
    rw1 = done("rw_n*")
    rw2 = done("rwx_*")
    rlog = (RUNS / "run_rows.log").read_text() if (RUNS / "run_rows.log").exists() else ""
    m2 = re.findall(r"^(\d+) transients on", rlog, re.M)
    rw2_total = int(m2[1]) if len(m2) > 1 else 0
    pending = 0
    for f in (ROOT / "paper").glob("sec*.tex"):
        pending += f.read_text().count("%% GRID")
    return dict(ok=ok, failed=failed, trans=trans, pending=pending, rw1=rw1, rw2=rw2, rw2_total=rw2_total,
                rw_failed=len(re.findall(r"FAILED", rlog)))


def main():
    names, abstract, title, npages = pages()
    st = status()
    now = dt.datetime.now().strftime("%d %b %Y, %H:%M")
    grid_done = st["ok"] >= 72
    if st["rw2_total"]:
        rows_pct = round(100 * st["rw2"] / st["rw2_total"])
        rows_line = f"phase 2: {st['rw2']} of {st['rw2_total']} transients (16–64 rows)"
        rows_pill, rows_cls = ("row sweep complete", "ok") if st["rw2"] >= st["rw2_total"] else ("row sweep phase 2", "run")
    else:
        rows_pct = round(100 * st["rw1"] / 594)
        rows_line = f"phase 1: {st['rw1']} of 594 transients (1–8 rows)"
        rows_pill, rows_cls = "row sweep phase 1", "run"
    if st["rw_failed"]:
        rows_line += f", {st['rw_failed']} failed"
    note_file = ROOT / "artifact" / "note.txt"
    NOTE = html.escape(note_file.read_text().strip()) if note_file.exists() else ""
    pct = round(100 * st["trans"] / 270)
    imgs = "\n".join(
        f'<figure class="page"><img src="{n}" alt="Paper page {i + 1} of {npages}" loading="lazy" width="1445" height="1870">'
        f'<figcaption>Page {i + 1} of {npages}{" (references only)" if i + 1 == npages and npages == 5 else ""}</figcaption></figure>'
        for i, n in enumerate(names))
    grid_line = ("Complete: all 72 sweeps finished." if grid_done else
                 f"{st['ok']} of 72 sweeps and {st['trans']} of 270 transients done ({pct}%).")
    page = f"""<title>RERGON 1T1R PiM Paper</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: one reading column; status strip, abstract, then the paper's pages as printed. */
:root {{
  --bg: #eef1f4; --surface: #ffffff; --ink: #14202b; --ink-2: #4a5866; --rule: #cfd6dd;
  --accent: #1f5f8b; --warn: #8a5a00; --warn-bg: #fff3d6; --ok: #1d6b45; --ok-bg: #e2f3ea;
  --display: "Newsreader", "Iowan Old Style", Georgia, serif;
  --body: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #11171d; --surface: #182029; --ink: #e6edf3; --ink-2: #a3b1bf; --rule: #2c3845;
  --accent: #7cb8e4; --warn: #f0c060; --warn-bg: #3a2e12; --ok: #74d3a1; --ok-bg: #133325; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #11171d; --surface: #182029; --ink: #e6edf3; --ink-2: #a3b1bf; --rule: #2c3845;
  --accent: #7cb8e4; --warn: #f0c060; --warn-bg: #3a2e12; --ok: #74d3a1; --ok-bg: #133325; color-scheme: dark }}
body {{ background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 15px; line-height: 1.55; }}
.wrap {{ max-width: 860px; margin: 0 auto; padding-block: 32px 56px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 28px; }}
header {{ display: grid; gap: 10px; }}
.eyebrow {{ font-family: var(--mono); font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: var(--ink-2); }}
h1 {{ font-family: var(--display); font-weight: 600; font-size: clamp(26px, 4.4vw, 38px); line-height: 1.15; margin: 0; text-wrap: balance; }}
.byline {{ color: var(--ink-2); margin: 0; }}
.status {{ display: grid; gap: 10px; background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 16px 18px; }}
.status h2, section h2 {{ font-family: var(--body); font-size: 13px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; margin: 0; color: var(--ink-2); }}
.row {{ display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: baseline; }}
.pill {{ font-family: var(--mono); font-size: 12px; padding: 2px 8px; border-radius: 999px; }}
.pill.run {{ background: var(--warn-bg); color: var(--warn); }}
.pill.ok {{ background: var(--ok-bg); color: var(--ok); }}
.bar {{ height: 6px; background: var(--rule); border-radius: 3px; overflow: hidden; }}
.bar > span {{ display: block; height: 100%; width: {pct}%; background: var(--accent); }}
.mono {{ font-family: var(--mono); font-size: 13px; font-variant-numeric: tabular-nums; }}
.note {{ color: var(--ink-2); font-size: 14px; margin: 0; max-width: 68ch; }}
section {{ display: grid; gap: 10px; }}
.abstract {{ font-family: var(--display); font-size: 18px; line-height: 1.55; margin: 0; max-width: 68ch; }}
.pages {{ display: grid; gap: 22px; }}
.page {{ margin: 0; display: grid; gap: 6px; }}
.page img {{ width: 100%; height: auto; background: #fff; border: 1px solid var(--rule); border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
.page figcaption {{ font-family: var(--mono); font-size: 12px; color: var(--ink-2); }}
</style>
<div class="wrap">
  <header>
    <div class="eyebrow">ISCAS 2027 draft · pre-silicon, tape-out ready · IHP SG13G2</div>
    <h1>{html.escape(title)}</h1>
    <p class="byline">Eyal Yemini, Adi Teman and Leonid Yavits, Bar-Ilan University · draft updated {now}</p>
  </header>
  <div class="status" role="status">
    <h2>Simulation status</h2>
    <div class="row"><span class="pill {'ok' if grid_done else 'run'}">{'grid complete' if grid_done else 'grid running'}</span>
      <span class="mono">{html.escape(grid_line)}</span></div>
    <div class="bar" aria-hidden="true"><span></span></div>
    <div class="row"><span class="pill {rows_cls}">{rows_pill}</span>
      <span class="mono">{html.escape(rows_line)}</span></div>
    <div class="bar" aria-hidden="true"><span style="width:{rows_pct}%"></span></div>
    <p class="note">Row-count sweep: 1 to 8 rows open over V<sub>drain</sub>, V<sub>gate</sub> 0.8–1.0 V and HRS 200 kΩ / 1 MΩ (phase 1), then 16 to 64 rows at the best points (phase 2).</p>
    <p class="note">Full read-supply grid (V<sub>drain</sub>, V<sub>gate</sub>, V<sub>DEL</sub> 0.8–1.0 V; HRS 200 kΩ and 1 MΩ ideal)
      with the extracted line capacitance and 10 fF MEMRES capacitance. {('Sections still marked for update after the grid: ' + str(st['pending']) + '.') if st['pending'] else 'All sections reflect the finished grid.'}
      {NOTE}</p>
  </div>
  <section>
    <h2>Abstract</h2>
    <p class="abstract">{html.escape(abstract)}</p>
  </section>
  <section>
    <h2>Paper</h2>
    <div class="pages">
{imgs}
    </div>
  </section>
</div>
"""
    (OUT / "index.html").write_text(page)
    print(f"wrote {OUT / 'index.html'} with {npages} pages; grid {st['ok']}/72, transients {st['trans']}/270")


if __name__ == "__main__":
    main()
