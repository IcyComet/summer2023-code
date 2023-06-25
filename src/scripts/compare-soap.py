#!/usr/bin/env python

import argparse
import numpy as np
import sparse

def main(soapfile_a: str, soapfile_b: str, tolerance: float):
    matrixA, matrixB = sparse.load_npz(soapfile_a), sparse.load_npz(soapfile_b)
    print(f"first SOAP file has shape: {matrixA.shape}")
    print(f"second SOAP file has shape: {matrixB.shape}")
    differences = np.abs(matrixA - matrixB) > tolerance
    print(f"number of elements outwith tolerance: {differences.nnz}")
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=\
                                     "Compare two .npz files to check if they are the same")
    parser.add_argument("npzFileA", type=str)
    parser.add_argument("npzFileB", type=str)
    parser.add_argument("-t", "--tolerance", required=False, type=float, default=1e-6)
    args = parser.parse_args()

    main(args.npzFileA, args.npzFileB, args.tolerance)