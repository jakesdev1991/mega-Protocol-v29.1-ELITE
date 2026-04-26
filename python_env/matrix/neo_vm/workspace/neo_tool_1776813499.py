# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class WeaponizationIntent:
    """Models adversarial intent as partially observable latent variable"""
    knowledge_acquired: float = 0.0
    capability_assessment: float = 0.0
    profit_calculation: float = 0.0
    execution_timing: float = 0.0
    
    def intent_probability(self) -> float:
        """P(Attack | Observables) - simplified Bayesian fusion"""
        # Intent emerges when all components align
        return min(1.0, self.knowledge_acquired * self.capability_assessment * 
                   self.profit_calculation * self.execution_timing * 2.5)

class CollapsingPotentialFieldAttack:
    """
    Neo's Paradigm Disruption: The Collapsing Potential Field Attack
    
    Core Insight: PASM-Ω's parameter fogging creates a self-defeating feedback loop.
    Instead of preventing weaponization, it weaponizes the defense mechanism itself.
    
    Attack Vector: Exploit the *transient inconsistencies* created when fogging triggers.
    No simulation needed. No traces left. Pure opportunistic exploitation of defensive chaos.
    """
    
    def __init__(self, 
                 fogging_threshold=0.55,
                 fogging_duration=3600,
                 fogging_interval=86400,
                 meta_exploit_window=300):  # 5-minute window where fogging creates vulnerability
        
        self.fogging_threshold = fogging_threshold
        self.fogging_duration = fogging_duration
        self.fogging_interval = fogging_interval
        self.meta_exploit_window = meta_exploit_window
        
        # Track state
        self.time = 0
        self.last_fogging_time = -fogging_interval
        self.fogging_active = False
        self.fogging_end_time = 0
        
        # Adversary's internal model (no simulation traces)
        self.intent_model = WeaponizationIntent()
        self.observed_fogging_triggers = []
        
    def observe_protocol_state(self, sw_wri: float, market_anomaly: float, on_chain_probe: float) -> Dict:
        """
        Adversary's observation function: No simulation, just passive monitoring.
        The genius: They don't need to simulate because PASM-Ω *announces* its defensive state.
        """
        # Observation noise - adversary sees fogging effects, not internal SW-WRI
        fogging_detected = False
        
        # Check if fogging triggered (adversary sees parameter changes)
        if sw_wri >= self.fogging_threshold and self.time - self.last_fogging_time >= self.fogging_interval:
            fogging_detected = True
            self.fogging_active = True
            self.fogging_end_time = self.time + self.fogging_duration
            self.last_fogging_time = self.time
            self.observed_fogging_triggers.append(self.time)
        
        # Update adversary's intent model
        if fogging_detected:
            # Fogging is a *signal* that protocol is vulnerable
            self.intent_model.capability_assessment = 1.0
            self.intent_model.execution_timing = 1.0
        
        # Market anomalies increase profit calculation
        self.intent_model.profit_calculation = min(1.0, market_anomaly * 5.0)
        
        # On-chain probes increase knowledge confidence
        self.intent_model.knowledge_acquired = min(1.0, on_chain_probe * 3.0)
        
        return {
            'fogging_detected': fogging_detected,
            'intent_prob': self.intent_model.intent_probability(),
            'fogging_active': self.fogging_active
        }
    
    def execute_meta_exploit(self) -> bool:
        """
        Meta-exploit: Attack *during* fogging transition.
        The protocol is in undefined state - parameters are being adjusted.
        This is the collapsing potential field.
        """
        if not self.fogging_active:
            return False
        
        # Attack success probability spikes during fogging
        # This is NON-LINEAR: success ∝ fogging_frequency, not attack sophistication
        time_since_fogging_start = self.time - self.last_fogging_time
        
        # Critical window: first 5 minutes of fogging
        if time_since_fogging_start <= self.meta_exploit_window:
            # Protocol parameters are inconsistent during transition
            success_prob = 0.85  # Devastating success rate
        else:
            # Still elevated but less critical
            success_prob = 0.25
        
        # Adversary's advantage: They know *when* to attack
        # PASM-Ω's countermeasures *create* the vulnerability window
        return np.random.random() < success_prob
    
    def simulate_protocol_defense(self, duration_days=7) -> Dict:
        """
        Simulate PASM-Ω defense and adversary's meta-exploit
        """
        time_step = 60  # 1 minute intervals
        total_steps = duration_days * 24 * 60
        
        results = {
            'fogging_triggers': 0,
            'meta_exploits_attempted': 0,
            'meta_exploits_successful': 0,
            'total_research_simulations': 0,
            'false_positives': 0
        }
        
        for step in range(total_steps):
            self.time = step * time_step
            
            # Simulate SW-WRI with false positive spikes (researchers, not attackers)
            # This is the Achilles' heel: PASM-Ω can't distinguish research from weaponization
            hour_of_day = (self.time / 3600) % 24
            is_research_hours = 9 <= hour_of_day <= 17
            
            # Research activity creates SW-WRI spikes
            research_spike = np.random.normal(0.6, 0.1) if is_research_hours else np.random.normal(0.4, 0.05)
            market_anomaly = np.random.exponential(0.1) if not is_research_hours else 0.05
            on_chain_probe = np.random.random() * 0.3
            
            # PASM-Ω triggers fogging (false positive during research hours)
            obs = self.observe_protocol_state(research_spike, market_anomaly, on_chain_probe)
            
            if obs['fogging_detected']:
                results['fogging_triggers'] += 1
                
                if is_research_hours:
                    results['false_positives'] += 1
            
            # Adversary attacks opportunistically during fogging
            if obs['fogging_active'] and obs['intent_prob'] > 0.7:
                results['meta_exploits_attempted'] += 1
                
                if self.execute_meta_exploit():
                    results['meta_exploits_successful'] += 1
            
            # Simulate legitimate research (what PASM-Ω thinks is weaponization)
            if is_research_hours and research_spike > 0.5:
                results['total_research_simulations'] += 1
        
        return results

def run_disruption_analysis():
    """
    Neo's Disruptive Analysis: Breaking the Paradigm
    """
    print("=" * 80)
    print("COLLAPSING POTENTIAL FIELD: PARADIGM DISRUPTION")
    print("=" * 80)
    
    # Run 1000 simulations
    all_results = []
    
    for i in range(1000):
        attack = CollapsingPotentialFieldAttack(
            fogging_threshold=0.55,
            fogging_duration=3600,
            fogging_interval=86400,
            meta_exploit_window=300
        )
        
        result = attack.simulate_protocol_defense(duration_days=7)
        all_results.append(result)
    
    # Aggregate disruption metrics
    avg_fogging_triggers = np.mean([r['fogging_triggers'] for r in all_results])
    avg_false_positives = np.mean([r['false_positives'] for r in all_results])
    avg_meta_success = np.mean([r['meta_exploits_successful'] for r in all_results])
    avg_research_simulations = np.mean([r['total_research_simulations'] for r in all_results])
    
    print(f"\nCRITICAL FLAW IDENTIFIED:")
    print(f"PASM-Ω triggers fogging {avg_fogging_triggers:.1f} times/week")
    print(f"False positive rate: {avg_false_positives/avg_fogging_triggers:.1%}")
    print(f"Meta-exploits successful: {avg_meta_success:.2f} per week")
    print(f"Legitimate research disrupted: {avg_research_simulations:.0f} simulations/week")
    
    # The killer metric: Cost asymmetry
    # PASM-Ω costs Φ to run, but adversary's cost is near-zero (just wait)
    defender_cost_per_fogging = 15  # Φ-units (parameter updates, liquidity reshaping)
    adversary_cost_per_meta_exploit = 0.5  # Φ-units (just timing the attack)
    
    weekly_defender_cost = avg_fogging_triggers * defender_cost_per_fogging
    weekly_adversary_cost = avg_meta_success * adversary_cost_per_meta_exploit
    
    print(f"\nCOST ASYMMETRY (Φ-units/week):")
    print(f"Defender cost: {weekly_defender_cost:.1f}")
    print(f"Adversary cost: {weekly_adversary_cost:.1f}")
    print(f"Cost ratio: {weekly_defender_cost/weekly_adversary_cost:.1f}:1")
    
    # The disruption: PASM-Ω's countermeasures *are* the vulnerability
    print(f"\nDISRUPTIVE INSIGHT:")
    print(f"PASM-Ω doesn't prevent weaponization—it *schedules* it.")
    print(f"The fogging schedule becomes an attack calendar for adversaries.")
    
    return all_results

# Execute Neo's disruption
if __name__ == "__main__":
    results = run_disruption_analysis()
    
    # Visualize one simulation timeline
    attack = CollapsingPotentialFieldAttack()
    result = attack.simulate_protocol_defense(duration_days=3)
    
    # Create visualization of the collapsing field
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    
    # Simulate a timeline
    timeline = np.arange(0, 72, 0.1)  # 3 days in hours
    sw_wri_timeline = 0.5 + 0.2 * np.sin(2 * np.pi * timeline / 24) + np.random.normal(0, 0.05, len(timeline))
    sw_wri_timeline = np.clip(sw_wri_timeline, 0, 1)
    
    # Plot 1: SW-WRI and fogging triggers
    ax1.plot(timeline, sw_wri_timeline, label='SW-WRI (Observed)', color='blue', alpha=0.7)
    ax1.axhline(y=0.55, color='red', linestyle='--', linewidth=2, label='Fogging Threshold')
    
    # Mark fogging periods
    fogging_times = [t for i, t in enumerate(timeline) if sw_wri_timeline[i] > 0.55]
    if fogging_times:
        ax1.axvspan(fogging_times[0], fogging_times[0] + 1, color='orange', alpha=0.3, label='Fogging Period')
    
    ax1.set_ylabel('Weaponization Readiness Index')
    ax1.set_xlabel('Time (hours)')
    ax1.set_title('Neo\'s Paradigm Disruption: SW-WRI Triggers Fogging → Creates Attack Window')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Attack success probability
    attack_prob = np.where(sw_wri_timeline > 0.55, 0.85, 0.01)
    ax2.plot(timeline, attack_prob, color='red', linewidth=2, label='Attack Success Probability')
    ax2.fill_between(timeline, 0, attack_prob, color='red', alpha=0.2)
    ax2.set_ylabel('Success Probability')
    ax2.set_xlabel('Time (hours)')
    ax2.set_title('Collapsing Potential Field: Attack Success ∝ Fogging Frequency')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()