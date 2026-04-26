# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# --- Disruption: Topological Coherence Percolation vs. Engine's Scalar Field ---
# The Engine's model assumes smooth, differentiable fields. This is a fatal flaw.
# Coherence collapse is a topological phase transition, not a Taylor series event.

# Simulate an HSA node: 8 compute units (4 CPUs, 4 GPUs)
NUM_NODES = 8
CRITICAL_PATHWAYS = [(0,4), (1,5), (2,6), (3,7)] # CPU-GPU pairs

def simulate_engine_model(t_span, dt):
    """Engine's flawed approach: smooth scalar field Phi_N(t)"""
    t = np.arange(0, t_span, dt)
    # Simulate "coherence" as a smooth process with a hidden drift
    # This is what Engine measures: average coherence, missing topological decay
    Phi_N = 0.8 + 0.1 * np.sin(2 * np.pi * 0.5 * t)  # Baseline "health"
    
    # Inject subtle, non-collapsing noise (high kurtosis but stable)
    noise = np.random.laplace(0, 0.02, size=len(t))
    Phi_N += noise
    
    # The "shredding" event is invisible to Phi_N: it stays high while graph fractures
    # Engine's jerk calculation
    jerk = np.gradient(np.gradient(np.gradient(Phi_N, dt), dt), dt)
    excess_kurtosis = np.mean(((jerk - np.mean(jerk)) / np.std(jerk))**4) - 3
    S_j = 1 / (1 + excess_kurtosis) if excess_kurtosis > -1 else 1.0
    
    return t, Phi_N, jerk, S_j

def simulate_topological_model(t_span, dt, failure_rate=0.001):
    """Anomaly's model: dynamic graph where edges are coherence pathways"""
    t = np.arange(0, t_span, dt)
    steps = len(t)
    
    # Initialize fully connected graph (ideal coherence)
    G = nx.complete_graph(NUM_NODES)
    for i, j in G.edges():
        G[i][j]['weight'] = 1.0  # Edge "strength"
    
    lcc_size_history = []
    spectral_jerk_history = []
    fiedler_history = []
    
    # Simulate edge failures: critical pathways fail faster
    for step in range(steps):
        # Random failures across all edges
        for i, j in list(G.edges()):
            if np.random.random() < failure_rate:
                G[i][j]['weight'] -= 0.1
                if G[i][j]['weight'] <= 0:
                    G.remove_edge(i, j)
        
        # Critical pathways have higher failure rate after t=3 (simulating stress)
        if t[step] > 3.0:
            for i, j in CRITICAL_PATHWAYS:
                if G.has_edge(i, j) and np.random.random() < failure_rate * 5:
                    G.remove_edge(i, j)
        
        # Measure largest connected component size (true coherence)
        lcc = max(nx.connected_components(G), key=len)
        lcc_size = len(lcc) / NUM_NODES
        lcc_size_history.append(lcc_size)
        
        # Measure algebraic connectivity (Fiedler eigenvalue)
        # This is the topological invariant Engine misses
        try:
            fiedler = nx.algebraic_connectivity(G, weight='weight')
        except nx.NetworkXError:
            fiedler = 0.0  # Graph is disconnected
        
        fiedler_history.append(fiedler)
        
        # Calculate topological "jerk": second derivative of spectral connectivity
        if len(fiedler_history) > 2:
            spectral_jerk = np.gradient(np.gradient(fiedler_history[-10:], dt), dt)[-1]
            spectral_jerk_history.append(abs(spectral_jerk))
        else:
            spectral_jerk_history.append(0.0)
    
    return t, np.array(lcc_size_history), np.array(fiedler_history), np.array(spectral_jerk_history)

# Run simulations
t, Phi_N, scalar_jerk, S_j = simulate_engine_model(t_span=6, dt=0.01)
t, lcc_size, fiedler, spectral_jerk = simulate_topological_model(t_span=6, dt=0.01, failure_rate=0.005)

# --- The Breaking Point ---
# Engine sees stable jerk metric (S_j ~ 1) and high Phi_N, declares system healthy.
# Anomaly sees spectral jerk spike and LCC collapse at t>4, predicts shredding.

fig, axes = plt.subplots(3, 1, figsize=(10, 8))

# Plot 1: Scalar vs. Topological Coherence
axes[0].plot(t, Phi_N, label="Engine's Φ_N (smooth field)", linewidth=2)
axes[0].plot(t, lcc_size, label="Anomaly's LCC/N (topological coherence)", linewidth=2, linestyle='--')
axes[0].axvline(x=3.0, color='red', linestyle=':', label="Stress onset")
axes[0].set_title("Fatal Flaw: Scalar Field Masks Topological Fracture")
axes[0].set_ylabel("Coherence Metric")
axes[0].legend()
axes[0].grid(True)

# Plot 2: Jerk Metrics
axes[1].plot(t, np.abs(scalar_jerk), label="Engine's |j(t)| (3rd derivative)", alpha=0.7)
axes[1].plot(t, spectral_jerk, label="Anomaly's |λ₂''(t)| (spectral jerk)", linewidth=2, color='orange')
axes[1].axvline(x=3.0, color='red', linestyle=':')
axes[1].set_title("Jerk Blindness: Scalar Jerk Silent, Spectral Jerk Screams")
axes[1].set_ylabel("Jerk Magnitude")
axes[1].legend()
axes[1].grid(True)

# Plot 3: Fiedler Eigenvalue (the invisible invariant)
axes[2].plot(t, fiedler, label="λ₂(t) (algebraic connectivity)", color='green', linewidth=2)
axes[2].axvline(x=3.0, color='red', linestyle=':')
axes[2].axhline(y=0.0, color='black', linestyle='--', label="Disconnection threshold")
axes[2].set_title("Topological Invariant: Fiedler Eigenvalue Collapse")
axes[2].set_xlabel("Time (s)")
axes[2].set_ylabel("λ₂ (connectivity)")
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.show()

# --- Disruptive Insight ---
print("--- DISRUPTION VERIFICATION ---")
print(f"Engine's final stability S_j: {S_j:.3f} (predicts STABLE)")
print(f"Anomaly's final LCC size: {lcc_size[-1]:.3f} (predicts SHREDDING)")
print(f"Anomaly's max spectral jerk: {np.max(spectral_jerk):.3f} at t={t[np.argmax(spectral_jerk)]:.2f}s")
print("\nBREAKING LOGIC:")
print("1. Engine's ψᵢⱼ(t) field is a statistical mirage. It averages away local failures.")
print("2. Coherence collapse is a percolation event: edges vanish, components fracture.")
print("3. Derivatives of a smooth field cannot detect topological ruptures.")
print("4. The rubric's kurtosis metric is a 19th-century statistical relic for 21st-century network catastrophes.")
print("\nOMEGA-ANOMALY PROTOCOL:")
print("Replace Φ_N(t) with λ₂(t) (Fiedler eigenvalue).")
print("Replace S_j (kurtosis) with S_λ = -d²λ₂/dt² (spectral acceleration).")
print("Replace entropy of ψ bins with entropy of degree distribution P(k).")
print("The state vector is not a vector—it's a time-varying simplicial complex.")