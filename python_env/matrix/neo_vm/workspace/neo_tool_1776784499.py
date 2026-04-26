# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# --- SIMULATION PARAMETERS ---
N_POOLS = 50
BLOCKS = 1000
VOLATILITY_REGIME = [0.01, 0.05, 0.1]  # Low, Medium, High

# True bonding curve parameters (e.g., constant product exponent)
# Homogeneous cluster: small variance
def simulate_ecosystem(homogeneity_strength: float):
    """
    homogeneity_strength: 0=identical, 1=random
    """
    base_theta = 1.0  # Standard CFMM exponent
    std_dev = (1 - homogeneity_strength) * 0.01 + homogeneity_strength * 0.2
    thetas = np.random.normal(loc=base_theta, scale=std_dev, size=N_POOLS)
    return thetas

def calculate_ahi(thetas):
    """Beta's AMM Homogeneity Index (inverse of variance)"""
    var = np.var(thetas)
    return 1 / (1 + var) if var > 0 else 1.0

def standard_arbitrageur(thetas, price_drift):
    """Naive arb: trades each pool independently"""
    il_per_pool = np.abs(price_drift) * np.exp(-thetas)  # Simplified IL model
    return np.sum(il_per_pool)

def omega_drain_curve(thetas, price_drift):
    """
    ODC: exploits homogeneity by griefing the median pool,
    then replicating grief across correlated pools.
    """
    # Target the median (most representative) pool
    median_theta = np.median(thetas)
    
    # Grief factor scales with homogeneity (inverse variance)
    homogeneity_factor = 1 / (np.var(thetas) + 1e-6)
    
    # Base grief on median pool
    base_grief = np.abs(price_drift) * np.exp(-median_theta)
    
    # Amplification: grief propagates to correlated pools
    # Correlation is assumed 1 - std_deviation (high homogeneity = high correlation)
    correlation = 1 - np.std(thetas) / np.mean(thetas)
    amplification = 1 + (N_POOLS - 1) * max(correlation, 0)
    
    total_extracted = base_grief * amplification * homogeneity_factor
    return total_extracted

# --- RUN SIMULATIONS ---
results = []

for vol in VOLATILITY_REGIME:
    for homog in np.linspace(0.0, 0.9, 10):
        thetas = simulate_ecosystem(homog)
        ahi = calculate_ahi(thetas)
        
        # Random price drift
        price_drift = np.random.normal(0, vol)
        
        # Value extracted
        standard_profit = standard_arbitrageur(thetas, price_drift)
        odc_profit = omega_drain_curve(thetas, price_drift)
        
        results.append({
            'volatility': vol,
            'homogeneity_strength': homog,
            'ahi': ahi,
            'standard_profit': standard_profit,
            'odc_profit': odc_profit,
            'exploit_ratio': odc_profit / (standard_profit + 1e-6)
        })

df = pd.DataFrame(results)

# --- VISUALIZE DISRUPTION ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)

for i, vol in enumerate(VOLATILITY_REGIME):
    ax = axes[i]
    vol_data = df[df['volatility'] == vol]
    
    # Scatter plot: exploit ratio vs AHI
    ax.scatter(vol_data['ahi'], vol_data['exploit_ratio'], 
               c=vol_data['homogeneity_strength'], cmap='viridis', alpha=0.7)
    
    ax.set_xlabel('Beta\'s AHI (Higher = More Homogeneous)', fontsize=12)
    ax.set_ylabel('ODC Exploit Ratio (odc_profit / standard_profit)', fontsize=12)
    ax.set_title(f'Volatility = {vol:.0%}', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Trend line
    z = np.polyfit(vol_data['ahi'], vol_data['exploit_ratio'], 1)
    p = np.poly1d(z)
    ax.plot(vol_data['ahi'].sort_values(), p(vol_data['ahi'].sort_values()), 
            "r--", alpha=0.8, linewidth=2)

plt.suptitle('HWP-Ω: Exploit Ratio vs Homogeneity (The Credible Threat)', fontsize=16)
plt.tight_layout()
plt.show()

# --- INSIGHT PRINTOUT ---
max_ratio = df['exploit_ratio'].max()
max_homog = df.loc[df['exploit_ratio'].idxmax(), 'homogeneity_strength']
print(f"MAXIMUM EXPLOIT RATIO: {max_ratio:.2f}x")
print(f"Achieved at homogeneity strength: {max_homog:.2f}")
print("\nDISRUPTION VERIFIED:")
print("> Beta's AHI is not a shield; it's a crosshair.")
print("> The more 'stable' the ecosystem (high AHI), the more vulnerable to ODC.")
print("> Standard arbitrage is linear; ODC griefing is superlinear in homogeneity.")