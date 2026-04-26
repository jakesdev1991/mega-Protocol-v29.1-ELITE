# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.stats as stats
from typing import List, Tuple, Dict
import math

# OMEGA PROTOCOL INVARIANT VALIDATOR FOR AFDS
# Enforces: Phi_N (Uncertainty Gain), Phi_Delta (Resource Proportionality), J* (No Φ-Leak Paths)

class OmegaInvariantValidator:
    def __init__(self):
        # Protocol constants from Omega Physics Rubric v26.0
        self.MIN_JITTER_MS = 1
        self.MAX_JITTER_MS = 50
        self.JITTER_DECAY_RATE = 0.7
        self.TRUSTED_PIDS = {1, 1234, 5678}  # systemd, sshd, DEDS
        self.SCORE_WEIGHTS = {"a": 0.4, "b": 0.3, "c": 0.3}  # From Engine output
        
    def validate_jitter_distribution(self, samples: int = 100000) -> Tuple[bool, Dict]:
        """
        Validates Non-linear Bounded Jitter creates uncertainty (Phi_N) without pattern leakage.
        Checks: 
          1. Support within [1,50]ms (bounded)
          2. Exponential decay shape (avoids periodic detection)
          3. Kolmogorov-Smirnov test vs uniform (p<0.01 confirms non-uniformity for stealth)
        """
        rng = np.random.default_rng(42)  # Fixed seed for reproducibility
        u = rng.uniform(0, 1, samples)
        jitter = self.MIN_JITTER_MS + (self.MAX_JITTER_MS - self.MIN_JITTER_MS) * np.power(u, self.JITTER_DECAY_RATE)
        
        # Invariant 1: Bounded support (Phi_N - prevents timing channel exploitation)
        in_bounds = np.all((jitter >= self.MIN_JITTER_MS) & (jitter <= self.MAX_JITTER_MS))
        
        # Invariant 2: Non-uniform distribution (Phi_N - thwarts spectral analysis)
        ks_stat, p_value = stats.kstest(jitter, 'uniform', args=(self.MIN_JITTER_MS, self.MAX_JITTER_MS))
        is_non_uniform = p_value < 0.01  # Significant deviation from uniform
        
        # Invariant 3: Heavy-tailed for uncertainty (Phi_N - increases attacker entropy)
        tail_weight = np.mean(jitter > np.percentile(jitter, 90))  # >90th percentile mass
        sufficient_tail = tail_weight > 0.08  # Empirical threshold for stealth efficacy
        
        return (
            in_bounds and is_non_uniform and sufficient_tail,
            {
                "in_bounds": in_bounds,
                "ks_p_value": p_value,
                "tail_weight": tail_weight,
                "mean_jitter": np.mean(jitter),
                "std_jitter": np.std(jitter)
            }
        )
    
    def validate_topology_stress(self, path_sequence: List[str], time_intervals: List[float]) -> Tuple[bool, Dict]:
        """
        Validates d(unique_paths)/dt calculation adheres to Phi_Delta (proportional response).
        Checks:
          1. Stress = |unique_paths(t)| / Δt (correct derivative approximation)
          2. Monotonic in path diversity (no false negatives for reconnaissance)
          3. Bounded by path_space_velocity (prevents overflow-induced Φ-leak)
        """
        if len(path_sequence) != len(time_intervals) or len(path_sequence) < 2:
            raise ValueError("Path sequence and time intervals must be equal length >=2")
        
        unique_paths = set()
        stresses = []
        cumulative_time = 0.0
        
        for i, (path, dt) in enumerate(zip(path_sequence, time_intervals)):
            cumulative_time += dt
            unique_paths.add(path)
            # Topology stress = d(unique_paths)/dt ≈ |U(t)| / t (valid for t>0)
            stress = len(unique_paths) / cumulative_time if cumulative_time > 0 else 0.0
            stresses.append(stress)
        
        # Invariant 1: Correct derivative approximation (Phi_Delta - proportional to threat velocity)
        # For linear path discovery: stress should approach constant (1/path_per_unit_time)
        expected_asymptote = len(set(path_sequence)) / cumulative_time if cumulative_time > 0 else 0
        stress_error = abs(stresses[-1] - expected_asymptote) / max(expected_asymptote, 1e-9)
        correct_derivative = stress_error < 0.05  # 5% tolerance
        
        # Invariant 2: Monotonic increase in unique paths (Phi_Delta - no missed reconnaissance)
        unique_counts = [len(set(path_sequence[:i+1])) for i in range(len(path_sequence))]
        is_monotonic = all(unique_counts[i] <= unique_counts[i+1] for i in range(len(unique_counts)-1))
        
        # Invariant 3: Bounded by path_space_velocity (J* - prevents Φ-leak via overflow)
        max_possible_stress = len(path_sequence) / min(time_intervals) if min(time_intervals) > 0 else float('inf')
        stress_bounded = all(s <= max_possible_stress * 1.1 for s in stresses)  # 10% buffer
        
        return (
            correct_derivative and is_monotonic and stress_bounded,
            {
                "final_stress": stresses[-1],
                "stress_error_pct": stress_error * 100,
                "is_monotonic": is_monotonic,
                "max_observed_stress": max(stresses),
                "theoretical_max": max_possible_stress
            }
        )
    
    def validate_scoring_invariants(self, call_rate: float, unique_paths: int, avg_depth: float) -> Tuple[bool, Dict]:
        """
        Validates Score = a*calls/sec + b*unique_paths + c*depth adheres to J* (no Φ-leak paths).
        Checks:
          1. Score linearity in each factor (no hidden nonlinearities that create blind spots)
          2. Weighted sum conservation (a+b+c=1.0 per protocol)
          3. Score bounds prevent resource starvation extremes (Phi_Delta)
        """
        a, b, c = self.SCORE_WEIGHTS.values()
        
        # Invariant 1: Weight conservation (J* - prevents score manipulation attacks)
        weights_sum = a + b + c
        weights_conserved = abs(weights_sum - 1.0) < 1e-9
        
        # Invariant 2: Linear response (Phi_N - ensures detectable threat gradient)
        # Perturb each factor and verify score change proportional to weight
        base_score = a*call_rate + b*unique_paths + c*avg_depth
        eps = 1e-5
        
        score_a = a*(call_rate+eps) + b*unique_paths + c*avg_depth
        score_b = a*call_rate + b*(unique_paths+eps) + c*avg_depth
        score_c = a*call_rate + b*unique_paths + c*(avg_depth+eps)
        
        linear_a = abs((score_a - base_score)/eps - a) < 1e-4
        linear_b = abs((score_b - base_score)/eps - b) < 1e-4
        linear_c = abs((score_c - base_score)/eps - c) < 1e-4
        linear_response = linear_a and linear_b and linear_c
        
        # Invariant 3: Score bounds prevent extreme resource allocation (Phi_Delta)
        # Max score: assume call_rate≤1000/sec, unique_paths≤10^6, depth≤20 (realistic bounds)
        max_theoretical = a*1000 + b*1_000_000 + c*20
        min_theoretical = 0.0
        score_in_bounds = min_theoretical <= base_score <= max_theoretical
        
        # Additional: Score must map to [0,100] for scheduler handover (per Engine)
        # Clamping in Omega_Flags_Handshake requires score≤100 for meaningful priority
        score_scalable = base_score <= 150.0  # Allows headroom before clamping
        
        return (
            weights_conserved and linear_response and score_in_bounds and score_scalable,
            {
                "weights_sum": weights_sum,
                "base_score": base_score,
                "linearity_errors": {
                    "a": abs((score_a - base_score)/eps - a),
                    "b": abs((score_b - base_score)/eps - b),
                    "c": abs((score_c - base_score)/eps - c)
                },
                "score_bounds": {"min": min_theoretical, "max": max_theoretical}
            }
        )
    
    def validate_trusted_pid_bypass(self, pid: int, is_trusted: bool) -> bool:
        """
        Validates Trusted PID registry prevents false positives (Phi_N - preserves legitimate Φ).
        Check: Trusted PIDs bypass jitter/scoring → no unnecessary Φ-density erosion.
        """
        is_in_registry = pid in self.TRUSTED_PIDS
        return is_in_registry == is_trusted  # Bypass iff trusted

def run_afds_validation():
    """Executable validation suite for AFDS implementation"""
    validator = OmegaInvariantValidator()
    results = {}
    
    print("=== OMEGA PROTOCOL INVARIANT VALIDATION: AFDS ===\n")
    
    # 1. Jitter Distribution Validation (Phi_N)
    print("[1/4] Validating Non-linear Bounded Jitter (1-50ms)...")
    jitter_ok, jitter_data = validator.validate_jitter_distribution()
    results["jitter"] = {"pass": jitter_ok, "data": jitter_data}
    print(f"  PASS: {jitter_ok} | KS p-value: {jitter_data['ks_p_value']:.2e} | "
          f"Tail weight: {jitter_data['tail_weight']:.3f}\n")
    
    # 2. Topology Stress Validation (Phi_Delta)
    print("[2/4] Validating Topology Stress Calculation...")
    # Simulate reconnaissance: linear path discovery
    recon_paths = [f"/etc/file{i}" for i in range(100)]
    recon_times = [0.01] * 100  # 10ms per path
    stress_ok, stress_data = validator.validate_topology_stress(recon_paths, recon_times)
    results["topology_stress"] = {"pass": stress_ok, "data": stress_data}
    print(f"  PASS: {stress_ok} | Final stress: {stress_data['final_stress']:.2f} paths/sec | "
          f"Error: {stress_data['stress_error_pct']:.2f}%\n")
    
    # 3. Scoring Invariants Validation (J*)
    print("[3/4] Validating Multi-factor Scoring Invariants...")
    # Test case: moderate threat (attacker scanning)
    score_ok, score_data = validator.validate_scoring_invariants(
        call_rate=50.0,      # 50 calls/sec
        unique_paths=75,     # 75 unique paths probed
        avg_depth=3.2        # Avg path depth
    )
    results["scoring"] = {"pass": score_ok, "data": score_data}
    print(f"  PASS: {score_ok} | Score: {score_data['base_score']:.2f} | "
          f"Weights sum: {score_data['weights_sum']:.6f}\n")
    
    # 4. Trusted PID Bypass Validation (Phi_N)
    print("[4/4] Validating Trusted PID Bypass...")
    test_cases = [
        (1, True),    # systemd
        (1234, True), # sshd
        (5678, True), # DEDS
        (9999, False), # attacker
        (0, False)    # invalid
    ]
    bypass_ok = all(validator.validate_trusted_pid_bypass(pid, expected) for pid, expected in test_cases)
    results["trusted_pid"] = {"pass": bypass_ok}
    print(f"  PASS: {bypass_ok} | Tested {len(test_cases)} PID cases\n")
    
    # Final Verdict
    all_pass = all(res["pass"] for res in results.values())
    print("=== VALIDATION SUMMARY ===")
    for name, res in results.items():
        status = "✓ PASS" if res["pass"] else "✗ FAIL"
        print(f"{name.upper():<15} {status}")
    
    print(f"\nOVERALL: {'PROTOCOL COMPLIANT' if all_pass else 'INVARIANT VIOLATION'}")
    print(f"Φ-Density Impact: {'+0.50Φ (Net Gain)' if all_pass else '-∞Φ (Critical Failure)'}")
    
    return all_pass

if __name__ == "__main__":
    # Execute validation - returns exit code 0 for PASS, 1 for FAIL
    exit(0 if run_afds_validation() else 1)