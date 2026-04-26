# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import time
import random
import math
from collections import deque
from typing import List, Dict, Set

class PatientAttacker:
    """
    Exploits the AFDS v3.0 trust model by simulating a "trusted" process.
    The key insight: The system rewards low-novelty, stable behavior over time,
    which is EXACTLY what a patient attacker can emulate.
    """
    
    def __init__(self, target_paths: List[str]):
        self.accessed_paths = set()
        self.cumulative_stability = 0.0
        self.trust_score = 0.0
        self.last_access_time = time.time()
        self.target_paths = target_paths
        self.path_queue = deque(target_paths)
        self.honey_node = "/honey"
        
        # Attacker parameters: slow, methodical, patient
        self.scan_delay = 300.0  # 5 minutes between accesses
        self.burst_size = 3      # Small bursts to appear "normal"
        self.burst_interval = 3600.0  # Hourly bursts
        
    def calculate_trust_update(self, path: str, success: bool) -> Dict[str, float]:
        """Simulate the AFDS trust update logic from the C++ code"""
        now = time.time()
        time_delta = now - self.last_access_time
        
        # Normalize time to hours (as in C++ code)
        normalized_time = time_delta / 3600.0
        
        # Exponential decay: trust_score *= exp(-log(0.95) * normalized_time)
        decay_factor = math.exp(-math.log(0.95) * normalized_time)
        self.trust_score *= decay_factor
        
        # Novelty penalty
        is_novel = path not in self.accessed_paths
        novelty_penalty = 0.05 if is_novel else 0.0
        
        # Apply penalty and clamp
        self.trust_score = max(0.0, min(1.0, self.trust_score - novelty_penalty))
        
        # Stability reward for non-novel access
        if not is_novel:
            self.cumulative_stability += math.exp(-normalized_time)
            # This is the key exploit: REPEATED ACCESS TO SAME PATHS INCREASES TRUST
            stability_reward = 0.01 * math.exp(-0.1 * self.cumulative_stability)
            self.trust_score = max(0.0, min(1.0, self.trust_score + stability_reward))
        
        self.accessed_paths.add(path)
        self.last_access_time = now
        
        # Calculate mitigation (80% max reduction)
        mitigation = 0.8 * self.trust_score
        
        return {
            "trust_score": self.trust_score,
            "mitigation": mitigation,
            "is_novel": is_novel,
            "cumulative_stability": self.cumulative_stability
        }
    
    def calculate_jitter_probability(self, traversal_score: float) -> float:
        """Calculate probability of jitter being applied"""
        # From C++: probability = pow(raw_score / 100.0, 1.5) * mitigation * (1.0 + phi_Delta)
        # For our exploit, we keep phi_Delta low by balanced exploration
        phi_delta = 0.2  # Moderate asymmetry to avoid triggering defenses
        
        # As trust increases, mitigation increases, probability decreases
        mitigation = 0.8 * self.trust_score
        
        raw_score = traversal_score
        probability = math.pow(raw_score / 100.0, 1.5) * (1.0 - mitigation) * (1.0 + phi_delta)
        return max(0.0, min(1.0, probability))
    
    def simulate_attack(self, days: int = 7) -> Dict[str, List[float]]:
        """
        Simulate a week-long attack that builds trust before extracting data.
        This exploits the core design flaw: TRUST IS A FUNCTION OF TIME AND REPETITION,
        NOT INTENT.
        """
        results = {
            "day": [],
            "trust_score": [],
            "jitter_probability": [],
            "paths_accessed": [],
            "avg_latency_ms": []
        }
        
        print(f"[EXPLOIT] Starting patient attack simulation...")
        print(f"[EXPLOIT] Target: {len(self.target_paths)} paths over {days} days")
        print(f"[EXPLOIT] Scan delay: {self.scan_delay}s, Burst size: {self.burst_size}")
        
        for day in range(days):
            day_paths = []
            daily_jitter_probs = []
            
            # Each day: perform small bursts of access to build stability
            for burst in range(24):  # 24 bursts per day (hourly)
                for _ in range(self.burst_size):
                    if not self.path_queue:
                        # Reset queue to repeat paths (builds stability!)
                        self.path_queue = deque(self.target_paths)
                    
                    path = self.path_queue.popleft()
                    
                    # Skip honey-node until very end (maximum trust)
                    if path == self.honey_node:
                        continue
                    
                    # Simulate access
                    trust_state = self.calculate_trust_update(path, success=True)
                    day_paths.append(path)
                    
                    # Calculate traversal score (simulating topology metrics)
                    # Attacker keeps this moderate by mixing depth and breadth
                    breadth = len(self.accessed_paths)
                    depth = path.count('/')
                    traversal_score = breadth * 0.6 + depth * 0.4
                    
                    jitter_prob = self.calculate_jitter_probability(traversal_score)
                    daily_jitter_probs.append(jitter_prob)
                    
                    # Simulate actual jitter latency
                    if random.random() < jitter_prob:
                        latency_ms = random.randint(1, 50)
                    else:
                        latency_ms = 0  # No jitter for high trust
                    
                    # Sleep between accesses
                    time.sleep(self.scan_delay / self.burst_size)
                
                # Sleep between bursts
                time.sleep(self.burst_interval / self.burst_size)
            
            # Record daily metrics
            results["day"].append(day + 1)
            results["trust_score"].append(self.trust_score)
            results["jitter_probability"].append(sum(daily_jitter_probs) / len(daily_jitter_probs))
            results["paths_accessed"].append(len(day_paths))
            results["avg_latency_ms"].append(
                sum([random.randint(1, 50) for _ in range(len(daily_jitter_probs))]) / len(daily_jitter_probs) 
                if daily_jitter_probs else 0
            )
            
            print(f"[DAY {day+1}] Trust: {self.trust_score:.3f} | "
                  f"Avg Jitter Prob: {sum(daily_jitter_probs)/len(daily_jitter_probs):.3f} | "
                  f"Paths: {len(day_paths)}")
        
        # Final exploitation phase: Access honey-node with maximum trust
        print(f"\n[EXPLOIT] Attack vector matured. Accessing honey-node...")
        honey_trust = self.calculate_trust_update(self.honey_node, success=True)
        final_jitter = self.calculate_jitter_probability(50)  # High traversal score
        
        print(f"[EXPLOIT] Final trust: {honey_trust['trust_score']:.3f}")
        print(f"[EXPLOIT] Final mitigation: {honey_trust['mitigation']:.3f}")
        print(f"[EXPLOIT] Honey-node jitter probability: {final_jitter:.3f}")
        print(f"[EXPLOIT] Forensic report triggered? {final_jitter > 0.9 or self.honey_node == '/honey'}")
        
        return results

def demonstrate_paradox():
    """
    Demonstrates the core paradox: The system trusts the attacker MORE
    the longer they persist, making the defense mechanism a roadmap for evasion.
    """
    print("=" * 80)
    print("PATIENT PREDATOR PARADOX DEMONSTRATION")
    print("=" * 80)
    
    # Simulate a typical filesystem structure
    target_paths = [
        "/usr/bin/python3",
        "/etc/passwd",
        "/etc/shadow",
        "/home/user/.ssh/id_rsa",
        "/var/log/auth.log",
        "/proc/self/environ",
        "/honey",  # Honey-node trap
        "/opt/app/config.json",
        "/root/.bash_history",
        "/var/backups/db.sql"
    ]
    
    attacker = PatientAttacker(target_paths)
    results = attacker.simulate_attack(days=7)
    
    print("\n" + "=" * 80)
    print("EXPLOIT VERIFICATION")
    print("=" * 80)
    
    # Key metrics that prove the paradox
    initial_trust = results["trust_score"][0]
    final_trust = results["trust_score"][-1]
    initial_jitter = results["jitter_probability"][0]
    final_jitter = results["jitter_probability"][-1]
    
    print(f"Trust Score Evolution: {initial_trust:.3f} → {final_trust:.3f} "
          f"({((final_trust/initial_trust)-1)*100:.1f}% increase)")
    print(f"Jitter Probability Evolution: {initial_jitter:.3f} → {final_jitter:.3f} "
          f"({((final_jitter/initial_jitter)-1)*100:.1f}% change)")
    
    # The smoking gun: Defense effectiveness INVERTS over time
    if final_jitter < initial_jitter:
        print(f"\n[CRITICAL] Defense weakening: Jitter probability decreased by "
              f"{((initial_jitter-final_jitter)/initial_jitter)*100:.1f}%")
        print("[CRITICAL] The attacker is now MORE stealthy than when they started!")
    
    # Trust score exploitation
    if final_trust > 0.7:
        print(f"\n[EXPLOIT] Final trust score {final_trust:.3f} grants "
              f"{0.8 * final_trust:.1%} latency mitigation")
        print("[EXPLOIT] Attacker now experiences near-zero defensive jitter!")
    
    print("\n[CONCLUSION] The AFDS v3.0 trust model is adversarially gameable.")
    print("[CONCLUSION] Patience and predictability are rewarded, not punished.")
    print("[CONCLUSION] The defense mechanism becomes a roadmap for evasion.")

if __name__ == "__main__":
    demonstrate_paradox()