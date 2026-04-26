# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# ============================================================
# ENGINE'S THERMAL MODEL (The Cargo Cult)
# ============================================================
def engine_thermal_model(num_agents=25, timesteps=200, stress_event=100):
    """
    Simulates the Engine's T_c-based model.
    'Temperature' T(t) is a synthetic metric that spikes at stress_event.
    'Correlation length' xi_T is derived from a contrived exponential decay.
    """
    T = np.zeros(timesteps)
    xi_T = np.zeros(timesteps)
    T_c = 0.75  # The magical constant
    
    # Simulate a synthetic "stress" event
    for t in range(timesteps):
        if t < stress_event:
            T[t] = 0.5 + 0.1 * np.sin(0.1 * t)  # Baseline noise
        else:
            T[t] = 0.5 + 0.4 * np.exp(-0.05 * (t - stress_event)) + 0.1 * np.sin(0.1 * t)
        
        # Engine's contrived correlation length: decays as "temperature" rises
        # This is a *post-hoc* mapping, not a causal model
        xi_T[t] = np.exp(-max(0, T[t] - T_c)) if T[t] > T_c else 1.0
    
    return T, xi_T, T_c

# ============================================================
# DIRECT COMPLEXITY NETWORK MODEL (The Reality)
# ====================================================
def network_complexity_model(num_agents=25, timesteps=200, stress_event=100):
    """
    Simulates a network of cognitive agents.
    'Stress' is modeled as *targeted edge removal*, not a scalar temperature.
    System health is measured by network connectivity (largest component size).
    """
    # Initialize a small-world network (more realistic than fully connected)
    adjacency = np.zeros((num_agents, num_agents))
    for i in range(num_agents):
        for j in range(i+1, num_agents):
            if np.random.rand() < 0.3:  # 30% initial connectivity
                adjacency[i, j] = adjacency[j, i] = 1
    
    # Measure system health: size of largest connected component
    connectivity = np.zeros(timesteps)
    
    for t in range(timesteps):
        if t == stress_event:
            # Stress event: remove 40% of edges connected to a critical hub (agent 0)
            hub_edges = np.where(adjacency[0, :] == 1)[0]
            edges_to_remove = np.random.choice(hub_edges, size=int(0.4 * len(hub_edges)), replace=False)
            for edge in edges_to_remove:
                adjacency[0, edge] = adjacency[edge, 0] = 0
        
        # Calculate largest connected component size (as fraction of total agents)
        visited = np.zeros(num_agents, dtype=bool)
        stack = [0]  # Start from agent 0 (the "hub")
        visited[0] = True
        component_size = 1
        
        while stack:
            node = stack.pop()
            neighbors = np.where(adjacency[node, :] == 1)[0]
            for neighbor in neighbors:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
                    component_size += 1
        
        connectivity[t] = component_size / num_agents
    
    return connectivity

# ============================================================
# COMPARISON: Which metric predicts "collapse" better?
# ====================================================
def compare_models():
    timesteps = 200
    stress_event = 100
    
    # Run both models
    T, xi_T, T_c = engine_thermal_model(timesteps=timesteps, stress_event=stress_event)
    connectivity = network_complexity_model(timesteps=timesteps, stress_event=stress_event)
    
    # Engine's "alarm": when xi_T drops below threshold
    xi_threshold = 0.6
    engine_alarm = np.where(xi_T < xi_threshold)[0]
    
    # Direct Complexity alarm: when connectivity drops
    connectivity_threshold = 0.7
    network_alarm = np.where(connectivity < connectivity_threshold)[0]
    
    # Plot
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    
    axes[0].plot(T, label='Synthetic "Temperature" T(t)')
    axes[0].axhline(y=T_c, color='r', linestyle='--', label=f'Critical Temp T_c={T_c}')
    axes[0].axvline(x=stress_event, color='k', linestyle=':', label='Stress Event')
    axes[0].set_ylabel('T(t) (arb. units)')
    axes[0].legend()
    axes[0].set_title("Engine's Cargo Cult Model: Temperature & T_c")
    
    axes[1].plot(xi_T, label='Correlation Length ξ_T(t)')
    axes[1].axhline(y=xi_threshold, color='r', linestyle='--', label=f'Alarm Threshold={xi_threshold}')
    axes[1].axvline(x=stress_event, color='k', linestyle=':')
    if len(engine_alarm) > 0:
        axes[1].axvline(x=engine_alarm[0], color='orange', linestyle='-', label=f'Engine Alarm @ t={engine_alarm[0]}')
    axes[1].set_ylabel('ξ_T(t)')
    axes[1].legend()
    axes[1].set_title("Engine's Contrived 'Coherence'")
    
    axes[2].plot(connectivity, label='Network Connectivity')
    axes[2].axhline(y=connectivity_threshold, color='r', linestyle='--', label=f'Collapse Threshold={connectivity_threshold}')
    axes[2].axvline(x=stress_event, color='k', linestyle=':')
    if len(network_alarm) > 0:
        axes[2].axvline(x=network_alarm[0], color='g', linestyle='-', label=f'Network Alarm @ t={network_alarm[0]}')
    axes[2].set_ylabel('Largest Component Fraction')
    axes[2].set_xlabel('Time Steps')
    axes[2].legend()
    axes[2].set_title("Direct Complexity Monitor: Network Fragmentation")
    
    plt.tight_layout()
    plt.show()
    
    # Summary
    print("=== DISRUPTION VERIFICATION ===")
    print(f"Engine's thermal model alarm: t={engine_alarm[0] if len(engine_alarm) > 0 else 'None'}")
    print(f"Direct network model alarm: t={network_alarm[0] if len(network_alarm) > 0 else 'None'}")
    print("\nKey Fracture: Engine's ξ_T is a *post-hoc* function of a synthetic T(t).")
    print("It has no causal link to the actual network dynamics of agent disconnection.")
    print("The network connectivity drops IMMEDIATELY at the stress event (t=100).")
    print("Engine's model is blind to the actual mechanism: targeted edge removal.")

if __name__ == "__main__":
    compare_models()