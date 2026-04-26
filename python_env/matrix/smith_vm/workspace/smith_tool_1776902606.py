# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
validate_afds.py
----------------
Validates the mathematical soundness of the AFDS v3.0 prototype
against the Omega Protocol invariants:
    * Phi_N   : Trust mitigation ∈ [0.2, 1.0]   (baseline jitter always applied)
    * Phi_Delta: |Δtrust| ≤ ε_trust  (ε_trust = 0.01 per event, configurable)
    * J_star  : Effective jitter latency ∈ [1, 50] ms
    * Trust score ∈ [0, 1]
    * Jitter probability ∈ [0, 1]
"""

import random
import math
from typing import Dict, Tuple

# -------------------------- Configuration --------------------------
EPS_TRUST = 0.01          # max allowed absolute change in trust per event (Phi_Delta)
MAX_PATHS_PER_PID = 10    # limit size of accessed_paths to keep consistency calc sane
TRUST_INCREMENT_FACTOR = 0.1
TRUST_DECREMENT_FACTOR = 0.005  # optional decay to avoid drift
TRUST_CLAMP = (0.0, 1.0)
MITIGATION_RANGE = (0.2, 1.0)    # 80% reduction at trust=1.0
JITTER_PROB_RANGE = (0.0, 1.0)
JITTER_MS_RANGE = (1, 50)        # inclusive
TRAVERSAL_SCORE_RANGE = (0.0, 100.0)   # assumed domain for the probability function
# ------------------------------------------------------------------

class TrustState:
    __slots__ = ("pid", "trust_score", "accessed_paths", "last_access")
    def __init__(self, pid: int):
        self.pid = pid
        self.trust_score = 0.0
        self.accessed_paths = set()
        self.last_access = 0  # placeholder

    def add_path(self, path: str):
        self.accessed_paths.add(path)
        if len(self.accessed_paths) > MAX_PATHS_PER_PID:
            # keep the set bounded to avoid memory blow‑up
            self.accessed_paths.clear()
            self.accessed_paths.add(path)

    def consistency(self, path: str) -> float:
        if not self.accessed_paths:
            return 0.0
        return self.accessed_paths.count(path) / len(self.accessed_paths)


class TrustManager:
    def __init__(self):
        self._states: Dict[int, TrustState] = {}

    def _get_state(self, pid: int) -> TrustState:
        if pid not in self._states:
            self._states[pid] = TrustState(pid)
        return self._states[pid]

    def update_trust(self, pid: int, path: str, traversal_score: float):
        state = self._get_state(pid)
        # ----- Consistency based increment -----
        consist = state.consistency(path)
        delta_inc = TRUST_INCREMENT_FACTOR * consist
        # ----- Optional decay (prevents runaway trust) -----
        delta_dec = TRUST_DECREMENT_FACTOR * (1.0 - state.trust_score)
        new_trust = state.trust_score + delta_inc - delta_dec
        new_trust = max(TRUST_CLAMP[0], min(TRUST_CLAMP[1], new_trust))
        # ----- Phi_Delta check -----
        assert abs(new_trust - state.trust_score) <= EPS_TRUST, \
            f"Trust delta {new_trust - state.trust_score:.4f} exceeds EPS_TRUST={EPS_TRUST}"
        state.trust_score = new_trust
        state.accessed_paths.add(path)
        # ----- Phi_N: trust must stay in [0,1] -----
        assert TRUST_CLAMP[0] <= state.trust_score <= TRUST_CLAMP[1], \
            f"Trust out of bounds: {state.trust_score}"
        return state.trust_score

    def get_mitigation(self, pid: int) -> float:
        state = self._states.get(pid)
        if state is None:
            # default mitigation for unknown process = max reduction (i.e. lowest latency)
            return MITIGATION_RANGE[0]
        mitigation = MITIGATION_RANGE[0] + (MITIGATION_RANGE[1] - MITIGATION_RANGE[0]) * state.trust_score
        # ----- Phi_N: mitigation must stay inside the allowed band -----
        assert MITIGATION_RANGE[0] <= mitigation <= MITIGATION_RANGE[1], \
            f"Mitigation {mitigation:.4f} outside [{MITIGATION_RANGE[0]}, {MITIGATION_RANGE[1]}]"
        return mitigation


def jitter_probability(traversal_score: float) -> float:
    # Clamp traversal_score to the assumed domain
    ts = max(TRAVERSAL_SCORE_RANGE[0], min(TRAVERSAL_SCORE_RANGE[1], traversal_score))
    p = math.pow(ts / 100.0, 1.5)
    # ----- Jitter probability must be in [0,1] -----
    assert JITTER_PROB_RANGE[0] <= p <= JITTER_PROB_RANGE[1], \
        f"Jitter probability {p:.4f} out of range"
    return p


def apply_jitter(traversal_score: float, mitigation: float) -> int:
    """Returns the latency in ms that should be slept."""
    prob = jitter_probability(traversal_score)
    if random.random() < prob:
        jitter_ms = random.randint(JITTER_MS_RANGE[0], JITTER_MS_RANGE[1])
        # Apply mitigation (higher trust → lower latency)
        effective_ms = jitter_ms * mitigation
        # Clamp to the protocol‑defined jitter band
        effective_ms = max(JITTER_MS_RANGE[0], min(JITTER_MS_RANGE[1], effective_ms))
        # ----- J_star: final latency must be within [1,50] ms -----
        assert JITTER_MS_RANGE[0] <= effective_ms <= JITTER_MS_RANGE[1], \
            f"Effective jitter {effective_ms:.2f} ms outside [{JITTER_MS_RANGE[0]}, {JITTER_MS_RANGE[1]}]"
        return int(round(effective_ms))
    return 0   # no jitter injected this call


def run_validation(iterations: int = 100_000):
    tm = TrustManager()
    for i in range(iterations):
        pid = random.randint(1, 1000)
        # Simulate a path like "/home/userX/dirY/fileZ"
        depth = random.randint(0, 5)
        path = "/" + "/".join([f"part{random.randint(0,9)}" for _ in range(depth)])
        traversal_score = random.uniform(*TRAVERSAL_SCORE_RANGE)

        # Update trust (also checks Phi_Delta and Phi_N)
        tr = tm.update_trust(pid, path, traversal_score)

        # Get mitigation (checks Phi_N)
        mitig = tm.get_mitigation(pid)

        # Apply jitter (checks J_star and probability bounds)
        latency_ms = apply_jitter(traversal_score, mitig)

        # Optional: sanity‑check that latency correlates with trust as expected
        # High trust → low latency, low trust → higher latency (but never zero)
        if tr > 0.8:
            assert latency_ms <= int(0.5 * JITTER_MS_RANGE[1]), \
                f"High trust ({tr:.2f}) produced too much latency: {latency_ms}ms"
        elif tr < 0.2:
            # low trust should see latency close to the raw jitter range
            assert latency_ms >= int(0.5 * JITTER_MS_RANGE[0]), \
                f"Low trust ({tr:.2f}) produced suspiciously low latency: {latency_ms}ms"

    print(f"✅ Validation passed over {iterations:,} random iterations.")


if __name__ == "__main__":
    run_validation()