# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for POASH‑Ω refined proposal.
Checks:
  * PHI in [0,1]
  * Phi_N >= 0.7, Phi_Delta <= 0.6
  * Stiffness invariants xi_N, xi_Delta > 0
  * psi = ln(xi/xi0) real
  * Optional: dimensional consistency (inputs must be dimensionless)
"""

import numpy as np

def validate_pipeline(PHI, A, Phi_N0, Phi_Delta0,
                      alpha, beta, gamma,
                      lam, I0, xi0,
                      coh_avg):
    """
    Parameters
    ----------
    PHI : float or array-like
        Pipeline Health Index (should be in [0,1]).
    A : array-like
        Harmonic amplitude vector [A1, A2, ...].
    Phi_N0, Phi_Delta0 : float
        Baseline covariant modes.
    alpha, beta, gamma : float
        Mapping coefficients.
    lam : float
        Coupling constant in V(I) = lam/4 * (I^2 - I0^2)^2.
    I0 : float
        Equilibrium information content.
    xi0 : float
        Reference correlation length.
    coh_avg : float
        Average coherence <coh(k)> (must be >0).
    """
    # ----- 1. Basic range checks -----
    PHI = np.asarray(PHI, dtype=float)
    if np.any(PHI < 0) or np.any(PHI > 1):
        raise ValueError("PHI must lie in the interval [0,1].")
    
    # ----- 2. Information content I(t) -----
    A = np.asarray(A, dtype=float)
    power = A**2
    p_k = power / np.sum(power)
    # avoid log(0)
    p_k = np.where(p_k == 0, np.finfo(float).tiny, p_k)
    I = -np.sum(p_k * np.log(p_k))
    
    # ----- 3. Covariant modes from proposed mapping -----
    # dPHI/dt approximated by finite difference if array supplied
    if PHI.ndim == 0:
        dPHI_dt = 0.0
    else:
        dPHI_dt = np.gradient(PHI)  # assumes unit time step
    
    Phi_N = Phi_N0 + alpha * dPHI_dt
    Phi_Delta = Phi_Delta0 - beta * PHI + gamma * np.var(A)
    
    if np.any(Phi_N < 0.7):
        raise ValueError(f"Phi_N ({Phi_N}) violates lower bound 0.7.")
    if np.any(Phi_Delta > 0.6):
        raise ValueError(f"Phi_Delta ({Phi_Delta}) violates upper bound 0.6.")
    
    # ----- 4. Stiffness invariants from coherence -----
    if coh_avg <= 0:
        raise ValueError("Average coherence must be positive.")
    xi_N_inv2 = lam * (3.0/coh_avg + 1.0/coh_avg**2)
    xi_Delta_inv2 = lam * (1.0/coh_avg + 3.0/coh_avg**2)
    if xi_N_inv2 <= 0 or xi_Delta_inv2 <= 0:
        raise ValueError("Computed inverse stiffness squared must be positive.")
    xi_N = 1.0/np.sqrt(xi_N_inv2)
    xi_Delta = 1.0/np.sqrt(xi_Delta_inv2)
    
    # ----- 5. Invariant psi -----
    xi = np.sqrt(xi_N * xi_Delta)  # geometric mean as a scalar proxy
    if xi <= 0:
        raise ValueError("Correlation length xi must be positive.")
    psi = np.log(xi / xi0)
    if not np.isfinite(psi):
        raise ValueError("psi must be a real finite number.")
    
    # ----- 6. Optional dimensional check (inputs assumed dimensionless) -----
    # If the user wishes to enforce dimensions, they can supply a dict of units
    # and verify that each term in the action has the same dimension.
    # For simplicity we assume dimensionless inputs.
    
    # ----- 7. Return validated quantities for downstream use -----
    return {
        "I": I,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "xi_N": xi_N,
        "xi_Delta": xi_Delta,
        "psi": psi
    }

# Example usage (replace with actual data from a pipeline)
if __name__ == "__main__":
    # Dummy data for illustration
    PHI_example = 0.85
    A_example = np.array([1.0, 0.5, 0.2])  # harmonic amplitudes
    Phi_N0_example = 0.75
    Phi_Delta0_example = 0.5
    alpha_example = 0.1
    beta_example = 0.2
    gamma_example = 0.05
    lam_example = 1.0
    I0_example = 0.5
    xi0_example = 1.0
    coh_avg_example = 0.7
    
    try:
        result = validate_pipeline(
            PHI_example, A_example,
            Phi_N0_example, Phi_Delta0_example,
            alpha_example, beta_example, gamma_example,
            lam_example, I0_example, xi0_example,
            coh_avg_example
        )
        print("Validation passed. Computed quantities:")
        for k, v in result.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print("Validation failed:", e)