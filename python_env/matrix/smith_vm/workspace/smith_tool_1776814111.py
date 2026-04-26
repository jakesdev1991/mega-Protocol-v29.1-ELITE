# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Epistemic Layer Validator
---------------------------------------
Validates:
  1. psi_epist = ln(Phi_N_epist / Phi_N0)
  2. Shannon entropy S_epist from info_flow matrix
  3. MPC-Omega constraints:
        EASI <= 0.7
        Phi_N_epist >= 0.4
        S_epist >= ln(3)
  4. Instantaneous cost (non-negative)
"""

import numpy as np
from typing import Tuple

# ------------------- Configuration -------------------
PHI_N0 = 1.0                     # reference epistemic Phi_N
MU = (1.0, 1.0, 1.0)             # cost weights (mu1, mu2, mu3)
EPS = 1e-12                      # numerical tolerance
# ----------------------------------------------------

def shannon_entropy(info_flow: np.ndarray) -> float:
    """
    Compute Shannon entropy S = - sum_ij p_ij log(p_ij)
    info_flow: 2D array of non-negative information flows.
    """
    if info_flow.ndim != 2:
        raise ValueError("info_flow must be a 2D matrix")
    total = info_flow.sum()
    if total <= 0:
        raise ValueError("Total information flow must be positive")
    p = info_flow / total
    # Avoid log(0) by masking zeros
    p_flat = p.flatten()
    p_nonzero = p_flat[p_flat > 0]
    return -np.sum(p_nonzero * np.log(p_nonzero))

def validate_epistemic_state(
    Phi_N_epist: float,
    Phi_Delta_epist: float,
    EASI: float,
    info_flow: np.ndarray,
    t: float = 0.0
) -> Tuple[float, float, float, float]:
    """
    Returns (psi_epist, S_epist, constraint_violation, instantaneous_cost)
    Raises ValueError if any invariant or constraint is broken.
    """
    # 1. Invariant: psi_epist = ln(Phi_N_epist / Phi_N0)
    if Phi_N_epist <= 0:
        raise ValueError(f"Phi_N_epist must be > 0 (got {Phi_N_epist})")
    psi_epist = np.log(Phi_N_epist / PHI_N0)

    # 2. Entropy gauge
    S_epist = shannon_entropy(info_flow)

    # 3. MPC-Omega constraints
    constraint_violation = 0.0
    if EASI > 0.7 + EPS:
        constraint_violation += (EASI - 0.7) ** 2
    if Phi_N_epist < 0.4 - EPS:
        constraint_violation += (0.4 - Phi_N_epist) ** 2
    if S_epist < np.log(3) - EPS:
        constraint_violation += (np.log(3) - S_epist) ** 2

    # 4. Instantaneous cost (integrand of J)
    inst_cost = (
        max(EASI - 0.7, 0.0) ** 2 +
        MU[0] * max(0.4 - Phi_N_epist, 0.0) ** 2 +
        MU[1] * (Phi_Delta_epist ** 2) +
        MU[2] * max(np.log(3) - S_epist, 0.0) ** 2
    )

    # If any constraint violated, raise
    if constraint_violation > EPS:
        raise ValueError(
            f"Constraint violation at t={t}: "
            f"EASI={EASI:.4f} (max 0.7), "
            f"Phi_N_epist={Phi_N_epist:.4f} (min 0.4), "
            f"S_epist={S_epist:.4f} (min ln3≈{np.log(3):.4f})"
        )

    return psi_epist, S_est, constraint_violation, inst_cost

# ------------------- Example Usage -------------------
if __name__ == "__main__":
    # Example state at a given time
    Phi_N_epist_example = 0.5
    Phi_Delta_epist_example = 0.2
    EASI_example = 0.6
    # Simple 2-agent info flow matrix (rows: src, cols: dst)
    info_flow_example = np.array([[10.0, 2.0],
                                  [1.0,  8.0]])

    try:
        psi, S, viol, cost = validate_epistemic_state(
            Phi_N_epist_example,
            Phi_Delta_epist_example,
            EASI_example,
            info_flow_example,
            t=1.0
        )
        print(f"[OK] t=1.0: psi_epist={psi:.4f}, S_epist={S:.4f}, cost={cost:.6f}")
    except ValueError as e:
        print(f"[VIOLATION] {e}")
# ----------------------------------------------------