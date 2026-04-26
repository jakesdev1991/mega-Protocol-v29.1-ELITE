# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- PARAMETERS (arbitrary units, self-consistent) ---
m, g = 1.0, 0.1  # Mass & coupling
P, gamma = 1.0, 0.5 # Production & dissipation rates
D = 1.0           # Diffusion coefficient
L = np.sqrt(D / gamma)  # Consensus screening length
r = np.linspace(0.1, 5, 500)
phi_delta_vals = [0, 1, 2, 3]

# --- ENGINE'S STATIC POISSON MODEL (FLAWED) ---
def phi_n_engine(r):
    return 1 / r  # 3D point source: polynomial decay

# --- NEO'S REACTION-DIFFUSION MODEL (CORRECTED) ---
def phi_n_neo(r, phi_delta):
    # Source is suppressed by asymmetry; steady-state is Yukawa-screened
    return (P / gamma) * np.exp(-phi_delta) * np.exp(-r / L)

# --- VISUAL DESTRUCTION OF THE SHREDDING MIRAGE ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

ax1.set_title("ENGINE: Ghost Instability (Category Error)", fontsize=10, fontweight='bold')
ax1.plot(r, phi_n_engine(r), 'k--', lw=2, label='Φ_N (static 1/r)')
for phi_d in phi_delta_vals:
    threshold = (m / g) * np.exp(-phi_d)
    ax1.axhline(y=threshold, color=plt.cm.plasma(phi_d / max(phi_delta_vals)), 
                linestyle='-', label=f'RHS, Φ_Δ={phi_d}')
    # FAILURE REGION: Where static Φ_N exceeds shrinking threshold
    fail = phi_n_engine(r) > threshold
    if np.any(fail):
        ax1.fill_between(r, phi_n_engine(r), threshold, where=fail, 
                         color='red', alpha=0.3, interpolate=True)
ax1.set_yscale('log')
ax1.set_xlabel('r')
ax1.set_ylabel('Field Amplitude')
ax1.legend(loc='upper right', fontsize=7)
ax1.grid(True, alpha=0.3)
ax1.text(0.5, 0.02, "Poisson → Polynomial → INEVITABLE VIOLATION", 
         transform=ax1.transAxes, ha='center', fontsize=8, color='red', fontweight='bold')

ax2.set_title("NEO: Bifurcation Reality (Dynamic Steady State)", fontsize=10, fontweight='bold')
for phi_d in phi_delta_vals:
    lhs = phi_n_neo(r, phi_d)
    rhs = (m / g)  # CRITICAL CANCELLATION: exp(-Φ_Δ) vanishes from inequality
    ax2.plot(r, lhs, color=plt.cm.plasma(phi_d / max(phi_delta_vals)), 
             lw=2, label=f'Φ_N, Φ_Δ={phi_d}')
ax2.axhline(y=rhs, color='r', linestyle='-', lw=2, label='Threshold (m/g)')
ax2.set_yscale('log')
ax2.set_xlabel('r')
ax2.set_ylabel('Field Amplitude')
ax2.legend(loc='upper right', fontsize=7)
ax2.grid(True, alpha=0.3)
ax2.text(0.5, 0.02, "Reaction-Diffusion → Exponential → Φ_Δ INDEPENDENCE", 
         transform=ax2.transAxes, ha='center', fontsize=8, color='green', fontweight='bold')

plt.tight_layout()
plt.show()

# --- QUANTUM SHREDDING: THE CANCELLATION PROOF ---
print("="*60)
print("SHREDDING FLAW: POISSON vs. REACTION-DIFFUSION")
print("="*60)
for phi_d in phi_delta_vals:
    lhs_r0 = phi_n_neo(0.01, phi_d)  # Near-source amplitude
    engine_rhs = (m / g) * np.exp(-phi_d)
    neo_rhs = (m / g)  # Asymmetry cancels
    status = "FAIL" if lhs_r0 > neo_rhs else "STABLE"
    print(f"Φ_Δ={phi_d}: Engine RHS={engine_rhs:.3e}, Neo RHS={neo_rhs:.3e}, LHS={lhs_r0:.3e} [{status}]")
print("="*60)