# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import quad, nquad
import matplotlib.pyplot as plt

# Define parameters
Lambda = 0.82
v = 1.28

def original_integrand(k):
    """Original integrand without shredding singularity"""
    return np.exp(-k**2/(2*Lambda**2)) / (1 + (k*v)**2)

def shredding_integrand(k):
    """Integrand with shredding singularity factor"""
    if k >= Lambda:
        return 0
    # Add singularity as k approaches Lambda
    singularity_factor = 1.0 / (1 - k/Lambda + 1e-10)  # small epsilon to avoid division by zero
    return original_integrand(k) * singularity_factor

# Evaluate the original 1D integral (radial part only)
def original_radial_integral():
    """Compute the radial integral for the original case"""
    def integrand(k):
        if k >= Lambda:
            return 0
        # 4πk² factor from spherical coordinates
        return 4*np.pi * k**2 * original_integrand(k)
    
    result, error = quad(integrand, 0, Lambda, limit=200)
    return result, error

def shredding_radial_integral():
    """Compute the radial integral with shredding singularity"""
    def integrand(k):
        if k >= Lambda:
            return 0
        # 4πk² factor from spherical coordinates
        return 4*np.pi * k**2 * shredding_integrand(k)
    
    result, error = quad(integrand, 0, Lambda, limit=200)
    return result, error

# Evaluate both integrals
orig_result, orig_error = original_radial_integral()
shred_result, shred_error = shredding_radial_integral()

print("=== INTEGRAL ANALYSIS ===")
print(f"Original integral result: {orig_result:.6e} ± {orig_error:.6e}")
print(f"Shredding integral result: {shred_result:.6e} ± {shred_error:.6e}")
print(f"Ratio (Shredding/Original): {shred_result/orig_result:.6e}")

# Analyze divergence behavior near Lambda
def analyze_near_horizon(num_points=1000):
    """Analyze behavior as k approaches Lambda"""
    ks = np.linspace(0, Lambda*0.999, num_points)
    orig_vals = [original_integrand(k) for k in ks]
    shred_vals = [shredding_integrand(k) for k in ks]
    
    print(f"\n=== NEAR-HORIZON ANALYSIS ===")
    print(f"Maximum original integrand value: {max(orig_vals):.6e}")
    print(f"Maximum shredding integrand value: {max(shred_vals):.6e}")
    
    # Check scaling near horizon
    k_near = ks[-10:]  # Last 10 points
    v_near = [shredding_integrand(k) for k in k_near]
    
    # Fit to power law (1 - k/Lambda)^-1
    x = 1 - k_near/Lambda
    y = v_near
    
    # Log-log fit to determine power
    log_x = np.log(x)
    log_y = np.log(y)
    slope, intercept = np.polyfit(log_x, log_y, 1)
    
    print(f"Divergence scaling exponent: {slope:.4f} (should be ~1 for (1-k/Λ)^-1)")
    
    return ks, orig_vals, shred_vals

# Run analysis
ks, orig_vals, shred_vals = analyze_near_horizon()

# Check dimensional consistency
print(f"\n=== DIMENSIONAL ANALYSIS ===")
print(f"Lambda = {Lambda} (dimensionless in derivation)")
print(f"If Lambda has dimension [L^-1], then original integral scales as Λ^3 = {Lambda**3:.6e}")
print(f"Correction factor (Φ_Δ/Φ_N) * (1/Λ^2) * I would scale as (Φ_Δ/Φ_N) * Λ")
print(f"For claimed Δα/α = 5.4e-6, required ratio: Φ_Δ/Φ_N = {5.4e-6/Lambda:.6e}")

# Check if this ratio is stable under perturbation
def stability_analysis(ratio=6.585e-06, perturbation=0.1):
    """Test stability of the ratio"""
    perturbed_ratio = ratio * (1 + perturbation)
    delta_alpha_original = ratio * Lambda
    delta_alpha_perturbed = perturbed_ratio * Lambda
    
    print(f"\n=== STABILITY ANALYSIS ===")
    print(f"Original ratio: {ratio:.6e}")
    print(f"Perturbed ratio (+10%): {perturbed_ratio:.6e}")
    print(f"Δα/α change: {delta_alpha_perturbed - delta_alpha_original:.6e}")
    print(f"Relative change: {(delta_alpha_perturbed - delta_alpha_original)/delta_alpha_original:.2%}")
    
    # Check if this violates Poisson recovery condition
    # Poisson recovery requires Φ_N to dominate, i.e., Φ_Δ/Φ_N << 1
    if perturbed_ratio > 0.01:
        print("WARNING: Perturbation drives ratio into non-perturbative regime!")
        return False
    return True

is_stable = stability_analysis()

# Plot the divergence
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(ks, orig_vals, 'b-', label='Original')
plt.plot(ks, shred_vals, 'r--', label='With Shredding')
plt.axvline(Lambda, color='k', linestyle=':', label='Horizon Λ')
plt.xlabel('k')
plt.ylabel('Integrand value')
plt.title('Integrand Comparison')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.loglog(1 - ks/Lambda, shred_vals, 'r-', label='Shredding behavior')
plt.xlabel('log(1 - k/Λ)')
plt.ylabel('log(Integrand)')
plt.title('Near-Horizon Divergence')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(f"\n=== FINAL VERDICT ===")
if not is_stable:
    print("SHREDDING FLAW CONFIRMED: The orthogonal decomposition breaks down at the horizon.")
    print("Φ_Δ diverges as (1 - k/Λ)^-1, violating Poisson recovery of Φ_N.")
    print("The claimed Δα/α = 5.4e-6 is an artifact of ignoring this singularity.")
else:
    print("No immediate instability detected, but dimensional inconsistencies remain.")