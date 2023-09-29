#!/usr/bin/env python3

import sys
sys.path.append('/storage/cmstore01/projects/Hydrocarbons/opt/summer2023-code/src')

from pytorch_lightning.strategies import DDPStrategy
from nnp.training.training import * 
import argparse
from pytorch_lightning.tuner import Tuner

def main(fn_db: str, epochs: int, activation: str, n_cpu_data: int, n_cpu_train: int, cutoff: float, batch_size: int = 1, checkpoint: str = None):
    
    # TODO: Check if there is a better strategy 
    device = 'cpu'
    strategy = DDPStrategy(find_unused_parameters=False)
    # change to 'auto' for automatic selection 
    # 'gpu' for cuda only
    
    # Files of reference data
    dir_nl_cache = 'nl_cache'

    # Data Settings

    ## Model Settings
    n_layers = 2  # Number of dense layers
    n_hidden = 20  # Size of the hidden layers
    n_interactions = 3
    n_features = 128
    n_gaussians = 25

    # Train settings
    rho = .1  # tradeoff parameter for loss function
    learning_rate = 1e-4  # Initial learning rate

    transforms, postprocess = get_transforms(
        dir_nl_cache, 
        cutoff
    )
    
    dataset = prepare_data(
        fn_db, 
        n_cpu_data,
        batch_size, 
        transforms
    )

    task_kwargs = {"cutoff" : cutoff,
                   "n_layers" : n_layers,
                   "n_hidden" : n_hidden,
                   "n_interactions" : n_interactions,
                   "n_features" : n_features,
                   "n_gaussians" : n_gaussians,
                   "rho" : rho,
                   "learning_rate" : learning_rate,
                   "postprocess": postprocess,
                   "activation" : activation}
    
    task = get_task(**task_kwargs)

    trainer = get_trainer(
        device, 
        epochs, 
        n_cpu_train,
        use_logger=False,
        strategy=strategy
    )
    
    tuner = Tuner(trainer) # FIXME
    lr_finder = tuner.lr_find(task, datamodule=dataset, early_stop_threshold=None, min_lr=1e-6, max_lr=0.1)
    task_kwargs["learning_rate"] = lr_finder.suggestion()
    task = get_task(**task_kwargs)
    print(task.__dict__)
    trainer.fit(task, dataset, ckpt_path=checkpoint)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Starts Schnetpack model trainaing with predifined parameters' 
    )
    
    parser.add_argument('infile', type=str, 
        help='Files with training data.')
    parser.add_argument('-p', '--epochs', type=int, required=False, default=-1, 
        help='How many epochs, if not chosen runs till convergence or otherwise stops.')
    parser.add_argument('-a','--activation', type=str, required=False, default='silu', 
        help='What activation function to use (silu (deafault), softplus, tanh, sigmoid)')
    parser.add_argument('-n', '--n_cpu_train', type=int, required=False, default=1,
        help='How many cores for training')
    parser.add_argument('-m', '--n_cpu_data', type=int, required=False, default=1,
        help='How many cores for data loading')
    parser.add_argument('-t', '--cutoff', type=float, required=False, default=4.0,
        help='Descriptor cutoff')
    parser.add_argument('-b', '--batch_size', type=int, required=False, default=1,
        help='Batch size')
    parser.add_argument('-c', '--checkpoint', type=str, required=False, default=None,
                        help='If set training will be continued from checkpoint')
    
    args = parser.parse_args()

    main(fn_db = args.infile, 
        epochs= args.epochs,
        activation= args.activation,
        n_cpu_train = args.n_cpu_train,
        n_cpu_data = args.n_cpu_data,
        cutoff = args.cutoff,
        batch_size = args.batch_size,
        checkpoint = args.checkpoint,)
