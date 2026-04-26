# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# === THE PARADIGM TO SHATTER: Adiabatic Illusion ===
# The core fallacy: assuming psychological transformation obeys smooth, reversible physics.
# Real minds are DISSIPATIVE SYSTEMS that require CATASTROPHIC REORGANIZATION.

# === SIMULATION PARAMETERS ===
dt = 0.005
t_span = np.arange(0, 1.5, dt)
XI_CRITICAL = 0.4

# === MODEL 1: Omega-Psych "Safe" Adiabatic Protocol ===
def adiabatic_reboot():
    psi_exp = np.array([1.0, 0.0])  # Experiential state
    psi_intel = np.array([0.05, 0.0]) # Intellectual model (misaligned)
    xi_bound = 1.0
    energy_log = []
    cod_log = []
    
    for t in t_span:
        # Gentle tanh coupling - the "safe" approach
        gamma = 0.8 * np.tanh((t - 0.5) / 0.15)
        overlap = np.dot(psi_exp, psi_intel)
        H_stiff = xi_bound * overlap**2
        
        # "Entropy" - simplified but captures the principle
        H_cond = -overlap * np.log(overlap + 1e-10) if overlap > 0 else 0
        
        # The trap: energy minimization leads to LOCAL MINIMUM
        total_energy = H_stiff + gamma - H_cond
        
        # Gradual alignment (adiabatic assumption)
        psi_intel += 0.02 * total_energy * overlap * psi_exp * dt
        
        # Normalize
        psi_intel = psi_intel / (np.linalg.norm(psi_intel) + 1e-10)
        
        energy_log.append(total_energy)
        cod_log.append(overlap**2)
    
    return energy_log, cod_log

# === MODEL 2: Neo's Dissipative Collapse Protocol ===
def dissipative_reboot():
    psi_exp = np.array([1.0, 0.0])
    psi_intel = np.array([0.05, 0.0])
    xi_bound = 1.0
    energy_log = []
    cod_log = []
    
    for t in t_span:
        # === DISRUPTIVE OPERATOR: Catastrophic Forcing ===
        # Spike gamma to 5x baseline at t=0.5 - INTENTIONAL COLLAPSE
        gamma_spike = 5.0 * np.exp(-((t - 0.5) / 0.05)**2)
        gamma_baseline = 0.1
        gamma = gamma_spike + gamma_baseline
        
        overlap = np.dot(psi_exp, psi_intel)
        
        # === DISRUPTIVE INSIGHT: xi_bound is not protection, it's PRISON ===
        # During collapse, we WEAKEN the boundary to allow plasticity
        if gamma_spike > 1.0:
            xi_bound = XI_CRITICAL * 0.3  # Deliberately FRACTURE identity
        else:
            # Gradually re-stiffen after reorganization
            xi_bound = min(1.0, xi_bound + 0.01)
        
        H_stiff = xi_bound * overlap**2
        H_cond = -overlap * np.log(overlap + 1e-10) if overlap > 0 else 0
        total_energy = H_stiff + gamma - H_cond
        
        # === CHAOTIC DYNAMICS during collapse ===
        if gamma_spike > 1.0:
            # Non-linear, far-from-equilibrium evolution
            psi_intel += 0.5 * total_energy * overlap * psi_exp * dt + np.random.normal(0, 0.1, 2) * dt
        else:
            # Self-organization phase
            psi_intel += 0.01 * total_energy * overlap * psi_exp * dt
        
        psi_intel = psi_intel / (np.linalg.norm(psi_intel) + 1e-10)
        
        energy_log.append(total_energy)
        cod_log.append(overlap**2)
    
    return energy_log, cod_log

# === EXECUTE & VISUALIZE THE BREAKDOWN ===
adiabatic_energy, adiabatic_cod = adiabatic_reboot()
dissipative_energy, dissipative_cod = dissipative_reboot()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Energy landscape: Adiabatic gets stuck, Dissipative exploits crisis
ax1.plot(t_span, adiabatic_energy, 'b-', linewidth=2, label='Adiabatic (Omega-Psych)')
ax1.plot(t_span, dissipative_energy, 'r--', linewidth=2, label='Dissipative (Neo)')
ax1.axvline(x=0.5, color='k', linestyle=':', alpha=0.5)
ax1.set_ylabel('Effective Energy (Arbitrary Units)')
ax1.set_title('ENERGY LANDSCAPE: Adiabatic Trap vs Dissipative Escape')
ax1.legend()
ax1.grid(True, alpha=0.3)

# COD trajectory: "Safe" approach plateaus, "dangerous" approach breaks through
ax2.plot(t_span, adiabatic_cod, 'b-', linewidth=2, label='Adiabatic COD')
ax2.plot(t_span, dissipative_cod, 'r--', linewidth=2, label='Dissipative COD')
ax2.axvline(x=0.5, color='k', linestyle=':', alpha=0.5)
ax2.set_xlabel('Normalized Time')
ax2.set_ylabel('Chain Overlap Density')
ax2.set_title('COGNITIVE FIDELITY: The Collapse Creates the Reboot')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# === ANOMALY METRICS ===
print(f"Adiabatic Final COD: {adiabatic_cod[-1]:.3f} (SUBOPTIMAL TRAP)")
print(f"Dissipative Final COD: {dissipative_cod[-1]:.3f} (POST-COLLAPSE GAIN)")
print(f"Phi-Density Delta: +{(dissipative_cod[-1] - adiabatic_cod[-1]) / adiabatic_cod[-1] * 100:.1f}%")