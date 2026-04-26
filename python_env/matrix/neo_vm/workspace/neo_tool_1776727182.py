# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# DEMONSTRATION: The PICM-Ω framework collapses under strategic manipulation
# and survivorship bias. The phi^4 field theory is mathematical theater.

def strategic_manipulation_simulation():
    """
    Shows that once companies know they're being monitored for cadence,
    they can game the system, making the signal *anti-predictive*.
    """
    np.random.seed(42)
    n_companies = 500
    
    # True financial health (latent variable)
    true_health = np.random.normal(0.5, 0.2, n_companies)
    true_health = np.clip(true_health, 0, 1)
    
    # Companies have a "gaming sophistication" score
    gaming_sophistication = np.random.beta(2, 5, n_companies)  # Most are naive
    
    # Before monitoring: natural presentation behavior
    # After monitoring: companies game the cadence score
    
    results = []
    for i in range(n_companies):
        health = true_health[i]
        gaming = gaming_sophistication[i]
        
        # Natural behavior (what PICM-Ω assumes)
        if health > 0.4:
            natural_intervals = np.random.normal(45, 15, size=8)
        else:
            natural_intervals = np.random.exponential(60, size=4)  # Irregular when stressed
        
        # Gaming behavior: companies reverse-engineer the CCS formula
        # They know: CCS = exp(-sigma/mu) * exp(-N_cluster/T)
        # So they artificially smooth intervals and avoid clustering
        if gaming > 0.3 and health < 0.4:  # Sophisticated but stressed companies
            # Fake regularity by spacing presentations artificially
            # This is costly, but less costly than revealing distress
            faked_intervals = np.random.normal(50, 5, size=6)  # Artificially regular
            # Add "strategic silence" gaps to hide problems
            faked_intervals[3] = np.random.uniform(90, 120)  # One big gap
        else:
            faked_intervals = natural_intervals
        
        # Calculate observable metrics
        def calculate_metrics(intervals):
            if len(intervals) < 2:
                return np.nan, np.nan, np.nan
            mu = np.mean(intervals)
            sigma = np.std(intervals)
            # Count clusters (intervals < 7 days)
            N_cluster = np.sum(intervals <= 7)
            # CCS approximation
            ccs = np.exp(-sigma/mu) * np.exp(-N_cluster/365)
            return mu, sigma, ccs
        
        natural_mu, natural_sigma, natural_ccs = calculate_metrics(natural_intervals)
        faked_mu, faked_sigma, faked_ccs = calculate_metrics(faked_intervals)
        
        # Determine failure (health < 0.2)
        failed = health < 0.2
        
        results.append({
            'company_id': i,
            'health': health,
            'gaming': gaming,
            'failed': failed,
            'natural_ccs': natural_ccs,
            'faked_ccs': faked_ccs,
            'natural_sigma': natural_sigma,
            'faked_sigma': faked_sigma
        })
    
    df = pd.DataFrame(results)
    
    # Analysis: Does CCS predict failure?
    # Before gaming
    corr_natural = np.corrcoef(df['natural_ccs'], 1-df['failed'])[0,1]
    # After gaming
    corr_faked = np.corrcoef(df['faked_ccs'], 1-df['failed'])[0,1]
    
    print("=== STRATEGIC MANIPULATION ANALYSIS ===")
    print(f"Natural CCS vs Survival correlation: {corr_natural:.3f}")
    print(f"Post-gaming CCS vs Survival correlation: {corr_faked:.3f}")
    print(f"Signal degradation: {corr_natural - corr_faked:.3f}")
    
    # False sense of security: stressed companies appear MORE regular
    stressed = df[df['health'] < 0.3]
    print(f"\nAmong stressed companies (health < 0.3):")
    print(f"Natural CCS (truth): {stressed['natural_ccs'].mean():.3f}")
    print(f"Faked CCS (illusion): {stressed['faked_ccs'].mean():.3f}")
    
    # Plot the deception
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Scatter: True health vs Perceived CCS
    ax1.scatter(df['health'], df['natural_ccs'], alpha=0.5, label='Natural (Truth)')
    ax1.scatter(df['health'], df['faked_ccs'], alpha=0.5, label='Post-Gaming (Illusion)')
    ax1.axvline(0.3, color='r', linestyle='--', label='Distress Threshold')
    ax1.set_xlabel('True Financial Health')
    ax1.set_ylabel('Cadence Coherence Score (CCS)')
    ax1.set_title('Gaming Creates False Signal')
    ax1.legend()
    
    # Histogram of CCS for failed vs non-failed
    ax2.hist(df[~df['failed']]['faked_ccs'], bins=20, alpha=0.5, label='Survived (Faked)', density=True)
    ax2.hist(df[df['failed']]['faked_ccs'], bins=20, alpha=0.5, label='Failed (Faked)', density=True)
    ax2.set_xlabel('Faked CCS')
    ax2.set_ylabel('Density')
    ax2.set_title('Failed Companies Look MORE Stable After Gaming')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
    
    return df

# Run the disruption
df_gaming = strategic_manipulation_simulation()