# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# ---- Supplied audit data ----
phi_N   = 0.78          # normalized Newtonian mode
phi_D   = 0.35          # normalized Archive mode
I0      = 1.0
dot_phi_N = 2.1e3       # s^-1
dot_phi_D = 8.7e3       # s^-1
xi_inv2 = 4.2e6         # s^-2  (xi^{-2})
J_source = 1.5e12       # s^-3
lam     = 1.0e10        # s^-2  (coupling lambda)
g_D     = 0.1           # Archive mode coupling

# ---- Derived quantities ----
psi = math.log(phi_N / I0)                     # metric coupling invariant
dot_psi = dot_phi_N / phi_N                    # dψ/dt
xi = 1.0 / math.sqrt(xi_inv2)                  # correlation time

# Approximate second derivative of ψ (using characteristic time)
ddot_psi = dot_psi / xi - dot_psi**2

# Entropy derivatives (two‑state model)
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)
S_h = -p_N*math.log(p_N) - p_D*math.log(p_D)   # nats (convert to bits if needed)
# dS_h/dψ ≈ φ_N * ∂S_h/∂φ_N ; using ∂S_h/∂φ_N = -ln(p_N/p_D)
dS_dpsi = phi_N * (-math.log(p_N/p_D))
# d²S_h/dψ² ≈ φ_N² * ∂²S_h/∂φ_N² + φ_N * ∂S_h/∂φ_N
# ∂²S_h/∂φ_N² ≈ -(1/p_N + 1/p_D)  (for binary distribution)
d2S_dpsi2 = phi_N**2 * (-(1/p_N + 1/p_D)) + phi_N * (-math.log(p_N/p_D))

# Dominant jerk term from ψ‑sector
J_psi = 2 * d2S_dpsi2 * dot_psi * ddot_psi   # s^-3
J_total = J_psi + J_source                  # s^-3

# Fluctuation estimate (±20%)
sigma_J = 0.2 * abs(J_total)
sigma_J2 = sigma_J**2                       # s^-6

# Stability threshold Θ(ψ)
exp2psi = math.exp(2*psi)
Theta = (lam * I0**4 / 9.0) * (exp2psi - 1.0)**2 * (1.0 + (3.0*g_D**2)/(4.0*math.pi) * math.exp(-2*psi))

# Boundary conditions
shredding_cond = phi_N**2 + 3.0*phi_D**2 - I0**2   # =0 at ξ_Δ→∞
freeze_cond    = 3.0*phi_N**2 + phi_D**2 - I0**2   # =0 at ξ_N→∞

# ---- Output results ----
print(f"ψ = {psi:.6f}")
print(f"dot_ψ = {dot_psi:.3e} s⁻¹")
print(f"ddot_ψ = {ddot_psi:.3e} s⁻²")
print(f"S_h (nats) = {S_h:.4f}  ({S_h/math.log(2):.4f} bits)")
print(f"∂S_h/∂ψ = {dS_dpsi:.4f}")
print(f"∂²S_h/∂ψ² = {d2S_dpsi2:.4f}")
print(f"J_ψ = {J_psi:.3e} s⁻³")
print(f"J_total (incl. source) = {J_total:.3e} s⁻³")
print(f"σ_J = {sigma_J:.3e} s⁻³  → σ_J² = {sigma_J2:.3e} s⁻⁶")
print(f"Θ(ψ) = {Theta:.3e} s⁻⁶")
print(f"Stability check (σ_J² < Θ)? {sigma_J2 < Theta}")
print(f"Shredding condition (3Φ_N²+Φ_Δ²-I₀²) = {shredding_cond:.6f} (zero → shredding)")
print(f"Freeze condition    (Φ_N²+3Φ_Δ²-I₀²) = {freeze_cond:.6f} (zero → freeze)")