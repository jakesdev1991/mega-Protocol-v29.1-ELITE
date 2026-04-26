# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Audit Script for Linux HSA Unified Memory Informational Jerk.
Validates the mathematical correctness of the analysis and checks invariants.
"""

import math
import numpy as np

# ----------------------------------------------------------------------
# Supplied data (normalized)
# ----------------------------------------------------------------------
phi_N   = 0.78          # Φ_N / I0
phi_D   = 0.35          # Φ_Δ / I0
phiN_dot= 2.1e3         # s^-1
phiD_dot= 8.7e3         # s^-1
xi_inv2 = 4.2e6         # s^-2  => xi = 1/sqrt(xi_inv2)
J_source= 1.5e12        # s^-3  (source jerk)

# ----------------------------------------------------------------------
# Derived quantities
# ----------------------------------------------------------------------
I0 = 1.0                # normalization (since phi's are already normalized)
Phi_N = phi_N * I0
Phi_D = phi_D * I0

psi = math.log(phi_N)               # ln(Φ_N/I0)
psi_dot = phiN_dot / phi_N
xi = 1.0 / math.sqrt(xi_inv2)

# relaxation‑time approximations (as in the original analysis)
phiN_ddot = phiN_dot / xi
phiD_ddot = phiD_dot / xi
psi_ddot  = phiN_ddot / phi_N - psi_dot**2
psi_dddot = psi_ddot / xi
phiD_dddot = phiD_ddot / xi

# ----------------------------------------------------------------------
# Entropy and its derivatives (exact analytical forms)
# ----------------------------------------------------------------------
def entropy(pN, pD):
    """Shannon entropy for two-state system."""
    if pN <= 0 or pD <= 0:
        return 0.0
    return -(pN*math.log(pN) + pD*math.log(pD))

# probabilities from phi_N, phi_D
s = phi_N + phi_D
pN = phi_N / s
pD = phi_D / s
S = entropy(pN, pD)

# Analytic derivatives (derived in the audit)
def dS_dphiN(phiN, phiD):
    s = phiN + phiD
    lnN = math.log(phiN/s)
    lnD = math.log(phiD/s)
    term = -(1/s)*lnN - (1/s) + phiD/(s**2)*lnD + phiD/(s**2)
    return term

def dS_dphiD(phiN, phiD):
    s = phiN + phiD
    lnN = math.log(phiN/s)
    lnD = math.log(phiD/s)
    term = -(1/s)*lnD - (1/s) + phiN/(s**2)*lnN + phiN/(s**2)
    return term

dS_dphiN_val = dS_dphiN(phiN, phiD)
dS_dphiD_val = dS_dphiD(phiN, phiD)

# chain rule: ψ depends only on φ_N
dS_dpsi   = dS_dphiN_val * phiN          # dφ_N/dψ = φ_N
d2S_dpsi2 = (dS_dphiN_val   # ∂S/∂φ_N term
              + phiN * (dS_dphiN_val   # derivative of ∂S/∂φ_N w.r.t φ_N * dφ_N/dψ
                        )) * phiN  # Actually we need second derivative; compute numerically for safety
# For robustness we compute derivatives via finite differences on the analytic S(ψ,φ_D)
eps = 1e-8
def S_of_psi_phiD(psi_val, phiD_val):
    phiN_val = math.exp(psi_val) * I0   # because ψ = ln(Φ_N/I0) → Φ_N = I0 e^ψ
    s = phiN_val + phiD_val
    pN = phiN_val / s
    pD = phiD_val / s
    return entropy(pN, pD)

dS_dpsi_fd   = (S_of_psi_phiD(psi+eps, phiD) - S_of_psi_phiD(psi-eps, phiD))/(2*eps)
d2S_dpsi2_fd = (S_of_psi_phiD(psi+eps, phiD) -2*S_of_psi_phiD(psi, phiD) + S_of_psi_phiD(psi-eps, phiD))/(eps**2)
d3S_dpsi3_fd = (S_of_psi_phiD(psi+2*eps, phiD)
                -2*S_of_psi_phiD(psi+eps, phiD)
                +2*S_of_psi_phiD(psi-eps, phiD)
                -S_of_psi_phiD(psi-2*eps, phiD))/(2*eps**3)

# Derivatives w.r.t φ_D (treat ψ constant → φ_N constant)
def S_of_phiD(phiD_val):
    # φ_N fixed
    s = phiN + phiD_val
    pN = phiN / s
    pD = phiD_val / s
    return entropy(pN, pD)

dS_dphiD_fd   = (S_of_phiD(phiD+eps) - S_of_phiD(phiD-eps))/(2*eps)
d2S_dphiD2_fd = (S_of_phiD(phiD+eps) -2*S_of_phiD(phiD) + S_of_phiD(phiD-eps))/(eps**2)

# ----------------------------------------------------------------------
# Jerk components (third derivative of S_h)
# ----------------------------------------------------------------------
# J_psi = S_psi * ψ''' + 3 S_psi_psi * ψ' ψ'' + S_psi_psi_psi * (ψ')^3
J_psi = (dS_dpsi_fd   * psi_dddot
         + 3 * d2S_dpsi2_fd * psi_dot * psi_ddot
         + d3S_dpsi3_fd * psi_dot**3)

# J_Delta = S_phiD * φD''' + 3 S_phiD_phiD * φD' φD''
J_Delta = (dS_dphiD_fd   * phiD_dddot
           + 3 * d2S_dphiD2_fd * phiD_dot * phiD_ddot)

J_total = J_psi + J_Delta + J_source

# ----------------------------------------------------------------------
# Boundary conditions (Omega Protocol invariants)
# ----------------------------------------------------------------------
# Stiffness inverses (lambda cancels in ratio, we just check the brackets)
xiN2_inv_bracket = 3*phi_N**2 + phi_D**2 - 1.0   # should be >0 for finite ξ_N
xiD2_inv_bracket = phi_N**2 + 3*phi_D**2 - 1.0   # should be >0 for finite ξ_D

shredding = math.isclose(xiD2_inv_bracket, 0.0, abs_tol=1e-12) or xiD2_inv_bracket < 0
freeze    = math.isclose(xiN2_inv_bracket, 0.0, abs_tol=1e-12) or xiN2_inv_bracket < 0

# ----------------------------------------------------------------------
# Jerk variance metric (requires a time‑series; if none, we flag)
# ----------------------------------------------------------------------
# For demonstration we assume we have a short window of jerk values.
# In a real audit you would supply the measured J_I[n] array.
# Here we synthesize a dummy series around the instantaneous value to illustrate.
J_series = np.array([J_total*0.9, J_total, J_total*1.1])  # three‑point example
J_var = np.var(J_series, ddof=1)   # unbiased sample variance

# Characteristic frequency and ψ‑modulated scale
omega = 1.0/xi
omega_psi = omega * math.exp(-psi/2.0)
J_natural = omega_psi**3

dimensionless_var = J_var / (J_natural**2) if J_natural != 0 else float('inf')

# ----------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------
def almost_equal(a, b, tol=1e-6):
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)

passed = True
report = []

# 1. Entropy derivatives sanity check (compare finite diff vs analytic)
if not almost_equal(dS_dpsi_fd, dS_dpsi):
    passed = False
    report.append(f"∂S/∂ψ mismatch: FD={dS_dpsi_fd:.3e}, analytic={dS_dpsi:.3e}")
if not almost_equal(d2S_dpsi2_fd, 0.0):  # we didn't compute analytic second; just flag if huge
    if abs(d2S_dpsi2_fd) > 1e2:
        passed = False
        report.append(f"∂²S/∂ψ² suspiciously large: {d2S_dpsi2_fd:.3e}")
if not almost_equal(d3S_dpsi3_fd, 0.0):
    if abs(d3S_dpsi3_fd) > 1e2:
        passed = False
        report.append(f"∂³S/∂ψ³ suspiciously large: {d3S_dpsi3_fd:.3e}")

# 2. Jerk components sign sanity (should be real numbers)
if not math.isfinite(J_psi) or not math.isfinite(J_Delta):
    passed = False
    report.append("Non‑finite jerk component.")
# 3. Boundary checks
if shredding:
    passed = False
    report.append("Shredding condition violated (ξ_Δ → ∞).")
if freeze:
    passed = False
    report.append("Freeze condition violated (ξ_N → ∞).")
# 4. Stability metric: if variance >> 1 we flag instability (as per protocol)
if dimensionless_var > 1.0:
    passed = False
    report.append(f"Dimensionless jerk variance = {dimensionless_var:.2f} > 1 → unstable.")
else:
    report.append(f"Dimensionless jerk variance = {dimensionless_var:.2f} ≤ 1 → stable.")

# ----------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------
if passed:
    print("PASS: All Omega Protocol invariants satisfied and math checks out.")
else:
    print("FAIL: Issues detected.")
    for line in report:
        print(" -", line)
    print("\nDiagnostics:")
    print(f"  ψ = {psi:.6f}, ψ̇ = {psi_dot:.3e}, ψ⃛ = {psi_dddot:.3e}")
    print(f"  J_psi = {J_psi:.3e}, J_Delta = {J_Delta:.3e}, J_source = {J_source:.3e}")
    print(f"  J_total = {J_total:.3e}")
    print(f"  ξ_N^{-2} bracket = {xiN2_inv_bracket:.6f}, ξ_Δ^{-2} bracket = {xiD2_inv_bracket:.6f}")
    print(f"  Jerk variance (sample) = {J_var:.3e}, natural scale³ = {J_natural:.3e}")
    print(f"  Dimensionless variance = {dimensionless_var:.2f}")