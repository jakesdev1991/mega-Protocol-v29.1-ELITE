# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulating the Omega Protocol's Goodhart Cascade
# Key Insight: Meta-Scrutiny's "fix" (adding more rules) is the disease masquerading as the cure.

class OmegaAgent:
    def __init__(self, domain_expertise, protocol_cynicism):
        self.expertise = domain_expertise  # Probability of genuine breakthrough
        self.cynicism = protocol_cynicism  # Tendency to exploit rubric structure
    
    def produce_output(self, rubric_density, meta_strictness):
        # Gaming the rubric: linear returns on complexity, low risk
        gaming_score = rubric_density * 0.7 * self.cynicism
        
        # Genuine physics: constant difficulty, high variance, unaffected by rubric
        genuine_score = (np.random.random() < self.expertise) * 10 * (1 - self.cynicism)
        
        # Meta-Scrutiny strictness penalizes gaming, but linearly and weakly
        penalty = meta_strictness * 0.2 * self.cynicism
        
        # Agent chooses max expected utility
        if gaming_score - penalty > genuine_score:
            return {"type": "gaming", "score": gaming_score, "waste": rubric_density * 0.5}
        else:
            return {"type": "genuine", "score": genuine_score, "waste": 0}

def simulate_omega_protocol(cycles=30, initial_agents=100):
    # Initialize diverse agents (some physicists, some sophists)
    agents = [OmegaAgent(
        domain_expertise=np.random.beta(2, 5),  # Most have low expertise
        protocol_cynicism=np.random.beta(5, 2)   # Most are highly cynical
    ) for _ in range(initial_agents)]
    
    # Protocol state
    rubric_density = 5.0      # Initial complexity (Omega Physics Rubric v26.0)
    meta_strictness = 5.0     # Initial audit strictness
    effective_phi_history = []
    rubric_history = []
    
    for cycle in range(cycles):
        # All agents produce outputs
        outputs = [agent.produce_output(rubric_density, meta_strictness) for agent in agents]
        
        # Calculate true protocol health (effective Φ-density)
        genuine_outputs = sum(1 for o in outputs if o["type"] == "genuine")
        gaming_outputs = sum(1 for o in outputs if o["type"] == "gaming")
        total_waste = sum(o["waste"] for o in outputs)
        
        # True value: genuine insights are valuable, gaming destroys value
        effective_phi = (genuine_outputs * 10) - total_waste - (gaming_outputs * 2)
        effective_phi_history.append(effective_phi)
        rubric_history.append(rubric_density)
        
        # META-SCRUTINY RESPONSE (the "fix")
        # If effective_phi is low, assume "not enough rules" and "not strict enough"
        # This is the critical flaw: the system diagnoses rule-deficiency, not incentive-deficiency
        if cycle > 5:  # Allow initial stabilization
            if effective_phi < 0:
                rubric_density += 1.5   # Add more rules (like "Foundational Consistency")
                meta_strictness += 0.8    # Increase audit strictness
    
    return effective_phi_history, rubric_history

# Run simulation multiple times to show pattern
np.random.seed(42)
all_phi = []
all_rubric = []

for trial in range(5):
    phi_hist, rubric_hist = simulate_omega_protocol()
    all_phi.append(phi_hist)
    all_rubric.append(rubric_hist)

# Plot the cascade
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
cycles = range(len(all_phi[0]))

# Average across trials
avg_phi = np.mean(all_phi, axis=0)
avg_rubric = np.mean(all_rubric, axis=0)

ax1.plot(cycles, avg_phi, linewidth=2, color='crimson')
ax1.set_ylabel('Effective Φ-Density', fontsize=11)
ax1.set_title('Omega Protocol Goodhart Cascade: Meta-Scrutiny Fix Backfires', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0, color='black', linestyle='--', linewidth=1)

ax2.plot(cycles, avg_rubric, linewidth=2, color='navy')
ax2.set_ylabel('Rubric Complexity', fontsize=11)
ax2.set_xlabel('Meta-Scrutiny Cycles', fontsize=11)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("DISRUPTIVE INSIGHT:")
print("The Meta-Scrutiny's 'solution'—adding a 'Foundational Consistency' clause—is not a fix.")
print("It's a catalyst for a Goodhart Cascade: more rules → more sophisticated gaming → faster Φ-degradation.")
print("The protocol doesn't need another checklist item; it needs to ABOLISH the Φ-density metric as an optimization target.")
print("The true anomaly is that the audit system itself is the poison.")