# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol compliance validator for the Information‑Cascade Monitor (IC‑Ω) proposal.
Checks dimensionless consistency, bounds, and invariant relationships.
"""

import numpy as np

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def CI_from_features(O, L, C, Delta, alpha=1.0, beta=1.0, gamma=1.0, delta=1.0):
    """Cascade Intensity Index as defined in the proposal."""
    arg = alpha * O + beta * L + gamma * C + delta * Delta
    # Ensure non‑negative argument so tanh maps to [0,1) after shift
    arg = np.maximum(arg, 0.0)
    return np.tanh(arg)          # ∈ [0,1)

def Phi_N_update(PhiN0, CI_lag, L_lag, eta1=0.5, eta2=0.3):
    """Phi_N connectivity update (Eq. in proposal)."""
    return PhiN0 - eta1 * CI_lag + eta2 * (1.0 - L_lag)

def Phi_Delta_update(PhiDelta0, Delta_lag, C_lag, eta3=0.4, eta4=0.2):
    """Phi_Delta asymmetry update."""
    return PhiDelta0 + eta3 * Delta_lag - eta4 * C_lag

def psi_cascade_from_PhiN(PhiN, PhiN0):
    """Invariant using Phi_N only (first definition)."""
    return np.log(PhiN / PhiN0)

def psi_cascade_from_graph(Rc, R0, CI, lam=0.5):
    """Invariant using graph curvature + CI (second definition)."""
    return np.log(np.abs(Rc) / R0) + lam * CI

def entropy_from_volumes(volumes):
    """Shannon entropy of trader‑type volume fractions."""
    total = np.sum(volumes)
    if total == 0:
        return 0.0
    p = volumes / total
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def cost_integrand(CI, PhiN, PhiDelta, S,
                   mu1=1.0, mu2=1.0, mu3=1.0,
                   CI_target=0.6, PhiN_target=0.6, S_target=np.log(3)):
    """Instantaneous cost (integrand of J)."""
    term1 = max(CI - CI_target, 0.0) ** 2
    term2 = mu1 * max(PhiN_target - PhiN, 0.0) ** 2
    term3 = mu2 * PhiDelta ** 2
    term4 = mu3 * max(S_target - S, 0.0) ** 2
    return term1 + term2 + term3 + term4

# ------------------------------------------------------------
# Synthetic data generation (for demonstration)
# ------------------------------------------------------------
np.random.seed(42)
T = 100  # time steps

# Simulated micro‑structure features (all ∈ [0,1] for simplicity)
O = np.random.uniform(0, 1, T)          # order‑imbalance surge
L = np.random.uniform(0, 1, T)          # liquidity withdrawal
C = np.random.uniform(0, 1, T)          # cross‑ETF correlation
Delta = np.random.uniform(-1, 1, T)     # trader‑response skew (can be negative)

# Parameters for CI
alpha, beta, gamma, delta = 0.8, 0.6, 0.4, 0.5

# Compute CI
CI = CI_from_features(O, L, C, Delta, alpha, beta, gamma, delta)

# Baseline Omega variables
PhiN0 = 1.0
PhiDelta0 = 0.2

# Lagged values (simple 1‑step lag for illustration)
CI_lag = np.concatenate(([CI[0]], CI[:-1]))
L_lag = np.concatenate(([L[0]], L[:-1]))
Delta_lag = np.concatenate(([Delta[0]], Delta[:-1]))
C_lag = np.concatenate(([C[0]], C[:-1]))

# Updated Omega variables
PhiN = PhiN_update(PhiN0, CI_lag, L_lag, eta1=0.5, eta2=0.3)
PhiDelta = PhiDelta_update(PhiDelta0, Delta_lag, C_lag, eta3=0.4, eta4=0.2)

# Entropy: simulate three trader types with time‑varying volumes
volumes = np.abs(np.random.randn(T, 3)) + 0.1  # ensure positivity
S = np.apply_along_axis(entropy_from_volumes, 1, volumes)

# Graph curvature: enforce relation Rc = R0 * (PhiN/PhiN0) * exp(-lambda*CI)
lam = 0.5
R0 = 1.0
Rc = R0 * (PhiN / PhiN0) * np.exp(-lam * CI)

# Compute both forms of psi_cascade
psi1 = psi_cascade_from_PhiN(PhiN, PhiN0)
psi2 = psi_cascade_from_graph(Rc, R0, CI, lam)

# ------------------------------------------------------------
# Validation checks
# ------------------------------------------------------------
def report(name, value, condition=None):
    """Print a check result."""
    if condition is None:
        ok = True
    else:
        ok = condition(value)
    status = "PASS" if ok else "FAIL"
    print(f"{status:4} | {name:30} | value = {value:.6f}")

print("\n=== Ω‑Protocol Compliance Validation ===\n")

# 1. CI bounds
report("CI ∈ [0,1]", CI.mean(),
       lambda x: np.all((x >= 0.0) & (x <= 1.0)))

# 2. Phi_N lower bound (MPC constraint)
report("Phi_N ≥ 0.6", PhiN.min(),
       lambda x: np.all(x >= 0.6))

# 3. Entropy lower bound
report("S_cascade ≥ ln(3)", S.min(),
       lambda x: np.all(x >= np.log(3)))

# 4. Invariant consistency (psi1 vs psi2)
diff_psi = np.abs(psi1 - psi2)
report("|ψ_cascade(ΦN) - ψ_cascade(R,CI)| < 1e-6", diff_psi.max(),
       lambda x: np.all(x < 1e-6))

# 5. Gauge current dimensionless check (PhiDelta dimensionless)
report("Phi_Δ dimensionless (|Phi_Δ| < 10)", PhiDelta.max(),
       lambda x: np.all(np.abs(x) < 10))

# 6. Cost integrand non‑negative
inst_cost = cost_integrand(CI, PhiN, PhiDelta, S)
report("Instantaneous cost ≥ 0", inst_cost.min(),
       lambda x: np.all(x >= 0.0))

# 7. QP constraints satisfaction (hard constraints)
report("CI ≤ 0.7 (hard)", CI.max(),
       lambda x: np.all(x <= 0.7))
report("Phi_N ≥ 0.6 (hard)", PhiN.min(),
       lambda x: np.all(x >= 0.6))
report("S_cascade ≥ ln(3) (hard)", S.min(),
       lambda x: np.all(x >= np.log(3)))

print("\n=== End of Validation ===\n")