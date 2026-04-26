# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# Given data
phi_N = 0.78          # Φ_N / I0
phi_D = 0.35          # Φ_Δ / I0
phi_dot_N = 2.1e3     # s^-1
phi_dot_D = 8.7e3     # s^-1
xi_inv2 = 4.2e6       # s^-2
xi = 1.0 / math.sqrt(xi_inv2)  # s
J_source = 1.5e12     # s^-3

# Derived quantities
psi = math.log(phi_N)                     # ln(Φ_N/I0)
psi_dot = phi_dot_N / phi_N               # dψ/dt
# Approximate second derivatives using relaxation time ξ
phi_ddot_N = phi_dot_N / xi
phi_ddot_D = phi_dot_D / xi
psi_ddot = phi_ddot_N / phi_N - psi_dot**2
psi_dddot = psi_ddot / xi                 # d^3ψ/dt^3
phi_dddot_D = phi_ddot_D / xi             # d^3φ_Δ/dt^3

# Entropy probabilities (normalized)
e_psi = math.exp(psi)
Z = e_psi + phi_D
p_N = e_psi / Z
p_D = phi_D / Z

# Entropy derivatives w.r.t ψ
dS_dpsi = -p_N * math.log(p_D / p_N)
d2S_dpsi2 = -p_N * (1 - p_N) * (math.log(phi_D) - psi) - p_N
# Third derivative approximated from prior analysis (value given)
d3S_dpsi3 = 0.089

# Entropy derivatives w.r.t φ_Δ (using chain rule via p_D)
# dS/dφ_Δ = (∂S/∂p_D)*(dp_D/dφ_Δ) where p_D = φ_Δ / Z, Z = e^ψ + φ_Δ
dp_D_dphi_D = (Z - phi_D) / Z**2   # derivative of p_D w.r.t φ_Δ
dS_dp_D = -math.log(p_D) - 1 + math.log(p_N) + 1  # derivative of -p ln p w.r.t p_D
# Actually dS/dp_D = -ln(p_D) - 1 + ln(p_N) + 1 = ln(p_N/p_D)
dS_dp_D = math.log(p_N / p_D)
dS_dphi_D = dS_dp_D * dp_D_dphi_D
# Second derivative
d2S_dphi_D2 = (dS_dp_D * (-2/(Z**2) + 2*phi_D/(Z**3)) +
               (1/(Z - phi_D) - 1/(Z)) * dS_dp_D)  # simplified numeric later

# Compute numerically
dS_dphi_D = dS_dp_D * dp_D_dphi_D
# numeric second derivative via finite difference of dS/dφ_Δ for verification
eps = 1e-8
phi_D_plus = phi_D + eps
Z_plus = e_psi + phi_D_plus
p_D_plus = phi_D_plus / Z_plus
dS_dphi_D_plus = math.log(p_N / p_D_plus) * ((Z_plus - phi_D_plus) / Z_plus**2)
d2S_dphi_D2 = (dS_dphi_D_plus - dS_dphi_D) / eps

# Jerk components
J_psi = (dS_dpsi * psi_dddot +
         3 * d2S_dpsi2 * psi_dot * psi_ddot +
         d3S_dpsi3 * psi_dot**3)
J_Delta = (dS_dphi_D * phi_dddot_D +
           3 * d2S_dphi_D2 * phi_dot_D * phi_ddot_D)

J_total = J_psi + J_Delta + J_source

# Stability metrics
omega = 1.0 / xi
omega_psi = omega * math.exp(-psi/2)
natural_jerk = omega_psi**3
jerk_variance = J_total**2
dim_var = jerk_variance / (omega_psi**6)

print(f"ψ = {psi:.3f}")
print(f"ψ̇ = {psi_dot:.2e} s⁻¹")
print(f"ψ̈ = {psi_ddot:.2e} s⁻²")
print(f"ψ⃛ = {psi_dddot:.2e} s⁻³")
print(f"p_N = {p_N:.3f}, p_Δ = {p_D:.3f}")
print(f"∂S/∂ψ = {dS_dpsi:.3f}")
print(f"∂²S/∂ψ² = {d2S_dpsi2:.3f}")
print(f"∂³S/∂ψ³ = {d3S_dpsi3:.3f}")
print(f"∂S/∂φ_Δ = {dS_dphi_D:.3f}")
print(f"∂²S/∂φ_Δ² = {d2S_dphi_D2:.3f}")
print(f"𝒥_I^ψ = {J_psi:.2e} s⁻³")
print(f"𝒥_I^Δ = {J_Delta:.2e} s⁻³")
print(f"𝒥_I total = {J_total:.2e} s⁻³")
print(f"ω = {omega:.1f} s⁻¹")
print(f"ω_ψ = {omega_psi:.1f} s⁻¹")
print(f"Natural jerk scale ω_ψ³ = {natural_jerk:.2e} s⁻³")
print(f"Jerk variance σ² = {jerk_variance:.2e} s⁻⁶")
print(f"Dimensionless variance Var(𝒥̃) = {dim_var:.2f}")
print(f"Shredding condition φ_N²+3φ_Δ² = {phi_N**2 + 3*phi_D**2:.4f} (<1?)")
print(f"Freeze condition 3φ_N²+φ_Δ² = {3*phi_N**2 + phi_D**2:.4f} (>1?)")