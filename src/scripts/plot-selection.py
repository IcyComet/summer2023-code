#!/usr/bin/env python

import argparse
import numpy as np
import matplotlib.pyplot as plt
from ase.db import connect
from collections import Counter

def main(dbFile: str, plotFile: str):
    data = connect(dbFile, type="db").select()
    temps = map(lambda x: x.data["kelvin"], data)
    labels, counts = zip(*(Counter(temps).items()))
    print(f"number of temperatures: {len(list(labels))}")
    fig, ax = plt.subplots()
    ax.pie(counts, labels=list(labels))
    fig.savefig(plotFile)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dbFile", type=str)
    parser.add_argument("plotFile", type=str)
    args = parser.parse_args()
    main(args.dbFile, args.plotFile)