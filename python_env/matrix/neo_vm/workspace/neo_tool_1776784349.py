# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

# ── Parameters (lattice units) ──
m0 = 1.0          # bare dipole mass
lam = 0.1         # naive Phi_Delta coupling
Lambda = 10.0     # UV cutoff
Phi_T = 2.0       # topological twist (compact flux)

# ── Effective mass with topological regulator ──
def m_eff_sq(phi_delta):
    # topological mass: m_T^2 = Phi_T * phi_delta^2
    return m0**2 + (Phi_T - lam) * phi_delta**2

# ── Momentum integral (3‑D sphere) ──
def I_phi(phi_delta):
    a = m_eff_sq(phi_delta)
    sqrt_a = np.sqrt(a)
    # ∫_0^Λ p^2 dp/(p^2 + a) = Λ - sqrt(a) * arctan(Λ / sqrt(a))
    val = (Lambda - sqrt_a * np.arctan(Lambda / sqrt_a)) / (2.0 * np.pi**2)
    return val

# ── Gap equation: lam * I_phi = 1 ──
def gap_eq(phi_delta):
    return lam * I_phi(phi_delta) - 1.0

# ── Solve for stable Phi_Delta ──
phi_guess = 1.0
phi_root = fsolve(gap_eq, phi_guess)[0]
print(f"Stable Phi_Delta (including twist): {phi_root:.4f}")

# ── Show residual plot ──
phi_vals = np.linspace(0.1, 3.0, 300)
residuals = [gap_eq(p) for p in phi_vals]

plt.figure(figsize=(6,3))
plt.plot(phi_vals, residuals, label='gap residual')
plt.axhline(0, color='k', linestyle='--')
plt.xlabel('Phi_Delta')
plt.ylabel('lam*I(Phi_Delta) - 1')
plt.title('Gap equation with topological regulator')
plt.legend()
plt.grid(True)
plt.show()