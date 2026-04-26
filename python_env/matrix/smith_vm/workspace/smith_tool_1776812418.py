# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rubric‑compliant validator for Perceptual Coherence Shield (PCS‑Ω) v2.0
"""

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh

# ----------------------------------------------------------------------
# User‑adjustable parameters (these would be set by calibration)
# ----------------------------------------------------------------------
alpha = -1.0      # <0
beta  =  2.0      # >0
gamma =  0.5      # >0
kappa1 = 0.8      # coupling for gradient term (used only for sanity check)
kappa2 = 0.1
kappa3 = 0.6      # coupling for skewness term
kappa4 = 0.05
# Entropy region parameters (example: split field into low/high coherence)
n_regions = 2
n_bins    = 10
# MPC‑Ω thresholds
PCI_min   = 0.6
PhiN_min  = 0.5
S_low     = 0.2 * np.log(n_bins)   # arbitrary low entropy bound
S_high    = 0.9 * np.log(n_bins)   # arbitrary high entropy bound
S_target  = 0.5 * np.log(n_bins)
mu1, mu2, mu3 = 1.0, 1.0, 1.0
dt = 0.01   # integration step for cost (dummy)
# ----------------------------------------------------------------------


def double_well(C):
    """V(C) = α/2 C^2 + β/4 C^4 - γ C"""
    return 0.5*alpha*C**2 + 0.25*beta*C**4 - gamma*C

def d2V_dC2(C):
    """Second derivative V''(C) = α + 3β C^2"""
    return alpha + 3.0*beta*C**2

def build_fluctuation_operator(C, dx):
    """
    Build sparse matrix for M = -∇^2 + V''(C0) I,
    where C0 is the spatial mean (vacuum expectation).
    """
    C0 = np.mean(C)
    V2 = d2V_dC2(C0) * np.ones_like(C)   # constant shift
    N = C.size
    # 1‑D Laplacian with Neumann BC (second order)
    main = -2.0 * np.ones(N)
    offs =  1.0 * np.ones(N-1)
    lap = diags([offs, main, offs], [-1, 0, 1], shape=(N, N)) / (dx**2)
    M = lap + diags(V2, 0)
    return M

def compute_conditional_entropy(C):
    """
    Simple region‑wise conditional entropy:
    - Split field into n_regions by thresholding at median.
    - Discretize coherence values into n_bins.
    Returns S_perc.
    """
    # region partition
    med = np.median(C)
    region_mask = C < med          # region 0 = low, region 1 = high
    p_region = [np.mean(region_mask), np.mean(~region_mask)]

    S = 0.0
    for mask, pr in zip([region_mask, ~region_mask], p_region):
        if pr == 0:
            continue
        vals = C[mask]
        # histogram
        hist, _ = np.histogram(vals, bins=n_bins, density=True)
        # avoid zeros in log
        hist = hist[hist > 0]
        S += -pr * np.sum(hist * np.log(hist))
    return S

def compute_PCI(PhiN, PhiD, Gamma=1.0):
    """PCI = ΦN * ΦD * Γ (Γ set to 1 for validation)"""
    return PhiN * PhiD * Gamma

def evaluate_configuration(C, dx=1.0):
    """
    Returns True if the configuration satisfies all rubric‑derived
    mathematical relations; False otherwise.
    """
    # 1. Fluctuation operator & eigenvalues
    M = build_fluctuation_operator(C, dx)
    # ask for two smallest eigenvalues (real symmetric)
    eigvals, _ = eigsh(M, k=2, which='SA')
    omega2_N, omega2_D = np.sort(eigvals)   # ascending
    # ensure positivity (physical requirement)
    if omega2_N <= 0 or omega2_D <= 0:
        return False, f"Non‑positive eigenvalue: ω_N^2={omega2_N:.3e}, ω_Δ^2={omega2_D:.3e}"
    PhiN = np.sqrt(omega2_N)
    PhiD = np.sqrt(omega2_D)

    # 2. Invariant
    PhiN0 = np.sqrt(alpha + 3*beta*(np.mean(C)**2))  # vacuum value from homogeneous C0
    if PhiN0 <= 0:
        return False, "Baseline ΦN0 non‑positive"
    psi = np.log(PhiN / PhiN0)

    # 3. Entropy gauge
    S_perc = compute_conditional_entropy(C)

    # 4. Boundary condition checks (thermodynamic)
    S_max = np.log(n_bins)   # maximal entropy for uniform distribution over bins
    shredding = (np.isinf(psi) or psi > 20) and (PhiN > 1e3) and (S_perc > 0.9*S_max)
    locking   = (np.isneginf(psi) or psi < -20) and (PhiN < 1e-3) and (S_perc < 0.1*S_max)
    # For finite fields we just check monotonic trend:
    if PhiN > 1e3 and S_perc > 0.9*S_max and psi <= 0:
        return False, "Shredding condition violated: ψ not → +∞"
    if PhiN < 1e-3 and S_perc < 0.1*S_max and psi >= 0:
        return False, "Locking condition violated: ψ not → -∞"

    # 5. PCI and QP constraints
    PCI = compute_PCI(PhiN, PhiD)
    if PCI < PCI_min:
        return False, f"PCI={PCI:.3f} < {PCI_min}"
    if PhiN < PhiN_min:
        return False, f"ΦN={PhiN:.3f} < {PhiN_min}"
    if not (S_low <= S_perc <= S_high):
        return False, f"S_perc={S_perc:.3f} outside [{S_low:.3f},{S_high:.3f}]"

    # 6. Cost function (should be non‑negative)
    cost = ((PCI_min - PCI)**2 if PCI < PCI_min else 0.0) \
         + mu1*((PhiN_min - PhiN)**2 if PhiN < PhiN_min else 0.0) \
         + mu2*(PhiD**2) \
         + mu3*((S_perc - S_target)**2)
    if cost < -1e-12:   # allow tiny negative due to rounding
        return False, f"Cost negative: {cost:.3e}"

    # All checks passed
    return True, {
        "PhiN": PhiN,
        "PhiD": PhiD,
        "psi": psi,
        "S_perc": S_perc,
        "PCI": PCI,
        "cost": cost
    }

# ----------------------------------------------------------------------
# Demo / self‑test
# ----------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    L = 50.0          # domain length
    N = 256           # grid points
    x = np.linspace(0, L, N, endpoint=False)
    dx = L / N

    # generate a random coherence field bounded in [-1,1] (cosine similarity)
    C = np.random.uniform(-0.8, 0.8, size=N)

    ok, info = evaluate_configuration(C, dx)
    if ok:
        print("✅ Configuration passes rubric validation.")
        for k, v in info.items():
            print(f"   {k}: {v}")
    else:
        print("❌ Configuration FAILS rubric validation.")
        print("   Reason:", info)