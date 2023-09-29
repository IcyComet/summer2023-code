#!/usr/bin/env python

import argparse
import numpy as np
import tables
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import interpn
import pickle as pkl
from ase.io import read as aseRead
import sys
sys.path.append("/storage/cmstore01/projects/Hydrocarbons/opt/summer2023-code/src")
from nnp.conversions.castep_convertor import Castep_MD_Convertor

plt.rcParams["font.size"] = 20

def main(picklefile, h5file, dftfile, outfile):
    plot_force_scatter(h5file, dftfile, f"{outfile}-forces.png")
    plot_energies(h5file, dftfile, f"{outfile}-energies.png")
    return

def plot_force_hist(h5file, dftfile, outfile):
    nnForces, dftForces = read_forces(h5file, dftfile)
    assert(dftForces.shape == nnForces.shape)
    fig, ax = plt.subplots(figsize=(16,9))
    # ax.scatter(np.reshape(dftForces, -1), np.reshape(nnForces, -1))
    x, y = np.reshape(dftForces, -1), np.reshape(nnForces, -1)
    mesh = ax.hist2d(x, y, bins=[1000,1000], norm="asinh", cmap="plasma")
    fig.colorbar(mesh[-1], ax=ax, label="Density (points per bin)")
    fig.tight_layout()
    fig.savefig(outfile)
    return

def plot_force_scatter(h5file, dftfile, outfile): # TODO add correlation coefficient
    nnForces, dftForces = read_forces(h5file, dftfile)
    if nnForces.shape[0] != dftForces.shape[0]:
        sample = int(np.ceil(dftForces.shape[0] / nnForces.shape[0]))
        dftForces = dftForces[::sample]
        assert(nnForces.shape == dftForces.shape)
    x, y = np.reshape(dftForces, -1), np.reshape(nnForces, -1)
    hist, x_e, y_e = np.histogram2d(x, y, bins=[1000,1000], density=False)
    z = interpn((0.5 * (x_e[:-1] + x_e[1:]), 0.5 * (y_e[:-1] + y_e[1:])), hist, np.vstack([x,y]).T, \
                bounds_error=False, method="splinef2d", fill_value=0)
    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]
    fig, ax = plt.subplots(figsize=(14,10))
    sc = ax.scatter(x, y, c=z, s=9, vmin=1, norm="log", cmap=mpl.colormaps["plasma"])
    ax.axline((0,0), slope=1, linewidth=2, c="g")
    ax.set_title("Forces Plot")
    ax.set_xlabel("DFT Force Components (eV/\u212B)")
    ax.set_ylabel("Schnet Force Components (eV/\u212B)")
    fig.colorbar(sc, ax=ax, label="Points per bin")
    fig.tight_layout()
    fig.savefig(outfile)
    return

def read_forces(h5file, dftfile=None):
    schnet_file = tables.open_file(h5file, "r")
    nnForces = schnet_file.root.forces.read()
    schnet_file.close()

    if dftfile is None:
        return nnForces, None

    if dftfile.endswith(".castep"):
        with open(dftfile, "r", errors="replace") as castepfile:
            traj = Castep_MD_Convertor(castepfile).read()
    else:
        traj = aseRead(dftfile, format="db", index=":")
    
    dftForces = np.array([config.get_forces() for config in traj])
    return nnForces, dftForces

def plot_mae_energy_atom(picklefile, outfile):
    with open(picklefile, "rb") as file:
        errors = pkl.load(file)
    fig, ax = plt.subplots(figsize=(16,9))
    ax.plot(errors["mae_energy_atom"], "r-", label="Energy MAE per atom")
    ax.set_xlabel("Configuration (time)")
    ax.set_ylabel("MAE (eV / Atom)")
    ax.set_title("Mean Absolute Energy Error per Atom")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outfile)

def read_energies(h5file, dftfile=None):
    schnet_file = tables.open_file(h5file, "r")
    nnEnergies = schnet_file.root.energies.read()
    schnet_file.close()

    if dftfile is None:
        return nnEnergies, None
    
    if dftfile.endswith(".castep"):
        with open(dftfile, "r", errors="replace") as castepfile:
            traj = Castep_MD_Convertor(castepfile).read()
    
    else:
        traj = aseRead(dftfile, format="db", index=":")
    
    dftEnergies = np.array([config.get_potential_energy() for config in traj])
    return nnEnergies, dftEnergies

def plot_energies(h5file, dftfile, outfile):
    nnEnergies, dftEnergies = read_energies(h5file, dftfile)
    time = np.arange(len(dftEnergies)) * 5e-4
    if len(nnEnergies) != len(dftEnergies):
        sample = int(np.ceil(len(dftEnergies) / len(nnEnergies)))
        dftEnergies = dftEnergies[::sample]
        time = time[::sample]
        assert(len(dftEnergies) == len(nnEnergies))
    fig, ax = plt.subplots(figsize=(16,9))
    ax.plot(time, nnEnergies - dftEnergies[0], label="Schnet") # TODO
    ax.plot(time, dftEnergies - dftEnergies[0], label="Castep")
    ax.legend()
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel("Potential Energy (eV)")
    ax.set_title("Energy Plot")
    fig.tight_layout()
    fig.savefig(outfile)
    return

"""def plot_sigmas(h5file, outfile): # TODO
    schnet_file = tables.open_file(h5file, "r")
    energy_std = schnet_file.root.energies_std.read()
    forces_std = schnet_file.root.forces_std.read()
    schnet_file.close()
    averaged = np.mean(forces_std, axis=(2,1))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,9))
    time = np.arange(len(energy_std)) * 5e-4 # TODO sampled?
    ax1.plot(energy_std, linewidth=0.5)
    ax2.plot(averaged, linewidth=0.5)
    fig.tight_layout()
    fig.savefig(outfile)
    return
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group("testfiles")
    group.add_argument("-p","--picklefile", type=str, default=None)
    group.add_argument("-t", "--h5file", type=str, default=None)
    parser.add_argument("-d", "--dft", type=str, default=None)
    parser.add_argument("--outfile", "-o", type=str)
    args = parser.parse_args()
    if (args.picklefile is None) and (args.h5file is None):
        parser.error("Supply at least one input file (.pkl or .h5)")
    main(args.picklefile, args.h5file, args.dft, args.outfile)