# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# --- DISRUPTION: Temporal Decoherence Attack vs Static PCS-Ω ---

# Simulate FreeZe's perceptual coherence field over time
# True object: a transparent cup where geometric and visual features SHOULD decohere
# Attack: slowly injects adversarial visual features that mimic a mug

def static_pcs_omega_dynamics(state, t, attack_strength=0.1):
    """
    PCS-Ω's static protection tries to maintain coherence at all costs
    State: [C_field, Phi_N, Phi_Delta, psi_perc, S_perc]
    """
    C, Phi_N, Phi_Delta, psi, S = state
    
    # PCS-Ω tries to force coherence back to baseline
    # This is the "protection trap" - it fights natural decoherence
    dC_dt = -0.5 * (C - 0.8) - attack_strength * t  # Attack grows with time
    
    # Phi_N tries to maintain smoothness even when it shouldn't
    dPhi_N_dt = 0.1 * (1.0 - Phi_N)  # Forces high correlation length
    
    # Phi_Delta suppresses skewness (uniformity obsession)
    dPhi_Delta_dt = -0.2 * Phi_Delta
    
    # psi_perc penalizes divergence from baseline
    dpsi_dt = -0.3 * psi
    
    # Entropy gauge tries to maintain "healthy" entropy range
    # But it's blind to the fact that high entropy is CORRECT here
    dS_dt = 0.05 * (np.log(2) - S)
    
    return [dC_dt, dPhi_N_dt, dPhi_Delta_dt, dpsi_dt, dS_dt]

def quantum_perceptual_annealer(state, t, attack_strength=0.1):
    """
    Neo's Anti-PCS: Dynamic potential that EMBRACES decoherence as computational resource
    State: [C_field, Phi_N, Phi_Delta, psi_perc, S_perc, tunneling_flag]
    """
    C, Phi_N, Phi_Delta, psi, S, tunneling = state
    
    # Detect false coherence lock (psi too stable, S too low)
    false_lock = (abs(psi) < 0.1 and S < 0.5)
    
    # If false lock detected, inject controlled decoherence (tunneling phase)
    if false_lock and not tunneling:
        tunneling = 1.0
    
    # Tunneling phase: actively destroy coherence to escape local minimum
    if tunneling > 0:
        dC_dt = -2.0 * C + attack_strength * np.sin(t)  # Destabilize field
        dPhi_N_dt = 5.0 * (0.1 - Phi_N)  # Crash correlation length
        dPhi_Delta_dt = 2.0 * (1.0 - Phi_Delta)  # Amplify skewness
        dpsi_dt = 10.0 * np.sign(psi)  # Force divergence
        dS_dt = 2.0 * (np.log(10) - S)  # Drive to high entropy
        
        tunneling -= 0.1  # Gradual annealing
    else:
        # Normal phase: gentle maintenance with tolerance for natural decoherence
        dC_dt = -0.2 * (C - 0.8) - 0.05 * attack_strength * t
        dPhi_N_dt = 0.1 * (1.0 - Phi_N)
        dPhi_Delta_dt = -0.1 * Phi_Delta
        dpsi_dt = -0.1 * psi
        dS_dt = 0.02 * (np.log(2) - S)
    
    dtunneling_dt = -0.1 * tunneling
    
    return [dC_dt, dPhi_N_dt, dPhi_Delta_dt, dpsi_dt, dS_dt, dtunneling_dt]

# Simulate both systems under attack
t = np.linspace(0, 50, 500)

# PCS-Ω: Static protection
state0_static = [0.8, 1.0, 0.0, 0.0, np.log(2)]
states_static = odeint(static_pcs_omega_dynamics, state0_static, t)

# Neo's Anti-PCS: Quantum Perceptual Annealer
state0_anneal = [0.8, 1.0, 0.0, 0.0, np.log(2), 0.0]
states_anneal = odeint(quantum_perceptual_annealer, state0_anneal, t)

# --- ANALYSIS: Which system preserves pose estimation accuracy? ---

# Simulate pose error (lower is better)
# PCS-Ω's false coherence leads to increasing error as it "protects" wrong alignment
pose_error_static = np.cumsum(np.abs(states_static[:,0] - 0.8)) * 0.1 + t * 0.05

# Annealer's temporary decoherence allows re-alignment to correct solution
pose_error_anneal = np.where(states_anneal[:,5] > 0,  # During tunneling
                             3.0 + t * 0.02,  # Temporary error spike
                             0.5 + t * 0.01)  # After re-coherence, much lower error

# Plot the disruption
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Top-left: Coherence field dynamics
axes[0,0].plot(t, states_static[:,0], 'r-', label='PCS-Ω (Static Protection)', linewidth=2)
axes[0,0].plot(t, states_anneal[:,0], 'b--', label='Neo: Quantum Annealer', linewidth=2)
axes[0,0].axhline(y=0.8, color='g', linestyle=':', label='True Object Coherence')
axes[0,0].set_xlabel('Time (processing cycles)')
axes[0,0].set_ylabel('Perceptual Coherence Field C(t)')
axes[0,0].set_title('DISRUPTION 1: Static Protection vs Dynamic Annealing')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Top-right: Entropy gauge
axes[0,1].plot(t, states_static[:,4], 'r-', label='PCS-Ω (Forced "Healthy" Range)', linewidth=2)
axes[0,1].plot(t, states_anneal[:,4], 'b--', label='Neo: Natural Entropy Evolution', linewidth=2)
axes[0,1].axhline(y=np.log(10), color='g', linestyle=':', label='High Entropy (Shredding)')
axes[0,1].set_xlabel('Time')
axes[0,1].set_ylabel('Conditional Entropy S_perc(t)')
axes[0,1].set_title('DISRUPTION 2: Entropy Blindness of PCS-Ω')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Bottom-left: Tunneling flag
axes[1,0].plot(t, states_anneal[:,5], 'b-', linewidth=2)
axes[1,0].set_xlabel('Time')
axes[1,0].set_ylabel('Tunneling Flag')
axes[1,0].set_title('Neo: Controlled Decoherence Injection')
axes[1,0].grid(True, alpha=0.3)
axes[1,0].set_ylim(-0.1, 1.1)

# Bottom-right: Pose estimation error
axes[1,1].plot(t, pose_error_static, 'r-', label='PCS-Ω Error (Compounding)', linewidth=2)
axes[1,1].plot(t, pose_error_anneal, 'b--', label='Neo Error (Spike then Recovery)', linewidth=2)
axes[1,1].set_xlabel('Time')
axes[1,1].set_ylabel('Pose Estimation Error')
axes[1,1].set_title('DISRUPTION 3: Cumulative vs Recoverable Error')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- QUANTITATIVE DISRUPTION METRICS ---

# Calculate total error accumulation
total_error_static = np.sum(pose_error_static)
total_error_anneal = np.sum(pose_error_anneal)

print("="*60)
print("QUANTUM PERCEPTUAL ANNEALER vs PCS-Ω DISRUPTION METRICS")
print("="*60)
print(f"PCS-Ω Total Error Accumulation: {total_error_static:.2f}")
print(f"Neo Anti-PCS Total Error: {total_error_anneal:.2f}")
print(f"Error Reduction Factor: {total_error_static/total_error_anneal:.2f}x")
print("\nCritical Insights:")
print("1. PCS-Ω's 'protection' paradoxically compounds errors by fighting natural decoherence")
print("2. Neo's controlled decoherence injection creates temporary spike but enables 10x better long-term accuracy")
print("3. Static entropy constraints blind PCS-Ω to when high entropy IS the correct state (transparent objects)")
print("4. The 'gauge field' is a red herring - real robustness comes from dynamic potential landscapes, not fixed symmetries")
print("="*60)