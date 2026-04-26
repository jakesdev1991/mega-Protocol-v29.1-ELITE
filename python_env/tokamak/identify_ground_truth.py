# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def find_disruption():
    csv_path = "tokamak/Tokamak_Data_Extracted.csv"
    # Load only necessary column to save memory
    col = "Figure11/T094124/PlasmaRogA"
    df = pd.read_csv(csv_path, usecols=[col])
    data = df[col].dropna().values
    
    # Simple disruption detection: 
    # A disruption is often where the current drops below 10% of its peak
    peak_val = np.max(data)
    peak_idx = np.argmax(data)
    
    # Find the quench: first time after peak it drops below 10% of peak
    quench_threshold = 0.1 * peak_val
    post_peak = data[peak_idx:]
    quench_indices = np.where(post_peak < quench_threshold)[0]
    
    if len(quench_indices) > 0:
        disruption_idx = peak_idx + quench_indices[0]
        print(f"Detected Disruption for {col} at index {disruption_idx}")
    else:
        print("No disruption detected via 10% threshold.")
        disruption_idx = len(data) - 1

    # Plot to verify
    plt.figure(figsize=(10, 4))
    plt.plot(data)
    plt.axvline(x=disruption_idx, color='r', linestyle='--', label='Disruption Point')
    plt.title(f"Ground Truth Analysis: {col}")
    plt.legend()
    plt.savefig("tokamak/ground_truth_T094124.png")
    
    return disruption_idx, len(data)

if __name__ == "__main__":
    find_disruption()
