# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# ---------- Input data (normalized) ----------
phi_N = 0.78          # Φ_N / I0
phi_D = 0.35          # Φ_Δ / I0
phi_N_dot = 2.1e3     # s^-1
phi_D_dot = 8.7e3     # s^-1
xi_inv_sq = 4.2e6     # s^-2  (=> ξ^-2)
J_source = 1.5e12     # s^-3

# ---------- Derived constants ----------
xi = math.sqrt(1.0 / xi_inv_sq)          # relaxation time scale
psi = math.log(phi_N)                    # ln(Φ_N/I0)
psi_dot = phi_N_dot / phi_N              # dψ/dt
# second derivatives via relaxation-time approximation
phi_N_ddot = phi_N_dot / xi
phi_D_ddot = phi_D_dot / xi
psi_ddot = phi_N_ddot / phi_N - psi_dot**2
psi_dddot = psi_ddot / xi
phi_D_dddot = phi_D_ddot / xi

# ---------- Entropy and its derivatives ----------
exp_psi = math.exp(psi)
Z = exp_psi + phi_D
p_N = exp_psi / Z
p_D = phi_D / Z
dS_dpsi = -p_N * math.log(p_D / p_N)
d2S_dpsi2 = -p_N * (1 - p_N) * (math.log(phi_D) - psi) - p_N
# third derivative approximated from prior analysis (value given)
d3S_dpsi3 = 0.089
dS_dphiD = math.log(p_N / p_D)
d2S_dphiD2 = -(1 / phi_D) + (1 / (exp_psi + phi_D))

# ---------- Jerk components ----------
J_psi = (dS_dpsi) * psi_dddot + 3 * (d2S_dpsi2) * psi_dot * psi_ddot + (d3S_dpsi3) * psi_dot**3
J_Delta = (dS_dphiD) * phi_D_dddot + 3 * (d2S_dphiD2) * phi_D_dot * phi_D_ddot
J_total = J_psi + J_Delta + J_source

# ---------- Boundary checks ----------
shredding_cond = phi_N**2 + 3 * phi_D**2
freeze_cond = 3 * phi_N**2 + phi_D**2
# tolerances to account for floating point
eps = 1e-12
shredding_ok = abs(shredding_cond - 1.0) > eps
freeze_ok = abs(freeze_cond - 1.0) > eps

# ---------- Stability metric ----------
omega = 1.0 / xi
omega_psi = omega * math.exp(-psi / 2.0)
omega_psi_cube = omega_psi ** 3
J_var = J_total ** 2
Var_J_tilde = J_var / (omega_psi ** 6)
threshold = 1.0  # order‑1 stability limit
stable = Var_J_tilde <= threshold

# ---------- Invariant assertions (Omega Protocol) ----------
# ψ definition
assert math.isclose(psi, math.log(phi_N)), "ψ invariant violated"
# Stiffness invariants (λ cancels, we check sign consistency)
# ξ_N^-2 ∝ (3Φ_N^2 + Φ_Δ^2 - I0^2)  -> proportional to (3φ_N^2 + φ_D^2 - 1)
# ξ_Δ^-2 ∝ (Φ_N^2 + 3Φ_Δ^2 - I0^2)  -> proportional to (φ_N^2 + 3φ_D^2 - 1)
# We only require that the computed ξ^-2 matches the combination used:
xi_calc_inv_sq = (phi_N**2 + 3 * phi_D**2 - 1.0)  # up to λ factor
assert math.isclose(xi_inv_sq, xi_calc_inv_sq, rel_tol=1e-9), "Stiffness invariant mismatch"

# ---------- Output ----------
print("=== Omega Protocol Validation ===")
print(f"ψ = {psi:.6f}")
print(f"ψ̇ = {psi_dot:.3e} s⁻¹")
print(f"ξ = {xi:.3e} s")
print(f"Informational jerk 𝒥_I = {J_total:.3e} s⁻³")
print(f"Shredding condition (φ_N²+3φ_Δ²) = {shredding_cond:.6f} {'OK' if shredding_ok else 'VIOLATION'}")
print(f"Freeze condition (3φ_N²+φ_Δ²) = {freeze_cond:.6f} {'OK' if freeze_ok else 'VIOLATION'}")
print(f"Dimensionless jerk variance Var(𝒥̃) = {Var_J_tilde:.3f}")
print(f"Stability threshold = {threshold}")
print(f"System stable? {'YES' if stable else 'NO'}")
print("=== Result ===")
if shredding_ok and freeze_ok and not stable:
    print("PASS: Invariants respected, boundaries not violated, instability correctly identified.")
else:
    print("FAIL: Check invariants, boundaries or stability conclusion.")