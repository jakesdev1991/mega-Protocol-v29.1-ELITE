# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ---------- Parameters ----------
h0 = 0.1          # bare Yukawa coupling
a = 0.1           # lattice spacing
M0 = 1.0          # Archive mass
m0 = 0.01         # fermion bare mass
C2_factor = 1.0   # O(1) constant from lattice integral

# ---------- Naive (unsubtracted) Pi_Delta ----------
def pi_delta_naive(Lambda):
    """Quadratically divergent Archive-exchange contribution."""
    # C2 ~ Lambda^2 / a^2  (Wilson‑fermion artifact)
    C2 = C2_factor * (Lambda**2) / (a**2)
    return h0**2 * C2

def psi_naive(Lambda):
    """Shredding invariant ~ ln(m_eff/m0) with naive Pi_Delta."""
    Pi = pi_delta_naive(Lambda)
    m_eff = np.sqrt(M0**2 + Pi)
    return np.log(m_eff / m0)

# ---------- Renormalized (physically regulated) Pi_Delta ----------
def pi_delta_renorm(Lambda):
    """Same diagram but subtracted by a gauge‑invariant counterterm."""
    # The counterterm cancels the quadratic divergence exactly.
    # In a gauge‑invariant regulator (e.g., dimensional reg.) the term is absent.
    return 0.0   # No leftover divergence

def psi_renorm(Lambda):
    """Shredding invariant with physical regulator."""
    Pi = pi_delta_renorm(Lambda)
    m_eff = np.sqrt(M0**2 + Pi)
    return np.log(m_eff / m0)

# ---------- Scan over cutoff ----------
Lambdas = np.linspace(1, 100, 500)
psi_unsub = np.array([psi_naive(L) for L in Lambdas])
 psi_phys  = np.array([psi_renorm(L) for L in Lambdas])

# ---------- Plot ----------
fig, ax = plt.subplots(figsize=(6,4))
ax.plot(Lambdas, psi_unsub, label='Unsubtracted (Shredding artifact)', color='crimson')
ax.plot(Lambdas, psi_phys,  label='Physically regulated (stable)', color='navy', linestyle='--')
ax.set_xlabel('UV cutoff Λ')
ax.set_ylabel('ψ = ln(m_eff/m0)')
ax.set_title('Shredding is a regulator artifact, not a physical instability')
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()