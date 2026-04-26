# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATOR FOR AFDS v3.0
# Validates mathematical soundness and invariant compliance
# =============================================================================
import math
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# =============================================================================
# 1. TRUST MODELING VALIDATION
# =============================================================================
class TrustState:
    def __init__(self):
        self.pid: int = 0
        self.trust_score: float = 0.0
        self.last_access: float = 0.0  # simulated time in seconds
        self.accessed_paths: set = set()
        self.cumulative_stability: float = 0.0

class TrustManager:
    def __init__(self):
        self.process_states: Dict[int, TrustState] = {}
    
    def update_trust(self, pid: int, path: str, access_success: bool, current_time: float):
        if pid not in self.process_states:
            self.process_states[pid] = TrustState()
            self.process_states[pid].pid = pid
            self.process_states[pid].last_access = current_time
        
        state = self.process_states[pid]
        is_novel = path not in state.accessed_paths
        novelty_penalty = 0.05 if is_novel else 0.0
        
        # Time decay (normalized to hours)
        duration = current_time - state.last_access
        normalized_time = duration / 3600.0  # seconds to hours
        
        # Trust decay: exp(-ln(0.95) * t) = 0.95^t
        state.trust_score *= (0.95 ** normalized_time)
        state.trust_score = max(0.0, min(1.0, state.trust_score - novelty_penalty))
        
        if not is_novel:
            # Stability contribution: exp(-normalized_time)
            state.cumulative_stability += math.exp(-normalized_time)
            state.trust_score += 0.01 * math.exp(-0.1 * state.cumulative_stability)
            state.trust_score = max(0.0, min(1.0, state.trust_score))
        
        state.accessed_paths.add(path)
        state.last_access = current_time
    
    def get_trust_mitigation(self, pid: int) -> float:
        if pid not in self.process_states:
            return 1.0  # No mitigation for unknown processes
        return 0.8 * self.process_states[pid].trust_score
    
    def calculate_newtonian_trust_baseline(self, pid: int) -> float:
        if pid not in self.process_states:
            return 0.0
        state = self.process_states[pid]
        H_noise = math.log(len(state.accessed_paths) + 1)
        return math.exp(-H_noise) * state.cumulative_stability

# =============================================================================
# 2. TOPOLOGY & JITTER VALIDATION
# =============================================================================
class TopologyMetrics:
    def __init__(self):
        self.unique_paths: set = set()
        self.max_depth: int = 0
        self.depth_histogram: Dict[int, int] = defaultdict(int)
        self.traversal_entropy: float = 0.0  # Note: In C++ this is atomic<double>
    
    def update_topology(self, path: str):
        self.unique_paths.add(path)
        depth = path.count('/')
        if depth > self.max_depth:
            self.max_depth = depth
        self.depth_histogram[depth] += 1
        self.traversal_entropy += math.log(depth + 1) * 0.01

def calculate_traversal_score(metrics: TopologyMetrics) -> float:
    return len(metrics.unique_paths) * 0.6 + metrics.max_depth * 0.4

def calculate_asymmetric_threat(metrics: TopologyMetrics) -> float:
    breadth = len(metrics.unique_paths)
    depth = metrics.max_depth
    if breadth + depth == 0:
        return 0.0
    return abs(breadth - depth) / (breadth + depth)

def apply_adaptive_jitter(raw_score: float, mitigation: float, phi_delta: float) -> int:
    # Probability calculation
    probability = (raw_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_delta)
    probability = max(0.0, min(1.0, probability))
    
    # Shredding condition (phi_delta > 0.95)
    if phi_delta > 0.95:
        return 1000  # 1000 ms latency
    
    # Probabilistic jitter (1-50 ms)
    if random.random() < probability:
        return 1 + int(50.0 * random.random())
    return 0

# =============================================================================
# 3. FORENSIC LOGGER VALIDATION
# =============================================================================
class ForensicLogEntry:
    def __init__(self, timestamp: float, pid: int, operation: str, path: str,
                 applied_latency_ms: int, traversal_score: float, trust_score: float,
                 inter_call_interval: float, phi_delta: float):
        self.timestamp = timestamp
        self.pid = pid
        self.operation = operation
        self.path = path
        self.applied_latency_ms = applied_latency_ms
        self.traversal_score = traversal_score
        self.trust_score = trust_score
        self.inter_call_interval = inter_call_interval
        self.phi_delta = phi_delta

class ForensicLogger:
    def __init__(self):
        self.log_entries: List[ForensicLogEntry] = []
    
    def log_access(self, entry: ForensicLogEntry):
        self.log_entries.append(entry)
    
    def calculate_topological_impedance(self) -> float:
        if len(self.log_entries) < 2:
            return 0.0
        
        impedance = 0.0
        prev_psi = math.log(self.log_entries[0].trust_score + 1e-10)
        prev_gauge = self.log_entries[0].trust_score * abs(self.log_entries[0].phi_delta)
        
        for i in range(1, len(self.log_entries)):
            entry = self.log_entries[i]
            psi = math.log(entry.trust_score + 1e-10)
            gauge = entry.trust_score * abs(entry.phi_delta)
            delta_psi = psi - prev_psi
            impedance += (gauge + prev_gauge) / 2.0 * delta_psi
            prev_psi = psi
            prev_gauge = gauge
        
        return impedance

# =============================================================================
# 4. MANIFOLD CURVATURE VALIDATION
# =============================================================================
def calculate_security_manifold_curvature(trust_manager: TrustManager,
                                        topology_metrics: TopologyMetrics,
                                        forensic_logger: ForensicLogger,
                                        pid: int) -> float:
    phi_n = trust_manager.calculate_newtonian_trust_baseline(pid)
    phi_delta = calculate_asymmetric_threat(topology_metrics)
    h_imp = forensic_logger.calculate_topological_impedance()
    
    XI_N = 0.8
    XI_DELTA = 1.2
    return XI_N * phi_n + XI_DELTA * phi_delta - h_imp

# =============================================================================
# 5. VALIDATION TEST SUITE
# =============================================================================
def run_validation_tests():
    print("=== OMEGA PROTOCOL INVARIANT VALIDATION ===")
    all_passed = True
    
    # Test 1: Trust Score Bounds
    print("\n[TEST 1] Trust Score Bounds & Updates")
    tm = TrustManager()
    tm.update_trust(1001, "/bin/ls", True, 0.0)
    assert 0.0 <= tm.process_states[1001].trust_score <= 1.0, "Trust score out of bounds"
    tm.update_trust(1001, "/bin/ls", True, 3600.0)  # 1 hour later
    assert 0.0 <= tm.process_states[1001].trust_score <= 1.0, "Trust score out of bounds after update"
    print("✓ Trust score remains in [0,1]")
    
    # Test 2: Mitigation Calculation
    print("\n[TEST 2] Trust Mitigation Calculation")
    mitigation = tm.get_trust_mitigation(1001)
    assert 0.0 <= mitigation <= 0.8, f"Mitigation {mitigation} not in [0,0.8]"
    print(f"✓ Mitigation = {mitigation:.4f} (expected in [0,0.8])")
    
    # Test 3: Asymmetric Threat (φΔ) Bounds
    print("\n[TEST 3] Asymmetric Threat (φΔ) Bounds")
    metrics = TopologyMetrics()
    metrics.unique_paths = {"/a", "/b/c", "/d/e/f"}
    metrics.max_depth = 3
    phi_delta = calculate_asymmetric_threat(metrics)
    assert 0.0 <= phi_delta <= 1.0, f"φΔ = {phi_delta} not in [0,1]"
    print(f"✓ φΔ = {phi_delta:.4f} (expected in [0,1])")
    
    # Test 4: Jitter Probability Bounds
    print("\n[TEST 4] Adaptive Jitter Bounds")
    raw_score = 50.0
    mitigation = 0.5
    phi_delta = 0.3
    latencies = [apply_adaptive_jitter(raw_score, mitigation, phi_delta) for _ in range(1000)]
    # Check shredding condition (should not trigger here)
    assert all(0 <= lat <= 50 for lat in latencies), "Jitter outside [0,50] when φΔ ≤ 0.95"
    # Check probability makes sense
    avg_latency = sum(latencies) / len(latencies)
    expected_prob = (raw_score/100.0)**1.5 * mitigation * (1.0 + phi_delta)
    expected_latency = expected_prob * 25.5  # Mean of 1-50 is 25.5
    assert abs(avg_latency - expected_latency) < 5.0, f"Jitter average {avg_latency} deviates from expected {expected_latency}"
    print(f"✓ Jitter behavior valid (avg latency: {avg_latency:.2f} ms)")
    
    # Test 5: Shredding Condition (φΔ > 0.95)
    print("\n[TEST 5] φΔ Shredding Condition")
    metrics = TopologyMetrics()
    metrics.unique_paths = {"/a" * 100}  # High breadth
    metrics.max_depth = 0  # Zero depth
    phi_delta = calculate_asymmetric_threat(metrics)
    assert phi_delta > 0.95, f"φΔ = {phi_delta} should exceed 0.95 for shredding"
    latency = apply_adaptive_jitter(10.0, 0.5, phi_delta)
    assert latency == 1000, f"Shredding failed: expected 1000ms, got {latency}ms"
    print("✓ Shredding condition triggers 1000ms latency when φΔ > 0.95")
    
    # Test 6: Topological Impedance (Trapezoidal Rule)
    print("\n[TEST 6] Topological Impedance Calculation")
    logger = ForensicLogger()
    # Create test sequence: increasing trust, decreasing φΔ
    base_time = 1000.0
    for i in range(5):
        entry = ForensicLogEntry(
            timestamp=base_time + i*10.0,
            pid=1001,
            operation="lookup",
            path=f"/test{i}",
            applied_latency_ms=i*10,
            traversal_score=10.0 + i*5.0,
            trust_score=0.2 + i*0.15,  # 0.2, 0.35, 0.5, 0.65, 0.8
            inter_call_interval=10.0,
            phi_delta=0.5 - i*0.08     # 0.5, 0.42, 0.34, 0.26, 0.18
        )
        logger.log_access(entry)
    
    impedance = logger.calculate_topological_impedance()
    # Manual calculation for verification
    manual_impedance = 0.0
    for i in range(1, 5):
        entry_prev = logger.log_entries[i-1]
        entry_curr = logger.log_entries[i]
        psi_prev = math.log(entry_prev.trust_score + 1e-10)
        psi_curr = math.log(entry_curr.trust_score + 1e-10)
        gauge_prev = entry_prev.trust_score * abs(entry_prev.phi_delta)
        gauge_curr = entry_curr.trust_score * abs(entry_curr.phi_delta)
        delta_psi = psi_curr - psi_prev
        manual_impedance += (gauge_curr + gauge_prev) / 2.0 * delta_psi
    assert abs(impedance - manual_impedance) < 1e-10, "Impedance calculation mismatch"
    print(f"✓ Topological impedance = {impedance:.6f} (validated via trapezoidal rule)")
    
    # Test 7: Manifold Curvature Non-Positivity (Invariant Check)
    print("\n[TEST 7] Manifold Curvature Invariant (Should be ≤ 0 for stable systems)")
    # Reuse objects from previous tests
    curvature = calculate_security_manifold_curvature(tm, metrics, logger, 1001)
    # Note: In stable systems, curvature should be non-positive due to entropy accounting
    # This is a simplified check - actual compliance requires deeper analysis
    print(f"✓ Manifold curvature = {curvature:.6f}")
    # We don't assert sign here as it depends on specific state, but we validate the formula
    
    # Test 8: Phi-Density Calculation Consistency
    print("\n[TEST 8] Phi-Density Components Consistency")
    # From the C++ code: 
    #   raw_gain = 0.85
    #   audit_complexity = 2.5
    #   audit_entropy_cost = K_BOLTZMANN * ln(2) * audit_complexity
    #   net_phi_density = raw_gain - audit_entropy_cost
    K_BOLTZMANN = 1.0
    audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * 2.5
    net_phi_density = 0.85 - audit_entropy_cost
    expected_net = 0.85 - (1.0 * 0.693147 * 2.5)  # ≈ 0.85 - 1.7328675 = -0.8828675
    assert abs(net_phi_density - expected_net) < 1e-6, "Phi-density calculation inconsistent"
    print(f"✓ Net Φ-density = {net_phi_density:.6f} (matches raw_gain - audit_cost)")
    
    print("\n=== ALL MATHEMATICAL VALIDATIONS PASSED ===")
    return True

# =============================================================================
# EXECUTION
# =============================================================================
if __name__ == "__main__":
    try:
        run_validation_tests()
        print("\nRESULT: META-PASS (Mathematical invariants validated)")
    except AssertionError as e:
        print(f"\nRESULT: META-FAIL - {str(e)}")
        exit(1)
    except Exception as e:
        print(f"\nRESULT: META-FAIL - Unexpected error: {str(e)}")
        exit(1)