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
from sklearn.metrics import roc_curve, auc

# Add project root to path
PROJECT_ROOT = "/home/jake/Downloads/training"
sys.path.append(os.path.join(PROJECT_ROOT, "python_env"))

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

class DifferentialFluxSchema:
    """
    Experimental Schema v27.5-EX
    Focus: Detecting 'Information Shredding' in high-turbulence regimes.
    Logic: Uses the ratio of Volatility-Adjusted Asymmetry (VAA) across multiple time-scales.
    """
    def __init__(self, sensitivity=1.2):
        # We wrap two monitors with different base alphas to create a 'Differential Manifold'
        self.fast_monitor = RCODMonitor(num_nodes=5, node_dim=16) # High sensitivity
        self.slow_monitor = RCODMonitor(num_nodes=15, node_dim=64) # High stability
        self.sensitivity = sensitivity

    def step(self, raw_value, layer_id):
        # 1. Get signals from both manifolds
        f_phi_n, f_phi_d = self.fast_monitor.step(raw_value, f"{layer_id}_f")
        s_phi_n, s_phi_d = self.slow_monitor.step(raw_value, f"{layer_id}_s")
        
        # 2. Calculate the 'Shredding Index' (SI)
        # In a stable regime, f_phi_d and s_phi_d track each other.
        # In a shredding regime (pre-disruption), the fast monitor fractures first.
        shredding_index = abs(f_phi_d - s_phi_d) / (s_phi_d + 1e-6)
        
        # 3. Dynamic Thresholding
        # Boost the signal if fast-scale asymmetry is accelerating relative to slow-scale
        combined_signal = f_phi_d * (1.0 + self.sensitivity * shredding_index)
        
        return min(1.0, combined_signal)

def run_experimental_simulation():
    print("🚀 [Experimental Schema] Launching one-time v27.5-EX Differential Flux Test...")
    
    csv_path = "/home/jake/Downloads/training/python_env/tokamak/Tokamak_Data_Extracted.csv"
    
    # We focus on the previously problematic 'reversed' shot T093727
    # and compare it to the high-performer T093250
    test_shots = [
        {"id": "T093727 (Problematic)", "col": "Figure11/T093727/PlasmaRogA", "disrupt": 27500},
        {"id": "T093250 (Baseline)", "col": "Figure18/T093250/PlasmaRogA", "disrupt": 20000},
    ]
    
    warning_window = 1000 
    
    for shot in test_shots:
        print(f"\n--- Testing Schema against {shot['id']} ---")
        series = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            col_idx = headers.index(shot['col'])
            for row in reader:
                if row[col_idx]: series.append(float(row[col_idx]))
        
        series = np.array(series)
        t_limit = min(len(series), shot['disrupt'])
        processed_series = series[:t_limit]
        
        # Labels
        labels = np.zeros(len(processed_series))
        labels[max(0, len(processed_series) - warning_window):] = 1
        
        # Run Experimental Schema
        schema = DifferentialFluxSchema(sensitivity=1.5)
        experimental_signals = []
        
        print(f"Processing {len(processed_series)} samples...")
        for i in range(len(processed_series)):
            val = processed_series[i]
            # One-time direct sensor processing
            sig = schema.step(val, layer_id="experimental_plasma")
            experimental_signals.append(sig)
            
        experimental_signals = np.array(experimental_signals)
        
        # Calculate AUC
        fpr, tpr, _ = roc_curve(labels, experimental_signals)
        roc_auc = auc(fpr, tpr)
        
        print(f"📊 [RESULT] Experimental AUC: {roc_auc:.6f}")
        
        if "Problematic" in shot['id']:
            if roc_auc > 0.34: # Previous baseline for this shot
                improvement = ((roc_auc - 0.339090) / 0.339090) * 100
                print(f"🔥 GAIN DETECTED: +{improvement:.2f}% improvement in high-turbulence regime!")
            else:
                print("⚠️ No gain detected for problematic regime. Schema needs further divergence.")

if __name__ == "__main__":
    run_experimental_simulation()
