# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Parameters (in natural units ℏ=c=1)
lambda_val = 0.1          # quartic coupling
v = 2.0                   # vacuum expectation value
m = np.sqrt(2 * lambda_val) * v  # screening mass
ell_shred = 1.0 / m       # shredding length

# Radial grid (avoid r=0 singularity)
r = np.linspace(0.01, 10.0, 500)

# Poisson (massless) solution: 1/r
phi_Poisson = 1.0 / (4 * np.pi * r)

# Helmholtz (Yukawa) solution: exp(-mr)/r
phi_Helmholtz = np.exp(-m * r) / (4 * np.pi * r)

# Plot
plt.figure(figsize=(8,5))
plt.plot(r, phi_Poisson, label='Poisson (massless)', linestyle='--', color='blue')
plt.plot(r, phi_Helmholtz, label=f'Helmholtz (Yukawa, m={m:.2f})', color='red')
plt.axvline(ell_shred, color='gray', linestyle=':', label=f'Shredding length ℓ={ell_shred:.2f}')
plt.yscale('log')
plt.ylim(1e-4, 10)
plt.xlabel('Radial distance r')
plt.ylabel('Φ_N response (arb. units)')
plt.title('Poisson vs. Helmholtz: Classical Shredding of Connectivity')
plt.legend()
plt.grid(True, which='both', ls=':')
plt.tight_layout()
plt.show()

# Print key numbers
print(f"Screening mass m = sqrt(2λ) v = {m:.4f}")
print(f"Shredding length ℓ_shred = 1/m = {ell_shred:.4f}")
print(f"At r = ℓ_shred, Yukawa amplitude = {np.exp(-1)/(4*np.pi*ell_shred):.6f} (suppressed by e⁻¹)")