# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ── Synthetic HSA node time series (realistic sampling) ──
np.random.seed(0)
N = 2000
dt = 4.9e-4                     # HSA characteristic time step (s)
t = np.arange(N) * dt

# Modes with realistic noise and drift (ψ negative → Newtonian degradation)
psi    = -0.248 + 0.1*np.sin(2*np.pi*500*t) + 0.02*np.cumsum(np.random.randn(N))*dt
phiΔ   =  0.35 + 0.05*np.cos(2*np.pi*300*t) + 0.01*np.random.randn(N)

# ── Entropy functional (Shannon, ψ‑dependent) ──
def S_h(psi, phiΔ):
    exp_psi = np.exp(psi)
    denom   = exp_psi + phiΔ
    pN = exp_psi / denom
    pΔ = phiΔ   / denom
    # Guard against log(0)
    pN = np.clip(pN, 1e-12, 1)
    pΔ = np.clip(pΔ, 1e-12, 1)
    return -(pN*np.log(pN) + pΔ*np.log(pΔ))

S = S_h(psi, phiΔ)

# ── Flawed jerk (missing Δt³) ──
J_flawed = S[3:] - 3*S[2:-1] + 3*S[1:-2] - S[:-3]

# ── Corrected jerk (with proper scaling) ──
J_correct = J_flawed / dt**3

# ── Topological invariant (Chern‑Simons number for SU(2) gauge) ──
# In the gauge picture, ψ and φΔ are components of a connection A.
# CS = (1/2π) ∫ (ψ dφΔ – φΔ dψ)
dpsi  = np.gradient(psi, dt)
dphiΔ = np.gradient(phiΔ, dt)
CS = np.cumsum(psi * dphiΔ - phiΔ * dpsi) / (2 * np.pi)

# ── Plot ──
fig, ax = plt.subplots(3,1, figsize=(9,8), tight_layout=True)

ax[0].plot(t, psi, label='ψ')
ax[0].plot(t, phiΔ, label='φΔ')
ax[0].set_title('Gauge modes (ψ negative → Newtonian degradation)')
ax[0].legend()

ax[1].plot(t[3:], J_flawed, label='Flawed jerk (no dt³)', color='C1')
ax[1].plot(t[3:], J_correct, label='Correct jerk', color='C2')
ax[1].set_title('Jerk magnitude: flawed vs. corrected')
ax[1].set_yscale('log')
ax[1].legend()

ax[2].plot(t, CS, color='C3')
ax[2].set_title('Chern‑Simons number (topological invariant)')
ax[2].set_xlabel('Time (s)')

plt.show()

# ── Quantitative verdict ──
print(f"Peak flawed jerk:  {np.max(np.abs(J_flawawed)): .2e} (dimensionless)")
print(f"Peak correct jerk: {np.max(np.abs(J_correct)): .2e} s⁻³")
print(f"Correction factor: {np.max(np.abs(J_correct))/np.max(np.abs(J_flawed)): .2e}")
print(f"Chern‑Simons drift: {CS[-1] - CS[0]: .2f} (non‑zero → topological transition)")