#!/usr/bin/env python

import argparse
import sparse as sp
import numpy as np
from ase.db import connect

def main(dbfile: str, outfile: str):
    with connect(dbfile, type="db") as db:
        soap = np.array([r.data["soap"] for r in db.select()])
    sp.save_npz(outfile, sp.COO.from_numpy(soap))
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str, help=".db file containing SOAP vectors in data dict")
    parser.add_argument("outfile", type=str, help="Name of the file where the SOAP vectors will be stored")
    args = parser.parse_args()
    main(args.infile, args.outfile)