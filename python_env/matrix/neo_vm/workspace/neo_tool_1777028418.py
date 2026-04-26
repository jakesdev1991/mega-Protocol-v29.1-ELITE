# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
FSG‑v57 Parametric Resonance Demo

Simulates a second‑order artillery tracking loop with adiabatic stiffness modulation.
An adversarial flux injection (sinusoidal disturbance) at the governor’s modulation
frequency induces parametric resonance, causing stiffness to exceed the physical
limit and the computed Φ‑density to collapse.
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Physical Parameters ──
m = 1.0                    # mass (kg)
C = 2.0                    # damping (N·s/m)
K0 = 10.0                  # nominal stiffness (N/m)
K_max = 15.0               # absolute physical limit (N/m)
alpha = 0.5                # modulation depth
omega_g = 2 * np.pi * 1.0  # governor modulation frequency (rad/s)

# ── Adversarial Flux Injection ──
A_disturb = 5.0            # disturbance amplitude (N)
omega_d = omega_g           # match governor frequency → parametric resonance

# ── Simulation Setup ──
dt = 0.001                 # time step (s)
t_final = 10.0
steps = int(t_final / dt)
t = np.linspace(0, t_final, steps)

# State variables
x = np.zeros(steps)        # position error (m)
v = np.zeros(steps)        # velocity (m/s)
K = np.zeros(steps)        # time‑varying stiffness

# Metrics
COD = np.zeros(steps)      # Chain Overlap Density (≈ 1/(1+|error|))
Phi_N = np.zeros(steps)    # Φ_N = log2(COD)
violation = np.zeros(steps, dtype=bool)  # Smith Audit violation flag

# ── Integration Loop ──
for i in range(1, steps):
    # Governor stiffness (adiabatic modulation)
    K[i] = K0 * (1 - alpha * np.sin(omega_g * t[i]))
    
    # Adversarial disturbance
    d = A_disturb * np.sin(omega_d * t[i])
    
    # Dynamics: m·a = −K·x − C·v + d
    a = (-K[i] * x[i-1] - C * v[i-1] + d) / m
    
    # Euler integration
    v[i] = v[i-1] + a * dt
    x[i] = x[i-1] + v[i] * dt
    
    # Compute informational metrics
    COD[i] = 1.0 / (1.0 + abs(x[i]))
    Phi_N[i] = np.log2(COD[i] + 1e-12)  # avoid log(0)
    
    # Smith Audit: invariant violation if stiffness exceeds physical limit
    violation[i] = K[i] > K_max

# ── Post‑process: Identify singularity onset ──
# Singularity = stiffness > K_max for sustained period (>0.5 s)
singularity_start = np.where(violation & (np.convolve(violation, np.ones(500), mode='same') > 250))[0]
if singularity_start.size > 0:
    singularity_t = t[singularity_start[0]]
else:
    singularity_t = None

# ── Visualization ──
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# Panel 1: Position error & stiffness
axs[0].plot(t, x, label='Position Error (m)', color='red')
axs[0].set_ylabel('Error (m)')
axs[0].legend(loc='upper left')
axs[0].grid(True)

ax0_twin = axs[0].twinx()
ax0_twin.plot(t, K, label='Stiffness K(t) (N/m)', color='blue', linestyle='--')
ax0_twin.axhline(K_max, color='black', linestyle=':', label='Physical Limit')
ax0_twin.set_ylabel('Stiffness (N/m)')
ax0_twin.legend(loc='lower right')

# Panel 2: Φ‑density collapse
axs[1].plot(t, Phi_N, label='Φ_N (log₂ COD)', color='green')
axs[1].set_ylabel('Φ‑Density (bits)')
axs[1].set_ylim(-5, 1)
axs[1].legend(loc='upper right')
axs[1].grid(True)

# Panel 3: Smith Audit violation flag
axs[2].plot(t, violation.astype(int), label='Invariant Violation', color='purple', drawstyle='steps-pre')
axs[2].set_ylabel('Violation Flag')
axs[2].set_xlabel('Time (s)')
axs[2].set_ylim(-0.1, 1.1)
axs[2].legend(loc='upper right')
axs[2].grid(True)

plt.suptitle('FSG‑v57 Parametric Resonance & Φ‑Density Collapse', fontsize=14)
plt.tight_layout()
plt.show()

# ── Summary ──
print(f"Singularity onset time: {singularity_t:.3f} s" if singularity_t else "No singularity detected")
print(f"Final position error: {x[-1]:.3f} m")
print(f"Final Φ_N: {Phi_N[-1]:.3f} bits (collapse to near zero)")