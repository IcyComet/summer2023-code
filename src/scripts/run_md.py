#!/usr/bin/env python3

import sys 
sys.path.append('/storage/cmstore01/projects/Hydrocarbons/opt/summer2023-code/src')
from os.path import isfile
import argparse
from ase.io import read
from nnp import md

def main(init_geo: str,
        dir_models: str,
        Temperature: float,
        n_steps: int = 10000,
        n_potentials: int = 4,
        exclude_models: list = [],
        logging_interval: int = 20,
        restart: bool = False, 
        soft_restart: bool = False,
        rescale_velocities: bool = False,
        init_temperature: float = None,
        outfile: str = "simulation",
        time_step: float = 0.5):
    
    n_replicas = 1

    time_constant = 100 # fs
    # time_step = .5 # fs

    cutoff = 4 # A
    shell= 1 # A
    fn_models = dir_models

    if n_potentials != 1:
        fmt_models = dir_models+'train-{:03d}/best_inference_model'
        fn_models = [fmt_models.format(i) for i in range(n_potentials) if i not in exclude_models]
        if not all(map(isfile, fn_models)):
            activations = ["silu", "sigmoid", "softplus", "tanh"]
            fn_models = [dir_models.removesuffix("/") + f"/train-{activation}/best_inference_model" for \
                         activation in activations]
    

    device = 'cpu'
    
    log_file = f'{outfile}.hdf5'
    
    if restart:
        log_file = f'{outfile}_restart.hdf5'

    chk_file = f'{outfile}.chk'
    buffer_size = 1 # how many steps to store in memory before writing to disk
    
    atoms = read(init_geo, '0')
    init_temperature = Temperature if init_temperature is None else init_temperature

    md_simulator = md.md.run_md_single(
        atoms = atoms,
        fn_models=fn_models,
        log_file=log_file,
        Temperature=Temperature,
        cutoff=cutoff, 
        n_steps=n_steps,
        n_replicas=n_replicas,
        time_constant=time_constant,
        time_step=time_step,
        device=device,
        chk_file=chk_file,
        buffer_size=buffer_size,
        logging_interval=logging_interval,
        restart=restart,
        soft_restart=soft_restart,
        rescale_velocities=rescale_velocities,
        init_temperature=init_temperature
    )
    

if __name__ == '__main__':
    

    parser = argparse.ArgumentParser()
    parser.add_argument('init_geo', type=str, 
                        help='Initial geometry')
    parser.add_argument('dir_models', type=str, 
                        help='Directory with models, or model filename if single model is used.')
    parser.add_argument('-t', '--temperature', type=float, default=None,
                        help='Temperature')
    parser.add_argument('-n', '--n_steps', type=int, default=10000, 
                        help='Number of steps (default: 10000)')
    parser.add_argument('-m', '--n_models', type=int, default=4,
                        help='Number of models (default: 4)')
    parser.add_argument('-e', '--exclude_models', type=int, nargs='+', default=[],
                        help='Models to exclude (default: [])')
    parser.add_argument('-l', '--logging_interval', type=int, default=20,
                        help='Logging interval (default: 20)')
    parser.add_argument('-r', '--restart', action='store_true',
                        help='Restart simulation (default: False)')    
    parser.add_argument('-s', '--soft_restart', action='store_true',
                        help='Soft restart simulation (default: False)')
    parser.add_argument('-v', '--rescale_velocities', action='store_true',
                        help='Rescale velocities to current temperature when restartin (default: False)')
    parser.add_argument('-i', '--init_temperature', type=float, default=None,
                        help='Initial temperature if none is given use temperature instead (default: None)')
    parser.add_argument("-o", "--outfile", type=str, default="simulation", help="name of the output files (don't include file ending)")
    parser.add_argument("-fs", "--timestep", type=float, default=0.5)

    
    args = parser.parse_args()
    main(
        args.init_geo, 
        args.dir_models, 
        args.temperature, 
        args.n_steps, 
        args.n_models, 
        args.exclude_models, 
        args.logging_interval, 
        args.restart, 
        args.soft_restart, 
        args.rescale_velocities, 
        args.init_temperature,
        args.outfile,
        args.timestep)