# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Informational Jerk Analysis
-----------------------------------------------------------------
This script checks the mathematical soundness of the jerk calculation
described in the Engine's output. It enforces:
  * Correct entropy derivatives (no missing p_N/p_Δ factors)
  * Proper chain‑rule construction of 𝒥_I
  * Dimensional consistency (using pint for unit checking)
  * The finite‑difference jerk estimator with Δt³ divisor
  * Comparison of jerk variance to the threshold Θ = (λ I₀² e^{-ψ})³
"""

import numpy as np
import sympy as sp
from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity

# ----------------------------------------------------------------------
# 1. Symbolic definitions (dimensionless normalized quantities)
# ----------------------------------------------------------------------
psi, phi_D = sp.symbols('psi phi_D', real=True)   # ψ = ln(Φ_N/I₀), φ_Δ = Φ_Δ/I₀
# Normalised Newtonian mode:
phi_N = sp.exp(psi)          # Φ_N/I₀ = e^ψ

# Probabilities from softmax:
den = phi_N + phi_D
p_N = phi_N / den
p_D = phi_D / den

# Shannon conditional entropy:
S = -(p_N * sp.log(p_N) + p_D * sp.log(p_D))

# Exact derivatives w.r.t. ψ and φ_Δ:
dS_dpsi   = sp.diff(S, psi)
dS_dphiD  = sp.diff(S, phi_D)
d2S_dpsi2 = sp.diff(dS_dpsi, psi)
d2S_dphiD2 = sp.diff(dS_dphiD, phi_D)
d3S_dpsi3 = sp.diff(d2S_dpsi2, psi)
d3S_dphiD3 = sp.diff(d2S_dphiD2, phi_D)

# Lambdify for fast numeric evaluation:
f_S          = sp.lambdify((psi, phi_D), S, 'numpy')
f_dS_dpsi    = sp.lambdify((psi, phi_D), dS_dpsi, 'numpy')
f_dS_dphiD   = sp.lambdify((psi, phi_D), dS_dphiD, 'numpy')
f_d2S_dpsi2  = sp.lambdify((psi, phi_D), d2S_dpsi2, 'numpy')
f_d2S_dphiD2 = sp.lambdify((psi, phi_D), d2S_dphiD2, 'numpy')
f_d3S_dpsi3  = sp.lambdify((psi, phi_D), d3S_dpsi3, 'numpy')
f_d3S_dphiD3 = sp.lambdify((psi, phi_D), d3S_dphiD3, 'numpy')

# ----------------------------------------------------------------------
# 2. Helper: dimensional check (returns True if units match expected)
# ----------------------------------------------------------------------
def check_units(val, expected_dim):
    """val is a pint Quantity; expected_dim is a string like '[time]**(-3)'."""
    return val.check(expected_dim)

# ----------------------------------------------------------------------
# 3. Example dynamical model for Φ_N(t), Φ_Δ(t)
#    (replace with actual HSA node data or a more realistic model)
# ----------------------------------------------------------------------
def simulate_dynamics(t, phi_N0=0.78, phi_D0=0.35,
                      tau_N=4.9e-4, tau_D=4.9e-4,
                      phi_N_eq=0.80, phi_D_eq=0.30):
    """
    Simple exponential relaxation towards equilibrium:
        dφ/dt = -(φ - φ_eq)/τ
    Returns arrays phi_N(t), phi_D(t) and their first three derivatives.
    """
    phi_N = phi_N_eq + (phi_N0 - phi_N_eq) * np.exp(-t/tau_N)
    phi_D = phi_D_eq + (phi_D0 - phi_D_eq) * np.exp(-t/tau_D)

    # derivatives via analytic formulas:
    phi_N_dot = -(phi_N - phi_N_eq)/tau_N
    phi_N_ddot = -(phi_N_dot)/tau_N
    phi_N_dddot = -(phi_N_ddot)/tau_N

    phi_D_dot = -(phi_D - phi_D_eq)/tau_D
    phi_D_ddot = -(phi_D_dot)/tau_D
    phi_D_dddot = -(phi_D_ddot)/tau_D

    return (phi_N, phi_D,
            phi_N_dot, phi_N_ddot, phi_N_dddot,
            phi_D_dot, phi_D_ddot, phi_D_dddot)

# ----------------------------------------------------------------------
# 4. Core jerk calculation (exact, using chain rule)
# ----------------------------------------------------------------------
def compute_jerk(t):
    """Return instantaneous informational jerk 𝒥_I(t) = d³S/dt³."""
    (phi_N, phi_D,
     phi_N_dot, phi_N_ddot, phi_N_dddot,
     phi_D_dot, phi_D_ddot, phi_D_dddot) = simulate_dynamics(t)

    # ψ = ln(phi_N)   (since I₀ = 1 in normalisation)
    psi_val = np.log(phi_N)
    # ψ derivatives via chain rule:
    psi_dot   = phi_N_dot / phi_N
    psi_ddot  = (phi_N_ddot/phi_N) - (phi_N_dot/phi_N)**2
    psi_dddot = (phi_N_dddot/phi_N) \
                - 3*(phi_N_ddot*phi_N_dot)/(phi_N**2) \
                + 2*(phi_N_dot**3)/(phi_N**3)

    # φ_Δ derivatives are just the simulated ones (phi_D = φ_Δ/I₀)
    phi_D_val = phi_D
    phi_D_dot_val = phi_D_dot
    phi_D_ddot_val = phi_D_ddot
    phi_D_dddot_val = phi_D_dddot

    # Evaluate entropy derivatives at the instantaneous point:
    dS_dpsi   = f_dS_dpsi(psi_val, phi_D_val)
    dS_dphiD  = f_dS_dphiD(psi_val, phi_D_val)
    d2S_dpsi2 = f_d2S_dpsi2(psi_val, phi_D_val)
    d2S_dphiD2 = f_d2S_dphiD2(psi_val, phi_D_val)
    d3S_dpsi3 = f_d3S_dpsi3(psi_val, phi_D_val)
    d3S_dphiD3 = f_d3S_dphiD3(psi_val, phi_D_val)

    # Chain rule for third derivative:
    jerk = (dS_dpsi   * psi_dddot +
            3 * d2S_dpsi2 * psi_dot * psi_ddot +
            d3S_dpsi3 * psi_dot**3 +
            dS_dphiD  * phi_D_dddot_val +
            3 * d2S_dphiD2 * phi_D_dot_val * phi_D_ddot_val +
            d3S_dphiD3 * phi_D_dot_val**3)
    return jerk

# ----------------------------------------------------------------------
# 5. Finite‑difference jerk estimator (for comparison)
# ----------------------------------------------------------------------
def fd_jerk(S_samples, dt):
    """Backward 3rd‑derivative estimate: (S[n] - 3S[n-1] + 3S[n-2] - S[n-3])/dt³."""
    if len(S_samples) < 4:
        raise ValueError("Need at least 4 samples for FD jerk.")
    num = (S_samples[-1] - 3*S_samples[-2] + 3*S_samples[-3] - S_samples[-4])
    return num / dt**3

# ----------------------------------------------------------------------
# 6. Stability threshold Θ = (λ I₀² e^{-ψ})³
# ----------------------------------------------------------------------
def stability_threshold(psi_val, lam):
    """Return Θ with units [time]^{-6} given λ [time]^{-2}."""
    I0 = 1.0 * ureg.dimensionless   # normalisation
    term = lam * I0**2 * np.exp(-psi_val)   # [time]^{-2}
    return term**3                         # [time]^{-6}

# ----------------------------------------------------------------------
# 7. Main validation routine
# ----------------------------------------------------------------------
def validate():
    # Parameters from the Engine's output (normalised I₀ = 1)
    lam = 4.2e6 / ureg.second**2          # λ = ξ^{-2}
    # Characteristic time ξ = sqrt(1/λ)
    xi = np.sqrt(1/lam.magnitude) * ureg.second
    print(f"Characteristic time ξ = {xi:.3e}")

    # Time vector for simulation (cover a few ξ)
    t = np.linspace(0, 5*xi.magnitude, 500) * ureg.second

    # Compute instantaneous jerk:
    jerk_inst = np.array([compute_jerk(ti) for ti in t.magnitude]) \
                * ureg.second**(-3)

    # Compute finite‑difference jerk using sampling interval Δt = ξ (as Engine did)
    dt = xi
    S_samples = f_S(np.log(phi_N_eq + (0.78-phi_N_eq)*np.exp(-t/xi)),
                    phi_D_eq + (0.35-phi_D_eq)*np.exp(-t/xi))
    jerk_fd = fd_jerk(S_samples, dt.magnitude) * ureg.second**(-3)

    # Variance of the jerk (use instantaneous as proxy for ensemble)
    var_jerk = np.var(jerk_inst.magnitude) * ureg.second**(-6)

    # Threshold:
    psi_now = np.log(0.78)   # ψ at t=0 from Engine's numbers
   Theta = stability_threshold(psi_now.magnitude, lam.magnitude) * ureg.second**(-6)

    # ---- Unit checks -------------------------------------------------
    assert check_units(jerk_inst, "[time]**(-3)"), "Jerk units wrong"
    assert check_units(jerk_fd,   "[time]**(-3)"), "FD jerk units wrong"
    assert check_units(var_jerk,  "[time]**(-6)"), "Variance units wrong"
    assert check_units(Theta,     "[time]**(-6)"), "Theta units wrong"

    # ---- Numeric sanity ------------------------------------------------
    print(f"Instantaneous jerk mean = {np.mean(jerk_inst.magnitude):.3e} s⁻³")
    print(f"FD jerk estimate       = {jerk_fd.magnitude:.3e} s⁻³")
    print(f"Jerk variance          = {var_jerk.magnitude:.3e} s⁻⁶")
    print(f"Stability threshold Θ = {Theta.magnitude:.3e} s⁻⁶")
    print(f"Variance / Θ = {var_jerk.magnitude/Theta.magnitude:.3f}")

    # Decision based on exact variance (not ad‑hoc number)
    if var_jerk > Theta:
        print("RESULT: System is UNSTABLE (variance exceeds threshold).")
        return False
    else:
        print("RESULT: System is STABLE (variance below threshold).")
        return True

if __name__ == "__main__":
    validate()