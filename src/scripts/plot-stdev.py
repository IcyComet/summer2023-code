#!/usr/bin/env python

import argparse
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def main(stdevfile, fpsfile, outfile):
    composition = stdevfile.rsplit("/")[-1].removesuffix("-sigma-vectors.npz")
    fps_ranks = np.load(fpsfile)
    vectors = np.load(stdevfile)
    try:
        vecs = vectors["inner"]
    except KeyError:
        vecs = vectors["outer"]
    sigmas = np.linalg.norm(vecs, axis=1)
    sigma_ranks = np.argsort(sigmas)[::-1] #FIXME?
    traj_fps, traj_sigmas = ranks_to_indices(fps_ranks), ranks_to_indices(sigma_ranks)
    spearman = stats.spearmanr(traj_fps, traj_sigmas)
    correlation, p_value = spearman.statistic, spearman.pvalue
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,9))
    ax1.scatter(traj_fps[1:], traj_sigmas[1:], s=9)
    ax1.set_xlabel("FPS Rank")
    ax1.set_ylabel("Standard Deviation Rank")
    present = lambda s: s.replace("_", " ").replace("gpa", "GPa")
    ax1.set_title(f"{present(composition)} FPS and Standard Deviation Ranks")
    fig.text(0, 0, f"Spearman rank\ncorrelation coefficient: {correlation:.3}", in_layout=True,\
             ha="left", va="bottom")
    ax2.plot(sigmas, "k-", linewidth=0.5, zorder=1)
    cutoff = 100
    sc = ax2.scatter(fps_ranks[:cutoff], sigmas[fps_ranks[:cutoff]], c=np.arange(cutoff), cmap="plasma",\
                zorder=2, s=25, label=f"FPS top {cutoff}")
    fig.colorbar(sc, ax=ax2, label="FPS Rank")
    ax2.set_xlabel("Configuration")
    ax2.set_ylabel("Standard Deviation")
    ax2.set_title(f"{present(composition)} Trajectory")
    ax2.legend()
    fig.tight_layout()
    fig.savefig(outfile)
    return

def ranks_to_indices(ranked):
    indexed = np.zeros_like(ranked)
    indexed[ranked] = np.arange(np.size(ranked))
    return indexed

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stdevfile", type=str, help=".npz file containing standard deviations of SOAP vectors")
    parser.add_argument("fpsfile", type=str, help="-perm.npy file containing fps ranking")
    parser.add_argument("-o", "--outfile", type=str, help="file where figures are saved")
    args = parser.parse_args()
    main(args.stdevfile, args.fpsfile, args.outfile)