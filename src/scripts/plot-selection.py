#!/usr/bin/env python

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from ase.db import connect
from collections import Counter

def main(dbFile: str, plotFile: str):
    """
    TODO clean up presentation, stack bars or add multiple datasets to one chart. Possibly make a 3D plot with 
    x=pressure, y=temperature, z=number of configurations, colour=composition?
    """
    with connect(dbFile, type="db") as db:
        data = [row for row in db.select()] #FIXME
    temps = map(lambda x: x.data["kelvin"], data)
    pressures = map(lambda x: x.data["gpa"], data)
    structures = map(lambda x: x.data["structure"], data)
    t_labels, t_counts = zip(*(Counter(temps).items()))
    p_labels, p_counts = zip(*(Counter(pressures).items()))
    t_sort, p_sort = np.argsort(np.fromiter(t_labels, int)), np.argsort(np.fromiter(p_labels, int))
    t_labels, t_counts = np.array(t_labels)[t_sort], np.array(t_counts)[t_sort]
    p_labels, p_counts = np.array(p_labels)[p_sort], np.array(p_counts)[p_sort]
    comp_labels, comp_counts = zip(*(Counter(structures).items()))
    comp_sort = np.argsort(comp_labels)
    comp_labels, comp_counts = np.array(comp_labels, dtype=str)[comp_sort], np.array(comp_counts)[comp_sort]
    plt.rcParams['font.size'] = 22
    # plt.rcParams["figure.constrained_layout.use"] = True
    fig, (ax1,ax2,ax3) = plt.subplots(1,3, figsize=(35, 12), layout="constrained")
    for ax in fig.axes:
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
    # autopct = lambda pct: f"{pct:.1f}% ({int(pct*len(data)/100)})"
    # wedges, *rest = ax1.pie(t_counts,labels=[str(x) + "K" for x in t_labels], labeldistance=None, autopct=autopct, pctdistance=1.1)
    # ax1.legend(bbox_to_anchor=(1,1), loc="upper left")
    color_func = lambda x: mpl.cm.ScalarMappable(cmap="viridis").to_rgba(x)
    discrete_color = lambda x: mpl.cm.ScalarMappable(cmap="Dark2").to_rgba(x)
    rect1 = ax1.bar(4 * np.arange(len(t_counts)), t_counts, width=3, tick_label=[str(x) for x in t_labels],
                    label=[f"{x*100/len(data):.1f}%" for x in t_counts], color=color_func(t_labels))
    plt.setp(ax1.get_xticklabels(), rotation=90)
    # ax1.legend(fontsize=14)
    ax1.bar_label(rect1, fmt=lambda x: f"{x*100/len(data):.1f}%", padding=5, color="k", fontsize=18)
    # ax2.pie(p_counts, labels=[str(x) + " GPa" for x in p_labels])
    rect2 = ax2.bar(range(len(p_counts)), p_counts, tick_label=[str(x) for x in p_labels], 
                    color=color_func(p_labels))
    ax2.bar_label(rect2, [f"{count*100/len(data):.1f}%" for count in p_counts], padding=5, color="k")
    # ax3.pie(comp_counts, labels=[x for x  in comp_labels])
    rect3 = ax3.bar(range(len(comp_counts)), comp_counts, tick_label=[x for x in comp_labels], 
                    color=discrete_color(np.arange(len(comp_counts))))
    ax3.bar_label(rect3, [f"{count*100/len(data):.1f}%" for count in comp_counts], padding=5, color="k")
    # ax1.set_title(f"Temperatures of {len(data)} selected configurations")
    # ax2.set_title(f"Pressures of {len(data)} selected configurations")
    # ax3.set_title(f"Compositions of {len(data)} selected configurations")
    ax1.set_xlabel("Temperature (K)", labelpad=6)
    ax2.set_xlabel("Pressure (GPa)")
    ax3.set_xlabel("Composition")
    fig.suptitle(f"Summary of {len(data)} Selected Configurations", fontweight="bold")
    fig.supylabel("Number of configurations")
    # fig.tight_layout() #FIXME
    fig.savefig(plotFile)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dbFile", type=str)
    parser.add_argument("plotFile", type=str)
    args = parser.parse_args()
    main(args.dbFile, args.plotFile)