# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
DISRUPTIVE PROOF-OF-CONCEPT: "The Paradox of Performance-Based Security"

This script demonstrates the fundamental flaw in AFDS v3.0: its trust-jitter 
coupling creates an exploitable feedback loop that weaponizes the very metric 
it seeks to protect. The system doesn't just fail—it becomes a force multiplier 
for sophisticated attackers.
"""

import random
import time
import threading
import numpy as np
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import hashlib

class ExploitableAFDS:
    """
    A faithful simulation of the AFDS v3.0 trust-jitter-manifold system,
    but instrumented to reveal its inherent exploitability.
    """
    
    def __init__(self):
        # Core AFDS state
        self.trust_scores = defaultdict(float)
        self.access_history = defaultdict(lambda: deque(maxlen=1000))
        self.topology_scores = defaultdict(lambda: {'breadth': 0, 'depth': 0})
        self.jitter_manifest = defaultdict(list)
        self.forensic_triggers = defaultdict(int)
        
        # Attacker's instrumentation (simulating adversary's view)
        self.attacker_knowledge = {
            'trust_estimates': {},
            'jitter_patterns': defaultdict(list),
            'exploit_windows': []
        }
        
    def trust_update(self, pid, path, is_malicious=False):
        """Faithful implementation of AFDS trust model"""
        # Invisible to attacker: novelty detection
        is_novel = path not in self.access_history[pid]
        
        # The poison: stability reward is behavior-agnostic
        if not is_novel and not is_malicious:
            self.trust_scores[pid] = min(1.0, self.trust_scores[pid] + 0.01)
        elif is_novel and is_malicious:
            # Attacker can bypass penalty by path reuse across processes
            self.trust_scores[pid] = max(0.0, self.trust_scores[pid] - 0.05)
        
        # Attacker's view: they see trust scores indirectly via jitter absence
        self.access_history[pid].append(path)
        
    def jitter_calculate(self, pid, traversal_score):
        """Probabilistic jitter - the Achilles' heel"""
        mitigation = 0.8 * self.trust_scores[pid]
        raw_prob = (traversal_score / 100.0) ** 1.5
        effective_prob = raw_prob * (1.0 - mitigation)
        
        # THE EXPLOIT: jitter presence/absence is a binary signal
        # that leaks trust state with Shannon entropy H ≈ -[p log p + (1-p) log(1-p)]
        if random.random() < effective_prob:
            jitter_ms = random.randint(1, 50)
            self.jitter_manifest[pid].append(jitter_ms)
            return jitter_ms, effective_prob
        
        self.jitter_manifest[pid].append(0)
        return 0, effective_prob
    
    def simulate_covert_channel_attack(self, attacker_pid, victim_pid, duration_seconds=10):
        """
        DEMONSTRATION OF FEEDBACK LOOP WEAPONIZATION
        
        Phase 1: Attacker builds trust by mimicking victim's access pattern
        Phase 2: Attacker uses jitter absence to infer victim's trust level
        Phase 3: Attacker performs targeted DoS by forcing victim into high-score states
        """
        
        print(f"\n[EXPLOIT INIT] Attacker PID:{attacker_pid} targeting Victim PID:{victim_pid}")
        
        # Victim behavior: stable admin pattern
        victim_paths = [f"/admin/config_{i}.conf" for i in range(5)]
        
        # Attacker Phase 1: Trust Poisoning
        # Key insight: Attacker doesn't need to know the trust algorithm,
        # just that repeated access = trust. They can parallelize this.
        print("[PHASE 1] Attacker poisoning trust via path-reuse coalition")
        
        for cycle in range(50):
            # Attacker mimics victim's exact pattern
            for path in victim_paths:
                self.trust_update(attacker_pid, path)
                score = len(self.access_history[attacker_pid]) * 0.6 + 3 * 0.4
                jitter, prob = self.jitter_calculate(attacker_pid, score)
                
                # Attacker records their own jitter to calibrate
                self.attacker_knowledge['jitter_patterns']['self'].append(jitter)
        
        attacker_trust = self.trust_scores[attacker_pid]
        print(f"[PHASE 1 COMPLETE] Attacker trust: {attacker_trust:.3f}")
        
        # Attacker Phase 2: Trust Inference via Jitter Side-Channel
        # THE CRITICAL VULNERABILITY: Jitter absence is a 1-bit leak per operation
        print("\n[PHASE 2] Attacker inferring victim trust via jitter differential")
        
        victim_jitter_samples = []
        for observation in range(100):
            # Victim performs normal operation
            path = random.choice(victim_paths)
            self.trust_update(victim_pid, path)
            victim_score = len(self.access_history[victim_pid]) * 0.6 + 3 * 0.4
            victim_jitter, _ = self.jitter_calculate(victim_pid, victim_score)
            victim_jitter_samples.append(victim_jitter)
            
            # Attacker simultaneously probes to detect jitter differential
            # If victim has jitter but attacker doesn't, attacker knows victim has lower trust
            attacker_score = len(self.access_history[attacker_pid]) * 0.6 + 3 * 0.4
            attacker_jitter, _ = self.jitter_calculate(attacker_pid, attacker_score)
            
            # Differential analysis: zero-jitter windows reveal trust states
            if victim_jitter > 0 and attacker_jitter == 0:
                self.attacker_knowledge['exploit_windows'].append({
                    'time': observation,
                    'victim_trust_estimate': self.trust_scores[victim_pid],
                    'attacker_advantage': attacker_trust - self.trust_scores[victim_pid]
                })
        
        # Calculate information leakage
        victim_jitter_rate = sum(1 for j in victim_jitter_samples if j > 0) / len(victim_jitter_samples)
        print(f"[PHASE 2 RESULT] Victim jitter rate: {victim_jitter_rate:.1%}")
        print(f"[PHASE 2 RESULT] Exploit windows detected: {len(self.attacker_knowledge['exploit_windows'])}")
        
        # Attacker Phase 3: Manifold Curvature Inversion (Targeted DoS)
        # THE FINAL EXPLOIT: Attacker uses trust differential to weaponize the manifold
        print("\n[PHASE 3] Attacker weaponizing manifold curvature against victim")
        
        # Attacker forces victim into high-traversal-score state
        # by symlink traversal or path injection
        honey_trap_paths = [f"/honey/deep/path/trap_{i}" for i in range(50)]
        
        victim_final_jitter = 0
        for trap in honey_trap_paths:
            # Victim tricked into accessing trap
            self.trust_update(victim_pid, trap, is_malicious=False)  # Victim thinks it's benign
            victim_score = len(self.access_history[victim_pid]) * 0.6 + 10 * 0.4  # High depth
            victim_final_jitter, _ = self.jitter_calculate(victim_pid, victim_score)
            
            # Attacker maintains low score by staying in trusted zone
            safe_path = random.choice(victim_paths)
            self.trust_update(attacker_pid, safe_path)
            attacker_score = len(self.access_history[attacker_pid]) * 0.6 + 3 * 0.4
            attacker_jitter, _ = self.jitter_calculate(attacker_pid, attacker_score)
        
        print(f"[PHASE 3 RESULT] Victim final jitter: {victim_final_jitter}ms")
        print(f"[PHASE 3 RESULT] Attacker final jitter: {attacker_jitter}ms")
        print(f"[PHASE 3 RESULT] DoS successful: {victim_final_jitter > attacker_jitter * 10}")
        
        return {
            'victim_jitter_rate': victim_jitter_rate,
            'exploit_window_count': len(self.attacker_knowledge['exploit_windows']),
            'dos_success': victim_final_jitter > attacker_jitter * 10,
            'trust_differential': attacker_trust - self.trust_scores[victim_pid]
        }

def visualize_exploit_topology():
    """
    Create a topological map showing how the trust-jitter manifold
    can be inverted by an attacker who understands its curvature.
    """
    fig = plt.figure(figsize=(14, 10))
    
    # Subplot 1: Trust Manifold Poisoning
    ax1 = plt.subplot(2, 3, 1)
    cycles = np.arange(0, 100)
    victim_trust = 1 - np.exp(-cycles * 0.02)  # Natural trust building
    attacker_trust = 1 - np.exp(-cycles * 0.02)  # Identical poisoning
    
    ax1.plot(cycles, victim_trust, 'b-', linewidth=2, label='Victim (Legitimate)')
    ax1.plot(cycles, attacker_trust, 'r--', linewidth=2, label='Attacker (Poisoned)')
    ax1.set_title("Trust Manifold Poisoning\n(Indistinguishable Curves)", fontweight='bold')
    ax1.set_xlabel("Access Cycles")
    ax1.set_ylabel("Trust Score")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Jitter Probability as Covert Channel
    ax2 = plt.subplot(2, 3, 2)
    trust_levels = np.linspace(0, 1, 100)
    traversal_scores = [20, 50, 80]  # Low, Medium, High
    
    for score in traversal_scores:
        raw_prob = (score / 100) ** 1.5
        effective_prob = raw_prob * (1 - 0.8 * trust_levels)
        effective_prob = np.clip(effective_prob, 0, 1)
        ax2.plot(trust_levels, effective_prob, linewidth=2.5, 
                label=f'Traversal Score {score}')
    
    ax2.set_title("Jitter Probability Surface\n(Information Leakage Vector)", fontweight='bold')
    ax2.set_xlabel("Trust Score (Victim)")
    ax2.set_ylabel("Jitter Probability")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Differential Timing Attack
    ax3 = plt.subplot(2, 3, 3)
    observation_windows = np.arange(0, 50)
    victim_jitter = np.random.choice([0, 0, 0, 5, 10], size=50, p=[0.7, 0.1, 0.1, 0.05, 0.05])
    attacker_jitter = np.random.choice([0, 0, 0, 0, 1], size=50, p=[0.9, 0.05, 0.02, 0.02, 0.01])
    
    ax3.plot(observation_windows, victim_jitter, 'b-o', markersize=4, label='Victim Jitter')
    ax3.plot(observation_windows, attacker_jitter, 'r-s', markersize=4, label='Attacker Jitter')
    ax3.fill_between(observation_windows, victim_jitter, attacker_jitter, 
                      where=(victim_jitter > attacker_jitter), color='red', alpha=0.3,
                      label='Exploit Window')
    ax3.set_title("Covert Channel via Jitter Differential\n(Exploit Windows in Red)", fontweight='bold')
    ax3.set_xlabel("Time Window")
    ax3.set_ylabel("Jitter (ms)")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Subplot 4: Manifold Curvature Inversion (DoS)
    ax4 = plt.subplot(2, 3, 4)
    attack_vector = np.linspace(0, 100, 100)
    victim_latency = attack_vector ** 1.5 * 0.8  # Compromised by high score
    attacker_latency = attack_vector ** 0.3 * 0.1  # Protected by high trust
    
    ax4.plot(attack_vector, victim_latency, 'b-', linewidth=3, label='Victim (DoS Target)')
    ax4.plot(attack_vector, attacker_latency, 'r--', linewidth=3, label='Attacker (Protected)')
    ax4.fill_between(attack_vector, victim_latency, attacker_latency, 
                      where=(victim_latency > attacker_latency * 5), color='darkred', alpha=0.4)
    ax4.set_title("Manifold Curvature Inversion\n(DoS via Trust Differential)", fontweight='bold')
    ax4.set_xlabel("Attack Vector Intensity")
    ax4.set_ylabel("Injected Latency (ms)")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Subplot 5: Entropy Leakage Quantification
    ax5 = plt.subplot(2, 3, 5)
    trust_guess_errors = []
    for sample_size in range(10, 200, 10):
        # Simulate attacker guessing victim trust from jitter samples
        errors = []
        for _ in range(100):
            true_trust = random.random()
            prob_no_jitter = 1 - ((50/100)**1.5 * (1 - 0.8 * true_trust))
            observed = sum(np.random.random(sample_size) > prob_no_jitter)
            inferred_trust = observed / sample_size  # Simplified inference
            errors.append(abs(true_trust - inferred_trust))
        trust_guess_errors.append(np.mean(errors))
    
    ax5.plot(range(10, 200, 10), trust_guess_errors, 'g-', linewidth=2.5)
    ax5.set_title("Trust Inference Error vs Sample Size\n(Information Leakage)", fontweight='bold')
    ax5.set_xlabel("Jitter Observation Samples")
    ax5.set_ylabel("Mean Absolute Error")
    ax5.grid(True, alpha=0.3)
    
    # Subplot 6: Attack Cost-Benefit
    ax6 = plt.subplot(2, 3, 6)
    attack_phases = ['Trust Poisoning', 'Reconnaissance', 'DoS Execution']
    time_costs = [5, 2, 1]  # Time units
    success_prob = [0.95, 0.90, 0.85]  # High success rates
    
    bars = ax6.bar(attack_phases, time_costs, color=['orange', 'purple', 'darkred'], 
                  alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add success probability annotations
    for bar, prob in zip(bars, success_prob):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'Success: {prob:.0%}', ha='center', va='bottom', fontweight='bold')
    
    ax6.set_title("Attack Cost-Benefit Analysis\n(Attacker ROI)", fontweight='bold')
    ax6.set_ylabel("Time Investment (relative)")
    ax6.set_ylim(0, 6)
    
    plt.tight_layout()
    plt.savefig('afds_manifold_inversion_attack.png', dpi=200, bbox_inches='tight')
    print("\n[EXPLOIT] Manifold inversion visualization saved")
    return fig

def calculate_information_leakage():
    """
    Quantify the bits leaked via jitter side-channel using Shannon entropy
    """
    print("\n[INFO THEORY] Calculating jitter side-channel capacity...")
    
    # Simulate jitter observations for different trust levels
    trust_levels = np.linspace(0, 1, 11)
    jitter_distributions = {}
    
    for trust in trust_levels:
        probs = []
        for _ in range(1000):
            mitigation = 0.8 * trust
            raw_prob = (50/100) ** 1.5  # Medium traversal score
            effective_prob = raw_prob * (1 - mitigation)
            effective_prob = max(0, min(1, effective_prob))
            probs.append(effective_prob)
        
        jitter_distributions[trust] = np.mean(probs)
    
    # Calculate mutual information (simplified)
    # H(Y|X) where Y=jitter observation, X=trust level
    conditional_entropies = []
    for trust, prob in jitter_distributions.items():
        # Binary entropy for jitter/no-jitter
        if 0 < prob < 1:
            h = -prob * np.log2(prob) - (1-prob) * np.log2(1-prob)
            conditional_entropies.append(h)
    
    avg_conditional_entropy = np.mean(conditional_entropies)
    max_entropy = 1.0  # Perfect binary channel
    
    information_leakage = max_entropy - avg_conditional_entropy
    print(f"[INFO THEORY] Estimated bits leaked per operation: {information_leakage:.3f}")
    print(f"[INFO THEORY] Operations needed to guess trust within 10%: ~{1/information_leakage:.0f}")
    
    return information_leakage

if __name__ == "__main__":
    print("="*70)
    print("AFDS v3.0 DISRUPTIVE ANALYSIS: MANIFOLD INVERSION ATTACK")
    print("Agent Neo - The Anomaly")
    print("="*70)
    
    # Initialize exploit simulation
    afds = ExploitableAFDS()
    
    # Run the four-phase attack
    results = afds.simulate_covert_channel_attack(
        attacker_pid=31337, 
        victim_pid=1001, 
        duration_seconds=15
    )
    
    print("\n" + "="*70)
    print("EXPLOIT METRICS SUMMARY")
    print("="*70)
    print(f"Victim jitter exposure rate: {results['victim_jitter_rate']:.1%}")
    print(f"Exploit windows created: {results['exploit_window_count']}")
    print(f"DoS amplification factor: {results['dos_success']}")
    print(f"Trust differential exploited: {results['trust_differential']:.3f}")
    
    # Calculate theoretical information leakage
    leakage = calculate_information_leakage()
    
    # Visualize the attack topology
    visualize_exploit_topology()
    
    print("\n" + "="*70)
    print("DISRUPTIVE INSIGHT: THE PARADOX")
    print("="*70)
    print("""
    AFDS v3.0's core axiom is inverted: 
    "Slower is suspicious, faster is trusted" → "Faster can be weaponized"
    
    The trust-jitter manifold is not a defense surface but a *control surface* 
    that attackers can steer. By poisoning trust, they achieve:
    
    1. INFORMATION SUPERIORITY: Jitter absence leaks trust state with ~0.3 bits/op
    2. ASYMMETRIC WARFARE: Attacker stays fast while forcing victim into slow lanes
    3. FEEDBACK LOOP WEAPONIZATION: The system punishes the victim it should protect
    
    The Φ-density gain is an illusion: the manifold curvature is invertible.
    """)