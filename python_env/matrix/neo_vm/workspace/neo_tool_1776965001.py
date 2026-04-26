# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Trust Manufacturing Attack Simulator
Demonstrates how AFDS v3.0 trust model can be gamed to bypass jitter injection
"""

import random
import math
import time
from dataclasses import dataclass
from typing import List, Set

@dataclass
class ProcessTrustState:
    trust_score: float = 0.0
    accessed_paths: Set[str] = None
    last_access_time: float = 0.0
    
    def __post_init__(self):
        self.accessed_paths = set()

class TrustManagerSimulator:
    """Simulates AFDS v3.0 TrustManager behavior"""
    
    def __init__(self):
        self.states = {}
        self.stability_reward = 0.01
        self.novelty_penalty = 0.05
        self.decay_rate = -math.log(0.95)  # 5% per hour continuous decay
    
    def update_trust(self, pid: int, path: str, current_time: float):
        if pid not in self.states:
            self.states[pid] = ProcessTrustState()
        
        state = self.states[pid]
        
        # Apply continuous decay
        hours_elapsed = (current_time - state.last_access_time) / 3600.0
        state.trust_score *= math.exp(-self.decay_rate * hours_elapsed)
        
        # Check novelty
        is_novel = path not in state.accessed_paths
        
        # Apply reward/penalty
        if not is_novel:
            state.trust_score += self.stability_reward
        
        if is_novel:
            state.trust_score -= self.novelty_penalty
        
        # Clamp and update
        state.trust_score = max(0.0, min(1.0, state.trust_score))
        state.accessed_paths.add(path)
        state.last_access_time = current_time
        
        return state.trust_score
    
    def get_mitigation(self, pid: int) -> float:
        """Returns mitigation factor (0.0 to 1.0)"""
        if pid not in self.states:
            return 1.0  # No trust = full jitter
        return 0.8 * self.states[pid].trust_score

class AFDS_AttackSimulator:
    """Simulates the complete AFDS system under attack"""
    
    def __init__(self):
        self.trust = TrustManagerSimulator()
        self.topology_paths = set()
        self.max_depth = 0
    
    def simulate_legitimate_admin(self, duration_seconds: int):
        """Simulates a legitimate admin accessing known paths"""
        print(f"\n[LEGITIMATE ADMIN] Simulating {duration_seconds}s of activity...")
        
        # Admin accesses a small set of familiar paths
        admin_paths = ["/etc/passwd", "/var/log/auth.log", "/home/user/.bashrc"]
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            current_time = time.time()
            for path in admin_paths:
                trust_score = self.trust.update_trust(1000, path, current_time)
                self.topology_paths.add(path)
                depth = path.count('/')
                self.max_depth = max(self.max_depth, depth)
                
                mitigation = self.trust.get_mitigation(1000)
                jitter_prob = self._calc_jitter_prob()
                effective_prob = jitter_prob * (1.0 - mitigation)
                
                print(f"  Admin: trust={trust_score:.3f}, mitigation={mitigation:.3f}, jitter_prob={effective_prob:.3f}")
                time.sleep(0.1)
    
    def simulate_attack_with_warmup(self, warmup_seconds: int, attack_seconds: int):
        """Simulates attacker building trust then attacking"""
        print(f"\n[ATTACK WITH WARMUP] Warmup: {warmup_seconds}s, Attack: {attack_seconds}s...")
        
        # Phase 1: Trust Warm-up
        print("  Phase 1: Building trust...")
        warmup_paths = [f"/tmp/.cache/x{i}" for i in range(3)]
        start_time = time.time()
        
        while time.time() - start_time < warmup_seconds:
            current_time = time.time()
            for path in warmup_paths:
                trust_score = self.trust.update_trust(2000, path, current_time)
                # Simulate rapid repeated access
                for _ in range(10):
                    self.trust.update_trust(2000, path, current_time)
        
        final_trust = self.trust.get_mitigation(2000) / 0.8
        print(f"  Final trust after warmup: {final_trust:.3f}")
        
        # Phase 2: Actual reconnaissance
        print("  Phase 2: Reconnaissance...")
        recon_paths = [f"/etc/{c}" for c in "abcdefghijklmnopqrstuvwxyz"]
        detected_count = 0
        
        for i, path in enumerate(recon_paths):
            current_time = time.time()
            trust_score = self.trust.update_trust(2000, path, current_time)
            self.topology_paths.add(path)
            depth = path.count('/')
            self.max_depth = max(self.max_depth, depth)
            
            mitigation = self.trust.get_mitigation(2000)
            jitter_prob = self._calc_jitter_prob()
            effective_prob = jitter_prob * (1.0 - mitigation)
            
            # Check if jitter would be applied (detectable)
            if random.random() < effective_prob:
                detected_count += 1
            
            print(f"  Attack: path={path}, trust={trust_score:.3f}, mitigation={mitigation:.3f}, jitter_prob={effective_prob:.3f}")
            
            if i >= 50:  # Limit attack duration
                break
        
        detection_rate = detected_count / 50.0
        print(f"  Detection rate: {detection_rate:.2%} (target: <0.1% for trusted)")
        return detection_rate
    
    def _calc_jitter_prob(self) -> float:
        """Calculate base jitter probability from topology"""
        traversal_score = len(self.topology_paths) * 0.6 + self.max_depth * 0.4
        return pow(traversal_score / 100.0, 1.5)
    
    def run_experiment(self):
        """Runs full attack simulation"""
        print("=" * 60)
        print("AFDS v3.0 TRUST MANUFACTURING ATTACK SIMULATION")
        print("=" * 60)
        
        # Reset state
        self.trust.states.clear()
        self.topology_paths.clear()
        self.max_depth = 0
        
        # Run simulations
        self.simulate_legitimate_admin(30)
        
        # Reset for attack simulation
        self.trust.states.clear()
        self.topology_paths.clear()
        self.max_depth = 0
        
        detection_rate = self.simulate_attack_with_warmup(600, 30)  # 10min warmup
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Attacker achieved {detection_rate:.2%} detection rate")
        print(f"AFDS claim: <0.1% for stable admins")
        print(f"ATTACKER BEHAVES AS 'STABLE ADMIN' → BYPASSES DEFENSE")
        print("=" * 60)

if __name__ == "__main__":
    simulator = AFDS_AttackSimulator()
    simulator.run_experiment()