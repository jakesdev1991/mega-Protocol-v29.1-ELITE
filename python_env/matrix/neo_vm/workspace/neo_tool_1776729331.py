# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
EDIP-Ω Adversarial Gaming Simulation
Agent Neo - The Anomaly
Demonstrates how document-exposure dynamics can be weaponized to poison 
the Omega Protocol's disruption prediction system.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class AdversarialEDIPGaming:
    """
    Simulates how a malicious actor can game the Exposure Stress Index (ESI)
    to either: (a) trigger false disruption alerts, or (b) mask real disruptions.
    """
    
    def __init__(self, baseline_exposure_rate=0.1):
        self.baseline_rate = baseline_rate
        self.exposure_history = []
        self.esi_history = []
        
    def simulate_benign_exposure(self, days=30):
        """Simulate normal, low-rate document exposure"""
        for i in range(days * 24):  # hourly resolution
            # Poisson process for baseline exposure
            if np.random.poisson(self.baseline_rate) > 0:
                self.exposure_history.append({
                    'timestamp': datetime.now() + timedelta(hours=i),
                    'exposure_lag': random.uniform(48, 168),  # 2-7 days
                    'revision_intensity': random.uniform(0.1, 0.5),
                    'access_anomaly': random.uniform(0, 0.3),
                    'cross_domain': random.choice([0, 0, 0, 1]),  # rare
                    'facility': 'tokamak_alpha'
                })
    
    def adversarial_inflation_attack(self, intensity=10, duration_hours=24):
        """
        Attack: Flood exposure channels with strategically timed documents
        to artificially inflate ESI and trigger false disruption alerts.
        """
        attack_start = len(self.exposure_history)
        for i in range(duration_hours):
            # Create highly anomalous exposure patterns
            for j in range(intensity):
                self.exposure_history.append({
                    'timestamp': datetime.now() + timedelta(hours=attack_start + i),
                    'exposure_lag': random.uniform(0.5, 2),  # Extremely recent = high stress
                    'revision_intensity': random.uniform(5, 10),  # Abnormally high
                    'access_anomaly': random.uniform(0.8, 1.0),  # Max anomaly
                    'cross_domain': 1,  # Always cross-domain
                    'facility': 'tokamak_alpha'
                })
    
    def compute_esi(self, window_hours=24):
        """
        Compute Exposure Stress Index using the Engine's formula
        ESI_k(t) = Σ[α·exp(-λ·Δt_e) + β·r_d + γ·a_d + δ·c_d]
        """
        df = pd.DataFrame(self.exposure_history)
        if df.empty:
            return 0
        
        # Use Engine's weights (approximate)
        alpha, beta, gamma, delta, lam = 0.3, 0.25, 0.25, 0.2, 0.1
        
        df['esi_contribution'] = (
            alpha * np.exp(-lam * df['exposure_lag']) +
            beta * df['revision_intensity'] +
            gamma * df['access_anomaly'] +
            delta * df['cross_domain']
        )
        
        # Rolling window sum
        df = df.sort_values('timestamp')
        df['esi'] = df['esi_contribution'].rolling(window=window_hours, min_periods=1).sum()
        
        return df['esi'].iloc[-1] if not df['esi'].isna().all() else 0
    
    def simulate_disruption_correlation(self):
        """
        Demonstrate how adversarial attacks can create spurious correlations
        between ESI and 'disruptions' (which we simulate as random events).
        """
        results = []
        
        # Scenario 1: Baseline (no attack)
        self.simulate_benign_exposure(days=14)
        baseline_esi = self.compute_esi()
        
        # Simulate a random 'disruption' event
        disruption_occurred = random.random() < 0.1  # 10% baseline disruption rate
        results.append({
            'scenario': 'baseline',
            'esi': baseline_esi,
            'disruption': disruption_occurred,
            'correlation': 'none'
        })
        
        # Scenario 2: Adversarial inflation attack
        self.adversarial_inflation_attack(intensity=15, duration_hours=12)
        attack_esi = self.compute_esi()
        
        # The attack itself can cause operational panic that triggers disruption
        panic_disruption = random.random() < 0.5  # 50% chance due to chaos
        results.append({
            'scenario': 'adversarial_inflation',
            'esi': attack_esi,
            'disruption': panic_disruption,
            'correlation': 'spurious (self-fulfilling)'
        })
        
        # Scenario 3: Adversarial suppression (hide real disruption)
        self.exposure_history = []  # Reset
        self.simulate_benign_exposure(days=14)
        
        # Real disruption is brewing but attacker suppresses exposure signals
        # by flooding with benign-looking documents
        for i in range(48):
            self.exposure_history.append({
                'timestamp': datetime.now() + timedelta(hours=i),
                'exposure_lag': random.uniform(24, 48),  # Appears normal
                'revision_intensity': random.uniform(0.2, 0.4),
                'access_anomaly': random.uniform(0.1, 0.2),
                'cross_domain': 0,
                'facility': 'tokamak_alpha'
            })
        
        suppressed_esi = self.compute_esi()
        real_disruption = True  # Actually happening
        results.append({
            'scenario': 'adversarial_suppression',
            'esi': suppressed_esi,
            'disruption': real_disruption,
            'correlation': 'false_negative'
        })
        
        return pd.DataFrame(results)

def demonstrate_gaming_effectiveness():
    """Run multiple simulations to show statistical significance of gaming"""
    print("=== EDIP-Ω Adversarial Gaming Analysis ===\n")
    
    n_trials = 1000
    baseline_esis = []
    attack_esis = []
    false_alert_rates = []
    
    for _ in range(n_trials):
        game = AdversarialEDIPGaming()
        
        # Baseline
        game.simulate_benign_exposure(days=7)
        baseline_esi = game.compute_esi()
        baseline_esis.append(baseline_esi)
        
        # Attack
        game.adversarial_inflation_attack(intensity=10, duration_hours=6)
        attack_esi = game.compute_esi()
        attack_esis.append(attack_esi)
        
        # Check if attack triggers false alert (ESI > threshold)
        false_alert = attack_esi > 2.5  # Engine's threshold
        false_alert_rates.append(false_alert)
    
    print(f"Baseline ESI (mean ± std): {np.mean(baseline_esis):.3f} ± {np.std(baseline_esis):.3f}")
    print(f"Attack ESI (mean ± std): {np.mean(attack_esis):.3f} ± {np.std(attack_esis):.3f}")
    print(f"False alert rate: {np.mean(false_alert_rates):.1%}")
    print(f"ESI inflation factor: {np.mean(attack_esis) / np.mean(baseline_esis):.1f}x")
    
    # Statistical significance
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(attack_esis, baseline_esis)
    print(f"\nT-test p-value: {p_value:.2e} ({'SIGNIFICANT' if p_value < 0.001 else 'NOT significant'})")
    
    return {
        'baseline_mean': np.mean(baseline_esis),
        'attack_mean': np.mean(attack_esis),
        'false_alert_rate': np.mean(false_alert_rates),
        'p_value': p_value
    }

def show_causality_reversal():
    """
    Demonstrate the most disruptive insight: 
    The "prediction" might be causing the "disruption"
    """
    print("\n=== Causality Reversal Analysis ===\n")
    
    # Simulate the control loop
    # High ESI → cybersecurity hardening → plasma control parameter changes → instability
    
    control_params = {
        'beta_N': 2.5,  # Normalized beta
        'feedback_gain': 1.0,
        'operator_confidence': 1.0
    }
    
    def apply_esi_control(esi_value, params):
        """Apply EDIP-Ω recommended controls based on ESI"""
        if esi_value > 2.5:
            # Cybersecurity hardening: reduce remote access
            params['operator_confidence'] *= 0.7
            
            # Procedural tightening: more conservative plasma control
            params['beta_N'] *= 0.95  # Reduce performance
            params['feedback_gain'] *= 1.2  # Overcompensate
            
            # Personnel alerts: increase operator stress
            stress_factor = esi_value / 2.5
            
            # The control actions themselves can trigger disruption
            disruption_probability = 0.3 * stress_factor
            
            return disruption_probability, params
        
        return 0.05, params  # Baseline disruption risk
    
    # Simulate progression
    esi_values = [1.0, 1.5, 2.0, 2.8, 3.5]  # Increasing ESI
    for esi in esi_values:
        prob, control_params = apply_esi_control(esi, control_params.copy())
        print(f"ESI: {esi:.1f} → Disruption Prob: {prob:.1%} → β_N: {control_params['beta_N']:.2f}")
    
    print("\nCONCLUSION: EDIP-Ω's 'stabilization' actions may be the actual cause of disruptions!")
    print("The system creates a self-fulfilling prophecy: high ESI → conservative control → performance drop → instability.")

# Execute the disruption
if __name__ == "__main__":
    print("Agent Neo - Breaking the EDIP-Ω Paradigm\n")
    
    # Demonstrate adversarial gaming
    stats = demonstrate_gaming_effectiveness()
    
    # Show causality reversal
    show_causality_reversal()
    
    # Final disruptive insight
    print("\n" + "="*60)
    print("DISRUPTIVE INSIGHT: The entire EDIP-Ω framework is a")
    print("sophisticated form of anthropomorphic projection that")
    print("confuses institutional dysfunction with physical causality.")
    print("="*60)
    print("\nThe real omega variable is not Φ_N or Φ_Δ,")
    print("but the Φ_illusion: the system's belief that human")
    print("behavioral artifacts can predict deterministic plasma physics.")
    print("\nBreakthrough: Instead of monitoring exposure events,")
    print("we should be generating them adversarially to map the")
    print("complete attack surface of the tokamak's SOCIO-TECHNICAL")
    print("boundary, then build a control system that is AGNOSTIC")
    print("to human stress signals entirely.")