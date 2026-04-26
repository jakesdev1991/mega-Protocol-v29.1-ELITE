# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Validation Script
Validates the mathematical soundness and invariant compliance of the
Organizational Decision Manifold derivation (Omega-Psych-Theorist).

Invariants (as inferred from the Omega Protocol):
    Φ_N   : Normalization of the latent institutional state vector
            (probabilities sum to 1)
    Φ_Δ   : Boundedness of risk tolerance and rigidity [0,1]
    J*    : Non‑negative impedance and monotonic non‑increase under
            the stabilization operator (Protocol Harmonization)
            while preserving safety orthogonality.
"""

import random
import math
from dataclasses import dataclass, field
from typing import Tuple

TOL = 1e-9

@dataclass
class DecisionManifold:
    # Subconscious (Latent Institutional Will)
    latent_acceptance_prob: float = 0.0
    latent_reject_prob: float = 0.0
    latent_defer_prob: float = 0.0
    latent_risk_tolerance: float = 0.0   # ∈ [0,1]

    # Conscious (Explicit Protocol Layer)
    approval_layers: int = field(default=1)   # ≥1
    rule_rigidity: float = 0.0               # ∈ [0,1]

    # Derived / dynamic quantities
    impedance_factor: float = 0.0            # ≥0

    def __post_init__(self):
        self._normalize_latent()
        self._clamp_risk()
        self._clamp_rigidity()
        self._enforce_layers()
        self._enforce_impedance_nonneg()

    # -----------------------------------------------------------------
    # Invariant helpers
    # -----------------------------------------------------------------
    def _normalize_latent(self):
        total = self.latent_acceptance_prob + self.latent_reject_prob + self.latent_defer_prob
        if abs(total) < TOL:
            # degenerate case: assign uniform distribution
            self.latent_acceptance_prob = self.latent_reject_prob = self.latent_defer_prob = 1.0/3.0
        else:
            self.latent_acceptance_prob /= total
            self.latent_reject_prob     /= total
            self.latent_defer_prob      /= total

    def _clamp_risk(self):
        self.latent_risk_tolerance = min(max(self.latent_risk_tolerance, 0.0), 1.0)

    def _clamp_rigidity(self):
        self.rule_rigidity = min(max(self.rule_rigidity, 0.0), 1.0)

    def _enforce_layers(self):
        if self.approval_layers < 1:
            self.approval_layers = 1

    def _enforce_impedance_nonneg(self):
        if self.impedance_factor < 0:
            self.impedance_factor = 0.0

    # -----------------------------------------------------------------
    # COD calculation (as per derivation)
    # -----------------------------------------------------------------
    def calculate_COD(self, proposal_novelty: float) -> float:
        """
        COD = 1 - (proposal_novelty * rule_rigidity)
        Both inputs expected in [0,1]; output clamped to [0,1].
        """
        proposal_novelty = min(max(proposal_novelty, 0.0), 1.0)
        cod = 1.0 - (proposal_novelty * self.rule_rigidity)
        return min(max(cod, 0.0), 1.0)

    # -----------------------------------------------------------------
    # Stabilization Operator: Protocol Harmonization
    # -----------------------------------------------------------------
    def apply_protocol_harmonization(self, proposal_value: float) -> None:
        """
        Implements the steps described in the derivation:
          1. Increase latent risk tolerance (softening)
          2. Reduce approval layers (sandbox) – min 1
          3. Reduce impedance factor by 30%
          4. Safety orthogonality check: if proposal_value > risk tolerance,
             increment approval layers (escalation)
        All operations preserve the defined invariants.
        """
        # Store pre‑state for monotonicity checks
        old_impedance = self.impedance_factor
        old_layers    = self.approval_layers
        old_risk      = self.latent_risk_tolerance

        # Step 1: Softening of latent will
        self.latent_risk_tolerance = min(self.latent_risk_tolerance + 0.1, 1.0)

        # Step 2: Sandbox – reduce approval layers (but not below 1)
        self.approval_layers = max(self.approval_layers - 1, 1)

        # Step 3: Impedance reduction
        self.impedance_factor *= 0.7
        self._enforce_impedance_nonneg()

        # Step 4: Safety orthogonality guardrail
        if proposal_value > self.latent_risk_tolerance:
            self.approval_layers += 1
            self._enforce_layers()

        # -----------------------------------------------------------------
        # Invariant enforcement after operation
        # -----------------------------------------------------------------
        self._normalize_latent()
        self._clamp_risk()
        self._clamp_rigidity()
        self._enforce_layers()
        self._enforce_impedance_nonneg()

        # Assert Omega Protocol invariants
        assert abs(self.latent_acceptance_prob +
                   self.latent_reject_prob +
                   self.latent_defer_prob - 1.0) < TOL, "Φ_N violated: latent state not normalized"

        assert 0.0 <= self.latent_risk_tolerance <= 1.0, "Φ_Δ violated: risk tolerance out of bounds"
        assert 0.0 <= self.rule_rigidity <= 1.0,       "Φ_Δ violated: rule rigidity out of bounds"
        assert self.approval_layers >= 1,              "Φ_Δ violated: approval_layers < 1"
        assert self.impedance_factor >= 0.0,           "J* violated: negative impedance"

        # Monotonicity of impedance under harmonization (should not increase)
        assert self.impedance_factor <= old_impedance + TOL, \
               "J* violated: impedance increased after harmonization"

        # Approval layers may drop by at most one (sandbox) before safety check
        # After safety check they can only increase relative to the sandboxed value.
        assert self.approval_layers >= old_layers - 1, \
               "Protocol Harmonization reduced layers by more than one (pre‑safety)"

        # Latent risk tolerance increase bounded by 0.1 (clipped)
        assert self.latent_risk_tolerance <= old_risk + 0.1 + TOL, \
               "Latent risk tolerance increased beyond allowed harmonization step"

    # -----------------------------------------------------------------
    # Utility for testing
    # -----------------------------------------------------------------
    def state_snapshot(self) -> Tuple:
        return (self.latent_acceptance_prob,
                self.latent_reject_prob,
                self.latent_defer_prob,
                self.latent_risk_tolerance,
                self.approval_layers,
                self.rule_rigidity,
                self.impedance_factor)


def random_test(iterations: int = 1000):
    """Run random stress‑tests to verify invariant compliance."""
    for i in range(iterations):
        dm = DecisionManifold(
            latent_acceptance_prob=random.random(),
            latent_reject_prob=random.random(),
            latent_defer_prob=random.random(),
            latent_risk_tolerance=random.random(),
            approval_layers=random.randint(1, 5),
            rule_rigidity=random.random(),
            impedance_factor=random.random()
        )
        # Random proposal novelty and value
        novelty = random.random()
        value   = random.random()

        # COD should be well‑defined
        cod = dm.calculate_COD(novelty)
        assert 0.0 <= cod <= 1.0, f"Iter {i}: COD out of bounds"

        # Apply harmonization; should not raise AssertionError
        dm.apply_protocol_harmonization(value)

    print(f"All {iterations} random tests passed – invariants hold.")


if __name__ == "__main__":
    random_test()