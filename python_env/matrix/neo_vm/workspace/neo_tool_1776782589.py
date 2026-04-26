# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Neo‑Anomaly Disruption Script
----------------------------
Demonstrates that the heuristic informational‑jerk is a mirage and
introduces the fractional‑jerk + Lyapunov‑tensor stability metric.
"""

import numpy as np
from scipy.special import gamma
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

# ─────────────────────────────────────────────────────────────────────────────
# 1.  Synthetic HSA‑node fields (noisy sinusoids)
# ─────────────────────────────────────────────────────────────────────────────
t_max = 1e-3          # 1 ms of operation
fs = 1e7              # 10 MHz sampling
t = np.arange(0, t_max, 1/fs)

# base values
phi_N0 = 0.78
phi_D0 = 0.35

# add modest periodic modulation + AWGN
np.random.seed(0)
phi_N = phi_N0 + 0.1*np.sin(2*np.pi*2.5e3*t) + 1e-3*np.random.randn(len(t))
phi_D = phi_D0 + 0.05*np.sin(2*np.pi*8.7e3*t + 0.3) + 5e-4*np.random.randn(len(t))

# ─────────────────────────────────────────────────────────────────────────────
# 2.  Probabilities & entropies
# ─────────────────────────────────────────────────────────────────────────────
eps = 1e-12
phi_N_sq = phi_N**2
phi_D_sq = phi_D**2
den = phi_N_sq + phi_D_sq + eps

p_N = phi_N_sq / den
p_D = phi_D_sq / den

# Shannon entropy
S_h = -(p_N*np.log(p_N+eps) + p_D*np.log(p_D+eps))

# Rényi‑2 (collision) entropy
S2 = -np.log(p_N**2 + p_D**2 + eps)

# ─────────────────────────────────────────────────────────────────────────────
# 3.  Heuristic scalar jerk (the “repaired” formula)
# ─────────────────────────────────────────────────────────────────────────────
# constants
xi_inv_sq = 4.2e6          # ξ⁻² (s⁻²)
xi_inv_4 = xi_inv_sq**2     # ξ⁻⁴ (s⁻⁴)
J_source = 1.5e12           # s⁻³

# time‑derivatives of the fields (central diff)
def central_diff(y, dt):
    # returns same‑length array; boundaries are linear
    d = np.empty_like(y)
    d[1:-1] = (y[2:] - y[:-2]) / (2*dt)
    d[0] = (y[1] - y[0]) / dt
    d[-1] = (y[-1] - y[-2]) / dt
    return d

dot_phi_N = central_diff(phi_N, 1/fs)
dot_phi_D = central_diff(phi_D, 1/fs)

# heuristic jerk
J_heur = (3*phi_D * dot_phi_D**3) * xi_inv_4 - (phi_N * dot_phi_N**3) * xi_inv_4 + J_source

# ─────────────────────────────────────────────────────────────────────────────
# 4.  Rigorous third‑derivative of Shannon entropy (numerical)
# ─────────────────────────────────────────────────────────────────────────────
def third_derivative(y, dt):
    # 5‑point stencil
    d3 = np.empty_like(y, dtype=float)
    h = dt
    # interior
    d3[2:-2] = (y[4:] - 2*y[3:-1] + 2*y[1:-3] - y[:-4]) / (2*h**3)
    # boundaries – fallback to lower‑order
    d3[0] = d3[1] = d3[2]
    d3[-1] = d3[-2] = d3[-3]
    return d3

J_rigorous = third_derivative(S_h, 1/fs)

# ─────────────────────────────────────────────────────────────────────────────
# 5.  Fractional (Caputo) derivative of Rényi‑2 entropy, order α = 2.5
# ─────────────────────────────────────────────────────────────────────────────
def caputo_fractional(y, dt, alpha, window=50):
    """
    Grünwald‑Letnikov approximation of the Caputo derivative.
    We assume zero initial conditions for simplicity.
    """
    # binomial coefficients (α choose k)
    k = np.arange(window+1)
    binom = gamma(alpha+1) / (gamma(k+1) * gamma(alpha - k + 1))
    # alternating signs
    coeffs = (-1)**k * binom
    # convolution (causal, so we flip the kernel)
    frac = np.zeros_like(y)
    for i in range(window, len(y)):
        frac[i] = (1 / dt**alpha) * np.sum(coeffs * y[i-window:i+1][::-1])
    # scale by Gamma(2-α) for Caputo (we already accounted for α in coeffs)
    return frac / gamma(2 - alpha)

J_frac = caputo_fractional(S2, 1/fs, alpha=2.5, window=30)

# ─────────────────────────────────────────────────────────────────────────────
# 6.  Probability‑flow Jacobian & largest Lyapunov eigenvalue
# ─────────────────────────────────────────────────────────────────────────────
# dp_N/dt = (2 φ_N φ̇_N φ_Δ² - 2 φ_N² φ_Δ φ̇_Δ) / (φ_N² + φ_Δ²)²
dp_N_dt = (2*phi_N*dot_phi_N*phi_D_sq - 2*phi_N_sq*phi_D*dot_phi_D) / (den**2)

# The “Jacobian” for the 1‑D flow is simply d(dp_N/dt)/dp_N.
# Since p_N = φ_N²/(φ_N²+φ_Δ²), we can compute d(dp_N/dt)/dp_N numerically:
dp_N = p_N[1:] - p_N[:-1]
dp_N_dt_mid = 0.5*(dp_N_dt[1:] + dp_N_dt[:-1])
jac = np.empty_like(p_N)
jac[0] = 0.0
jac[1:-1] = dp_N_dt_mid / (dp_N + eps)   # approximate derivative
jac[-1] = jac[-2]

# largest eigenvalue (real part) – for 1‑D system this is just the Jacobian
lambda_max = jac

# ─────────────────────────────────────────────────────────────────────────────
# 7.  Composite stability metric Ξ(t) = λ_max * |J_frac|^{1/α}
# ─────────────────────────────────────────────────────────────────────────────
alpha = 2.5
Xi = lambda_max * np.abs(J_frac)**(1.0/alpha)

# ─────────────────────────────────────────────────────────────────────────────
# 8.  Print a snapshot at t ≈ 0.5 ms
# ─────────────────────────────────────────────────────────────────────────────
idx = np.argmin(np.abs(t - 0.5e-3))

print(f"{'─'*60}")
print(f"Snapshot @ t = {t[idx]*1e6:.1f} µs")
print(f"{'─'*60}")
print(f"Heuristic scalar jerk          : {J_heur[idx]:.3e} s⁻³")
print(f"Rigorous 3rd‑der. of S_h       : {J_rigorous[idx]:.3e} s⁻³")
print(f"Fractional (α=2.5) jerk (Rényi): {J_frac[idx]:.3e} s⁻ᵅ")
print(f"Largest Lyapunov eigenvalue    : {lambda_max[idx]:.3e} s⁻¹")
print(f"Composite metric Ξ             : {Xi[idx]:.3e} (dimensionless)")
print(f"{'─'*60}")

# ─────────────────────────────────────────────────────────────────────────────
# 9.  (Optional) Plot the time series to visualise the divergence
# ─────────────────────────────────────────────────────────────────────────────
# Uncomment the block below if you have matplotlib installed
"""
import matplotlib.pyplot as plt
fig, ax = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
ax[0].plot(t*1e6, J_heur, label='Heuristic jerk')
ax[0].plot(t*1e6, J_rigorous, label='Rigorous 3rd‑der S_h')
ax[0].set_ylabel('J (s⁻³)')
ax[0].legend()
ax[0].set_title('Scalar jerk comparisons')

ax[1].plot(t*1e6, J_frac, label='Fractional (α=2.5) jerk')
ax[1].set_ylabel('J_frac (s⁻ᵅ)')
ax[1].legend()

ax[2].plot(t*1e6, Xi, label='Composite Ξ')
ax[2].set_ylabel('Ξ (dimensionless)')
ax[2].set_xlabel('Time (µs)')
ax[2].legend()
plt.tight_layout()
plt.show()
"""