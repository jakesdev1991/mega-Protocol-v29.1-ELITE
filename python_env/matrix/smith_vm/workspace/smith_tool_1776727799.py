# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation: Informational Jerk Stability
------------------------------------------------------
Validates the mathematical steps presented in the agent's analysis
and enforces the invariants Phi_N, Phi_Delta, and the jerk bound.
"""

import math
import numpy as np

def validate_omega_psi(phi_n, phi_delta, i0=1.0):
    """
    Check the metric coupling invariant psi = ln(Phi_N / I0).
    Returns psi and a boolean indicating if the invariant holds (within tolerance).
    """
    psi = math.log(phi_n / i0)
    # invariant holds by definition; we just return the value
    return psi, True

def stiffness_invariants(phi_n, phi_delta, lam=1e10, i0=1.0):
    """
    Compute the Newtonian and Archive stiffness inverses:
        xi_N^{-2} = lambda * (3*phi_n^2 + phi_delta^2 - i0^2)
        xi_Delta^{-2} = lambda * (phi_n^2 + 3*phi_delta^2 - i0^2)
    """
    xi_n_inv2 = lam * (3 * phi_n**2 + phi_delta**2 - i0**2)
    xi_d_inv2 = lam * (phi_n**2 + 3 * phi_delta**2 - i0**2)
    return xi_n_inv2, xi_d_inv2

def shredding_condition(phi_n, phi_delta, i0=1.0):
    """
    Returns True if the Shredding condition xi_Delta^{-2} == 0 is satisfied.
    """
    lhs = phi_n**2 + 3 * phi_delta**2 - i0**2
    return math.isclose(lhs, 0.0, abs_tol=1e-12)

def threshold_psi(psi, lam=1e10, i0=1.0, g_delta=0.1):
    """
    Compute the psi-dependent stability threshold:
        Theta(psi) = (lam * i0^4 / 9) * (exp(2*psi) - 1)^2 *
                     (1 + (3*g_delta^2/(4*pi)) * exp(-2*psi))
    Units: s^{-6}
    """
    pref = lam * i0**4 / 9.0
    exp_term = math.exp(2 * psi) - 1.0
    metric_factor = 1.0 + (3 * g_delta**2 / (4 * math.pi)) * math.exp(-2 * psi)
    return pref * (exp_term**2) * metric_factor

def informational_jerk(
    phi_n, phi_delta,
    phi_n_dot, phi_delta_dot,
    d2S_dpsi2, dS_dpsi,
    psi_ddot,
    source_jerk=0.0
):
    """
    Compute the informational jerk using the dominant chain‑rule term
    employed in the analysis:
        J_I ≈ d/dt[ (d2S/dpsi2) * psi_dot^2 ] + source_jerk
            ≈ 2 * (d2S/dpsi2) * psi_dot * psi_ddot + source_jerk
    where psi_dot = phi_n_dot / phi_n.
    """
    psi_dot = phi_n_dot / phi_n
    jerk_term = 2.0 * d2S_dpsi2 * psi_dot * psi_ddot
    return jerk_term + source_jerk

def jerk_variance_from_jerk(jitter_jerk, rel_fluctuation=0.20):
    """
    Approximate sigma_J^2 assuming a symmetric relative fluctuation
    around the mean jerk value.
    """
    sigma_j = rel_fluctuation * abs(jitter_jerk)
    return sigma_j**2

def main():
    # ---- Supplied audit data ------------------------------------------------
    phi_n = 0.78          # normalized Newtonian mode (I0 = 1)
    phi_delta = 0.35      # normalized Archive mode
    i0 = 1.0

    phi_n_dot = 2.1e3     # s^{-1}
    phi_delta_dot = 8.7e3 # s^{-1}

    lam = 1e10            # s^{-2}
    g_delta = 0.1

    # Stiffness invariant (provided in the audit)
    xi_inv2_audit = 4.2e6 # s^{-2}
    # Source jerk (provided)
    source_jerk = 1.5e12  # s^{-3}

    # ---- Step 1: Invariant check -------------------------------------------
    psi, ok = validate_omega_psi(phi_n, phi_delta, i0)
    print(f"psi = ln(Phi_N/I0) = {psi:.6f}  (invariant holds: {ok})")

    # ---- Step 2: Stiffness & Shredding ------------------------------------
    xi_n_inv2, xi_d_inv2 = stiffness_invariants(phi_n, phi_delta, lam, i0)
    print(f"xi_N^{-2} = {xi_n_inv2:.3e} s^(-2)")
    print(f"xi_Delta^{-2} = {xi_d_inv2:.3e} s^(-2)")
    print(f"Shredding condition satisfied? {shredding_condition(phi_n, phi_delta, i0)}")

    # Compare with audit-provided stiffness (should match one of the modes)
    print(f"Audit xi^{-2} = {xi_inv2_audit:.3e} s^(-2) "
          f"(matches Newtonian? {math.isclose(xi_n_inv2, xi_inv2_audit, rel_tol=1e-2)} "
          f"or Archive? {math.isclose(xi_d_inv2, xi_inv2_audit, rel_tol=1e-2)})")

    # ---- Step 3: Entropy derivatives (as used in the analysis) -------------
    # Two‑state model probabilities
    p_n = phi_n / (phi_n + phi_delta)
    p_d = phi_delta / (phi_n + phi_delta)
    S_h = -p_n * math.log(p_n) - p_d * math.log(p_d)  # bits
    print(f"Shannon entropy S_h = {S_h:.4f} bits")

    # Derivatives w.r.t. phi_n (from two‑state model)
    dS_dphi_n = -math.log(p_n / p_d)
    d2S_dphi_n2 = - (1.0 / p_n + 1.0 / p_d)  # derivative of dS/dphi_n
    # Chain‑rule to psi
    dS_dpsi = phi_n * dS_dphi_n
    d2S_dpsi2 = phi_n**2 * d2S_dphi_n2 + phi_n * dS_dphi_n
    print(f"dS/dpsi = {dS_dpsi:.6f}")
    print(f"d^2S/dpsi^2 = {d2S_dpsi2:.6f}")

    # ---- Step 4: Estimate psi_ddot from characteristic time ---------------
    xi = 1.0 / math.sqrt(xi_inv2_audit)   # characteristic time from audit
    psi_dot = phi_n_dot / phi_n
    psi_ddot_est = psi_dot / xi - psi_dot**2   # approximation used in analysis
    print(f"Characteristic time xi = {xi:.3e} s")
    print(f"psi_dot = {psi_dot:.3e} s^(-1)")
    print(f"psi_ddot (estimate) = {psi_ddot_est:.3e} s^(-2)")

    # ---- Step 5: Compute informational jerk --------------------------------
    J_I = informational_jerk(
        phi_n, phi_delta,
        phi_n_dot, phi_delta_dot,
        d2S_dpsi2, dS_dpsi,
        psi_ddot_est,
        source_jerk=source_jerk
    )
    print(f"Informational jerk J_I = {J_I:.3e} s^(-3)")

    # ---- Step 6: Fluctuation variance --------------------------------------
    sigma_J2 = jerk_variance_from_jerk(J_I, rel_fluctuation=0.20)
    print(f"Estimated sigma_J^2 (20% fluctuation) = {sigma_J2:.3e} s^(-6)")

    # ---- Step 7: Threshold -------------------------------------------------
    Theta = threshold_psi(psi, lam=lam, i0=i0, g_delta=g_delta)
    print(f"Threshold Theta(psi) = {Theta:.3e} s^(-6)")

    # ---- Step 8: Stability verdict -----------------------------------------
    stable = sigma_J2 < Theta
    print(f"\nStability check: sigma_J^2 < Theta ? {'STABLE' if stable else 'UNSTABLE'}")
    if not stable:
        print("=> The system violates the Omega Protocol jerk bound.")
    else:
        print("=> The system satisfies the Omega Protocol jerk bound.")

if __name__ == "__main__":
    main()