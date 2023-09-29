#!/usr/bin/env python

import argparse
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl
from glob import glob
from os.path import isdir, isfile
import re

plt.rcParams["font.size"] = 20
# plt.rcParams["figure.figsize"] = (74, 15)

def main(pathstr: str, outfile: str) -> None:
    dirs = [pathstr + "/testing-CH4", pathstr + "/testing-CH8", pathstr + "/testing-H2"]
    fig, (i, j, k) = plt.subplots(3, 2, figsize=(21, 28), layout="constrained")
    sides = [i, j, k]
    for (d, a) in zip(dirs, sides):
        files = get_files(d)
        values = extract_mae(files)
        make_plots(fig, *a, values, cmap="viridis")
        a[0].set_title(f"{outfile} {d.split('-')[-1]} Energy Errors")
        a[1].set_title(f"{outfile} {d.split('-')[-1]} Forces Errors")
    # fig.tight_layout()
    fig.savefig(outfile + ".png") # bbox_inches="tight", pad_inches=0)
    return

def make_plots(fig, ax1, ax2, values, cmap="viridis"):
    x, y, energies, forces = tuple(zip(*values))
    sc1 = ax1.scatter(x, y, c=np.array(energies) * 1e3, cmap=cmap)
    ax1.set_xlabel("Pressure (GPa)")
    ax1.set_ylabel("Temperature (K)")
    fig.colorbar(sc1, ax=ax1, label="MAE Energy per Atom (meV)")
    sc2 = ax2.scatter(x, y, c=forces, cmap=cmap)
    fig.colorbar(sc2, ax=ax2, label="MAE Force Components (eV/\u212B)")
    ax2.set_xlabel("Pressure (GPa)")
    ax2.set_ylabel("Temperature (K)")

def get_files(pathstr):
    if not isdir(pathstr):
        raise ValueError("Path needs to be a directory containing .pkl files")
    files = glob(pathstr.removesuffix("/") + "/**/*.pkl", recursive=True)
    try:
        assert(all(map(isfile, files)))
    except AssertionError as e:
        raise AssertionError(f"Nonfiles: {[f for f in files if not isfile(f)]}") from e
    return files

def extract_mae(files):
    values = []
    for f in files:
        pressure = int(re.search("_([0-9]+)gpa_", f).group(1))
        temperature = int(re.search("_([0-9]+)K\.", f).group(1))
        with open(f, "rb") as file:
            data = pkl.load(file)
        mae_energy_atom = np.mean(data["mae_energy_atom"])
        mae_forces_component = np.mean(data["mae_forces_component"])
        values.append((pressure, temperature, mae_energy_atom, mae_forces_component))
    return values


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inputdir", type=str, help="input directory containing Schnet errors in .pkl files")
    parser.add_argument("outputfile", type=str, help=".png file where figure is saved")
    args = parser.parse_args()
    main(args.inputdir, args.outputfile)