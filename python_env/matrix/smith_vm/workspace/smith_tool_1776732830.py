# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ---- Supplied audit data ----
I0 = 1.0
phi_N = 0.78          # normalized Φ_N
phi_D = 0.35          # normalized Φ_Δ
psi = np.log(phi_N / I0)          # ψ = ln(Φ_N/I0)

# time derivatives (s^-1)
dot_phi_N = 2.1e3
dot_phi_D = 8.7e3

# stiffness invariant (s^-2)
xi_inv2 = 4.2e6
xi = 1.0 / np.sqrt(xi_inv2)       # s

# source jerk (s^-3)
J_source = 1.5e12

# ---- Entropy from two‑state model ----
p_N = phi_N / (phi_N + phi_D)
p_D = 1.0 - p_N
S_h = -(p_N * np.log(p_N) + p_D * np.log(p_D))   # nats (convert to bits if needed)
# derivatives w.r.t. psi (using chain rule d/dpsi = phi_N * d/dphi_N)
dS_dphi_N = -np.log(p_N / p_D)
dS_dpsi   = phi_N * dS_dphi_N
# second derivative approx (phi_N^2 * d2S/dphiN2 + phi_N * dS/dphiN)
# we approximate d2S/dphiN2 ~ -1/(p_N*p_D) (from binary entropy curvature)
d2S_dphiN2 = -1.0 / (p_N * p_D)
d2S_dpsi2  = phi_N**2 * d2S_dphiN2 + phi_N * dS_dphi_N

# ---- Jerk estimate (dominant term) ----
dot_psi = dot_phi_N / phi_N
# approximate psi double dot from characteristic time scale
ddot_psi = dot_psi / xi - dot_psi**2

J_est = 2.0 * d2S_dpsi2 * dot_psi * ddot_psi   # s^-3
J_total = J_est + J_source

# fluctuation (20% of total)
sigma_J = 0.2 * np.abs(J_total)
sigma_J2 = sigma_J**2

# ---- Stability threshold Θ(ψ) ----
lam = 1.0e10          # s^-2 (assumed)
g_D = 0.1
Theta = (lam * I0**4 / 9.0) * (np.exp(2*psi) - 1.0)**2 * \
        (1.0 + (3.0 * g_D**2) / (4.0 * np.pi) * np.exp(-2*psi))

# ---- Boundary checks ----
# Shredding: ξ_Δ → ∞  <=>  phi_N**2 + 3*phi_D**2 = I0**2
shred_cond = phi_N**2 + 3*phi_D**2 - I0**2
# Freeze: ξ_N → ∞  <=>  3*phi_N**2 + phi_D**2 = I0**2
freeze_cond = 3*phi_N**2 + phi_D**2 - I0**2

# ---- Output ----
print(f"ψ = {psi:.4f}")
print(f"S_h (nats) = {S_h:.4f}  ({S_h/np.log(2):.3f} bits)")
print(f"∂S/∂ψ = {dS_dpsi:.4f}, ∂²S/∂ψ² = {d2S_dpsi2:.4f}")
print(f"dot_ψ = {dot_psi:.2e} s⁻¹, ddot_ψ = {ddot_psi:.2e} s⁻²")
print(f"Estimated jerk term = {J_est:.2e} s⁻³")
print(f"Total jerk J_I = {J_total:.2e} s⁻³")
print(f"σ_J = {sigma_J:.2e} s⁻³ → σ_J² = {sigma_J2:.2e} s⁻⁶")
print(f"Threshold Θ(ψ) = {Theta:.2e} s⁻⁶")
print(f"Stability? σ_J² < Θ ? {sigma_J2 < Theta}")
print(f"Shredding condition (should be 0): {shred_cond:.4f}")
print(f"Freeze condition (should be 0):   {freeze_cond:.4f}")