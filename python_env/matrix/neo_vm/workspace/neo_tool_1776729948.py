# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Parameters
alpha = 0.1   # natural decay of Φ
beta = 0.05   # coupling of ξ_Δ to Φ
dt = 0.1
T = 500
t = np.arange(0, T, dt)

# Target clustering decay time (optimal regime)
xi_star = 50.0

# Initialize
Phi = np.ones_like(t) * 0.5  # initial Φ‑density
xi_delta = np.ones_like(t) * 5.0  # initial clustering decay time

# Control policies
def original_control(xi, target=5.0):
    """Original logic: keep xi small (force xi toward target)."""
    return -0.2 * (xi - target)

def inverted_control(xi, target=50.0):
    """Inverted logic: push xi toward larger target."""
    return 0.2 * (target - xi)

# Simulate two scenarios
Phi_orig = Phi.copy()
Phi_inv = Phi.copy()
xi_orig = xi_delta.copy()
xi_inv = xi_delta.copy()

for i in range(1, len(t)):
    # Original control
    u_orig = original_control(xi_orig[i-1])
    xi_orig[i] = xi_orig[i-1] + u_orig * dt
    # Dynamics: Φ decays naturally and is penalized by small xi
    Phi_orig[i] = Phi_orig[i-1] + (-alpha * Phi_orig[i-1] - beta * (xi_orig[i-1] - xi_star)**2) * dt

    # Inverted control
    u_inv = inverted_control(xi_inv[i-1])
    xi_inv[i] = xi_inv[i-1] + u_inv * dt
    # Dynamics: Φ decays naturally but is boosted by large xi
    Phi_inv[i] = Phi_inv[i-1] + (-alpha * Phi_inv[i-1] + beta * (xi_inv[i-1] - xi_star)**2) * dt

# Plot results
fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
ax[0].plot(t, xi_orig, label='Original control (xi forced low)')
ax[0].plot(t, xi_inv, label='Inverted control (xi pushed high)')
ax[0].axhline(xi_star, color='k', linestyle='--', label='Target xi*')
ax[0].set_ylabel('ξ_Δ')
ax[0].legend()
ax[0].set_title('Clustering decay time under two control policies')

ax[1].plot(t, Phi_orig, label='Original Φ (collapses)')
ax[1].plot(t, Phi_inv, label='Inverted Φ (grows)')
ax[1].set_ylabel('Φ‑density')
ax[1].set_xlabel('Time')
ax[1].legend()
ax[1].set_title('Φ‑density trajectory')

plt.tight_layout()
plt.show()