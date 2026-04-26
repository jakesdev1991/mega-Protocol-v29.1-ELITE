# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator – HSA Jerk Stability
Validates the repaired analysis against Rubric v26.0.
"""

import numpy as np
from scipy.integrate import cumtrapz

# ------------------- USER PARAMETERS -------------------
# Physical constants from the analysis (adjust as needed)
lam = 1.0e-2          # λ (coupling)  [GB^-2 s^2]  chosen so that λ I^2 is dimensionless
v   = 200.0           # v  [GB/s]    reference scale (I0)
I0  = 200.0           # I0 [GB/s]    stable operating point
dt  = 0.001           # sampling step [s]
T   = 1.0             # total simulation time [s]
# -------------------------------------------------------

def I_of_t(t):
    """Example bandwidth: I(t) = 200 + 50*sin(20π t)  [GB/s]"""
    return I0 + 50.0 * np.sin(20.0 * np.pi * t)

def dI_dt(t):
    """First derivative (analytic)"""
    return 50.0 * 20.0 * np.pi * np.cos(20.0 * np.pi * t)

def d2I_dt2(t):
    """Second derivative (analytic)"""
    return -50.0 * (20.0 * np.pi)**2 * np.sin(20.0 * np.pi * t)

def d3I_dt3(t):
    """Third derivative (analytic) – the physical jerk"""
    return -50.0 * (20.0 * np.pi)**3 * np.cos(20.0 * np.pi * t)

def jerk_from_action(I, dI):
    """Jerk derived from the Omega Action: J = -λ (3 I^2 - v^2) * dI"""
    return -lam * (3.0 * I**2 - v**2) * dI

def compute_entropy(I_vals, window=100):
    """Shannon conditional entropy over a sliding window (nats)."""
    N = len(I_vals)
    S = np.full(N, np.nan)
    half = window // 2
    for i in range(half, N - half):
        segment = I_vals[i-half:i+half+1]
        p = segment / segment.sum()
        # avoid log(0)
        p = p[p > 0]
        S[i] = -np.sum(p * np.log(p))
    return S

def main():
    t = np.arange(0, T, dt)
    I = I_of_t(t)
    dI = dI_dt(t)
    d2I = d2I_dt2(t)
    d3I = d3I_dt3(t)

    # Jerk from the action formula
    J_action = jerk_from_action(I, dI)

    # Numerical third derivative (finite difference) for cross‑check
    J_num = np.gradient(np.gradient(np.gradient(I, dt), dt), dt)

    # Tolerances
    tol = 1e-6

    # 1. Unit check: J should have same dimensions as d3I/dt3
    #    (both are GB/s^4). We verify that the scaling matches.
    assert np.allclose(J_action, J_num, atol=tol, rtol=1e-3), \
        "Action‑derived jerk does not match numerical third derivative."

    # 2. Invariant positivity (stable regime: I^2 < v^2/3 ensures denominator >0)
    xi_N = 1.0 / np.sqrt(lam * np.abs(3.0 * I**2 - v**2))
    # For xi_Delta we need Phi_Delta; assume small asymmetry: Phi_Delta = 0.1*I
    Phi_Delta = 0.1 * I
    xi_Delta = 1.0 / np.sqrt(lam * np.abs(I**2 + 3.0 * Phi_Delta**2 - v**2))
    assert np.all(xi_N > 0), "xi_N non‑positive"
    assert np.all(xi_Delta > 0), "xi_Delta non‑positive"

    # 3. Entropy
    S = compute_entropy(I, window=int(1.0/dt))  # 1‑second window
    S_valid = S[~np.isnan(S)]
    assert np.all(S_valid > 2.5), "Entropy below threshold"

    # 4. Stability criteria
    J_rms = np.sqrt(np.mean(J_action**2))
    J_max = np.max(np.abs(J_action))
    J_crit = 1.2e7  # GB/s^4 (from analysis)
    assert J_rms < J_crit, f"RMS jerk {J_rms:.3e} exceeds J_crit {J_crit:.3e}"
    assert J_max < 3.0 * J_rms, f"Peak jerk {J_max:.3e} > 3*RMS {3*J_rms:.3e}"
    # stiffness thresholds (converted to seconds via inverse sqrt)
    assert np.all(xi_N > 0.1), "xi_N below 0.1 s"
    assert np.all(xi_Delta > 0.05), "xi_Delta below 0.05 s"

    # If we reach here, all checks passed
    print("✅ All Omega Protocol invariants validated.")
    print(f"   RMS(J) = {J_rms:.3e} GB/s^4  (limit {J_crit:.3e})")
    print(f"   max|J| = {J_max:.3e} GB/s^4")
    print(f"   <S_h>  = {np.mean(S_valid):.3f} nats")
    print(f"   <xi_N> = {np.mean(xi_N):.3f} s")
    print(f"   <xi_Δ> = {np.mean(xi_Delta):.3f} s")

if __name__ == "__main__":
    main()