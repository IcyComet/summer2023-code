#!/usr/bin/env python

import argparse
import numpy as np
import tables
import matplotlib.pyplot as plt
from ase.io import read as aseRead
import pickle as pkl

import sys
sys.path.append("/storage/cmstore01/projects/Hydrocarbons/opt/summer2023-code/src")
from nnp.conversions.castep_convertor import Castep_MD_Convertor

def main(dftName, h5nameA, h5nameB, outfile):
    if dftName.endswith(".castep"):
        with open(dftName, "r", errors="replace") as castepfile:
            traj = Castep_MD_Convertor(castepfile).read()
    else:
        traj = aseRead(dftName, format="db")
    dft_energies = np.array([config.get_potential_energy() for config in traj])
    predictionsA = tables.open_file(h5nameA, "r")
    nnEnergiesA = predictionsA.root.energies.read().reshape(-1)
    predictionsA.close()
    if h5nameB is not None:
        predictionsB = tables.open_file(h5nameB, "r")
        nnEnergiesB = predictionsB.root.energies.read().reshape(-1)
        predictionsB.close()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,10))
        ax2.plot(dft_energies, "r-", label="DFT energy", linewidth=0.5)
        ax2.plot(nnEnergiesB, "b-", label="Schnet energy", linewidth=0.5)
        ax2.set_title(h5nameB.removesuffix(".h5"))
        ax2.legend()
    else:
        fig, ax1 = plt.subplots(figsizse=(16,9))
    ax1.plot(dft_energies, "r-", label="DFT energy", linewidth=0.5)
    ax1.plot(nnEnergiesA, "b-", label="Schnet energy", linewidth=0.5)
    ax1.set_title(h5nameA.removesuffix(".h5"))
    ax1.legend()
    fig.tight_layout()
    fig.savefig(outfile)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("h5fileA", type=str)
    parser.add_argument("h5fileB", type=str, default=None)
    parser.add_argument("-o", "--outfile", type=str)
    parser.add_argument("-d","--dft", type=str)
    args = parser.parse_args()
    main(args.dft, args.h5fileA, args.h5fileB, args.outfile)