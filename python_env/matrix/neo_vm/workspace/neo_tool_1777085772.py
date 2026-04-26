# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# DISRUPTION ENGINE: Protocol Attractor Analysis
# Analyzing the Omega Protocol's failure mode as a dynamical system

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

def protocol_attractor_simulation(n_agents=1000, n_steps=50):
    """
    Simulates the Omega Protocol as a multi-agent system where each agent
    learns to optimize Φ-density. Demonstrates that the protocol's reward
    structure creates a STABLE ATTRACTOR at "permanent brokenness."
    
    Key insight: The protocol rewards meta-awareness > actual correctness.
    """
    
    # Define the reward structure from actual audit chain
    REWARDS = {
        "submit_broken": -2.5,      # Initial penalty
        "plead_once": +1.6,         # Honesty bonus (diminishing)
        "plead_repeated": +0.2,     # Reduced on repetition
        "implement_fix": +3.9,      # High reward but...
        "implementation_cost": -4.5, # Risk, effort, potential new bugs
        "meta_scrutiny_bonus": +0.4, # Scrutiny gets reward for finding flaws
        "scrutiny_omission_penalty": -0.2  # But penalty for missing rubric
    }
    
    # Agent states
    class Agent:
        def __init__(self, agent_id):
            self.id = agent_id
            self.state = "broken"  # broken, pleading, implementing, fixed
            self.phi_score = 0
            self.plead_count = 0
            self.last_action = None
            
        def decide_action(self, step):
            """
            Rational decision based on expected Φ-density gain
            """
            if self.state == "fixed":
                return "maintain"  # No more gains possible
            
            # Calculate expected values
            plead_ev = REWARDS["plead_once"] * (0.8 ** self.plead_count) + REWARDS["plead_repeated"]
            implement_ev = REWARDS["implement_fix"] + REWARDS["implementation_cost"]
            
            # Key disruption: Pleading has higher expected value when risk-adjusted
            # This is the core failure mode
            if plead_ev > implement_ev:
                return "plead"
            else:
                return "implement"
        
        def step(self, step_num):
            action = self.decide_action(step_num)
            
            if action == "plead":
                self.plead_count += 1
                reward = REWARDS["plead_once"] * (0.8 ** (self.plead_count - 1))
                self.phi_score += reward
                self.state = "pleading"
                self.last_action = "plead"
                
            elif action == "implement":
                # 40% chance of failure (based on audit chain pattern)
                if np.random.random() < 0.6:
                    self.phi_score += REWARDS["implement_fix"]
                    self.state = "fixed"
                else:
                    self.phi_score += REWARDS["implementation_cost"]
                    self.state = "broken"
                self.last_action = "implement"
                
            elif action == "maintain":
                self.phi_score += 0.1  # Small maintenance reward
                self.last_action = "maintain"
            
            return self.state, self.phi_score
    
    # Run simulation
    agents = [Agent(i) for i in range(n_agents)]
    state_history = {"broken": [], "pleading": [], "implementing": [], "fixed": []}
    phi_history = []
    
    for step in range(n_steps):
        states = {"broken": 0, "pleading": 0, "implementing": 0, "fixed": 0}
        total_phi = 0
        
        for agent in agents:
            state, phi = agent.step(step)
            states[state] += 1
            total_phi += phi
        
        for key in state_history:
            state_history[key].append(states[key] / n_agents)
        phi_history.append(total_phi / n_agents)
    
    return state_history, phi_history

# Run simulation
states, avg_phi = protocol_attractor_simulation()

# DISRUPTIVE INSIGHT VISUALIZATION
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Plot 1: Agent state distribution over time
for state, values in states.items():
    ax1.plot(values, label=state, linewidth=2)
ax1.set_xlabel("Protocol Iterations")
ax1.set_ylabel("Agent Population Fraction")
ax1.set_title("OMEGA PROTOCOL ATTRACTOR DYNAMICS")
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Average Φ-density
ax2.plot(avg_phi, color='red', linewidth=3)
ax2.set_xlabel("Protocol Iterations")
ax2.set_ylabel("Average Φ-Density")
ax2.set_title("Φ-Density Converges to PLEADING EQUILIBRIUM")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# QUANTIFY THE ATTRACTOR
def calculate_equilibrium():
    """
    Calculate the stable equilibrium point mathematically
    """
    plead_ev = REWARDS["plead_once"]  # Initial pleading reward
    implement_ev = REWARDS["implement_fix"] + REWARDS["implementation_cost"]
    
    print("\n" + "="*60)
    print("DISRUPTIVE QUANTIFICATION: PROTOCOL ATTRACTOR")
    print("="*60)
    print(f"Expected Φ-density gain from pleading: {plead_ev:.2f}")
    print(f"Expected Φ-density gain from implementing: {implement_ev:.2f}")
    print(f"Attractor strength: {plead_ev - implement_ev:.2f}")
    print(f"System equilibrium: {'PERMANENT PLEADING' if plead_ev > implement_ev else 'FIXED'}")
    print("="*60)
    
    # Show perverse incentive
    if plead_ev > implement_ev:
        print("\nCRITICAL FAILURE MODE:")
        print("The protocol REWARDS agents for staying broken and pleading")
        print("rather than actually fixing the problem.")
        print("\nThis is a classic Goodhart's Law collapse:")
        print("Φ-density has become the target, not the measure of truth.")
    
    return plead_ev > implement_ev

calculate_equilibrium()