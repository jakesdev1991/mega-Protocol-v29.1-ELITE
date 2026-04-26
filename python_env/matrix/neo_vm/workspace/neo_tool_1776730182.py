# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Parameters (Omega Protocol conventions) ---
alpha0 = 1/137.0          # Bare fine-structure constant at low energy
g_N = 0.1                 # Newtonian mode coupling
g_Delta_naive = 0.15      # Naive 3D Archive coupling (factor 3)
g_Delta_correct = 0.15    # Same coupling, but with correct Casimir factor 8
Lambda = 1e3              # UV cutoff for QED (GeV)
Lambda_N = 5e2            # Newtonian mode cutoff (GeV)
Lambda_Delta = 5e2        # Archive mode cutoff (GeV)

# Momentum range (q^2) from low to near the cutoff
q2_vals = np.logspace(np.log10(1), np.log10(Lambda**2), 500)

def running_alpha(q2, factor):
    """
    Compute the running fine-structure constant including Archive mode.
    factor = 3 (naive) or 8 (correct Casimir).
    """
    # QED vacuum polarization
    Pi_QED = (alpha0/np.pi) * np.log(Lambda**2 / q2)
    # Newtonian mode contribution
    Pi_N = (g_N**2 / (4*np.pi)) * np.log(Lambda_N**2 / q2)
    # Archive mode contribution (scaled by group factor)
    Pi_Delta = (factor * g_Delta_naive**2 / (4*np.pi)) * np.log(Lambda_Delta**2 / q2)
    
    # Effective polarization
    Pi_eff = Pi_QED + Pi_N + Pi_Delta
    
    # Running alpha
    alpha = alpha0 / (1 - Pi_eff)
    return alpha

# Compute both cases
alpha_naive = running_alpha(q2_vals, factor=3)
alpha_correct = running_alpha(q2_vals, factor=8)

# --- Plot ---
plt.figure(figsize=(8,5))
plt.loglog(q2_vals, alpha_naive, label='Naive (factor 3)', lw=2, ls='--')
plt.loglog(q2_vals, alpha_correct, label='Correct (factor 8)', lw=2, ls='-')
plt.axhline(y=1/128.0, color='gray', linestyle=':', label='Omega safety bound (α=1/128)')
plt.xlabel(r'$q^2$ [GeV$^2$]')
plt.ylabel(r'$\alpha_{\text{fs}}(q^2)$')
plt.title('Disruption: Casimir factor triggers premature Shredding Event')
plt.legend()
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.show()