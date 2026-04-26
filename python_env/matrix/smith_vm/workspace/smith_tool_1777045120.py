# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for C‑SAGN (Chrono‑Synchronized Artillery Governance Nexus)

Usage:
    Provide the measured quantities as arguments to the validation functions.
    The module returns a dict with pass/fail status and explanatory messages.

Author:  (generated for the purpose of this audit)
"""

import math
from typing import Dict, Tuple, List

# ----------------------------------------------------------------------
# Constants (Ω‑Protocol canonical values)
C = 299_792_458  # speed of light in m/s
ENTROPY_TOLERANCE = 0.018  # 1.8 % increase allowed


def check_causal_fidelity(
    max_signal_speed: float,
    max_distance: float,
    measured_latency: float,
) -> Tuple[bool, str]:
    """
    Φ‑1: No firing adjustment shall propagate faster than local causal influence (c).

    Parameters
    ----------
    max_signal_speed : float
        The highest speed at which any control signal is known to travel (m/s).
        Should be ≤ C for a physical implementation.
    max_distance : float
        Greatest separation between any two nodes that must stay causally linked (m).
    measured_latency : float
        Observed worst‑case one‑way delay for a control adjustment (s).

    Returns
    -------
    (bool, str)
        True if invariant satisfied, else False with reason.
    """
    if max_signal_speed > C + 1e-9:  # tiny numerical tolerance
        return False, f"Signal speed {max_signal_speed:.3e} m/s exceeds c ({C:.3e} m/s)."
    min_allowed_latency = max_distance / C
    if measured_latency < min_allowed_latency - 1e-9:
        return False, (
            f"Latency {measured_latency:.6f}s < d/c ({min_allowed_latency:.6f}s) "
            f"for distance {max_distance:.1f}m → superluminal adjustment possible."
        )
    return True, "Causal fidelity satisfied."


def check_entropy_conservation(
    initial_entropy: float,
    final_entropy: float,
) -> Tuple[bool, str]:
    """
    Φ‑2: Total entropy ≤ initial + 1.8 %.

    Parameters
    ----------
    initial_entropy : float
        Entropy (Shannon or von‑Neumann) of the informational state before salvo.
    final_entropy : float
        Entropy after salvo (including any abort‑protocol overhead).

    Returns
    -------
    (bool, str)
        True if invariant satisfied, else False with reason.
    """
    allowed = initial_entropy * (1.0 + ENTROPY_TOLERANCE)
    if final_entropy > allowed + 1e-12:
        return False, (
            f"Final entropy {final_entropy:.6f} > allowed {allowed:.6f} "
            f"(initial {initial_entropy:.6f} + 1.8 %)."
        )
    return True, "Entropy conservation satisfied."


def check_topological_integrity(
    betti_numbers: List[int],
) -> Tuple[bool, str]:
    """
    Φ‑3: Artillery mesh homotopy‑equivalent to 3‑sphere (S³).

    For a simplicial or cell complex representing the swarm,
    the Betti numbers must match those of S³:
        β₀ = 1  (one connected component)
        β₁ = 0  (no 1‑dimensional holes)
        β₂ = 0  (no 2‑dimensional voids)
        β₃ = 1  (one 3‑dimensional void)

    Parameters
    ----------
    betti_numbers : list of int
        [β₀, β₁, β₂, β₃, …] – we only inspect the first four entries.

    Returns
    -------
    (bool, str)
        True if invariant satisfied, else False with reason.
    """
    if len(betti_numbers) < 4:
        return False, "Insufficient Betti numbers supplied (need at least β₀‑β₃)."
    expected = [1, 0, 0, 1]
    mismatches = [
        i
        for i, (got, exp) in enumerate(zip(betti_numbers[:4], expected))
        if got != exp
    ]
    if mismatches:
        names = ["β₀", "β₁", "β₂", "β₃"]
        bad = ", ".join(f"{names[i]}={betti_numbers[i]}" for i in mismatches)
        return False, f"Topological invariant failed: {bad} (expected {expected})."
    return True, "Topological integrity satisfied (mesh ≃ S³)."


def check_phi_budget_consistency(
    baseline_phi: float,
    claimed_gain: float,
    gain_breakdown: Dict[str, float],
) -> Tuple[bool, str]:
    """
    Verify that the claimed Φ‑density gain matches the sum of its parts
    and that the resulting Φ‑density stays within a sensible range.
    The Ω‑Protocol does not prescribe an absolute upper bound, but
    Φ‑density is interpreted as a *normalized* informational integrity
    score, so we enforce 0 ≤ Φ ≤ 1 for safety. (If the protocol treats
    Φ as an additive unit, adjust the bound accordingly.)

    Parameters
    ----------
    baseline_phi : float
        Reported baseline Φ‑density (should be in [0,1]).
    claimed_gain : float
        Total Φ gain asserted by the proposal.
    gain_breakdown : dict
        Mapping from subsystem label to its claimed Φ contribution.
        The sum of values should equal `claimed_gain` (within tolerance).

    Returns
    -------
    (bool, str)
        True if budget consistent, else False with reason.
    """
    # 1. Baseline sanity
    if not (0.0 - 1e-12 <= baseline_phi <= 1.0 + 1e-12):
        return False, f"Baseline Φ‑density {baseline_phi} outside [0,1]."

    # 2. Gain breakdown consistency
    total_from_breakdown = sum(gain_breakdown.values())
    if not math.isclose(total_from_breakdown, claimed_gain, rel_tol=1e-9, abs_tol=1e-9):
        return False, (
            f"Sum of breakdown {total_from_breakdown:.6f} ≠ claimed gain {claimed_gain:.6f}."
        )

    # 3. Final Φ‑density range
    final_phi = baseline_phi + claimed_gain
    if not (0.0 - 1e-12 <= final_phi <= 1.0 + 1e-12):
        return False, (
            f"Resulting Φ‑density {final_phi:.6f} would exceed [0,1] "
            f"(baseline {baseline_phi} + gain {claimed_gain})."
        )
    return True, "Φ‑budget consistent and within bounds."


def run_full_validation(
    # ----- causal fidelity inputs -----
    max_signal_speed: float,
    max_distance: float,
    measured_latency: float,
    # ----- entropy inputs -----
    initial_entropy: float,
    final_entropy: float,
    # ----- topological inputs -----
    betti_numbers: List[int],
    # ----- Φ‑budget inputs -----
    baseline_phi: float,
    claimed_gain: float,
    gain_breakdown: Dict[str, float],
) -> Dict[str, Tuple[bool, str]]:
    """
    Executes all invariant checks and returns a report.
    """
    results = {}

    results["causal_fidelity"] = check_causal_fidelity(
        max_signal_speed, max_distance, measured_latency
    )
    results["entropy_conservation"] = check_entropy_conservation(
        initial_entropy, final_entropy
    )
    results["topological_integrity"] = check_topological_integrity(betti_numbers)
    results["phi_budget"] = check_phi_budget_consistency(
        baseline_phi, claimed_gain, gain_breakdown
    )

    return results


# ----------------------------------------------------------------------
# Example usage (with placeholder data that would *fail* the audit):
if __name__ == "__main__":
    # Placeholder measurements – replace with real sensor/simulation data.
    example_report = run_full_validation(
        max_signal_speed=3.0e8,  # slightly above c → will fail Φ‑1
        max_distance=5000.0,
        measured_latency=0.01,
        initial_entropy=1.0,
        final_entropy=1.025,  # 2.5 % increase → will fail Φ‑2
        betti_numbers=[1, 0, 0, 1],  # passes Φ‑3
        baseline_phi=0.92,
        claimed_gain=5.2,
        gain_breakdown={
            "Causal Trajectory Prediction": 1.5,
            "Relativistic Swarm Coherence": 2.0,
            "TOE Compliance": 1.5,
            "Invariant Adherence": 0.2,
        },
    )

    print("Ω‑Protocol Validation Report:")
    for name, (ok, msg) in example_report.items():
        status = "PASS" if ok else "FAIL"
        print(f"{name:25}: {status} – {msg}")

    # Overall pass only if every check passed
    overall = all(ok for ok, _ in example_report.values())
    print("\nOverall:", "PASS" if overall else "FAIL")