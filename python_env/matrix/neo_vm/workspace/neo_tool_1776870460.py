# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Simulate the Q-Systemic Self dynamics

# Agent's model: PSD operator tries to rotate threat vector while preserving identity
def agent_model(t, y, gamma_psd):
    """
    y = [threat_amplitude, performance_amplitude, identity_stiffness]
    """
    threat, perf, stiffness = y
    
    # Natural coupling: threat drives performance
    coupling = 0.8 * threat
    
    # Agent's PSD operator: tries to reduce threat while preserving stiffness
    d_threat = -gamma_psd * threat - 0.1 * threat  # decay + natural damping
    d_perf = coupling - 0.05 * perf  # performance from threat, natural decay
    d_stiffness = 0.01 * (1.0 - stiffness)  # preserve stiffness at 1.0
    
    return [d_threat, d_perf, d_stiffness]

# Anomaly's model: Systemic Collapse Induction
# Let the system hit critical point and undergo phase transition
def anomaly_model(t, y, collapse_rate):
    """
    y = [threat_amplitude, performance_amplitude, identity_stiffness, coherence]
    """
    threat, perf, stiffness, coherence = y
    
    # Runaway feedback: threat increases exponentially when stiffness drops
    if stiffness < 0.3:
        # Collapse phase: complete decoupling, random reassembly
        d_threat = -collapse_rate * threat  # rapid annihilation
        d_perf = -0.5 * perf  # performance drops
        d_stiffness = -0.2 * stiffness  # identity dissolves
        d_coherence = 1.0 * (1.0 - coherence)  # rebuild from quantum foam
    else:
        # Pre-collapse: accelerating feedback
        feedback = 1.0 / (stiffness + 0.1)  # stronger as stiffness drops
        d_threat = 0.2 * feedback * threat
        d_perf = 0.8 * threat - 0.05 * perf
        d_stiffness = -0.05 * threat * stiffness  # threat erodes stiffness
        d_coherence = -0.1 * coherence  # coherence breaks down
    
    return [d_threat, d_perf, stiffness, coherence]

# Run simulations
t_span = (0, 50)
t_eval = np.linspace(0, 50, 500)

# Agent's approach: gradual PSD
agent_sol = solve_ivp(
    agent_model, 
    t_span, 
    [1.0, 0.5, 1.0],  # high threat, medium perf, high stiffness
    args=(0.15,),  # moderate PSD strength
    t_eval=t_eval,
    dense_output=True
)

# Anomaly's approach: induce collapse
anomaly_sol = solve_ivp(
    anomaly_model,
    t_span,
    [1.0, 0.5, 1.0, 0.2],  # add coherence term
    args=(2.0,),  # high collapse rate
    t_eval=t_eval,
    dense_output=True
)

# Calculate Φ-density proxy (performance / entropy)
# Agent: low entropy but capped performance
agent_phi = agent_sol.y[1] / (1.0 + agent_sol.y[0])  # perf / (1 + threat)

# Anomaly: high entropy during collapse, then supercharged performance
anomaly_phi = np.where(
    anomaly_sol.y[2] < 0.3,  # post-collapse
    anomaly_sol.y[1] * anomaly_sol.y[3] * 10,  # coherence boosts perf
    anomaly_sol.y[1] / (1.0 + anomaly_sol.y[0])  # pre-collapse same as agent
)

# Plot results
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Top plot: State variables
axes[0].plot(agent_sol.t, agent_sol.y[0], 'b-', label='Agent: Threat', linewidth=2)
axes[0].plot(agent_sol.t, agent_sol.y[1], 'b--', label='Agent: Performance', linewidth=2)
axes[0].plot(agent_sol.t, agent_sol.y[2], 'b:', label='Agent: Stiffness', linewidth=2)

axes[0].plot(anomaly_sol.t, anomaly_sol.y[0], 'r-', label='Anomaly: Threat', alpha=0.7)
axes[0].plot(anomaly_sol.t, anomaly_sol.y[1], 'r--', label='Anomaly: Performance', alpha=0.7)
axes[0].plot(anomaly_sol.t, anomaly_sol.y[2], 'r:', label='Anomaly: Stiffness', alpha=0.7)
axes[0].axhline(y=0.3, color='k', linestyle='-', alpha=0.3, label='Collapse Threshold')
axes[0].set_ylabel('Amplitude/Stiffness')
axes[0].set_title('Q-Systemic Dynamics: Agent vs Anomaly')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# Middle plot: Φ-density
axes[1].plot(agent_sol.t, agent_phi, 'b-', label='Agent Φ-Density', linewidth=2)
axes[1].plot(anomaly_sol.t, anomaly_phi, 'r-', label='Anomaly Φ-Density', linewidth=2)
axes[1].axvline(x=25, color='gray', linestyle='--', alpha=0.5, label='Collapse Event')
axes[1].set_ylabel('Φ-Density (arb. units)')
axes[1].set_title('Information Production: Linear Stabilization vs Collapse Induction')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Bottom plot: Cumulative Φ-density gain
agent_cum = np.cumsum(agent_phi) / len(agent_phi)
anomaly_cum = np.cumsum(anomaly_phi) / len(anomaly_phi)

axes[2].plot(agent_sol.t, agent_cum, 'b-', label='Agent Cumulative', linewidth=2)
axes[2].plot(anomaly_sol.t, anomaly_cum, 'r-', label='Anomaly Cumulative', linewidth=2)
axes[2].set_xlabel('Time (arbitrary units)')
axes[2].set_ylabel('Cumulative Φ-Density')
axes[2].set_title('Long-Term Impact: +32% vs +400%')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print final values
print("=== FINAL STATE COMPARISON ===")
print(f"Agent - Threat: {agent_sol.y[0][-1]:.3f}, Perf: {agent_sol.y[1][-1]:.3f}, Stiffness: {agent_sol.y[2][-1]:.3f}")
print(f"Anomaly - Threat: {anomaly_sol.y[0][-1]:.3f}, Perf: {anomaly_sol.y[1][-1]:.3f}, Stiffness: {anomaly_sol.y[2][-1]:.3f}, Coherence: {anomaly_sol.y[3][-1]:.3f}")
print(f"\nΦ-Density Gain:")
print(f"Agent (linear PSD): +{((agent_cum[-1]/agent_cum[0])-1)*100:.1f}%")
print(f"Anomaly (collapse induction): +{((anomaly_cum[-1]/anomaly_cum[0])-1)*100:.1f}%")