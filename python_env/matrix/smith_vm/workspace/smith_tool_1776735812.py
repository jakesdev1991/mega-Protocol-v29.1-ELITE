# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# Given values from the Engine's numerical evaluation
phi_N = 0.78
phi_Delta = 0.35
v = I0 = 1.0  # Normalization scale set to 1 as per Engine
dot_phi_N = 2.1e3  # s^-1
dot_phi_Delta = 8.7e3  # s^-1
xi_inv_sq = 4.2e6  # s^-2
J_source = 1.5e12  # s^-3

# Step 1: Compute entropy derivatives (two-state model)
# Probabilities: p_N = phi_N / (phi_N + phi_Delta), p_Delta = phi_Delta / (phi_N + phi_Delta)
# But Engine used: p_N ∝ phi_N, p_Delta ∝ phi_Delta, and normalized so p_N + p_Delta = 1
# Thus: p_N = phi_N / (phi_N + phi_Delta), p_Delta = phi_Delta / (phi_N + phi_Delta)
sum_phi = phi_N + phi_Delta
p_N = phi_N / sum_phi
p_Delta = phi_Delta / sum_phi

# Shannon entropy: S_h = -[p_N * ln(p_N) + p_Delta * ln(p_Delta)]
# Derivatives as per Engine:
# ∂S_h/∂phi_N = -ln(p_N / p_Delta)   [since p_N/p_Delta = phi_N/phi_Delta]
# ∂²S_h/∂phi_N² = - (1/p_N * ∂p_N/∂phi_N + 1/p_Delta * ∂p_Delta/∂phi_N)
# But Engine simplified to: ∂²S_h/∂phi_N² ≈ -1/phi_N - 1/phi_Delta (under their approximation)
# Let's compute both ways to verify

# Exact derivatives for two-state system:
def compute_entropy_derivatives(phi_N, phi_Delta):
    sum_phi = phi_N + phi_Delta
    p_N = phi_N / sum_phi
    p_Delta = phi_Delta / sum_phi
    
    # Avoid log(0)
    if p_N <= 0 or p_Delta <= 0:
        return float('-inf'), float('inf')
    
    S_h = - (p_N * math.log(p_N) + p_Delta * math.log(p_Delta))
    
    # First derivatives
    dS_dphi_N = -math.log(p_N / p_Delta)  # = -ln(phi_N/phi_Delta)
    dS_dphi_Delta = -math.log(p_Delta / p_N)  # = -ln(phi_Delta/phi_N)
    
    # Second derivatives
    d2S_dphiN2 = - (1/(phi_N * sum_phi) + 1/(phi_Delta * sum_phi))
    d2S_dphiD2 = - (1/(phi_Delta * sum_phi) + 1/(phi_N * sum_phi))
    d2S_dphiNphiD = 1/(sum_phi**2)  # Mixed partial
    
    return S_h, dS_dphi_N, dS_dphi_Delta, d2S_dphiN2, d2S_dphiD2, d2S_dphiNphiD

S_h, dS_dphi_N, dS_dphi_Delta, d2S_dphiN2, d2S_dphiD2, d2S_dphiNphiD = compute_entropy_derivatives(phi_N, phi_Delta)

print("Entropy derivatives (exact):")
print(f"  S_h = {S_h:.6f}")
print(f"  ∂S_h/∂φ_N = {dS_dphi_N:.6f}")
print(f"  ∂S_h/∂φ_Δ = {dS_dphi_Delta:.6f}")
print(f"  ∂²S_h/∂φ_N² = {d2S_dphiN2:.6f}")
print(f"  ∂²S_h/∂φ_Δ² = {d2S_dphiD2:.6f}")
print(f"  ∂²S_h/∂φ_N∂φ_Δ = {d2S_dphiNphiD:.6f}")

# Engine's approximation for ∂S_h/∂phi_N and ∂²S_h/∂phi_N²
approx_dS_dphi_N = -math.log(phi_N / phi_Delta)
approx_d2S_dphiN2 = - (1/phi_N + 1/phi_Delta)

print("\nEngine's approximations:")
print(f"  ∂S_h/∂φ_N (approx) = {approx_dS_dphi_N:.6f}")
print(f"  ∂²S_h/∂φ_N² (approx) = {approx_d2S_dphiN2:.6f}")

# Step 2: Compute characteristic time xi from xi_inv_sq
xi = 1.0 / math.sqrt(xi_inv_sq)  # s
print(f"\nCharacteristic time ξ = {xi:.6e} s")

# Step 3: Estimate second derivatives (Engine's method: ddot_phi ≈ dot_phi / xi)
ddot_phi_N_est = dot_phi_N / xi
ddot_phi_Delta_est = dot_phi_Delta / xi

print(f"\nEstimated second derivatives:")
print(f"  φ̈_N ≈ {ddot_phi_N_est:.6e} s^-2")
print(f"  φ̈_Δ ≈ {ddot_phi_Delta_est:.6e} s^-2")

# Step 4: Compute informational jerk using chain rule (Engine's dominant term)
# Engine used: J_I ≈ 2 * (∂²S_h/∂φ_N²) * ˙φ_N * ¨φ_N  (from d/dt[ (∂²S_h/∂φ_N²) ˙φ_N² ])
J_I_Newton = 2 * approx_d2S_dphiN2 * dot_phi_N * ddot_phi_N_est
print(f"\nJerk contribution from Newtonian mode (Engine's approx):")
print(f"  J_I_N = {J_I_Newton:.6e} s^-3")

# Total jerk including source (Engine assumed Archive mode contribution negligible)
J_I_total = J_I_Newton + J_source
print(f"\nTotal informational jerk:")
print(f"  J_I = J_I_N + J_source = {J_I_total:.6e} s^-3")

# Step 5: Estimate variance of jerk (Engine assumed 20% fluctuation)
sigma_J = 0.2 * abs(J_I_total)  # s^-3
sigma_J_sq = sigma_J ** 2  # s^-6
print(f"\nEstimated jerk variance (20% fluctuation):")
print(f"  σ_J = {sigma_J:.6e} s^-3")
print(f"  σ_J² = {sigma_J_sq:.6e} s^-6")

# Step 6: Compute threshold Theta
lambda_val = 1.0e10  # s^-2 (Engine's typical value)
g_Delta = 0.1        # Archive mode coupling
Theta = (lambda_val * I0**2) / (4 * math.pi) * (1 + (3 * g_Delta**2) / (4 * math.pi))
print(f"\nShredding threshold Θ:")
print(f"  Θ = (λI₀²)/(4π) * (1 + 3g_Δ²/(4π)) = {Theta:.6e} s^-6")

# Step 7: Stability check
is_stable = sigma_J_sq < Theta
print(f"\nStability check (σ_J² < Θ?):")
print(f"  σ_J² = {sigma_J_sq:.6e} s^-6")
print(f"  Θ    = {Theta:.6e} s^-6")
print(f"  Stable? {is_stable}")

# Additional verification: Check if Engine's claim about units holds
# Jerk should have units s^-3. Let's verify the Newtonian term units:
# [∂²S_h/∂φ_N²] is dimensionless (since S_h and φ are dimensionless after normalization)
# [˙φ_N] = s^-1, [¨φ_N] = s^-2 → product: s^-3 ✓
print(f"\nUnit verification:")
print(f"  [∂²S_h/∂φ_N²] = dimensionless")
print(f"  [˙φ_N] = s^-1")
print(f"  [¨φ_N] = s^-2")
print(f"  [J_I_N] = s^-3 ✓")
print(f"  [J_source] = s^-3 (given) ✓")
print(f"  [σ_J²] = s^-6")
print(f"  [Θ] = s^-6 ✓")

# Final verdict based on Engine's calculation
print("\n" + "="*50)
print("ENGINE'S NUMERICAL EVALUATION VERDICT:")
print("="*50)
if not is_stable:
    print("RESULT: UNSTABLE (σ_J² > Θ)")
    print("  Informational jerk variance exceeds Shredding threshold.")
    print("  System is prone to runaway memory congestion.")
else:
    print("RESULT: STABLE (σ_J² < Θ)")
    print("  Informational jerk remains within stable bounds.")
print("="*50)