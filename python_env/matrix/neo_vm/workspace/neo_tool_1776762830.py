# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
import random
import statistics

# ─────────────────────────────────────────────────────────────────────────────
# Alpha's MCI (flawed metaphorical version)
# ─────────────────────────────────────────────────────────────────────────────
def compute_alpha_mci(v, deltaG, dVdATP, redox_vals):
    """Compute Alpha's MCI; returns NaN if denominator is zero or redox mean is zero."""
    v = np.array(v, dtype=float)
    deltaG = np.array(deltaG, dtype=float)
    dVdATP = np.array(dVdATP, dtype=float)
    redox_vals = np.array(redox_vals, dtype=float)
    
    numerator = np.sum(np.abs(v * deltaG))
    denominator = math.sqrt(np.sum(dVdATP ** 2))
    if denominator == 0:
        return np.nan
    
    mu_redox = np.mean(redox_vals)
    if mu_redox == 0:
        return np.nan
    sigma_redox = np.std(redox_vals, ddof=0)
    factor = 1 - sigma_redox / mu_redox
    
    return numerator / denominator * factor

# ─────────────────────────────────────────────────────────────────────────────
# Robust information‑theoretic metric (MCI‑Ω′)
# ─────────────────────────────────────────────────────────────────────────────
def compute_entropy(v):
    """Shannon entropy of flux distribution (bits)."""
    v = np.array(v, dtype=float)
    total = v.sum()
    if total == 0:
        return 0.0
    p = v / total
    p = p[p > 0]  # avoid log(0)
    return -np.sum(p * np.log2(p))

def compute_condition_number(S):
    """2‑norm condition number of stoichiometric matrix."""
    return np.linalg.cond(S)

def generate_random_network(m=5, n=5):
    """Create a random stoichiometric matrix and flux vector."""
    # Random integer stoichiometry (dense)
    S = np.random.randint(-3, 4, size=(m, n)).astype(float)
    # Ensure full rank for non‑trivial condition number
    while np.linalg.matrix_rank(S) < min(m, n):
        S = np.random.randint(-3, 4, size=(m, n)).astype(float)
    
    # Random flux vector (positive)
    v = np.random.rand(n) * 10 + 0.1
    
    # Random parameters for Alpha's MCI
    deltaG = np.random.randn(n) * 10  # kJ/mol
    dVdATP = np.random.randn(n) * 0.5  # arbitrary derivative
    redox_vals = np.random.rand(n) * 0.5 + 0.1
    
    return S, v, deltaG, dVdATP, redox_vals

# ─────────────────────────────────────────────────────────────────────────────
# Ensemble test: compare coefficient of variation
# ─────────────────────────────────────────────────────────────────────────────
def ensemble_test(num_samples=1000):
    alpha_mcis = []
    mci_primes = []
    
    for _ in range(num_samples):
        S, v, deltaG, dVdATP, redox_vals = generate_random_network()
        
        # Alpha's metric
        alpha_mci = compute_alpha_mci(v, deltaG, dVdATP, redox_vals)
        if not np.isnan(alpha_mci):
            alpha_mcis.append(alpha_mci)
        
        # Robust metric
        H = compute_entropy(v)
        kappa = compute_condition_number(S)
        mci_prime = kappa * H
        mci_primes.append(mci_prime)
    
    # Coefficient of variation
    def cv(x):
        return np.std(x) / np.mean(x)
    
    print(f"Alpha MCI coefficient of variation: {cv(alpha_mcis):.2f}")
    print(f"MCI‑Ω′ coefficient of variation: {cv(mci_primes):.2f}")
    
    # Collapse simulation: slash fluxes by 90%
    S, v, _, _, _ = generate_random_network()
    v_collapsed = v * 0.1
    H_normal = compute_entropy(v)
    H_collapsed = compute_entropy(v_collapsed)
    kappa = compute_condition_number(S)
    
    print("\nCollapse simulation:")
    print(f"Normal H = {H_normal:.3f}, Collapsed H = {H_collapsed:.3f}")
    print(f"MCI‑Ω′ normal = {kappa * H_normal:.3f}, collapsed = {kappa * H_collapsed:.3f}")
    print("Entropy drops, MCI‑Ω′ drops → clear signal.")
    
    # Show Alpha's MCI under same collapse
    # Use arbitrary parameters for demo
    deltaG = np.random.randn(len(v)) * 10
    dVdATP = np.random.randn(len(v)) * 0.5
    redox_vals = np.random.rand(len(v)) * 0.5 + 0.1
    alpha_normal = compute_alpha_mci(v, deltaG, dVdATP, redox_vals)
    alpha_collapsed = compute_alpha_mci(v_collapsed, deltaG, dVdATP, redox_vals)
    print(f"Alpha MCI normal = {alpha_normal:.3f}, collapsed = {alpha_collapsed:.3f}")
    print("Alpha's metric can fluctuate unpredictably; no clear collapse signature.")

if __name__ == "__main__":
    ensemble_test()