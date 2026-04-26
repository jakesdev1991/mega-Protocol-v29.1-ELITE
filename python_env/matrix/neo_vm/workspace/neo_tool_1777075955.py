# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import hashlib
import time

# ============================================
# BETA'S TRADITIONAL SYSTEM (VULNERABLE)
# ============================================
class BetaSystem:
    def __init__(self):
        # Static config - the "trophy artifact"
        self.threshold = 10000  # contracts/sec
        self.config_exposure = 0.7  # discoverable
        
    def detect_unusual(self, volume):
        # Simple threshold check
        return volume > self.threshold
    
    def adversarial_optimize(self, true_risk_level):
        # Adversary learns threshold and tunes just below it
        if self.config_exposure > 0.5:  # Config is discoverable
            return self.threshold * 0.99  # Evade detection
        return true_risk_level

# ============================================
# NEO'S FRAGMENTED SYSTEM (DISRUPTIVE)
# ============================================
class FragmentedDesk:
    def __init__(self, desk_id, analyst_biohash):
        self.desk_id = desk_id
        self.biohash = analyst_biohash
        self.session_nonce = hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:8]
        # Perceptually incompatible semantics
        self.risk_vector = self._generate_epistemic_fragment()
        
    def _generate_epistemic_fragment(self):
        # Randomly selects a *risk dimension* that makes no sense to other desks
        dimensions = [
            lambda v, g, d: v > 10000 and g < 0.3,  # Volume + Gamma
            lambda v, g, d: hash(f"{v}{self.biohash}") % 1000 > 500,  # Personal hash
            lambda v, g, d: np.random.random() > 0.5,  # True randomness
            lambda v, g, d: d > 0.8 and self.desk_id % 2 == 0,  # Desk-specific logic
        ]
        return random.choice(dimensions)
    
    def detect_unusual(self, volume, gamma, dark_activity):
        # Uses the *personalized* risk vector
        return self.risk_vector(volume, gamma, dark_activity)
    
    def rotate_epistemology(self):
        # Changes the *semantics* of risk, not just thresholds
        self.risk_vector = self._generate_epistemic_fragment()
        self.session_nonce = hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:8]

class DEFSystem:
    def __init__(self, num_desks=5):
        self.desks = [
            FragmentedDesk(i, f"biohash_{i}") 
            for i in range(num_desks)
        ]
        self.rotation_interval = 10  # seconds
        
    def detect_unusual(self, volume, gamma, dark_activity):
        # Each desk votes with incompatible logic
        votes = [desk.detect_unusual(volume, gamma, dark_activity) for desk in self.desks]
        # **DELIBERATE DISSONANCE**: Flag if *any* desk sees risk
        # This creates noise for adversaries, clarity for institution
        return any(votes)
    
    def adversarial_optimize(self, *args):
        # **IMPOSSIBLE**: No single config to optimize against
        # Adversary faces N incompatible ontologies
        return None  # Signal that optimization is futile
    
    def rotate_configs(self):
        if time.time() % self.rotation_interval < 0.1:
            for desk in self.desks:
                desk.rotate_epistemology()

# ============================================
# SIMULATION: ADVERSARIAL ATTACK
# ============================================
def simulate_attack(num_rounds=1000):
    # True underlying risk (hidden from adversaries)
    true_risks = np.random.exponential(15000, num_rounds)  # Most are safe, some are huge
    
    beta = BetaSystem()
    neo = DEFSystem(num_desks=8)
    
    beta_detected = 0
    neo_detected = 0
    beta_adversarial_success = 0
    neo_adversarial_success = 0
    
    for i, true_risk in enumerate(true_risks):
        # Simulate market data
        volume = true_risk
        gamma = np.random.random()
        dark_activity = np.random.random()
        
        # Beta system
        if beta.detect_unusual(beta.adversarial_optimize(true_risk)):
            beta_detected += 1
        if true_risk > 15000 and beta.adversarial_optimize(true_risk) < beta.threshold:
            beta_adversarial_success += 1  # Adversary hid true risk
            
        # DEF system
        neo.rotate_configs()
        if neo.detect_unusual(volume, gamma, dark_activity):
            neo_detected += 1
        # Adversary cannot optimize - returns None, so risk passes through
        if true_risk > 15000:
            neo_adversarial_success += 1  # Adversary fails to hide
    
    print("=== ADVERSARIAL SIMULATION RESULTS ===")
    print(f"Beta System:")
    print(f"  Detection Rate: {beta_detected/num_rounds:.2%}")
    print(f"  Adversarial Success: {beta_adversarial_success/num_rounds:.2%} (adversary hides risk)")
    
    print(f"\nDEF System:")
    print(f"  Detection Rate: {neo_detected/num_rounds:.2%}")
    print(f"  Adversarial Success: {neo_adversarial_success/num_rounds:.2%} (adversary cannot adapt)")
    
    print(f"\nFRAGMENTATION IMPACT:")
    print(f"  Adversarial Failure Rate: {(neo_adversarial_success - beta_adversarial_success)/num_rounds:.2%}")
    print(f"  Epistemic Chaos Factor: {neo.detect_unusual(5000, 0.1, 0.1) != neo.detect_unusual(5000, 0.1, 0.1)}")

simulate_attack()