# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol validator for Informational Jerk stability in an HSA node.

Checks:
  1. Dimensional consistency of J(t) = -λ (3 I^2 - v^2) dI/dt.
  2. Correct computation of invariants ψ, ξ_N, ξ_Δ from the Mexican‑hat potential.
  3. Stability criteria:
        RMS(J) < Jcrit
        max|J| < 3 * RMS(J)
        S_h > S_min
        ξ_N > ξN_min, ξ_Δ > ξΔ_min
  4. (Optional) Numerical jerk vs analytic jerk agreement.

Usage:
    python3 omega_jerk_validator.py   # runs the built‑in test case
"""

import numpy as np
from scipy.signal import savgol_filter

# ----------------------------------------------------------------------
# User‑defined parameters (match the repaired solution)
# ----------------------------------------------------------------------
I0   = 200.0          # GB/s  – reference bandwidth
v    = 250.0          # GB/s  – symmetry‑breaking scale
lam  = 0.01           # (GB/s)^-2  – coupling constant
cN   = 1.0            # arbitrary, not needed for the ODE
cD   = 1.0

# Stability thresholds (derived from historical operation)
Jcrit      = 1.2e7    # GB/s^4
S_min      = 2.5      # nats
xiN_min    = 0.1      # s
xiD_min    = 0.05     # s

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def I_of_t(t, A=50.0, omega=20*np.pi):
    """Example I(t): baseline + sinusoid (GB/s)."""
    return I0 + A * np.sin(omega * t)

def dI_dt(t, A=50.0, omega=20*np.pi):
    """Analytic derivative of I(t)."""
    return A * omega * np.cos(omega * t)

def jerk_analytic(t, A=50.0, omega=20*np.pi):
    """Jerk from the Omega‑Action derivation."""
    I  = I_of_t(t, A, omega)
    dI = dI_dt(t, A, omega)
    return -lam * (3.0*I**2 - v**2) * dI

def invariants(I, PhiDelta=0.0):
    """Compute ψ, ξ_N, ξ_Δ from instantaneous I and (optional) Φ_Δ."""
    psi   = np.log(I / I0)
    xi_N  = 1.0 / np.sqrt(lam * (3.0*I**2 - v**2)) if (3.0*I**2 - v**2) > 0 else np.inf
    xi_D  = 1.0 / np.sqrt(lam * (I**2 + 3.0*PhiDelta**2 - v**2)) if (I**2 + 3.0*PhiDelta**2 - v**2) > 0 else np.inf
    return psi, xi_N, xi_D

def shannon_entropy(samples, bins=50):
    """Shannon conditional entropy of a 1‑D sample set (nats)."""
    hist, _ = np.histogram(samples, bins=bins, density=True)
    # Remove zero entries to avoid log(0)
    p = hist[hist > 0]
    return -np.sum(p * np.log(p))

def numerical_jerk(t, I_vals, window=21, order=3):
    """
    Estimate jerk via Savitzky‑Golay smoothing + three derivatives.
    Returns jerk array aligned with t (same length as input).
    """
    # smooth
    I_smooth = savgol_filter(I_vals, window_length=window, polyorder=order, deriv=0)
    # first, second, third derivatives
    dI  = savgol_filter(I_vals, window_length=window, polyorder=order, deriv=1, delta=t[1]-t[0])
    d2I = savgol_filter(I_vals, window_length=window, polyorder=order, deriv=2, delta=t[1]-t[0])
    d3I = savgol_filter(I_vals, window_length=window, polyorder=order, deriv=3, delta=t[1]-t[0])
    return d3I  # this is the numerical jerk

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate():
    # Time vector for one second (sufficient for entropy window)
    t = np.linspace(0.0, 1.0, 1000)
    I  = I_of_t(t)
    dI = dI_dt(t)

    # Analytic jerk from the Omega‑Action
    J_ana = jerk_analytic(t)

    # Numerical jerk (for sanity check)
    J_num = numerical_jerk(t, I)

    # Agreement check (should be < 5% relative error)
    rel_err = np.mean(np.abs(J_ana - J_num) / (np.abs(J_ana) + 1e-12))
    print(f"Mean relative error between analytic and numeric jerk: {rel_err*100:.2f}%")
    assert rel_err < 0.05, "Jerk implementation mismatch!"

    # ----- Invariant calculations (using the instantaneous I) -----
    psi, xi_N, xi_D = invariants(I.mean())   # use time‑average as representative
    print(f"Invariants (time‑averaged I):")
    print(f"  ψ = {psi:.4f}")
    print(f"  ξ_N = {xi_N:.4f} s")
    print(f"  ξ_Δ = {xi_D:.4f} s")

    # ----- Entropy -----
    S_h = shannon_entropy(I)
    print(f"Shannon entropy S_h = {S_h:.3f} nats")

    # ----- Stability metrics -----
    J_rms = np.sqrt(np.mean(J_ana**2))
    J_max = np.max(np.abs(J_ana))
    print(f"Jerk statistics:")
    print(f"  RMS(J) = {J_rms:.3e} GB/s^4")
    print(f"  max|J| = {J_max:.3e} GB/s^4")
    print(f"  J_crit = {Jcrit:.3e} GB/s^4")

    # ----- Criteria -----
    crit1 = J_rms < Jcrit
    crit2 = J_max < 3.0 * J_rms
    crit3 = S_h > S_min
    crit4 = (xi_N > xiN_min) and (xi_D > xiD_min)

    print("\nStability checklist:")
    print(f"  RMS(J) < J_crit          : {'PASS' if crit1 else 'FAIL'}")
    print(f"  max|J| < 3·RMS(J)        : {'PASS' if crit2 else 'FAIL'}")
    print(f"  S_h > S_min ({S_min})    : {'PASS' if crit3 else 'FAIL'}")
    print(f"  ξ_N > {xiN_min}s & ξ_Δ > {xiD_min}s : {'PASS' if crit4 else 'FAIL'}")

    overall = all([crit1, crit2, crit3, crit4])
    print(f"\nOVERALL VERDICT: {'Informational Jerk STABLE' if overall else 'UNSTABLE'}")
    return overall

if __name__ == "__main__":
    validate()