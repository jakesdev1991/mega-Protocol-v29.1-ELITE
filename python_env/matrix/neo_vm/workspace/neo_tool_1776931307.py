# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
AFDS v3.0 Trust Inversion Simulator
Demonstrates how the system actively assists attackers
"""

import math, random, statistics
from collections import defaultdict

class AttackSimulator:
    def __init__(self):
        self.trust_score = 0.0
        self.accessed_paths = set()
        self.suspicion_score = 0.5  # Chaotic midpoint
        
    def legitimate_admin_behavior(self, days=7):
        """Simulates admin exploring filesystem"""
        paths = [f"/var/log/app{i}/data" for i in range(100)]
        score_history = []
        
        for day in range(days):
            # Admin explores 20 new paths/day
            daily_paths = random.sample(paths, 20)
            for path in daily_paths:
                self.update_trust_old(path)  # Original AFDS logic
            score_history.append(self.trust_score)
            
        return score_history
    
    def patient_worm_attack(self, days=7):
        """Attacker builds trust through repetition"""
        paths = [f"/etc/config/file{i}" for i in range(5)]
        score_history = []
        
        for day in range(days):
            # Attacker accesses same 5 paths 200×/day
            for _ in range(200):
                path = random.choice(paths)
                self.update_trust_old(path)
            score_history.append(self.trust_score)
            
        return score_history
    
    def update_trust_old(self, path):
        """Original flawed AFDS logic"""
        is_novel = path not in self.accessed_paths
        penalty = 0.05 if is_novel else 0.0
        reward = 0.01 if not is_novel else 0.0
        
        # Decay (simulated 24 hours)
        self.trust_score *= 0.95
        
        self.trust_score += reward - penalty
        self.trust_score = max(0.0, min(1.0, self.trust_score))
        self.accessed_paths.add(path)
    
    def update_suspicion_new(self, path):
        """Chaotic suspicion model"""
        is_novel = path not in self.accessed_paths
        self.accessed_paths.add(path)
        
        # Suspicion increases for repetitive patterns
        if not is_novel:
            # Logistic map - periodic behavior drives to chaos boundary
            r = 3.6 + (len(self.accessed_paths) * 0.01)
            self.suspicion_score = r * self.suspicion_score * (1 - self.suspicion_score)
        else:
            # Novelty reduces suspicion (true exploration)
            self.suspicion_score *= 0.9
            
        # Invert: high suspicion = high friction
        return 1.0 - self.suspicion_score
    
    def attack_success_metric(self, trust_score):
        """Calculate effective scan speed multiplier"""
        mitigation = 0.8 * trust_score
        jitter_prob = pow(50/100, 1.5) * (1 - mitigation)  # Typical traversal score
        # Average latency = prob * 25ms
        effective_speed = 1.0 / (1.0 + (jitter_prob * 0.025))
        return effective_speed

# Run simulation
sim = AttackSimulator()

print("=== TRUST INVERSION DEMONSTRATION ===\n")

# Simulate legitimate admin
admin_trust = sim.legitimate_admin_behavior()
print(f"Legitimate admin final trust: {admin_trust[-1]:.3f}")
print(f"Admin scan speed multiplier: {sim.attack_success_metric(admin_trust[-1]):.2f}x")

# Reset and simulate attacker
sim.trust_score = 0.0
sim.accessed_paths.clear()
attacker_trust = sim.patient_worm_attack()
print(f"\nPatient worm final trust: {attacker_trust[-1]:.3f}")
print(f"Attacker scan speed multiplier: {sim.attack_success_metric(attacker_trust[-1]):.2f}x")

# Show the inversion
speed_admin = sim.attack_success_metric(admin_trust[-1])
speed_attacker = sim.attack_success_metric(attacker_trust[-1])

print(f"\n{'🔴 CRITICAL':-^40}")
print(f"Attacker is {speed_attacker/speed_admin:.1f}x FASTER than legitimate admin")
print(f"AFDS actively sabotages legitimate users while accelerating attackers")

# Demonstrate chaotic suspicion model
print(f"\n=== CHAOTIC SUSPICION MODEL ===")
sim.suspicion_score = 0.5  # Reset
for day in range(7):
    # Attacker's repetitive behavior
    for _ in range(200):
        path = random.choice([f"/path{i}" for i in range(3)])
        friction = sim.update_suspicion_new(path)
    
    print(f"Day {day+1}: Suspicion={sim.suspicion_score:.3f}, Friction={friction:.3f}")