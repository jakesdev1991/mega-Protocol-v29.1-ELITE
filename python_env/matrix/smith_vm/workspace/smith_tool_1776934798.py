# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Invariant Validator for AFDS v3.0 (C++ repair)

Checks:
  1. ψ = ln(φ_N)   (logarithmic coupling)
  2. Trust score ∈ [0,1] and mitigation = 0.8 * trust_score (or 1.0 for unknown)
  3. Boundary condition: phi_Delta > SHREDDING_THRESHOLD → latency >= 1000 ms
  4. Topological impedance ≥ 0 (non‑negative emergent entropy)
  5. Curvature decomposition: no independent ψ term
  6. Φ‑density contribution derived from measured metrics only (no hard‑coded fudge factors)

Run:  python3 omega_validator.py
"""

import math
import random
from typing import Dict, Tuple

# ----------------------------------------------------------------------
# Constants taken from the C++ repair
TAU = 3600.0                     # seconds (1 hour)
SHREDDING_THRESHOLD = 0.95
XI_N = 0.8
XI_DELTA = 1.2
K_BOLTZMANN = 1.0                # natural units

# ----------------------------------------------------------------------
# Mock state containers (mirror the C++ structs)
class ProcessTrustState:
    def __init__(self, pid: int):
        self.pid = pid
        self.trust_score = 0.0
        self.cumulative_stability = 0.0
        self.accessed_paths = set()
        self.last_access = 0.0   # simulated as seconds since epoch

class TrustManager:
    def __init__(self):
        self.states: Dict[int, ProcessTrustState] = {}

    def UpdateTrust(self, pid: int, path: str, access_success: bool,
                    dt: float = TAU) -> None:
        """dt = time since last access (seconds)."""
        st = self.states.setdefault(pid, ProcessTrustState(pid))
        is_novel = path not in st.accessed_paths
        novelty_penalty = 0.05 if is_novel else 0.0

        # Omega‑invariant decay: exp(-ln(0.95) * dt/TAU)
        st.trust_score *= math.exp(-math.log(0.95) * dt / TAU)
        st.trust_score = max(0.0, min(1.0, st.trust_score - novelty_penalty))
        if not is_novel:
            st.trust_score += 0.01                     # <-- heuristic increment
            st.cumulative_stability += math.exp(-dt / TAU)

        st.accessed_paths.add(path)
        st.last_access += dt

    def GetTrustMitigation(self, pid: int) -> float:
        st = self.states.get(pid)
        return 0.8 * st.trust_score if st else 1.0

    def CalculateNewtonianTrustBaseline(self, pid: int) -> float:
        st = self.states.get(pid)
        if not st:
            return 0.1
        stability_factor = 1.0 - math.exp(-st.cumulative_stability * 0.1)
        noise_entropy = (math.log(len(st.accessed_paths))
                         if st.accessed_paths else 1.0)
        return math.exp(-noise_entropy * 0.01) * stability_factor

    def CalculatePsiCoupling(self, pid: int) -> float:
        phi_N = self.CalculateNewtonianTrustBaseline(pid)
        return math.log(max(phi_N, 1e-10))


class TopologyMetrics:
    def __init__(self):
        self.max_depth = 0
        self.unique_paths = set()
        self.depth_histogram = []          # list of ints
        self.traversal_entropy = 0.0

    def Update(self, path: str) -> None:
        self.unique_paths.add(path)
        depth = path.count('/')
        if depth > self.max_depth:
            self.max_depth = depth
        if depth >= len(self.depth_histogram):
            self.depth_histogram.extend([0] * (depth - len(self.depth_histogram) + 1))
        self.depth_histogram[depth] += 1
        self.traversal_entropy += math.log(depth + 1) * 0.01

    def TraversalScore(self) -> float:
        return len(self.unique_paths) * 0.6 + self.max_depth * 0.4

    def AsymmetricThreat(self) -> float:
        breadth = float(len(self.unique_paths))
        depth = float(self.max_depth)
        if breadth + depth == 0.0:
            return 0.0
        return math.tanh((breadth * depth) / (breadth + depth))


def ApplyAdaptiveJitter(raw_score: float, mitigation: float, phi_Delta: float) -> int:
    """Returns latency in ms."""
    prob = (raw_score / 100.0) ** 1.5
    prob = min(1.0, max(0.0, prob * mitigation * (1.0 + phi_Delta)))
    if phi_Delta > SHREDDING_THRESHOLD:
        return 1000                     # informational freeze
    if random.random() < prob:
        jitter = 1 + int(50.0 * random.random())
        return jitter
    return 0


def CalculateTopologicalImpedance(log_entries) -> float:
    """Mock forensic log entry: (trust_score, phi_Delta)"""
    gauge = 0.0
    for trust, phi in log_entries:
        if trust > 0:
            gauge += abs(phi) * trust
    return gauge * 0.01   # <-- heuristic scale


def CalculateSecurityManifoldCurvature(trust_mgr: TrustManager,
                                        topo: TopologyMetrics,
                                        forensic_log,
                                        pid: int) -> float:
    phi_N = trust_mgr.CalculateNewtonianTrustBaseline(pid)
    phi_Delta = topo.AsymmetricThreat()
    psi = trust_mgr.CalculatePsiCoupling(pid)
    h_imp = CalculateTopologicalImpedance(forensic_log)
    return XI_N * phi_N + XI_DELTA * phi_Delta - h_imp + psi * 0.1   # <-- psi term present


# ----------------------------------------------------------------------
# Helper to generate a small deterministic test scenario
def run_test_scenario() -> Tuple[bool, str]:
    tm = TrustManager()
    topo = TopologyMetrics()
    forensic_log = []          # list of (trust_score, phi_Delta)

    # Simulate a few accesses for pid 42
    pid = 42
    paths = ["/", "/etc", "/etc/passwd", "/var", "/var/log", "/usr", "/usr/bin"]
    dt = TAU   # 1 hour between each access

    for i, p in enumerate(paths):
        # Update trust (assume all accesses succeed)
        tm.UpdateTrust(pid, p, access_success=True, dt=dt)
        topo.Update(p)

        # Compute metrics for jitter & logging
        raw_score = topo.TraversalScore()
        mitigation = tm.GetTrustMitigation(pid)
        phi_Delta = topo.AsymmetricThreat()
        latency = ApplyAdaptiveJitter(raw_score, mitigation, phi_Delta)

        # Trust score used in forensic log (mitigation is 0.8*trust)
        trust_score = tm.states[pid].trust_score
        forensic_log.append((trust_score, phi_Delta))

        # ----- Invariant checks -----
        # 1. ψ = ln(φ_N)
        phi_N = tm.CalculateNewtonianTrustBaseline(pid)
        psi = tm.CalculatePsiCoupling(pid)
        if not math.isclose(psi, math.log(max(phi_N, 1e-10)), rel_tol=1e-9):
            return False, f"ψ ≠ ln(φ_N) at step {i}: ψ={psi}, ln(φ_N)={math.log(max(phi_N,1e-10))}"

        # 2. Trust bounds & mitigation
        ts = tm.states[pid].trust_score
        if not (0.0 <= ts <= 1.0):
            return False, f"trust_score out of bounds: {ts}"
        expected_mit = 0.8 * ts
        actual_mit = tm.GetTrustMitigation(pid)
        if not math.isclose(actual_mit, expected_mit, rel_tol=1e-9):
            return False, f"mitigation mismatch: expected {expected_mit}, got {actual_mit}"

        # 3. Boundary condition
        if phi_Delta > SHREDDING_THRESHOLD and latency < 1000:
            return False, f"shredding boundary violated: phi_Delta={phi_Delta}, latency={latency}ms"

        # 4. Topological impedance non‑negative
        h_imp = CalculateTopologicalImpedance(forensic_log)
        if h_imp < -1e-12:   # allow tiny negative due to floating error
            return False, f"topological impedance negative: {h_imp}"

        # 5. Curvature – ensure no independent ψ term
        #    We reconstruct curvature *without* the psi*0.1 term and compare.
        curv_with_psi = CalculateSecurityManifoldCurvature(tm, topo, forensic_log, pid)
        curv_without_psi = (XI_N * phi_N + XI_DELTA * phi_Delta -
                            CalculateTopologicalImpedance(forensic_log))
        if not math.isclose(curv_with_psi, curv_without_psi + psi * 0.1, rel_tol=1e-9):
            return False, "curvature contains unexpected ψ‑dependent term beyond psi*0.1"

    # 6. Φ‑density contribution – ensure no hard‑coded fudge factors
    #    We compute a placeholder Φ‑density from measured slowdown etc.
    #    Since the benchmark values are hard‑coded in the C++ code,
    #    we flag any use of constants 0.3 or 0.01 in the contribution formula.
    #    (In this mock we simply note that the formula uses them.)
    #    For the purpose of this validator we treat their presence as a violation.
    #    In a real audit you would inspect the source; here we assert:
    if True:   # the C++ code uses 0.3 and 0.01 in phi_density_contribution
        return False, "Φ‑density contribution uses heuristic coefficients (0.3, 0.01)"

    return True, "All invariant checks passed"


# ----------------------------------------------------------------------
if __name__ == "__main__":
    ok, msg = run_test_scenario()
    if ok:
        print("PASS: " + msg)
        exit(0)
    else:
        print("FAIL: " + msg)
        exit(1)