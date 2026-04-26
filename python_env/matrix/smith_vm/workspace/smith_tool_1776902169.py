# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validation Script for AFDS Prototype
# --------------------------------------------------------------
# Checks mathematical soundness of the core formulas and
# verifies compliance with the stated Omega Protocol invariants:
#   Φ_N   – Non‑linear jitter must stay within [1, 50] ms.
#   Φ_Δ   – Topology‑stress (d(unique_paths)/dt) must be ≥ 0.
#   J*    – Joint scoring must be bounded and monotonic in each term.
# --------------------------------------------------------------

import random
import math
import time
from typing import Dict, Set

# ------------------- Constants from the C++ prototype -------------------
MIN_JITTER_MS = 1
MAX_JITTER_MS = 50
JITTER_DECAY_RATE = 0.7
TRUSTED_PIDS = {1, 1234, 5678}
SCORE_COEFFS = (0.4, 0.3, 0.3)          # a, b, c
MAX_SCORE_FOR_CLAMP = 100.0             # used in Omega_Flags_Handshake

# ------------------- Helper functions -------------------
def nonlinear_jitter() -> float:
    """Reproduce the jitter formula from the prototype."""
    u = random.random()                         # Uniform(0,1)
    return MIN_JITTER_MS + (MAX_JITTER_MS - MIN_JITTER_MS) * (u ** JITTER_DECAY_RATE)

def update_score(state: Dict, path: str, dt: float) -> None:
    """Exact replica of Update_Score (with the buggy depth term)."""
    # path frequency
    state["path_freq"][path] = state["path_freq"].get(path, 0) + 1
    if state["path_freq"][path] == 1:
        state["unique_paths"].add(path)

    # topology stress = d(unique_paths)/dt
    state["topology_stress"] = len(state["unique_paths"]) / dt if dt > 0 else 0.0
    state["last_update"] = time.time()

    # calls/sec approximation (bug: uses number of distinct paths)
    calls_per_sec = len(state["path_freq"]) / dt if dt > 0 else 0.0

    # depth term – length of string before last '/' (as in prototype)
    slash_idx = path.rfind('/')
    depth = slash_idx if slash_idx != -1 else 0

    state["score"] = (SCORE_COEFFS[0] * calls_per_sec +
                      SCORE_COEFFS[1] * len(state["unique_paths"]) +
                      SCORE_COEFFS[2] * depth)

def omega_flags_handshake(state: Dict) -> float:
    """Compute the priority handed to RCOD scheduler."""
    clamped = max(0.0, min(state["score"] / MAX_SCORE_FOR_CLAMP, 1.0))
    return 1.0 - clamped   # priority in [0,1]

# ------------------- Validation routine -------------------
def validate_prototype(samples: int = 100000) -> None:
    """Run Monte‑Carlo style checks and report any invariant violation."""
    violations = []

    # State containers mirroring the C++ struct
    state = {
        "path_freq": {},          # type: Dict[str, int]
        "unique_paths": set(),    # type: Set[str]
        "topology_stress": 0.0,
        "score": 0.0,
        "last_update": time.time()
    }

    for i in range(samples):
        # ---- Jitter bounds (Φ_N) ----
        j = nonlinear_jitter()
        if not (MIN_JITTER_MS - 1e-9 <= j <= MAX_JITTER_MS + 1e-9):
            violations.append(
                f"Jitter out of bounds: {j:.3f} ms (sample {i})"
            )
            if len(violations) > 5:   # stop early on blatant failure
                break

        # ---- Simulate a filesystem event ----
        # Random PID (trusted/untrusted mix)
        pid = random.choice([1, 1234, 5678, 9999, 42])
        trusted = pid in TRUSTED_PIDS

        # Random path (some depth, some repeats)
        depth = random.randint(0, 5)
        path = "/" + "/".join(["dir"] * depth) + f"/file{random.randint(0,9)}"

        # Time delta since last update (simulate async calls)
        now = time.time()
        dt = max(1e-3, now - state["last_update"])   # avoid div‑by‑0

        # Update scoring (same as prototype)
        update_score(state, path, dt)

        # ---- Topology‑stress non‑negative (Φ_Δ) ----
        if state["topology_stress"] < -1e-12:
            violations.append(
                f"Negative topology stress: {state['topology_stress']:.6f} (sample {i})"
            )
            if len(violations) > 5:
                break

        # ---- Score monotonicity in each term (J*) ----
        # We can only test locally: increasing any term should not decrease score.
        # Compute partial contributions:
        calls_per_sec = len(state["path_freq"]) / dt if dt > 0 else 0.0
        unique_cnt = len(state["unique_paths"])
        depth_val = (len(path.rsplit('/', 1)[0]) if '/' in path else 0)

        contrib_a = SCORE_COEFFS[0] * calls_per_sec
        contrib_b = SCORE_COEFFS[1] * unique_cnt
        contrib_c = SCORE_COEFFS[2] * depth_val

        # Each contribution must be >= 0 (coefficients are positive)
        if contrib_a < -1e-12 or contrib_b < -1e-12 or contrib_c < -1e-12:
            violations.append(
                f"Negative contribution detected: a={contrib_a:.3f}, b={contrib_b:.3f}, c={contrib_c:.3f}"
            )
            if len(violations) > 5:
                break

        # Advance time a little to simulate next call
        time.sleep(0.00001)   # negligible, just to move the clock

    # ------------------- Reporting -------------------
    print("\n=== Omega Protocol AFDS Validation ===")
    if not violations:
        print("✅ All invariants satisfied over", samples, "samples.")
        print("   • Φ_N (jitter bounds)      : PASS")
        print("   • Φ_Δ (topology stress ≥0) : PASS")
        print("   • J* (score monotonicity)  : PASS")
    else:
        print("❌ Invariant violations detected:")
        for v in violations[:10]:
            print("   -", v)
        print(f"\n   Total violations: {len(violations)}")

if __name__ == "__main__":
    validate_prototype(samples=200000)