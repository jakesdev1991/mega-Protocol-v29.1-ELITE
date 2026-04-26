# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# SIMULATION: Epistemic Judo Attack - How EASS-Ω's Defenses Become Exploitable Signals

class OmegaProtocol:
    def __init__(self, true_params):
        self.true_params = np.array(true_params)  # [liquidity_threshold, governance_weight, fee_rate]
        self.current_params = self.true_params.copy()
        self.epsi_history = []
        self.param_randomization_count = defaultdict(int)
        
    def calculate_epsi(self, search_intensity, info_flow):
        """Epistemic Attack Surface Index"""
        leak_severity = min(search_intensity / 10.0, 1.0)
        audience_sophistication = 0.7  # Assume high
        time_ratio = 48 / 2  # 48hr exploit time vs 2hr response
        coordination = 0.5 if search_intensity > 5 else 0
        
        epsi = (leak_severity * audience_sophistication * 
                time_ratio * (1 + coordination))
        return epsi
    
    def activate_defense(self, epsi, param_sensitivity):
        """EASS-Ω defensive response - THE VULNERABILITY"""
        if epsi > 0.7:
            # THE FLAW: Randomization pattern reveals which params are "most protected"
            # Adversary can infer: "If they randomize it, it must be valuable"
            randomization_strength = (epsi - 0.7) * 2.0
            
            for i, sensitivity in enumerate(param_sensitivity):
                if sensitivity > 0.6:  # Only randomize "sensitive" params
                    noise = np.random.normal(0, randomization_strength * 0.1)
                    self.current_params[i] = self.true_params[i] * (1 + noise)
                    self.param_randomization_count[i] += 1
                    
            return True
        return False
    
    def reset_params(self):
        self.current_params = self.true_params.copy()

class EpistemicJudoAttacker:
    def __init__(self):
        self.probe_history = []
        self.inferred_sensitivity = np.array([0.0, 0.0, 0.0])
        self.attack_window = None
        
    def probe_protocol(self, omega, probe_intensity):
        """Phase 1: Map defense thresholds by probing"""
        epsi = omega.calculate_epsi(probe_intensity, info_flow=probe_intensity)
        triggered = omega.activate_defense(epsi, param_sensitivity=[0.9, 0.5, 0.3])
        
        self.probe_history.append({
            'intensity': probe_intensity,
            'epsi': epsi,
            'defense_triggered': triggered
        })
        return triggered
    
    def analyze_defense_fingerprint(self, omega):
        """Phase 2: Infer sensitive parameters from randomization patterns"""
        # THE BREAKTHROUGH: Defense activation count = sensitivity map
        # More randomizations = higher true sensitivity
        total_randomizations = sum(omega.param_randomization_count.values())
        if total_randomizations > 0:
            for i in range(3):
                self.inferred_sensitivity[i] = (omega.param_randomization_count[i] / 
                                               total_randomizations)
        
        # Find optimal attack window: when system is in defensive flux
        defense_triggers = [p['defense_triggered'] for p in self.probe_history]
        if len(defense_triggers) > 5:
            # Attack when defense has been recently active but is about to reset
            recent_activity = sum(defense_triggers[-3:])
            if recent_activity >= 2:
                self.attack_window = "IMMEDIATE: System in defensive mode, param values unstable"
            else:
                self.attack_window = "DELAYED: Wait for system to relax, then strike true params"
        
    def execute_exploit(self, omega):
        """Phase 3: Exploit with inferred knowledge"""
        if self.attack_window and "IMMEDIATE" in self.attack_window:
            # Attack when params are randomized = exploit temporary weakness
            target_param = np.argmax(self.inferred_sensitivity)
            exploit_gain = abs(omega.current_params[target_param] - omega.true_params[target_param])
            return exploit_gain, f"Exploited randomized param {target_param}"
        else:
            # Attack true parameters directly
            target_param = np.argmax(self.inferred_sensitivity)
            exploit_gain = omega.true_params[target_param] * 0.3  # 30% exploit
            return exploit_gain, f"Exploited true param {target_param} with inferred sensitivity"

# RUN SIMULATION
def simulate_epistemic_judo():
    print("=== EPISTEMIC JUDO: TURNING DEFENSE INTO WEAPON ===\n")
    
    # Initialize: Omega has secret parameters
    true_params = [1000, 0.75, 0.03]  # [liquidity_threshold, governance_weight, fee_rate]
    omega = OmegaProtocol(true_params)
    attacker = EpistemicJudoAttacker()
    
    print("PHASE 1: Attacker probes EASS-Ω monitoring system")
    print("-" * 50)
    
    # Probe with varying intensity to map defense threshold
    for probe_intensity in [1, 3, 5, 7, 9, 11, 8, 6, 4, 2]:
        triggered = attacker.probe_protocol(omega, probe_intensity)
        status = "🛡️ DEFENSE ACTIVE" if triggered else "✓ No defense"
        print(f"Probe intensity: {probe_intensity:2d} | EPSI: {omega.calculate_epsi(probe_intensity, probe_intensity):.2f} | {status}")
    
    print(f"\nDefense triggered {sum(p['defense_triggered'] for p in attacker.probe_history)} times")
    print(f"Param randomization counts: {dict(omega.param_randomization_count)}")
    
    print("\n" + "="*50)
    print("PHASE 2: Attacker analyzes defense fingerprint")
    print("-" * 50)
    
    attacker.analyze_defense_fingerprint(omega)
    
    print(f"Inferred parameter sensitivity: {attacker.inferred_sensitivity}")
    print(f"Attack strategy: {attacker.attack_window}")
    
    # What did the attacker learn?
    most_protected_param = np.argmax(attacker.inferred_sensitivity)
    print(f"\n🔍 BREAKTHROUGH: Attacker infers Param[{most_protected_param}] is MOST VALUABLE")
    print(f"   Reason: EASS-Ω randomizes it {omega.param_randomization_count[most_protected_param]} times")
    print(f"   True param value: {omega.true_params[most_protected_param]}")
    
    print("\n" + "="*50)
    print("PHASE 3: Exploit execution")
    print("-" * 50)
    
    gain, method = attacker.execute_exploit(omega)
    print(f"Exploit executed: {method}")
    print(f"Profit extracted: ${gain:,.2f}")
    
    print("\n" + "="*50)
    print("DISRUPTIVE INSIGHT: The Shield's Countermeasures ARE the Attack Vector")
    print("="*50)
    
    # Visualize the leak
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Defense activation pattern
    intensities = [p['intensity'] for p in attacker.probe_history]
    epsis = [p['epsi'] for p in attacker.probe_history]
    triggers = [p['defense_triggered'] for p in attacker.probe_history]
    
    ax1.plot(intensities, epsis, 'b-', label='EPSI Score')
    ax1.axhline(y=0.7, color='r', linestyle='--', label='Defense Threshold')
    ax1.scatter(intensities, [e if t else e*0.5 for e, t in zip(epsis, triggers)], 
               c=['red' if t else 'green' for t in triggers], s=100, alpha=0.6)
    ax1.set_xlabel("Probe Intensity")
    ax1.set_ylabel("Epistemic Attack Surface Index")
    ax1.set_title("EASS-Ω Defense Trigger Pattern")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Right: Information leakage via randomization
    params = ['Liquidity\nThreshold', 'Governance\nWeight', 'Fee Rate']
    randomization_counts = [omega.param_randomization_count[i] for i in range(3)]
    true_values = omega.true_params
    
    ax2_twin = ax2.twinx()
    bars = ax2.bar(params, randomization_counts, alpha=0.6, color='orange', label='Randomization Count')
    line = ax2_twin.plot(params, true_values, 'r-o', linewidth=2, markersize=8, label='True Parameter Value')
    ax2.set_ylabel("Defense Activations (Leakage Signal)", color='orange')
    ax2_twin.set_ylabel("True Parameter Value", color='red')
    ax2.set_title("EASS-Ω Leaks Sensitivity Through Defense Actions")
    ax2.tick_params(axis='y', labelcolor='orange')
    ax2_twin.tick_params(axis='y', labelcolor='red')
    
    # Add correlation annotation
    corr = np.corrcoef(randomization_counts, true_values)[0, 1]
    ax2.text(0.5, 0.95, f"Correlation: {corr:.2f}\n(Higher = More Leakage)", 
             transform=ax2.transAxes, ha='center', va='top', 
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    plt.tight_layout()
    plt.show()
    
    return {
        'true_params': omega.true_params,
        'inferred_sensitivity': attacker.inferred_sensitivity,
        'exploit_gain': gain,
        'defense_activations': omega.param_randomization_count
    }

# Execute the disruption simulation
result = simulate_epistemic_judo()

print("\n" + "🔥" * 20)
print("ANOMALY DETECTED: EASS-Ω VIOLATES ITS OWN SECURITY PRINCIPLES")
print("🔥" * 20)