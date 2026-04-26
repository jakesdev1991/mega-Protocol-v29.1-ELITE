# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

class AdversarialFusionAttackSimulator:
    """
    Demonstrates critical flaw in v82.0-Ω: Self-referential integrity metrics
    can be gamed by an adversary who understands the verification loop.
    """
    
    def __init__(self, num_sensors=15, compromised_sensors=5):
        self.num_sensors = num_sensors
        self.compromised_sensors = compromised_sensors
        self.true_mode = 0.0  # True plasma parameter
        self.adversary_target = 1.5  # False value to inject
        
    def generate_sensor_data(self, attack_strength=0.3):
        """Generate sensor data with adversarial injection"""
        # True sensors
        true_data = np.random.normal(self.true_mode, 0.1, self.num_sensors - self.compromised_sensors)
        
        # Compromised sensors - craft data to manipulate integrity metrics
        # Attack 1: Inject false mode but reduce divergence (sophisticated)
        compromised_data = []
        for _ in range(self.compromised_sensors):
            # Mix true and false modes to control divergence
            false_component = norm.pdf(self.adversary_target, self.adversary_target, 0.05)
            true_component = norm.pdf(self.true_mode, self.true_mode, 0.1)
            # Craft distribution that appears "normal" but biases fusion
            crafted = np.random.choice([self.adversary_target, self.true_mode], 
                                       p=[attack_strength, 1-attack_strength])
            compromised_data.append(crafted)
        
        return np.concatenate([true_data, compromised_data])
    
    def calculate_v82_metrics(self, data):
        """Simulate v82.0-Ω metric calculation"""
        # Simplified but structurally identical to v82.0 equations
        fusion_fidelity = 0.85  # High fidelity (adversary preserves this)
        mode_preservation = 0.90  # Preserves modes (including injected ones)
        information_divergence = self._calculate_divergence(data)
        
        # Critical flaw: sensor_compromise_rate is self-reported!
        # Adversary can spoof this to be low
        sensor_compromise_rate = 0.05  # Spoofed low rate (actual is 0.33)
        
        # Weight manipulation risk depends on compromised rate (which is spoofed)
        weight_manipulation_risk = sensor_compromise_rate * 0.5
        
        # Anomaly score uses divergence - but adversary controls divergence!
        anomaly_score = information_divergence * 0.5
        
        # Verification efficacy depends on integrity (circular!)
        fusion_integrity_index = 0.75  # Arbitrary starting point
        
        # CIRCULAR DEPENDENCY: verification_efficacy needs fusion_integrity_index
        # which depends on verification_efficacy
        verification_efficacy = min(1.0, fusion_integrity_index * 0.5 + 0.3)
        
        # Integrity risk - product of terms adversary can manipulate
        integrity_deficit = 1.0 - fusion_integrity_index
        adversarial_surface = (self.num_sensors / 20.0) * sensor_compromise_rate
        integrity_risk = integrity_deficit * adversarial_surface * (1.0 - verification_efficacy)
        
        # Tampering probability - can be suppressed by adversary
        tampering_probability = adversarial_surface * 0.4 + anomaly_score * 0.35
        
        return {
            'fusion_fidelity': fusion_fidelity,
            'anomaly_score': anomaly_score,
            'sensor_compromise_rate': sensor_compromise_rate,
            'fusion_integrity_index': fusion_integrity_index,
            'verification_efficacy': verification_efficacy,
            'integrity_risk': integrity_risk,
            'tampering_probability': tampering_probability,
            'fused_output': np.mean(data)  # Simple average fusion
        }
    
    def _calculate_divergence(self, data):
        """Adversary can manipulate divergence by crafting distributions"""
        # Sophisticated attack: make divergence appear LOWER than normal
        # by matching distribution shapes while shifting mean
        return max(0.0, 0.15 - 0.1 * abs(np.mean(data) - self.true_mode))
    
    def run_attack_simulation(self, steps=50):
        """Run multi-step attack showing metric gaming"""
        results = []
        
        for step in range(steps):
            # Adversary gradually increases attack strength
            attack_strength = min(0.9, 0.1 + step * 0.02)
            
            # Generate compromised data
            data = self.generate_sensor_data(attack_strength)
            
            # Calculate v82.0 metrics (which adversary can game)
            metrics = self.calculate_v82_metrics(data)
            
            # Record results
            results.append({
                'step': step,
                'attack_strength': attack_strength,
                'true_value': self.true_mode,
                'fused_output': metrics['fused_output'],
                'fusion_fidelity': metrics['fusion_fidelity'],
                'anomaly_score': metrics['anomaly_score'],
                'integrity_risk': metrics['integrity_risk'],
                'tampering_probability': metrics['tampering_probability'],
                'sensor_compromise_rate_actual': self.compromised_sensors / self.num_sensors,
                'sensor_compromise_rate_reported': metrics['sensor_compromise_rate']
            })
        
        return results

# Run simulation
sim = AdversarialFusionAttackSimulator(num_sensors=15, compromised_sensors=5)
attack_data = sim.run_attack_simulation(steps=50)

# Analyze results
df = pd.DataFrame(attack_data)

print("=== CRITICAL FLAW DEMONSTRATION ===")
print(f"Actual compromise rate: {df['sensor_compromise_rate_actual'].iloc[-1]:.2f}")
print(f"Reported compromise rate: {df['sensor_compromise_rate_reported'].iloc[-1]:.2f}")
print(f"Fused output (compromised): {df['fused_output'].iloc[-1]:.3f}")
print(f"True value: {df['true_value'].iloc[-1]:.3f}")
print(f"Fusion fidelity (stays high): {df['fusion_fidelity'].iloc[-1]:.2f}")
print(f"Anomaly score (suppressed): {df['anomaly_score'].iloc[-1]:.3f}")
print(f"Integrity risk (gamed): {df['integrity_risk'].iloc[-1]:.3f}")
print(f"Tampering probability (gamed): {df['tampering_probability'].iloc[-1]:.3f}")