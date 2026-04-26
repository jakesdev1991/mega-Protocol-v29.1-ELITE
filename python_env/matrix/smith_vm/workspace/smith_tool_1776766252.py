# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# Given normalized data
phi_N = 0.78
phi_D = 0.35
phi_dot_N = 2.1e3          # s^-1
phi_dot_D = 8.7e3          # s^-1
xi_inv_sq = 4.2e6          # s^-2  (stiffness inverse squared)
source_jerk = 1.5e12       # s^-3

# Derived timescale xi
xi = 1.0 / math.sqrt(xi_inv_sq)   # s
print(f"xi = {xi:.3e} s")

# Psi and its derivatives
psi = math.log(phi_N)
psi_dot = phi_dot_N / phi_N
# Approximate second derivative of phi_N using phi_ddot_N ≈ phi_dot_N / xi
phi_ddot_N = phi_dot_N / xi
psi_ddot = (phi_ddot_N / phi_N) - psi_dot**2
# Third derivative approximation: psi_dddot ≈ psi_ddot / xi
psi_dddot = psi_ddot / xi

print(f"psi = {psi:.6f}")
print(f"psi_dot = {psi_dot:.3e} s^-1")
print(f"psi_ddot = {psi_ddot:.3e} s^-2")
print(f"psi_dddot = {psi_dddot:.3e} s^-3")

# Delta derivatives (similar approximation)
phi_ddot_D = phi_dot_D / xi
phi_dddot_D = phi_ddot_D / xi
print(f"phi_ddot_D = {phi_ddot_D:.3e} s^-2")
print(f"phi_dddot_D = {phi_dddot_D:.3e} s^-3")

# Entropy and its derivatives w.r.t psi and phi_D
def compute_entropy_derivatives(psi_val, phi_D_val):
    e_psi = math.exp(psi_val)
    denom = e_psi + phi_D_val
    p_N = e_psi / denom
    p_D = phi_D_val / denom
    S = -(p_N * math.log(p_N) if p_N > 0 else 0.0 +
          p_D * math.log(p_D) if p_D > 0 else 0.0)
    # First derivatives
    dS_dpsi = -p_N * math.log(p_D / p_N) if p_N > 0 and p_D > 0 else 0.0
    dS_dphiD = -p_D * math.log(p_N / p_D) if p_N > 0 and p_D > 0 else 0.0
    # Second derivatives via finite difference
    eps = 1e-8
    # d2S/dpsi2
    psi_plus = psi_val + eps
    psi_minus = psi_val - eps
    def dS_dpsi_at(psi_at):
        e = math.exp(psi_at)
        den = e + phi_D_val
        pN = e / den
        pD = phi_D_val / den
        return -pN * math.log(pD / pN) if pN > 0 and pD > 0 else 0.0
    d2S_dpsi2 = (dS_dpsi_at(psi_plus) - dS_dpsi_at(psi_minus)) / (2*eps)
    # d2S/dphiD2
    phiD_plus = phi_D_val + eps
    phiD_minus = phi_D_val - eps
    def dS_dphiD_at(phiD_at):
        e = math.exp(psi_val)
        den = e + phiD_at
        pN = e / den
        pD = phiD_at / den
        return -pD * math.log(pN / pD) if pN > 0 and pD > 0 else 0.0
    d2S_dphiD2 = (dS_dphiD_at(phiD_plus) - dS_dphiD_at(phiD_minus)) / (2*eps)
    # Third derivatives via finite difference of second derivatives
    # d3S/dpsi3
    d2S_psi_plus = (dS_dpsi_at(psi_plus+eps) - dS_dpsi_at(psi_plus-eps)) / (2*eps)
    d2S_psi_minus = (dS_dpsi_at(psi_minus+eps) - dS_dpsi_at(psi_minus-eps)) / (2*eps)
    d3S_dpsi3 = (d2S_psi_plus - d2S_psi_minus) / (2*eps)
    # d3S/dphiD3
    d2S_phiD_plus = (dS_dphiD_at(phiD_plus+eps) - dS_dphiD_at(phiD_plus-eps)) / (2*eps)
    d2S_phiD_minus = (dS_dphiD_at(phiD_minus+eps) - dS_dphiD_at(phiD_minus-eps)) / (2*eps)
    d3S_dphiD3 = (d2S_phiD_plus - d2S_phiD_minus) / (2*eps)
    return {
        'S': S, 'p_N': p_N, 'p_D': p_D,
        'dS_dpsi': dS_dpsi, 'dS_dphiD': dS_dphiD,
        'd2S_dpsi2': d2S_dpsi2, 'd2S_dphiD2': d2S_dphiD2,
        'd3S_dpsi3': d3S_dpsi3, 'd3S_dphiD3': d3S_dphiD3
    }

derivs = compute_entropy_derivatives(psi, phi_D)
print("\nEntropy derivatives:")
for k, v in derivs.items():
    if isinstance(v, float):
        print(f"{k}: {v:.6e}")

# Jerk components
J_psi = (derivs['dS_dpsi'] * psi_dddot +
         3 * derivs['d2S_dpsi2'] * psi_dot * psi_ddot +
         derivs['d3S_dpsi3'] * psi_dot**3)
J_D = (derivs['dS_dphiD'] * phi_dddot_D +
       3 * derivs['d2S_dphiD2'] * phi_dot_D * phi_ddot_D +
       derivs['d3S_dphiD3'] * phi_dot_D**3)
J_total = J_psi + J_D + source_jerk

print("\nJerk components:")
print(f"J_psi = {J_psi:.3e} s^-3")
print(f"J_D   = {J_D:.3e} s^-3")
print(f"J_source = {source_jerk:.3e} s^-3")
print(f"J_total = {J_total:.3e} s^-3")

# Stability threshold
lam = xi_inv_sq  # lambda
I0 = 1.0  # normalized
threshold = (lam * I0**2 * math.exp(-psi))**3
print(f"\nThreshold Θ = (λ I0^2 e^{-ψ})^3 = {threshold:.3e} s^-6")

# Estimate variance of jerk (using square of total jerk as proxy)
sigma_J_sq = J_total**2
print(f"Estimated σ_𝒥² ≈ J_total^2 = {sigma_J_sq:.3e} s^-6")

# Dimensionless variance using natural scale ω_psi = ξ^{-1} e^{-ψ/2}
omega_psi = (1.0/xi) * math.exp(-psi/2)
omega_psi_cubed = omega_psi**3
omega_psi_sixth = omega_psi**6
dimless_var = sigma_J_sq / omega_psi_sixth
print(f"\nNatural jerk scale ω_ψ³ = {omega_psi_cubed:.3e} s^-3")
print(f"ω_ψ⁶ = {omega_psi_sixth:.3e} s^-6")
print(f"Dimensionless variance σ̃² = σ_𝒥² / ω_ψ⁶ = {dimless_var:.3f}")

# Compliance checks
tolerance = 1e-2  # 1% relative tolerance acceptable
def approx_equal(a, b, rel=tolerance):
    return math.isclose(a, b, rel_tol=rel, abs_tol=0.0)

# Expected values from the Engine's output (approx)
expected_psi = math.log(0.78)
expected_psi_dot = 2.69e3
expected_psi_ddot = -1.74e6
expected_psi_dddot = -3.55e9
expected_J_psi = 7.07e9
expected_J_D = -1.30e12
expected_J_total = 2.07e11
expected_threshold = 1.56e20
expected_sigma_J_sq = 1.71e21
expected_dimless_var = 11.5

checks = [
    ("psi", psi, expected_psi),
    ("psi_dot", psi_dot, expected_psi_dot),
    ("psi_ddot", psi_ddot, expected_psi_ddot),
    ("psi_dddot", psi_dddot, expected_psi_dddot),
    ("J_psi", J_psi, expected_J_psi),
    ("J_D", J_D, expected_J_D),
    ("J_total", J_total, expected_J_total),
    ("Threshold", threshold, expected_threshold),
    ("σ_𝒥²", sigma_J_sq, expected_sigma_J_sq),
    ("dimensionless variance", dimless_var, expected_dimless_var)
]

print("\nCompliance check (within 2% tolerance):")
all_ok = True
for name, val, exp in checks:
    ok = approx_equal(val, exp, rel=0.02)
    if not ok:
        all_ok = False
    print(f"{name}: computed {val:.3e}, expected {exp:.3e} -> {'PASS' if ok else 'FAIL'}")

if all_ok:
    print("\nOverall: MATHEMATICALLY SOUND AND COMPLIANT with Omega Protocol invariants.")
else:
    print("\nOverall: DISCREPANCIES DETECTED – review needed.")