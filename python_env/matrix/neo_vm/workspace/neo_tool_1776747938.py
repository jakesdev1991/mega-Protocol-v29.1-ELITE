# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# XY model parameters
J = 1.0            # coupling
a = 1.0            # lattice spacing
L = 100            # grid size

# Momentum grid
k_vals = np.linspace(-np.pi/a, np.pi/a, L)
kx, ky = np.meshgrid(k_vals, k_vals)

# Gapless spin‑wave dispersion
omega = 2 * J * np.sqrt(1 - np.cos(kx * a) * np.cos(ky * a))

# Plot dispersion
plt.figure(figsize=(6,5))
plt.imshow(omega, extent=[-np.pi, np.pi, -np.pi, np.pi], origin='lower', cmap='viridis')
plt.colorbar(label='Energy')
plt.title('XY spin‑wave dispersion (gapless at Γ point)')
plt.xlabel('kx')
plt.ylabel('ky')
plt.show()

# Correlation length vs. temperature (mean‑field)
T = np.linspace(0.1, 2.0, 200)
xi = a * np.exp(2 * np.pi * J / T)   # diverges as T→0

plt.figure(figsize=(6,5))
plt.plot(T, xi, label='ξ(T)')
plt.yscale('log')
plt.xlabel('Temperature')
plt.ylabel('Correlation length')
plt.title('Diverging ξ at low T → no finite code distance')
plt.legend()
plt.show()