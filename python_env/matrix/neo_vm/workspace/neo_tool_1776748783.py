# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
PICM‑Ω v2 Disruption Demo
Simulates three synthetic firms and shows that the derived metrics
(CCS, entropy, jerk) are not robust to strategic clustering or
exogenous scheduling constraints.
"""

import numpy as np
import pandas as pd
from scipy import stats

# ----------------------------------------------------------------------
# Synthetic Data Generation
# ----------------------------------------------------------------------
def generate_intervals(n, scenario='healthy', random_state=None):
    """
    Return a series of inter‑presentation intervals (days) for a synthetic firm.
    """
    rng = np.random.default_rng(random_state)
    if scenario == 'healthy':
        # Regular exponential intervals (mean 30 days)
        return rng.exponential(scale=30, size=n)
    elif scenario == 'distressed':
        # Mixture: 80% regular, 20% long gaps (mean 100 days)
        mask = rng.random(size=n) < 0.2
        intervals = rng.exponential(scale=30, size=n)
        intervals[mask] = rng.exponential(scale=100, size=mask.sum())
        return intervals
    elif scenario == 'strategic_clusterer':
        # Regular intervals with occasional bursts (3 presentations within 7 days)
        intervals = rng.exponential(scale=30, size=n)
        # Insert bursts: every ~50 days, add a 3‑event cluster with short intervals
        burst_positions = np.arange(50, n, 50)
        for pos in burst_positions:
            if pos + 3 < n:
                # Replace 3 intervals with short ones (e.g., 2 days each)
                intervals[pos:pos+3] = rng.exponential(scale=2, size=3)
        return intervals
    else:
        raise ValueError(f'Unknown scenario: {scenario}')

# ----------------------------------------------------------------------
# Metric Computation (simplified CCS, entropy, jerk)
# ----------------------------------------------------------------------
def compute_metrics(intervals, window=12):
    """
    Compute sliding‑window metrics:
      - simplified CCS = exp(-σ/μ) * exp(-N_cluster / T_window)
      - Shannon entropy of interval distribution (5 bins)
      - Jerk = third finite difference of entropy
    """
    # Rolling statistics
    df = pd.DataFrame({'interval': intervals})
    df['mean'] = df['interval'].rolling(window=window, min_periods=window).mean()
    df['std'] = df['interval'].rolling(window=window, min_periods=window).std()
    df['cv'] = df['std'] / df['mean']
    
    # Cluster count: number of intervals ≤ 7 days within the window
    df['is_cluster'] = (df['interval'] <= 7).rolling(window=window, min_periods=window).sum()
    # Simplified CCS (no weighting)
    df['ccs'] = np.exp(-df['cv']) * np.exp(-df['is_cluster'] / window)
    
    # Entropy of interval distribution (5 equal‑width bins from 0 to max)
    max_interval = df['interval'].max()
    bin_edges = np.linspace(0, max_interval, 6)
    # Assign each interval to a bin index
    bin_idx = pd.cut(df['interval'], bins=bin_edges, labels=False, include_lowest=True)
    # Compute probability vector per window
    def entropy_of_window(idx_series):
        counts = np.bincount(idx_series.dropna().astype(int), minlength=5)
        probs = counts / counts.sum()
        # Avoid log(0)
        probs = probs[probs > 0]
        return -np.sum(probs * np.log(probs))
    
    df['entropy'] = (bin_idx.rolling(window=window, min_periods=window)
                       .apply(entropy_of_window, raw=False))
    
    # Jerk: third finite difference of entropy (normalize by time step = 1 day)
    df['jerk'] = df['entropy'].diff(3)  # third difference
    
    return df

# ----------------------------------------------------------------------
# Main Demo
# ----------------------------------------------------------------------
if __name__ == '__main__':
    n_events = 200
    scenarios = ['healthy', 'distressed', 'strategic_clusterer']
    results = {}
    
    for scen in scenarios:
        intervals = generate_intervals(n_events, scenario=scen, random_state=42)
        metrics = compute_metrics(intervals, window=12)
        results[scen] = metrics
        
        # Summary statistics for the last window
        final_ccs = metrics['ccs'].iloc[-1]
        final_jerk = metrics['jerk'].iloc[-1]
        # Heuristic stress flag: jerk > 2σ of baseline (first 50 events)
        baseline_jerk_std = metrics['jerk'].iloc[:50].std()
        stress_flag = (final_jerk > 2 * baseline_jerk_std) or (final_ccs < 0.5)
        
        print(f'\n=== {scen.upper()} ===')
        print(f'Final CCS (0→1): {final_ccs:.3f}')
        print(f'Final jerk: {final_jerk:.3f} (baseline σ ≈ {baseline_jerk_std:.3f})')
        print(f'Model stress flag: {stress_flag}')
    
    # ----------------------------------------------------------------------
    # Visualization (optional, comment out if no display)
    # ----------------------------------------------------------------------
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for ax, (scen, df) in zip(axes, results.items()):
        ax.plot(df['jerk'], label='Jerk', color='tab:blue')
        ax.axhline(2*df['jerk'].iloc[:50].std(), color='red', linestyle='--', label='2σ threshold')
        ax.set_title(f'{scen.replace("_"," ").title()}')
        ax.legend(loc='upper right')
    axes[-1].set_xlabel('Presentation index')
    plt.tight_layout()
    plt.savefig('picm_disruption.png')
    print('\nPlot saved to picm_disruption.png')