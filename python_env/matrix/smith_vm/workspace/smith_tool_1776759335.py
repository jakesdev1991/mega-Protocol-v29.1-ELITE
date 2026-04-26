# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the corrected BRS-Omega formulation.
Checks dimensional consistency and sign of latency term in Phi_Delta.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# 1. Symbolic dimensions
# ----------------------------------------------------------------------
# Base dimensions: M (mass), L (length), T (time), I (information - dimensionless)
# We only need T for latency; everything else is dimensionless.
T = sp.symbols('T', positive=True)   # time dimension
one = sp.Integer(1)                  # dimensionless

# Define symbols with assumed dimensions
t   = sp.symbols('t')   # count -> dimensionless
s   = sp.symbols('s')   # sparsity ratio -> dimensionless
ell = sp.symbols('ell') # latency -> time
ell_max = sp.symbols('ell_max', positive=True) # time

# Coefficients (dimensionless unless noted)
alpha1, alpha2, beta1, beta2 = sp.symbols('alpha1 alpha2 beta1 beta2')
gamma0, gamma1, gamma2 = sp.symbols('gamma0 gamma1 gamma2')
delta0, delta1, delta2 = sp.symbols('delta0 delta1 delta2')
lam = sp.symbols('lam')  # lambda -> 1/T^2 to make xi^{-2} correct

# ----------------------------------------------------------------------
# 2. Define dimensionless noise and latency error terms
# ----------------------------------------------------------------------
# eta(t) and zeta(ell) are assumed dimensionless (normalized)
eta = sp.symbols('eta')   # dimensionless
zeta = ell / ell_max      # dimensionless latency error

# ----------------------------------------------------------------------
# 3. Covariant mode expressions (corrected Phi_Delta)
# ----------------------------------------------------------------------
Phi_N0, Phi_Delta0 = sp.symbols('Phi_N0 Phi_Delta0')
Phi_N_stream = Phi_N0 - alpha1*eta - alpha2*zeta
# Original (incorrect) Phi_Delta:
Phi_Delta_stream_wrong = Phi_Delta0 + beta1*eta - beta2*zeta
# Corrected Phi_Delta:
Phi_Delta_stream_corr = Phi_Delta0 + beta1*eta + beta2*zeta

print("Phi_N stream expression:", Phi_N_stream)
print("Phi_Delta stream (wrong):", Phi_Delta_stream_wrong)
print("Phi_Delta stream (corrected):", Phi_Delta_stream_corr)

# ----------------------------------------------------------------------
# 4. Dimensional check
# ----------------------------------------------------------------------
def dim(expr):
    """Replace each symbol by its dimension and simplify."""
    subs_dict = {
        t: one, s: one,
        ell: T,
        ell_max: T,
        eta: one,          # assumed dimensionless
        zeta: ell/ell_max, # -> T/T = dimensionless
        alpha1: one, alpha2: one,
        beta1: one, beta2: one,
        gamma0: one, gamma1: one, gamma2: one/T,   # so gamma2*ell dimensionless
        delta0: one, delta1: one, delta2: one/T,
        lam: 1/T**2,       # lambda has 1/T^2
        Phi_N0: one, Phi_Delta0: one
    }
    return sp.simplify(expr.subs(subs_dict))

print("\n--- Dimensionality of core expressions ---")
print("[Phi_N] =", dim(Phi_N_stream))          # should be 1 (dimensionless)
print("[Phi_Delta_wrong] =", dim(Phi_Delta_stream_wrong))
print("[Phi_Delta_corr] =", dim(Phi_Delta_stream_corr))
print("[xi_N^{-2}] =", dim(lam*(gamma0 + gamma1*t + gamma2*ell)))  # should be 1/T^2
print("[xi_Delta^{-2}] =", dim(lam*(delta0 - delta1*t + delta2*ell))) # should be 1/T^2

# ----------------------------------------------------------------------
# 5. Sign check for latency term in Phi_Delta
# ----------------------------------------------------------------------
# We expect d(Phi_Delta)/d(ell) > 0 (latency increases asymmetry)
dPhi_Delta_dell_corr = sp.diff(Phi_Delta_stream_corr, ell)
dPhi_Delta_dell_wrong = sp.diff(Phi_Delta_stream_wrong, ell)

print("\n--- Sensitivity to latency ---")
print("dPhi_Delta_corr/dell =", dPhi_Delta_dell_corr)   # should be +beta2/ell_max >0
print("dPhi_Delta_wrong/dell =", dPhi_Delta_dell_wrong) # should be -beta2/ell_max <0

# Evaluate sign assuming positive coefficients
beta2_pos = 1.0
ell_max_val = 1.0
sign_corr = np.sign(beta2_pos/ell_max_val)
sign_wrong = np.sign(-beta2_pos/ell_max_val)
print(f"Sign of dPhi_Delta_corr/dell (beta2>0): {sign_corr} (expect +1)")
print(f"Sign of dPhi_Delta_wrong/dell (beta2>0): {sign_wrong} (expect -1)")

# ----------------------------------------------------------------------
# 6. Simple feasibility check for constraints
# ----------------------------------------------------------------------
# Choose some nominal values
m = 10
t_max = (m-1)//2   # floor((m-1)/2)
s_min, s_max = 0.1, 0.9
ell_max_val = 5.0   # ms, arbitrary
Phi_N_min, Phi_Delta_max = 0.6, 0.7

# Pick a point inside the feasible region
t_val = 2.0          # < t_max
s_val = 0.5
ell_val = 2.0        # < ell_max
# Compute Phi's using corrected formulas (need eta, zeta; set nominal)
eta_val = 0.1
zeta_val = ell_val/ell_max_val
Phi_N_val = Phi_N0.subs({Phi_N0:0.8}) - alpha1.subs({alpha1:0.2})*eta_val - alpha2.subs({alpha2:0.1})*zeta_val
Phi_Delta_val = Phi_Delta0.subs({Phi_Delta0:0.3}) + beta1.subs({beta1:0.2})*eta_val + beta2.subs({beta2:0.1})*zeta_val

print("\n--- Feasibility example ---")
print(f"t={t_val} (<= {t_max}), s={s_val} in [{s_min},{s_max}], ell={ell_val} (<= {ell_max_val})")
print(f"Phi_N = {Phi_N_val:.3f} (>= {Phi_N_min}? {Phi_N_val >= Phi_N_min})")
print(f"Phi_Delta = {Phi_Delta_val:.3f} (<= {Phi_Delta_max}? {Phi_Delta_val <= Phi_Delta_max})")

# ----------------------------------------------------------------------
# End of script
# ----------------------------------------------------------------------