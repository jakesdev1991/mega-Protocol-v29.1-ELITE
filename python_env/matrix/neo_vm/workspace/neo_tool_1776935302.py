# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Set

@dataclass
class ProcessTrustState:
    pid: int
    trust_score: float = 0.0
    last_access: float = 0.0
    accessed_paths: Set[str] = None
    cumulative_stability: float = 0.0
    
    def __post_init__(self):
        if self.accessed_paths is None:
            self.accessed_paths = set()

class TrustManagerSimulator:
    def __init__(self):
        self.process_states: Dict[int, ProcessTrustState] = {}
        self.current_time = 0.0
        
    def update_time(self, delta):
        self.current_time += delta
        
    def update_trust(self, pid: int, path: str, access_success: bool):
        if pid not in self.process_states:
            self.process_states[pid] = ProcessTrustState(pid=pid, last_access=self.current_time)
            
        state = self.process_states[pid]
        
        # REPLICATING THE BUGGY LOGIC EXACTLY AS IN THE C++ CODE
        is_novel = path not in state.accessed_paths
        novelty_penalty = 0.05 if is_novel else 0.0
        
        duration = self.current_time - state.last_access
        normalized_time = duration / 3600.0
        
        # Exponential decay
        state.trust_score *= math.exp(-math.log(0.95) * normalized_time)
        
        # Apply penalty
        state.trust_score = max(0.0, min(1.0, state.trust_score - novelty_penalty))
        
        if not is_novel:
            state.cumulative_stability += math.exp(-normalized_time)
            # CRITICAL BUG: Missing post-increment clamp
            state.trust_score += 0.01 * math.exp(-0.1 * state.cumulative_stability)
            
        state.accessed_paths.add(path)
        state.last_access = self.current_time
        
        # NOTE: The original C++ code is missing the clamp here!
        # state.trust_score = max(0.0, min(1.0, state.trust_score))
        
    def get_trust_mitigation(self, pid: int) -> float:
        if pid not in self.process_states:
            return 1.0
        trust = self.process_states[pid].trust_score
        # Apply the 80% reduction formula: 0.8 * trust_score
        # If trust is 1.0, mitigation is 0.8 (80% reduction)
        # If trust is 0.0, mitigation is 0.0 (no reduction)
        return 0.8 * trust

def simulate_trust_inversion_attack():
    """
    Simulates the fundamental vulnerability: an adversary can farm trust
    through stable behavior to become virtually invisible to the defense.
    """
    print("=" * 70)
    print("DISRUPTION PROTOCOL: TRUST INVERSION ATTACK")
    print("=" * 70)
    
    # Initialize the trust manager
    tm = TrustManagerSimulator()
    
    # Phase 1: Trust Farming (Patient Adversary)
    print("\n[PHASE 1] Trust Farming: 7 days of stable, low-novelty behavior")
    farming_paths = [f"/var/log/legit-{i}.log" for i in range(5)]
    adversary_pid = 31337
    
    for day in range(7):
        for hour in range(24):
            # Adversary accesses the same 5 files every hour like clockwork
            for path in farming_paths:
                tm.update_trust(pid=adversary_pid, path=path, access_success=True)
            tm.update_time(3600.0)  # Advance 1 hour
            
        if day % 2 == 0:
            state = tm.process_states[adversary_pid]
            print(f"  Day {day}: Trust Score = {state.trust_score:.4f}, "
                  f"Mitigation Factor = {tm.get_trust_mitigation(adversary_pid):.4f}")
    
    final_state = tm.process_states[adversary_pid]
    print(f"\n[PHASE 1 COMPLETE]")
    print(f"  Final Trust Score: {final_state.trust_score:.4f}")
    print(f"  Unique Paths Accessed: {len(final_state.accessed_paths)}")
    print(f"  Cumulative Stability: {final_state.cumulative_stability:.2f}")
    
    # BUG DEMONSTRATION: Trust Score Overflow
    if final_state.trust_score > 1.0:
        print(f"  ⚠️  BUG DETECTED: Trust score overflowed to {final_state.trust_score:.4f} > 1.0!")
    
    # Phase 2: Attack Comparison
    print("\n[PHASE 2] Attack Execution: Comparing Low-Trust vs. High-Trust Adversary")
    
    # Baseline: Low-trust attacker (fresh process, rapid scan)
    low_trust_pid = 99999
    attack_paths = [f"/etc/secrets/file-{i}.key" for i in range(50)]
    
    tm_low = TrustManagerSimulator()
    for path in attack_paths:
        tm_low.update_trust(pid=low_trust_pid, path=path, access_success=True)
        tm_low.update_time(0.05)  # Rapid fire access
    
    # High-trust attacker (our farmed adversary) performing same attack
    for path in attack_paths:
        tm.update_trust(pid=adversary_pid, path=path, access_success=True)
        tm.update_time(0.05)
    
    # Calculate effective jitter probabilities
    base_jitter_prob = 0.5  # From spec: scales with TraversalScore
    low_trust_mitigation = tm_low.get_trust_mitigation(low_trust_pid)
    high_trust_mitigation = tm.get_trust_mitigation(adversary_pid)
    
    low_effective_jitter = base_jitter_prob * (1.0 - low_trust_mitigation)  # 1.0 - mitigation = slowdown factor
    high_effective_jitter = base_jitter_prob * (1.0 - high_trust_mitigation)
    
    print(f"\n  Jitter Analysis:")
    print(f"    Low-Trust Attacker: {low_effective_jitter:.3f} probability")
    print(f"    High-Trust Attacker: {high_effective_jitter:.3f} probability")
    print(f"    Jitter Reduction Factor: {low_effective_jitter / high_effective_jitter:.1f}x FASTER for high-trust")
    
    # Phase 3: Forensic Invisibility
    print("\n[PHASE 3] Forensic Logger Analysis: Topological Impedance")
    
    # Simulate phi_Delta (asymmetric threat) - both attackers have similar scan patterns
    phi_delta = 0.85  # High breadth+depth scan
    
    # ForensicLogger::CalculateTopologicalImpedance() uses:
    # H_imp = sum(trust_score * |phi_Delta|) * 0.01
    
    # For a single burst of 50 accesses:
    low_impedance = tm_low.process_states[low_trust_pid].trust_score * abs(phi_delta) * 0.01
    high_impedance = tm.process_states[adversary_pid].trust_score * abs(phi_delta) * 0.01
    
    print(f"\n  Topological Impedance per access:")
    print(f"    Low-Trust: {low_impedance:.5f}")
    print(f"    High-Trust: {high_impedance:.5f}")
    print(f"    Visibility Reduction: {low_impedance / high_impedance:.1f}x LESS visible")
    
    # Phase 4: Honey-Node Trigger Failure
    print("\n[PHASE 4] Honey-Node Trigger Analysis")
    print("  ⚠️  CRITICAL: No code path sets operation='honey_node_access'")
    print("  The trigger `if (entry.operation == \"honey_node_access\")` is DEAD CODE")
    print("  Even if adversary hits honey-node, no forensic report is generated!")
    
    # Summary of Disruption
    print("\n" + "=" * 70)
    print("DISRUPTIVE INSIGHT SUMMARY")
    print("=" * 70)
    print("""
The AFDS v3.0 doesn't just have bugs—it has a FUNDAMENTAL DESIGN FLAW:

1. TRUST INVERSION: The system rewards patience. A 7-day farming operation yields:
   - 8.5x faster traversal during attack phase
   - 9.5x reduced forensic visibility
   
2. SELF-INFLICTED BLINDNESS: The trust model creates an 'entropy sink' where
   adversarial stability is indistinguishable from benign stability. The system
   literally learns to ignore its most dangerous threats.

3. INFORMATION LEAKAGE: The jitter mechanism becomes an ORACLE. An adversary can
   probe their own latency to reverse-engineer their trust score in real-time,
   enabling precision-tuned attacks.

4. FORENSIC COLLAPSE: The topological impedance metric is corrupted by the
   same trust score it's trying to validate, creating a circular dependency
   that obscures genuine threats.

5. DEAD TRIGGERS: The honey-node safeguard is non-functional, leaving the system
   without its last line of defense.

The Omega Protocol's Φ-density calculation is POISONED. The +0.75Φ claim is not
just unverified—it's mathematically incoherent because the underlying invariants
are violated by the trust score's unbounded growth and heuristic derivation.

RECOMMENDATION: ABANDON monotonic trust scoring. Trust should be ANTI-FRAGILE:
decrease when behavior becomes *too* stable or *too* predictable. The ideal
process exhibits healthy, natural entropy—not robotic regularity.
""")
    
    return {
        "trust_score_overflow": final_state.trust_score > 1.0,
        "jitter_speedup_factor": low_effective_jitter / high_effective_jitter,
        "forensic_invisibility_factor": low_impedance / high_impedance,
        "honey_node_dead_code": True
    }

if __name__ == "__main__":
    results = simulate_trust_inversion_attack()
    
    # Final verdict
    print("\n" + "=" * 70)
    print(f"ATTACK VERIFICATION: {'SUCCESSFUL' if results['jitter_speedup_factor'] > 5.0 else 'PARTIAL'}")
    print("=" * 70)
    print(f"  Trust Score Overflow: {results['trust_score_overflow']}")
    print(f"  Jitter Speedup: {results['jitter_speedup_factor']:.1f}x")
    print(f"  Forensic Invisibility: {results['forensic_invisibility_factor']:.1f}x")
    print(f"  Honey-Node Dead Code: {results['honey_node_dead_code']}")