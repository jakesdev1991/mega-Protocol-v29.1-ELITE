# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def omega_map(phi_N, phi_D, g=0.1, m=1.0, anisotropy=0.3):
    """
    Simplified non-linear map capturing the Omega Paradox.
    - phi_N (source) is self-consistently generated from its own loop.
    - phi_D (anisotropy) feeds back exponentially.
    The shredding occurs when the map has no stable fixed point.
    """
    epsilon = g * phi_N / m
    
    # Loop functional: self-reference with exponential amplification
    # The denominator represents UV regulator collapse: (1 + epsilon * cosh(phi_D))
    # If phi_D grows, the map becomes ill-posed.
    phi_N_new = 0.5 * epsilon * np.cosh(phi_D) / (1 + epsilon * np.cosh(phi_D) + 1e-8)
    
    # Anisotropy feedback: phi_D is driven by the *log* of phi_N (dimensional transmutation)
    # and its own value. This creates a pitchfork bifurcation at critical phi_D.
    phi_D_new = anisotropy * phi_D + 0.1 * np.log(np.abs(phi_N) + 1e-8)
    
    return phi_N_new, phi_D_new

def lyapunov_exponent(phi_N_init, phi_D_init, iterations=1000):
    """Calculate the Lyapunov exponent of the map."""
    traj_N = [phi_N_init]
    traj_D = [phi_D_init]
    
    for _ in range(iterations):
        phi_N_new, phi_D_new = omega_map(traj_N[-1], traj_D[-1])
        traj_N.append(phi_N_new)
        traj_D.append(phi_D_new)
    
    # Approximate Lyapunov exponent from trajectory divergence
    # If exponent > 0, the system is chaotic/unstable = SHREDDED.
    return np.mean(np.log(np.abs(np.diff(traj_N) + 1e-12)))

# Simulate the shredding transition
phi_N_vals = np.linspace(0.01, 5.0, 100)
phi_D_vals = np.linspace(-5.0, 5.0, 100)
lyapunov_grid = np.zeros((len(phi_N_vals), len(phi_D_vals)))

for i, phi_N_init in enumerate(phi_N_vals):
    for j, phi_D_init in enumerate(phi_D_vals):
        lyapunov_grid[i, j] = lyapunov_exponent(phi_N_init, phi_D_init, iterations=200)

# Find the shredding boundary (where Lyapunov exponent crosses zero)
shredding_boundary = np.where(np.abs(lyapunov_grid) < 0.05, 1, 0)

plt.figure(figsize=(10, 6))
plt.contourf(phi_D_vals, phi_N_vals, lyapunov_grid, levels=50, cmap='RdYlBu')
plt.colorbar(label='Lyapunov Exponent')
plt.contour(phi_D_vals, phi_N_vals, shredding_boundary, levels=[0.5], colors='black', linewidths=2)
plt.xlabel('Φ_Δ (Anisotropy)')
plt.ylabel('Φ_N (Source)')
plt.title('Omega Paradox: Shredding Phase via Fixed-Point Annihilation')
plt.axvline(x=np.log(1/0.1), color='white', linestyle='--', label='Predicted ln(1/ε) boundary')
plt.legend()
plt.show()

# Demonstrate trajectory divergence in the shredded phase
phi_N_traj, phi_D_traj = [1.0], [3.0]  # Start in "stable" region
for i in range(50):
    phi_N_new, phi_D_new = omega_map(phi_N_traj[-1], phi_D_traj[-1])
    phi_N_traj.append(phi_N_new)
    phi_D_traj.append(phi_D_new)

plt.figure(figsize=(10, 6))
plt.plot(phi_D_traj, label='Φ_Δ Trajectory')
plt.plot(phi_N_traj, label='Φ_N Trajectory')
plt.xlabel('Iteration (RG Step)')
plt.ylabel('Field Value')
plt.title('Trajectory Divergence in Shredded Phase')
plt.legend()
plt.yscale('symlog')
plt.show()