#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import argparse
from rdf import main as make_rdf
from glob import glob
import re
from hdf52ase import convert
from os.path import isfile

plt.rcParams["font.size"] = 20

def retry_rdf(infile, outfile, multiply=1):
    try:
        make_rdf(infile, outfile, multiply=multiply)
        return
    except AssertionError:
        retry_rdf(infile, outfile, multiply=2*multiply)
        return

def main(infile: str, outfile=None):
    outfile = infile if outfile is None else outfile

    if infile.endswith(".npy"):
        npy_files = [infile]
        outfile = infile.removesuffix(".npy")

    elif not (npy_files := glob(infile + "_RDF*.npy")):
        if not isfile(infile + ".db"):
            convert([infile + ".hdf5"], infile + ".db")
        
        retry_rdf(infile + ".db", outfile=infile)

        npy_files = glob(infile + "_RDF*.npy")
    
    fig, ax = plt.subplots(figsize=(16,9))
    for file in npy_files:
        rdf = np.load(file)
        label = re.search("RDF_([A-Z]+)\.npy", file).group(1)
        ax.plot(np.linspace(0, 11.255/2, num=len(rdf)), rdf, label=label) # rmax=11.255/2 Angstrom by default
    ax.set_ylim(bottom=0, top=5) # NOTE
    ax.legend()
    ax.set_xlabel("Radial Distance (\u212B)")
    ax.set_ylabel("RDF")
    ax.set_title(outfile.split("/")[-1])
    fig.tight_layout()
    fig.savefig(outfile + ".png")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str, help="filename (no ending or .npy) for plotting rdf")
    parser.add_argument("-o", "--outfile", type=str, default=None, help="Name of output file (don't include .png extension)")
    args = parser.parse_args()
    main(args.infile, args.outfile)