# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import torch

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

def run_multi_scale_analysis():
    print("🚀 [Finance Branch] Starting Multi-Scale RCOD Analysis (Bitcoin Inception to Present)...")
    
    # 1. Load data
    df = pd.read_csv('finance/btc_historical_full.csv', index_col='Date', parse_dates=True)
    prices = df['Close'].values
    dates = df.index
    
    print(f"Analyzing {len(prices)} days of price action.")
    
    # 2. Multi-Scale Config
    scales = {
        "Micro (10d)": 10,
        "Monthly (30d)": 30,
        "Quarterly (90d)": 90,
        "Annual (365d)": 365
    }
    
    results = {}
    
    for label, window_size in scales.items():
        print(f"--- Computing Scale: {label} ---")
        monitor = RCODMonitor()
        phi_delta_series = np.zeros(len(prices))
        
        for i in range(window_size, len(prices)):
            # Extract and normalize window
            window = prices[i-window_size:i]
            norm_window = (window - np.mean(window)) / (np.std(window) + 1e-6)
            
            # Step monitor
            window_tensor = torch.from_numpy(norm_window).float().unsqueeze(0)
            v = layer_stat(window_tensor)
            _, phi_delta = monitor.step(v, layer_id=f"btc_{window_size}")
            
            phi_delta_series[i] = phi_delta
            
        results[label] = phi_delta_series

    # 3. Visualization
    fig, axes = plt.subplots(len(scales) + 1, 1, figsize=(15, 20), sharex=True)
    
    # Plot Price (Log scale for long history)
    axes[0].plot(dates, prices, color='gold', label="BTC/USD (Log Scale)")
    axes[0].set_yscale('log')
    axes[0].set_title("Bitcoin Price History (Inception-Present)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    
    # Plot RCOD at different scales
    for i, (label, series) in enumerate(results.items()):
        ax = axes[i+1]
        ax.plot(dates, series, label=f"Phi_Delta ({label})", color='red', alpha=0.8)
        ax.axhline(y=0.6, color='orange', linestyle='--', alpha=0.5, label="Instability Threshold")
        ax.set_ylabel("Asymmetry")
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.2)
        ax.legend(loc='upper left')
        
    plt.xlabel("Timeline")
    plt.tight_layout()
    output_path = "finance/btc_multi_scale_analysis.png"
    plt.savefig(output_path)
    print(f"\n✅ Multi-scale analysis complete. Results saved to: {output_path}")

if __name__ == "__main__":
    run_multi_scale_analysis()
