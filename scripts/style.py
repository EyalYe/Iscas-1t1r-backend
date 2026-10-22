"""Shared matplotlib style for the ISCAS figures (IEEE column = 3.5 in, page = 7.16 in)."""
from pathlib import Path
import matplotlib as mpl

WS = Path("/project/sg13g2/users/yeminie/ws")
BACKEND = WS / "backend/rergon"
FRONTEND = WS / "frontend/rergon"
EXP = WS / "1t1r-exp"
PIM_RUNS = EXP / "runs/pim"          # multi-row SPICE runs (1t1r-exp/pim/*.py), git-ignored there
RESULTS = EXP / "docs/results"
SPICE_RUNS = FRONTEND / "runspace/spice_1t1r"
FIGS = Path(__file__).resolve().parent.parent / "figs"

COL_W = 3.5
PAGE_W = 7.16

# reference palette (dataviz skill, light mode), categorical slots in fixed order
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
SURFACE = "#ffffff"


def setup():
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIXGeneral", "Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.minor.width": 0.4,
        "ytick.minor.width": 0.4,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.5,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "lines.linewidth": 1.4,
        "lines.markersize": 4,
        "legend.frameon": False,
        "pdf.fonttype": 42,          # TrueType, no Type 3 (IEEE PDF eXpress)
        "ps.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "figure.dpi": 150,
    })


def save(fig, name):
    FIGS.mkdir(exist_ok=True)
    fig.savefig(FIGS / f"{name}.pdf")
    fig.savefig(FIGS / f"{name}.png", dpi=300)
