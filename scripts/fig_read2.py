"""Fig. 3 (column width): single-row read on the slice, (a) level-shifter delay vs Vgate,
(b) BL crossing time vs cell resistance (TDC read and discharge-length test)."""
import matplotlib.pyplot as plt
import style as S
import fig_read as R


def main():
    S.setup()
    fig, axs = plt.subplots(1, 2, figsize=(S.COL_W, 1.7))
    R.panel_ls(axs[0])
    R.panel_cross(axs[1])
    axs[1].set_title("(b)", loc="left", x=-0.22, fontsize=8, weight="bold")
    fig.tight_layout(w_pad=1.2)
    S.save(fig, "read_char2")


if __name__ == "__main__":
    main()
