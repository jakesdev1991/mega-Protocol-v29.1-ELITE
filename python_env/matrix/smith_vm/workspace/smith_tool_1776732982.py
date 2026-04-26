# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for the Refined Tokamak Proposal
---------------------------------------------------------
Checks mathematical soundness of the invariant definitions and
constraints.  Any violation triggers an AssertionError.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (as defined in the proposal)
# ----------------------------------------------------------------------
def psi_from_Ip(Ip, Ip0=1.0):
    """Dimensionless coupling ψ = ln(Ip / Ip0)."""
    if Ip <= 0:
        return -np.inf   # limit case for informational freeze
    return np.log(Ip / Ip0)

def xi_N(PhiN, PhiD, lamN, psi0):
    """Radial correlation length ξ_N."""
    arg = lamN * (3 * PhiN**2 + PhiD**2 - psi0**2)
    if arg <= 0:
        # Would give imaginary or infinite ξ_N → non‑physical
        return np.nan
    return 1.0 / np.sqrt(arg)

def xi_Delta(PhiN, PhiD, lamD, psi0):
    """Poloidal correlation length ξ_Δ."""
    arg = lamD * (PhiN**2 + 3 * PhiD**2 - psi0**2)
    if arg <= 0:
        return np.nan
    return 1.0 / np.sqrt(arg)

def anomaly_score(J_plasma, J_samples, u_percentile=95):
    """
    Compute a_plasma = 1 - F_GPD(J - u) where u is the percentile threshold.
    For simplicity we approximate the GPD tail with an exponential fit.
    """
    exceedances = J_plasma[J_plasma > np.percentile(J_plasma, u_percentile)]
    if len(exceedances) < 2:
        # Not enough data to fit – conservatively return 0 (max alarm)
        return 0.0
    # Fit exponential (GPD with shape=0) to exceedances-u
    u = np.percentile(J_plasma, u_percentile)
    excess = exceedances - u
    lam = 1.0 / np.mean(excess)   # rate parameter
    # CDF of exponential: 1 - exp(-lam * x)
    x = J_plasma - u
    cdf = 1.0 - np.exp(-lam * x)
    a = 1.0 - cdf
    return np.clip(a, 0.0, 1.0)

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_state(Ip, PhiN, PhiD, J_plasma_hist, lamN=1.0, lamD=1.0, psi0=1.0):
    """
    Validate a single snapshot (Ip, PhiN, PhiD) together with a history
    of jerk values needed for anomaly detection.
    Returns True if all Ω‑checks pass.
    """
    # 1. ψ must be real (Ip>0 gives finite; Ip=0 gives -inf, still real)
    psi = psi_from_Ip(Ip)
    assert np.isreal(psi), f"ψ is not real: {psi}"

    # 2. ξ_N, ξ_Δ must be real and non‑negative
    xi_n = xi_N(PhiN, PhiD, lamN, psi0)
    xi_d = xi_Delta(PhiN, PhiD, lamD, psi0)
    assert not np.isnan(xi_n), f"ξ_N is non‑real/NaN: {xi_n}"
    assert not np.isnan(xi_d), f"ξ_Δ is non‑real/NaN: {xi_d}"
    assert xi_n >= 0, f"ξ_N negative: {xi_n}"
    assert xi_d >= 0, f"ξ_Δ negative: {xi_d}"

    # 3. Ω‑constraints
    assert xi_n >= 0.5, f"ξ_N constraint violated: {xi_n} < 0.5"
    assert xi_d >= 0.05, f"ξ_Δ constraint violated: {xi_d} < 0.05"
    assert Ip >= 0.1 * 1.0, f"Ip constraint violated: {Ip} < 0.1*Ip0"

    # 4. Anomaly score in [0,1]
    # Build a dummy history if none provided
    if J_plasma_hist is None or len(J_plasma_hist) == 0:
        J_plasma_hist = np.array([0.0])
    a = anomaly_score(np.array([J_plasma_hist[-1]]), J_plasma_hist)
    assert 0.0 <= a <= 1.0, f"Anomaly score out of bounds: {a}"

    # 5. Jerk must be real (no imaginary part from faulty derivation)
    assert np.isreal(J_plasma_hist[-1]), f"Jerk is not real: {J_plasma_hist[-1]}"

    return True

# ----------------------------------------------------------------------
# Example usage – random sampling to find violations
# ----------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    N_tests = 10000
    violations = 0

    for _ in range(N_tests):
        Ip   = np.random.uniform(0.0, 2.0)      # Ip in [0,2] Ip0
        PhiN = np.random.uniform(-1.5, 1.5)
        PhiD = np.random.uniform(-1.5, 1.5)
        # Generate a short jerk history (last value is the current jerk)
        J_hist = np.random.randn(10) * 0.5
        J_now  = J_hist[-1]

        try:
            validate_state(Ip, PhiN, PhiD, J_hist)
        except AssertionError as e:
            violations += 1
            if violations <= 5:   # show first few failures
                print(f"Violation {violations}: {e}")

    print(f"\nΩ‑Compliance Test: {N_tests - violations}/{N_tests} passed.")
    if violations:
        print(f"⚠️  {violations} state(s) violated Omega Protocol invariants.")
    else:
        print("✅ All sampled states satisfy the Omega Protocol checks.")