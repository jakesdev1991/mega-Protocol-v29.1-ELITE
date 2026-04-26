# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation of the Informational Jerk stability analysis
as presented in the engine output.

The script reproduces the numeric steps and evaluates:
    sigma_J^2 < Theta(psi)   -> Stable
    otherwise                -> Unstable

It also prints the computed Informational Freeze boundary
for completeness (though the original analysis omitted it).
"""

import math

# ----------------------------------------------------------------------
# Supplied data (normalized to I0 = 1)
# ----------------------------------------------------------------------
I0 = 1.0
phi_N = 0.78          # Normalized Newtonian mode
phi_D = 0.35          # Normalized Archive mode

# Derived quantities
psi = math.log(phi_N / I0)          # ψ = ln(Φ_N / I0)
print(f"ψ = ln(Φ_N/I0) = {psi:.6f}")

# Time derivatives (s^-1)
dot_phi_N = 2.1e3
dot_phi_D = 8.7e3

# Stiffness invariant (s^-2)
xi_inv_sq = 4.2e6
xi = 1.0 / math.sqrt(xi_inv_sq)    # characteristic time scale (s)
print(f"ξ = 1/√(ξ⁻²) = {xi:.6e} s")

# Source jerk (s^-3)
J_source = 1.5e12

# ----------------------------------------------------------------------
# Entropy and its derivatives (two‑state model)
# ----------------------------------------------------------------------
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)
S_h = -p_N * math.log(p_N) - p_D * math.log(p_D)   # Shannon entropy (nats)
print(f"S_h = {S_h:.6f} nats ({S_h/math.log(2):.6f} bits)")

# dS_h/dφ_N and dS_h/dφ_D for two‑state system
# S_h = -p_N ln p_N - p_D ln p_D,  p_N = φ_N/(φ_N+φ_D)
# Derivative w.r.t φ_N:
dS_dphiN = -math.log(p_N) + math.log(p_D)   # = -ln(p_N/p_D)
dS_dphiD = -math.log(p_D) + math.log(p_N)   # = -ln(p_D/p_N) = -dS_dphiN
print(f"∂S_h/∂Φ_N = {dS_dphiN:.6f}, ∂S_h/∂Φ_Δ = {dS_dphiD:.6f}")

# Chain‑rule conversion to ψ (ψ = ln φ_N, I0=1)
# dψ/dt = (dot_phi_N)/phi_N
dot_psi = dot_phi_N / phi_N
print(f"ψ̇ = Φ̇_N/Φ_N = {dot_psi:.6e} s⁻¹")

# ∂S_h/∂ψ = (∂S_h/∂φ_N) * (∂φ_N/∂ψ) = (∂S_h/∂φ_N) * φ_N
dS_dpsi = dS_dphiN * phi_N
print(f"∂S_h/∂ψ = {dS_dpsi:.6f}")

# ∂²S_h/∂ψ² = φ_N² * (∂²S_h/∂φ_N²) + φ_N * (∂S_h/∂φ_N)
# For two‑state: ∂²S_h/∂φ_N² = 1/(φ_N) + 1/(φ_D)
d2S_dphiN2 = 1.0/phi_N + 1.0/phi_D
d2S_dpsi2 = (phi_N**2) * d2S_dphiN2 + phi_N * dS_dphiN
print(f"∂²S_h/∂ψ² = {d2S_dpsi2:.6f}")

# ----------------------------------------------------------------------
# Estimate ψ̈ using characteristic time ξ
# ψ̈ ≈ ψ̇/ξ - ψ̇²
# ----------------------------------------------------------------------
psi_ddot = dot_psi / xi - dot_psi**2
print(f"ψ̈ ≈ ψ̇/ξ - ψ̇² = {psi_ddot:.6e} s⁻²")

# ----------------------------------------------------------------------
# Dominant jerk term: d/dt[ (∂²S_h/∂ψ²) ψ̇² ] ≈ 2 (∂²S_h/∂ψ²) ψ̇ ψ̈
# ----------------------------------------------------------------------
J_psi = 2.0 * d2S_dpsi2 * dot_psi * psi_ddot
print(f"Jerk from ψ‑term ≈ 2·∂²S_h/∂ψ²·ψ̇·ψ̈ = {J_psi:.6e} s⁻³")

# Total informational jerk (add source)
J_total = J_psi + J_source
print(f"Total 𝒥_I = 𝒥_ψ + 𝒥_source = {J_total:.6e} s⁻³")

# ----------------------------------------------------------------------
# Fluctuation estimate (±20%)
# ----------------------------------------------------------------------
sigma_J = 0.20 * abs(J_total)   # 20% fluctuation amplitude
sigma_J_sq = sigma_J**2
print(f"σ_𝒥 ≈ 20%·|𝒥_I| = {sigma_J:.6e} s⁻³")
print(f"σ_𝒥² = {sigma_J_sq:.6e} s⁻⁶")

# ----------------------------------------------------------------------
# Threshold Θ(ψ)  (using λ ≈ 1e10 s⁻², g_Δ ≈ 0.1)
# ----------------------------------------------------------------------
lam = 1.0e10          # s⁻²
g_Delta = 0.1

# Shredding boundary: Φ_N² + 3Φ_Δ² = I0²
# Solve for Φ_Δ² at boundary:
phi_D_sq_shred = (I0**2 - phi_N**2) / 3.0
print(f"Φ_Δ² at Shredding boundary = {phi_D_sq_shred:.6f}")

# Potential at shredding:
V_shred = (lam/4.0) * ((phi_N**2 + 3*phi_D_sq_shred - I0**2)**2)
# Since the bracket is zero by construction, V_shred = 0; we use the
# expression derived in the analysis:
V_shred_alt = (lam * I0**4 / 9.0) * (math.exp(2*psi) - 1)**2
print(f"V_shred (ψ‑dependent form) = {V_shred_alt:.6e}")

# Threshold:
Theta = (lam * I0**4 / 9.0) * (math.exp(2*psi) - 1)**2 * \
        (1.0 + (3.0 * g_Delta**2) / (4.0 * math.pi) * math.exp(-2*psi))
print(f"Θ(ψ) = {Theta:.6e} s⁻⁶")

# ----------------------------------------------------------------------
# Stability decision
# ----------------------------------------------------------------------
stable = sigma_J_sq < Theta
print(f"\nStability check: σ_𝒥² ({sigma_J_sq:.6e}) < Θ ({Theta:.6e}) ?")
print(f"Result: {'STABLE' if stable else 'UNSTABLE'}")

# ----------------------------------------------------------------------
# Informational Freeze boundary (missing in original)
# Freeze occurs when Φ_Δ saturates at its maximal allowed value Λ_Δ.
# For illustration, assume Λ_Δ = I0 (i.e., Φ_Δ cannot exceed I0).
# Then the freeze condition is Φ_Δ = Λ_Δ = I0.
# ----------------------------------------------------------------------
Lambda_Delta = I0   # placeholder; actual value would be model‑dependent
print(f"\nInformational Freeze boundary (Φ_Δ = Λ_Δ) = {Lambda_Delta:.6f}")
print(f"Current Φ_Δ = {phi_D:.6f} → {'Below' if phi_D < Lambda_Delta else 'At/Above'} freeze limit.")