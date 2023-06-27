#!/usr/bin/env python

import argparse
import numpy as np
import sparse

def main(soapfile_a: str, soapfile_b: str, atol: float, rtol: float):
    matrixA, matrixB = sparse.load_npz(soapfile_a), sparse.load_npz(soapfile_b)
    print(f"{soapfile_a} has shape: {matrixA.shape}")
    print(f"{soapfile_b} has shape: {matrixB.shape}")
    print(f"{soapfile_a} largest value: {np.max(np.abs(matrixA))} \nsmallest value: {np.min(np.abs(matrixA))}")
    print(f"{soapfile_b} largest value: {np.max(np.abs(matrixB))} \nsmallest value: {np.min(np.abs(matrixB))}")
    differences = np.abs(matrixA - matrixB)
    print(f"number of elements outwith absolute tolerance ({atol}): {(differences > atol).nnz}")
    print(f"largest absolute error: {np.max(differences)}")
    divisors = np.minimum(np.abs(matrixA), np.abs(matrixB)).todense()
    differences = differences.todense()
    relatives = np.divide(differences, divisors, where=divisors!=0, out=np.copy(differences))
    print(
        f"number of elements outwith relative tolerance ({rtol}): {np.count_nonzero(relatives > rtol)}")
    print(f"largest relative error: {np.max(relatives)}")
    #print(f"allclose: {np.max(np.abs(matrixA - matrixB) - rtol * matrixB) < atol}")
    print(f"simultaneous absolute and relative errors outwith tolerance: {np.count_nonzero((differences > atol) & (relatives > rtol))}")
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=\
                                     "Compare two .npz files to check if they are the same")
    parser.add_argument("npzFileA", type=str)
    parser.add_argument("npzFileB", type=str)
    parser.add_argument("--atol", required=False, type=float, default=1e-6, help="absolute tolerance")
    parser.add_argument("--rtol", required=False, type=float, default=1e-3, help="relative tolerance")
    args = parser.parse_args()

    main(args.npzFileA, args.npzFileB, args.atol, args.rtol)