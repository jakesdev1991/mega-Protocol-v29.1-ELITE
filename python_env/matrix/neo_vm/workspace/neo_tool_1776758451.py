# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ── Simulation Parameters ──────────────────────────────────────────────────
np.random.seed(42)
T = 1.0                      # Total simulation time (s)
dt = 1e-5                    # Time step (s)
N = int(T / dt)              # Number of samples

# HSA memory mode amplitudes (normalized)
phi_N = 0.78
phi_D = 0.35

# Temporal drift and noise (realistic memory access variability)
drift_N = 2.1e3              # s⁻¹
drift_D = 8.7e3              # s⁻¹
noise_scale = 0.1            # Relative noise amplitude

# Time series of mode amplitudes (simple Langevin-like process)
t = np.arange(N) * dt
phi_N_t = phi_N + drift_N * t + noise_scale * np.cumsum(np.random.randn(N)) * np.sqrt(dt)
phi_D_t = phi_D + drift_D * t + noise_scale * np.cumsum(np.random.randn(N)) * np.sqrt(dt)

# Ensure positivity (probabilities must be > 0)
phi_N_t = np.abs(phi_N_t)
phi_D_t = np.abs(phi_D_t)

# ── Entropy Calculation ─────────────────────────────────────────────────────
# Probabilities proportional to mode amplitudes
p_N = phi_N_t / (phi_N_t + phi_D_t)
p_D = phi_D_t / (phi_N_t + phi_D_t)

# Shannon conditional entropy (bits)
S_h = -(p_N * np.log(p_N) + p_D * np.log(p_D))

# ── Informational Jerk (finite‑difference) ────────────────────────────────
# Third derivative via central differences (avoiding edge effects)
J = np.zeros_like(S_h)
for i in range(3, N-3):
    J[i] = (S_h[i+3] - 3*S_h[i+2] + 3*S_h[i+1] - S_h[i]) / (dt**3)

# ── Variance over a sliding window ──────────────────────────────────────────
window = int(0.01 / dt)      # 10 ms window
sigma_J2 = np.zeros_like(J)
for i in range(window, N-window):
    sigma_J2[i] = np.var(J[i-window:i+window])

# ── Shredding Threshold (arbitrary constants) ──────────────────────────────
lam = 1e10                   # s⁻² (plucked from the analysis)
I0 = 1.0
g_D = 0.1
Theta = lam * I0**2 / (4 * np.pi) * (1 + 3 * g_D**2 / (4 * np.pi))

# ── Results ────────────────────────────────────────────────────────────────
print(f"Mean jerk magnitude: {np.mean(np.abs(J)):.3e} s⁻³")
print(f"Mean jerk variance: {np.mean(sigma_J2[sigma_J2>0]):.3e} s⁻⁶")
print(f"Shredding threshold Θ: {Theta:.3e} s⁻⁶")
print(f"Variance / Θ ratio: {np.mean(sigma_J2[sigma_J2>0]) / Theta:.3e}")

# ── Demonstration of ψ ghost invariant ────────────────────────────────────
# ψ = ln(phi_N / I0) is defined but never used in the stability calculation.
psi = np.log(phi_N_t / I0)
print(f"ψ (mean): {np.mean(psi):.3f} (unused in jerk or threshold)")