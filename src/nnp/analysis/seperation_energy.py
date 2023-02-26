import schnetpack as spk
import schnetpack.transform as trn
import torch
import numpy as np
import matplotlib.pyplot as plt

import ase
from ase.io import read

def get_calculator(fn_model: str) -> spk.interfaces.SpkCalculator:
    """Get calculator for a given model.
    
    Parameters:
        fn_model (str): path to model

    Returns:
        calculator (spk.interfaces.SpkCalculator): calculator
    """

    calulator = spk.interfaces.SpkCalculator(
        model_file = fn_model,
        neighbor_list=trn.ASENeighborList(cutoff=4.0),
        energy_key = 'energy',
        forces_key = 'forces',
        energy_unit ='eV',
        position_unit='Ang'
    )
    return calulator


def get_schent_energy(
        atoms: ase.Atoms, 
        calculator: spk.interfaces.SpkCalculator
        ) -> float:
    """Get energy of a structure using SchNetPack.

    Parameters:
        atoms (ase.Atoms): structure
        calculator (spk.interfaces.SpkCalculator): calculator

    Returns:
        energy (float): energy of the structure
    """
    atoms.set_calculator(calculator)
    energy = atoms.get_potential_energy()
    return energy


def get_schnet_energies(atoms: ase.Atoms,
    calculators: list
    )-> np.array :
    """Get energies of a structure using SchNetPack.

    Parameters:
        atoms (ase.Atoms): structure
        calculators (list): list of calculators
    
    Returns:
        energies (np.array): energies of the structure
    """
    energies = np.zeros(len(calculators))
    for i, calculator in enumerate(calculators):
        energies[i] = get_schent_energy(atoms, calculator)
    return energies


def seperation_energy(
    fn_data: str,
    dir_model: str,
    fn_reference: str = None,
    align: bool = True, 
    n_models: int = 4,
    exclude: list = [],
    ) -> tuple((np.array, np.array, np.array)):
    """Calculate seperation energy.

    Parameters:
        fn_data (str): path to data
        fn_reference (str): path to reference data
        dir_model (str): path to models
        align (bool): use offset to align energies
        n_models (int): number of models
        exclude (list): list of model indecies to exclude

    Returns:
        mean_schnet (np.array): mean of energies
        std_schnet (np.array): std of energies
        if fn_reference is not None:
            reference_energies (np.array): energies from reference
    """
    
    # read data
    traj = read(fn_data, index=':')
    
    # get models
    fmt_model = dir_model+'/train-{:03d}/best_inference_model'
    fn_models = [fmt_model.format(i) for i in range(n_models) if i not in exclude]

    # get energies
    calculators = [get_calculator(mod) for mod in fn_models]
    schnet_energies = np.array([get_schnet_energies(atoms, calculators) for atoms in traj])

    # calculate mean and std of schnet energies
    mean_schnet = np.mean(schnet_energies, axis=1)
    std_schnet = np.std(schnet_energies, axis=1)

    if fn_reference is not None:
        # read reference data
        traj_reference = read(fn_reference, index=':')
        reference_energies = np.array([atoms.get_potential_energy() for atoms in traj_reference])

        # align energies
        offset = np.min(reference_energies) - np.min(mean_schnet) if align else 0
        mean_schnet += offset
        schnet_energies += offset

        return mean_schnet, std_schnet, reference_energies
    
    return mean_schnet, std_schnet