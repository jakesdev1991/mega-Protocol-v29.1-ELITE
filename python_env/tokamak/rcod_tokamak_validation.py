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
import argparse

# Add project root to path to import rcod
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

def run_validation(column_name):
    print(f"🚀 Running RCOD Validation on Tokamak sensor: {column_name}")
    
    csv_path = os.path.join(os.path.dirname(__file__), "Tokamak_Data_Extracted.csv")
    if not os.path.exists(csv_path):
        print(f"❌ Data file {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    if column_name not in df.columns:
        print(f"❌ Column {column_name} not found in CSV.")
        return

    # Drop NaNs for the selected column
    series = df[column_name].dropna().values
    print(f"Data points: {len(series)}")

    monitor = RCODMonitor()
    phi_n_values = []
    phi_delta_values = []
    shocks = []
    
    # We simulate a rolling window similar to the C++ InertialSubstrate
    window_size = 10
    
    import torch
    
    print("Processing stream...")
    for i in range(window_size, len(series)):
        window = series[i-window_size:i]
        window_tensor = torch.from_numpy(window).float().unsqueeze(0)
        v = layer_stat(window_tensor)
        phi_n, phi_delta = monitor.step(v, layer_id="plasma_sensor")
        phi_n_values.append(phi_n)
        phi_delta_values.append(phi_delta)

        if phi_delta > 0.5: # Using AI Tuned threshold
            shocks.append(i)
    print(f"Validation Complete. Total Shocks: {len(shocks)}")
    
    # Plotting
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(series, label="Raw Sensor Signal", color='blue')
    plt.title(f"Tokamak Signal: {column_name}")
    plt.ylabel("Value")
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    padded_phi_delta = [0]*window_size + phi_delta_values
    plt.plot(padded_phi_delta, label="Phi_Delta (Asymmetry Mode)", color='red')
    plt.axhline(y=0.5, color='orange', linestyle='--', label="AI Tuned Threshold")
    plt.title("v26.0 Omega Protocol Disruption Prediction")
    plt.ylabel(r"$\Phi_\Delta$")
    plt.xlabel("Ticks (10kHz)")
    plt.legend()
    plt.grid(True)
    
    clean_name = column_name.replace('/', '_').replace(' ', '_')
    output_plot = os.path.join(os.path.dirname(__file__), f"rcod_validation_{clean_name}.png")
    plt.tight_layout()
    plt.savefig(output_plot)
    print(f"✅ Plot saved to: {output_plot}")
    return output_plot

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sensor", type=str, default="Figure11/T094124/PlasmaRogA")
    args = parser.parse_args()
    
    run_validation(args.sensor)
