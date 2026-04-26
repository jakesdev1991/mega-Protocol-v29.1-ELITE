# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol v26.0 compliance checker for Informational Jerk Stability.
Validates the repaired HSA node analysis against the Rubric.
"""

import numpy as np
from scipy.stats import entropy

# -------------------------- USER‑DEFINED PARAMETERS --------------------------
# Physical constants (chosen to match the example in the analysis)
I0 = 200.0          # GB/s, reference bandwidth
lam = 1.0e-4        # 1/(GB^2) – coupling constant (chosen for illustration)
v  = 200.0          # GB/s, vacuum expectation value of the correlation field
Jcrit = 1.2e7       # GB/s^4, critical jerk threshold (from historical stable op)
Sh_min = 2.5        # nats, entropy lower bound
xiN_min = 0.1       # s, radial stiffness lower bound
xiD_min = 0.05      # s, poloidal stiffness lower bound
# ---------------------------------------------------------------------------

def I_t(t):
    """Example bandwidth: I(t) = 200 + 50*sin(20π t)  [GB/s]"""
    return 200.0 + 50.0 * np.sin(20.0 * np.pi * t)

def dIdt(t, dt=1e-4):
    """Numerical first derivative (central difference)."""
    return (I_t(t+dt) - I_t(t-dt)) / (2*dt)

def jerk_analytic(t):
    """Physical jerk from Omega Action: J = -λ(3I^2 - v^2) dI/dt."""
    I = I_t(t)
    return -lam * (3.0*I**2 - v**2) * dIdt(t)

def jerk_numeric(t, dt=1e-4):
    """Third derivative via finite differences (for unit/check)."""
    # Use a higher‑order stencil for better accuracy
    return (I_t(t+2*dt) - 2*I_t(t+dt) + 2*I_t(t-dt) - I_t(t-2*dt)) / (2*dt**3)

def compute_invariants(t):
    """Compute ψ, ξ_N, ξ_Δ from the definitions."""
    I = I_t(t)
    # ψ = ln(I/I0)
    psi = np.log(I / I0)
    # Radial stiffness: ξ_N = [λ(3I^2 - v^2)]^{-1/2}
    xi_N = 1.0 / np.sqrt(lam * (3.0*I**2 - v**2))
    # Poloidal stiffness: need Φ_Δ; for the homogeneous test we set Φ_Δ=0
    Phi_Delta = 0.0
    xi_Delta = 1.0 / np.sqrt(lam * (I**2 + 3.0*Phi_Delta**2 - v**2))
    return psi, xi_N, xi_Delta

def shannon_entropy(samples, bins=50):
    """Shannon conditional entropy of the bandwidth distribution."""
    hist, _ = np.histogram(samples, bins=bins, density=True)
    # Remove zeros to avoid log(0)
    p = hist[hist > 0]
    return -np.sum(p * np.log(p))

def main():
    # Time vector covering several periods of the test signal
    t_max = 0.5          # seconds (covers 5 periods of 20π rad/s)
    dt = 1e-4
    t = np.arange(0, t_max, dt)

    # ---- 1. Unit consistency check (dimension analysis) ----
    I_units = "GB/s"
    dI_units = "GB/s^2"
    d2I_units = "GB/s^3"
    J_units = "GB/s^4"
    # The analytic jerk expression yields units GB/s^4 by construction;
    # we verify numerically that the magnitude matches the finite‑difference third derivative.
    J_ana = jerk_analytic(t)
    J_num = jerk_numeric(t, dt)
    unit_match = np.allclose(J_ana, J_num, rtol=1e-2, atol=1e-2)
    if not unit_match:
        raise ValueError("Unit mismatch: analytic jerk does not agree with numerical third derivative.")

    # ---- 2. Invariant and boundary evaluation ----
    psi, xi_N, xi_Delta = compute_invariants(t)
    # Shredding Event: xi_Delta → 0  <=> denominator → ∞  <=> I^2 + 3Φ_Δ^2 → v^2
    # For our test (Φ_Δ=0) the condition reduces to I^2 → v^2.
    shredding_approach = np.min(np.abs(I_t(t)**2 - v**2))  # should be small if near shredding
    # Informational Freeze: I → 0  <=> ψ → -∞
    freeze_approach = np.min(I_t(t))  # should be >0 for non‑freeze

    # ---- 3. Entropy calculation ----
    Sh = shannon_entropy(I_t(t))

    # ---- 4. Stability criteria ----
    J_rms = np.sqrt(np.mean(J_ana**2))
    J_max = np.max(np.abs(J_ana))
    crit1 = J_rms < Jcrit
    crit2 = J_max < 3.0 * J_rms
    crit3 = Sh > Sh_min
    crit4 = np.all(xi_N > xiN_min) and np.all(xi_Delta > xiD_min)

    all_ok = crit1 and crit2 and crit3 and crit4 and unit_match

    # ---- Reporting ----
    print("=== Omega Protocol v26.0 Jerk‑Stability Audit ===")
    print(f"Unit consistency (analytic vs numeric jerk): {'PASS' if unit_match else 'FAIL'}")
    print(f"RMS(J) = {J_rms:.3e} GB/s^4  < Jcrit? {'PASS' if crit1 else 'FAIL'} (Jcrit={Jcrit:.3e})")
    print(f"max|J| = {J_max:.3e} GB/s^4  < 3·RMS? {'PASS' if crit2 else 'FAIL'}")
    print(f"Shannon entropy S_h = {Sh:.3f} nats  > {Sh_min}? {'PASS' if crit3 else 'FAIL'}")
    print(f"ξ_N min = {np.min(xi_N):.3f} s  > {xiN_min}? {'PASS' if np.all(xi_N>xiN_min) else 'FAIL'}")
    print(f"ξ_Δ min = {np.min(xi_Delta):.3f} s  > {xiD_min}? {'PASS' if np.all(xi_Delta>xiD_min) else 'FAIL'}")
    print(f"Shredding proximity (|I^2−v^2|_min) = {shredding_approach:.3e} (→0 indicates shredding)")
    print(f"Informational freeze proximity (I_min) = {freeze_approach:.3f} GB/s (→0 indicates freeze)")
    print("-" * 60)
    print(f"OVERALL VERDICT: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    exit(main())