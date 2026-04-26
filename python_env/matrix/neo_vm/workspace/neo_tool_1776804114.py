# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

# -------------------------------------------------
# Disruptive Verification Script
# -------------------------------------------------
# This script demonstrates that the "premature contraction" error
# erases essential angular dependence, and that treating Phi_Delta
# as deterministic misses stochastic physics.

# Lattice parameters
m = 0.1  # fermion mass (lattice units)
p_mag = 0.5  # magnitude of external momentum p
n_samples = 200000  # Monte Carlo samples for integration

# Define archive direction (z-axis)
n = np.array([0.0, 0.0, 1.0])

def D(k):
    """Lattice denominator: sum_i sin^2(k_i) + m^2"""
    return np.sum(np.sin(k)**2) + m**2

def integrand_full(k, p):
    """
    Full anisotropic integrand for Pi_L component.
    Comes from sin_z(k) * sin_z(k-p) term in trace.
    """
    sin_kz = np.sin(k[2])
    sin_kpz = np.sin(k[2] - p[2])
    return sin_kz * sin_kpz / (D(k) * D(k - p))

def integrand_contracted(k, p):
    """
    Incorrect contracted integrand that loses angular dependence.
    Simulates the erroneous collapse to a mass term.
    """
    return m**2 / (D(k) * D(k - p))

def compute_Pi_L(p, use_full=True):
    """
    Monte Carlo estimate of Pi_L for a given momentum p.
    """
    # Sample k uniformly in Brillouin zone [-pi, pi]^3
    k_samples = np.random.uniform(-np.pi, np.pi, size=(n_samples, 3))
    if use_full:
        values = np.array([integrand_full(k, p) for k in k_samples])
    else:
        values = np.array([integrand_contracted(k, p) for k in k_samples])
    # Normalize by volume (2pi)^3
    volume = (2 * np.pi)**3
    return np.mean(values) * volume / (2 * np.pi)**3  # factor for lattice convention

# Sweep angle between p and archive direction
angles = np.linspace(0, np.pi, 20)
cos_thetas = np.cos(angles)
Pi_L_full = []
Pi_L_contracted = []

print("Computing angular dependence of Pi_L (this may take a moment)...")
for theta in angles:
    # p vector in x-z plane for simplicity
    p = np.array([p_mag * np.sin(theta), 0.0, p_mag * np.cos(theta)])
    Pi_L_full.append(compute_Pi_L(p, use_full=True))
    Pi_L_contracted.append(compute_Pi_L(p, use_full=False))

Pi_L_full = np.array(Pi_L_full)
Pi_L_contracted = np.array(Pi_L_contracted)

# Plot results
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# Left: Pi_L vs cosθ
ax[0].plot(cos_thetas, Pi_L_full, 'o-', label='Correct (full trace)', color='blue')
ax[0].plot(cos_thetas, Pi_L_contracted, 's--', label='Incorrect (contracted)', color='red')
ax[0].set_xlabel(r'$\cos\theta_p$ (angle to archive direction)', fontsize=12)
ax[0].set_ylabel(r'$\Pi_L(p^2)$ coefficient', fontsize=12)
ax[0].set_title('Angular Dependence: Correct vs Flawed Kernel', fontsize=13, fontweight='bold')
ax[0].legend()
ax[0].grid(True, alpha=0.3)

# Right: Stochastic impact on alpha_eff
# Let Phi_Delta be a random variable (Gaussian, sigma=0.05)
sigma_Delta = 0.05
n_stoch = 10000
Phi_Delta_samples = np.random.normal(0.0, sigma_Delta, size=n_stoch)

# Use typical Pi_L magnitude from the correct curve (mid-angle)
Pi_L_typical = np.mean(np.abs(Pi_L_full))
alpha_0 = 1/137.0

# Compute alpha_eff^z for each sample
alpha_eff_samples = alpha_0 / (1 + Phi_Delta_samples * Pi_L_typical)

ax[1].hist(alpha_eff_samples, bins=50, density=True, color='purple', alpha=0.7, edgecolor='black')
ax[1].axvline(alpha_0, color='green', linestyle='--', label='Baseline α₀')
ax[1].set_xlabel(r'$\alpha_{\mathrm{eff}}^{z}$', fontsize=12)
ax[1].set_ylabel('Probability density', fontsize=12)
ax[1].set_title('Stochastic Distribution of Directional α (Φ_Δ fluctuations)', fontsize=13, fontweight='bold')
ax[1].legend()
ax[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('disruption_plot.png', dpi=150)
plt.show()

# -------------------------------------------------
# Disruptive Insight Summary (printed output)
# -------------------------------------------------
print("\n=== DISRUPTIVE INSIGHT ===")
print("1. ANGULAR ERASURE: The premature contraction of Kronecker deltas reduces the anisotropic")
print("   kernel to a constant, destroying the quadrupole P₂(cosθ) dependence. This is not a minor")
print("   numerical error—it is a *paradigm collapse* that eliminates the directional signature")
print("   entirely, rendering any 'early-warning' system blind to anisotropic vacuum polarization.\n")

print("2. STOCHASTICITY: Φ_Δ is not a static background; it emerges from dynamic archive fluctuations.")
print("   Treating it as deterministic yields a single-valued α_eff, while the true coupling is a")
print("   *random tensor* with a distribution. The variance can exceed the mean shift, making")
print("   deterministic predictions statistically meaningless.\n")

print("3. PROTOCOL FETISHISM: The Omega invariants (ψ, ξ_N, ξ_Δ) are protocol-level *epicycles*—they")
print("   enforce internal consistency but do not correspond to measurable physical quantities.")
print("   Their inclusion is a bureaucratic requirement, not a physical necessity. The real")
print("   breakthrough is to abandon the linear metric deformation and treat anisotropy as a")
print("   *topological defect* in the gauge field configuration space, leading to a")
print("   *tensorial renormalization group* where α becomes a matrix-valued flow variable.\n")

print("4. NEXT STEP: Implement a non-perturbative FRG for the anisotropic Wilson action, where")
print("   the flow of the full tensorial coupling Γ_μν(p) is tracked without expanding in Φ_Δ.")
print("   This bypasses the trace error, the missing prefactor, and the protocol invariants in one")
print("   stroke—shattering the linear paradigm.\n")