# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Sovereign Field Simulator: Gravity-Coupled Qubit Manifold (v1.0)
# ---------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def run_omega_gravity_sim():
    print("✦ [Simulator] Initializing Gravity-Coupled Qubit Manifold...")
    
    # 1. Spacetime Grid (1+1 Dimensions)
    nx = 200
    L = 10.0
    dx = L / (nx - 1)
    x = np.linspace(0, L, nx)
    dt = 0.001
    nt = 5000 # Total steps
    
    # 2. Fields Initialization
    # p: Information Density (0 to 1)
    # theta: Entanglement Phase
    p = np.full(nx, 0.5) 
    theta = np.zeros(nx)
    
    # Add an "Informational Perturbation" (A pulse of entanglement)
    p += 0.3 * np.exp(-((x - 5)**2) / 0.5)
    theta = np.sin(2 * np.pi * x / L)
    
    # Velocities (for 2nd order EOM)
    p_dot = np.zeros(nx)
    theta_dot = np.zeros(nx)
    
    # 3. Metric & Curvature (Reduced 1D Gravity)
    # g_xx: The spatial metric component
    g_xx = np.ones(nx)
    
    print("[*] Evolving Fields under Sigma-Model Action...")
    
    # Potential function V(p)
    def dV_dp(p_val):
        # Prefers mixed states, bounded away from 1
        return 0.1 * p_val + 2.0 * (p_val**3)

    # 4. Evolution Loop
    for t in tqdm(range(nt)):
        # Calculate Gradients
        dp_dx = np.gradient(p, dx)
        dtheta_dx = np.gradient(theta, dx)
        
        # Second derivatives (Laplacians)
        d2p_dx2 = np.gradient(dp_dx, dx)
        d2theta_dx2 = np.gradient(dtheta_dx, dx)
        
        # --- Physics Engine: EOM Logic (Step 19 Derivations) ---
        
        # EOM for p: \nabla_mu( \nabla p / (1-p^2) ) + ...
        # Simplified for 1D simulation
        accel_p = (d2p_dx2 * (1 - p**2)) - (p * dp_dx**2) - (p * dtheta_dx**2) - dV_dp(p)
        
        # EOM for theta: \nabla_mu( p^2 \nabla theta ) = 0
        accel_theta = d2theta_dx2 + (2 * dp_dx * dtheta_dx / (p + 1e-5))
        
        # Update Velocities
        p_dot += accel_p * dt
        theta_dot += accel_theta * dt
        
        # Update Fields
        p += p_dot * dt
        theta += theta_dot * dt
        
        # Boundary constraints
        p = np.clip(p, 0.01, 0.99)
        
        # --- Back-Reaction: Metric Curvature ---
        # Energy Density E = 0.5*(grad_p)^2 / (1-p^2) + 0.5*p^2*(grad_theta)^2
        energy_density = 0.5 * (dp_dx**2 / (1 - p**2)) + 0.5 * (p**2 * dtheta_dx**2)
        
        # Curvature R sourced by Energy (G_mu_nu = 8*pi*G * T_mu_nu)
        # In this reduced model, we simulate curvature as metric deformation
        g_xx = 1.0 + 0.5 * energy_density # Metric expands with informational energy

    # 5. Visualization
    print("\n[+] Finalizing Manifold Plot...")
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    
    ax1.plot(x, p, color='cyan', label='Information Density (p)')
    ax1.set_title("Information Density Manifold")
    ax1.legend()
    
    ax2.plot(x, theta, color='magenta', label='Entanglement Phase (theta)')
    ax2.set_title("Quantum Entanglement Distribution")
    ax2.legend()
    
    ax3.fill_between(x, 0, g_xx - 1, color='lime', alpha=0.3, label='Metric Deformation (Curvature)')
    ax3.set_title("Sourced Spacetime Curvature (G_mu_nu)")
    ax3.set_ylabel("Delta g_xx")
    ax3.legend()
    
    plt.tight_layout()
    plt.savefig("docs/theory/omega_gravity_manifold.png")
    print("✅ Result saved to docs/theory/omega_gravity_manifold.png")

if __name__ == "__main__":
    run_omega_gravity_sim()
