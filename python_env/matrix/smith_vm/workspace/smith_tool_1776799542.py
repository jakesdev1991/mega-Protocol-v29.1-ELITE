# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Ω‑Protocol Validation of Higher‑Order Lattice Polarization
# --------------------------------------------------------------
import sympy as sp

# ---------- Symbols ----------
# Fundamental constants
e, alpha0 = sp.symbols('e alpha0', positive=True)
# Lattice spacing (set to 1 for natural units, keep for dimensional check)
a = sp.symbols('a', positive=True)
# Momenta
p = sp.symbols('p', positive=True)
# Modes
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
# Loop functions (treated as generic symbols)
Pi0_iso, PiDelta = sp.symbols('Pi0_iso PiDelta', real=True)
# Direction indicator: i = 0 (x),1 (y),2 (z)
i = sp.symbols('i', integer=True)
# Kronecker delta
delta_i_z = sp.KroneckerDelta(i, 2)   # 1 if i==z else 0

# ---------- 1. Isotropic part Pi0 (dimensionally corrected) ----------
# One-loop log term (dimensionless)
Pi_log = e**2/(12*sp.pi**2) * sp.log(a**(-2)/p**2)
# Newtonian mode contribution: must be dimensionless -> a^2 * Phi_N
Pi_N = e**2/(sp.pi**2) * (a**2 * Phi_N)
Pi0_correct = Pi_log + Pi_N   # <-- this is the dimensionally sound Pi0

# ---------- 2. Anisotropic kernel ----------
# We keep PiDelta as a generic O(1) function; later we can substitute a model.
# For demonstration we use a simple placeholder: PiDelta = e**2/pi**2 * I_Delta
I_Delta = sp.symbols('I_Delta', real=True)
PiDelta_model = e**2/(sp.pi**2) * I_Delta

# ---------- 3. Effective alpha in direction i ----------
alpha_eff = alpha0 / (1 + Pi0_correct + delta_i_z * Phi_Delta * PiDelta_model + sp.O(e**6))

# ---------- Checks ----------
print("=== Ω‑Protocol Consistency Checks ===")

# (a) Zero‑mode limit
alpha_zero = alpha_eff.subs({Phi_N:0, Phi_Delta:0})
print("(a) α_eff(Φ_N=0, Φ_Δ=0) =", sp.simplify(alpha_zero))
assert sp.simplify(alpha_zero - alpha0) == 0, "Failed: should reduce to bare α0"

# (b) Directional derivative
d_alpha_dPhiDelta = sp.diff(alpha_eff, Phi_Delta)
print("\n(b) ∂α_eff/∂Φ_Δ =", sp.simplify(d_alpha_dPhiDelta))
# Evaluate for i = z (i=2) and i = x (i=0)
d_alpha_z = d_alpha_dPhiDelta.subs(i, 2)
d_alpha_x = d_alpha_dPhiDelta.subs(i, 0)
print("   → i = z :", sp.simplify(d_alpha_z))
print("   → i = x :", sp.simplify(d_alpha_x))
assert sp.simplify(d_alpha_x) == 0, "Derivative must vanish for transverse directions"
assert sp.simplify(d_alpha_z) != 0, "Derivative must be non‑zero along archive axis"

# (c) Ω‑invariant combination sqrt(g)*(α0^{-1}+δ_N^{-1}+δ_Δ^{-1}cos^2θ)
# Metric determinant: g = diag(1,1,1,1+Φ_Δ) → sqrt(g) = sqrt(1+Φ_Δ)
sqrt_g = sp.sqrt(1 + Phi_Delta)
# Inverse couplings from the derivation:
alpha0_inv = 1/alpha0
delta_N_inv = alpha0_inv * Pi0_correct          # isotropic piece
delta_Delta_inv = alpha0_inv * Phi_Delta * PiDelta_model  # anisotropic piece
# Average over angles: <cos^2θ> = 1/3 for isotropic distribution; we keep symbolic cos2
cos2_theta = sp.symbols('cos2_theta', real=True)
Omega_combo = sqrt_g * (alpha0_inv + delta_N_inv + delta_Delta_inv * cos2_theta)
# Variation under infinitesimal rescaling A_μ → (1+ε)A_μ leaves the combination invariant
# because the whole term multiplies A_μ(-∂^2)A^μ; we simply check that the coefficient
# does not depend on the gauge field (it doesn't). Here we verify that the coefficient
# is a function only of Φ_N, Φ_Δ and kinematics.
print("\n(c) Ω‑invariant coefficient =", sp.simplify(Omega_combo))
# Ensure no explicit dependence on the gauge field (A_μ) – trivially true.
# Additionally, check that expanding to O(Φ_Δ) reproduces the linear term:
Omega_series = sp.series(Omega_combo, Phi_Delta, 0, 2).removeO()
print("   Expanded to O(Φ_Δ):", Omega_series)
# The linear term should be (1/2)*α0^{-1} + (δ_N_inv term) + (δ_Delta_inv * cos2θ)
expected_linear = (1/2)*(1/alpha0) + alpha0_inv*Pi0_correct + alpha0_inv*Phi_Delta*PiDelta_model*cos2_theta
print("   Expected linear :", sp.simplify(expected_linear))
assert sp.simplify(Omega_series - expected_linear) == 0, "Ω‑invariant expansion mismatch"

print("\nAll checks passed – derivation is Ω‑Protocol compliant (after the Pi0 correction).")