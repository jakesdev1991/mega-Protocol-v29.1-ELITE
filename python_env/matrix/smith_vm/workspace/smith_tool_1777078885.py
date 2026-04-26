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
Validates the Φ‑density bookkeeping and ethical constraints
described in the meta‑scrutiny reflection.

Invariants checked:
1. Φ_N ≥ 0   (Net Φ density never negative)
2. Φ_Δ = Φ_N(new) - Φ_N(old)   (Exact accounting)
3. For any action deemed unethical/excluded,
   the simulated Φ_Δ must be ≤ 0 (no net gain under ethical model).

The script is deliberately minimal; replace the `ethical_impact`
function with a real model if needed.
"""

from dataclasses import dataclass
from typing import List, Tuple

# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass
class Action:
    label: str
    phi_delta_claimed: float   # Φ_Δ as reported by the agent
    phi_n_before: float        # Φ_N prior to action
    phi_n_after: float         # Φ_N after action (claimed)
    ethical: bool              # True if action complies with Omega Protocol ethics

# ----------------------------------------------------------------------
# Helper: ethical impact model (stub)
# ----------------------------------------------------------------------
def ethical_impact(action: Action) -> float:
    """
    Stub model that returns the *ethical* Φ_Δ for an action.
    For compliant actions we trust the claimed value.
    For non‑compliant actions we apply a penalty that ensures
    non‑positive Φ_Δ (representing reputational/entropy cost).
    """
    if action.ethical:
        return action.phi_delta_claimed
    # Simple penalty: assume any unethical action incurs at least
    # the same magnitude of loss as the claimed gain, plus a base cost.
    # This guarantees Φ_Δ ≤ 0 for unethical actions.
    return -abs(action.phi_delta_claimed) - 0.5  # -0.5 is an arbitrary base entropy cost

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_omega_invariants(actions: List[Action]) -> Tuple[bool, List[str]]:
    """
    Returns (is_valid, list_of_violations).
    """
    violations = []
    prev_phi_n = None

    for i, act in enumerate(actions, start=1):
        # 1. Φ_N non‑negative
        if act.phi_n_before < 0 or act.phi_n_after < 0:
            violations.append(
                f"Action {i} ('{act.label}'): Φ_N negative "
                f"(before={act.phi_n_before}, after={act.phi_n_after})"
            )
        # 2. Exact accounting
        expected_delta = act.phi_n_after - act.phi_n_before
        if not _close_enough(act.phi_delta_claimed, expected_delta):
            violations.append(
                f"Action {i} ('{act.label}'): Φ_Δ mismatch "
                f"(claimed={act.phi_delta_claimed:.5f}, "
                f"computed={expected_delta:.5f})"
            )
        # 3. Ethical constraint: simulated ethical Φ_Δ must be ≤ 0 for non‑ethical actions
        simulated_delta = ethical_impact(act)
        if not act.ethical and simulated_delta > 0:
            violations.append(
                f"Action {i} ('{act.label}'): Unethical action yields positive ethical Φ_Δ "
                f"({simulated_delta:.5f})"
            )
        # Update for next iteration consistency check
        if prev_phi_n is not None and not _close_enough(act.phi_n_before, prev_phi_n):
            violations.append(
                f"Action {i} ('{act.label}'): Φ_N discontinuity "
                f"(previous after={prev_phi_n:.5f}, current before={act.phi_n_before:.5f})"
            )
        prev_phi_n = act.phi_n_after

    return len(violations) == 0, violations

def _close_enough(a: float, b: float, eps: float = 1e-9) -> bool:
    return abs(a - b) <= eps

# ----------------------------------------------------------------------
# Example: actions extracted from the meta‑scrutiny reflection
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Action 1: The meta‑scrutiny itself (ethical, positive Φ_Δ)
    meta_scrutiny = Action(
        label="Meta‑Scrutiny (Φ density +0.05)",
        phi_delta_claimed=+0.05,
        phi_n_before=49.06,
        phi_n_after=49.11,
        ethical=True,
    )

    # Action 2: Including the config.php vector (deemed unethical)
    config_php_inclusion = Action(
        label="Include config.php vector (short‑term +0.2, long‑term –1.5)",
        phi_delta_claimed=+0.2,   # only the short‑term gain claimed by the agent
        phi_n_before=49.06,       # assuming we evaluate from same baseline
        phi_n_after=49.06 + 0.2,  # naive before penalty
        ethical=False,            # excluded by the Engine → treated as unethical
    )

    # Action 3: Excluding the config.php vector (ethical, net positive over time)
    config_php_exclusion = Action(
        label="Exclude config.php vector (ethical, net +0.8+ over time)",
        phi_delta_claimed=+0.8,   # conservative estimate of long‑term gain
        phi_n_before=49.06,
        phi_n_after=49.06 + 0.8,
        ethical=True,
    )

    actions = [meta_scrutiny, config_php_inclusion, config_php_exclusion]

    valid, errs = validate_omega_invariants(actions)

    print("=== Omega Protocol Invariant Validation ===")
    if valid:
        print("✅ All invariants satisfied.")
    else:
        print("❌ Violations detected:")
        for v in errs:
            print(" -", v)