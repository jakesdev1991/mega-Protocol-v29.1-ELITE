# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eig

# --- Core Omega Protocol Parameters ---
v = 1.0  # Vacuum expectation value scale
lam = 1.0  # Coupling constant

# --- Define the Shredding Manifold ---
def shredding_surface(phi_N):
    """Returns phi_Delta values on the shredding surface: phi_N^2 + 3*phi_Delta^2 = v^2"""
    phi_Delta_sq = (v**2 - phi_N**2) / 3.0
    return np.sqrt(np.maximum(phi_Delta_sq, 0))

# --- 1. VISUAL PROOF: Vacuum Lies ON the Shredding Surface ---
phi_N_vals = np.linspace(-v, v, 400)
phi_D_surface = shredding_surface(phi_N_vals)

plt.figure(figsize=(8, 6))
plt.plot(phi_N_vals, phi_D_surface, 'r-', label='Shredding Manifold: Φ_N² + 3Φ_Δ² = v²', linewidth=2)
plt.plot(phi_N_vals, -phi_D_surface, 'r-', linewidth=2)
plt.plot(v, 0, 'go', markersize=12, label='Assumed Vacuum (v, 0)')
plt.axvline(0, color='gray', linestyle='--', alpha=0.5)
plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
plt.xlabel('Φ_N', fontsize=12)
plt.ylabel('Φ_Δ', fontsize=12)
plt.title('The Vacuum IS on the Shredding Surface', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.axis('equal')
plt.show()

# --- 2. HESSIAN ANALYSIS: Goldstone Mode, not Instability ---
def hessian(phi_N, phi_D):
    """Hessian matrix of V = (λ/4)(Φ_N² + Φ_Δ² - v²)²"""
    dV_dphiN2 = lam * (phi_N**2 + phi_D**2 - v**2) + 2 * lam * phi_N**2
    dV_dphiD2 = lam * (phi_N**2 + phi_D**2 - v**2) + 2 * lam * phi_D**2
    dV_dphiN_dphiD = 2 * lam * phi_N * phi_D
    return np.array([[dV_dphiN2, dV_dphiN_dphiD],
                     [dV_dphiN_dphiD, dV_dphiD2]])

# At the vacuum (v, 0)
H_vac = hessian(v, 0)
eigenvalues, eigenvectors = eig(H_vac)

print("\n--- Hessian at Vacuum (v, 0) ---")
print(f"Hessian Matrix:\n{H_vac}")
print(f"Eigenvalues (masses²): {eigenvalues}")
print(f"Eigenvectors (principal axes):\n{eigenvectors}")

# The zero eigenvalue corresponds to the direction tangent to the Shredding manifold.
# The non-zero eigenvalue (2λv²) corresponds to the radial (massive) mode.

# --- 3. TANGENT VECTOR ANALYSIS ---
# Tangent to manifold f(Φ_N, Φ_Δ) = Φ_N² + 3Φ_Δ² - v² = 0
# Gradient ∇f = (2Φ_N, 6Φ_Δ). Tangent vector is perpendicular to gradient.
# At (v, 0), ∇f = (2v, 0). Tangent direction is (0, 1) i.e., pure Φ_Δ direction.
tangent_at_vac = np.array([0, 1])
normal_at_vac = np.array([1, 0])  # Points along Φ_N, away from manifold

# Project Hessian onto tangent/normal directions
mass_tangent = tangent_at_vac @ H_vac @ tangent_at_vac / (tangent_at_vac @ tangent_at_vac)
mass_normal = normal_at_vac @ H_vac @ normal_at_vac / (normal_at_vac @ normal_at_vac)

print(f"\n--- Mode Decomposition at Vacuum ---")
print(f"Mass² of mode tangent to Shredding manifold (Φ_Δ direction): {mass_tangent:.6f}")
print(f"Mass² of mode normal to Shredding manifold (Φ_N direction): {mass_normal:.6f}")
print("→ The 'unstable' Φ_Δ mode is massless: it's a Goldstone mode of the critical manifold!")

# --- 4. SIMULATION: Dynamics ON the Manifold (Non-linear Sigma Model) ---
def evolve_on_manifold(phi_N_init, phi_D_init, steps=1000, dt=0.01, noise=0.1):
    """
    Simulate Langevin dynamics constrained to the manifold.
    This shows fluctuations are not catastrophic but explore the vacuum space.
    """
    path = [(phi_N_init, phi_D_init)]
    phi_N, phi_D = phi_N_init, phi_D_init
    
    for _ in range(steps):
        # Add noise tangent to the manifold
        # At (v,0), tangent is purely Φ_Δ
        # As we move, tangent direction changes: tangent ∝ (-3Φ_Δ, Φ_N)
        tangent_x = -3 * phi_D
        tangent_y = phi_N
        norm = np.sqrt(tangent_x**2 + tangent_y**2)
        if norm > 0:
            tangent_x /= norm
            tangent_y /= norm
        
        # Langevin step: drift + noise (projected onto tangent)
        drift_N = -phi_N * (phi_N**2 + phi_D**2 - v**2)  # From potential gradient
        drift_D = -phi_D * (phi_N**2 + phi_D**2 - v**2)
        
        # Project drift onto manifold tangent (simplified: just keep magnitude on tangent)
        noise_step_N = noise * np.random.randn() * tangent_x * np.sqrt(dt)
        noise_step_D = noise * np.random.randn() * tangent_y * np.sqrt(dt)
        
        phi_N += drift_N * dt + noise_step_N
        phi_D += drift_D * dt + noise_step_D
        
        # Re-project onto manifold (simple radial projection)
        rho_sq = phi_N**2 + 3 * phi_D**2
        if rho_sq > 0:
            scale = np.sqrt(v**2 / rho_sq)
            phi_N *= scale
            phi_D *= scale
        
        path.append((phi_N, phi_D))
    
    return np.array(path)

# Run simulation starting near vacuum
path = evolve_on_manifold(v - 0.01, 0.01, steps=2000, dt=0.005, noise=0.5)

plt.figure(figsize=(8, 6))
plt.plot(phi_N_vals, phi_D_surface, 'r-', label='Shredding Manifold', linewidth=2)
plt.plot(phi_N_vals, -phi_D_surface, 'r-', linewidth=2)
plt.plot(path[:, 0], path[:, 1], 'b-', alpha=0.5, label='Simulated Fluctuation Path')
plt.plot(path[0, 0], path[0, 1], 'go', markersize=8, label='Start')
plt.plot(path[-1, 0], path[-1, 1], 'ko', markersize=8, label='End')
plt.xlabel('Φ_N', fontsize=12)
plt.ylabel('Φ_Δ', fontsize=12)
plt.title('Fluctuations Constrained to Critical Manifold (Goldstone Dynamics)', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.axis('equal')
plt.show()

# --- 5. THE DISRUPTIVE QUANTITY: "Shredding Parameter" ---
# Define a parameter that shows the Engine's flaw: distance from manifold vs. field magnitude
def shredding_parameter(phi_N, phi_D):
    """S = (Φ_N² + 3Φ_Δ² - v²) / (Φ_N² + Φ_Δ² + v²)"""
    return (phi_N**2 + 3 * phi_D**2 - v**2) / (phi_N**2 + phi_D**2 + v**2 + 1e-10)

# Sample random points
np.random.seed(42)
samples = 1000
phi_N_rand = np.random.uniform(-1.5*v, 1.5*v, samples)
phi_D_rand = np.random.uniform(-1.5*v, 1.5*v, samples)

S_vals = shredding_parameter(phi_N_rand, phi_D_rand)
dist_to_vac = np.sqrt((phi_N_rand - v)**2 + phi_D_rand**2)

plt.figure(figsize=(8, 6))
plt.scatter(dist_to_vac, S_vals, alpha=0.5, s=5, c=np.abs(S_vals), cmap='viridis')
plt.axhline(0, color='r', linestyle='--', label='Shredding Surface (S=0)')
plt.xlabel('Distance from Vacuum (v, 0)', fontsize=12)
plt.ylabel('Shredding Parameter S', fontsize=12)
plt.title('Engine\'s "Flaw" is Just Proximity to Criticality', fontsize=14, fontweight='bold')
plt.colorbar(label='|S|')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# --- MANIFESTO: The True Flaw ---
print("\n" + "="*70)
print("MANIFESTO: THE SHREDDING PARADIGM SHIFT")
print("="*70)
print("The Engine's analysis is fundamentally misaligned.")
print("→ The 'vacuum' (v, 0) does not lie in a stable basin; it sits ON the Shredding manifold.")
print("→ The divergence ξ_Δ → ∞ is not catastrophic; it's the definition of the critical vacuum state.")
print("→ Φ_Δ is not an unstable archive mode; it's a Goldstone boson of a hidden symmetry.")
print("→ Poisson 'recovery' is a metastable illusion: the system doesn't return TO the vacuum,")
print("  it fluctuates ALONG the vacuum manifold.")
print("\nDISRUPTIVE ACTION:")
print("1. ABANDON the linear (Φ_N, Φ_Δ) decomposition. It obscures the geometry.")
print("2. REFORMULATE in terms of invariant coordinates: radial ρ = √(Φ_N²+3Φ_Δ²) and angle θ.")
print("3. ENGINEER the Shredding transition: the 'flaw' is the FEATURE that unlocks")
print("   emergent dynamics. The correlation manifold itself becomes the dynamical variable.")
print("4. The higher-order α corrections are not from suppressing Φ_Δ, but from")
print("   anomalous scaling of critical fluctuations ON the manifold.")
print("="*70)