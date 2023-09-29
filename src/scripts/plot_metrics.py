#!/usr/bin/env python

import argparse
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.size"] = 18

def plot_file(metrics_file, outfile):
    train_loss, val_loss, train_energy_MSE, val_energy_MSE, train_forces_MSE, val_forces_MSE, lr = read_metrics(metrics_file)
    fig, ((ax1, ax4), (ax2, ax3)) = plt.subplots(2, 2, figsize=(20,20))
    vls = val_loss[(vi := ~np.isnan(val_loss))]
    tls = train_loss[(ti := np.roll(np.isnan(train_loss) & vi, -1))]
    te_MSE, ve_MSE = train_energy_MSE[ti], val_energy_MSE[vi]
    tf_MSE, vf_MSE = train_forces_MSE[ti], val_forces_MSE[vi]
    ax1.semilogy(tls, "b-", label="Training", linewidth=0.5)
    ax1.semilogy(vls, "r-", label="Validation", linewidth=0.5)
    ax1.set_title("Neural Network Loss")
    ax1.set_xlabel("Epochs")
    ax1.set_ylabel("Loss Function")
    ax1.legend()
    ax2.semilogy(te_MSE, "b-", label="Training", linewidth=0.5)
    ax2.semilogy(ve_MSE, "r-", label="Validation", linewidth=0.5)
    ax3.plot(tf_MSE, "b-", label="Training", linewidth=0.5)
    ax3.plot(vf_MSE, "r-", label="Validation", linewidth=0.5)
    ax4.semilogy(lr[~np.isnan(lr)], "r-", label="Learning Rate", linewidth=1)
    # ax4.text(0.95, 0.95, f"Initial learning rate: {lr[~np.isnan(lr)][0]:.3f}", va="top", ha="right",
    #          transform=ax4.transAxes)
    ax2.legend()
    ax2.set_title("Neural Network Energy MSE")
    ax2.set_xlabel("Epochs")
    ax2.set_ylabel("Energy MSE ([eV]^2)")
    ax3.legend()
    ax3.set_xlabel("Epochs")
    ax3.set_ylabel("Forces MSE ([ev/Ang]^2)")
    ax3.set_title("Neural Network Forces MSE")
    # ax4.legend()
    ax4.set_xlabel("Epochs")
    ax4.set_ylabel("Learning Rate")
    ax4.set_title("Optimizer Learning Rate")
    fig.suptitle("Neural Network Training Metrics", fontweight="bold")
    fig.tight_layout()
    fig.savefig(outfile)
    return

def read_metrics(metrics_file):
    metrics = np.genfromtxt(metrics_file, dtype=np.float_, delimiter=",", missing_values="", \
                            filling_values=np.NaN, names=True)
    epochs = metrics["epoch"]
    train_loss = metrics["train_loss"]
    val_loss = metrics["val_loss"]
    train_energy_MSE = metrics["train_energy_MSE"]
    val_energy_MSE = metrics["val_energy_MSE"]
    train_forces_MSE = metrics["train_forces_MSE"]
    val_forces_MSE = metrics["val_forces_MSE"]
    try:
        lr = metrics["lr_schedule"]
    except ValueError:
        lr = None
    return train_loss,val_loss,train_energy_MSE,val_energy_MSE,train_forces_MSE,val_forces_MSE,lr

def add_plot(metrics_file, fig, ax1, ax2, ax3, ax4, title=""):
    train_loss, val_loss, train_energy_MSE, val_energy_MSE, train_forces_MSE, val_forces_MSE, lr = read_metrics(metrics_file)
    vls = val_loss[(vi := ~np.isnan(val_loss))]
    tls = train_loss[(ti := np.roll(np.isnan(train_loss) & vi, -1))]
    te_MSE, ve_MSE = train_energy_MSE[ti], val_energy_MSE[vi]
    tf_MSE, vf_MSE = train_forces_MSE[ti], val_forces_MSE[vi]
    ax1.semilogy(tls, label=f"{title} training", linewidth=0.5)
    ax1.semilogy(vls, label=f"{title} validation", linewidth=0.5)
    ax2.semilogy(te_MSE, label=f"{title} training", linewidth=0.5)
    ax2.semilogy(ve_MSE, label=f"{title} validation", linewidth=0.5)
    ax3.semilogy(tf_MSE, label=f"{title} training", linewidth=0.5)
    ax3.semilogy(vf_MSE, label=f"{title} validation", linewidth=0.5)
    if lr is not None:
        ax4.semilogy(lr[~np.isnan(lr)], label=title, linewidth=1)
    return

def plot_multiple(metrics_files, outfile):
    fig, ((ax1, ax4), (ax2, ax3)) = plt.subplots(2, 2, figsize=(20,20))
    for metric_file in metrics_files:
        title = metric_file.removesuffix(".csv").split("/")[-1].replace("-", " ")
        add_plot(metric_file, fig, ax1, ax2, ax3, ax4, title)
    ax1.set_title("Neural Network Loss")
    ax1.set_xlabel("Epochs")
    ax1.set_ylabel("Loss Function")
    ax1.legend()
    ax2.legend()
    ax2.set_title("Neural Network Energy MSE")
    ax2.set_xlabel("Epochs")
    ax2.set_ylabel("Energy MSE ([eV]^2)")
    ax3.legend()
    ax3.set_xlabel("Epochs")
    ax3.set_ylabel("Forces MSE ([ev/\u212B]^2)")
    ax3.set_title("Neural Network Forces MSE")
    ax4.legend()
    ax4.set_xlabel("Epochs")
    ax4.set_ylabel("Learning Rate")
    ax4.set_title("Optimizer Learning Rate")
    fig.suptitle("Neural Network Training Metrics")
    fig.tight_layout()
    fig.savefig(outfile)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("metricsfile", type=str, help="CSV file containting training metrics")
    parser.add_argument("-o", "--outfile", type=str, help="Name of the file where the figure will be stored")
    parser.add_argument("files", type=str, nargs="+", help="paths to metrics files")
    args = parser.parse_args()
    # plot_file(args.metricsfile, args.outfile)
    plot_multiple(args.files, args.outfile)