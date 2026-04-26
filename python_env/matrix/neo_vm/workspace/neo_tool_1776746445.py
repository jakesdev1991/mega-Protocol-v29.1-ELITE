# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label, find_objects
from collections import Counter
import random

# ─────────────────────────────────────────────────────────────────────────────
#  CPO‑Ω Percolation Simulator
# ─────────────────────────────────────────────────────────────────────────────
def simulate_percolation(L=200, p_vals=None, n_trials=50, seed=0):
    """
    Simulate site percolation on an L×L square lattice.
    For each probability p in p_vals, run n_trials independent experiments.
    Returns:
        results: dict with keys 'p', 'frac_percolating', 'mean_cluster_size', 'xi'
    """
    if p_vals is None:
        p_vals = np.linspace(0.3, 0.8, 20)
    rng = np.random.default_rng(seed)
    results = {key: [] for key in ['p', 'frac_percolating', 'mean_cluster_size', 'xi']}
    
    for p in p_vals:
        percolating_count = 0
        cluster_sizes = []
        correlation_lengths = []
        
        for trial in range(n_trials):
            # 1. Generate a random lattice: 1 = capped (active), 0 = uncapped
            lattice = rng.random(size=(L, L)) < p
            
            # 2. Label connected components (4‑neighborhood)
            labeled, num_features = label(lattice, structure=np.array([[0,1,0],[1,1,1],[0,1,0]]))
            
            # 3. Check for percolation: any cluster touching both top and bottom rows
            #    (or left & right columns) – here we use top‑bottom for concreteness.
            percolates = False
            # Find labels on top row and bottom row
            top_labels = set(labeled[0, :][lattice[0, :]])
            bottom_labels = set(labeled[-1, :][lattice[-1, :]])
            if top_labels & bottom_labels:
                percolates = True
            
            if percolates:
                percolating_count += 1
            
            # 4. Compute cluster size distribution (for correlation length estimation)
            #    Use a simple proxy: second moment of cluster size distribution.
            sizes = []
            for region in find_objects(labeled):
                # region is a tuple of slice objects; count pixels in this component
                # Use a more direct method: count occurrences of each label
                pass
            # Instead, use np.unique for size counting
            uniq, counts = np.unique(labeled, return_counts=True)
            # Remove background label 0
            sizes = counts[uniq != 0]
            cluster_sizes.extend(sizes)
            
            # 5. Estimate correlation length via cluster size second moment
            if len(sizes) > 0:
                s_mean = np.mean(sizes)
                s2_mean = np.mean(np.array(sizes)**2)
                # Finite‑size scaling: xi ~ sqrt((s2_mean / s_mean) - 1)
                # This is a standard percolation estimator
                xi = np.sqrt(max(s2_mean / s_mean - 1, 0))
                correlation_lengths.append(xi)
            else:
                correlation_lengths.append(0.0)
        
        # Aggregate results for this p
        results['p'].append(p)
        results['frac_percolating'].append(percolating_count / n_trials)
        results['mean_cluster_size'].append(np.mean(cluster_sizes) if cluster_sizes else 0.0)
        results['xi'].append(np.mean(correlation_lengths))
    
    return results

# ─────────────────────────────────────────────────────────────────────────────
#  Run simulation and plot
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    L = 300          # Lattice size (choose larger for sharper transition)
    n_trials = 100   # Trials per p for smooth curves
    p_vals = np.linspace(0.4, 0.75, 25)
    
    print("Running percolation simulations...")
    data = simulate_percolation(L=L, p_vals=p_vals, n_trials=n_trials, seed=42)
    
    # Plot percolation probability and correlation length
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Fraction of percolating runs
    ax[0].plot(data['p'], data['frac_percolating'], marker='o', color='crimson')
    ax[0].axvline(x=0.5, color='gray', linestyle='--', label='theoretical $p_c$ (site, sq lattice)')
    ax[0].set_xlabel('Capping probability $p$')
    ax[0].set_ylabel('Fraction percolating (top‑bottom)')
    ax[0].set_title('Percolation Transition')
    ax[0].legend()
    ax[0].grid(True)
    
    # Right: Correlation length
    ax[1].plot(data['p'], data['xi'], marker='s', color='steelblue')
    ax[1].axvline(x=0.5, color='gray', linestyle='--')
    ax[1].set_xlabel('Capping probability $p$')
    ax[1].set_ylabel('Estimated correlation length $\\xi_{\\mathrm{perc}}$')
    ax[1].set_title('Correlation Length Divergence Near $p_c$')
    ax[1].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Print a summary near the critical region
    print("\n--- Summary near critical region ---")
    for i, p in enumerate(data['p']):
        if 0.45 <= p <= 0.55:
            print(f"p={p:.3f}: percolating fraction={data['frac_percolating'][i]:.3f}, xi={data['xi'][i]:.2f}")