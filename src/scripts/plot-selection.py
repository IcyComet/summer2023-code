#!/usr/bin/env python

import argparse
import numpy as np
import matplotlib.pyplot as plt
from ase.db import connect
from collections import Counter

def main(dbFile: str, plotFile: str):
    """
    TODO clean up presentation, stack bars or add multiple datasets to one chart. Possibly make a 3D plot with 
    x=pressure, y=temperature, z=number of configurations, colour=composition?
    """
    data = list(connect(dbFile, type="db").select())
    temps = map(lambda x: x.data["kelvin"], data[:])
    pressures = map(lambda x: x.data["gpa"], data[:])
    structures = map(lambda x: x.data["structure"], data[:])
    t_labels, t_counts = zip(*(Counter(temps).items()))
    p_labels, p_counts = zip(*(Counter(pressures).items()))
    comp_labels, comp_counts = zip(*(Counter(structures).items()))
    plt.rcParams['font.size'] = 14
    fig, (ax1,ax2,ax3) = plt.subplots(1,3, figsize=(24,10))
    # autopct = lambda pct: f"{pct:.1f}% ({int(pct*len(data)/100)})"
    # wedges, *rest = ax1.pie(t_counts,labels=[str(x) + "K" for x in t_labels], labeldistance=None, autopct=autopct, pctdistance=1.1)
    # ax1.legend(bbox_to_anchor=(1,1), loc="upper left")
    rect1 = ax1.bar(range(len(t_counts)), t_counts, tick_label=[str(x)+"K" for x in t_labels])
    ax1.bar_label(rect1, [f"{count*100/len(data):.1f}%" for count in t_counts], padding=5, color="k")
    # ax2.pie(p_counts, labels=[str(x) + " GPa" for x in p_labels])
    rect2 = ax2.bar(range(len(p_counts)), p_counts, tick_label=[str(x) + " GPa" for x in p_labels])
    ax2.bar_label(rect2, [f"{count*100/len(data):.1f}%" for count in p_counts], padding=5, color="k")
    # ax3.pie(comp_counts, labels=[x for x  in comp_labels])
    rect3 = ax3.bar(range(len(comp_counts)), comp_counts, tick_label=[x for x in comp_labels])
    ax3.bar_label(rect3, [f"{count*100/len(data):.1f}%" for count in comp_counts], padding=5, color="k")
    ax1.set_title(f"Temperatures of {len(data)} selected configurations")
    ax2.set_title(f"Pressures of {len(data)} selected configurations")
    ax3.set_title(f"Compositions of {len(data)} selected configurations")
    fig.tight_layout() #FIXME
    fig.savefig(plotFile)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dbFile", type=str)
    parser.add_argument("plotFile", type=str)
    args = parser.parse_args()
    main(args.dbFile, args.plotFile)