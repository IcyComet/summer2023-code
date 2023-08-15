#!/usr/bin/env python

import argparse
import re
import sparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib 
from ase.db import connect

import sys
sys.path.append('/storage/cmstore01/projects/Hydrocarbons/opt/summer2023-code/src')
from scripts.castep2soap import convert # Function for reading Atoms objects from castep files

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

def main(fil, fn_perm, outfile, distance, n_structures):
    
    name = fil.split('/')[-1]
    name = name.split('.')[0]
    fn_lam = fn_perm.replace('-perm', '-lam')

    perm = np.load(fn_perm)
    lam = np.load(fn_lam)[1:]

    if distance is not None:
        # selection based on distance    
        #we are ignoring the first element because first distance is always zero
        n_structures = np.where(lam<distance)[0][0]    
    
    idx_selected = perm[:n_structures].astype(int)

    print(f"{name}: {n_structures:d} geometries selected with {lam[n_structures-1]} minimum distance")

    """NOTE don't try to parallelise with & in bash because it leads to sqlite3.OperationalErrors 
    (trying to connnect to locked files)"""
    
    if fil.endswith(".db"):
        with connect(fil, type="db") as db:
            data = [row for row in db.select()]
        data_selected = [data[idx] for idx in idx_selected]
        write_from_db(outfile, data_selected)
    elif fil.endswith(".castep"):
        data = convert(fil)
        
        details = re.search("(C?H[0-9]).*?([0-9]+)gpa.*?([0-9]+)K", fil) #info values
        assert(details is not None)
        info = {"structure":details[1], "gpa":int(details[2]), "kelvin":int(details[3])}
        data_selected = [data[idx] for idx in idx_selected]
        soap_selected = read_soap(fn_perm, idx_selected, data)
        write_from_castep(outfile, data_selected, info, soap_selected)
    
    else:
        raise ValueError("Filename does not end in .db or .castep")
    
    return

def read_soap(fn_perm, idx_selected, data):
    try:
        soapdata = sparse.load_npz(fn_perm.replace("-perm.npy", ".npz"))
        assert(soapdata.shape[0] == len(data))
        soap_selected = soapdata[idx_selected]
        assert(soap_selected.shape == (len(idx_selected),soapdata.shape[1]))
    except FileNotFoundError as fe:
        raise FileNotFoundError("Error: could not find corresponding .npz file in the directory of the perm file") \
            from fe
        
    return soap_selected

def write_from_castep(outfile, data_selected, info, soap_selected : sparse.COO):
    ds = [info | {"soap": vector.todense()} for vector in soap_selected]
    assert(len(data_selected) == len(ds))
    with connect(outfile, type="db") as db:
        for (atoms, vals) in zip(data_selected, ds):
            db.write(atoms, data=vals)

def write_from_db(outfile, data_selected):
    with connect(outfile, type="db") as db:
        for row in data_selected:
            db.write(row.toatoms(), data=row.data)


def plot_selected_energies(data, idx_selected, name='', timestep = .5):
    
    energies = np.array([x.get_potential_energy() for x in data])
    energies -= np.min(energies)
    
    n_steps = len(energies)
    time = timestep*np.linspace(0, n_steps-1, n_steps)
    
    matplotlib.rcParams.update({'font.size': 22})
    
    plt.figure(figsize=(30, 20))

    plt.plot(time, energies, c='black')
    plt.scatter(time[idx_selected], energies[idx_selected], c='red', label='Selected geometries', s=80)
    plt.scatter(time[idx_selected], np.zeros(len(idx_selected)), c='red', s=20)
    
    plt.legend()
    plt.title('Selected Geometries by FPS')
    plt.ylabel('Energy [eV]')
    plt.xlabel('Time [fs]')
    
    plt.savefig('FPS-energies-' + name + '.png', dpi=200)

if __name__=='__main__':
    
    parser = argparse.ArgumentParser(
        description='Select data after FPS was done.' 
    )
    parser.add_argument('infile', type=str, help='Original data')
    parser.add_argument('permfile', type=str, help='.npy file with permutations')
    parser.add_argument('outfile', type=str)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--distance', type = float, default=None,
     help='What distance should be between point at the cuttof')
    group.add_argument('-n', '--nstructures', type=int, default=None,
     help='How many structures to use. Either this or the distance parameter should be selected')


    args = parser.parse_args()
    assert((args.distance is None) != (args.nstructures is None)) #For testing purposes

    main(args.infile, args.permfile, args.outfile, args.distance, args.nstructures)
