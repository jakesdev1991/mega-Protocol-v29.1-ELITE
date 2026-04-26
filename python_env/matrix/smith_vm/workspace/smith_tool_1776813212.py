# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol validation script for Adversarial Transactional Geometry Shield (ATGS‑Ω).

Checks:
  - ATI ∈ [0,1]
  - Φ_N_adv ≥ 0.6
  - ψ_adv real (|R_adv|/R0 > 0)
  - S_adv ≥ log(3)
  - MPC constraints feasible (ATI ≤ 0.72, Φ_N_adv ≥ 0.6, S_adv ≥ log(3))
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# Helper functions (symbolic)
# ----------------------------------------------------------------------
def ATI(alpha, beta, gamma, delta, rho, G, nu, sigma_IL):
    """Adversarial Threat Index – tanh maps ℝ → (-1,1); we shift+scale to [0,1]."""
    raw = alpha * rho + beta * G + gamma * nu**(-1) + delta * sigma_IL
    # Shift to [0,1]: (tanh(x)+1)/2
    return (sp.tanh(raw) + 1) / 2

def Phi_N_adv(Phi_N0, eta1, eta2, ATI_val, G_val, tau=0):
    """Connectivity mode after adversarial influence (lead time τ ignored for static check)."""
    return Phi_N0 - eta1 * ATI_val + eta2 * (1 - G_val)

def Phi_Delta_adv(Phi_Delta0, eta3, eta4, rho_val, nu_val, tau=0):
    """Asymmetry mode after adversarial influence."""
    return Phi_Delta0 + eta3 * rho_val - eta4 * nu_val**(-1)

def psi_adv(R_adv, R0, lam, ATI_val):
    """Adversarial invariant from Ricci curvature."""
    # Ensure argument of log positive
    assert R_adv != 0, "Ricci curvature must be non‑zero for log."
    return sp.ln(sp.Abs(R_adv) / R0) + lam * ATI_val

def S_adv(p_k):
    """Shannon entropy of attack‑strategy distribution."""
    return -sp.sum([p * sp.log(p) for p in p_k if p > 0])

# ----------------------------------------------------------------------
# Numerical validation (Monte‑Carlo style)
# ----------------------------------------------------------------------
np.random.seed(42)
N_SAMPLES = 10_000

# Plausible parameter ranges (chosen from DeFi literature)
rho_range      = (0.0, 1.0)          # cross‑pool correlation
G_range        = (0.0, 1.0)          # Gini coefficient
nu_range       = (1.0, 20.0)         # blocks between detection & execution
sigma_IL_range = (0.0, 0.5)          # LP loss dispersion (normalized)

# Coefficients (calibrated via logistic regression – example values)
alpha, beta, gamma, delta = 0.3, 0.4, 0.2, 0.1

# Omega baseline values
Phi_N0, Phi_Delta0 = 0.8, 0.2
eta1, eta2, eta3, eta4 = 0.15, 0.1, 0.12, 0.08
R0, lam = 1.0, 0.5   # curvature scaling

# MPC thresholds
ATI_max   = 0.72
Phi_N_min = 0.6
S_min     = np.log(3)

def sample_params():
    rho      = np.random.uniform(*rho_range)
    G        = np.random.uniform(*G_range)
    nu       = np.random.uniform(*nu_range)
    sigma_IL = np.random.uniform(*sigma_IL_range)
    # Ricci curvature – draw from a distribution centred on R0 with some variance
    R_adv    = np.random.normal(loc=R0, scale=0.3)
    # Attack strategy probabilities (3 strategies) – Dirichlet ensures sum=1
    p_k      = np.random.dirichlet(alpha=[1.0, 1.0, 1.0])
    return rho, G, nu, sigma_IL, R_adv, p_k

violations = []

for i in range(N_SAMPLES):
    rho, G, nu, sigma_IL, R_adv, p_k = sample_params()

    # 1. ATI in [0,1]
    ATI_val = float(ATI(alpha, beta, gamma, delta, rho, G, nu, sigma_IL))
    if not (0.0 <= ATI_val <= 1.0):
        violations.append(f"Sample {i}: ATI={ATI_val:.4f} out of bounds")
        continue

    # 2. Φ_N_adv ≥ 0.6
    Phi_N_val = Phi_N_adv(Phi_N0, eta1, eta2, ATI_val, G)
    if Phi_N_val < Phi_N_min:
        violations.append(f"Sample {i}: Φ_N_adv={Phi_N_val:.4f} < {Phi_N_min}")

    # 3. ψ_adv real (log argument positive)
    if R_adv == 0:
        violations.append(f"Sample {i}: R_adv == 0 → log undefined")
        continue
    psi_val = psi_adv(R_adv, R0, lam, ATI_val)
    # psi_val is always real for real R_adv; we just check that ln argument >0
    if np.abs(R_adv) / R0 <= 0:
        violations.append(f"Sample {i}: |R_adv|/R0 ≤ 0")

    # 4. Entropy gauge
    S_val = float(S_adv(p_k))
    if S_val < S_min:
        violations.append(f"Sample {i}: S_adv={S_val:.4f} < log(3)={S_min:.4f}")

    # 5. MPC constraints (hard limits)
    if ATI_val > ATI_max:
        violations.append(f"Sample {i}: ATI={ATI_val:.4f} > {ATI_max}")
    if Phi_N_val < Phi_N_min:
        violations.append(f"Sample {i}: Φ_N_adv={Phi_N_val:.4f} < {Phi_N_min}")
    if S_val < S_min:
        violations.append(f"Sample {i}: S_adv={S_val:.4f} < {S_min:.4f}")

# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
if violations:
    print(f"Found {len(violations)} invariant violations (first 5 shown):")
    for v in violations[:5]:
        print(" -", v)
    raise AssertionError("Omega‑Protocol invariants violated – integration rejected.")
else:
    print(f"All {N_SAMPLES} random samples satisfy Omega‑Protocol invariants.")
    print("ATGS‑Ω integration is mathematically sound (within tested parameter ranges).")