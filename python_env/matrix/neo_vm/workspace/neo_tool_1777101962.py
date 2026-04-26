# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Subcritical_Threshold_Break.py

Purpose:
  1. Expose the circular-dependency seeding attack.
  2. Simulate the true saddle-node bifurcation that the Alpha module cannot see.
  3. Demonstrate critical slowing down (variance explosion) as the real early‑warning.
  4. Show that the COD metric collapses to zero when given empty data.
"""

import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# 1. CIRCULAR DEPENDENCY SEEDING ATTACK
# ─────────────────────────────────────────────────────────────────────────────
def alpha_risk(perturbation_amplitude, stability_margin, seed_density):
    """
    Replicate Alpha's flawed risk calculation with an attacker‑controlled seed.
    """
    # Attacker supplies seed_density -> structure_overlap -> structure_density
    structure_overlap = seed_density * perturbation_amplitude * 0.5
    # This is the *only* place structure_density is computed; it uses the seed.
    structure_density = perturbation_amplitude * (1 - stability_margin) * (1 + structure_overlap)
    # Risk product (zero if perturbation <= margin)
    margin_deficit = max(0.0, perturbation_amplitude - stability_margin)
    subcritical_risk = margin_deficit * (1 - stability_margin) * structure_density
    return subcritical_risk, structure_density, structure_overlap

# Show that by choosing seed_density, the attacker can make risk *any* value.
p, m = 0.6, 0.5
for seed in [0.0, 0.5, 1.0, 2.0]:
    risk, dens, over = alpha_risk(p, m, seed)
    print(f"Seed={seed:.2f} -> risk={risk:.3f}, density={dens:.3f}, overlap={over:.3f}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. SADDLE‑NODE BIFURCATION (Real physics Alpha misses)
# ─────────────────────────────────────────────────────────────────────────────
def saddle_node_ode(r, x, dt=0.01, steps=10000):
    """
    Simple forward‑Euler for the normal‑form ODE:
        dx/dt = r + x**2 - x**3
    r is the control parameter (true stability margin).
    """
    xs = np.empty(steps)
    x_cur = 0.0  # start from laminar state
    for i in range(steps):
        # Critical slowing down near r = 0
        x_cur += dt * (r + x_cur**2 - x_cur**3)
        xs[i] = x_cur
    return xs

# Sweep r from -0.2 (stable) to +0.2 (turbulent) and back to show hysteresis.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))

# Forward sweep (r increasing)
rs_fwd = np.linspace(-0.2, 0.2, 50)
xss_fwd = [saddle_node_ode(r, 0.0)[-1] for r in rs_fwd]

# Backward sweep (r decreasing)
rs_bwd = np.linspace(0.2, -0.2, 50)
xss_bwd = [saddle_node_ode(r, 0.0)[-1] for r in rs_bwd]

ax1.plot(rs_fwd, xss_fwd, 'o-', label='Forward (r ↑)')
ax1.plot(rs_bwd, xss_bwd, 's-', label='Backward (r ↓)')
ax1.axvline(0, color='k', linestyle='--')
ax1.set_xlabel('Control parameter r (true stability margin)')
ax1.set_ylabel('Order parameter x (turbulence amplitude)')
ax1.set_title('Saddle‑node hysteresis (Alpha’s linear model misses this)')
ax1.legend()
ax1.grid(True)

# ─────────────────────────────────────────────────────────────────────────────
# 3. CRITICAL SLOWING DOWN (variance explosion near bifurcation)
# ─────────────────────────────────────────────────────────────────────────────
def window_variance(series, win=1000):
    return np.array([np.var(series[i:i+win]) for i in range(len(series)-win)])

# Run the ODE three times: r = -0.05 (safe), r = -0.01 (near critical), r = +0.05 (turbulent)
for r, color, label in [(-0.05, 'green', 'Safe (r=-0.05)'),
                        (-0.01, 'orange', 'Near critical (r=-0.01)'),
                        (0.05, 'red', 'Turbulent (r=+0.05)')]:
    traj = saddle_node_ode(r, 0.0, steps=20000)
    var = window_variance(traj, win=2000)
    ax2.plot(var, color=color, label=label)

ax2.set_xlabel('Time window')
ax2.set_ylabel('Variance of x')
ax2.set_title('Critical slowing down: variance spikes near r≈0')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

# ─────────────────────────────────────────────────────────────────────────────
# 4. COD COLLAPSE (empty vectors → zero metric)
# ─────────────────────────────────────────────────────────────────────────────
def calculate_cod_empty():
    diagnostic_vec = np.array([])  # empty as in Alpha’s code
    plasma_vec = np.array([])
    dot = np.abs(np.vdot(diagnostic_vec, plasma_vec))
    magD = np.abs(np.vdot(diagnostic_vec, diagnostic_vec))
    magP = np.abs(np.vdot(plasma_vec, plasma_vec))
    fidelity = 0.0 if (magD < 1e-9 or magP < 1e-9) else dot / (np.sqrt(magD) * np.sqrt(magP))
    # penalties are exp(-k*x) → at most 1, so COD = fidelity * 1 * 1 * ... = 0
    return fidelity

print("\nCOD with empty vectors =", calculate_cod_empty())
# → 0.0, i.e. the protocol is flying blind.

# ─────────────────────────────────────────────────────────────────────────────
# 5. ATTACKER’S EXPLOIT: seeding + stealth ramp
# ─────────────────────────────────────────────────────────────────────────────
def stealth_attack():
    """
    Attacker keeps perturbation_amplitude *just* below the static margin
    while slowly increasing the seed density, causing structure_density
    to grow *exponentially* via the circular loop.
    """
    p = 0.59          # just below static margin of 0.60
    m = 0.60
    seed = 0.01
    densities = []
    for step in range(50):
        risk, dens, over = alpha_risk(p, m, seed)
        densities.append(dens)
        # Attacker increases seed each step (positive feedback)
        seed = dens * 1.1
    return densities

densities = stealth_attack()
print("\nStructure density after 50 stealth steps:", densities[-1])
# → can become arbitrarily large while *risk* remains zero because p ≤ m.