# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Invariant Validator for CDST-Ω

Checks three core invariants:
    1. Phi_N  <= Phi_N_max          (parameter norm budget)
    2. |Phi_N_k+1 - Phi_N_k| <= Phi_Delta_max   (drift bound)
    3. J_val  <= J_star_thr         (prediction error threshold)

The script is deliberately minimal – it expects the user to supply:
    - params:   numpy array of model parameters after training
    - prev_phi_n: Phi_N from the previous checkpoint (or None for first run)
    - val_mse:  validation mean‑squared error (or any loss proxy for J*)
    - thresholds: dict with the limits defined by the Omega Protocol.

If any invariant fails, a RuntimeError is raised – the calling pipeline
should abort or trigger a remedial action (e.g., regularisation, rollback).
"""

from __future__ import annotations
import numpy as np
from typing import Optional, Dict

def compute_phi_n(params: np.ndarray) -> float:
    """
    Phi_N is defined as the L2 norm of the parameter vector.
    (Alternative definitions – e.g., Frobenius for layered weights –
     can be swapped in here without changing the validator logic.)
    """
    return float(np.linalg.norm(params, ord=2))

def validate_cdst_omega(
    params: np.ndarray,
    prev_phi_n: Optional[float],
    val_mse: float,
    thresholds: Dict[str, float],
) -> None:
    """
    Raises RuntimeError if any Omega invariant is violated.

    Parameters
    ----------
    params : np.ndarray
        Current model parameters (flattened).
    prev_phi_n : float | None
        Phi_N from the previous training checkpoint.
    val_mse : float
        Validation loss serving as proxy for J* (prediction error).
    thresholds : dict
        Must contain:
            'phi_n_max'   : upper bound for Phi_N
            'phi_delta_max': maximum allowed absolute drift in Phi_N
            'j_star_thr'  : maximum allowed validation loss
    """
    # ---- 1. Phi_N -------------------------------------------------
    phi_n = compute_phi_n(params)
    phi_n_max = thresholds.get("phi_n_max")
    if phi_n_max is None:
        raise ValueError("Threshold 'phi_n_max' missing.")
    if phi_n > phi_n_max:
        raise RuntimeError(
            f"Phi_N invariant violated: {phi_n:.4f} > {phi_n_max:.4f}"
        )

    # ---- 2. Phi_Delta ---------------------------------------------
    if prev_phi_n is not None:
        phi_delta = abs(phi_n - prev_phi_n)
        phi_delta_max = thresholds.get("phi_delta_max")
        if phi_delta_max is None:
            raise ValueError("Threshold 'phi_delta_max' missing.")
        if phi_delta > phi_delta_max:
            raise RuntimeError(
                f"Phi_Delta invariant violated: drift={phi_delta:.4f} > {phi_delta_max:.4f}"
            )

    # ---- 3. J* (prediction error) ---------------------------------
    j_star_thr = thresholds.get("j_star_thr")
    if j_star_thr is None:
        raise ValueError("Threshold 'j_star_thr' missing.")
    if val_mse > j_star_thr:
        raise RuntimeError(
            f"J* invariant violated: validation loss={val_mse:.4f} > {j_star_thr:.4f}"
        )

    # If we reach here, all invariants hold.
    print(
        f"[OK] Phi_N={phi_n:.4f} (<={phi_n_max}), "
        f"Phi_Delta={phi_delta if prev_phi_n is not None else 0:.4f} "
        f"(<={phi_delta_max if prev_phi_n is not None else 'N/A'}), "
        f"J*={val_mse:.4f} (<={j_star_thr})"
    )


# ----------------------------------------------------------------------
# Example usage (replace with actual training pipeline outputs)
if __name__ == "__main__":
    # Dummy parameters – in practice these come from your model
    dummy_params = np.random.randn(128) * 0.1  # small random vector
    prev_phi = None  # first training iteration
    dummy_val_mse = 0.0025  # example validation MSE

    # Example thresholds – these should be supplied by the Omega‑Protocol governance
    THRESHOLDS = {
        "phi_n_max": 5.0,          # maximum allowed L2 norm of parameters
        "phi_delta_max": 0.2,      # max permissible drift per update
        "j_star_thr": 0.01,        # maximum validation loss (J*)
    }

    try:
        validate_cdst_omega(
            params=dummy_params,
            prev_phi_n=prev_phi,
            val_mse=dummy_val_mse,
            thresholds=THRESHOLDS,
        )
    except RuntimeError as inv_err:
        print(f"Invariant violation: {inv_err}")
        # Here you could trigger a rollback, increase regularisation, etc.