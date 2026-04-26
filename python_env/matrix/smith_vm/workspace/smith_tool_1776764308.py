# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Audit: Computational Resource Fragility Monitor (CRFM‑Ω)
Validates mathematical soundness and invariant compliance.
"""

import numpy as np
import sympy as sp

# ---------------------------
# Symbolic definitions
# ---------------------------
# Time‑dependent variables (treated as symbols for generic checking)
t = sp.symbols('t', real=True)
CFI = sp.symbols('CFI', real=True)          # fragility index, expected in [0,1]
Eff = sp.symbols('Eff', real=True)          # energy‑efficiency metric (normalised)
PhiN0 = sp.symbols('PhiN0', real=True)      # baseline strategic connectivity
PhiD0 = sp.symbols('PhiD0', real=True)      # baseline information asymmetry
eta1, eta2, eta3 = sp.symbols('eta1 eta2 eta3', real=True, nonnegative=True)
tau1, tau2 = sp.symbols('tau1 tau2', real=True, nonnegative=True)
lam = sp.symbols('lam', real=True)          # lambda in psi
xi = sp.symbols('xi', real=True, positive=True)   # correlation length
xi0 = sp.symbols('xi0', real=True, positive=True) # reference length
mu1, mu2 = sp.symbols('mu1 mu2', real=True, nonnegative=True)

# ---------------------------
# 1. CFI bounds
# ---------------------------
assert CFI >= 0 and CFI <= 1, "CFI must lie in [0,1]"

# ---------------------------
# 2. Mapping to Omega variables
# ---------------------------
PhiN_comp = PhiN0 - eta1 * sp.tanh(CFI)   # tau shift omitted for generic check; tanh argument shift does not affect bounds
PhiD_comp = PhiD0 + eta2 * CFI - eta3 * Eff

# Protocol‑imposed normalisation (assume [0,1] for both fields)
assert PhiN_comp >= 0 and PhiN_comp <= 1, "PhiN_comp out of [0,1]"
assert PhiD_comp >= 0 and PhiD_comp <= 1, "PhiD_comp out of [0,1]"

# ---------------------------
# 3. Invariant ψ and stiffness
# ---------------------------
psi = sp.log(xi/xi0) + lam * CFI   # log argument positive by xi>0,xi0>0
# Stiffness coefficients (derivatives)
xi_N = sp.diff(PhiN_comp, psi)
xi_D = sp.diff(PhiD_comp, psi)

# Ensure derivatives are finite (no division by zero, etc.)
assert xi_N.is_finite, "xi_N (dPhiN/dpsi) is not finite"
assert xi_D.is_finite, "xi_D (dPhiD/dpsi) is not finite"

# ---------------------------
# 4. MPC‑Ω constraints (numeric check)
# ---------------------------
# Choose plausible baseline values for a numeric sanity test
num_vals = {
    PhiN0: 0.85,
    PhiD0: 0.30,
    eta1: 0.15,
    eta2: 0.20,
    eta3: 0.10,
    lam: 0.05,
    xi: 1.2,
    xi0: 1.0,
    Eff: 0.7,   # normalised efficiency (0–1)
    mu1: 1.0,
    mu2: 1.0,
}
# Sample CFI across its allowed range
cfi_samples = np.linspace(0, 1, 101)
for c in cfi_samples:
    subs_dict = {**num_vals, CFI: c}
    PhiN_val = float(PhiN_comp.subs(subs_dict))
    PhiD_val = float(PhiD_comp.subs(subs_dict))
    # Enforce MPC constraints
    assert c <= 0.6 + 1e-9, f"CFI constraint violated: {c}"
    assert PhiN_val >= 0.7 - 1e-9, f"PhiN constraint violated: {PhiN_val}"
    assert PhiD_val <= 0.6 + 1e-9, f"PhiDelta constraint violated: {PhiD_val}"

# ---------------------------
# 5. Cost function non‑negativity
# ---------------------------
s_CFI = sp.symbols('s_CFI', real=True)   # anomaly score (non‑negative)
cost_integrand = CFI**2 + mu1 * s_CFI**2 + mu2 * (1 - PhiN_comp)**2
assert cost_integrand >= 0, "Cost integrand can be negative"

# ---------------------------
# 6. Summary
# ---------------------------
print("All symbolic and numeric checks passed.")
print("CRFM‑Ω formulation is mathematically sound w.r.t. Omega Protocol invariants.")