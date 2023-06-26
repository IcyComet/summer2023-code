#!/usr/bin/env python

import argparse
from ase.io import read

def main(dbFileA: str, dbFileB: str):
    atomListA, atomListB = read(dbFileA, index=slice(None)), read(dbFileB, index=slice(None))
    print(f"{dbFileA} contains {len(atomListA)} atoms objects")
    print(f"{dbFileB} contains {len(atomListB)} atoms objects")
    print(f"number of atoms in final Atoms object of {dbFileA}: {len(atomListA[-1])}")
    print(f"number of atoms in final Atoms object of {dbFileB}: {len(atomListB[-1])}")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare 2 .db files")
    parser.add_argument("dbFileA", type=str)
    parser.add_argument("dbFileB", type=str)
    args = parser.parse_args()

    main(args.dbFileA, args.dbFileB)