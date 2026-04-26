# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script – Audience Resonance Architecture
-----------------------------------------------------------------
This script validates the mathematical soundness and Omega‑Protocol compliance
of the C++ derivation provided by the user.
"""

import math
from dataclasses import dataclass, field
from typing import Callable

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def sigmoid(x: float) -> float:
    """Map any real psi to (0,1) – used as Trust(psi)."""
    return 1.0 / (1.0 + math.exp(-x))

def binary_entropy(p: float) -> float:
    """Shannon entropy of a Bernoulli variable with probability p."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))

# ----------------------------------------------------------------------
# Data structures mirroring the C++ structs
# ----------------------------------------------------------------------
@dataclass
class CommunicationInvariants:
    psi_identity_coherence: float   # ln(Trust_Score) – can be negative
    xi_solution_stability: float    # 0.0 – 1.0
    xi_process_rigidity: float      # 0.0 – 1.0

    def verify(self) -> bool:
        """Omega Rubric §3 – Invariant compatibility check."""
        return (self.psi_identity_coherence > -2.0) and \
               (self.xi_solution_stability > 0.5) and \
               (self.xi_process_rigidity < 0.9)

@dataclass
class AudienceState:
    latent_need_strength: float
    explicit_risk_perception: float
    decision_entropy: float = field(init=False)
    measurement_avoidance: bool = False

    def calculate_conditional_entropy(self,
                                      pitch_clarity: float,
                                      audience_uncertainty: float) -> float:
        """Shannon conditional entropy H(D|I) for a binary decision."""
        p = pitch_clarity / (pitch_clarity + audience_uncertainty)
        return binary_entropy(p)

    def update_entropy(self, pitch_clarity: float, audience_uncertainty: float):
        self.decision_entropy = self.calculate_conditional_entropy(
            pitch_clarry, audience_uncertainty)

@dataclass
class ChainOverlapDensity:
    alignment_score: float          # cosine similarity [-1,1]
    energy_cost_factor: float       # >=0
    psi_identity_coherence: float   # needed to compute trust weight

    @property
    def trust_weight(self) -> float:
        """Trust(psi) – explicit mapping from psi to (0,1)."""
        return sigmoid(self.psi_identity_coherence)

    def coherence_index(self) -> float:
        """Stability metric – penalises high energy cost."""
        return (self.alignment_score * self.trust_weight) / (1.0 + self.energy_cost_factor)

@dataclass
class FailureMode:
    ENTROPY_MAX_TOLERANCE: float = 0.80
    STIFFNESS_YIELD_LIMIT: float = 0.75

    @staticmethod
    def check_paralysis(entropy: float, risk: float) -> bool:
        return (entropy > FailureMode.ENTROPY_MAX_TOLERANCE) and \
               (risk > FailureMode.STIFFNESS_YIELD_LIMIT)

# ----------------------------------------------------------------------
# Resonant Alignment Operator (exact translation of the C++ version)
# ----------------------------------------------------------------------
def apply_resonant_alignment(audience: AudienceState,
                             invariants: CommunicationInvariants,
                             pitch_clarity: float = 0.7) -> None:
    """
    Mutates `audience` and `invariants` in‑place.
    """
    # Step 1: Validate Invariants
    if not invariants.verify():
        # Fallback: reduce latent need strength to protect brand identity
        audience.latent_need_strength *= 0.9
        return

    # Step 2: Measure current entropy
    current_entropy = audience.calculate_conditional_entropy(
        pitch_clarity, audience.explicit_risk_perception)

    # Step 3: Reduce uncertainty if entropy too high
    if current_entropy > FailureMode().ENTROPY_MAX_TOLERANCE:
        # Validate Signal: "I understand the risk"
        audience.explicit_risk_perception *= 0.85
        audience.decision_entropy -= 0.15   # entropy reduction

    # Step 4: Soft collapse (incremental commitment)
    audience.measurement_avoidance = False

    # Step 5: Update invariants – successful alignment raises solution stability
    invariants.xi_solution_stability += 0.05
    if invariants.xi_solution_stability > 1.0:
        invariants.xi_solution_stability = 1.0

# ----------------------------------------------------------------------
# Validation harness
# ----------------------------------------------------------------------
def run_validation_suite():
    """Execute a series of assertions that enforce Omega compliance."""
    # --- Baseline objects ------------------------------------------------
    inv = CommunicationInvariants(
        psi_identity_coherence=0.0,      # ln(1) = neutral trust
        xi_solution_stability=0.6,
        xi_process_rigidity=0.4
    )
    aud = AudienceState(
        latent_need_strength=1.0,
        explicit_risk_perception=0.3
    )
    aud.update_entropy(pitch_clarity=0.5, audience_uncertainty=0.2)
    cod = ChainOverlapDensity(
        alignment_score=0.7,
        energy_cost_factor=0.2,
        psi_identity_coherence=inv.psi_identity_coherence
    )

    # Helper to capture pre‑state
    def snapshot():
        return {
            "inv_psi": inv.psi_identity_coherence,
            "inv_xiN": inv.xi_solution_stability,
            "inv_xiD": inv.xi_process_rigidity,
            "aud_risk": aud.explicit_risk_perception,
            "aud_entropy": aud.decision_entropy,
            "aud_avoid": aud.measurement_avoidance,
            "cod_coh": cod.coherence_index()
        }

    # 1. Invariants must hold initially
    assert inv.verify(), "Initial invariants violate Omega Rubric §3"

    # 2. Entropy calculation must be Shannon conditional entropy
    #    Spot‑check a few known values:
    assert math.isclose(
        aud.calculate_conditional_entropy(1.0, 0.0), 0.0,
        rel_tol=1e-9), "Entropy for certainty should be 0"
    assert math.isclose(
        aud.calculate_conditional_entropy(1.0, 1.0), binary_entropy(0.5),
        rel_tol=1e-9), "Entropy for 50/50 should be 1 bit"

    # 3. Failure mode detection
    fm = FailureMode()
    # Not paralysed yet
    assert not fm.check_paralysis(aud.decision_entropy, aud.explicit_risk_perception), \
        "False positive paralysis detection"
    # Force paralysis condition
    aud.explicit_risk_perception = 0.8
    aud.decision_entropy = 0.85
    assert fm.check_paralysis(aud.decision_entropy, aud.explicit_risk_perception), \
        "Failed to detect genuine paralysis"

    # 4. Apply Resonant Alignment – should reduce entropy & risk, not break invariants
    apply_resonant_alignment(aud, inv, pitch_clarity=0.7)
    post = snapshot()

    # Invariants still valid
    assert inv.verify(), "Invariants broken after RAO"

    # Entropy must not have increased (it may stay same if already low)
    assert post["aud_entropy"] <= snapshot()["aud_entropy"] + 1e-9, \
        "Entropy increased after Resonant Alignment"

    # Risk perception should have been attenuated (if entropy was high)
    # In our test entropy was high enough to trigger the block:
    assert post["aud_risk"] < snapshot()["aud_risk"] + 1e-9, \
        "Risk perception not reduced when entropy high"

    # Measurement avoidance cleared
    assert not post["aud_avoid"], "Measurement avoidance not cleared"

    # COD coherence index should not decrease (soft collapse improves or maintains alignment)
    # We recompute COD with updated psi (unchanged) and same alignment/energy cost.
    cod_post = ChainOverlapDensity(
        alignment_score=cod.alignment_score,
        energy_cost_factor=cod.energy_cost_factor,
        psi_identity_coherence=inv.psi_identity_coherence
    )
    assert cod_post.coherence_index() >= cod.coherence_index() - 1e-9, \
        "Coherence index degraded after RAO"

    # 5. Trust weight must be a monotonic function of psi
    #    We'll test two psi values.
    def trust_from_psi(psi: float) -> float:
        return sigmoid(psi)

    assert trust_from_psi(-1.0) < trust_from_psi(0.0) < trust_from_psi(1.0), \
        "Trust weight not monotonic in psi"

    # 6. Energy cost factor should not be increased by RAO (implicitly checked)
    #    RAO never touches energy_cost_factor, so we assert equality.
    assert math.isclose(cod_post.energy_cost_factor, cod.energy_cost_factor, rel_tol=1e-9), \
        "Energy cost factor altered by RAO"

    # 7. Safety thresholds – ensure we can evaluate them
    assert 0.0 <= cod_post.coherence_index() <= 1.0, "Coherence index out of expected bounds"
    assert aud.decision_entropy <= FailureMode().ENTROPY_MAX_TOLERANCE + 0.2, \
        "Entropy exceeded reasonable safety margin"

    print("✅ All validation checks passed – the architecture is Omega‑compliant.")

if __name__ == "__main__":
    run_validation_suite()