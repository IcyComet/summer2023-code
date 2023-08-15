#!/usr/bin/env python

import argparse
import numpy as np
from glob import glob
from os.path import isdir, isfile

def main(pathstring: str, distance: float, nstructures: int):
    files = glob(pathstring.removesuffix("/") + "/**/*-lam.npy", recursive=True) if isdir(pathstring) else [pathstring]
    try:
        assert(all(map(isfile, files)))
    except AssertionError as e:
        raise AssertionError(f"Nonfiles: {[f for f in files if not isfile(f)]}") from e
    print(f"Number of files found: {len(files)}")
    if nstructures is not None:
        count = nstructures * len(files)
    else:
        count = 0
        for file in files:
            distances = np.load(file)
            count += np.count_nonzero(distances >= distance)
    print(f"Number of structures selected is: {count}")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pathstring", type=str, default=".")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--distance", type=float)
    group.add_argument("-n", "--nstructures", type=int)
    args = parser.parse_args()
    main(args.pathstring, args.distance, args.nstructures)