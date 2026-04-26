# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Checks the revised Shredding‑flaw analysis for:
  1. Metric positivity: 1 + Phi_Delta > 0
  2. Well‑defined Newtonian invariant: Phi_N > 0  => psi = ln(Phi_N) real
  3. Positive stiffness coefficients: xi_N > 0, xi_Delta > 0
  4. MPC-Omega constraint: Phi_Delta >= Phi_min
  5. Effective lattice spacing a_z = a * sqrt(1+Phi_Delta) stays above a cutoff
"""

import numpy as np

def validate_omega(Phi_N, Phi_Delta, xi_N, xi_Delta, a=1.0, a_cutoff=1e-3):
    """
    Parameters
    ----------
    Phi_N : float or array-like
        Newtonian mode (must be >0).
    Phi_Delta : float or array-like
        Anisotropic mode.
    xi_N, xi_Delta : float or array-like
        Stiffness coefficients (must be >0).
    a : float
        Base lattice spacing.
    a_cutoff : float
        Minimum allowed lattice spacing in the archive direction.
    
    Returns
    -------
    dict with validation flags and diagnostic values.
    """
    # Convert to numpy arrays for vectorised checks
    Phi_N = np.asarray(Phi_N, dtype=float)
    Phi_Delta = np.asarray(Phi_Delta, dtype=float)
    xi_N = np.asarray(xi_N, dtype=float)
    xi_Delta = np.asarray(xi_Delta, dtype=float)

    # 1. Metric positivity
    metric_pos = 1.0 + Phi_Delta > 0
    # 2. Newtonian positivity (for psi)
    newt_pos = Phi_N > 0
    # 3. Stiffness positivity
    stiff_pos = (xi_N > 0) & (xi_Delta > 0)

    # Compute invariants
    psi = np.log(Phi_N)  # only valid if newt_pos True
    # Avoid division by zero in Phi_min
    Phi_min = -1.0 + (xi_N / xi_Delta) * np.exp(psi)

    # 4. MPC-Omega constraint
    constraint_ok = Phi_Delta >= Phi_min

    # 5. Effective lattice spacing in archive direction
    a_z = a * np.sqrt(1.0 + Phi_Delta)
    spacing_ok = a_z >= a_cutoff

    # Overall validity (all conditions must hold)
    overall = metric_pos & newt_pos & stiff_pos & constraint_ok & spacing_ok

    return {
        "metric_positivity": bool(np.all(metric_pos)),
        "newtonian_positivity": bool(np.all(newt_pos)),
        "stiffness_positivity": bool(np.all(stiff_pos)),
        "MPC_Omega_constraint": bool(np.all(constraint_ok)),
        "lattice_spacing_ok": bool(np.all(spacing_ok)),
        "overall_valid": bool(np.all(overall)),
        "diagnostics": {
            "psi": psi,
            "Phi_min": Phi_min,
            "a_z": a_z,
            "violations": {
                "metric": np.where(~metric_pos)[0].tolist(),
                "newtonian": np.where(~newt_pos)[0].tolist(),
                "stiffness": np.where(~stiff_pos)[0].tolist(),
                "constraint": np.where(~constraint_ok)[0].tolist(),
                "spacing": np.where(~spacing_ok)[0].tolist(),
            }
        }
    }

# Example test sweep
if __name__ == "__main__":
    # Grid of physically plausible values
    Phi_N_vals   = np.linspace(0.1, 5.0, 50)          # >0
    Phi_Delta_vals = np.linspace(-0.9, 0.5, 50)      # > -1 to stay perturbative
    xi_N_vals    = np.ones_like(Phi_N_vals) * 0.5   # positive stiffness
    xi_Delta_vals= np.ones_like(Phi_N_vals) * 0.5

    # Meshgrid for exhaustive check
    PN, PD, xiN, xiD = np.meshgrid(Phi_N_vals, Phi_Delta_vals,
                                   xi_N_vals, xi_Delta_vals, indexing='ij')
    result = validate_omega(PN.ravel(), PD.ravel(),
                            xiN.ravel(), xiD.ravel(),
                            a=1.0, a_cutoff=1e-3)

    print("=== Omega Protocol Validation Summary ===")
    for k, v in result.items():
        if k != "diagnostics":
            print(f"{k:25}: {v}")
    print("\nDiagnostics (first 5 violations if any):")
    diag = result["diagnostics"]
    for key in ["metric","newtonian","stiffness","constraint","spacing"]:
        vio = diag["violations"][key]
        if vio:
            print(f"  {key}: {vio[:5]} (showing first 5)")
        else:
            print(f"  {key}: none")