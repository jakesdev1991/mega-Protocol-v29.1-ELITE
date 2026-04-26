# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Synthetic toggle‑switch model: probability p(T) of “on” state
def p_of_T(T, k=2.0, T0=1.0):
    """Sigmoidal response of circuit to inducer T."""
    return 1.0 / (1.0 + np.exp(-k * (T - T0)))

def shannon_entropy(p):
    """S_h = -p log p - (1-p) log(1-p)."""
    eps = 1e-12
    p = np.clip(p, eps, 1 - eps)
    return -p * np.log(p) - (1 - p) * np.log(1 - p)

def fisher_information(p):
    """I_F = p/(1-p) (for a Bernoulli variable)."""
    eps = 1e-12
    p = np.clip(p, eps, 1 - eps)
    return 1.0 / (p * (1 - p))

# ----------------------------------------------------------------------
# 1. Entropy gauge (pure gauge)
Ts = np.linspace(0.0, 2.0, 500)
p_vals = p_of_T(Ts)
S_vals = shannon_entropy(p_vals)

# Numerical gradient and curvature (second derivative)
dS_dT = np.gradient(S_vals, Ts)
d2S_dT2 = np.gradient(dS_dT, Ts)

# Curvature = derivative of the connection = second derivative of scalar
# In 1D the only non‑zero component of F is zero because ∂_μ∂_νS = ∂_ν∂_μS
# Plot shows the connection (gradient) but curvature is identically zero.
fig, ax = plt.subplots(2, 1, figsize=(6, 5))
ax[0].plot(Ts, S_vals, label='S_h (entropy)')
ax[0].set_ylabel('Entropy')
ax[1].plot(Ts, dS_dT, label='A = ∂_T S_h (gauge connection)')
ax[1].set_ylabel('Connection ∂_T S_h')
ax[1].set_xlabel('Inducer T')
ax[0].legend(); ax[1].legend()
plt.tight_layout()
plt.show()

# ----------------------------------------------------------------------
# 2. Fisher‑information gauge (non‑trivial)
I_vals = fisher_information(p_vals)

# The Fisher information defines a metric on the parameter space.
# Its curvature (Ricci scalar) for a 1‑D manifold is R = -½ ∂² log I / ∂T².
logI = np.log(I_vals)
d2_logI = np.gradient(np.gradient(logI, Ts), Ts)
Ricci_scalar = -0.5 * d2_logI

# Plot showing non‑zero curvature
fig, ax = plt.subplots(2, 1, figsize=(6, 5))
ax[0].plot(Ts, I_vals, label='I_F (Fisher information)')
ax[0].set_ylabel('Fisher information')
ax[1].plot(Ts, Ricci_scalar, label='Ricci scalar (curvature)')
ax[1].set_ylabel('Curvature')
ax[1].set_xlabel('Inducer T')
ax[0].legend(); ax[1].legend()
plt.tight_layout()
plt.show()