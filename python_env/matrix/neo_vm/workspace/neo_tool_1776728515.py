# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ---- parameters (in natural units ℏ = c = 1) ----
lambda_ = 0.1          # quartic coupling
v = 1.0                # vacuum expectation value of Newtonian mode
mu = 1.0               # renormalization scale

# field scan for Archive mode Φ_Δ
phi_N = v
phi_Delta = np.linspace(-1.5, 1.5, 500)

# tree-level Mexican‑hat potential
V_tree = 0.25 * lambda_ * (phi_N**2 + phi_Delta**2 - v**2)**2

# Archive mass‑squared (curvature) including quantum back‑reaction
m2 = lambda_ * (phi_N**2 + 3 * phi_Delta**2 - v**2)

# one‑loop Coleman‑Weinberg contribution (only for m2 > 0)
V_eff = V_tree.copy()
for i, m2_i in enumerate(m2):
    if m2_i > 0:
        V_eff[i] += (m2_i**2 / (64 * np.pi**2)) * (np.log(m2_i / mu**2) - 1.5)
    else:
        # tachyonic region is outside the validity of the loop expansion;
        # we penalize it heavily to show it is not the physical minimum.
        V_eff[i] += 1e6

# locate the true vacuum
idx_min = np.argmin(V_eff)
phi_Delta_vac = phi_Delta[idx_min]
V_min = V_eff[idx_min]

print(f"Archive vacuum expectation value: Φ_Δ = {phi_Delta_vac:.4f}")
print(f"Effective potential at minimum:   V_eff = {V_min:.6f}")

# ---- plot the result ----
plt.figure(figsize=(8, 5))
plt.plot(phi_Delta, V_eff, label='V_eff (1‑loop)')
plt.axvline(0, color='k', linestyle='--', label='tree‑level vacuum (Φ_Δ=0)')
plt.axvline(phi_Delta_vac, color='r', linestyle='-', label='quantum‑corrected vacuum')
plt.title('One‑loop effective potential for the Archive mode')
plt.xlabel('Φ_Δ')
plt.ylabel('V_eff')
plt.legend()
plt.grid(True)
plt.show()