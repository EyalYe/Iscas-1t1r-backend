"""Cache selected Spectre psfascii waveforms (frontend runspace/spice_1t1r) as .npz for plotting."""
import re
import sys
from pathlib import Path
import numpy as np
import style as S

sys.path.insert(0, str(S.EXP / "spice"))
from psf import Tran, sweep_files  # noqa: E402  (the experiment repo's own reader)

CACHE = Path(__file__).resolve().parent.parent / "data"
RUNS = ["read_code_r_vg15_d1", "read_code_vgate", "read_code_r_vg15_off0", "read_code_r"]
KEEP = ["BL_0", "SL_0", "WL_0", "READ", "READ_DELAYED", "DRAIN_SL", "CLK_IN_0", "CLK_IN_7"]


def sweep_vals(psfdir):
    txt = (psfdir / "swp_tran1.sweep").read_text()
    return [float(v) for v in re.findall(r'"\S+" ([-+\d.eE]+)', txt.split("VALUE", 1)[1])]


def main():
    CACHE.mkdir(exist_ok=True)
    for run in RUNS:
        psfdir = S.SPICE_RUNS / run / "psf"
        vals = sweep_vals(psfdir)
        out = {"values": np.array(vals)}
        for i, f in enumerate(sweep_files(psfdir)):
            tr = Tran(f)
            out[f"t_{i}"] = np.array(tr.t)
            for k in KEEP:
                if k in tr.sig:
                    out[f"{k}_{i}"] = np.array(tr.sig[k])
        np.savez_compressed(CACHE / f"{run}.npz", **out)
        print(run, len(vals), "points")


if __name__ == "__main__":
    main()
