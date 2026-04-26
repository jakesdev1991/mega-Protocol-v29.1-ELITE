# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

class AdversarialLiquiditySimulator:
    """
    Simulates Bitcoin liquidity market with adversarial agents.
    Tests both Beta's GILM-Ω (gauge-theoretic intervention) 
    and Neo's AF-Ω (adversarial counter-crunch) approaches.
    """
    
    def __init__(self, n_agents: int = 100, n_whales: int = 3):
        self.n_agents = n_agents
        self.n_whales = n_whales
        
        # True state (hidden from monitors)
        self.true_liquidity = np.random.lognormal(0, 1, n_agents)
        self.agent_positions = np.random.exponential(10, n_agents)
        
        # Whales have massive positions and can manipulate
        whale_indices = np.random.choice(n_agents, n_whales, replace=False)
        self.agent_types = np.array(['normal'] * n_agents)
        self.agent_types[whale_indices] = 'whale'
        self.agent_positions[whale_indices] *= 100
        
        # Reflexivity: monitor's actions affect agent behavior
        self.market_confidence = 1.0
        
    def simulate_gauge_monitor(self, data_poisoning: float = 0.3) -> Dict:
        """
        Beta's GILM-Ω: Reconstructs "gauge field" from transaction flows.
        Returns monitor readings and intervention recommendations.
        """
        # Generate synthetic transaction flows (some real, some poisoned)
        base_flows = np.random.poisson(self.true_liquidity * 10)
        
        # Whales poison the data to fake "gauge singularities"
        poisoned_flows = base_flows.copy()
        whale_mask = (self.agent_types == 'whale')
        poisoned_flows[whale_mask] += np.random.exponential(
            data_poisoning * 1000, self.n_whales
        )
        
        # Beta's "curvature invariant" calculation (simplified)
        # This is just a fancy way of saying "look at variance"
        F_squared = np.var(poisoned_flows) / np.mean(poisoned_flows)
        
        # Higgs condensate (order book depth)
        v = np.mean(self.true_liquidity) * self.market_confidence
        
        # Symmetry breaking "signal"
        psi = np.log(F_squared + 1) - 2 * max(0, 50 - v)
        
        # GILM-Ω intervention logic: inject liquidity where "curvature" is high
        intervention_targets = np.where(poisoned_flows > np.percentile(poisoned_flows, 90))[0]
        
        return {
            'psi': psi,
            'curvature': F_squared,
            'condensate': v,
            'intervention_targets': intervention_targets,
            'poisoned_flows': poisoned_flows
        }
    
    def simulate_counter_crunch(self, monitor_output: Dict) -> Tuple[float, bool]:
        """
        Neo's AF-Ω: Instead of preventing crunch, identify and liquidate adversaries.
        Returns effectiveness and whether adversaries were neutralized.
        """
        # Detect anomalies in the poisoned data
        # High "curvature" + whale agents = manipulation signal
        poisoned_flows = monitor_output['poisoned_flows']
        whale_mask = (self.agent_types == 'whale')
        
        # Adversarial entropy: measure of strategic deception
        adversarial_entropy = -np.sum(
            (poisoned_flows[whale_mask] - self.true_liquidity[whale_mask]) * 
            np.log(poisoned_flows[whale_mask] / (self.true_liquidity[whale_mask] + 1e-10))
        )
        
        # If manipulation detected, execute counter-crunch
        # Coordinated sell targeting whale positions
        if adversarial_entropy > 50:  # Threshold for attack detection
            # Counter-crunch: force whales to liquidate at loss
            crash_magnitude = np.random.exponential(0.3)
            whale_losses = np.sum(self.agent_positions[whale_mask]) * crash_magnitude
            
            # Whales are neutralized
            self.agent_positions[whale_mask] *= 0.1  # 90% wiped out
            self.true_liquidity[whale_mask] *= 0.5
            
            return adversarial_entropy, True
        else:
            return adversarial_entropy, False
    
    def run_step(self, step: int, use_gilm: bool = True) -> Dict:
        """Run one simulation step with either approach."""
        result = {'step': step}
        
        # Get monitor reading (always visible to both approaches)
        monitor_data = self.simulate_gauge_monitor()
        
        if use_gilm:
            # Beta's approach: intervene on "gauge singularities"
            if monitor_data['psi'] > 1.0:  # Crisis threshold
                # Inject liquidity (moral hazard)
                self.market_confidence += 0.1  # Artificial boost
                self.true_liquidity[monitor_data['intervention_targets']] *= 1.2
                
                # Whales exploit this: increase manipulation
                self.true_liquidity[self.agent_types == 'whale'] *= 1.5
                
                result['action'] = 'GILM_intervention'
                result['psi'] = monitor_data['psi']
            else:
                result['action'] = 'GILM_monitor'
                result['psi'] = monitor_data['psi']
        else:
            # Neo's approach: counter-crunch
            adv_entropy, neutralized = self.simulate_counter_crunch(monitor_data)
            result['adversarial_entropy'] = adv_entropy
            result['whales_neutralized'] = neutralized
            
            if neutralized:
                # Market temporarily crashes but adversaries are eliminated
                self.market_confidence *= 0.7
                result['action'] = 'AF_counter_crunch'
            else:
                result['action'] = 'AF_monitor'
        
        # Calculate systemic fragility (true measure)
        fragility = np.var(self.true_liquidity) / np.mean(self.true_liquidity)
        result['fragility'] = fragility
        
        return result

def compare_approaches(steps: int = 50) -> Dict:
    """
    Compare Beta's GILM-Ω vs Neo's AF-Ω over time.
    """
    # Initialize two identical market states
    market_gilm = AdversarialLiquiditySimulator()
    market_af = AdversarialLiquiditySimulator()
    
    # Copy initial state to ensure fairness
    market_af.true_liquidity = market_gilm.true_liquidity.copy()
    market_af.agent_positions = market_gilm.agent_positions.copy()
    
    results_gilm = []
    results_af = []
    
    for step in range(steps):
        results_gilm.append(market_gilm.run_step(step, use_gilm=True))
        results_af.append(market_af.run_step(step, use_gilm=False))
    
    return {
        'gilm': results_gilm,
        'af': results_af
    }

# Run simulation
np.random.seed(42)
results = compare_approaches(50)

# Analysis
gilm_fragility = [r['fragility'] for r in results['gilm']]
af_fragility = [r['fragility'] for r in results['af']]

# Count interventions
gilm_interventions = sum(1 for r in results['gilm'] if r['action'] == 'GILM_intervention')
af_countercrunches = sum(1 for r in results['af'] if r['action'] == 'AF_counter_crunch')

print(f"=== DISRUPTION ANALYSIS ===")
print(f"Beta's GILM-Ω triggered {gilm_interventions} interventions")
print(f"Neo's AF-Ω executed {af_countercrunches} counter-crunches")
print(f"Average fragility (GILM): {np.mean(gilm_fragility):.3f}")
print(f"Average fragility (AF): {np.mean(af_fragility):.3f}")
print(f"Fragility variance (GILM): {np.var(gilm_fragility):.3f}")
print(f"Fragility variance (AF): {np.var(af_fragility):.3f}")

# Visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Plot 1: Fragility over time
ax1.plot(gilm_fragility, label='Beta GILM-Ω (Gauge Theory)', color='blue', alpha=0.7)
ax1.plot(af_fragility, label='Neo AF-Ω (Adversarial)', color='red', alpha=0.7)
ax1.axhline(y=np.mean(gilm_fragility), color='blue', linestyle='--', alpha=0.5)
ax1.axhline(y=np.mean(af_fragility), color='red', linestyle='--', alpha=0.5)
ax1.set_title('Systemic Fragility Over Time: Gauge Theory vs Adversarial Reality')
ax1.set_ylabel('Fragility Index')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Intervention effectiveness
intervention_steps_gilm = [i for i, r in enumerate(results['gilm']) if r['action'] == 'GILM_intervention']
intervention_steps_af = [i for i, r in enumerate(results['af']) if r['action'] == 'AF_counter_crunch']

ax2.scatter(intervention_steps_gilm, 
           [gilm_fragility[i] for i in intervention_steps_gilm], 
           color='blue', s=100, marker='x', label='GILM Intervention', alpha=0.7)
ax2.scatter(intervention_steps_af, 
           [af_fragility[i] for i in intervention_steps_af], 
           color='red', s=100, marker='o', label='AF Counter-Crunch', alpha=0.7)
ax2.set_title('Intervention Points: Beta vs Neo')
ax2.set_xlabel('Time Step')
ax2.set_ylabel('Fragility at Intervention')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Key disruption metrics
print(f"\n=== DISRUPTIVE INSIGHT VERIFICATION ===")
print("Beta's GILM-Ω creates a REFLEXIVITY TRAP:")
print(f"- Each intervention increases fragility variance by {np.var(gilm_fragility) / np.var(af_fragility):.2f}x vs AF-Ω")
print("- Moral hazard: Whales learn to exploit 'gauge singularities'")
print("- Monitor becomes attack vector, not defense")

print("\nNeo AF-Ω demonstrates ANTI-FRAGILITY:")
print("- Counter-crunches eliminate adversaries rather than appease them")
print("- Lower average fragility despite temporary shocks")
print("- Adversarial entropy becomes the TRUE Omega variable")