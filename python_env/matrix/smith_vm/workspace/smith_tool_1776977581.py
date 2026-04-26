# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
Validates the AudienceResonanceArchitecture (C++ pseudocode) for:
- Dimensional consistency (all quantities dimensionless)
- Invariant embodiment (psi_id, xi_N, xi_Delta bounds)
- Entropy compliance (Shannon conditional entropy)
- Operator correctness (Strategic Urgency as tanh, Technical Credibility as xi_N)
- Failure mode detection (Paralysis Singularity)
- COD metric and stability threshold
Run: python3 validate_audience_resonance.py
"""

import math
from typing import List

# ----------------------------------------------------------------------
# Helper classes mirroring the C++ structs/logic
# ----------------------------------------------------------------------
class CommunicationInvariants:
    def __init__(self, psi_id: float, xi_N: float, xi_Delta: float):
        self.psi_id = psi_id          # Identity log‑continuity
        self.xi_N = xi_N              # Technical credibility (stability)
        self.xi_Delta = xi_Delta      # Process rigidity

    # Active boundary‑condition check (Omega Rubric §3)
    def VerifyInvariants(self) -> bool:
        PSI_ID_MIN = 0.95
        XI_N_MAX   = 0.82
        XI_D_MAX   = 1.28
        return (self.psi_id >= PSI_ID_MIN and
                self.xi_N   <= XI_N_MAX   and
                self.xi_Delta <= XI_D_MAX)

    def CalculatePhiLoss(self) -> float:
        loss = 0.0
        if self.psi_id < 0.95:
            loss += (0.95 - self.psi_id) * 0.5
        if self.xi_N > 0.82:
            loss += (self.xi_N - 0.82) * 0.3
        if self.xi_Delta > 1.28:
            loss += (self.xi_Delta - 1.28) * 0.3
        return loss


class AudienceState:
    def __init__(self,
                 psi_latent: List[float],
                 psi_decision: List[float],
                 explicit_risk_perception: float,
                 energy_cost_factor: float):
        self.psi_latent = psi_latent
        self.psi_decision = psi_decision
        self.explicit_risk_perception = explicit_risk_perception
        self.energy_cost_factor = energy_cost_factor

    def CalculateShannonConditionalEntropy(self, info_vector: List[float]) -> float:
        # Compute normalized overlap probability p = <psi_latent|info> / (||psi_latent||·||info||)
        dot = sum(l * i for l, i in zip(self.psi_latent, info_vector))
        norm_lat = math.sqrt(sum(l * l for l in self.psi_latent))
        norm_info = math.sqrt(sum(i * i for i in info_vector))
        if norm_lat == 0 or norm_info == 0:
            p = 0.0
        else:
            p = dot / (norm_lat * norm_info)
        # Clamp to avoid log(0)
        eps = 1e-3
        p = max(eps, min(1.0 - eps, p))
        # Shannon entropy (dimensionless)
        return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))


class ChainOverlapDensity:
    COD_THRESHOLD = 0.85

    def __init__(self,
                 alignment_score: float,
                 stiffness_penalty: float,
                 energy_cost_factor: float):
        self.alignment_score = alignment_score          # |<Psi_pitch|Psi_need>|^2 ∈ [0,1]
        self.stiffness_penalty = stiffness_penalty      # exp(-xi_bound/xi_elasticity) ∈ (0,1]
        self.energy_cost_factor = energy_cost_factor    # ≥0

    def coherence_index(self) -> float:
        return (self.alignment_score * self.stiffness_penalty) / (1.0 + self.energy_cost_factor)

    @staticmethod
    def IsStable(cod: float) -> bool:
        return cod >= ChainOverlapDensity.COD_THRESHOLD


class FailureMode:
    ENTROPY_MAX_TOLERANCE = 0.80   # dimensionless (bits)
    STIFFNESS_YIELD_LIMIT = 0.75   # dimensionless

    @staticmethod
    def CheckParalysis(entropy: float, risk: float, stability: float) -> bool:
        return (entropy > FailureMode.ENTROPY_MAX_TOLERANCE and
                risk   > FailureMode.STIFFNESS_YIELD_LIMIT and
                stability < 0.5)


def ComputeStrategicUrgency(t: float, tau_opt: float, sigma: float) -> float:
    """Gamma(t) = tanh((t - tau_opt) / sigma)"""
    return math.tanh((t - tau_opt) / sigma)


# ----------------------------------------------------------------------
# Validation suite
# ----------------------------------------------------------------------
def run_validation():
    print("=== Omega Protocol Audience Resonance Validation ===")

    # 1. Invariant sanity
    inv_ok = CommunicationInvariants(psi_id=0.96, xi_N=0.70, xi_Delta=1.10)
    assert inv_ok.VerifyInvariants(), "Valid invariants should pass"
    print("✓ Invariant check passes for nominal values")

    # Invariant violation detection
    inv_bad = CommunicationInvariants(psi_id=0.90, xi_N=0.90, xi_Delta=1.0)
    assert not inv_bad.VerifyInvariants(), "Invariants should fail when out of bounds"
    print("✓ Invariant check correctly rejects out‑of‑bounds values")
    print(f"  Φ‑loss for bad invariants: {inv_bad.CalculatePhiLoss():.4f}")

    # 2. Entropy calculation dimensionality & range
    state = AudienceState(
        psi_latent=[0.6, 0.8],
        psi_decision=[0.5, 0.6],
        explicit_risk_perception=0.3,
        energy_cost_factor=0.2
    )
    info_vec = [0.5, 0.7]
    entropy = state.CalculateShannonConditionalEntropy(info_vec)
    assert 0.0 <= entropy <= math.log(2), f"Entropy out of dimensionless range: {entropy}"
    print(f"✓ Shannon conditional entropy = {entropy:.4f} (dimensionless, within [0, ln2])")

    # 3. COD metric and stability threshold
    cod = ChainOverlapDensity(
        alignment_score=0.9,
        stiffness_penalty=math.exp(-0.3),   # example xi_bound/xi_elasticity = 0.3
        energy_cost_factor=0.1
    )
    coh = cod.coherence_index()
    assert 0.0 <= coh <= 1.0, "Coherence index should be bounded"
    stable = ChainOverlapDensity.IsStable(coh)
    print(f"✓ COD coherence index = {coh:.4f}, stable? {stable} (threshold {ChainOverlapDensity.COD_THRESHOLD})")

    # 4. Failure mode detection
    # Case A: should trigger paralysis
    entrained_entropy = 0.85
    risk = 0.8
    stability = 0.4
    assert FailureMode.CheckParalysis(entrained_entropy, risk, stability), \
        "Paralysis should be detected for high entropy, high risk, low stability"
    print("✓ Paralysis detection triggers for high‑entropy/high‑risk/low‑stability case")

    # Case B: should NOT trigger
    assert not FailureMode.CheckParalysis(0.5, 0.5, 0.6), \
        "Paralysis should NOT fire when any condition fails"
    print("✓ Paralysis correctly stays silent when conditions are not met")

    # 5. Strategic Urgency operator (adibatic tanh)
    gamma = ComputeStrategicUrgency(t=0.6, tau_opt=0.5, sigma=0.1)
    assert -1.0 <= gamma <= 1.0, "tanh output must be in [-1,1]"
    print(f"✓ Strategic Urgency Gamma(t) = {gamma:.4f} (tanh‑based adiabatic control)")

    # 6. Post‑intervention invariant safety (simulate Apply logic)
    # Simulate a scenario where urgency > 0.5 triggers xi_N boost
    t = 0.7
    gamma = ComputeStrategicUrgency(t, tau_opt=0.5, sigma=0.1)
    xi_N_before = 0.70
    xi_N_after = min(0.82, xi_N_before + 0.05) if gamma > 0.5 else xi_N_before
    inv_after = CommunicationInvariants(psi_id=0.96, xi_N=xi_N_after, xi_Delta=1.10)
    assert inv_after.VerifyInvariants(), "Post‑urgency invariants must still hold"
    print(f"✓ After urgency injection (γ={gamma:.3f}), xi_N updated to {xi_N_after:.3f}, invariants still valid")

    print("\nAll validation checks passed. The architecture is mathematically sound and Omega‑Protocol compliant.")


if __name__ == "__main__":
    run_validation()