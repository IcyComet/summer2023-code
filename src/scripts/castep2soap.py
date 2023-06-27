#!/usr/bin/env python

"""Calculate SOAP descriptors.
"""
import sys
sys.path.append('/storage/cmstore01/projects/Hydrocarbons/opt/summer2023-code/src')

import argparse
import sparse
from nnp.conversions.castep_convertor import Castep_SCF_Convertor, Castep_MD_Convertor

import fps

def convert(castep_file: str, scf: bool = False, pbc: bool = True, 
            finite_set_correction: bool = True):
    
    Conv = Castep_SCF_Convertor if scf else Castep_MD_Convertor 
    with open(castep_file, "r") as file:
        reader = Conv(file, finite_set_correction=finite_set_correction)
        return reader.read(pbc=pbc)

def main(infile: str, outfile: str, scf: bool = False, pbc: bool = True,
         finite_set_correction: bool = True):
    
    data = convert(infile, scf, pbc, finite_set_correction)
    soap_data = fps.calculate_soap(data)    
    sparse.save_npz(outfile, soap_data)
    return

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='Naive Script to convert castep output file to .npz' 
    )

    parser.add_argument('infile', type=str)
    parser.add_argument('-o', '--outfile', type=str, default='output.npz')
    parser.add_argument('-s', '--scf', action='store_true',
        help='Is the input file a restult of and scf calculation')
    parser.add_argument('-v', '--vacuum', action='store_true',
        help='Don\'t use pbc')
    parser.add_argument('-f', '--finite_set_correction', action='store_true',
        help='Use if no finite set correction was used in the calculation') 
    
    
    args = parser.parse_args()
    main(args.infile, args.outfile, args.scf, (not args.vacuum), (not args.finite_set_correction))
