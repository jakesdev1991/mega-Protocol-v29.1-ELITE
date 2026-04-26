# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
----------------------------------
Checks that the core invariants prescribed by the Omega Physics Rubric
and the MPC‑Ω constraints hold for a given set of system variables.

Invariants (from the Rubric & MPC‑Ω section):
    • Φ_N ∈ [0, 1]                     (connectedness)
    • Φ_Δ ≥ 0                          (asymmetry – non‑negative)
    • ξ_Δ ≥ 1                          (asymmetry stiffness)
    • ψ = ln(Φ_N)                      (dimensionless invariant)
    • MPC‑Ω hard constraints:
          ESI_k ≤ 2.5
          Φ_N ≥ 0.75
          Φ_Δ ≤ 0.6
          ξ_Δ ≤ 3.0
"""

from __future__ import annotations
import numpy as np

def validate_omega_state(
    Phi_N: float,
    Phi_Delta: float,
    xi_Delta: float,
    ESI: float,
    *,
    psi: float | None = None,
    tol: float = 1e-12,
) -> None:
    """
    Raise AssertionError if any Omega invariant or MPC constraint is violated.

    Parameters
    ----------
    Phi_N : float
        Connectedness invariant.
    Phi_Delta : float
        Asymmetry invariant (must be non‑negative per rubric).
    xi_Delta : float
        Asymmetry stiffness invariant (must be ≥ 1).
    ESI : float
        Exposure Stress Index for the facility under consideration.
    psi : float | None, optional
        If supplied, checked against ln(Phi_N). If None, the check is skipped.
    tol : float, optional
        Numerical tolerance for floating‑point comparisons.
    """
    # ---- Rubric invariants -------------------------------------------------
    assert 0.0 - tol <= Phi_N <= 1.0 + tol, \
        f"Phi_N out of bounds [0,1]: got {Phi_N}"
    assert Phi_Delta >= -tol, \
        f"Phi_Delta must be non‑negative: got {Phi_Delta}"
    assert xi_Delta >= 1.0 - tol, \
        f"xi_Delta must be ≥ 1: got {xi_Delta}"
    if psi is not None:
        expected_psi = np.log(max(Phi_N, tol))  # guard against log(0)
        assert abs(psi - expected_psi) <= tol, \
            f"Psi inconsistent: expected ln(Phi_N)={expected_psi:.6f}, got {psi:.6f}"

    # ---- MPC‑Ω hard constraints -------------------------------------------
    assert ESI <= 2.5 + tol, \
        f"ESI_k exceeds hard limit 2.5: got {ESI}"
    assert Phi_N >= 0.75 - tol, \
        f"MPC constraint Phi_N ≥ 0.75 violated: got {Phi_N}"
    assert Phi_Delta <= 0.6 + tol, \
        f"MPC constraint Phi_Δ ≤ 0.6 violated: got {Phi_Delta}"
    assert xi_Delta <= 3.0 + tol, \
        f"MPC constraint xi_Δ ≤ 3.0 violated: got {xi_Delta}"

    # If we reach here, all checks passed
    return True


# -------------------------------------------------------------------------
# Example usage (replace with actual outputs from your pipeline)
if __name__ == "__main__":
    # Dummy values that should pass
    test_state = {
        "Phi_N": 0.82,
        "Phi_Delta": 0.42,
        "xi_Delta": 1.7,
        "ESI": 1.9,
        "psi": np.log(0.82),   # consistent psi
    }

    try:
        validate_omega_state(**test_state)
        print("✅ All Omega invariants and MPC constraints satisfied.")
    except AssertionError as e:
        print("❌ Invariant violation:", e)

    # Example of a deliberate failure
    bad_state = test_state.copy()
    bad_state["Phi_N"] = 0.70  # violates MPC constraint
    try:
        validate_omega_state(**bad_state)
    except AssertionError as e:
        print("❌ Expected failure:", e)