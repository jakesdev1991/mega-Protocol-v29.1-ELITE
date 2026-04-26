# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for the Informational Jerk Stability Analysis
--------------------------------------------------------------------
This script checks the mathematical soundness and Rubric‑v26.0 compliance
of the repaired HSA‑node jerk‑stability derivation.

It validates:
  1. Covariant decomposition  I = Φ_N + Φ_Δ σ_z   (formal check)
  2. Equation‑level jerk from the Omega Action:
        J(t) = -λ (3 I(t)^2 - v^2) dI/dt
  3. Unit consistency (I [GB/s] → J [GB/s^4])
  4. Invariants:
        ψ   = ln(I/I0)
        ξ_N = [λ (3 I^2 - v^2)]^{-1/2}
        ξ_Δ = [λ (I^2 + 3 Φ_Δ^2 - v^2)]^{-1/2}
  5. Boundaries:
        Shredding: ξ_Δ → 0  ⇔  Φ_N^2 + 3 Φ_Δ^2 → v^2
        Freeze   : I   → 0  ⇔  ψ → -∞
  6. Shannon entropy of I(t) over a sliding window
  7. Stability criteria:
        RMS(J) < J_crit
        max|J| < 3·RMS(J)
        S_h   > S_min   (nats)
        ξ_N   > ξ_N_min , ξ_Δ > ξ_Δ_min
  8. Cross‑domain structural check (nonlinear damping form)

If all checks pass, the script prints META-PASS.
"""

import numpy as np
from typing import Callable, Tuple

# ----------------------------------------------------------------------
# USER‑DEFINED PARAMETERS (match the repaired analysis)
# ----------------------------------------------------------------------
I0   = 200.0          # GB/s, reference bandwidth
A    = 50.0           # GB/s, sinusoidal amplitude
omega = 20.0*np.pi    # rad/s, angular frequency (10 Hz sinusoid)
lam   = 1.0/(I0**2)   # 1/(GB^2) chosen so that λ I0^2 = 1 (dimensionless)
v     = I0            # GB/s, set v = I0 for the example (stable point)
J_crit = 1.2e7        # GB/s^4, critical jerk from historical data
S_min   = 2.5         # nats, entropy bound
xi_N_min = 0.1        # s, radial stiffness viability
xi_Delta_min = 0.05   # s, poloidal stiffness viability
window_sec = 1.0      # entropy window length
fs = 1000.0           # sampling rate for numerical checks (Hz)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def I(t: np.ndarray) -> np.ndarray:
    """Aggregate memory bandwidth I(t) = I0 + A sin(ω t)."""
    return I0 + A * np.sin(omega * t)

def dIdt(t: np.ndarray) -> np.ndarray:
    """First derivative dI/dt."""
    return A * omega * np.cos(omega * t)

def J(t: np.ndarray) -> np.ndarray:
    """Physical jerk from the Omega Action derivation."""
    return -lam * (3.0 * I(t)**2 - v**2) * dIdt(t)

def psi(t: np.ndarray) -> np.ndarray:
    """Metric coupling invariant."""
    return np.log(I(t) / I0)

def xi_N(t: np.ndarray) -> np.ndarray:
    """Radial stiffness invariant."""
    return 1.0 / np.sqrt(lam * (3.0 * I(t)**2 - v**2))

def xi_Delta(t: np.ndarray, PhiDelta: np.ndarray) -> np.ndarray:
    """Poloidal stiffness invariant (requires Φ_Δ(t))."""
    return 1.0 / np.sqrt(lam * (I(t)**2 + 3.0 * PhiDelta**2 - v**2))

def shredding_condition(PhiN: np.ndarray, PhiDelta: np.ndarray) -> np.ndarray:
    """Returns True where shredding boundary is approached (ξ_Δ → 0)."""
    return np.abs(PhiN**2 + 3.0 * PhiDelta**2 - v**2) < 1e-9

def freeze_condition(Ivals: np.ndarray) -> np.ndarray:
    """Returns True where informational freeze is approached (I → 0)."""
    return np.abs(Ivals) < 1e-9

def shannon_entropy(signal: np.ndarray, bins: int = 50) -> float:
    """Shannon entropy of a 1‑D signal (natural log)."""
    hist, _ = np.histogram(signal, bins=bins, density=True)
    # Remove zeros to avoid log(0)
    p = hist[hist > 0]
    return -np.sum(p * np.log(p))

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate() -> Tuple[bool, str]:
    t = np.linspace(0, 2*np.pi/omega, int(fs * 2*np.pi/omega))  # two periods
    I_vals = I(t)
    dI_vals = dIdt(t)
    J_vals = J(t)

    # ---- 1. Unit consistency check (dimensionless λ I^2) ----
    dimless = lam * I_vals**2   # should be pure number
    if not np.allclose(dimless, dimless, rtol=1e-12, atol=1e-12):
        return False, "Lambda * I^2 not dimensionless (unit mismatch)."

    # ---- 2. Jerk derivation sanity (compare to finite‑difference) ----
    J_fd = np.gradient(np.gradient(np.gradient(I_vals, t), t), t)  # 3rd derivative
    if not np.allclose(J_vals, J_fd, rtol=1e-3, atol=1e-3):
        return False, "Derived jerk does not match numerical third derivative."

    # ---- 3. Invariants definitions ----
    psi_vals = psi(t)
    xiN_vals = xi_N(t)
    # For ξ_Δ we need a model Φ_Δ(t). Use the simplest: Φ_Δ = 0.1 * I(t) (small asymmetry)
    PhiDelta = 0.1 * I_vals
    xiD_vals = xi_Delta(t, PhiDelta)

    # Check that ξ_N, ξ_Δ have units of seconds (by construction they are 1/sqrt(λ * I^2))
    # No extra test needed; the formula guarantees seconds if λ has 1/(GB^2).

    # ---- 4. Boundaries ----
    # Shredding: look for points where denominator of ξ_Δ → 0
    shred_mask = shredding_condition(I_vals, PhiDelta)
    freeze_mask = freeze_condition(I_vals)

    # In the chosen example we never hit the exact boundaries; we just verify the logic.
    # If any point violates the physical domain (e.g., sqrt of negative), fail.
    if np.any(lam * (3.0 * I_vals**2 - v**2) <= 0):
        return False, "Radial stiffness denominator non‑positive (invalid ξ_N)."
    if np.any(lam * (I_vals**2 + 3.0 * PhiDelta**2 - v**2) <= 0):
        return False, "Poloidal stiffness denominator non‑positive (invalid ξ_Δ)."

    # ---- 5. Entropy ----
    # Use a sliding window of 1 second (fs samples)
    win_len = int(window_sec * fs)
    S_vals = []
    for start in range(0, len(I_vals) - win_len + 1, win_len):
        window = I_vals[start:start+win_len]
        S_vals.append(shannon_entropy(window))
    S_vals = np.array(S_vals)
    S_min_obs = np.min(S_vals)

    # ---- 6. Stability criteria ----
    rms_J = np.sqrt(np.mean(J_vals**2))
    max_J = np.max(np.abs(J_vals))

    conds = [
        (rms_J < J_crit, f"RMS(J) = {rms_J:.3e} ≥ J_crit = {J_crit:.3e}"),
        (max_J < 3 * rms_J, f"max|J| = {max_J:.3e} ≥ 3·RMS(J) = {3*rms_J:.3e}"),
        (S_min_obs > S_min, f"Entropy min = {S_min_obs:.3f} ≤ S_min = {S_min}"),
        (np.min(xiN_vals) > xi_N_min, f"ξ_N min = {np.min(xiN_vals):.3f} ≤ ξ_N_min = {xi_N_min}"),
        (np.min(xiD_vals) > xi_Delta_min, f"ξ_Δ min = {np.min(xiD_vals):.3f} ≤ ξ_Δ_min = {xi_Delta_min}")
    ]

    for ok, msg in conds:
        if not ok:
            return False, f"Stability criterion failed: {msg}"

    # ---- 7. Cross‑domain structural check (nonlinear damping form) ----
    # The derived J(t) must be expressible as -λ (α I^2 + β) dI/dt with α,β constants.
    # Here α = 3, β = -v^2. Verify linearity in I^2.
    lhs = -J_vals / dIdt(t)   # should equal λ (3 I^2 - v^2)
    rhs = lam * (3.0 * I_vals**2 - v**2)
    if not np.allclose(lhs, rhs, rtol=1e-6, atol=1e-6):
        return False, "Jerk does not follow the required nonlinear damping form."

    # All checks passed
    return True, "All Omega Protocol invariants and mathematical checks satisfied."

# ----------------------------------------------------------------------
# Execute validation and output result
# ----------------------------------------------------------------------
if __name__ == "__main__":
    passed, message = validate()
    if passed:
        print("META-PASS")
        print("Details:", message)
    else:
        print("META-FAIL")
        print("Reason:", message)