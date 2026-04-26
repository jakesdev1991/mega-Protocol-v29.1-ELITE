# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator for the Quantum Logistical Manifold Governor (QLMG) proposal.

This script checks the three absolute invariants (Φ‑1, Φ‑2, Φ‑3) that any submission must
never violate.  It also performs a basic sanity‑check on the claimed Φ‑density
value and on the metric‑non‑degeneracy condition that the proposal ties to TOE Step 4.

The validator is deliberately minimal – it expects the proposer to supply the
numerical data that the invariants depend on.  If any invariant fails, the
function returns False and a diagnostic message.

Usage:
    from omega_validator import validate_qlmg
    ok, msg = validate_qlmg(
        route_adjustments=[(d1, dt1), (d2, dt2), ...],   # list of (distance [m], time [s])
        entropy_data={                                   # for Φ‑2
            'S_initial': float,                          # initial Shannon entropy (bits)
            'S_final':   float,                          # entropy after stabilization
            'S_env':     float                           # entropy exchanged with environment (bits)
        },
        lattice_betti=(b0, b1, b2, b3),                  # Betti numbers of the fleet lattice
        metric_tensor=function returning a 4x4 numpy array g'   # post‑stabilization metric
    )
    if not ok:
        raise ValueError(f"Omega Protocol violation: {msg}")
"""

import numpy as np
from typing import List, Tuple, Callable

# ----------------------------------------------------------------------
# Physical constants (SI)
C_LIGHT = 299_792_458  # m/s
# ----------------------------------------------------------------------


def _check_causal_fidelity(route_adjustments: List[Tuple[float, float]]) -> Tuple[bool, str]:
    """
    Φ‑1: No route adjustment shall propagate faster than local causal influence (c).
    For each adjustment we require Δt ≥ d / c.
    """
    for i, (d, dt) in enumerate(route_adjustments):
        if d < 0 or dt < 0:
            return False, f"Adjustment {i}: negative distance or time (d={d}, dt={dt})"
        min_dt = d / C_LIGHT
        if dt < min_dt - 1e-12:  # tiny tolerance for FP error
            return False, (
                f"Adjustment {i}: superluminal propagation. "
                f"d={d:.3f} m requires dt≥{min_dt:.3e} s, got dt={dt:.3e} s."
            )
    return True, "Causal fidelity satisfied."


def _check_entropy_conservation(entropy_data: dict) -> Tuple[bool, str]:
    """
    Φ‑2: Total entropy ≤ initial + 2.1%.
    We compute ΔS = S_final - S_initial + S_env and require ΔS ≤ 0.021 * S_initial.
    """
    try:
        S0 = float(entropy_data["S_initial"])
        Sf = float(entropy_data["S_final"])
        Senv = float(entropy_data.get("S_env", 0.0))
    except KeyError as e:
        return False, f"Missing entropy field: {e}"
    except (TypeError, ValueError):
        return False, "Entropy fields must be numeric."

    if S0 < 0:
        return False, f"Initial entropy cannot be negative (S0={S0})."

    delta_S = Sf - S0 + Senv
    max_allowed = 0.021 * S0
    if delta_S > max_allowed + 1e-12:
        return False, (
            f"Entropy bound violated: ΔS={delta_S:.6f} bits > 0.021·S0={max_allowed:.6f} bits. "
            f"(S0={S0}, Sf={Sf}, S_env={Senv})"
        )
    return True, f"Entropy conservation satisfied (ΔS={delta_S:.6f} bits ≤ {max_allowed:.6f} bits)."


def _check_topological_integrity(lattice_betti: Tuple[int, int, int, int]) -> Tuple[bool, str]:
    """
    Φ‑3: Fleet lattice must be homotopy‑equivalent to a 3‑torus.
    For a 3‑torus T³ the Betti numbers are (b0, b1, b2, b3) = (1, 3, 3, 1).
    """
    b0, b1, b2, b3 = lattice_betti
    expected = (1, 3, 3, 1)
    if (b0, b1, b2, b3) != expected:
        return False, (
            f"Topological integrity failed: lattice Betti numbers { (b0,b1,b2,b3) } "
            f"do not match the 3‑torus expectation {expected}."
        )
    return True, "Topological integrity satisfied (Betti numbers match T³)."


def _check_metric_non_degeneracy(metric_fn: Callable[[], np.ndarray]) -> Tuple[bool, str]:
    """
    TOE Step 4 link: after stabilization the metric must be non‑degenerate,
    i.e. det(g') ≠ 0.  We check that the absolute determinant is above a
    tiny threshold to avoid FP‑zero false positives.
    """
    try:
        g_prime = metric_fn()
        if not isinstance(g_prime, np.ndarray) or g_prime.shape != (4, 4):
            return False, "Metric function must return a 4×4 numpy array."
        det = np.linalg.det(g_prime)
        if np.abs(det) < 1e-15:
            return False, f"Metric near‑degenerate: det(g') = {det:.3e}."
        return True, f"Metric non‑degenerate (det = {det:.6e})."
    except Exception as e:
        return False, f"Error evaluating metric: {e}"


def _check_phi_density_claim(phi_density: float) -> Tuple[bool, str]:
    """
    The proposal states Φ‑density = 0.89 (a dimensionless informational integrity
    unit).  In the Omega Protocol Φ is *not* a bounded probability‑like density;
    it is an additive unit of informational integrity.  Nevertheless, the
    submitted value must be a real number; we simply check that it is numeric
    and non‑negative (negative Φ would indicate informational debt).
    """
    if not isinstance(phi_density, (int, float)):
        return False, "Φ‑density claim must be numeric."
    if phi_density < 0:
        return False, f"Φ‑density cannot be negative (got {phi_density})."
    return True, f"Φ‑density claim ({phi_density}) is a valid real number."


def validate_qlmg(
    route_adjustments: List[Tuple[float, float]],
    entropy_data: dict,
    lattice_betti: Tuple[int, int, int, int],
    metric_fn: Callable[[], np.ndarray],
    phi_density: float = 0.89,
) -> Tuple[bool, str]:
    """
    Master validator.  Returns (True, "All checks passed") if every invariant
    and basic sanity check holds; otherwise (False, <reason>).
    """
    checks = [
        ("Causal fidelity (Φ‑1)", _check_causal_fidelity(route_adjustments)),
        ("Entropy conservation (Φ‑2)", _check_entropy_conservation(entropy_data)),
        ("Topological integrity (Φ‑3)", _check_topological_integrity(lattice_betti)),
        ("Metric non‑degeneracy (TOE Step 4)", _check_metric_non_degeneracy(metric_fn)),
        ("Φ‑density claim sanity", _check_phi_density_claim(phi_density)),
    ]

    for name, (ok, msg) in checks:
        if not ok:
            return False, f"{name} failed: {msg}"
    return True, "All Omega Protocol invariants and sanity checks satisfied."


# ----------------------------------------------------------------------
# Example usage (commented out – replace with real data from the proposal)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Dummy data that *should* pass the checks:
    #   - Two route adjustments well within light‑speed limits.
    #   - Entropy change within 2.1%.
    #   - Lattice Betti numbers of a 3‑torus.
    #   - A random positive‑definite metric (non‑degenerate).
    #   - Φ‑density = 0.89.

    dummy_adjustments = [
        (100.0, 1.0e-6),   # 100 m in 1 µs -> required dt ≥ 3.34e-7 s, we give 1e-6 s
        (500.0, 2.0e-6),   # 500 m in 2 µs -> required dt ≥ 1.67e-6 s, we give 2e-6 s
    ]

    dummy_entropy = {
        "S_initial": 1000.0,   # bits
        "S_final":   1010.0,   # bits (increase of 10 bits)
        "S_env":     -5.0,     # environment absorbed 5 bits
        # ΔS = 1010 - 1000 -5 = 5 bits; 0.021*S0 = 21 bits → OK
    }

    dummy_betti = (1, 3, 3, 1)

    def dummy_metric():
        # Create a simple diagonal metric with positive entries → det > 0
        return np.diag([1.0, 1.0, 1.0, 1.0])

    ok, msg = validate_qlmg(
        route_adjustments=dummy_adjustments,
        entropy_data=dummy_entropy,
        lattice_betti=dummy_betti,
        metric_fn=dummy_metric,
        phi_density=0.89,
    )
    print(f"Validation result: {ok}\nMessage: {msg}")