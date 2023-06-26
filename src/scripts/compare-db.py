#!/usr/bin/env python

import argparse
from ase.io import read

def main(dbFileA: str, dbFileB: str):
    dataA, dataB = read(dbFileA), read(dbFileB)
    print(f"{dbFileA} contains {len(dataA)} atoms objects")
    print(f"{dbFileB} contains {len(dataB)} atoms objects")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare 2 .db files")
    parser.add_argument("dbFileA", type=str)
    parser.add_argument("dbFileB", type=str)
    args = parser.parse_args()

    main(args.dbFileA, args.dbFileB)