#!/usr/bin/env python

"""Calculate SOAP descriptors.
"""
import sys
sys.path.append('/storage/cmstore01/projects/Hydrocarbons/opt/summer2023-code/src')

import argparse
import numpy as np
import sparse
from itertools import zip_longest
from nnp.conversions.castep_convertor import Castep_SCF_Convertor, Castep_MD_Convertor

import fps

def convert(castep_file: str, scf: bool = False, pbc: bool = True, 
            finite_set_correction: bool = True):
    
    Conv = Castep_SCF_Convertor if scf else Castep_MD_Convertor 
    with open(castep_file, "r", errors="replace") as file:
        reader = Conv(file, finite_set_correction=finite_set_correction)
        return reader.read(pbc=pbc)

def main(infile: str, outfile: str, scf: bool = False, pbc: bool = True,
         finite_set_correction: bool = True, npzfile: str = None):
    
    data = convert(infile, scf, pbc, finite_set_correction)
    inner = sparse.load_npz(npzfile).todense() if npzfile else []
    assert(len(inner) in [0, len(data)])
    pairs = zip_longest(data, inner, fillvalue=None)

    # sigmas = lambda mat, avg: np.sqrt(np.mean((mat - avg)**2, axis=0)) if avg is not None else \
    #     np.std(mat, axis=0)
    
    # sigma_outer = lambda mat: np.std(mat, axis=0)
    # sigma_inner = lambda mat, avg: np.sqrt(np.mean(mat - avg)**2, axis=0) if avg is not None else None
    
    sigmas = lambda mat, avg: (np.std(mat, axis=0), np.sqrt(np.mean((mat - avg)**2, axis=0)) if avg is not None \
                               else None)
    
    matrix = lambda atoms: fps.calculate_soap(atoms, average="off", sparse=False)

    sigmas_o, sigmas_i = zip(*[sigmas(matrix(atoms), avg) for (atoms, avg) in pairs])

    if None in np.array(sigmas_i):
        np.savez_compressed(outfile, outer=np.array(sigmas_o))
    else:
        np.savez_compressed(outfile, outer=np.array(sigmas_o), inner=np.array(sigmas_i))
    return

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='Script to calculate standard deviations of SOAP vectors for a castep file' 
    )

    parser.add_argument('infile', type=str)
    parser.add_argument('-n', '--npzfile', type=str, default=None)
    parser.add_argument('-o', '--outfile', type=str)
    parser.add_argument('-s', '--scf', action='store_true',
        help='Is the input file a restult of and scf calculation')
    parser.add_argument('-v', '--vacuum', action='store_true',
        help='Don\'t use pbc')
    parser.add_argument('-f', '--finite_set_correction', action='store_true',
        help='Use if no finite set correction was used in the calculation') 
    
    
    args = parser.parse_args()
    main(args.infile, args.outfile, args.scf, (not args.vacuum), (not args.finite_set_correction),\
         args.npzfile)
