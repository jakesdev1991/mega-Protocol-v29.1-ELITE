# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

def plot_metrics(csv_path, output_path):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    
    # Filter out validation rows if they exist (they might have NaNs for train metrics)
    train_df = df.dropna(subset=['train_loss'])

    fig, axs = plt.subplots(3, 1, figsize=(10, 15), sharex=True)

    # Loss plot
    axs[0].plot(train_df['step'], train_df['train_loss'], label='Train Loss', color='blue', alpha=0.6)
    if 'val_loss' in df.columns:
        val_df = df.dropna(subset=['val_loss'])
        axs[0].scatter(val_df['step'], val_df['val_loss'], label='Val Loss', color='red', marker='x')
    axs[0].set_ylabel('Loss')
    axs[0].legend()
    axs[0].set_title('Training and Validation Loss')

    # RCOD plot
    axs[1].plot(train_df['step'], train_df['rcod'], label='RCOD', color='green')
    axs[1].set_ylabel('Curvature (RCOD)')
    axs[1].axhline(y=0.6, color='r', linestyle='--', alpha=0.3, label='High Threshold')
    axs[1].axhline(y=0.2, color='y', linestyle='--', alpha=0.3, label='Low Threshold')
    axs[1].legend()
    axs[1].set_title('Representation Curvature (RCOD)')

    # LR Scale plot
    axs[2].plot(train_df['step'], train_df['lr_scale'], label='LR Scale', color='purple')
    axs[2].set_ylabel('LR Scale Factor')
    axs[2].set_xlabel('Step')
    axs[2].legend()
    axs[2].set_title('Dynamic Learning Rate Scaling')

    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True, help="Path to metrics.csv")
    parser.add_argument("--out", type=str, default="training_plot.png", help="Output filename")
    args = parser.parse_args()
    plot_metrics(args.csv, args.out)
