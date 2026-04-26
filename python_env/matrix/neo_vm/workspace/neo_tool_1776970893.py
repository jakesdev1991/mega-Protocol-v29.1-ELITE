# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_resonance_cage():
    """
    Simulates the "Resonance Cage" failure mode:
    High COD + Low Entropy = Trapped non-decision state
    """
    # Simulation parameters
    time_steps = 100
    n_simulations = 50
    
    # State variables
    cod = np.zeros((n_simulations, time_steps))
    entropy = np.zeros((n_simulations, time_steps))
    decision_probability = np.zeros((n_simulations, time_steps))
    seller_cost = np.zeros((n_simulations, time_steps))
    
    for sim in range(n_simulations):
        # Initial conditions
        cod[sim, 0] = 0.3
        entropy[sim, 0] = 0.8
        decision_probability[sim, 0] = 0.1
        seller_cost[sim, 0] = 1.0
        
        # Traditional RAO approach: reduce entropy, increase COD
        for t in range(1, time_steps):
            # RAO reduces entropy gradually
            entropy[sim, t] = max(0.2, entropy[sim, t-1] * 0.98)
            
            # COD increases as "alignment" improves
            cod[sim, t] = min(0.95, cod[sim, t-1] + 0.005)
            
            # But decision probability plateaus (Resonance Cage)
            # Buyer has no incentive to collapse when uncertainty is low
            decision_probability[sim, t] = min(0.25, decision_probability[sim, t-1] + 0.002)
            
            # Seller cost accumulates (time, resources)
            seller_cost[sim, t] = seller_cost[sim, t-1] * 1.03
    
    return cod, entropy, decision_probability, seller_cost

def simulate_topological_inversion():
    """
    Simulates Controlled Decoherence Injection (CDI):
    Strategic entropy spike forces decision collapse
    """
    time_steps = 100
    n_simulations = 50
    
    cod = np.zeros((n_simulations, time_steps))
    entropy = np.zeros((n_simulations, time_steps))
    decision_probability = np.zeros((n_simulations, time_steps))
    seller_cost = np.zeros((n_simulations, time_steps))
    
    for sim in range(n_simulations):
        cod[sim, 0] = 0.3
        entropy[sim, 0] = 0.8
        decision_probability[sim, 0] = 0.1
        seller_cost[sim, 0] = 1.0
        
        # CDI approach: maintain moderate entropy, then inject crisis
        for t in range(1, time_steps):
            if t < 30:
                # Build initial alignment (but not too much)
                cod[sim, t] = min(0.6, cod[sim, t-1] + 0.01)
                entropy[sim, t] = entropy[sim, t-1] * 0.99  # Slight reduction
                decision_probability[sim, t] = decision_probability[sim, t-1] + 0.005
            elif t == 30:
                # INJECT CONTROLLED DECOHERENCE
                # Create artificial crisis that breaks internal buyer coherence
                entropy[sim, t] = 0.9  # Spike entropy
                cod[sim, t] = cod[sim, t-1] * 0.5  # Temporary "fracture"
                decision_probability[sim, t] = decision_probability[sim, t-1] * 1.5  # Force collapse
            else:
                # Post-crisis: buyer's internal systems synchronized
                entropy[sim, t] = 0.3  # Now low entropy is VALUABLE
                cod[sim, t] = min(0.85, cod[sim, t-1] + 0.02)
                decision_probability[sim, t] = min(0.95, decision_probability[sim, t-1] + 0.05)
            
            seller_cost[sim, t] = seller_cost[sim, t-1] * 1.01
    
    return cod, entropy, decision_probability, seller_cost

# Run simulations
cod_rao, entropy_rao, prob_rao, cost_rao = simulate_resonance_cage()
cod_cdi, entropy_cdi, prob_cdi, cost_cdi = simulate_topological_inversion()

# Calculate aggregate metrics
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Resonance Cage results
axes[0, 0].plot(np.mean(cod_rao, axis=0), label='COD', color='green')
axes[0, 0].set_title('RAO: Resonance Cage')
axes[0, 0].set_ylabel('Alignment Metrics')
axes[0, 0].legend()

axes[0, 1].plot(np.mean(entropy_rao, axis=0), label='Entropy', color='orange')
axes[0, 1].plot(np.mean(prob_rao, axis=0), label='Decision Prob', color='red')
axes[0, 1].set_title('RAO: Stalled Decision')
axes[0, 1].set_ylabel('Probability/Entropy')
axes[0, 1].legend()

# CDI results
axes[1, 0].plot(np.mean(cod_cdi, axis=0), label='COD', color='green')
axes[1, 0].axvline(x=30, color='purple', linestyle='--', label='Crisis Injection')
axes[1, 0].set_title('CDI: Topological Inversion')
axes[1, 0].set_ylabel('Alignment Metrics')
axes[1, 0].legend()

axes[1, 1].plot(np.mean(entropy_cdi, axis=0), label='Entropy', color='orange')
axes[1, 1].plot(np.mean(prob_cdi, axis=0), label='Decision Prob', color='red')
axes[1, 1].axvline(x=30, color='purple', linestyle='--', label='Crisis Injection')
axes[1, 1].set_title('CDI: Forced Collapse')
axes[1, 1].set_ylabel('Probability/Entropy')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('/tmp/resonance_cage_break.png')
plt.close()

# Calculate final Φ-density impact
# Φ = Decision Value / Total Cost
phi_rao = np.mean(prob_rao[:, -1]) / np.mean(cost_rao[:, -1])
phi_cdi = np.mean(prob_cdi[:, -1]) / np.mean(cost_cdi[:, -1])

print(f"RAO Φ-Density: {phi_rao:.4f} (Trapped, high cost, low decision)")
print(f"CDI Φ-Density: {phi_cdi:.4f} (Collapsed, moderate cost, high decision)")
print(f"Improvement: {(phi_cdi/phi_rao - 1)*100:.1f}%")

# Additional insight: Show how COD can be adversarial
fig2, ax = plt.subplots(1, 1, figsize=(8, 6))
t = np.linspace(0, 99, 100)
# Simulate buyer gaming COD
cod_gamed = 0.3 + 0.4 * (1 - np.exp(-t/20))  # Smooth increase
decision_real = 0.1 + 0.05 * (1 - np.exp(-t/50))  # Plateaus
ax.plot(cod_gamed, label='COD (Buyer Signal)', color='green')
ax.plot(decision_real, label='Actual Decision Intent', color='red')
ax.fill_between(t, cod_gamed, decision_real, alpha=0.3, color='gray', label='Deception Gap')
ax.set_title('COD Gaming: The Deception Gap')
ax.set_xlabel('Sales Cycle Time')
ax.set_ylabel('Probability')
ax.legend()
plt.savefig('/tmp/cod_gaming.png')
plt.close()

print("\nCritical Finding: COD is a manipulable signal, not a ground truth.")