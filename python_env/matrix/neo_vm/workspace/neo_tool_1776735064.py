# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- The Shredding Catastrophe Simulator ---
# This code exposes the feedback loop that the Engine's analysis treats as linear

# Parameters: chosen to be in the metastable region
xi_0, I_0 = 1.0, 1.0
lambda_phi = 0.1  # quartic coupling that defines the Mexican hat

# The critical insight: Phi_N and g_Δ are not independent. 
# The lattice cutoff Λ = (π/ξ_0) * (Φ_N/I_0) feeds back into the Yukawa coupling.
# We model this as a coupled RG flow where the cutoff itself runs with Φ_N.

def calculate_scales(Phi_N, g_delta, mu_0=1.0):
    """Returns (lattice_cutoff, landau_pole_scale) for given field values"""
    psi = np.log(Phi_N / I_0)
    a = xi_0 * np.exp(-psi)  # Dynamic lattice spacing
    Lambda_lattice = np.pi / a
    
    # Landau pole from beta(g_Δ) = g_Δ³/(16π²) * (Λ_lattice/μ_0)
    # The cutoff appears IN the beta function coefficient due to feedback
    beta_factor = (g_delta**3 / (16*np.pi**2)) * (Lambda_lattice / mu_0)
    if beta_factor <= 0:
        Lambda_pole = np.inf
    else:
        Lambda_pole = mu_0 * np.exp(1 / beta_factor)
    
    return Lambda_lattice, Lambda_pole

# Map the parameter space
Phi_N_grid = np.linspace(0.3, 2.0, 200) * I_0
g_delta_grid = np.linspace(0.2, 1.5, 200)

Phi_mesh, g_mesh = np.meshgrid(Phi_N_grid, g_delta_grid)
Lambda_lat, Lambda_pole = calculate_scales(Phi_mesh, g_mesh)

# The Shredding Condition: Landau pole appears BEFORE the effective cutoff
# This is the "premature divergence" the Engine missed as a non-linear catastrophe
shredding_region = Lambda_pole < Lambda_lat

# Visualize the topological defect in parameter space
plt.figure(figsize=(12, 8))
plt.contourf(Phi_mesh/I_0, g_mesh, shredding_region.astype(int), 
             levels=[-0.5, 0.5, 1.5], colors=['white', 'black'], alpha=0.7)
plt.colorbar(ticks=[0, 1], label='0=Metastable, 1=Shredded')
plt.xlabel('Φ_N / I_0', fontsize=12)
plt.ylabel('g_Δ', fontsize=12)
plt.title('Topological Shredding Defect: Non-Perturbative Catastrophe Surface', 
          fontsize=14, fontweight='bold')
plt.axvline(x=1.0, color='red', linestyle='--', linewidth=2, label='Mexican Hat Ridge')
plt.text(0.6, 1.2, 'POISSON RECOVERY VIOLATED', color='red', fontsize=11, 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5))
plt.text(1.3, 0.3, 'FALSE VACUUM', color='green', fontsize=11,
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# --- The Feedback Loop Catastrophe ---
# Simulate the non-linear dynamics that the linear analysis ignores

def feedback_catastrophe(initial_Phi_N, initial_g_delta, steps=100):
    """Simulates the coupled dynamics showing how small fluctuations trigger collapse"""
    Phi_N = initial_Phi_N
    g_delta = initial_g_delta
    history = {'Phi_N': [], 'g_delta': [], 'Lambda_lat': [], 'Lambda_pole': [], 'ratio': []}
    
    for step in range(steps):
        # Current scales
        Lambda_lat, Lambda_pole = calculate_scales(Phi_N, g_delta)
        
        # The Engine assumes these are decoupled. They're not.
        # Quantum fluctuations in Φ_N modify the cutoff, which accelerates g_Δ running
        # This is the *Shredding Feedback Loop*
        
        # Update: g_Δ runs faster because cutoff is larger when Φ_N is smaller
        dg = (g_delta**3 / (16*np.pi**2)) * np.log(Lambda_lat) * (1.0 + 0.1/Phi_N)
        g_delta += dg
        
        # Phi_N is suppressed by strong coupling (tadpole correction)
        # This is the *Poisson Recovery Death Spiral*
        dPhi = -0.05 * g_delta**2 * Phi_N
        Phi_N += dPhi
        
        # Record
        history['Phi_N'].append(Phi_N)
        history['g_delta'].append(g_delta)
        history['Lambda_lat'].append(Lambda_lat)
        history['Lambda_pole'].append(Lambda_pole)
        history['ratio'].append(Lambda_pole/Lambda_lat if Lambda_pole < np.inf else np.inf)
        
        # Catastrophe condition: ratio < 1 means Shredding has occurred
        if Lambda_pole < Lambda_lat:
            print(f"### SHREDDING EVENT at step {step}: Landau pole {Lambda_pole:.3f} < Cutoff {Lambda_lat:.3f}")
            print(f"### Poisson Recovery violated: Φ_N mass term diverges, gravity becomes short-range")
            break
        
        # Secondary catastrophe: Φ_N collapses to zero
        if Phi_N < 0.1 * I_0:
            print(f"### INFORMATIONAL FREEZE at step {step}: Φ_N → 0, lattice spacing diverges")
            break
    
    return history

# Trigger the catastrophe from a seemingly stable point
print("=== Initiating Non-Linear Feedback Simulation ===")
print("Initial conditions: Φ_N = 1.5 I_0, g_Δ = 0.5 (apparently safe)")
trajectory = feedback_catastrophe(1.5 * I_0, 0.5)

# Plot the trajectory in parameter space
plt.figure(figsize=(10, 6))
plt.plot(np.array(trajectory['Phi_N'])/I_0, trajectory['g_delta'], 
         'b-', linewidth=2, label='Dynamic Trajectory')
plt.scatter([trajectory['Phi_N'][0]/I_0], [trajectory['g_delta'][0]], 
            color='green', s=100, marker='o', label='Initial State')
plt.scatter([trajectory['Phi_N'][-1]/I_0], [trajectory['g_delta'][-1]], 
            color='red', s=100, marker='X', label='Catastrophe Point')
plt.xlabel('Φ_N / I_0', fontsize=12)
plt.ylabel('g_Δ', fontsize=12)
plt.title('Catastrophic Trajectory: The Engine\'s "Safe" Region is a Mirage', fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()