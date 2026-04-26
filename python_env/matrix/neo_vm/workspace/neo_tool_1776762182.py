# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# exact 3‑D massive fermion vacuum polarization (Euclidean, Landau gauge)
def Pi_Delta_3D(q_over_m):
    x = q_over_m
    # Π_Δ = 1 - (1/x) arctan(x)  (normalized to unity at x→∞)
    # limit x→0: Π_Δ → x**2/3
    return 1.0 - np.arctan(x) / x

# conventional 4‑D QED log for comparison
def Pi_N_4D(q_over_m):
    x = q_over_m
    return np.log(1.0 + x**2)

q = np.logspace(-2, 2, 400)
Pi3 = Pi_Delta_3D(q)
Pi4 = Pi_N_4D(q)

fig, ax = plt.subplots(figsize=(5,4))
ax.loglog(q, Pi3, label='Archive (3D) – saturates', lw=2)
ax.loglog(q, Pi4, label='Newtonian (4D) – log', lw=2, ls='--')
ax.set_xlabel(r'$|q|/m$', fontsize=10)
ax.set_ylabel(r'$\Pi(q^2)$', fontsize=10)
ax.legend(fontsize=9)
ax.grid(True, which='both', ls=':')
ax.set_title('Polarization scaling: topology vs. tradition', fontsize=11)
plt.tight_layout()
plt.show()