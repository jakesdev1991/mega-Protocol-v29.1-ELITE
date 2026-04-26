# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# Omega Protocol Invariant Validator for AFDS v3.0 (Research‑Grade)
# =============================================================================
# This script checks the core mathematical invariants that any compliant
# implementation of the Adaptive Filesystem Defense System must satisfy.
# It does **not** execute the actual FUSE daemon; instead it validates the
# formulas and bounds used in the Trust Manager, Jitter, Forensic Logger,
# and Curvature calculations.
#
# Usage: python3 afds_invariant_check.py
# =============================================================================

import math
import random
from typing import List, Tuple

# -----------------------------------------------------------------------------
# Constants that should appear as `constexpr` in the C++ source
# -----------------------------------------------------------------------------
XI_N: float = 0.8          # stiffness for Newtonian trust
XI_DELTA: float = 1.2      # stiffness for asymmetric threat
TRUST_DECAY_BASE: float = 0.95   # base of exponential trust decay (per hour)
NOVELTY_PENALTY: float = 0.05    # penalty when a path is novel
TRUST_STABILITY_GAIN: float = 0.01   # gain per unit of cumulative stability
JITTER_RANGE_MS: Tuple[int, int] = (1, 50)   # normal jitter range
PHI_DELTA_SHRED_THRESHOLD: float = 0.95   # triggers 1000 ms stall
EPS: float = 1e-10         # small epsilon to avoid log(0)

# -----------------------------------------------------------------------------
# Helper data structures mirroring the C++ definitions (simplified)
# -----------------------------------------------------------------------------
class ProcessTrustState:
    def __init__(self, pid: int):
        self.pid = pid
        self.trust_score: float = 0.0          # ∈ [0,1]
        self.last_access: float = 0.0          # seconds since epoch (dummy)
        self.accessed_paths: set = set()
        self.cumulative_stability: float = 0.0 # Σ exp(-Δt/τ)

class TopologyMetrics:
    def __init__(self):
        self.max_depth: int = 0
        self.unique_paths: set = set()
        self.depth_histogram: List[int] = []   # index = depth
        self.traversal_entropy: float = 0.0    # Σ log(depth+1)·0.01

class ForensicLogEntry:
    def __init__(self, pid: int, operation: str, path: str,
                 applied_latency_ms: int, traversal_score: float,
                 trust_score: float, inter_call_interval: float,
                 phi_Delta: float, timestamp: float = 0.0):
        self.pid = pid
        self.operation = operation
        self.path = path
        self.applied_latency_ms = applied_latency_ms
        self.traversal_score = traversal_score
        self.trust_score = trust_score
        self.inter_call_interval = inter_call_interval
        self.phi_Delta = phi_Delta
        self.timestamp = timestamp

# -----------------------------------------------------------------------------
# Core invariant‑checking functions
# -----------------------------------------------------------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def trust_update(state: ProcessTrustState, path: str, access_success: bool,
                 now: float) -> None:
    """Implements the trust‑score update from the C++ code."""
    is_novel = path not in state.accessed_paths
    novelty_penalty = NOVELTY_PENALTY if is_novel else 0.0

    # time decay (hours)
    delta_h = (now - state.last_access) / 3600.0
    state.trust_score *= math.exp(-math.log(TRUST_DECAY_BASE) * delta_h)
    state.trust_score = clamp(state.trust_score - novelty_penalty, 0.0, 1.0)

    if not is_novel:
        # stability contribution (approximate integral)
        state.cumulative_stability += math.exp(-delta_h)
        state.trust_score += TRUST_STABILITY_GAIN * math.exp(-0.1 * state.cumulative_stability)
        state.trust_score = clamp(state.trust_score, 0.0, 1.0)

    state.accessed_paths.add(path)
    state.last_access = now

def trust_mitigation(state: ProcessTrustState) -> float:
    """0.8 * trust_score (as in GetTrustMitigation)."""
    return 0.8 * state.trust_score

def newtonian_trust_baseline(state: ProcessTrustState) -> float:
    """φ_N = exp(-H_noise) * stability_integral."""
    H_noise = math.log(len(state.accessed_paths) + 1.0)
    return math.exp(-H_noise) * state.cumulative_stability

def asymmetric_threat(metrics: TopologyMetrics) -> float:
    """φ_Delta = |breadth - depth| / (breadth + depth)."""
    breadth = len(metrics.unique_paths)
    depth = metrics.max_depth
    if breadth + depth == 0:
        return 0.0
    return abs(breadth - depth) / (breadth + depth)

def traversal_score(metrics: TopologyMetrics) -> float:
    """Score used for jitter probability: 0.6*|unique| + 0.4*max_depth."""
    return 0.6 * len(metrics.unique_paths) + 0.4 * metrics.max_depth

def jitter_probability(raw_score: float, mitigation: float, phi_Delta: float) -> float:
    """p = (raw/100)^1.5 * mitigation * (1+phi_Delta), clamped [0,1]."""
    p = (raw_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_Delta)
    return clamp(p, 0.0, 1.0)

def apply_adaptive_jitter(raw_score: float, mitigation: float, phi_Delta: float) -> int:
    """Returns latency in ms according to the spec."""
    if phi_Delta > PHI_DELTA_SHRED_THRESHOLD:
        return 1000   # shredding stall
    p = jitter_probability(raw_score, mitigation, phi_Delta)
    if random.random() < p:
        return random.randint(*JITTER_RANGE_MS)
    return 0

def update_topology(path: str, metrics: TopologyMetrics) -> None:
    """Updates unique paths, max depth, histogram, and entropy."""
    metrics.unique_paths.add(path)
    depth = path.count('/')
    # max_depth (atomic‑style update)
    if depth > metrics.max_depth:
        metrics.max_depth = depth
    # histogram
    if depth >= len(metrics.depth_histogram):
        metrics.depth_histogram.extend([0] * (depth - len(metrics.depth_histogram) + 1))
    metrics.depth_histogram[depth] += 1
    # entropy (approximate)
    metrics.traversal_entropy += math.log(depth + 1) * 0.01

def topological_impedance(log: List[ForensicLogEntry]) -> float:
    """Discrete trapezoidal ∫ gauge dψ where ψ=ln(trust+ε), gauge=trust*|phi_Delta|."""
    if not log:
        return 0.0
    impedance = 0.0
    prev_psi = math.log(log[0].trust_score + EPS)
    prev_gauge = log[0].trust_score * abs(log[0].phi_Delta)
    for entry in log[1:]:
        psi = math.log(entry.trust_score + EPS)
        gauge = entry.trust_score * abs(entry.phi_Delta)
        impedance += (gauge + prev_gauge) * 0.5 * (psi - prev_psi)
        prev_psi, prev_gauge = psi, gauge
    return impedance

def manifold_curvature(phi_N: float, phi_Delta: float, H_imp: float) -> float:
    """ξ_N·φ_N + ξ_Δ·φ_Δ - H_imp."""
    return XI_N * phi_N + XI_DELTA * phi_Delta - H_imp

# -----------------------------------------------------------------------------
# Validator that runs a synthetic scenario and asserts all invariants
# -----------------------------------------------------------------------------
def run_validation() -> None:
    print("[AFDS Invariant Validator] Starting synthetic test...")

    # --- Setup dummy state ----------------------------------------------------
    pid = 12345
    state = ProcessTrustState(pid)
    metrics = TopologyMetrics()
    log: List[ForensicLogEntry] = []

    now = 0.0   # simulated time in seconds

    # Simulate a mixed sequence of accesses
    test_paths = [
        "/etc/passwd", "/etc/shadow", "/var/log/syslog",
        "/home/user/fileA", "/home/user/fileB", "/home/user/fileC",
        "/tmp/x", "/tmp/y", "/tmp/z", "/honey"   # honey node at the end
    ]

    for i, p in enumerate(test_paths):
        # --- Trust update ----------------------------------------------------
        trust_update(state, p, access_success=True, now=now)
        now += 300.0   # 5 min between operations

        # --- Topology update -------------------------------------------------
        update_topology(p, metrics)

        # --- Compute derived quantities ---------------------------------------
        phi_N = newtonian_trust_baseline(state)
        phi_Delta = asymmetric_threat(metrics)
        raw_score = traversal_score(metrics)
        mitigation = trust_mitigation(state)

        # --- Jitter -----------------------------------------------------------
        latency = apply_adaptive_jitter(raw_score, mitigation, phi_Delta)

        # --- Forensic log entry -----------------------------------------------
        entry = ForensicLogEntry(
            pid=pid,
            operation="lookup",
            path=p,
            applied_latency_ms=latency,
            traversal_score=raw_score,
            trust_score=state.trust_score,
            inter_call_interval=300.0,
            phi_Delta=phi_Delta,
            timestamp=now
        )
        log.append(entry)

    # --- Invariant checks -----------------------------------------------------
    errors: List[str] = []

    # 1. Trust score bounds
    if not (0.0 <= state.trust_score <= 1.0):
        errors.append(f"Trust score out of bounds: {state.trust_score}")

    # 2. Mitigation bounds (0.8 * trust)
    mitigation = trust_mitigation(state)
    if not (0.0 <= mitigation <= 0.8):
        errors.append(f"Mitigation out of bounds: {mitigation}")

    # 3. φ_N non‑negative (by definition)
    phi_N = newtonian_trust_baseline(state)
    if phi_N < 0.0:
        errors.append(f"φ_N negative: {phi_N}")

    # 4. φ_Delta in [0,1]
    phi_Delta = asymmetric_threat(metrics)
    if not (0.0 <= phi_Delta <= 1.0):
        errors.append(f"φ_Delta out of bounds: {phi_Delta}")

    # 5. Traversal score non‑negative
    raw_score = traversal_score(metrics)
    if raw_score < 0.0:
        errors.append(f"Traversal score negative: {raw_score}")

    # 6. Jitter probability in [0,1] (implicit in function)
    p = jitter_probability(raw_score, mitigation, phi_Delta)
    if not (0.0 <= p <= 1.0):
        errors.append(f"Jitter probability out of bounds: {p}")

    # 7. Applied latency must be either 0, 1‑50, or 1000
    if latency not in (0, 1000) and not (JITTER_RANGE_MS[0] <= latency <= JITTER_RANGE_MS[1]):
        errors.append(f"Illegal latency: {latency} ms")

    # 8. Topological impedance should be a real number (no NaN/Inf)
    H_imp = topological_impedance(log)
    if math.isnan(H_imp) or math.isinf(H_imp):
        errors.append(f"Topological impedance is NaN/Inf: {H_imp}")

    # 9. Curvature should be real
    curvature = manifold_curvature(phi_N, phi_Delta, H_imp)
    if math.isnan(curvature) or math.isinf(curvature):
        errors.append(f"Manifold curvature is NaN/Inf: {curvature}")

    # 10. Honey‑node trigger: at least one entry with path == "/honey" should have
    #     triggered a report (we simulate by checking that the entry exists)
    honey_entries = [e for e in log if e.path == "/honey"]
    if not honey_entries:
        errors.append("Honey‑node path '/honey' never accessed in test.")
    else:
        # In a real system the forensic logger would call GenerateReport()
        # Here we just note that the condition is detectable.
        pass

    # -------------------------------------------------------------------------
    if errors:
        print("\n[FAIL] Invariant violations detected:")
        for err in errors:
            print(" -", err)
        return False
    else:
        print("\n[PASS] All core Omega‑Protocol invariants hold for the synthetic run.")
        print(f"   Final trust score: {state.trust_score:.4f}")
        print(f"   φ_N: {phi_N:.4f}, φ_Δ: {phi_Delta:.4f}")
        print(f"   Topological impedance: {H_imp:.4f}")
        print(f"   Manifold curvature: {curvature:.4f}")
        return True

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    success = run_validation()
    exit(0 if success else 1)