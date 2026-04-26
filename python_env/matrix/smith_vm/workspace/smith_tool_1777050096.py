# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Submission Validator
-----------------------------------
Enforces the four‑pillar rubric and the core invariants:
    Φ_N ≥ 0                     (baseline informational density)
    |Φ_Δ| ≤ C_channel          (bounded informational flux)
    J* = Φ_N * Φ_Δ + J0       (conserved Jordan‑invariant, J0 constant)

A missing or empty pillar incurs a *finite* penalty proportional to its weight.
"""

from dataclasses import dataclass
from typing import Dict, Any

# ----------------------------------------------------------------------
# Configuration – adjust to match your domain's calibration
# ----------------------------------------------------------------------
PILLAR_WEIGHTS = {
    "concept":        1.0,   # Informational Advantage definition
    "architecture":   1.2,   # System diagram / software structure
    "physics_link":   0.9,   # TOE step mapping + derivation
    "smith_audit":    1.1,   # Absolute invariants + verification
}
LAMBDA = 0.5                     # Penalty scaling factor (λ in RCOD‑§4.2)
CHANNEL_CAPACITY = 10.0          # Maximum allowable |Φ_Δ| per review cycle
J0 = 2.0                         # Base constant for the Jordan‑invariant

# ----------------------------------------------------------------------
# Exception definition
# ----------------------------------------------------------------------
class OmegaProtocolViolation(RuntimeError):
    """Raised when a submission breaks any Omega Protocol invariant."""
    pass

# ----------------------------------------------------------------------
# Core validation logic
# ----------------------------------------------------------------------
@dataclass
class OmegaState:
    Phi_N: float = 0.0   # baseline informational density (starts at 0)
    Phi_Delta: float = 0.0
    J_star: float = J0   # initialized with the base constant

    def apply_penalty(self, penalty: float) -> None:
        """Apply a negative informational contribution (penalty)."""
        self.Phi_N -= penalty          # baseline drops
        self.Phi_Delta -= penalty      # flux change equals the penalty
        self.J_star = self.Phi_N * self.Phi_Delta + J0
        self._check_invariants()

    def _check_invariants(self) -> None:
        if self.Phi_N < 0:
            raise OmegaProtocolViolation(
                f"Φ_N dropped below zero: {self.Phi_N:.3f} (must be ≥ 0)"
            )
        if abs(self.Phi_Delta) > CHANNEL_CAPACITY:
            raise OmegaProtocolViolation(
                f"|Φ_Δ| exceeds channel capacity: {abs(self.Phi_Delta):.3f} > {CHANNEL_CAPACITY}"
            )
        # J* should stay constant; allow tiny floating‑point drift
        if not abs(self.J_star - J0) < 1e-9:
            raise OmegaProtocolViolation(
                f"Jordan‑invariant J* not conserved: {self.J_star:.6f} ≠ {J0:.6f}"
            )

def validate_submission(submission: Dict[str, Any]) -> OmegaState:
    """
    Returns the post‑validation OmegaState if the submission passes.
    Raises OmegaProtocolViolation on any invariant breach.
    """
    state = OmegaState()
    missing_penalty = 0.0

    for pillar, weight in PILLAR_WEIGHTS.items():
        content = submission.get(pillar, None)
        # Treat None, empty string, empty list/dict as missing
        if content is None or (isinstance(content, (str, list, dict)) and len(content) == 0):
            missing_penalty += LAMBDA * weight
            continue
        # If present, we assume it contributes *positive* informational density.
        # For simplicity we add a unit gain; in a real system you would compute
        # the actual Φ contribution from the content.
        state.Phi_N += weight          # positive contribution
        state.Phi_Delta += weight      # flux increase matches the gain

    # Apply the penalty for any missing/empty pillars
    if missing_penalty > 0:
        state.apply_penalty(missing_penalty)

    # Final invariant check (redundant but explicit)
    state._check_invariants()
    return state

# ----------------------------------------------------------------------
# Example usage – replace the dict with the engine's actual output
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example 1: Empty engine output (the one we audited)
    empty_output = {}   # ← this is what the engine returned
    try:
        final_state = validate_submission(empty_output)
        print("✅ Submission accepted. Final state:", final_state)
    except OmegaProtocolViolation as e:
        print("❌ Omega Protocol violation:", e)

    # Example 2: A minimally compliant submission
    minimal_submission = {
        "concept":        "Informational Advantage = ↑Φ_density via adaptive topology sensing.",
        "architecture":   ["Sensor mesh", "Topology solver", "Feedback actuator"],
        "physics_link":   "Metric Non‑Degeneracy (TOE step 7) guarantees invertible strain‑information map.",
        "smith_audit":    "Invariants: Φ_N≥0, |Φ_Δ|≤C, J*=const. Verified via runtime monitors.",
    }
    try:
        final_state = validate_submission(minimal_submission)
        print("✅ Submission accepted. Final state:", final_state)
    except OmegaProtocolViolation as e:
        print("❌ Omega Protocol violation:", e)