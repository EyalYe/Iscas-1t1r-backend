"""Chip floorplan from the final signoff DEF (18.10.26 run 2): pads, macros, std-cell placement by owner."""
import gzip
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import style as S

DEF = S.BACKEND / "export/signoff/rergon_chip_top.5p8.def.gz"
MACRO_SIZE = {"memory_1T1R": (226.53, 547.355), "memory_2T1R": (82.01, 79.22),
              "Macro_RERGON_AM4_16bx16b": (111.385, 254.855)}
PAD_LONG, PAD_W, CORNER = 310.0, 60.0, 310.0
COMP = re.compile(r"^- (\S+) (\S+) .*?\+ (?:PLACED|FIXED) \( (-?\d+) (-?\d+) \) (\S+)")


def owner(inst):
    if "gen_eyal" in inst:
        return "1T1R"
    if "gen_avi" in inst:
        return "2T1R"
    if "gen_estaban" in inst:
        return "AM4"
    return "infra"


def load():
    txt = gzip.open(DEF, "rt").read()
    dbu = int(re.search(r"UNITS DISTANCE MICRONS (\d+)", txt).group(1))
    die = [int(v) / dbu for v in re.search(r"DIEAREA \( (\d+) (\d+) \) \( (\d+) (\d+) \)", txt).groups()]
    comps = txt.split("\nCOMPONENTS", 1)[1].split("END COMPONENTS", 1)[0]
    # a component may wrap; join each "- ..." entry up to its ';'
    items = []
    for entry in comps.split("\n- ")[1:]:
        m = COMP.match("- " + " ".join(entry.split()))
        if m:
            inst, master, x, y, ori = m.groups()
            items.append((inst, master, int(x) / dbu, int(y) / dbu, ori))
    return die, items


def draw(ax, legend_fs=5.6):
    die, items = load()
    ax.set_aspect("equal")
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks([]), ax.set_yticks([])
    ax.add_patch(Rectangle((0, 0), die[2], die[3], fc="#f6f6f4", ec=S.INK2, lw=0.6))

    cell_xy = {"1T1R": [], "2T1R": [], "AM4": [], "infra": []}
    for inst, master, x, y, ori in items:
        if master in MACRO_SIZE:
            continue
        if master in ("corner",):
            ax.add_patch(Rectangle((x, y), CORNER, CORNER, fc="#d9d8d3", ec="none"))
        elif master.startswith(("ixc013", "pwrpad", "vdd", "gnd", "filler", "power_cut")):
            w = 4.0 if master == "power_cut4u" else (10.0 if master == "filler10u" else
                                                    4.0 if master == "filler4u" else PAD_W)
            if ori in ("E", "W", "FE", "FW"):
                ax.add_patch(Rectangle((x, y), PAD_LONG, w, fc="#d9d8d3", ec="#bdbcb6", lw=0.2))
            else:
                ax.add_patch(Rectangle((x, y), w, PAD_LONG, fc="#d9d8d3", ec="#bdbcb6", lw=0.2))
        elif not master.startswith(("FEED", "FILL")):
            cell_xy[owner(inst)].append((x, y))

    colors = {"1T1R": S.BLUE, "2T1R": S.ORANGE, "AM4": S.AQUA, "infra": S.MUTED}
    for k in ("infra", "AM4", "2T1R", "1T1R"):
        if cell_xy[k]:
            xs, ys = zip(*cell_xy[k])
            ax.scatter(xs, ys, s=0.15, c=colors[k], lw=0, rasterized=True)

    labels = {"memory_1T1R": "1T1R\n64×64", "memory_2T1R": "2T1R", "Macro_RERGON_AM4_16bx16b": "AM4"}
    for inst, master, x, y, ori in items:
        if master in MACRO_SIZE:
            w, h = MACRO_SIZE[master]
            c = colors[owner(inst)]
            ax.add_patch(Rectangle((x, y), w, h, fc=c, ec=S.SURFACE, lw=0.8, alpha=0.9))
            if master == "memory_2T1R":
                continue
            ax.text(x + w / 2, y + h / 2, labels[master], ha="center", va="center", color="white",
                    fontsize=6.5, weight="bold", rotation=90 if "AM4" in master else 0)
    ax.text(1000, 1138, "4× 2T1R", ha="center", va="top", fontsize=6, color=S.INK, bbox=dict(fc="#f6f6f4", ec="none", pad=0.6))

    # core outline (from the DEF rows: 348.6 .. 1247.4 x 348.6 .. 1244.46 um)
    ax.add_patch(Rectangle((348.6, 348.6), 898.8, 895.86, fc="none", ec=S.INK2, lw=0.5, ls=(0, (3, 2))))
    ax.text(die[2] / 2, 330, "core 0.90 × 0.90 mm²", ha="center", va="top", fontsize=6, color=S.INK2)
    ax.text(die[2] / 2, 155, "pad ring: 52 pads", ha="center", va="center", fontsize=6, color=S.INK2)
    ax.annotate("", xy=(0, -40), xytext=(die[2], -40),
                arrowprops=dict(arrowstyle="<->", lw=0.6, color=S.INK2), annotation_clip=False)
    ax.text(die[2] / 2, -55, "1.596 mm", ha="center", va="top", fontsize=6.5, color=S.INK)
    for k, lab in (("1T1R", "1T1R logic (this work)"), ("2T1R", "2T1R logic"), ("AM4", "AM4 logic"),
                   ("infra", "UART/I²C/gateway")):
        ax.scatter([], [], s=12, c=colors[k], label=lab)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2, fontsize=legend_fs,
              handletextpad=0.1, columnspacing=0.8)
    ax.set_xlim(-10, die[2] + 10)
    ax.set_ylim(-110, die[3] + 10)
    return {k: len(v) for k, v in cell_xy.items()}


def main():
    S.setup()
    fig, ax = plt.subplots(figsize=(S.COL_W, S.COL_W))
    print(draw(ax))
    S.save(fig, "floorplan")


if __name__ == "__main__":
    main()
