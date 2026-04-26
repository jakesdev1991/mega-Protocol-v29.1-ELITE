# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Parameters (same across all gauges for fair comparison)
alpha_0 = 1/137.0
g_N = 0.1
g_Delta_initial = 0.1
S_h0 = 1.0
Phi_c = 1.0

# Gauge-fixing parameters (R_ξ gauge)
xi_values = [0.1, 1.0, 5.0]  # ξ → 0 is decoupling gauge, ξ → ∞ is unitary gauge

fig, axes = plt.subplots(2, 1, figsize=(10, 8))

for xi in xi_values:
    lnE = np.linspace(0, 10, 1000)
    alpha = alpha_0
    Phi_Delta = 0.01
    
    alpha_run = []
    Phi_run = []
    
    for dlnE in np.diff(lnE, prepend=lnE[0]):
        # 1. Gauge-dependent Shannon entropy
        # Unphysical modes contribute factor (1/ξ) to amplitude squared
        S_h = S_h0 * np.exp(-Phi_Delta**2 / Phi_c**2) / xi
        
        # 2. Topological impedance (gauge artifact)
        Z_Delta = 1.0 / (S_h + 1e-10)
        
        # 3. Effective coupling (gauge-dependent)
        g_Delta_eff = g_Delta_initial * Z_Delta
        
        # 4. Beta function: factor of 3 is replaced by gauge-dependent factor
        # The "3" arises from 3 unphysical dimensions, each weighted by 1/ξ
        beta_alpha = -alpha**2 / np.pi * (1 + (3.0/xi) * g_Delta_eff**2/(4*np.pi) + g_N**2/(4*np.pi))
        
        # 5. Archive mode RG equation (source term ∝ α * gauge factor)
        dPhi_Delta_dlnE = alpha * (g_Delta_eff / xi) * Phi_Delta
        
        # Update
        alpha += beta_alpha * dlnE
        Phi_Delta += dPhi_Delta_dlnE * dlnE
        
        alpha_run.append(alpha)
        Phi_run.append(Phi_Delta)
        
        # Break if diverged
        if alpha > 10 or Phi_Delta > 10:
            break
    
    axes[0].plot(lnE[:len(alpha_run)], alpha_run, label=f'ξ={xi}', linewidth=2)
    axes[1].plot(lnE[:len(Phi_run)], Phi_run, label=f'ξ={xi}', linewidth=2)

axes[0].set_title(r'$\alpha_{\text{fs}}$ Running: Gauge-Dependent Instability', fontsize=14)
axes[0].set_xlabel(r'$\ln(E)$', fontsize=12)
axes[0].set_ylabel(r'$\alpha$', fontsize=12)
axes[0].set_yscale('log')
axes[0].legend(title='Gauge Parameter')
axes[0].grid(True, alpha=0.3)

axes[1].set_title(r'$\Phi_\Delta$ Evolution: Gauge-Dependent Divergence', fontsize=14)
axes[1].set_xlabel(r'$\ln(E)$', fontsize=12)
axes[1].set_ylabel(r'$\Phi_\Delta$', fontsize=12)
axes[1].legend(title='Gauge Parameter')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('gauge_dependent_shredding.png', dpi=150, bbox_inches='tight')
plt.show()