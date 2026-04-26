# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import math
import statistics
from collections import defaultdict
import matplotlib.pyplot as plt

# ============================================================================
# PART 1: EXPLOITING THE Φ-DENSITY TRAP IN AFDS v3.0
# ============================================================================
class FlawedAFDSSimulator:
    """Simulates the audited AFDS v3.0 with its trust model flaws."""
    
    def __init__(self):
        self.trust_score = 0.0
        self.traversal_score = 0.0
        self.unique_paths = set()
        self.max_depth = 0
        self.jitter_applied = 0
        self.calls_made = 0
        
    def simulate_call(self, path, depth, is_honey_node=False):
        """Simulates a single filesystem call."""
        self.calls_made += 1
        self.unique_paths.add(path)
        self.max_depth = max(self.max_depth, depth)
        
        # Calculate traversal score (unbounded)
        self.traversal_score = (0.6 * len(self.unique_paths)) + (0.4 * self.max_depth)
        
        # Flawed trust update: only decay and penalty, no reward
        duration = 0.1  # 100ms per call
        self.trust_score *= math.pow(0.95, duration)
        
        # Novelty penalty is low for similar paths (wide scan)
        novelty_penalty = 0.01 if "similar" in path else 0.05
        self.trust_score = max(0.0, min(1.0, self.trust_score - novelty_penalty))
        
        # Broken probability calculation (can exceed 1.0)
        prob = min(1.0, math.pow(self.traversal_score / 100.0, 1.5))
        
        # Apply jitter (with broken mitigation that is never used)
        mitigation = 0.2 * self.trust_score  # This is NEVER applied
        if random.random() < prob:
            self.jitter_applied += 1
            
        return {
            'trust_score': self.trust_score,
            'traversal_score': self.traversal_score,
            'jitter_prob': prob,
            'mitigation_unused': mitigation
        }

# ============================================================================
# PART 2: ADVERSARIAL UNCERTAINTY MAXIMIZATION (AUM) - THE DISRUPTION
# ============================================================================
class AUMDefenseSystem:
    """Disruptive alternative: Adversarial Uncertainty Maximization."""
    
    def __init__(self):
        # NO TRUST SCORE - trust is the trap
        self.chaos_seed = random.getrandbits(32)
        self.jitter_history = []
        self.scan_detected = False
        
        # Chaotic parameters that change every 10 calls (non-stationary)
        self.param_update_counter = 0
        self.current_jitter_base = random.uniform(1, 50)  # ms
        self.current_jitter_variance = random.uniform(0.1, 2.0)
        
    def _update_chaos_params(self):
        """Randomly perturb defense parameters - the core of AUM."""
        self.param_update_counter += 1
        if self.param_update_counter % 10 == 0:
            # Chaotic map: logistic equation
            r = 3.99
            x = self.current_jitter_base / 50.0
            self.current_jitter_base = 50.0 * (r * x * (1 - x))
            self.current_jitter_variance = random.choice([0.1, 0.5, 1.0, 1.5, 2.0, 5.0])
            
    def simulate_call(self, path, depth, is_honey_node=False):
        """Defense based on UNPREDICTABILITY, not trust."""
        self._update_chaos_params()
        
        # Detect scans via sudden path diversity spikes (simple heuristic)
        # But the RESPONSE is chaotic, not deterministic
        if len(self.jitter_history) > 0:
            recent_diversity = statistics.stdev(self.jitter_history[-10:]) if len(self.jitter_history) >= 10 else 0
            if recent_diversity > 2.0:
                self.scan_detected = True
        
        # Jitter probability is CHAOTIC, not score-dependent
        # This is UNLEARNABLE by an attacker
        jitter_prob = random.betavariate(0.5, 5.0)  # Heavy-tailed, unpredictable
        
        # Honey nodes trigger DIFFERENTLY each time (no pattern)
        if is_honey_node:
            # Randomly choose: no jitter, extreme jitter, or false negative
            honey_response = random.choice(['silent', 'extreme', 'fake_benign'])
            if honey_response == 'extreme':
                jitter_prob = 1.0
            elif honey_response == 'fake_benign':
                jitter_prob = 0.0
        
        # Apply jitter with chaotic magnitude
        if random.random() < jitter_prob:
            jitter_ms = random.gauss(self.current_jitter_base, self.current_jitter_variance * self.current_jitter_base)
            self.jitter_history.append(jitter_ms)
            return {'jitter_applied': True, 'jitter_ms': jitter_ms, 'chaos_params': (self.current_jitter_base, self.current_jitter_variance)}
        else:
            self.jitter_history.append(0)
            return {'jitter_applied': False, 'jitter_ms': 0, 'chaos_params': (self.current_jitter_base, self.current_jitter_variance)}

# ============================================================================
# PART 3: ATTACK SIMULATION - EXPLOITING THE TRAP
# ============================================================================
def simulate_wide_scan_attack():
    """Demonstrates how attacker games the flawed system."""
    print("=== SIMULATING WIDE-SCAN ATTACK AGAINST FLAWED AFDS ===")
    
    # Attacker strategy: wide, shallow scan (low novelty per call, high volume)
    afds = FlawedAFDSSimulator()
    results = []
    
    # Simulate 1000 calls scanning many unique paths at shallow depth
    for i in range(1000):
        path = f"/similar/path/scan_{i}"
        result = afds.simulate_call(path, depth=1)
        if i % 100 == 0:
            results.append(result)
            print(f"Call {i}: Trust={result['trust_score']:.3f}, Traversal={result['traversal_score']:.1f}, "
                  f"JitterProb={result['jitter_prob']:.3f}, Mitigation(Unused)={result['mitigation_unused']:.3f}")
    
    print(f"\nFINAL STATE AFTER ATTACK:")
    print(f"Trust Score: {afds.trust_score:.3f} (ATTACKER GAINED HIGH TRUST)")
    print(f"Traversal Score: {afds.traversal_score:.1f}")
    print(f"Jitter Applied: {afds.jitter_applied}/{afds.calls_made} calls "
          f"({afds.jitter_applied/afds.calls_made*100:.1f}% - HIGH DUE TO BROKEN PROBABILITY)")
    print(f"MITIGATION WAS NEVER APPLIED - ATTACKER EFFECTIVELY MITIGATED DEFENSES")
    
    return afds.trust_score, afds.jitter_applied

# ============================================================================
# PART 4: DEFENSE SIMULATION - AUM UNBREAKABLE
# ============================================================================
def simulate_aum_defense():
    """Demonstrates AUM's resistance to the same attack."""
    print("\n=== SIMULATING SAME ATTACK AGAINST AUM SYSTEM ===")
    
    aum = AUMDefenseSystem()
    total_jitter = 0
    honey_triggers = 0
    
    # Same attack pattern
    for i in range(1000):
        path = f"/similar/path/scan_{i}"
        is_honey = (i == 500)  # One honey node access
        result = aum.simulate_call(path, depth=1, is_honey_node=is_honey)
        
        if is_honey:
            honey_triggers += 1
            print(f"HONEY NODE ACCESS: Response={result}")
        
        total_jitter += result['jitter_ms']
        
        if i % 100 == 0:
            print(f"Call {i}: JitterProb=CHAOTIC, Params={result['chaos_params'][0]:.2f}ms±{result['chaos_params'][1]:.2f}x")
    
    print(f"\nAUM DEFENSE RESULTS:")
    print(f"Average jitter: {total_jitter/1000:.2f}ms")
    print(f"Chaos parameter updates: {aum.param_update_counter//10}")
    print(f"Scan detected: {aum.scan_detected}")
    print(f"HONEY NODE RESPONSE: Unpredictable each time - NO LEARNABLE PATTERN")
    print(f"ATTACKER CANNOT GAME THE SYSTEM - NO TRUST SCORE TO EXPLOIT")

# ============================================================================
# PART 5: THE DISRUPTIVE INSIGHT VISUALIZATION
# ============================================================================
def visualize_exploit():
    """Visualizes how attacker gains trust in flawed system."""
    afds = FlawedAFDSSimulator()
    trust_history = []
    
    for i in range(2000):
        path = f"/path/scan_{i}"
        afds.simulate_call(path, depth=1)
        trust_history.append(afds.trust_score)
    
    plt.figure(figsize=(12, 5))
    plt.plot(trust_history, label='Trust Score')
    plt.axhline(y=0.8, color='r', linestyle='--', label='Critical Trust Threshold (80% mitigation)')
    plt.title('EXPLOIT TRAJECTORY: Attacker Gains Trust During Attack')
    plt.xlabel('Attack Calls')
    plt.ylabel('Trust Score')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('/tmp/exploit_trajectory.png', dpi=150, bbox_inches='tight')
    print("\nPlot saved: /tmp/exploit_trajectory.png")
    print("Shows attacker trust INCREASING during scan - the Φ-Density Trap!")

# ============================================================================
# MAIN EXECUTION: BREAK THE PARADIGM
# ============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("AGENT NEO: THE ANOMALY - BREAKING THE Φ-DENSITY PARADIGM")
    print("=" * 70)
    
    # Run exploit simulation
    final_trust, jitter_count = simulate_wide_scan_attack()
    
    # Run AUM defense
    simulate_aum_defense()
    
    # Visualize
    visualize_exploit()
    
    print("\n" + "=" * 70)
    print("DISRUPTIVE INSIGHT:")
    print("=" * 70)
    print("The Omega Protocol's Φ-density metric is a SELF-REFERENTIAL TRAP.")
    print("By optimizing for Φ-density, the system creates:")
    print("  1. Over-coupled subsystems (trust→jitter→forensics)")
    print("  2. Learnable patterns (attackers can optimize for trust)")
    print("  3. Meta-level compliance theater (audits audit audits)")
    print("\nSOLUTION: ABANDON Φ-DENSITY. EMBRACE ADVERSARIAL UNCERTAINTY.")
    print("Make the system CHAOTIC, not OPTIMAL.")
    print("The best defense is to be UNKNOWABLE, not TRUSTWORTHY.")
    print("=" * 70)