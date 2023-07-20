#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import argparse

def main(infiles: list[str], outfile: str):
    data = {fname.removesuffix("-lam.npy") : np.load(fname) for fname in infiles}
    fig, ax = plt.subplots(figsize=(14,10))
    for (label, distances) in data.items():
        ax.semilogy(range(1,len(distances)), distances[1:], linewidth=0.5, label=label)
    ax.legend()
    ax.set_title("Comparison of FPS Results")
    ax.set_xlabel("FPS rank")
    ax.set_ylabel("Distance")
    plt.tight_layout()
    plt.savefig(outfile + ".png")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", type=str, nargs="+", help="names of -lam.npy files")
    parser.add_argument("-o", "--outfile", type=str, help="name of the .png where the plot is saved")
    args = parser.parse_args()
    main(args.filenames, args.outfile)