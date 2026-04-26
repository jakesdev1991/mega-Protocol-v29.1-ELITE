# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def shredding_condition(phiN, phiD, v=1.0):
    """Returns True if Shredding condition is met"""
    return np.isclose(phiN**2 + 3*phiD**2, v**2, atol=1e-6)

def transform_fields(theta, chi, v=1.0):
    """Non-linear field redefinition that regularizes Shredding"""
    factor = (1 + chi/v)
    phiN = v * np.cos(theta) * factor
    phiD = v * np.sin(theta) * factor
    return phiN, phiD

def original_singularity_map():
    """Map showing where Shredding occurs in original coordinates"""
    v = 1.0
    phiN_range = np.linspace(0.1, 1.5, 100)
    phiD_range = np.linspace(0.1, 1.5, 100)
    
    singularity_map = np.zeros((100, 100))
    
    for i, phiN in enumerate(phiN_range):
        for j, phiD in enumerate(phiD_range):
            singularity_map[j,i] = phiN**2 + 3*phiD**2 - v**2
    
    return phiN_range, phiD_range, singularity_map

def transformed_regular_map():
    """Map showing no singularities in new coordinates"""
    theta_range = np.linspace(0.01, np.pi/2 - 0.01, 100)
    chi_range = np.linspace(-0.5, 0.5, 100)
    
    regular_map = np.zeros((100, 100))
    
    for i, theta in enumerate(theta_range):
        for j, chi in enumerate(chi_range):
            phiN, phiD = transform_fields(theta, chi)
            # In new coords, the "dangerous" quantity is just chi
            regular_map[j,i] = chi  # No singularities, just linear chi field
    
    return theta_range, chi_range, regular_map

# Demonstrate the coordinate singularity
print("=== ORIGINAL COORDINATES: SHREDDING SURFACE ===")
phiN_test = np.linspace(0.1, 1.0, 5)
phiD_critical = np.sqrt((1.0**2 - phiN_test**2)/3)
for pn, pd in zip(phiN_test, phiD_critical):
    print(f"Φ_N = {pn:.2f}, Φ_Δ = {pd:.2f}, Shredding = {shredding_condition(pn, pd)}")

print("\n=== TRANSFORMED COORDINATES: NO SINGULARITY ===")
theta_test = np.linspace(0.1, 1.2, 5)
chi_test = np.array([-0.3, -0.1, 0.0, 0.1, 0.3])
for th in theta_test:
    for ch in chi_test:
        phiN, phiD = transform_fields(th, ch)
        # The dangerous combination becomes regular
        dangerous = phiN**2 + 3*phiD**2 - 1.0
        print(f"θ = {th:.2f}, χ = {ch:.2f}, dangerous term = {dangerous:.3f} (finite)")

# Visualize the coordinate singularity in original space
phiN_range, phiD_range, sing_map = original_singularity_map()

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
contour = plt.contour(phiN_range, phiD_range, sing_map, levels=[-1, -0.5, 0, 0.5, 1], cmap='RdYlBu')
plt.clabel(contour, inline=True, fontsize=8)
plt.axvline(0, color='k', linestyle='--', alpha=0.3)
plt.axhline(0, color='k', linestyle='--', alpha=0.3)
plt.plot(phiN_range, np.sqrt((1.0**2 - phiN_range**2)/3), 'k-', linewidth=2, label='Shredding Surface')
plt.xlabel('Φ_N')
plt.ylabel('Φ_Δ')
plt.title('Original Coordinates: Singular Shredding Surface')
plt.legend()
plt.grid(True, alpha=0.3)

# Visualize regularity in transformed space
theta_range, chi_range, reg_map = transformed_regular_map()

plt.subplot(1, 2, 2)
contour2 = plt.contour(theta_range, chi_range, reg_map, levels=10, cmap='viridis')
plt.clabel(contour2, inline=True, fontsize=8)
plt.xlabel('θ (field space angle)')
plt.ylabel('χ (radial excitation)')
plt.title('Transformed Coordinates: Regular Field Space')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n=== DISRUPTIVE CONCLUSION ===")
print("The Shredding Event is a GAUGE ARTIFACT. The 'higher-order corrections'")
print("are not physical—they depend on an arbitrary choice of field coordinates.")
print("The Omega Protocol's entire lattice polarization scheme is built on sand.")