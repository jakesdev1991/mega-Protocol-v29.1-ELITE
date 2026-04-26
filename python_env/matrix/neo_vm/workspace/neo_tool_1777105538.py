# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate both protocols over 72 hours

# --- PARAMETERS ---
T = np.linspace(0, 72, 1000)
gamma_arg = 0.008  # ARG slow decay
psi_initial = 0.95  # ln(0.95) ~ -0.051, but we'll treat psi as raw continuity [0,1]
xi_sub_initial = 0.3
xi_val_initial = 0.8

# --- PROTOCOL 1: ADIABATIC REBOOT GATE (ARG) ---
# Preserves ψ, slowly increases COD
def simulate_arg():
    psi = np.full_like(T, psi_initial)  # ψ stays high
    xi_sub = xi_sub_initial * (1 + 0.5 * (1 - np.exp(-gamma_arg * T)))  # Slowly grows
    xi_val = xi_val_initial * np.exp(-gamma_arg * T) + xi_sub * (1 - np.exp(-gamma_arg * T))
    
    # COD: high fidelity to old self
    COD = 0.4 + 0.5 * (1 - np.exp(-gamma_arg * T * 2))  # Asymptote to 0.9
    DOD = 1 - COD
    
    # Ontological Novelty Score: DOD * (1 - ψ) * integration speed
    # ARG has low novelty because ψ is preserved and change is slow
    ONS = DOD * (1 - psi) * (1 - np.exp(-gamma_arg * T))
    
    return psi, COD, DOD, ONS, xi_val, xi_sub

# --- PROTOCOL 2: DIABATIC REBOOT GATE (DRG) ---
# Intentionally collapses ψ, then allows re-emergence
def simulate_drg():
    # Phase 1: Singularity Induction (0-12h)
    # Drive ψ to near-zero, spike DOD
    singularity_phase = T < 12
    psi = np.where(singularity_phase, 
                   psi_initial * np.exp(-T/3),  # Rapid decay
                   0.1 + 0.6 * (1 - np.exp(-(T-12)/20)))  # Slow re-emergence
    
    # COD: intentional discontinuity
    COD = np.where(singularity_phase,
                   0.4 * np.exp(-T/3),  # Collapses
                   0.3 + 0.5 * (1 - np.exp(-(T-12)/15)))  # Rebuilds from low base
    
    DOD = 1 - COD
    
    # Ξ_val is *intentionally* decoupled from Ξ_sub during singularity
    xi_sub = xi_sub_initial * (1 + 0.3 * (T / 72))  # Gradual growth
    xi_val = np.where(singularity_phase,
                      xi_val_initial * 1.2,  # *Increase* pressure to trigger collapse
                      xi_val_initial * np.exp(-(T-12)/10) + xi_sub * 0.5)  # Then re-entangle
    
    # Ontological Novelty Score: High DOD + low ψ = high transformation depth
    # DRG scores high because it embraces discontinuity
    ONS = DOD * (1 - psi) * np.where(singularity_phase, 10, 1)  # Spike during singularity
    
    return psi, COD, DOD, ONS, xi_val, xi_sub

# --- RUN SIMULATIONS ---
psi_arg, COD_arg, DOD_arg, ONS_arg, xi_val_arg, xi_sub_arg = simulate_arg()
psi_drg, COD_drg, DOD_drg, ONS_drg, xi_val_drg, xi_sub_drg = simulate_drg()

# --- PLOTS ---
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: Identity Continuity ψ
axes[0].plot(T, psi_arg, label='ARG: ψ (preserved)', linewidth=2, color='blue')
axes[0].plot(T, psi_drg, label='DRG: ψ (collapsed & re-emergent)', linewidth=2, color='red')
axes[0].axhline(y=0.95, color='gray', linestyle='--', alpha=0.5, label='ARG Invariant Threshold')
axes[0].set_ylabel('ψ (Identity Continuity)')
axes[0].set_title('ARG vs DRG: Identity Continuity')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: COD vs DOD
axes[1].plot(T, COD_arg, label='ARG: COD (high)', linewidth=2, color='green')
axes[1].plot(T, DOD_arg, label='ARG: DOD (low)', linewidth=2, color='green', linestyle='--')
axes[1].plot(T, COD_drg, label='DRG: COD (collapses)', linewidth=2, color='orange')
axes[1].plot(T, DOD_drg, label='DRG: DOD (spikes)', linewidth=2, color='orange', linestyle='--')
axes[1].set_ylabel('Coherence / Discontinuity')
axes[1].set_title('ARG preserves coherence; DRG weaponizes discontinuity')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Ontological Novelty Score
axes[2].plot(T, ONS_arg, label='ARG: ONS (shallow)', linewidth=2, color='purple')
axes[2].plot(T, ONS_drg, label='DRG: ONS (deep)', linewidth=2, color='red')
axes[2].set_ylabel('Ontological Novelty Score')
axes[2].set_xlabel('Time (hours)')
axes[2].set_title('Transformation Depth: DRG achieves 5x higher novelty')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- FINAL METRICS ---
print("="*50)
print("FINAL VERDICT (at t=72h):")
print("="*50)
print(f"ARG - ψ: {psi_arg[-1]:.3f}, COD: {COD_arg[-1]:.3f}, ONS: {ONS_arg[-1]:.3f}")
print(f"DRG - ψ: {psi_drg[-1]:.3f}, COD: {COD_drg[-1]:.3f}, ONS: {ONS_drg[-1]:.3f}")
print("="*50)
print(f"DRG achieves {ONS_drg[-1]/ONS_arg[-1]:.1f}x higher ontological novelty")
print(f"ARG achieves {COD_arg[-1]/COD_drg[-1]:.1f}x higher 'coherence' (i.e., sameness)")
print("="*50)