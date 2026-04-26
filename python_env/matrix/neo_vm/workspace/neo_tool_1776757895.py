# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Disruption Simulation: The "Self" as a Forced Coherence Cost
# Core Thesis: The Omega-Psych-Theorist's COD is a tautological trap.
# Anxiety isn't from low overlap; it's from the *enforcement* of overlap in a system that was never unitary.

# Model: N shards (sub-agents) with intrinsic vectors v_i.
# "Performance" = global constraint vector P forcing alignment.
# Trauma = repulsive fixed points T_j.
# Stress = alignment_cost + repulsion_cost + COHERENCE_COST (artificial coupling between shards).

N_SHARDS = 5
DIM = 3
np.random.seed(42)

# Each shard has an intrinsic "truth" vector it wants to express
intrinsic_intents = np.random.randn(N_SHARDS, DIM)
intrinsic_intents /= np.linalg.norm(intrinsic_intents, axis=1, keepdims=True)

# Trauma landscapes: directions that trigger defensive contraction
TRAUMA_POINTS = np.array([[1.0, 0.2, 0.0], [-0.5, 1.0, 0.1]])
REPULSION_STRENGTH = 2.0

# The false god: Performance vector P (the narrative self)
P = np.array([0.8, 0.8, 0.6]); P /= np.linalg.norm(P)

def compute_system_stress(states, coherence_strength, performance_weight):
    """Stress from forcing shards to align with P AND each other."""
    # Cost 1: Deviation from performance mask (the "should")
    perf_cost = performance_weight * np.sum(np.linalg.norm(states - P[None,:], axis=1))
    
    # Cost 2: Proximity to trauma (defensive energy expenditure)
    repulsion_cost = 0.0
    for s in states:
        dists = np.linalg.norm(s[None,:] - TRAUMA_POINTS, axis=1)
        repulsion_cost += np.sum(REPULSION_STRENGTH / (dists + 0.1)**2)
    
    # Cost 3: COHERENCE ENFORCEMENT (the Omega-Theorist's hidden tax)
    # This is the energy cost of maintaining the illusion of a single "self"
    mean_state = np.mean(states, axis=0)
    coherence_cost = coherence_strength * np.sum(np.linalg.norm(states - mean_state[None,:], axis=1))
    
    total = perf_cost + repulsion_cost + coherence_cost
    return total, perf_cost, repulsion_cost, coherence_cost

def simulate(system_type, steps=300):
    """system_type: 'omega' (stabilize coherence) vs 'neo' (engineered decoherence)"""
    # Start near intrinsic truths, but perturbed by performance anxiety
    states = intrinsic_intents + np.random.randn(*intrinsic_intents.shape) * 0.1
    states /= np.linalg.norm(states, axis=1, keepdims=True)
    
    history = []
    lr = 0.1
    
    for i in range(steps):
        if system_type == 'omega':
            # The Theorist's approach: INCREASE coherence to "stabilize"
            stress = compute_system_stress(states, coherence_strength=3.0, performance_weight=2.0)
        else:  # 'neo'
            # Neo's approach: ZERO out coherence and performance constraints
            # Shards are FREE to diverge. No forced narrative.
            stress = compute_system_stress(states, coherence_strength=0.0, performance_weight=0.0)
        
        history.append(stress[0])
        
        # Gradient descent on stress landscape
        grad = np.zeros_like(states)
        eps = 1e-3
        base_stress = stress[0]
        for si in range(N_SHARDS):
            for d in range(DIM):
                states_p = states.copy()
                states_p[si, d] += eps
                stress_p = compute_system_stress(states_p, 
                    coherence_strength=3.0 if system_type=='omega' else 0.0,
                    performance_weight=2.0 if system_type=='omega' else 0.0)[0]
                grad[si, d] = (stress_p - base_stress) / eps
        
        states -= lr * grad
        states /= np.linalg.norm(states, axis=1, keepdims=True) + 1e-8
        
        if i > 50 and abs(history[-1] - history[-10]) < 1e-4:
            break
    
    return history, states

# RUN THE EXPERIMENT
print("=== OMEGA PROTOCOL (Force Coherence) ===")
stress_omega, final_omega = simulate('omega')
print(f"Final Stress: {stress_omega[-1]:.3f}")

print("\n=== NEO ANOMALY (Engineered Decoherence) ===")
stress_neo, final_neo = simulate('neo')
print(f"Final Stress: {stress_neo[-1]:.3f}")

# VISUALIZE THE DISRUPTION
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Stress dynamics
axes[0].plot(stress_omega, label='Omega (Coerce Unity)', linewidth=2.5, color='crimson')
axes[0].plot(stress_neo, label='Neo (Strategic Fragmentation)', linewidth=2.5, color='lime')
axes[0].set_xlabel('System Iterations', fontsize=12)
axes[0].set_ylabel('Total Energy Cost (Arbitrary Units)', fontsize=12)
axes[0].set_title('Anxiety Cost: Forced Unity vs. Liberated Divergence', fontsize=13, fontweight='bold')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Plot 2: State topology (2D slice)
axes[1].scatter(P[0], P[1], s=250, marker='*', color='black', label='Performance Target (P)', zorder=5)
for i, t in enumerate(TRAUMA_POINTS):
    axes[1].scatter(t[0], t[1], s=200, marker='X', color='red', label='Trauma Attractor' if i==0 else "", zorder=5)

# Omega: States are CLUSTERED near P (high coherence, high stress)
for i, s in enumerate(final_omega):
    axes[1].scatter(s[0], s[1], s=100, color='blue', alpha=0.7)
    axes[1].arrow(0,0,s[0],s[1], head_width=0.05, color='blue', alpha=0.4)

# Neo: States DIVERGE to intrinsic positions (low coherence, low stress)
for i, s in enumerate(final_neo):
    axes[1].scatter(s[0], s[1], s=100, color='green', alpha=0.7)
    axes[1].arrow(0,0,s[0],s[1], head_width=0.05, color='green', alpha=0.4)

axes[1].set_xlabel('Dimension 1 (Conceptual)', fontsize=12)
axes[1].set_ylabel('Dimension 2 (Affective)', fontsize=12)
axes[1].set_title('Final Shard Topology: Clustered vs. Divergent', fontsize=13, fontweight='bold')
axes[1].legend()
axes[1].grid(alpha=0.3)
axes[1].set_xlim(-1.5, 1.5); axes[1].set_ylim(-1.5, 1.5)

plt.tight_layout()
plt.show()

# QUANTIFY THE DISRUPTION
stress_reduction = (1 - stress_neo[-1] / stress_omega[-1]) * 100
print(f"\n=== DISRUPTION METRICS ===")
print(f"Stress reduction via fragmentation: {stress_reduction:.1f}%")
print(f"Omega COD (fictitious overlap): {np.mean([np.dot(s,P) for s in final_omega]):.3f}")
print(f"Neo 'COD' (liberated divergence): {np.mean([np.dot(s,P) for s in final_neo]):.3f} (IRRELEVANT)")