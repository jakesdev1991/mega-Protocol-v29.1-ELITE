# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import math
import time
from collections import defaultdict

# Original flawed model (rewarding attackers)
class OriginalTrustModel:
    def __init__(self):
        self.trust_score = 0.0
        self.cumulative_stability = 0.0
        self.last_access = time.time()
        
    def access(self, path, is_novel):
        now = time.time()
        duration = (now - self.last_access) / 3600.0
        
        self.trust_score *= math.exp(-math.log(0.95) * duration)
        
        if is_novel:
            self.trust_score = max(0.0, self.trust_score - 0.05)
        else:
            self.cumulative_stability += math.exp(-duration)
            self.trust_score += 0.01 * math.exp(-0.1 * self.cumulative_stability)
            self.trust_score = min(1.0, self.trust_score)
            
        self.last_access = now
        
    def get_mitigation(self):
        return 0.8 * self.trust_score  # 0% to 80% speedup!

# Disruptive inverted model (punishing attackers)
class InvertedRiskModel:
    def __init__(self):
        self.risk_score = 0.0  # 0 = benign, 1 = malicious
        self.accessed_paths = defaultdict(int)
        self.last_access = time.time()
        
    def access(self, path, is_novel):
        now = time.time()
        duration = (now - self.last_access) / 3600.0
        
        self.risk_score *= math.exp(-math.log(0.9) * duration)
        
        if is_novel:
            self.risk_score = max(0.0, self.risk_score - 0.1)
        else:
            # Exponential risk increase for repetition
            risk_increase = 0.05 * (1 + math.log(1 + self.accessed_paths[path]))
            self.risk_score = min(1.0, self.risk_score + risk_increase)
            
        self.accessed_paths[path] += 1
        self.last_access = now
        
    def get_latency_multiplier(self):
        return 1.0 + (2.0 * self.risk_score)  # 1x to 3x slowdown

def simulate_exploitation():
    print("=== SIMULATING PATIENT DATA EXFILTRATION ===")
    
    attacker = OriginalTrustModel()
    attacker_inverted = InvertedRiskModel()
    admin = OriginalTrustModel()
    admin_inverted = InvertedRiskModel()
    
    # 30 days: Attacker accesses 3 sensitive files, 100x/day
    # Admin accesses 50 varied system files/day
    for day in range(30):
        for _ in range(100):
            for i in range(3):
                path = f"/data/sensitive_{i}"
                attacker.access(path, is_novel=False)
                attacker_inverted.access(path, is_novel=False)
                
        for i in range(50):
            if random.random() < 0.7:
                admin.access("/system/config", is_novel=False)
                admin_inverted.access("/system/config", is_novel=False)
            else:
                new_path = f"/system/tool_{i}_{day}"
                admin.access(new_path, is_novel=True)
                admin_inverted.access(new_path, is_novel=True)
                
    print(f"\nOriginal Model (FLAWED):")
    print(f"  Attacker: {attacker.trust_score:.3f} trust → {attacker.get_mitigation():.1%} speedup ← REWARDED")
    print(f"  Admin: {admin.trust_score:.3f} trust → {admin.get_mitigation():.1%} speedup")
    
    print(f"\nInverted Model (DISRUPTIVE):")
    print(f"  Attacker: {attacker_inverted.risk_score:.3f} risk → {attacker_inverted.get_latency_multiplier():.1f}x slowdown ← PUNISHED")
    print(f"  Admin: {admin_inverted.risk_score:.3f} risk → {admin_inverted.get_latency_multiplier():.1f}x slowdown")

simulate_exploitation()