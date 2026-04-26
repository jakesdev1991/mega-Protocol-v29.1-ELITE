# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import numpy as np

# ----------------------------------------------------------------------
# Supplied audit data (normalized, I0 = 1)
# ----------------------------------------------------------------------
phi_N = 0.78          # Φ_N / I0
phi_D = 0.35          # Φ_Δ / I0
I0    = 1.0

# Time derivatives (s^-1)
dot_phi_N = 2.1e3
dot_phi_D = 8.7e3

# Stiffness invariant (s^-2)
xi_inv_sq = 4.2e6          # ξ⁻²
xi        = 1.0/np.sqrt(xi_inv_sq)   # characteristic time (s)

# Source jerk (s^-3)
J_source = 1.5e12

# Coupling constants (used in the thought's threshold)
lam   = 1.0e10   # λ (s^-2)
g_D   = 0.1      # g_Δ

# ----------------------------------------------------------------------
# Helper: Shannon entropy for two-state system
# ----------------------------------------------------------------------
def shannon_entropy(p):
    """p: array-like of probabilities (must sum to 1)"""
    p = np.asarray(p)
    # avoid log(0)
    p = np.clip(p, 1e-15, 1.0)
    return -np.sum(p * np.log(p))

# ----------------------------------------------------------------------
# Step 1: Probabilities and entropy
# ----------------------------------------------------------------------
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)
S_h = shannon_entropy([p_N, p_D])          # in nats (natural log)
# Convert to bits if desired: S_h_bits = S_h / np.log(2)
S_h_bits = S_h / np.log(2)

# Derivatives of S_h w.r.t. phi_N and phi_D (analytic for two-state)
# dS/dp_i = -ln(p_i) - 1
dS_dp_N = -np.log(p_N) - 1.0
dS_dp_D = -np.log(p_D) - 1.0

# dS/dψ = (dS/dphi_N)*(dphi_N/dpsi) + (dS/dphi_D)*(dphi_D/dpsi)
# Since psi = ln(phi_N) => dphi_N/dpsi = phi_N, dphi_D/dpsi = 0
dS_dpsi = dS_dp_N * phi_N

# Second derivative d²S/dψ²:
# d²S/dψ² = d/dpsi (dS/dpsi) = d/dphi_N(dS/dpsi)*phi_N
# dS/dpsi = phi_N * dS_dp_N
# derivative w.r.t phi_N:
# d/dphi_N (phi_N * dS_dp_N) = dS_dp_N + phi_N * d²S/dp_N²
# d²S/dp_N² = -1/p_N
d2S_dpN2 = -1.0 / p_N
d2S_dpsi2 = (dS_dp_N + phi_N * d2S_dpN2) * phi_N   # chain rule extra phi_N

# ----------------------------------------------------------------------
# Step 2: Time derivatives of psi
# ----------------------------------------------------------------------
psi = np.log(phi_N)                     # ln(Phi_N/I0)
dot_psi = dot_phi_N / phi_N             # dψ/dt = Φ̇_N / Φ_N

# Approximate ψ̈ using characteristic time ξ:
# ψ̈ ≈ ψ̇/ξ - ψ̇²   (derived from damped harmonic estimate)
ddot_psi = dot_psi / xi - dot_psi**2

# ----------------------------------------------------------------------
# Step 3: Internal jerk from chain-rule expression
# ----------------------------------------------------------------------
# The continuous third‑derivative (see thought) reduces, under the
# two‑state approximation and neglecting cross‑terms with Φ_Δ,
# to:   J_int ≈ 2 * (d²S/dψ²) * ψ̇ * ψ̈
J_int = 2.0 * d2S_dpsi2 * dot_psi * ddot_psi

# Total jerk (internal + source)
J_total = J_int + J_source

# ----------------------------------------------------------------------
# Step 4: Fluctuation variance (20% relative)
# ----------------------------------------------------------------------
sigma_J = 0.20 * np.abs(J_total)   # 20% fluctuation amplitude
sigma_J_sq = sigma_J**2

# ----------------------------------------------------------------------
# Step 5: Thresholds
# ----------------------------------------------------------------------
# 5A: Threshold as given in the thought (ad‑hoc factor)
psi_val = psi
exp2psi = np.exp(2.0*psi_val)
# V_shred = (lam/4)*( (2/3)*(exp2psi - 1) )**2
V_shred = (lam/4.0) * ( (2.0/3.0)*(exp2psi - 1.0) )**2
Theta_A = V_shred * (1.0 + (3.0*g_D**2)/(4.0*np.pi) * np.exp(-2.0*psi_val))

# 5B: Protocol‑consistent threshold from Omega Action:
# ξ_Δ⁻² = λ (Φ_N² + 3 Φ_Δ² - I₀²)
Phi_N = phi_N * I0
Phi_D = phi_D * I0
Theta_B = lam * (Phi_N**2 + 3.0*Phi_D**2 - I0**2)   # should be >0 for stability

# ----------------------------------------------------------------------
# Step 6: Stability decision
# ----------------------------------------------------------------------
stable_A = sigma_J_sq < Theta_A
stable_B = sigma_J_sq < Theta_B

# ----------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------
print("=== Informational Jerk Stability Audit ===")
print(f"ψ = ln(Φ_N/I0) = {psi:.6f}")
print(f"S_h (nats) = {S_h:.6f}  →  S_h (bits) = {S_h_bits:.6f}")
print(f"∂S/∂ψ = {dS_dpsi:.6f}")
print(f"∂²S/∂ψ² = {d2S_dpsi2:.6f}")
print(f"ψ̇ = {dot_psi:.3e} s⁻¹")
print(f"ψ̈ = {ddot_psi:.3e} s⁻²")
print(f"Internal jerk J_int = {J_int:.3e} s⁻³")
print(f"Source jerk J_source = {J_source:.3e} s⁻³")
print(f"Total jerk J_total = {J_total:.3e} s⁻³")
print(f"σ_J (20% rel.) = {sigma_J:.3e} s⁻³")
print(f"σ_J² = {sigma_J_sq:.3e} s⁻⁶")
print()
print("Threshold A (thought's ad‑hoc): Θ_A = {:.3e} s⁻⁶".format(Theta_A))
print("Threshold B (Omega‑Action):      Θ_B = {:.3e} s⁻⁶".format(Theta_B))
print()
print("Stability test (σ_J² < Θ)?")
print(f"  Using Θ_A : {'PASS' if stable_A else 'FAIL'}")
print(f"  Using Θ_B : {'PASS' if stable_B else 'FAIL'}")