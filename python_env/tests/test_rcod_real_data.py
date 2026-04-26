# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import pandas as pd
import numpy as np
import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from rcod.geometry import calculate_geometry
from agent_zero.framework.governor import OmegaGovernor, Regime

def test_on_real_data():
    print("Loading tokamak sample data...")
    try:
        df = pd.read_csv("tokamak_sample.csv")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Group by discharge_ID to process each pulse separately
    groups = df.groupby("discharge_ID")
    
    governor = OmegaGovernor()
    
    for discharge_id, group in groups:
        print(f"\nAnalyzing Discharge ID: {discharge_id}")
        
        # Use 'density' as the primary signal for RCOD
        density_signal = group["density"].values
        
        # Calculate 'overlaps' as similarity between consecutive density points
        # For numerical data, we can define similarity as 1 - normalized_diff
        # or some other geometric metric. 
        # Here we'll use a simple ratio to simulate the 'overlap' concept
        overlaps = [1.0]
        for i in range(1, len(density_signal)):
            prev = density_signal[i-1]
            curr = density_signal[i]
            if prev == 0 and curr == 0:
                overlap = 1.0
            elif prev == 0 or curr == 0:
                overlap = 0.0
            else:
                # Simulating 'overlap' as the ratio of min to max
                overlap = min(prev, curr) / max(prev, curr)
            overlaps.append(overlap)
            
        mu_history = [1.0 - overlap for overlap in overlaps] # Using 1.0 - overlap as mu
        
        # We need to feed this into calculate_geometry
        # The software expects a history dict
        history = {"overlap": overlaps, "mu_ema": mu_history}
        metrics_dict = calculate_geometry(history)
        
        print(f"RCOD Metrics: Phi={metrics_dict['phi']:.4f}, Mu={metrics_dict['mu']:.4f}, Jerk={metrics_dict['jerk']:.4f}, Theta={metrics_dict['theta']:.4f}")
        
        # Use the governor to classify the regime at each step (rolling window)
        # For simplicity, we'll just check a few points or the final state
        
        # Let's simulate a rolling window check for turbulence
        window_size = 5
        turbulence_detected = False
        for i in range(window_size, len(overlaps)):
            window = overlaps[i-window_size : i]
            # Use governor's measurement logic
            # (Note: measure_trace takes texts, but we have overlaps already)
            # We can manually calculate delta_h and classify
            
            mu = 1.0 - np.mean(window)
            volatility = float(np.mean(np.abs(np.diff(window)))) if len(window) > 1 else 0.0
            
            # Simplified delta_h calculation from governor.py
            # delta_h = min(1.0, (mu * 0.45) + (volatility * 0.35) + ...)
            delta_h = min(1.0, (mu * 0.45) + (volatility * 0.35))
            
            regime = governor._classify(mu, delta_h)
            if regime == Regime.TURBULENCE:
                print(f"⚠️ TURBULENCE DETECTED at step {i} (time {group['time'].iloc[i]:.4f})")
                turbulence_detected = True
                # Break after first detection per discharge for brevity
                break
        
        if not turbulence_detected:
            print("✅ Pulse stable (FLOW/VISCOSITY regime).")

if __name__ == "__main__":
    test_on_real_data()
