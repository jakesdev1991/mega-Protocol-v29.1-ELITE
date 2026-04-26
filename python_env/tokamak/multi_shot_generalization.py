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
import pandas as pd
from sklearn.metrics import roc_curve, auc

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

def get_disruption_time(data):
    peak_val = np.max(data)
    peak_idx = np.argmax(data)
    quench_threshold = 0.1 * peak_val
    post_peak = data[peak_idx:]
    quench_indices = np.where(post_peak < quench_threshold)[0]
    if len(quench_indices) > 0:
        return peak_idx + quench_indices[0]
    return len(data) - 1

def run_multi_shot_validation():
    print("🔬 [Generalization] Starting Multi-Shot Omega Protocol Validation...")
    
    csv_path = "tokamak/Tokamak_Data_Extracted.csv"
    
    # Define columns to test (Plasma Current / Rogowski coils)
    target_cols = [
        "Figure11/T094124/PlasmaRogA",
        "Figure11/T093863/PlasmaRogA",
        "Figure11/T093727/PlasmaRogA",
        "Figure18/T092680/PlasmaRogA",
        "Figure18/T092689/PlasmaRogA",
        "Figure18/T092727/PlasmaRogA",
        "Figure18/T093250/PlasmaRogA",
        "Figure14/T097031/PlasmaRogA",
        "Figure14/T096987/PlasmaRogA"
    ]
    
    results = []
    warning_window = 1000 # Ticks
    window_size = 10
    
    for col in target_cols:
        print(f"\n📡 Processing {col}...")
        
        # Load column efficiently
        try:
            # Use chunks to avoid OOM
            chunks = pd.read_csv(csv_path, usecols=[col], chunksize=50000)
            series_list = []
            for chunk in chunks:
                series_list.append(chunk[col].dropna().values)
            series = np.concatenate(series_list)
        except Exception as e:
            print(f"  ❌ Error loading {col}: {e}")
            continue
            
        if len(series) < warning_window * 2:
            print("  ⚠️ Signal too short for validation.")
            continue
            
        t_disruption = get_disruption_time(series)
        print(f"  Detected Disruption at index: {t_disruption}")
        
        # Prepare evaluation window
        processed_series = series[:t_disruption]
        labels = np.zeros(len(processed_series))
        labels[max(0, t_disruption - warning_window):] = 1
        
        # Run Monitor
        monitor = RCODMonitor()
        phi_delta_values = []
        for i in range(len(processed_series)):
            if i < window_size:
                phi_delta_values.append(0.0)
                continue
            
            window = processed_series[i-window_size:i]
            window_tensor = torch.from_numpy(window).float().unsqueeze(0)
            v = layer_stat(window_tensor)
            _, phi_delta = monitor.step(v, layer_id="plasma_sensor")
            phi_delta_values.append(phi_delta)
            
        phi_delta_values = np.array(phi_delta_values)
        fpr, tpr, _ = roc_curve(labels, phi_delta_values)
        roc_auc = auc(fpr, tpr)
        
        print(f"  ✅ AUC: {roc_auc:.4f}")
        results.append({"shot": col, "auc": roc_auc})

    # Summary
    print("\n" + "="*50)
    print("📊 MULTI-SHOT VALIDATION SUMMARY")
    print("="*50)
    aucs = [r['auc'] for r in results]
    for r in results:
        print(f"{r['shot']}: {r['auc']:.4f}")
    
    print("-" * 20)
    print(f"AVERAGE AUC: {np.mean(aucs):.4f}")
    print(f"MEDIAN AUC:  {np.median(aucs):.4f}")
    print(f"STD DEV:      {np.std(aucs):.4f}")
    
    # Save report
    summary_df = pd.DataFrame(results)
    summary_df.to_csv("tokamak/multi_shot_validation_results.csv", index=False)
    print("\n✅ Final report saved to: tokamak/multi_shot_validation_results.csv")

if __name__ == "__main__":
    run_multi_shot_validation()
