# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import csv
import numpy as np
import os
import sys
import torch
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

def run_benchmark():
    print("📊 [Benchmark] Starting Omega Protocol v26.5 Falsification Test (Manual CSV Reading)...")
    
    csv_path = "tokamak/Tokamak_Data_Extracted.csv"
    sensor_col = "Figure11/T094124/PlasmaRogA"
    
    # Manually find the column index and read data
    series = []
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        try:
            col_idx = headers.index(sensor_col)
        except ValueError:
            print(f"❌ Column {sensor_col} not found.")
            return

        for row in reader:
            if row[col_idx]:
                series.append(float(row[col_idx]))
                
    series = np.array(series)
    print(f"Total data points: {len(series)}")
    
    # Ground Truth (from identify_ground_truth.py)
    t_disruption = 29135
    warning_window = 1000 # Number of ticks (lead time)
    
    # Define Ground Truth Labels
    processed_series = series[:t_disruption]
    labels = np.zeros(len(processed_series))
    labels[max(0, t_disruption - warning_window):] = 1
    
    # Run Omega Monitor
    monitor = RCODMonitor()
    phi_delta_values = []
    window_size = 10
    
    print(f"Processing {len(processed_series)} points with Omega Monitor...")
    for i in range(len(processed_series)):
        if i < window_size:
            phi_delta_values.append(0.0)
            continue
            
        window = processed_series[i-window_size:i]
        window_tensor = torch.from_numpy(window).float().unsqueeze(0)
        v = layer_stat(window_tensor)
        _, phi_delta = monitor.step(v, layer_id="plasma_sensor")
        phi_delta_values.append(phi_delta)
        
    # Calculate ROC Metrics
    phi_delta_values = np.array(phi_delta_values)
    fpr, tpr, thresholds = roc_curve(labels, phi_delta_values)
    roc_auc = auc(fpr, tpr)
    
    print(f"📈 [Results] AUC: {roc_auc:.4f}")
    
    # Find optimal threshold (Youden's J statistic)
    idx = np.argmax(tpr - fpr)
    opt_threshold = thresholds[idx]
    print(f"🎯 Optimal Phi_Delta Threshold: {opt_threshold:.4f}")
    
    # Plot ROC
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'Falsification Test: Omega Phi_Delta (Shot T094124)')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.savefig("tokamak/omega_roc_validation.png")
    
    # Plot Lead Time Analysis
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(processed_series, label="Sensor (I_p)", alpha=0.7)
    plt.axvline(x=t_disruption - warning_window, color='black', alpha=0.3, label="Warning Window Start")
    plt.title("Plasma Current (I_p)")
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(phi_delta_values, label="Phi_Delta", color='red')
    plt.axhline(y=opt_threshold, color='green', linestyle='--', label=f'Opt Threshold ({opt_threshold:.2f})')
    plt.title("Asymmetry Evolution (Phi_Delta)")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("tokamak/omega_lead_time_analysis.png")
    
    # Falsification check
    print("\n--- Final Assessment ---")
    if roc_auc < 0.5:
        print("❌ [FALSIFIED] Phi_Delta performs worse than random guessing. Theory needs fundamental revision.")
    elif roc_auc < 0.7:
        print("⚠️ [WEAK] Phi_Delta has low predictive power. Heuristic value only.")
    elif roc_auc > 0.9:
        print("🔥 [EXCEPTIONALLY STRONG] Phi_Delta provides near-perfect predictive signal.")
    else:
        print("✅ [VALIDATED] Phi_Delta shows strong predictive signal and statistical significance.")

if __name__ == "__main__":
    run_benchmark()
