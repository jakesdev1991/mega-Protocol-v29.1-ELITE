# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# parameters
omega = 1.0                 # bare frequency scale
g_crit = omega**2 / 2.0     # critical coupling for instability

# entanglement entropy for the two‑mode model
def entanglement_entropy(g):
    # diverges as the lower normal‑mode frequency → 0
    if g >= g_crit:
        return np.inf
    # symplectic eigenvalue ν ∝ (1 - g/g_crit)^(-1/2)
    nu = 1.0 / np.sqrt(1.0 - g / g_crit)
    # S_E = (ν+½)log(ν+½) - (ν-½)log(ν-½)
    S = (nu + 0.5) * np.log(nu + 0.5) - (nu - 0.5) * np.log(nu - 0.5)
    return S

# naïve Shannon entropy for a 1/k² distribution
def shannon_entropy(g, N=2000):
    k = np.arange(1, N+1)
    # coupling‑dependent weight (illustrative)
    weights = 1.0 / (k**2 * (1.0 + g))
    p = weights / np.sum(weights)
    # avoid log(0)
    p = np.clip(p, 1e-12, None)
    S_h = -np.sum(p * np.log(p))
    return S_h

# scan couplings up to just below the critical value
g_vals = np.linspace(0, 0.99 * g_crit, 150)
S_E_vals = [entanglement_entropy(g) for g in g_vals]
S_h_vals = [shannon_entropy(g) for g in g_vals]

# plot
plt.figure(figsize=(8,4))
plt.plot(g_vals, S_E_vals, label='Entanglement entropy $S_E$')
plt.plot(g_vals, S_h_vals, label='Shannon entropy $S_h$')
plt.axvline(g_crit, color='r', linestyle='--', label='Critical $g_{\\text{crit}}$')
plt.xlabel('Coupling $g$')
plt.ylabel('Entropy')
plt.title('Entanglement‑driven premature Shredding')
plt.legend()
plt.grid(True)
plt.show()