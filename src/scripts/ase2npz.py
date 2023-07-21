#!/usr/bin/env python

import argparse
import sparse
from ase.db import connect
import numpy as np

def main(infile: str, outfile: str):
    denseArray = np.array(list(map(lambda row: row.data["soap"], \
        connect(infile, type="db").select())))
    sparse.save_npz(outfile + ".npz", sparse.COO.from_numpy(denseArray))
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str, \
                        help=".db file containing SOAP vectors in data dictionary")
    parser.add_argument("-o", "--outfile", type=str, \
                    help="name of the file where SOAP vectors are written (excluding .npz extension)")
    args = parser.parse_args()
    main(args.infile, args.outfile)