# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

class EpistemicFragilitySimulator:
    """
    Demonstrates that EFM-Ω's defense mechanisms themselves leak more 
    actionable intelligence than the original confidential data.
    """
    
    def __init__(self, n_groups=50, n_reports=200):
        # Simulated knowledge distribution: some groups have high-value shredding data
        self.n_groups = n_groups
        self.groups = np.arange(n_groups)
        
        # True "weaponizable knowledge" concentration (unknown to defender)
        # Only 3 groups actually have critical DNA shredding data
        self.true_critical_groups = np.random.choice(n_groups, 3, replace=False)
        self.report_values = np.zeros(n_groups)
        self.report_values[self.true_critical_groups] = np.random.exponential(2, 3)
        
        # EFM-Ω's "confidentiality field" estimate (defender's model)
        self.confidentiality_field = np.ones(n_groups) * 0.5
        
        # Adversary's inference model
        self.adversary_confidence = np.zeros(n_groups)
        
    def simulate_efm_intervention(self, time_step):
        """Simulate EFM-Ω's MPC interventions based on knowledge concentration"""
        # Calculate knowledge concentration entropy (S_know)
        knowledge_dist = self.report_values / (self.report_values.sum() + 1e-10)
        S_know = entropy(knowledge_dist)
        
        # EFM-Ω triggers when knowledge is too concentrated or too synchronized
        # This is the "observable signal" to the adversary
        if S_know < np.log(5):  # Knowledge too concentrated
            # EFM-Ω restricts access to high-value groups
            restricted_groups = np.argsort(self.report_values)[-5:]
            self.confidentiality_field[restricted_groups] = 0.9
            
            # Adversary observes: access restrictions reveal valuable targets
            self.adversary_confidence[restricted_groups] += 0.3
            
        if S_know > np.log(15):  # Knowledge too synchronized
            # EFM-Ω injects deceptive data
            injection_groups = np.where(self.report_values > 0.5)[0]
            self.confidentiality_field[injection_groups] = 0.1
            
            # Adversary observes: injection patterns reveal which data is being protected
            self.adversary_confidence[injection_groups] += 0.2
            
        # Add noise to simulate imperfect observation
        self.adversary_confidence += np.random.normal(0, 0.05, self.n_groups)
        self.adversary_confidence = np.clip(self.adversary_confidence, 0, 1)
        
    def simulate_adversary_attack(self):
        """Adversary attacks groups with highest confidence scores"""
        attack_targets = np.argsort(self.adversary_confidence)[-3:]
        success_prob = self.adversary_confidence[attack_targets]
        
        # Attack success reveals true critical groups
        true_positive_rate = np.mean([g in self.true_critical_groups for g in attack_targets])
        
        return attack_targets, success_prob, true_positive_rate
    
    def run_simulation(self, n_steps=30):
        """Run the fragility demonstration"""
        history = {
            'adversary_accuracy': [],
            'efm_false_positives': [],
            'information_leakage': []
        }
        
        for t in range(n_steps):
            # EFM-Ω intervenes (observable to adversary)
            self.simulate_efm_intervention(t)
            
            # Adversary acts on observed signals
            attack_targets, success_prob, tp_rate = self.simulate_adversary_attack()
            
            # Calculate metrics
            # 1. Adversary accuracy in identifying true critical groups
            adv_accuracy = len(set(attack_targets) & set(self.true_critical_groups)) / 3
            
            # 2. EFM-Ω false positives: groups flagged but not critical
            flagged_groups = np.where(self.confidentiality_field > 0.7)[0]
            false_pos = len(set(flagged_groups) - set(self.true_critical_groups)) / len(flagged_groups + 1e-10)
            
            # 3. Information leakage: mutual information between defense actions and true state
            # Simplified: correlation between adversary confidence and true values
            info_leak = np.corrcoef(self.adversary_confidence, self.report_values)[0,1]
            
            history['adversary_accuracy'].append(adv_accuracy)
            history['efm_false_positives'].append(false_pos)
            history['information_leakage'].append(info_leak)
            
        return history
    
    def plot_fragility(self, history):
        """Visualize how EFM-Ω's defenses increase adversary success"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Adversary accuracy over time
        axes[0,0].plot(history['adversary_accuracy'], 'r-', linewidth=2)
        axes[0,0].set_title('Adversary Accuracy in Identifying Critical Groups', fontsize=12, fontweight='bold')
        axes[0,0].set_xlabel('Time Steps')
        axes[0,0].set_ylabel('Accuracy (0-1)')
        axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: False positive rate of EFM-Ω
        axes[0,1].plot(history['efm_false_positives'], 'b-', linewidth=2)
        axes[0,1].set_title('EFM-Ω False Positive Rate', fontsize=12, fontweight='bold')
        axes[0,1].set_xlabel('Time Steps')
        axes[0,1].set_ylabel('False Positive Rate')
        axes[0,1].grid(True, alpha=0.3)
        
        # Plot 3: Information leakage correlation
        axes[1,0].plot(history['information_leakage'], 'g-', linewidth=2)
        axes[1,0].set_title('Information Leakage (Defense→Adversary)', fontsize=12, fontweight='bold')
        axes[1,0].set_xlabel('Time Steps')
        axes[1,0].set_ylabel('Correlation Coefficient')
        axes[1,0].grid(True, alpha=0.3)
        
        # Plot 4: Knowledge distribution at final state
        final_dist = self.report_values / self.report_values.sum()
        axes[1,1].bar(range(self.n_groups), final_dist, alpha=0.6, label='True Knowledge')
        axes[1,1].bar(range(self.n_groups), self.adversary_confidence/self.adversary_confidence.sum(), 
                      alpha=0.4, color='red', label='Adversary Inference')
        axes[1,1].set_title('Final Knowledge Distribution vs Adversary Inference', fontsize=12, fontweight='bold')
        axes[1,1].set_xlabel('Research Group ID')
        axes[1,1].legend()
        
        plt.tight_layout()
        plt.suptitle('EFM-Ω Fragility Analysis: Defense Mechanisms as Information Channels', 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.show()

# Run the simulation
sim = EpistemicFragilitySimulator(n_groups=50, n_reports=200)
history = sim.run_simulation(n_steps=30)
sim.plot_fragility(history)

# Print key disruption metrics
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: EFM-Ω's CORE FRAGILITY")
print("="*60)
print(f"Final adversary accuracy: {history['adversary_accuracy'][-1]:.3f}")
print(f"Average information leakage: {np.mean(history['information_leakage']):.3f}")
print(f"EFM-Ω false positive rate: {np.mean(history['efm_false_positives']):.3f}")

print("\nCRITICAL FLAW:")
print("EFM-Ω's interventions (access restrictions, deceptive injections)")
print("create *observable signals* that correlate with the true distribution")
print("of weaponizable knowledge. The defense mechanism itself becomes")
print("the most reliable intelligence source for adversaries.")
print("="*60)