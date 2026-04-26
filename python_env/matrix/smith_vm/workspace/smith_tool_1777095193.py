# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for the Bureaucratic Impedance derivation.
Checks dimensionality, invariant compliance, and stability conditions.
"""

import numpy as np
from typing import Tuple

# ----------------------------------------------------------------------
# Tolerances & constants (set by the Omega Protocol)
# ----------------------------------------------------------------------
EPS_DET = 1e-6          # minimum allowed determinant of g_decision
PHI_DELTA_MAX = 0.05    # max permissible |Δψ| per step (example value)
# ----------------------------------------------------------------------


def _assert_dimensionless(val: float, name: str) -> None:
    """Omega Protocol requires all scalar arguments to be dimensionless [1]."""
    if not isinstance(val, (int, float, np.floating, np.integer)):
        raise TypeError(f"{name} must be a real number (dimensionless). Got {type(val)}")
    # In this VM we cannot inspect units, so we trust the caller.


def validate_identity(psi: float, phi_N: float, phi_delta: float, psi_prev: float = None) -> None:
    """
    Enforce:
        ψ = exp(-Φ_N)   → 0 < ψ ≤ 1
        |ψ - ψ_prev| ≤ Φ_Delta   (if psi_prev supplied)
    """
    _assert_dimensionless(psi, "psi")
    _assert_dimensionless(phi_N, "Phi_N")
    _assert_dimensionless(phi_delta, "Phi_Delta")

    # ψ must be exp(-Φ_N) → automatically in (0,1] if Φ_N ≥ 0
    if phi_N < 0:
        raise ValueError(f"Phi_N must be non‑negative (got {phi_N}) to keep ψ = exp(-Φ_N) in (0,1].")
    psi_theoretical = np.exp(-phi_N)
    if not np.isclose(psi, psi_theoretical, rtol=1e-12, atol=1e-12):
        raise ValueError(
            f"Psi inconsistency: supplied ψ={psi} does not equal exp(-Phi_N)={psi_theoretical}."
        )
    if psi_prev is not None:
        delta_psi = abs(psi - psi_prev)
        if delta_psi > phi_delta + 1e-12:
            raise ValueError(
                f"Identity change |Δψ|={delta_psi} exceeds Φ_Delta={phi_delta}."
            )


def validate_metric_determinant(
    xi_rule: float,
    xi_req: float,
    Lambda: float,
    Gamma: float,
    H_proc: float,
) -> float:
    """
    Compute an effective determinant proxy:
        g_eff = exp(-Lambda * H_proc) * exp(-Gamma * |xi_rule - xi_req|)
    The protocol demands g_eff ≥ EPS_DET.
    Returns the determinant proxy for possible downstream use.
    """
    _assert_dimensionless(xi_rule, "Xi_rule")
    _assert_dimensionless(xi_req, "Xi_req")
    _assert_dimensionless(Lambda, "Lambda")
    _assert_dimensionless(Gamma, "Gamma")
    _assert_dimensionless(H_proc, "H_proc")

    if Lambda <= 0:
        raise ValueError(f"Lambda must be > 0 (got {Lambda}) to provide entropy damping.")
    if Gamma <= 0:
        raise ValueError(f"Gamma must be > 0 (got {Gamma}) to provide stiffness‑mismatch damping.")
    if H_proc < 0:
        raise ValueError(f"Informational heat H_proc must be non‑negative (got {H_proc}).")

    det_proxy = np.exp(-Lambda * H_proc) * np.exp(-Gamma * abs(xi_rule - xi_req))
    if det_proxy < EPS_DET:
        raise ValueError(
            f"Effective determinant proxy {det_proxy:.3e} fell below EPS_DET={EPS_DET}. "
            f"Bureaucratic stiffness/entropy too high → metric degeneracy."
        )
    return det_proxy


def validate_COD(
    fidelity: float,
    Lambda: float,
    Gamma: float,
    H_proc: float,
    xi_rule: float,
    xi_req: float,
) -> float:
    """
    Compute COD_buro = fidelity * exp(-Lambda*H_proc) * exp(-Gamma*|xi_rule - xi_req|)
    Enforce 0 ≤ COD ≤ 1.
    """
    _assert_dimensionless(fidelity, "fidelity |<Ψ_intent|Ψ_exec>|^2")
    if not (0.0 <= fidelity <= 1.0 + 1e-12):
        raise ValueError(f"Fidelity must be in [0,1] (got {fidelity}).")
    # Re‑use the damping factor from validate_metric_determinant (but without raising)
    det_factor = np.exp(-Lambda * H_proc) * np.exp(-Gamma * abs(xi_rule - xi_req))
    COD = fidelity * det_factor
    if not (0.0 <= COD <= 1.0 + 1e-12):
        raise ValueError(
            f"COD_buro={COD:.6f} out of bounds [0,1] after damping. "
            f"Check fidelity ({fidelity}) and damping factors."
        )
    return COD


# ----------------------------------------------------------------------
# Example usage (illustrative only; replace with actual telemetry)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Sample telemetry from an agent
    Phi_N = 0.2                     # → ψ = exp(-0.2) ≈ 0.819
    psi = np.exp(-Phi_N)
    psi_prev = 0.80                 # previous step identity
    Phi_Delta = 0.05

    Xi_rule = 1.3
    Xi_req = 1.0
    Lambda = 0.4
    Gamma = 0.6
    H_proc = 0.25                   # normalized entropy of approval chain
    fidelity = 0.92                 # |<Ψ_intent|Ψ_exec>|^2

    try:
        validate_identity(psi, Phi_N, Phi_Delta, psi_prev)
        det = validate_metric_determinant(
            Xi_rule, Xi_req, Lambda, Gamma, H_proc
        )
        COD = validate_COD(
            fidelity, Lambda, Gamma, H_proc, Xi_rule, Xi_req
        )
        print(
            f"[PASS] ψ={psi:.4f}, det(g)_proxy={det:.6e}, COD_buro={COD:.4f}"
        )
    except Exception as e:
        print(f"[FAIL] Omega Protocol violation: {e}")
        raise  # re‑raise to halt the agent if running in the VM