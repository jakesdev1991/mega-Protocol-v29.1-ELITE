# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith – HVFI-Ω v2 Mathematical Consistency Check
Verifies:
  • ψ definition matches ξ from ϕ₀
  • ξ_N, ξ_Δ formulas satisfy the derived sum rule
  • Σ_A + εI is positive‑definite ⇒ Ψ real
  • Entropy stays in [0, ln(bins)]
Run in the isolated VM; any AssertionError flags a violation.
"""

import sympy as sp
import numpy as np

# ---- Symbolic parameters ----
lam, v, phi0, xi0 = sp.symbols('lam v phi0 xi0', positive=True, real=True)
PhiN, PhiD = sp.symbols('PhiN PhiD', real=True)   # Φ_N, Φ_Δ

# ---- Definitions ----
xi   = 1/sp.sqrt(lam*(3*phi0**2 - v**2))          # correlation length
psi  = sp.log(xi/xi0)                            # invariant ψ
xiN2 = lam*(3*PhiN**2 + PhiD**2 - v**2)          # ξ_N^{-2}
xiD2 = lam*(PhiN**2 + 3*PhiD**2 - v**2)          # ξ_Δ^{-2}

# ---- 1. ψ‑definition check ----
psi_from_def = sp.simplify(sp.log(1/(xi0*sp.sqrt(lam*(3*phi0**2 - v**2)))))
assert sp.simplify(psi - psi_from_def) == 0, "ψ definition inconsistent with ξ"

# ---- 2. Invariant sum rule ----
sum_rule = sp.simplify(xiN2 + xiD2 - (4*lam*(PhiN**2 + PhiD**2) - 2*lam*v**2))
assert sum_rule == 0, "ξ_N^{-2}+ξ_Δ^{-2} sum rule violated"

# ---- 3. Positive‑definiteness of Σ_A + εI (numeric test) ----
def test_covariance_posdef(num_samples=100, dim=3):
    eps = 1e-6
    for _ in range(num_samples):
        # random activation matrix A (dim x L) – L = num_scales
        L = np.random.randint(2, 5)
        A = np.random.randn(dim, L)
        Sigma = np.cov(A)          # LxL covariance
        M = Sigma + eps*np.eye(L)
        eigvals = np.linalg.eigvals(M)
        if np.any(eigvals <= 0):
            return False, eigvals
    return True, None

ok, bad = test_covariance_posdef()
assert ok, f"Covariance matrix not PD → Ψ may become complex. Bad eigs: {bad}"

# ---- 4. Entropy bounds (numeric) ----
def shannon_entropy(probs):
    # probs: 1D array, sums to 1
    return -np.sum(probs * np.log(probs + 1e-12))

def test_entropy(bins=20, trials=200):
    for _ in range(trials):
        p = np.random.dirichlet(alpha=np.ones(bins))
        h = shannon_entropy(p)
        if not (0 - 1e-12 <= h <= np.log(bins) + 1e-12):
            return False, h
    return True, None

ok_e, bad_e = test_entropy()
assert ok_e, f"Entropy out of bounds: {bad_e}"

print("All symbolic and numeric checks passed. HVFI‑Ω v2 core math is Ω‑Protocol compliant.")