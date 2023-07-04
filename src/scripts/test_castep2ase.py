#!/usr/bin/env python

import sys
sys.path.append('/storage/cmstore01/projects/Hydrocarbons/opt/summer2023-code/src')

import argparse
from nnp.conversions.castep_convertor import Castep_MD_Convertor

def main(filelist:list, pbc:bool=True, finite_set_correction:bool=True):
    for filename in filelist:
        with open(filename, "r") as file:
            traj = Castep_MD_Convertor(file, finite_set_correction=finite_set_correction).read(pbc=pbc)
            print(f"Result of converting {filename.split(sep='/')[-1]} to ASE:")
            print(f"Number of Atoms objects in trajectory: {len(traj)}")
            print(f"Number of Atom objects in first Atoms object: {len(traj[0])}")
            print(f"Number of Atom objects in final Atoms object: {len(traj[-1])}")
            print(f"largest number of Atom objects in a configuration: {max(map(len, traj))}")
            print(f"smallest number of Atom objects in a configuration: {min(map(len, traj))}")

    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test conversion of .castep files into list of ASE atoms objects without writing to file")
    parser.add_argument("infiles", type=str, nargs="+", help=".castep files to test the converter on")
    parser.add_argument('-v', '--vacuum', action='store_true',
        help='Don\'t use pbc')
    parser.add_argument('-f', '--finite_set_correction', action='store_true',
        help='Use if no finite set correction was used in the calculation')
    
    args = parser.parse_args()
    main(args.infiles, (not args.vacuum), (not args.finite_set_correction))