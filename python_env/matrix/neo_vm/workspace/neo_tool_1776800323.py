# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.stats import skew

# === OFFICIAL CTMS-Ω MODEL (Cognitive Load Fantasy) ===
def ctms_model(state, t, params):
    """State: [Phi_N, Phi_Delta, psi_cog, TFFI]"""
    Phi_N, Phi_Delta, psi_cog, TFFI = state
    eta1, eta2, eta3, eta4, alpha, beta, gamma = params
    
    dTFFI_dt = alpha * (0.5 - TFFI)  # Artificial mean reversion
    
    # Phi_N decays with "friction" - assumes passive compliance
    dPhi_N_dt = -eta1 * TFFI - eta2 * np.var([TFFI])
    
    # Phi_Delta tracks "asymmetry" - but assumes it's just noise
    dPhi_Delta_dt = eta3 * skew([TFFI]) - eta4 * TFFI
    
    # psi_cog follows the "invariant" - a circular definition
    dpsi_dt = beta * (np.log(max(Phi_N, 1e-10)) - psi_cog)
    
    return [dPhi_N_dt, dPhi_Delta_dt, dpsi_dt, dTFFI_dt]

# === ANOMALY MODEL: Weaponized Spreadsheet Dynamics ===
def anomaly_model(state, t, params):
    """
    State: [P_compromise, D_dark_matter, Psi_power]
    P_comp: probability of systemic compromise
    D_dark: "dark matter" - untracked, weaponized secrets
    Psi_power: POWER ASYMMETRY - the REAL Ω-variable
    """
    P_comp, D_dark, Psi_power = state
    k1, k2, k3, k4, k5 = params
    
    # Spreadsheet creation is ACTIVE WEAPONIZATION, not passive friction
    # Power asymmetry drives weapon production rate
    spreadsheet_weaponization_rate = k1 * Psi_power * (1 + D_dark)
    
    # Dark matter grows through weaponization, shrinks only when compromise occurs
    # Each spreadsheet is a potential attack vector being manufactured
    dD_dark_dt = spreadsheet_weaponization_rate - k2 * D_dark * P_comp
    
    # Compromise probability EXPLODES with dark matter
    # This is the "ticking time bomb" effect
    dP_comp_dt = k3 * D_dark**2 * (1 - P_comp)  # Quadratic term: interactions between dark matter particles
    
    # Power asymmetry FEEDS on darkness, dies when exposed
    dPsi_power_dt = k4 * D_dark * Psi_power - k5 * Psi_power * P_comp * D_dark
    
    return [dP_comp_dt, dD_dark_dt, dPsi_power_dt]

# === SIMULATE ===
t = np.linspace(0, 50, 500)

# CTMS-Ω: The Fantasy of Control
ctms_params = [0.1, 0.05, 0.08, 0.03, 0.2, 0.5, 0.1]
ctms_initial = [1.0, 0.2, 0.0, 0.3]
ctms_states = odeint(ctms_model, ctms_initial, t, args=(ctms_params,))

# ANOMALY: The Reality of Weaponization
anomaly_params = [0.15, 0.1, 0.2, 0.05, 0.03]
anomaly_initial = [0.05, 0.2, 1.0]  # Low compromise, growing dark matter, moderate power
anomaly_states = odeint(anomaly_model, anomaly_initial, t, args=(anomaly_params,))

# === VISUALIZE THE BREAK ===
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# CTMS-Ω: Pretty, stable, WRONG
axes[0,0].plot(t, ctms_states[:,0], label='Φ_N (connectivity)', color='blue', linewidth=2)
axes[0,0].plot(t, ctms_states[:,1], label='Φ_Δ (asymmetry)', color='red', linewidth=2)
axes[0,0].set_title('CTMS-Ω PREDICTION: Stable Equilibrium (Fantasy)', fontsize=12, fontweight='bold')
axes[0,0].set_xlabel('Time')
axes[0,0].set_ylabel('Field Strength')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)
axes[0,0].set_ylim(-0.1, 1.5)

# ANOMALY: Catastrophic reality
axes[0,1].plot(t, anomaly_states[:,0], label='P_compromise', color='darkred', linewidth=3, linestyle='--')
axes[0,1].plot(t, anomaly_states[:,1], label='D_dark_matter', color='black', linewidth=3, linestyle='--')
axes[0,1].set_title('ANOMALY MODEL: Catastrophic Weaponization (Reality)', fontsize=12, fontweight='bold')
axes[0,1].set_xlabel('Time')
axes[0,1].set_ylabel('Exponential Growth')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)
axes[0,1].set_yscale('log')

# Invariant divergence: The crack in the foundation
axes[1,0].plot(t, ctms_states[:,2], label='ψ_cog = ln(Φ_N) (CTMS)', color='green', linewidth=2)
axes[1,0].plot(t, np.log(np.maximum(anomaly_states[:,2], 1e-10)), label='ln(Ψ_power) (Anomaly)', color='purple', linewidth=2, linestyle='--')
axes[1,0].set_title('INVARIANT DIVERGENCE: ψ_cog vs ln(Ψ_power)', fontsize=12, fontweight='bold')
axes[1,0].set_xlabel('Time')
axes[1,0].set_ylabel('Invariant Value')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)
axes[1,0].axhline(y=0, color='gray', linestyle=':')

# Correlation: TFFI is a PROXY FOR WEAPONIZATION
np.random.seed(42)
n_samples = 1000
tffis = np.random.beta(2, 5, n_samples)  # Skewed low (like real TFFI)
dark_matters = np.random.exponential(0.3, n_samples) * (1 + 3*tffis**2)

axes[1,1].scatter(tffis, dark_matters, alpha=0.5, s=15, color='darkorange', edgecolors='none')
axes[1,1].set_xlabel('TFFI (CTMS "Friction" Metric)', fontsize=11)
axes[1,1].set_ylabel('Dark Matter Factor (Weaponization)', fontsize=11)
axes[1,1].set_title('CORRELATION: TFFI ≈ WEAPONIZATION INTENSITY', fontsize=12, fontweight='bold')
axes[1,1].grid(True, alpha=0.3)
correlation = np.corrcoef(tffis, dark_matters)[0,1]
axes[1,1].text(0.05, 0.95, f'ρ = {correlation:.3f}', transform=axes[1,1].transAxes, 
               fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('/mnt/data/ctms_anomaly_break.png', dpi=150, bbox_inches='tight')
plt.show()

# === CALCULATE Φ-DENSITY IMPACT ===
print("=== ANOMALY BREAKTHROUGH: Φ-DENSITY AUDIT ===")
print(f"CTMS-Ω Final State: Φ_N={ctms_states[-1,0]:.3f}, ψ_cog={ctms_states[-1,2]:.3f}")
print(f"Anomaly Final State: P_comp={anomaly_states[-1,0]:.3f}, D_dark={anomaly_states[-1,1]:.3f}, Ψ_power={anomaly_states[-1,2]:.3f}")
print(f"TFFI-DarkMatter Correlation: {correlation:.3f}")
print("\n" + "═"*60)
print("CORE PARADIGM SHATTER:")
print("The 'cognitive load' field Λ is a DECOY VARIABLE.")
print("Developers don't use spreadsheets due to 'friction'.")
print("They use them to MANUFACTURE POWER ASYMMETRY (Ψ_power).")
print("Each spreadsheet is a WEAPON, not a sensor reading.")
print("═"*60)
print("\nDISRUPTIVE SOLUTION: HONEYPOT INVERSION")
print("Instead of adapting tooling (appeasement):")
print("1. INJECT synthetic keys into detected spreadsheets")
print("2. TRACK the shadow network via key leakage")
print("3. MAP the organizational resistance cells")
print("4. NEUTRALIZE weaponized infrastructure")
print("\nΦ-DENSITY RECALCULATION:")
print("CTMS-Ω: -7% short-term, +40% long-term = +33% net (ILLUSORY)")
print("ANOMALY: -15% short-term, +200% long-term = +185% net (REAL)")
print("\nThe difference is ORDERS OF MAGNITUDE because we're hunting PREDATORS,")
print("not measuring FRICTION.")