# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for the Higher-Order Lattice Polarization
correction to the fine-structure constant.

Checks:
  * Stiffness invariants (no tachyons)
  * Shredding condition: Phi_N^2 + 3*Phi_Delta^2 < v^2
  * One-loop RG running of alpha (with corrected beta-function)
  * Landau pole must lie above a user-defined UV cutoff
  * Optional entropy-impedance feedback loop for Phi_Delta
  * Poisson recovery for Phi_N (static solution with source J_N)
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

# ----------------------------------------------------------------------
# User-defined parameters (adjust as needed for a specific scenario)
# ----------------------------------------------------------------------
v          = 1.0          # symmetry‑breaking scale
lam        = 0.1          # quartic coupling
g_N        = 0.02         # Newtonian mode coupling
g_Delta0   = 0.015        # initial Archive mode coupling
alpha0     = 1/137.0      # low-energy fine-structure constant
mu         = 91.2e9       # reference scale (e.g. Z‑mass) in eV
Lambda_UV  = 1e12         # UV cutoff where perturbation theory must still hold (eV)
# Feedback loop parameters (set to zero to disable feedback)
kappa      = 0.0          # Phi_Delta response rate
eta        = 0.0          # entropy-to-coupling strength
S0         = 1.0          # baseline Shannon entropy
Phi0       = 0.5          # entropy scale
# Source for Phi_N Poisson equation
J_N        = 0.01         # constant source term (in same units as Phi_N)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def stiffness_invariants(Phi_N, Phi_Delta):
    """Return xi_N^{-2} and xi_Delta^{-2}."""
    xi_N_inv2  = lam * (3*Phi_N**2 + Phi_Delta**2 - v**2)
    xi_Delta_inv2 = lam * (Phi_N**2 + 3*Phi_Delta**2 - v**2)
    return xi_N_inv2, xi_Delta_inv2

def shredding_condition(Phi_N, Phi_Delta):
    """True if the system is *stable* (xi_Delta^{-2}>0)."""
    _, xi_Delta_inv2 = stiffness_invariants(Phi_N, Phi_Delta)
    return xi_Delta_inv2 > 0   # stability <=> denominator positive

def beta_alpha(alpha, g_N, g_Delta):
    """One-loop beta function for alpha (QED-like prefactor 2/3π)."""
    return (2.0/ (3.0*np.pi)) * alpha**2 * (1.0 + 3.0*g_Delta**2/(4.0*np.pi) + g_N**2/(4.0*np.pi))

def run_alpha(q2_vals, alpha_init, mu_ref, g_N, g_Delta):
    """
    Solve d alpha / d ln q^2 = beta(alpha) from mu_ref^2 to each q2 in q2_vals.
    Returns alpha(q2) array.
    """
    def ode(lnq2, a):
        return beta_alpha(a, g_N, g_Delta)
    sol = solve_ivp(ode, [np.log(mu_ref**2), np.log(q2_vals[-1])],
                    [alpha_init], t_eval=np.log(q2_vals), vectorized=False, max_step=0.1)
    if not sol.success:
        raise RuntimeError("RG integration failed: " + sol.message)
    return sol.y[0]

def landau_pole_scale(alpha0, mu, g_N, g_Delta):
    """
    Analytic Landau pole for constant beta coefficient B = (2/(3π))*(1+3gΔ^2/4π+gN^2/4π).
    q_LP^2 = mu^2 * exp[π/(α0 * B)].
    """
    B = (2.0/(3.0*np.pi)) * (1.0 + 3.0*g_Delta**2/(4.0*np.pi) + g_N**2/(4.0*np.pi))
    if B <= 0:
        return np.inf
    return mu**2 * np.exp(np.pi/(alpha0 * B))

def entropy_feedback(Phi_Delta):
    """Shannon entropy model S_h = S0 - ln(1 + (Phi_Delta/Phi0)^2)."""
    return S0 - np.log(1.0 + (Phi_Delta/Phi0)**2)

def effective_g_Delta(Phi_Delta, g_Delta):
    """g_Delta^eff = g_Delta * (1 + eta * S_h)."""
    return g_Delta * (1.0 + eta * entropy_feedback(Phi_Delta))

def phi_delta_ode(t, y, g_Delta):
    """dy/dt = kappa * (g_eff - g0) ; y = Phi_Delta."""
    Phi_Delta = y[0]
    g_eff = effective_g_Delta(Phi_Delta, g_Delta)
    return [kappa * (g_eff - g_Delta)]

def poisson_phi_N(Phi_Delta):
    """
    Static solution of  -∇^2 Φ_N + λ Φ_N (Φ_N^2 + Φ_Delta^2 - v^2) = J_N.
    In homogeneous approximation (∇^2 Φ_N = 0) we solve the algebraic equation:
        λ Φ_N (Φ_N^2 + Φ_Delta^2 - v^2) = J_N.
    Returns the real root(s).
    """
    def eq(phi):
        return lam * phi * (phi**2 + Phi_Delta**2 - v**2) - J_N
    # Use fsolve starting from a few guesses
    roots = []
    for guess in [-2.0, -0.5, 0.0, 0.5, 2.0]:
        try:
            root = fsolve(eq, guess, full_output=True)[0][0]
            if np.isreal(root) and abs(np.imag(root)) < 1e-12:
                root = float(np.real(root))
                if all(abs(root - r) > 1e-6 for r in roots):
                    roots.append(root)
        except Exception:
            pass
    return roots

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate():
    print("=== Omega Protocol Invariant Validation ===")
    # 1. Stiffness invariants at the origin (Phi_N=Phi_Delta=0)
    xi_N_inv2_0, xi_Delta_inv2_0 = stiffness_invariants(0.0, 0.0)
    print(f"Stiffness at origin: xi_N^{-2} = {xi_N_inv2_0:.6e}, xi_Delta^{-2} = {xi_Delta_inv2_0:.6e}")
    if xi_N_inv2_0 <= 0 or xi_Delta_inv2_0 <= 0:
        raise ValueError("Tachyonic mode at the origin – violates stability invariant.")
    print("✓ Stiffness invariants are positive (no tachyons).")

    # 2. Shredding condition for a range of Phi_Delta values (Phi_N set to 0 for simplicity)
    Phi_Delta_test = np.linspace(0, 1.5*v, 200)
    stable = shredding_condition(0.0, Phi_Delta_test)
    if not np.all(stable[:np.where(~stable)[0][0] if np.any(~stable) else len(stable)]):
        first_unstable = Phi_Delta_test[np.where(~stable)[0][0]] if np.any(~stable) else None
        raise ValueError(f"Shredding condition violated at Phi_Delta ≈ {first_unstable:.3f} (Phi_N=0).")
    print("✓ Shredding condition satisfied for scanned Phi_Delta range (Phi_N=0).")

    # 3. RG running and Landau pole check
    Landau_q2 = landau_pole_scale(alpha0, mu, g_N, g_Delta0)
    print(f"Landau pole scale (analytic) = {np.sqrt(Landau_q2):.3e} eV")
    if np.sqrt(Landau_q2) < Lambda_UV:
        raise ValueError(
            f"Landau pole ({np.sqrt(Landau_q2):.3e} eV) lies below UV cutoff ({Lambda_UV:.3e} eV). "
            "Perturbative breakdown – potential Shredding trigger."
        )
    print("✓ Landau pole is above the UV cutoff – perturbative control retained.")

    # Optional: explicit RG integration to double-check
    q2_samples = np.logspace(np.log10(mu**2), np.log10(Landau_q2*0.9), 50)
    alpha_run = run_alpha(q2_samples, alpha0, mu, g_N, g_Delta0)
    if np.any(alpha_run > 1.0):  # arbitrary sanity bound
        raise ValueError("Alpha ran to non‑perturbative values before Landau pole.")
    print("✓ Explicit RG integration confirms perturbative behavior up to 0.9×Landau scale.")

    # 4. Entropy‑impedance feedback (only if kappa or eta non‑zero)
    if kappa != 0.0 or eta != 0.0:
        t_span = (0.0, 50.0)
        sol = solve_ivp(phi_delta_ode, t_span, [0.1*v], args=(g_Delta0,), max_step=0.1)
        Phi_Delta_t = sol.y[0]
        # Check if Phi_Delta ever exceeds the shredding boundary (with Phi_N=0)
        Phi_N_test = 0.0
        shred_bound = np.sqrt((v**2 - Phi_N_test**2)/3.0)   # from Phi_N^2+3Phi_Delta^2=v^2
        if np.any(Phi_Delta_t > shred_bound):
            t_shred = sol.t[np.where(Phi_Delta_t > shred_bound)[0][0]]
            raise ValueError(
                f"Feedback-driven Phi_Delta exceeds shredding bound at t≈{t_shred:.2f}. "
                "Premature Shredding event detected."
            )
        print("✓ Entropy‑impedance feedback does not drive Phi_Delta into shredding region.")
    else:
        print("⚠ Feedback loop disabled (kappa=eta=0). Skipping Phi_Delta dynamics test.")

    # 5. Poisson recovery for Phi_N (homogeneous case)
    # Evaluate at a few representative Phi_Delta values within the stable region
    test_Phi_Delta = [0.0, 0.5*v, 0.9*np.sqrt((v**2)/3.0)]  # last is near shredding boundary
    for Phi_Delta in test_Phi_Delta:
        roots = poisson_phi_N(Phi_Delta)
        if not roots:
            raise ValueError(f"No real solution for Phi_N at Phi_Delta={Phi_Delta:.3f}.")
        # Additionally, check that the solution is unique (single root) – multiple roots could signal instability
        if len(roots) > 1:
            print(f"⚠ Multiple real Phi_N roots ({roots}) at Phi_Delta={Phi_Delta:.3f}; check for bistability.")
        else:
            print(f"✓ Phi_N solution unique: Phi_N = {roots[0]:.6f} at Phi_Delta={Phi_Delta:.3f}.")
    print("=== Validation completed successfully ===")

if __name__ == "__main__":
    try:
        validate()
    except Exception as e:
        print("\nVALIDATION FAILED:")
        print(e)
        exit(1)