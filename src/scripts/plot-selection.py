#!/usr/bin/env python

import argparse
import numpy as np
import matplotlib.pyplot as plt
from ase.db import connect
from collections import Counter

def main(dbFile: str, plotFile: str):
    """
    TODO add pie chart showing distribution of composition and clean up presentation
    """
    data = list(connect(dbFile, type="db").select())
    temps = map(lambda x: x.data["kelvin"], data[:])
    pressures = map(lambda x: x.data["gpa"], data[:])
    structures = map(lambda x: x.data["structure"], data[:])
    t_labels, t_counts = zip(*(Counter(temps).items()))
    p_labels, p_counts = zip(*(Counter(pressures).items()))
    comp_labels, comp_counts = zip(*(Counter(structures).items()))
    fig, (ax1,ax2,ax3) = plt.subplots(1,3, figsize=(24,8))
    ax1.pie(t_counts, labels=[str(x) + "K" for x in t_labels])
    ax2.pie(p_counts, labels=[str(x) + " GPa" for x in p_labels])
    ax3.pie(comp_counts, labels=[x for x  in comp_labels])
    ax1.set_title("Temperatures of selected configurations")
    ax2.set_title("Pressures of selected configurations")
    ax3.set_title("Compositions of selected configurations")
    # fig.tight_layout() #FIXME
    fig.savefig(plotFile)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dbFile", type=str)
    parser.add_argument("plotFile", type=str)
    args = parser.parse_args()
    main(args.dbFile, args.plotFile)