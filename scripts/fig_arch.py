"""Fig. 1: (a) RERGON chip architecture (rergon_chip_top.sv), (b) floorplan from the final signoff DEF."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import style as S
import fig_floorplan as FP

LW = 0.7


def rbox(ax, x, y, w, h, text, fc="white", ec=S.INK2, fs=5.8, color=S.INK, weight="normal", lw=LW):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color,
            weight=weight, linespacing=1.1)


def arrow(ax, a, b, color=S.INK2, both=False, lw=LW):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", lw=lw,
                                                     color=color, shrinkA=0, shrinkB=0,
                                                     mutation_scale=5))


def arch(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.4)
    ax.axis("off")
    blue_fc, or_fc, aq_fc = "#dbe8f8", "#fbe3d9", "#d4f0e5"
    # host
    rbox(ax, 0.0, 5.75, 1.7, 1.2, "Host PC\nPython driver\n(pytest / lab)", fc="#f1f0ec")
    # pads + access
    rbox(ax, 2.2, 6.25, 1.7, 0.7, "Smart UART\nASCII / binary", fc="white")
    rbox(ax, 2.2, 5.35, 1.7, 0.7, "I²C target\n0x42", fc="white")
    arrow(ax, (1.7, 6.6), (2.2, 6.6), both=True)
    arrow(ax, (1.7, 5.7), (2.2, 5.7), both=True)
    ax.text(1.95, 6.68, "uart", fontsize=4.8, ha="center", va="bottom", color=S.INK2)
    ax.text(1.95, 5.78, "scl/sda", fontsize=4.8, ha="center", va="bottom", color=S.INK2)
    rbox(ax, 4.4, 5.35, 1.5, 1.6, "UART/I²C\narbiter\n+ cmd\nhistory", fc="white")
    arrow(ax, (3.9, 6.6), (4.4, 6.6), both=True)
    arrow(ax, (3.9, 5.7), (4.4, 5.7), both=True)
    rbox(ax, 6.4, 5.35, 3.6, 1.6, "mmap gateway\n16-bit address: [15:12] device,\n[4:2] register; "
         "baud & history\nsystem registers (dev 15)", fc="white")
    arrow(ax, (5.9, 6.15), (6.4, 6.15), both=True)
    # device bus
    ax.plot([0.3, 9.7], [4.75, 4.75], color=S.INK, lw=1.6, solid_capstyle="butt")
    ax.text(5.0, 4.85, "device bus: dev_id[3:0], reg[2:0], 32-bit wr/rd", fontsize=5.3,
            ha="center", va="bottom", color=S.INK)
    arrow(ax, (8.2, 5.35), (8.2, 4.75), both=True)
    # devices
    devs = [(0.1, "dev 0–1\n1T1R ×2", blue_fc, S.BLUE),
            (3.55, "dev 2–5\n2T1R ×4", or_fc, S.ORANGE),
            (6.85, "dev 6–7\nAM4 ×2", aq_fc, S.AQUA)]
    for x, t, fc, ec in devs:
        arrow(ax, (x + 1.5, 4.75), (x + 1.5, 4.35), both=True)
    # 1T1R stack (this work), detailed
    rbox(ax, 0.1, 3.45, 3.0, 0.9, "serializer: 8×32-bit regs\nCTRL CELLS WORD TIMINGS\nSTATUS DATA",
         fc=blue_fc, ec=S.BLUE, fs=5.2)
    rbox(ax, 0.1, 2.25, 3.0, 0.95, "controller FSM (21 states), 12 ops\nmulti-row PiM read (64-bit row mask)\nwrite / LOD / sample, 16-bit timers",
         fc=blue_fc, ec=S.BLUE, fs=5.2)
    rbox(ax, 0.1, 0.25, 3.0, 1.75, "memory_1T1R macro\n64×64 1T1R RRAM\n64 TS_LS drivers, 64 WL LS\n"
         "64 × 8-tap TDC\n226.5×547.4 µm²", fc=S.BLUE, ec=S.BLUE, color="white", fs=5.4, weight="bold")
    arrow(ax, (1.6, 3.45), (1.6, 3.2))
    arrow(ax, (1.0, 2.25), (1.0, 2.0))
    arrow(ax, (2.4, 2.0), (2.4, 2.25))
    ax.text(1.1, 2.12, "WLS[63:0] ...", fontsize=4.4, ha="left", va="center", color=S.INK2)
    ax.text(2.5, 2.12, "MEM_OUT", fontsize=4.4, ha="left", va="center", color=S.INK2)
    # others, context only
    rbox(ax, 3.55, 2.25, 3.0, 2.1, "2T1R arrays\n(other research\nmodule)", fc=or_fc, ec=S.ORANGE, fs=5.4)
    rbox(ax, 6.85, 2.25, 3.0, 2.1, "AM4 16b×16b\n(other research\nmodule)", fc=aq_fc, ec=S.AQUA, fs=5.4)
    # analog supply pads
    rbox(ax, 3.55, 0.25, 6.3, 1.75, "", fc="#f1f0ec")
    ax.text(6.7, 1.6, "dedicated supply pads (1T1R)", fontsize=5.6, ha="center", va="center")
    for i, (n, v) in enumerate(((r"$V_\mathrm{gate}$", "WL / READ LS level"),
                                (r"$V_\mathrm{drain}$", "write / precharge level"),
                                (r"$V_\mathrm{DEL}$", "TDC tap pitch"))):
        ax.text(3.85, 1.15 - 0.36 * i, n, fontsize=5.8, ha="left", va="center")
        ax.text(5.1, 1.15 - 0.36 * i, v, fontsize=5.2, ha="left", va="center", color=S.INK2)
    arrow(ax, (3.55, 1.1), (3.1, 1.1))


def main():
    S.setup()
    fig = plt.figure(figsize=(S.PAGE_W, 2.45))
    ax1 = fig.add_axes([0.0, 0.0, 0.58, 1.0])
    ax2 = fig.add_axes([0.62, 0.0, 0.38, 0.86])
    arch(ax1)
    FP.draw(ax2)
    fig.text(0.0, 0.99, "(a)", fontsize=8, weight="bold", va="top")
    fig.text(0.6, 0.99, "(b)", fontsize=8, weight="bold", va="top")
    S.save(fig, "arch_floorplan")


if __name__ == "__main__":
    main()
