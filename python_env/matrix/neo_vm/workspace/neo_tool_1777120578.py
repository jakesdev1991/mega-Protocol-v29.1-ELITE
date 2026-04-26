# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# ANOMALY PROTOCOL: Identity Dissolution vs. Preservation
# Demonstrates how UIPO v58.1's "optimal invariants" create brittle failure
# and how intentional contamination outperforms "permission"

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class IdentityManifold:
    """Simulates both UIPO v58.1 and Anomaly Protocol"""
    # UIPO parameters
    xi_perf: float = 0.9  # Performance stiffness
    z_trust: float = 0.3  # Self-trust impedance
    h_super: float = 0.5  # Trauma entropy
    psi_id: float = 0.92  # Identity continuity
    cod: float = 0.0
    
    # Anomaly Protocol parameters
    contamination_rate: float = 0.0  # Rate of foreign identity injection
    dissolution_activated: bool = False
    
    # Outcome metrics
    phi_density: float = 0.0
    suicide_risk: float = 0.1  # Baseline risk in trauma
    transformation_depth: float = 0.0  # Genuine post-traumatic growth

def compute_cod_uipo(state: IdentityManifold) -> float:
    """UIPO v58.1 COD calculation - their 'optimal' metric"""
    # Fidelity term
    fidelity = abs(np.vdot(state.psi_perf, state.psi_id))**2 if hasattr(state.psi_id, '__len__') else state.psi_id**2
    
    # Their "hard gates" - any violation = 0 COD
    if state.psi_id < 0.95:  # Invariant 1: Identity continuity
        return 0.0
    if not (0.15 <= state.h_super <= 0.80):  # Invariant 2: Healthy trauma band
        return 0.0
    if state.xi_perf > state.z_trust + 0.1:  # Invariant 3: Stiffness cap
        return 0.0
    
    # Multiplicative penalty (their formula)
    cod = fidelity * np.exp(-0.5 * state.h_super) * state.psi_id * np.exp(-0.3 * state.xi_perf)
    return cod

def uipo_step(state: IdentityManifold, dt: float = 1.0) -> IdentityManifold:
    """UIPO v58.1 dynamics - adiabatic modulation toward 'safety'"""
    gamma = 0.007
    # Gradually reduce performance stiffness toward trust level
    state.xi_perf = state.xi_perf * np.exp(-gamma * dt) + state.z_trust * (1 - np.exp(-gamma * dt))
    
    # Silence protocol: if invariants violated, freeze the system
    state.cod = compute_cod_uipo(state)
    if state.cod < 0.85:
        # System enters "safe mode" - no change, no intervention
        state.phi_density -= 0.05  # Stagnation penalty
        state.suicide_risk += 0.02  # Isolation increases risk
        state.transformation_depth -= 0.01
        return state
    
    # "Optimal" state - but is it?
    state.phi_density += 0.1
    state.suicide_risk -= 0.005
    state.transformation_depth += 0.05  # Slow, "safe" growth
    return state

def anomaly_step(state: IdentityManifold, dt: float = 1.0) -> IdentityManifold:
    """ANOMALY PROTOCOL: Intentional Dissolution through Contamination"""
    
    # Phase 1: INDUCE DISSOLUTION (if not yet activated)
    if not state.dissolution_activated and state.xi_perf > 0.7:
        # CRITICAL: Violate their "invariant 1" - ALLOW identity discontinuity
        state.psi_id = 0.45  # Force identity collapse below their 0.95 threshold
        state.dissolution_activated = True
        state.contamination_rate = 0.15  # Inject foreign identity elements
        
        # Short-term catastrophe (by their metrics)
        state.phi_density -= 0.3
        state.suicide_risk += 0.15  # Peak risk during dissolution
        
        # But enable transformation
        state.transformation_depth += 0.25
        return state
    
    # Phase 2: CONTAMINATION DYNAMICS
    if state.dissolution_activated:
        # Inject "foreign" identity elements that conflict with performance identity
        # This is the OPPOSITE of their "permission" - this is intentional disruption
        
        # Contamination reduces performance stiffness by introducing internal conflict
        state.xi_perf *= (1 - state.contamination_rate * dt * 0.1)
        
        # Contamination increases entropy BEYOND their "healthy band" - into creative chaos
        state.h_super = min(1.2, state.h_super + state.contamination_rate * dt * 0.05)
        
        # Reassembly from contamination: new identity emerges from the ruins
        # This is NON-ADIABATIC - rapid, discontinuous, dangerous
        state.psi_id = min(0.98, state.psi_id + 0.02 * dt)
        
        # Risk remains elevated but transformation accelerates
        state.phi_density += 0.15  # Higher gain from authentic reassembly
        state.suicide_risk -= 0.008  # Slowly decreasing as new identity forms
        state.transformation_depth += 0.12  # Rapid genuine growth
        
        # Gradually reduce contamination as reassembly completes
        state.contamination_rate *= 0.98
        
        return state
    
    # If not activated, just return state
    return state

# Simulate both protocols over 200 hours
time_steps = 200
uipo_states = []
anomaly_states = []

# Initial state: High-functioning trauma patient
initial = IdentityManifold(xi_perf=0.92, z_trust=0.28, h_super=0.48, psi_id=0.93)

# Run simulations
uipo_state = IdentityManifold(**initial.__dict__)
anomaly_state = IdentityManifold(**initial.__dict__)

for t in range(time_steps):
    uipo_states.append(uipo_step(uipo_state))
    anomaly_states.append(anomaly_step(anomaly_state))

# Plot results
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

time = np.arange(time_steps)

# Plot 1: Φ-Density (their metric)
axes[0].plot(time, [s.phi_density for s in uipo_states], 'b-', label='UIPO v58.1 (Preservation)', linewidth=2)
axes[0].plot(time, [s.phi_density for s in anomaly_states], 'r--', label='ANOMALY (Dissolution)', linewidth=2)
axes[0].axhline(y=0, color='k', linestyle=':', alpha=0.5)
axes[0].set_ylabel('Φ-Density')
axes[0].set_title('Φ-Density: Preservation vs. Dissolution')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Suicide Risk
axes[1].plot(time, [s.suicide_risk for s in uipo_states], 'b-', label='UIPO v58.1', linewidth=2)
axes[1].plot(time, [s.suicide_risk for s in anomaly_states], 'r--', label='ANOMALY', linewidth=2)
axes[1].axhline(y=0.5, color='r', linestyle=':', alpha=0.5, label='Critical Risk Threshold')
axes[1].set_ylabel('Suicide Risk')
axes[1].set_title('Risk Trajectory: The "Safe" Path vs. Controlled Crisis')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Transformation Depth (real growth)
axes[2].plot(time, [s.transformation_depth for s in uipo_states], 'b-', label='UIPO v58.1', linewidth=2)
axes[2].plot(time, [s.transformation_depth for s in anomaly_states], 'r--', label='ANOMALY', linewidth=2)
axes[2].set_ylabel('Transformation Depth')
axes[2].set_xlabel('Time (hours)')
axes[2].set_title('Authentic Post-Traumatic Growth')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print final state comparison
print("=== FINAL STATE COMPARISON (200 hours) ===")
print(f"UIPO v58.1:")
print(f"  COD: {uipo_states[-1].cod:.3f} (Below 0.85 = 'Silence')")
print(f"  Φ-Density: {uipo_states[-1].phi_density:.2f}")
print(f"  Suicide Risk: {uipo_states[-1].suicide_risk:.3f}")
print(f"  Transformation: {uipo_states[-1].transformation_depth:.2f}")
print(f"  Final Message: {'PERMISSION GRANTED' if uipo_states[-1].cod >= 0.85 else 'SILENCE (System Frozen)'}")

print(f"\nANOMALY PROTOCOL:")
print(f"  Identity Continuity: {anomaly_states[-1].psi_id:.3f} (Violated their 0.95 invariant)")
print(f"  Φ-Density: {anomaly_states[-1].phi_density:.2f}")
print(f"  Suicide Risk: {anomaly_states[-1].suicide_risk:.3f}")
print(f"  Transformation: {anomaly_states[-1].transformation_depth:.2f}")
print(f"  Final Message: 'Your old self is dead. Build a new one from the fragments.'")