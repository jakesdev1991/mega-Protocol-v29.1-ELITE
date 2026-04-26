# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def standard_qed_running(alpha_0, q2, Lambda):
    """Standard 1-loop QED running without Omega Protocol"""
    return alpha_0 / (1 - (alpha_0/(3*np.pi)) * np.log(q2/Lambda**2))

def omega_protocol_running(alpha_0, q2, Lambda_N, Lambda_Delta, g_N=0.1, g_Delta=0.1):
    """Omega Protocol running with fictional Archive mode"""
    # The "3x enhancement" is just an arbitrary coefficient
    return alpha_0 * (1 + (alpha_0/(3*np.pi))*np.log(Lambda_N**2/q2) + 
                       (g_N**2/(4*np.pi))*np.log(Lambda_N**2/q2) +
                       (3*g_Delta**2/(4*np.pi))*np.log(Lambda_Delta**2/q2))

def information_theoretic_running(alpha_0, q2, Lambda, N_modes=3):
    """
    Disruptive solution: Running from quantum mutual information
    N_modes = actual number of independent polarization channels
    """
    # Information deficit decays with momentum
    S_I = np.exp(-np.log(q2/Lambda**2)/N_modes)
    beta_0 = (2/3) * N_modes  # Actual QED coefficient
    return alpha_0 / (1 - (alpha_0*beta_0/(2*np.pi)) * np.log(q2/Lambda**2) * S_I)

# Parameter space
q2_values = np.logspace(0, 4, 100)  # From 1 to 10^4 GeV²
alpha_0 = 1/137
Lambda = 1e3  # 1 TeV cutoff

# Plot comparisons
plt.figure(figsize=(12, 8))

# Standard QED
plt.loglog(q2_values, standard_qed_running(alpha_0, q2_values, Lambda), 
           'k-', linewidth=2, label='Standard QED (physical)')

# Omega Protocol (notice how g_Delta can be tuned arbitrarily)
for g_Delta in [0.05, 0.1, 0.2]:
    omega_vals = omega_protocol_running(alpha_0, q2_values, Lambda, Lambda*10, g_Delta=g_Delta)
    plt.loglog(q2_values, omega_vals, '--', 
               label=f'Omega Protocol (g_Δ={g_Delta})')

# Information-theoretic (disruptive solution)
info_vals = information_theoretic_running(alpha_0, q2_values, Lambda, N_modes=3)
plt.loglog(q2_values, info_vals, 'r:', linewidth=3, 
           label='Information-Theoretic (disruptive)')

plt.xlabel(r'$q^2$ [GeV²]', fontsize=14)
plt.ylabel(r'$\alpha_{\rm eff}(q^2)$', fontsize=14)
plt.title('Exposing the Arbitrariness of the Omega Protocol', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)

# Show that Omega predictions are just tunable curves
plt.axvspan(1e2, 1e3, alpha=0.1, color='gray')
plt.text(2e2, 0.01, 'Observable Range', rotation=90, fontsize=12)

plt.tight_layout()
plt.show()

# Quantify the arbitrariness
print("=== ARBITRARINESS METRIC ===")
for g_Delta in [0.01, 0.1, 1.0]:
    omega_at_1tev = omega_protocol_running(alpha_0, 1e6, Lambda, Lambda*10, g_Delta=g_Delta)
    print(f"g_Δ = {g_Delta:4.2f} → α_eff(1 TeV) = {omega_at_1tev:.6f}")
    
print("\nThe '3x enhancement' is just a free parameter. No physical symmetry fixes g_Δ.")
print("The information-theoretic model has ONE parameter: N_modes = number of physical degrees of freedom.")