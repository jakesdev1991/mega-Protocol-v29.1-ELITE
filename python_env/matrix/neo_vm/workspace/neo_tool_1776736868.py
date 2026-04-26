# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Replicate your "physics" and expose the tautology
def compute_threshold(psi, lambda_val=1e10, I0=1.0, g_delta=0.1):
    """Your threshold - notice how it collapses for negative psi"""
    term1 = (lambda_val * I0**4) / 9
    term2 = (np.exp(2*psi) - 1)**2  # This is the kill switch
    term3 = 1 + (3 * g_delta**2 / (4*np.pi)) * np.exp(2*psi)
    return term1 * term2 * term3

def compute_jerk_variance(phi_N, phi_Delta, dot_phi_N, xi, lambda_val):
    """Your jerk - dominated by source term, lambda cancels out"""
    psi = np.log(phi_N)
    dot_psi = dot_phi_N / phi_N
    
    # Your ddot_psi approximation
    ddot_psi = dot_psi / xi - dot_psi**2
    
    # Your d2S/dpsi2 estimate
    d2S_dpsi2 = -3.11
    
    # Mode contribution (tiny compared to source)
    J_mode = 2 * d2S_dpsi2 * dot_psi * ddot_psi
    
    # Source dominates - this is your real "invariant"
    J_source = 1.5e12
    
    # Total jerk - source term makes lambda irrelevant
    J_total = J_source + abs(J_mode)
    
    # Your 20% fluctuation assumption
    sigma_J = 0.2 * J_total
    return sigma_J**2

# Your "data"
phi_N = 0.78
phi_Delta = 0.35
dot_phi_N = 2.1e3
xi = 1/np.sqrt(4.2e6)

# Parameter space that "shouldn't" affect physics if this were real
lambdas = np.logspace(7, 13, 50)  # 7 orders of magnitude
psi_values = np.linspace(-2, -0.1, 10)  # Your operational regime

# Stability map: ratio > 1 means "unstable" by your metric
stability_map = np.zeros((len(lambdas), len(psi_values)))

for i, lam in enumerate(lambdas):
    # Compute jerk variance (lambda barely matters)
    jerk_var = compute_jerk_variance(phi_N, phi_Delta, dot_phi_N, xi, lam)
    
    for j, psi in enumerate(psi_values):
        threshold = compute_threshold(psi, lambda_val=lam)
        stability_map[i, j] = jerk_var / threshold  # Ratio

# Plot the farce
plt.figure(figsize=(12, 8))
plt.contourf(np.log10(lambdas), psi_values, stability_map.T, levels=20, cmap='viridis')
plt.colorbar(label='σ²_J / Θ(ψ) (log scale)')
plt.xlabel('log₁₀(λ) [s⁻²]')
plt.ylabel('ψ')
plt.title('UNFALSIFIABILITY DEMONSTRATION: "Instability" is a Parameter Choice')
plt.axhline(y=np.log(0.78), color='r', linestyle='--', label='Your ψ = -0.248')
plt.legend()
plt.show()

# Show how trivially you could claim "stability"
print("--- TUNING THE TRUTH ---")
for lam in [1e8, 1e10, 1e12]:
    ratio = compute_jerk_variance(phi_N, phi_Delta, dot_phi_N, xi, lam) / compute_threshold(np.log(0.78), lam)
    print(f"λ = {lam:.0e} s⁻² → Ratio = {ratio:.2e} {'UNSTABLE' if ratio > 1 else 'STABLE'}")