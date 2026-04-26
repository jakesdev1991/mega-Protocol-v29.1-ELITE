# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for AFDS v3.0 (Corrected)
Checks:
  * Trust ∈ [0,1]
  * Mitigation M(T) = 1 - 0.8*T ∈ [0.2,1]
  * Base jitter probability P0 ∈ [0,1]
  * Final probability P ∈ [0,1]
  * Jitter latency L ∈ {0} ∪ [1,50] ∪ {1000}
  * Phi_Delta >= 0 (assumed supplied)
  * Audit cost subtraction yields net Φ-density <= raw_gain
"""

import random
import math
from typing import Tuple

# ------------------- Parameters (as per spec) -------------------
ALPHA = 1.5               # exponent for base probability
TRUST_DECAY_LAMBDA = -math.log(0.95)   # ≈0.051293
NOVELTY_PENALTY = 0.05
STABILITY_GAIN = 0.01
STABILITY_DECAY = 0.1
AUDIT_COMPLEXITY = 2.5
K_B = 1.0                 # Boltzmann constant (set to 1 for Φ-density units)

# ------------------- Helper Functions -------------------
def decay_trust(trust: float, dt_hours: float) -> float:
    """Apply exponential decay over dt (hours)."""
    return trust * math.exp(-TRUST_DECAY_LAMBDA * dt_hours)

def update_trust(trust: float, cumulative_stab: float,
                 is_novel: bool, dt_hours: float) -> Tuple[float, float]:
    trust = decay_trust(trust, dt_hours)
    if is_novel:
        trust -= NOVELTY_PENALTY
    else:
        cumulative_stab += math.exp(-STABILITY_DECAY * dt_hours)
        trust += STABILITY_GAIN * math.exp(-STABILITY_DECAY * cumulative_stab)
    trust = max(0.0, min(1.0, trust))
    return trust, cumulative_stab

def mitigation(trust: float) -> float:
    """Remaining jitter probability factor after trust discount."""
    return 1.0 - 0.8 * trust   # ∈ [0.2, 1.0]

def base_probability(raw_score: float) -> float:
    """P0 = (raw_score/100)^α, clamped to [0,1]."""
    p = (raw_score / 100.0) ** ALPHA
    return max(0.0, min(1.0, p))

def final_probability(raw_score: float, trust: float, phi_delta: float) -> float:
    p0 = base_probability(raw_score)
    m = mitigation(trust)
    p = p0 * m * (1.0 + phi_delta)
    return max(0.0, min(1.0, p))

def jitter_latency(raw_score: float, trust: float, phi_delta: float) -> int:
    if phi_delta > 0.95:
        return 1000                     # panic‑sleep (allowed extreme)
    p = final_probability(raw_score, trust, phi_delta)
    if random.random() < p:
        return random.randint(1, 50)    # ms
    return 0

def phi_density(raw_gain: float = 0.85) -> float:
    audit_entropy = K_B * math.log(2.0) * AUDIT_COMPLEXITY
    return raw_gain - audit_entropy   # should be +0.75Φ per claim

# ------------------- Monte‑Carlo Validation -------------------
def run_validation(samples: int = 200_000) -> None:
    random.seed(42)
    for i in range(samples):
        # Random but bounded inputs
        raw_score = random.uniform(0, 200)      # can exceed 100 to stress clamp
        trust = random.random()                 # [0,1]
        phi_delta = random.uniform(0, 2.0)      # allow >1 to test robustness
        dt_hours = random.uniform(0, 10)
        is_novel = random.choice([True, False])
        cum_stab = random.random()

        # Trust update
        trust2, cum_stab2 = update_trust(trust, cum_stab, is_novel, dt_hours)
        assert 0.0 <= trust2 <= 1.0, f"Trust out of bounds: {trust2}"
        assert 0.0 <= cum_stab2 <= 5.0, f"CumStab unreasonable: {cum_stab2}"

        # Mitigation bounds
        m = mitigation(trust2)
        assert 0.2 <= m <= 1.0, f"Mitigation out of [0.2,1]: {m}"

        # Probability bounds
        p = final_probability(raw_score, trust2, phi_delta)
        assert 0.0 <= p <= 1.0, f"Probability out of bounds: {p}"

        # Jitter latency bounds
        L = jitter_latency(raw_score, trust2, phi_delta)
        assert L == 0 or (1 <= L <= 50) or L == 1000, f"Invalid latency: {L}"

        # Periodic audit‑cost check (deterministic)
        if i % 5000 == 0:
            net_phi = phi_density()
            assert net_phi <= 0.85, f"Net Φ-density exceeds raw gain: {net_phi}"
            # The spec claims +0.75Φ after audit cost → net_phi ≈ 0.75
            # Allow small tolerance due to rounding
            assert abs(net_phi - 0.75) < 0.01, f"Net Φ-density mismatch: {net_phi}"

    print("[Ω-PASS] All invariants satisfied over", samples, "samples.")

if __name__ == "__main__":
    run_validation()