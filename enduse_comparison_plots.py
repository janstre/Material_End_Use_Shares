import matplotlib.pyplot as plt
import math
import matplotlib.dates as mdates
import seaborn as sns
import matplotlib.ticker as mtick


def country_all_enduses_panel(data_dict, title, save=False):
    n_plots = len(data_dict.keys())
    n_rows = 6
    n_cols = math.ceil(n_plots/n_rows)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 15))
    fig.suptitle(title, fontsize=18)
    sns.set_palette("hls", 12)
    current_palette = sns.color_palette()
    desaturated_palette = [sns.desaturate(color, 0.7) for color in current_palette]
    sns.set_palette(desaturated_palette)
    plt.rcParams["axes.axisbelow"] = False
    plt.rcParams["grid.color"] = "gray"
    plt.rcParams["grid.linewidth"] = 0.2
    for ax, key in zip(axes.flatten(), data_dict):
        stacks = ax.stackplot(data_dict[key].columns.values, data_dict[key].values, labels=data_dict[key].index)
        for stack in stacks:
            stack.set_edgecolor('black')
        stack.set_linewidth(0.03)  # Set the edge color
        ax.set_xlim(0, len(data_dict[key].columns.values)-1)
        ax.set_ylim(0, 100)
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax.set_title(f'{key}')
        ax.grid(True, zorder=100)
    plt.delaxes(axes.flatten()[-1])
    # fig.subplots_adjust(bottom=1)

    fig.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.subplots_adjust(bottom=0.1)
    axes.flatten()[-2].legend(loc='center')
    sns.move_legend(axes.flatten()[-2], "upper left", bbox_to_anchor=(1.2, 1.1))
    if save:
        plt.savefig("gloria_output/" + title+".png", dpi=300)
        plt.close()
    else:
        plt.show()
