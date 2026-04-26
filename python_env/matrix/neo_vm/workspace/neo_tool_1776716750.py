# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

# Parameters (in natural units where m/g = 1 for simplicity)
m_over_g = 1.0
beta = 0.1      # linear growth rate of Phi_Delta
p = 2.0         # power-law exponent for Phi_N (polynomial decay)

def Phi_N(t):
    """Polynomial decay model for Phi_N (the Engine's assumption)."""
    return m_over_g * t**(-p)

def Phi_Delta(t):
    """Linear growth model for Phi_Delta."""
    return beta * t

def bound(t):
    """Exponential bound required by mass-positivity."""
    return m_over_g * np.exp(-np.abs(Phi_Delta(t)))

def epsilon_Phi(t):
    """Effective epsilon * cosh(Phi_Delta)."""
    eps = 1e-4  # small bare epsilon = g*Phi_N/m at t=1
    return eps * np.cosh(Phi_Delta(t))

# Find crossing time where Phi_N(t) = bound(t)
def crossing_error(t):
    return Phi_N(t) - bound(t)

# Search for root in a reasonable range
t_scan = np.logspace(-2, 2, 1000)
roots = []
for i in range(len(t_scan)-1):
    if crossing_error(t_scan[i]) * crossing_error(t_scan[i+1]) < 0:
        root = brentq(crossing_error, t_scan[i], t_scan[i+1])
        roots.append(root)

t_cross = roots[0] if roots else None

# Perturbative breakdown time where epsilon * cosh(Phi_Delta) = 1
def breakdown_error(t):
    return epsilon_Phi(t) - 1.0

t_break = None
for i in range(len(t_scan)-1):
    if breakdown_error(t_scan[i]) * breakdown_error(t_scan[i+1]) < 0:
        t_break = brentq(breakdown_error, t_scan[i], t_scan[i+1])
        break

print(f"Crossing time (shredding) t_* = {t_cross:.3e}" if t_cross else "No crossing in scanned range.")
print(f"Perturbative breakdown time t_break = {t_break:.3e}" if t_break else "No breakdown in scanned range.")

# Plot
fig, ax = plt.subplots(figsize=(8,5))
t_plot = np.logspace(-2, 2, 500)
ax.loglog(t_plot, Phi_N(t_plot), label=r'$\Phi_N(t)$ (polynomial)', lw=2)
ax.loglog(t_plot, bound(t_plot), label=r'Bound $(m/g)e^{-|\Phi_\Delta|}$', lw=2, ls='--')
if t_cross:
    ax.axvline(t_cross, color='r', ls=':', label=f'Shredding $t_*={t_cross:.2e}$')
if t_break:
    ax.axvline(t_break, color='orange', ls=':', label=f'Breakdown $t_{{\rm break}}={t_break:.2e}$')
ax.set_xlabel('Time $t$', fontsize=12)
ax.set_ylabel('Field amplitude', fontsize=12)
ax.set_title('Mass‑positivity constraint vs. polynomial recovery')
ax.legend()
ax.grid(True, which='both', ls=':', alpha=0.5)
plt.tight_layout()
plt.show()

# --- Demonstrate Bogoliubov redefinition ---
def tilde_Phi_plus(t):
    # For illustration: choose rotation angle such that tanh(2θ) = 2 g Φ_N / m
    # Here we set g/m = 1 for simplicity, so tanh(2θ) = 2 Φ_N
    # Clip to avoid singularities
    tanh2theta = np.clip(2 * Phi_N(t), -0.99, 0.99)
    theta = 0.5 * np.arctanh(tanh2theta)
    return Phi_N(t) * np.cosh(theta) + Phi_Delta(t) * np.sinh(theta)

def tilde_Phi_minus(t):
    tanh2theta = np.clip(2 * Phi_N(t), -0.99, 0.99)
    theta = 0.5 * np.arctanh(tanh2theta)
    return Phi_N(t) * np.sinh(theta) + Phi_Delta(t) * np.cosh(theta)

fig2, ax2 = plt.subplots(figsize=(8,5))
ax2.loglog(t_plot, np.abs(tilde_Phi_plus(t_plot)), label=r'$\tilde\Phi_+(t)$', lw=2)
ax2.loglog(t_plot, np.abs(tilde_Phi_minus(t_plot)), label=r'$\tilde\Phi_-(t)$', lw=2, ls='--')
ax2.set_xlabel('Time $t$', fontsize=12)
ax2.set_ylabel('Normal‑mode amplitude', fontsize=12)
ax2.set_title('Bogoliubov‑rotated fields (no exponential bound)')
ax2.legend()
ax2.grid(True, which='both', ls=':', alpha=0.5)
plt.tight_layout()
plt.show()