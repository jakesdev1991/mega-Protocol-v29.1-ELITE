# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for Biological Stability Index (BSI‑Ω)

Checks:
  1. Feature normalisation (zero mean, unit variance)
  2. Positive reference values
  3. Monotonicity of Phi_N and Phi_Delta w.r.t. BSI
  4. Invariant consistency (psi, xi_N, xi_Delta)
  5. Feasibility of MPC‑Ω constraints
  6. Proper normalisation of the entropy gauge S_h

Run the script; it will either print "All Omega checks passed."
or raise an AssertionError with a diagnostic message.
"""

import numpy as np
from scipy.optimize import minimize_scalar

# ----------------------------------------------------------------------
# USER‑DEFINED PARAMETERS (these would normally come from training data)
# ----------------------------------------------------------------------
# Example values – replace with actual learned parameters
alpha, beta, gamma, delta = 0.4, 0.3, 0.2, 0.1          # BSI weights (should sum to 1)
sigma2_ref = 1.0                                        # variance reference (>0)
tau_ref    = 2.0                                        # autocorrelation time reference (>0)
# Mapping parameters (tanh & quadratic)
phi0       = 0.5                                        # baseline field
eta1, eta2, eta3 = 0.6, 0.4, 0.1                        # mapping coefficients
tau1, tau2, tau3 = 30.0, 14.0, 60.0                     # delays (days) – not used in static check
# MPC‑Ω limits
BSI_MAX_MPC   = 3.0
PHI_N_MIN_MPC = 0.8
PHI_D_MAX_MPC = 0.7
# ----------------------------------------------------------------------


def normalize_features(X):
    """
    Zero‑mean, unit‑variance normalisation for a 2‑D array (samples × features).
    Returns normalized array and the mean/std used (for possible later reuse).
    """
    mean = np.mean(X, axis=0)
    std  = np.std(X, axis=0, ddof=1)
    # Avoid division by zero
    std[std == 0] = 1.0
    Xnorm = (X - mean) / std
    return Xnorm, mean, std


def compute_BSI(features_norm):
    """
    Linear combination to obtain BSI (assumes features_norm already normalized).
    """
    return np.dot(features_norm, np.array([alpha, beta, gamma, delta]))


def phi_N_from_BSI(BSI):
    """Newtonian mode mapping (tanh)."""
    return phi0 + eta1 * np.tanh(BSI - tau1)   # tau1 acts as a shift; kept simple


def phi_Delta_from_BSI(BSI):
    """Asymmetry mode mapping (tanh + quadratic)."""
    return phi0 + eta2 * BSI - eta3 * BSI**2   # tau2, tau3 omitted for static check


def psi_from_BSI(BSI):
    """Invariant ψ = ln(1+BSI)."""
    return np.log1p(BSI)   # log(1+BSI) – safe for BSI≥0


def xi_N_from_BSI(BSI):
    """∂Φ_N/∂ψ = (dΦ_N/dBSI) / (dψ/dBSI)."""
    dPhiN_dBSI = eta1 * (1 - np.tanh(BSI - tau1)**2)   # derivative of tanh
    dpsi_dBSI  = 1.0 / (1.0 + BSI)
    return dPhiN_dBSI / dpsi_dBSI


def xi_Delta_from_BSI(BSI):
    """∂Φ_Δ/∂ψ = (dΦ_Δ/dBSI) / (dψ/dBSI)."""
    dPhiD_dBSI = eta2 - 2.0 * eta3 * BSI
    dpsi_dBSI  = 1.0 / (1.0 + BSI)
    return dPhiD_dBSI / dpsi_dBSI


def entropy_gamma(BSI_array):
    """
    Shannon entropy of the BSI distribution treating BSI as unnormalised weights.
    Returns S_h and the normalised probabilities p.
    """
    # Shift to make strictly positive (BSI≥0 already)
    weights = BSI_array.copy()
    total   = np.sum(weights)
    if total <= 0:
        raise ValueError("Sum of BSI weights must be >0 for entropy calculation.")
    p = weights / total
    # Avoid log(0)
    p = np.clip(p, 1e-12, None)
    S_h = -np.sum(p * np.log(p))
    return S_h, p


def check_monotonicity(func, BSI_low=0.0, BSI_high=10.0, n=1000):
    """Return True if func is monotonic (non‑decreasing) over [low, high]."""
    xs = np.linspace(BSI_low, BSI_high, n)
    vals = func(xs)
    diffs = np.diff(vals)
    # Allow tiny numerical noise
    return np.all(diffs >= -1e-12)


def check_mpc_feasibility():
    """
    Find the BSI interval that satisfies all three MPC constraints.
    Returns (BSI_low, BSI_high) if feasible, else None.
    """
    def constraints_satisfied(BSI):
        return (BSI <= BSI_MAX_MPC) and \
               (phi_N_from_BSI(BSI) >= PHI_N_MIN_MPC) and \
               (phi_Delta_from_BSI(BSI) <= PHI_D_MAX_MPC)

    # Scan for feasible region
    BSI_vals = np.linspace(0, 10, 2000)
    feasible = BSI_vals[np.vectorize(constraints_satisfied)(BSI_vals)]
    if feasible.size == 0:
        return None
    return feasible[0], feasible[-1]


def main():
    # ------------------------------------------------------------------
    # 1. Feature normalisation check (dummy data)
    # ------------------------------------------------------------------
    np.random.seed(42)
    dummy_raw = np.random.randn(100, 4) * 5 + 10   # arbitrary scale
    Xnorm, mu, sigma = normalize_features(dummy_raw)
    assert np.allclose(np.mean(Xnorm, axis=0), 0, atol=1e-10), "Features not zero‑mean"
    assert np.allclose(np.std(Xnorm, axis=0, ddof=1), 1, atol=1e-10), "Features not unit‑variance"
    print("[✓] Feature normalisation passed.")

    # ------------------------------------------------------------------
    # 2. Positive references
    # ------------------------------------------------------------------
    assert sigma2_ref > 0, "σ²_ref must be >0"
    assert tau_ref    > 0, "τ_ref must be >0"
    print("[✓] Positive reference values passed.")

    # ------------------------------------------------------------------
    # 3. Monotonicity of Ω‑variable mappings
    # ------------------------------------------------------------------
    assert check_monotonicity(phi_N_from_BSI), "Φ_N must be monotonic non‑decreasing in BSI"
    # For Φ_Δ we expect a *decreasing* monotonic behaviour (negative slope) to keep asymmetry in check.
    xs = np.linspace(0, 10, 1000)
    dPhiD = np.gradient(phi_Delta_from_BSI(xs), xs)
    assert np.all(dPhiD <= 1e-12), "Φ_Δ must be monotonic non‑increasing in BSI"
    print("[✓] Monotonicity of Φ_N and Φ_Δ passed.")

    # ------------------------------------------------------------------
    # 4. Invariant consistency (ψ, ξ_N, ξ_Δ)
    # ------------------------------------------------------------------
    BSI_test = np.linspace(0, 10, 500)
    psi = psi_from_BSI(BSI_test)
    xiN = xi_N_from_BSI(BSI_test)
    xiD = xi_Delta_from_BSI(BSI_test)
    # ψ must be ≥0 (since BSI≥0)
    assert np.all(psi >= -1e-12), "ψ = ln(1+BSI) must be non‑negative"
    # Omega invariant: ξ_N * ξ_Δ ≥ 0 (Newtonian and asymmetry channels should co‑vary)
    prod = xiN * xiD
    assert np.all(prod >= -1e-12), "ξ_N * ξ_Δ must be non‑negative (co‑variance condition)"
    print("[✓] Invariant consistency (ψ, ξ_N, ξ_Δ) passed.")

    # ------------------------------------------------------------------
    # 5. MPC‑Ω feasibility
    # ------------------------------------------------------------------
    feasible_interval = check_mpc_feasibility()
    if feasible_interval is None:
        raise AssertionError(
            "No BSI value satisfies the MPC‑Ω constraints "
            f"(BSI≤{BSI_MAX_MPC}, Φ_N≥{PHI_N_MIN_MPC}, Φ_Δ≤{PHI_D_MAX_MPC})."
        )
    BSI_low, BSI_high = feasible_interval
    print(f"[✓] MPC‑Ω feasible BSI interval: [{BSI_low:.3f}, {BSI_high:.3f}]")

    # ------------------------------------------------------------------
    # 6. Entropy gauge normalisation
    # ------------------------------------------------------------------
    # Use a synthetic population of BSI values drawn from the feasible interval
    pop_BSI = np.random.uniform(BSI_low, BSI_high, size=500)
    S_h, p = entropy_gamma(pop_BSI)
    assert np.isclose(np.sum(p), 1.0, atol=1e-12), "Entropy probabilities must sum to 1"
    assert 0 <= S_h <= np.log(len(p)) + 1e-12, "Entropy out of expected bounds"
    print(f"[✓] Entropy gauge S_h = {S_h:.4f} (normalised distribution).")

    # ------------------------------------------------------------------
    # All checks passed
    # ------------------------------------------------------------------
    print("\nAll Omega Protocol validation checks PASSED.")
    return 0


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\n[✗] Omega Protocol validation FAILED: {e}")
        exit(1)