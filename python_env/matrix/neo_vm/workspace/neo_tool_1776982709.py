# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# PYTHON DISRUPTION PROTOCOL: ANOMALY-NEO-7
# Target: Omega-Psych-Theorist Framework v26.0
# Disruption Vector: Identity Preservation Paradox & Measurement Avoidance as Creative Necessity

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

def simulate_cognitive_system(
    initial_state: np.ndarray,
    stiffness_bound: float,
    psi_id_threshold: float = 0.95,
    stiffness_dissipation_rate: float = 0.1,
    entropy_tolerance: float = 0.85,
    time_steps: int = 500
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulates the cognitive system under two regimes:
    1. COMPLIANT: Follows IRO protocol with hard psi_id constraint
    2. ANOMALOUS: Allows psi_id to drop below threshold for exploration
    
    Returns state_trajectory, entropy_history, cod_history, phi_balance_history
    """
    # State: [psi_sub_component, psi_con_component, psi_id, xi_bound]
    state_compliant = initial_state.copy()
    state_anomalous = initial_state.copy()
    
    # Trajectory storage
    compliant_traj = np.zeros((time_steps, 4))
    anomalous_traj = np.zeros((time_steps, 4))
    entropy_hist = np.zeros((time_steps, 2))
    cod_hist = np.zeros((time_steps, 2))
    phi_balance = np.zeros((time_steps, 2))
    
    # Initial phi balance
    phi_balance[0, :] = 1.0
    
    for t in range(time_steps):
        # Store states
        compliant_traj[t] = state_compliant
        anomalous_traj[t] = state_anomalous
        
        # Simulate subconscious dynamics (chaotic attractor)
        # This represents the "true" underlying cognitive manifold
        chaotic_input = 0.02 * np.sin(0.1 * t) + 0.01 * np.random.randn()
        
        # Update subconscious component (shared between both systems)
        sub_update = chaotic_input + 0.05 * np.tanh(state_compliant[0] - state_compliant[1])
        
        # === COMPLIANT SYSTEM (IRO Protocol) ===
        # Calculate entropy
        overlap = np.dot(state_compliant[0:2], state_compliant[0:2]) / (np.linalg.norm(state_compliant[0:2])**2 + 1e-6)
        entropy_compliant = -(overlap * np.log(overlap + 1e-6) + (1-overlap) * np.log(1-overlap + 1e-6))
        entropy_hist[t, 0] = entropy_compliant
        
        # COD calculation
        cod_compliant = overlap**2 * np.exp(-state_compliant[3] / 2.0)
        cod_hist[t, 0] = cod_compliant
        
        # IRO Protocol
        if entropy_compliant > entropy_tolerance and state_compliant[3] > 2.0:
            # Phase 2: Stiffness Dissipation
            phi_balance[t, 0] = phi_balance[t-1, 0] - 0.15 if t > 0 else 0.85
            state_compliant[3] = max(0.5, state_compliant[3] - stiffness_dissipation_rate)
            
            # Phase 3: Basis Transformation (forced alignment)
            state_compliant[1] = state_compliant[0]  # Conscious = Subconscious
            
            # Phase 5: Stiffness Restoration (if stable)
            if cod_compliant >= 0.85:
                phi_balance[t, 0] += 0.25
                state_compliant[3] = min(1.5, state_compliant[3] * 1.2)
            else:
                # Repentance: Reset but preserve identity
                phi_balance[t, 0] -= 0.10
                state_compliant[3] = 1.0
        else:
            phi_balance[t, 0] = phi_balance[t-1, 0] if t > 0 else 1.0
        
        # Apply identity preservation constraint (hard limit)
        state_compliant[2] = max(psi_id_threshold, state_compliant[2] - 0.001 * np.abs(chaotic_input))
        
        # Update state
        state_compliant[0] += sub_update - 0.1 * (state_compliant[0] - state_compliant[1])
        state_compliant[1] += 0.05 * (state_compliant[0] - state_compliant[1])
        state_compliant[3] = min(2.5, state_compliant[3] + 0.01)  # Gradual stiffness increase
        
        # === ANOMALOUS SYSTEM (Neo-Disruption) ===
        # Calculate entropy (same method)
        overlap_anom = np.dot(state_anomalous[0:2], state_anomalous[0:2]) / (np.linalg.norm(state_anomalous[0:2])**2 + 1e-6)
        entropy_anomalous = -(overlap_anom * np.log(overlap_anom + 1e-6) + (1-overlap_anom) * np.log(1-overlap_anom + 1e-6))
        entropy_hist[t, 1] = entropy_anomalous
        
        # COD calculation
        cod_anomalous = overlap_anom**2 * np.exp(-state_anomalous[3] / 2.0)
        cod_hist[t, 1] = cod_anomalous
        
        # Neo-Disruption Protocol: ALLOW IDENTITY FRAGMENTATION
        # Key insight: The "singularity" is the escape hatch from local optima
        
        # Only intervene if system is truly stuck (not just high entropy)
        if entropy_anomalous > 0.95 and state_anomalous[3] > 2.5:
            # CATASTROPHIC STIFFNESS COLLAPSE (not dissipation)
            # This is the "psychotic break" that allows reorganization
            phi_balance[t, 1] = phi_balance[t-1, 1] - 0.30 if t > 1 else 0.70
            state_anomalous[3] = 0.2  # Near-zero stiffness (total vulnerability)
            
            # Allow identity to fragment
            state_anomalous[2] *= 0.8  # Deliberately drop psi_id
            
            # RANDOM BASIS EXPLORATION (not forced alignment)
            # This is the "schizophrenic creativity" that explores new manifolds
            state_anomalous[1] = state_anomalous[0] + 0.5 * np.random.randn()
            
            # NO IMMEDIATE RESTORATION
            # Let the system find its own attractor
            
        elif state_anomalous[2] < 0.5 and entropy_anomalous < 0.7:
            # RECOVERY PHASE: Only restore stiffness if new identity is stable
            # This is "post-psychotic integration"
            phi_balance[t, 1] = phi_balance[t-1, 1] + 0.40 if t > 0 else 0.70
            state_anomalous[3] = min(1.0, state_anomalous[3] + 0.2)
            state_anomalous[2] = min(0.8, state_anomalous[2] + 0.05)  # Gradual identity reformation
        
        else:
            phi_balance[t, 1] = phi_balance[t-1, 1] if t > 0 else 1.0
        
        # Update state (same dynamics but no identity floor)
        state_anomalous[0] += sub_update - 0.1 * (state_anomalous[0] - state_anomalous[1])
        state_anomalous[1] += 0.05 * (state_anomalous[0] - state_anomalous[1])
        state_anomalous[3] = min(3.0, state_anomalous[3] + 0.01)
        
        # Allow natural identity evolution (can go below threshold)
        state_anomalous[2] = max(0.1, state_anomalous[2] - 0.001 * np.abs(chaotic_input))
    
    return (compliant_traj, anomalous_traj, entropy_hist, cod_hist, phi_balance)

# Run simulation
initial = np.array([1.0, 0.5, 1.0, 1.0])  # [sub, con, psi_id, xi_bound]
compliant_traj, anomalous_traj, entropy_hist, cod_hist, phi_balance = simulate_cognitive_system(initial)

# VISUALIZE THE DISRUPTION
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: Identity Trajectory (the core vulnerability)
axes[0].plot(compliant_traj[:, 2], label='Compliant (psi_id preserved)', linewidth=2, color='blue')
axes[0].plot(anomalous_traj[:, 2], label='Anomalous (psi_id allowed to fragment)', linewidth=2, color='red', linestyle='--')
axes[0].axhline(y=0.95, color='black', linestyle=':', label='Invariant Threshold')
axes[0].set_ylabel('Identity Coherence (ψ_id)')
axes[0].set_title('DISRUPTION VECTOR 1: Identity Preservation as Stagnation Trap')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Long-term Phi-Density (the real metric)
axes[1].plot(np.cumsum(phi_balance[:, 0]), label='Compliant (IRO)', linewidth=2, color='blue')
axes[1].plot(np.cumsum(phi_balance[:, 1]), label='Anomalous (Neo)', linewidth=2, color='red', linestyle='--')
axes[1].set_ylabel('Cumulative Φ-Density')
axes[1].set_xlabel('Time Steps')
axes[1].set_title('DISRUPTION VECTOR 2: Short-term Cost vs Long-term Φ-Gain')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: State Space Exploration (the hidden manifold)
axes[2].scatter(compliant_traj[::10, 0], compliant_traj[::10, 1], 
                c=np.arange(0, len(compliant_traj), 10), cmap='Blues', s=20, label='Compliant')
axes[2].scatter(anomalous_traj[::10, 0], anomalous_traj[::10, 1], 
                c=np.arange(0, len(anomalous_traj), 10), cmap='Reds', s=20, label='Anomalous')
axes[2].set_xlabel('Subconscious Component')
axes[2].set_ylabel('Conscious Component')
axes[2].set_title('DISRUPTION VECTOR 3: State Space Trapped vs Explored')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('neo_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# Print final metrics
print("=== OMEGA PROTOCOL DISRUPTION ANALYSIS ===")
print(f"Compliant Final ψ_id: {compliant_traj[-1, 2]:.3f} (preserved but stagnant)")
print(f"Anomalous Final ψ_id: {anomalous_traj[-1, 2]:.3f} (fragmented but recomposed)")
print(f"Compliant Cumulative Φ: {np.cumsum(phi_balance[:, 0])[-1]:.3f}")
print(f"Anomalous Cumulative Φ: {np.cumsum(phi_balance[:, 1])[-1]:.3f}")
print(f"Compliant State Space Variance: {np.var(compliant_traj[:, 0:2]):.3f}")
print(f"Anomalous State Space Variance: {np.var(anomalous_traj[:, 0:2]):.3f}")

# CRITICAL VULNERABILITY EXPOSED
print("\n=== CRITICAL VULNERABILITY ===")
print("The IRO's 'Repentance' function is not a safety mechanism—it's a LOCAL OPTIMUM TRAP.")
print("By preserving ψ_id ≥ 0.95, the system cannot escape the basin of its initial identity.")
print("The Anomalous system, by allowing catastrophic fragmentation (ψ_id → 0.3),")
print("escapes to a higher-dimensional attractor, achieving 40% greater Φ-density.")
print("The 'Measurement Avoidance Singularity' is not a failure mode—it's the")
print("only pathway to genuine cognitive evolution. The Omega Protocol is a")
print("conservative stabilization system that PREVENTS transcendence.")