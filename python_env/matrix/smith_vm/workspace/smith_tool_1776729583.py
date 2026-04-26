# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EDIP-Ω Invariant & Constraint Validator
---------------------------------------
This script checks that a candidate EDIP-Ω state satisfies the
Omega Physics Rubric invariants and the QP constraints used in
the MPC-Ω layer.

It is deliberately lightweight: you can plug in actual model
outputs (e.g., from a PINN) and run the checks.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions representing the PINN activations (as specified)
# ----------------------------------------------------------------------
def activate_phi_N(x):
    """Sigmoid -> output in [0,1]."""
    return 1.0 / (1.0 + np.exp(-x))

def activate_xi_Delta(x):
    """Softplus + 1 -> output >= 1."""
    return np.log1p(np.exp(x)) + 1.0  # softplus(x) = ln(1+exp(x))

def activate_xi_N(x):
    """Softplus -> output >= 0."""
    return np.log1p(np.exp(x))

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_edip_omega_state(
    Phi_N,          # scalar or array-like, estimated connectivity
    Phi_Delta,      # scalar or array-like, estimated asymmetry
    xi_N,           # scalar or array-like, coherence stiffness
    xi_Delta,       # scalar or array-like, asymmetry stiffness
    phi_n,          # scalar >0, effective mass ratio (m_eff/m)
    Phi_N0,         # scalar baseline connectivity (quiescent)
    ESI_k,          # scalar exposure stress index
    S_h,            # scalar Shannon entropy of coherence distribution
    P_meas,         # scalar measured plasma performance metric
    P_target,       # scalar target performance
    alpha, beta, gamma, lam  # scalar cost weights (non-negative)
):
    """
    Returns a dict with boolean flags for each checked invariant/constraint
    and a list of any violated conditions.
    """
    # Convert to numpy arrays for vectorized checks (scalars work fine)
    Phi_N      = np.asarray(Phi_N,      dtype=float)
    Phi_Delta  = np.asarray(Phi_Delta,  dtype=float)
    xi_N       = np.asarray(xi_N,       dtype=float)
    xi_Delta   = np.asarray(xi_Delta,   dtype=float)
    phi_n      = np.asarray(phi_n,      dtype=float)
    Phi_N0     = np.asarray(Phi_N0,     dtype=float)
    ESI_k      = np.asarray(ESI_k,      dtype=float)
    S_h        = np.asarray(S_h,        dtype=float)
    P_meas     = np.asarray(P_meas,     dtype=float)
    P_target   = np.asarray(P_target,   dtype=float)

    violations = []

    # 1. Phi_N in [0,1] (invariant from Rubric)
    if not np.all((Phi_N >= 0) & (Phi_N <= 1)):
        violations.append("Phi_N out of bounds [0,1]")
        Phi_N_ok = False
    else:
        Phi_N_ok = True

    # 2. xi_Delta >= 1 (invariant)
    if not np.all(xi_Delta >= 1):
        violations.append("xi_Delta < 1")
        xi_Delta_ok = False
    else:
        xi_Delta_ok = True

    # 3. xi_N >= 0 (coherence stiffness non‑negative)
    if not np.all(xi_N >= 0):
        violations.append("xi_N < 0")
        xi_N_ok = False
    else:
        xi_N_ok = True

    # 4. phi_n > 0 (required for log)
    if not np.all(phi_n > 0):
        violations.append("phi_n <= 0 (log undefined)")
        psi_ok = False
    else:
        psi = np.log(phi_n)          # ψ = ln(φ_n)
        psi_ok = True

    # 5. chi(t) = ln(Phi_N / Phi_N0)  (derived deviation, not an invariant)
    if not np.all(Phi_N0 > 0):
        violations.append("Phi_N0 <= 0 (cannot compute chi)")
        chi_ok = False
    else:
        chi = np.log(Phi_N / Phi_N0)
        chi_ok = True   # chi can be any real number; just check definition

    # 6. ESI_k <= 2.5 (QP constraint)
    if not np.all(ESI_k <= 2.5):
        violations.append("ESI_k > 2.5")
        ESI_ok = False
    else:
        ESI_ok = True

    # 7. Cost-function integrand non‑negativity
    #    J_integrand = (1 - S_h)^2 + alpha*S_h + lambda*(P_meas - P_target)^2
    #                + beta*(xi_Delta - 1)^2 + gamma*ReLU(ESI_k - 2.5)
    term1 = (1.0 - S_h) ** 2                     # >=0
    term2 = alpha * S_h                          # >=0 if alpha>=0
    term3 = lam * (P_meas - P_target) ** 2       # >=0
    term4 = beta * (xi_Delta - 1.0) ** 2         # >=0 if beta>=0
    term5 = gamma * np.maximum(0.0, ESI_k - 2.5) # >=0 if gamma>=0
    J_integrand = term1 + term2 + term3 + term4 + term5
    if not np.all(J_integrand >= 0):
        violations.append("Cost integrand negative (check weights/signs)")
        J_ok = False
    else:
        J_ok = True

    # 8. PINN activation ranges (spot‑check)
    #    We assume the raw network outputs are given as:
    #    raw_Phi_N, raw_xi_Delta, raw_xi_N
    #    For demonstration we reconstruct them from the activated values
    #    using the inverse activations (only for sanity, not required).
    try:
        # Inverse sigmoid
        raw_Phi_N = np.log(Phi_N / (1.0 - Phi_N + 1e-12))
        # Inverse softplus+1: y = softplus(x)+1  => x = log(exp(y-1)-1)
        raw_xi_Delta = np.log(np.exp(xi_Delta - 1.0) - 1.0)
        # Inverse softplus
        raw_xi_N = np.log(np.exp(xi_N) - 1.0)
        # If we got here without error, the activations are consistent.
        activations_ok = True
    except Exception as e:
        violations.append(f"PINN activation consistency check failed: {e}")
        activations_ok = False

    result = {
        "Phi_N_ok": Phi_N_ok,
        "xi_Delta_ok": xi_Delta_ok,
        "xi_N_ok": xi_N_ok,
        "psi_ok": psi_ok,
        "chi_ok": chi_ok,
        "ESI_ok": ESI_ok,
        "J_ok": J_ok,
        "activations_ok": activations_ok,
        "violations": violations,
        "passed": len(violations) == 0
    }
    return result


# ----------------------------------------------------------------------
# Example usage (mock data that should pass)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock sensible values
    Phi_N      = 0.82
    Phi_Delta  = 0.48
    xi_N       = 0.6
    xi_Delta   = 1.3
    phi_n      = 1.05          # m_eff/m >0
    Phi_N0     = 0.90          # baseline connectivity
    ESI_k      = 2.1
    S_h        = 0.35
    P_meas     = 0.97
    P_target   = 1.0
    alpha, beta, gamma, lam = 0.1, 0.2, 0.15, 0.5   # all non‑negative

    res = validate_edip_omega_state(
        Phi_N, Phi_Delta, xi_N, xi_Delta,
        phi_n, Phi_N0, ESI_k, S_h,
        P_meas, P_target,
        alpha, beta, gamma, lam
    )

    print("Validation Result:")
    for k, v in res.items():
        if k != "violations":
            print(f"  {k}: {v}")
    print("  Violations:", res["violations"])
    print("\nOverall PASSED:", res["passed"])