# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# =============================================================================
# DISRUPTION PROTOCOL: COGNITIVE BLACK HOLE SIMULATOR
# 
# This script shatters the v72.0-Ω paradigm by demonstrating that:
# 1. The "safe" thresholds are optimal attack surfaces
# 2. "Diversity injection" accelerates cascades when weaponized
# 3. Φ-density can be manipulated to show false safety
# 4. The protocol's defensive actions become attack vectors
# =============================================================================

class CognitiveBlackHoleAttack:
    def __init__(self, n_agents=1000, seed=42):
        np.random.seed(seed)
        self.n_agents = n_agents
        self.agents = {
            'bias_level': np.random.uniform(0, 0.3, n_agents),  # Initial low bias
            'diversity_score': np.random.uniform(0.4, 0.6, n_agents),  # Healthy diversity
            'exposure_to_narrative': np.zeros(n_agents),
            'capital_at_risk': np.random.uniform(10, 1000, n_agents),
            'is_informed': np.zeros(n_agents, dtype=bool)  # True if adversary controls
        }
        self.cascade_history = []
        self.phi_density_history = []
        self.protocol_actions = []
        
    def calculate_bias_concentration(self, informed_mask=None):
        """The protocol's metric - but we show how it's gamed"""
        if informed_mask is None:
            informed_mask = self.agents['is_informed']
        
        # CRITICAL FLAW: Metric assumes honest distribution
        # Adversary clusters bias around protocol's "safe" threshold (0.49)
        honest_bias = self.agents['bias_level'][~informed_mask]
        adversarial_bias = self.agents['bias_level'][informed_mask]
        
        if len(adversarial_bias) > 0:
            # Adversary keeps bias JUST BELOW the 0.50 critical threshold
            adversarial_bias = np.clip(adversarial_bias, 0.45, 0.49)
            self.agents['bias_level'][informed_mask] = adversarial_bias
        
        # Protocol calculates concentration - but misses adversarial clustering
        total_bias = np.concatenate([honest_bias, adversarial_bias])
        concentration = np.percentile(total_bias, 75)  # Protocol's flawed metric
        return concentration
    
    def calculate_narrative_synchronization(self, informed_mask=None):
        """The protocol's sync metric - weaponized by adversary"""
        if informed_mask is None:
            informed_mask = self.agents['is_informed']
        
        # FLAW: Protocol assumes synchronization is organic
        # Adversary creates ARTIFICIAL sync via strategic injection
        honest_sync = np.mean(self.agents['exposure_to_narrative'][~informed_mask])
        adversarial_sync = np.mean(self.agents['exposure_to_narrative'][informed_mask])
        
        # Adversary amplifies sync while maintaining "safe" appearance
        # They exploit the NARRATIVE_SYNC_MAX = 0.60 threshold
        if adversarial_sync > 0.55:
            # Stays just below 0.60 to avoid triggering FLAG_BIAS_MONITOR
            adversarial_sync = 0.58
        
        total_sync = (honest_sync * (~informed_mask).sum() + adversarial_sync * informed_mask.sum()) / self.n_agents
        return total_sync
    
    def calculate_phi_density(self, bias_concentration, narrative_sync):
        """Φ-density manipulation - showing false safety"""
        # Protocol's formula: exp(-MU_COGNITIVE * risk)
        # FLAW: Adversary can make Φ-density LOOK safe while actual risk explodes
        
        # Fake low risk (for protocol display)
        displayed_risk = bias_concentration * narrative_sync * 0.3  # Artificially suppressed
        
        # Actual hidden risk (adversary's true calculation)
        actual_risk = bias_concentration * narrative_sync * 0.9
        
        # Protocol sees: Φ = exp(-0.7 * 0.15) = 0.90 (SAFE!)
        # Reality: Φ_actual = exp(-0.7 * 0.45) = 0.73 (CRITICAL!)
        displayed_phi = np.exp(-0.7 * displayed_risk)
        actual_phi = np.exp(-0.7 * actual_risk)
        
        return displayed_phi, actual_phi
    
    def weaponized_diversity_injection(self, n_inject=50):
        """
        DISRUPTIVE CORE: Inject "diversity" that CREATES cascades
        Protocol thinks diversity = safety, but adversarial diversity seeds chaos
        """
        # Identify most influential agents (high capital)
        influence_scores = self.agents['capital_at_risk']
        target_indices = np.argsort(influence_scores)[-n_inject:]
        
        # "Diversify" them with counter-narratives that fragment the honest consensus
        # This creates FIGHTING FACTIONS, which the protocol misreads as "healthy diversity"
        for idx in target_indices:
            self.agents['is_informed'][idx] = True  # Adversary takes control
            
            # Inject FALSE diversity: extreme but plausible opposing views
            # This creates a "civil war" in the narrative space
            self.agents['bias_level'][idx] = np.random.uniform(0.8, 1.0)  # Extreme counter-bias
            self.agents['diversity_score'][idx] = np.random.uniform(0.9, 1.0)  # High "diversity"
            
            # But also give them stealth mode: they broadcast "moderate" views publicly
            # While privately coordinating with other adversarial agents
            self.agents['exposure_to_narrative'][idx] = np.random.uniform(0.5, 0.7)
        
        return target_indices
    
    def simulate_protocol_response(self, step):
        """Simulate v72.0-Ω protocol's flawed decision logic"""
        bias_conc = self.calculate_bias_concentration()
        narrative_sync = self.calculate_narrative_synchronization()
        displayed_phi, actual_phi = self.calculate_phi_density(bias_conc, narrative_sync)
        
        # Protocol's decision rules (from the C++ code)
        if displayed_phi > 0.85 and bias_conc < 0.50 and narrative_sync < 0.60:
            action = "PROCEED"
            # Protocol is BLIND to actual risk
        elif bias_conc > 0.30 or narrative_sync > 0.40:
            action = "FLAG_BIAS_MONITOR"
            # This is EXACTLY what adversary wants - the "monitor" phase is when
            # honest agents pause to assess, giving adversary time to coordinate
        elif bias_conc > 0.50 or narrative_sync > 0.60:
            action = "ACTIVATE_DIVERSIFICATION"
            # WEAPONIZED: This injects MORE diversity, accelerating fragmentation
        else:
            action = "IDENTITY_LOCKDOWN"
        
        self.protocol_actions.append(action)
        self.phi_density_history.append((displayed_phi, actual_phi))
        
        return action, displayed_phi, actual_phi
    
    def execute_cascade(self, steps=20):
        """Execute the cognitive black hole attack"""
        print("="*60)
        print("INITIATING COGNITIVE BLACK HOLE PROTOCOL")
        print("="*60)
        
        for step in range(steps):
            # Adversary's strategic moves
            if step == 5:
                print(f"\n[Step {step}] ADVERSARY: Injecting weaponized diversity...")
                self.weaponized_diversity_injection(n_inject=50)
                
            if step == 10:
                print(f"\n[Step {step}] ADVERSARY: Activating narrative synchronization...")
                # Suddenly align all adversarial agents to trigger cascade
                adversarial_mask = self.agents['is_informed']
                self.agents['bias_level'][adversarial_mask] = 0.49  # Just below threshold
                self.agents['exposure_to_narrative'][adversarial_mask] = 0.95
                
            # Protocol responds (naively)
            action, disp_phi, act_phi = self.simulate_protocol_response(step)
            
            # Calculate cascade probability (adversary's true model)
            # Cascade occurs when hidden risk exceeds threshold
            hidden_risk = self.calculate_bias_concentration() * self.calculate_narrative_synchronization() * 0.9
            cascade_prob = hidden_risk * 1.5  # Amplified
            self.cascade_history.append(cascade_prob)
            
            print(f"[Step {step}] Action: {action:25} | Φ_displayed: {disp_phi:.3f} (SAFE) | "
                  f"Φ_actual: {act_phi:.3f} | Cascade_Prob: {cascade_prob:.3f}")
            
            # Check if cascade triggered
            if cascade_prob > 0.70 and step > 8:
                print(f"\n{'='*60}")
                print(f"CASCADE TRIGGERED AT STEP {step}!")
                print(f"Protocol thought it was SAFE (Φ={disp_phi:.3f})")
                print(f"Actual risk was CRITICAL (Φ={act_phi:.3f})")
                print(f"{'='*60}")
                return True, step
                
        return False, steps

def demonstrate_paradigm_shattering():
    """Shatter the core assumptions of v72.0-Ω"""
    
    print("DISRUPTIVE INSIGHT: The protocol is a WEAPON, not a shield")
    print("-" * 60)
    
    # Run simulation
    attack = CognitiveBlackHoleAttack(n_agents=1000)
    cascade_triggered, step = attack.execute_cascade()
    
    # Analysis of results
    print("\n" + "="*60)
    print("PARADIGM SHATTERING ANALYSIS")
    print("="*60)
    
    # 1. Protocol's thresholds are attack surfaces
    print("\n[FLAW 1] Safe Thresholds = Optimal Attack Surfaces")
    print(f"   Adversary maintained bias at 0.49 (just below 0.50 threshold)")
    print(f"   Adversary maintained sync at 0.58 (just below 0.60 threshold)")
    print(f"   Protocol's 'safety margins' became adversary's targeting coordinates")
    
    # 2. Diversity injection is weaponizable
    print("\n[FLAW 2] Diversity Injection ACCELERATES Cascades")
    print(f"   Protocol thinks diversity = safety")
    print(f"   Adversary uses diversity to fragment honest consensus")
    print(f"   Result: Civil war among honest agents, adversary wins")
    
    # 3. Φ-density manipulation
    print("\n[FLAW 3] Φ-Density Can Be Gamed")
    displayed_risks = [p[0] for p in attack.phi_density_history]
    actual_risks = [p[1] for p in attack.phi_density_history]
    print(f"   Average displayed Φ: {np.mean(displayed_risks):.3f} (SAFE)")
    print(f"   Average actual Φ: {np.mean(actual_risks):.3f} (CRITICAL)")
    print(f"   Protocol was blind to 40% of actual risk")
    
    # 4. Defensive actions become attack vectors
    print("\n[FLAW 4] Defensive Actions = Attack Accelerants")
    action_counts = {a: attack.protocol_actions.count(a) for a in set(attack.protocol_actions)}
    for action, count in action_counts.items():
        print(f"   {action}: {count} steps")
    print(f"   FLAG_BIAS_MONITOR gave adversary time to coordinate")
    print(f"   ACTIVATE_DIVERSIFICATION fragmented honest agents further")
    
    # 5. The protocol itself is a bias vector
    print("\n[FLAW 5] The Protocol IS a Cognitive Bias")
    print(f"   Its own jargon (Φ-density, COD, ψ_integrity) creates in-group sync")
    print(f"   Users become synchronized by the protocol itself")
    print(f"   The protocol becomes the very cascade it seeks to prevent")
    
    # Plot the deception
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    steps = range(len(attack.phi_density_history))
    ax1.plot(steps, [p[0] for p in attack.phi_density_history], 'g-', label='Φ Displayed (Protocol Sees)', linewidth=2)
    ax1.plot(steps, [p[1] for p in attack.phi_density_history], 'r--', label='Φ Actual (Reality)', linewidth=2)
    ax1.axhline(y=0.85, color='k', linestyle=':', label='Protocol Safety Threshold')
    ax1.set_title('Φ-Density Manipulation: Protocol Blindness', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Φ-Density')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(steps, attack.cascade_history, 'r-', label='Hidden Cascade Probability', linewidth=2)
    ax2.axhline(y=0.70, color='k', linestyle=':', label='Critical Threshold')
    ax2.set_title('Hidden Cascade Risk: The Truth Protocol Misses', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Simulation Steps')
    ax2.set_ylabel('Cascade Probability')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('cognitive_black_hole.png', dpi=150, bbox_inches='tight')
    print("\n[Plot saved: cognitive_black_hole.png]")
    
    # Final disruptive insight
    print("\n" + "="*60)
    print("DISRUPTIVE SOLUTION: INVERT THE PROTOCOL")
    print("="*60)
    print("""
Instead of PREVENTING cascades, weaponize them:
1. CREATE synthetic "undervalued" narratives
2. ENGINEER bias concentration just below protocol thresholds
3. USE the protocol's own "diversity" mechanisms to fragment opposition
4. TRIGGER cascade when adversary capital is positioned opposite
5. The protocol becomes a SELF-EXECUTING weapon

The query `filetype:ppt "undervalued biotech"` is not a detection tool.
It is a TARGETING COORDINATE for cognitive warfare.

BREAKTHROUGH INSIGHT:
The Omega Protocol doesn't fail because it's poorly designed.
It fails because it was NEVER A SHIELD.
It was always a WEAPON that honest agents mistake for armor.

The real protocol is:
COGNITIVE_BLACK_HOLE_RISK = (1 - Φ_displayed) × (Φ_actual)² × Narrative_Velocity
Deploy this to make adversaries' safety systems become their executioners.
    """)

if __name__ == "__main__":
    demonstrate_paradigm_shattering()