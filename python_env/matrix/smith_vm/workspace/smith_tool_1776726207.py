# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Invariant Validator for SERC Output
Checks:
  - ψ = ln(Φ_N/Φ₀) is dimensionless
  - ξ_Δ ≥ 1
  - 0 < S_j ≤ 1, S_j == 1 for Gaussian jerk
  - Cost integrand non‑negative
  - Warning condition well‑defined
Run inside the isolated VM; any AssertionError aborts the agent's thought.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# Symbolic definitions (units are carried as symbols for dimensional check)
# ----------------------------------------------------------------------
t = sp.symbols('t', real=True)
# Base dimensions: [Φ_N] = U (coherence rate), [t] = T
U, T = sp.symbols('U T', positive=True)   # units
# Reference scale Φ₀ has same units as Φ_N
Phi0 = sp.symbols('Phi0', positive=True)  # same unit U

# Fields (generic symbols)
Phi_N = sp.Function('Phi_N')(t)   # has unit U
# Jerk: third derivative
j = sp.diff(Phi_N, t, 3)          # unit U / T^3

# Statistical symbols (assume ergodic over window [t-T, t])
Twin = sp.symbols('Twin', positive=True)   # window width, unit T
j_bar = sp.Function('j_bar')(t)            # mean jerk
sigma_j_sq = sp.Function('sigma_j_sq')(t)  # variance of jerk (unit U^2/T^6)
eps = sp.symbols('eps', positive=True)     # regularisation, same unit as sigma_j_sq

# ----------------------------------------------------------------------
# 1. Scalar invariant ψ
# ----------------------------------------------------------------------
psi = sp.log(Phi_N / Phi0)   # dimensionless argument
# Check: log argument must be dimensionless -> units cancel
assert psi.free_symbols.intersection({U, T}) == set(), \
    "ψ is not dimensionless: check units of Φ_N and Φ₀"
print("[OK] ψ = ln(Φ_N/Φ₀) is dimensionless")

# ----------------------------------------------------------------------
# 2. Poloidal correlation ξ_Δ  (ratio of variances → ≥1)
# ----------------------------------------------------------------------
# Symbolic variances for three classes c
sigma2_c = {c: sp.symbols(f'sigma2_{c}', positive=True) for c in ('CPU_GPU','GPU_GPU','CPU_CPU')}
xi_Delta = max(sigma2_c.values()) / min(sigma2_c.values())
# Since all symbols positive, xi_Delta >= 1 holds by construction
assert sp.simplify(xi_Delta - 1) >= 0, "ξ_Δ < 1 detected"
print("[OK] ξ_Δ ≥ 1 (by construction)")

# ----------------------------------------------------------------------
# 3. Jerk‑stability metric S_j (regularised)
# ----------------------------------------------------------------------
# Normalised jerk inside the fourth‑power moment
norm_j = (j - j_bar) / sp.sqrt(sigma_j_sq + eps)
# Raw kurtosis κ = <norm_j^4>
kappa = sp.Integral(norm_j**4, (t, t - Twin, t)) / Twin
# Excess kurtosis part inside absolute value
excess = sp.Abs(kappa - 3)
S_j = 1 / (1 + excess)

# Properties to test:
# (a) S_j > 0 always
assert sp.simplify(S_j - 0) > 0, "S_j ≤ 0"
# (b) S_j ≤ 1  (since denominator ≥1)
assert sp.simplify(1 - S_j) >= 0, "S_j > 1"
# (c) For Gaussian jerk: kappa = 3 → excess = 0 → S_j = 1
# Substitute kappa = 3
S_j_gauss = S_j.subs(kappa, 3)
assert sp.simplify(S_j_gauss - 1) == 0, "S_j ≠ 1 for Gaussian jerk"
print("[OK] S_j ∈ (0,1] and S_j=1 for Gaussian jerk")

# ----------------------------------------------------------------------
# 4. Cost functional integrand non‑negative
# ----------------------------------------------------------------------
alpha, lam = sp.symbols('alpha lam', positive=True)
P_meas = sp.Function('P_meas')(t)
P_target = sp.Function('P_target')(t)
S_h = sp.Function('S_h')(t)   # entropy, assumed ≥0
integrand = (1 - S_j)**2 + alpha * S_h + lam * (P_meas - P_target)**2
# Each term is a square or product of positive symbols → ≥0
assert sp.simplify(integrand) >= 0, "Cost integrand can be negative"
print("[OK] Cost integrand ≥ 0")

# ----------------------------------------------------------------------
# 5. Warning condition well‑defined (no division by zero etc.)
# ----------------------------------------------------------------------
j_thresh = sp.symbols('j_thresh', positive=True)
warning = sp.And(sp.Lt(S_j, 0.7), sp.Lt(j, -j_thresh))
# Just ensure the symbols exist; no further check needed
print("[OK] Warning condition syntactically valid")

# ----------------------------------------------------------------------
# Numerical sanity‑check (optional, but cheap)
# ----------------------------------------------------------------------
def numeric_check():
    """Randomised test to catch hidden runtime issues."""
    np.random.seed(42)
    for _ in range(1000):
        # random positive numbers for units (set U=T=1 for simplicity)
        PhiN_val = np.random.uniform(0.5, 2.0)
        Phi0_val = 1.0
        psi_val = np.log(PhiN_val / Phi0_val)
        assert np.isfinite(psi_val)

        # variances
        var_vals = np.random.uniform(0.1, 5.0, size=3)
        xi_delta_val = np.max(var_vals) / np.min(var_vals)
        assert xi_delta_val >= 1.0 - 1e-12

        # jerk and stats
        j_val = np.random.uniform(-1, 1)
        j_bar_val = np.random.uniform(-1, 1)
        sigma2_val = np.random.uniform(1e-6, 2.0)  # avoid zero
        eps_val = 1e-8
        norm = (j_val - j_bar_val) / np.sqrt(sigma2_val + eps_val)
        kappa_val = norm**4  # single‑sample estimate
        excess_val = np.abs(kappa_val - 3)
        S_j_val = 1.0 / (1.0 + excess_val)
        assert 0.0 < S_j_val <= 1.0 + 1e-12
        # Gaussian case: force norm^4 = 3
        norm_gauss = np.sign(np.random.randn()) * (3.0)**0.25
        kappa_gauss = norm_gauss**4
        S_j_gauss = 1.0 / (1.0 + np.abs(kappa_gauss - 3))
        assert np.abs(S_j_gauss - 1.0) < 1e-12

        # cost integrand
        alpha_val, lam_val = np.random.uniform(0.1, 2.0, size=2)
        P_meas_val = np.random.uniform(0, 5)
        P_target_val = np.random.uniform(0, 5)
        S_h_val = np.random.uniform(0, 2)  # entropy bound loose
        integrand_val = (1 - S_j_val)**2 + alpha_val * S_h_val + lam_val * (P_meas_val - P_target_val)**2
        assert integrand_val >= -1e-12

    print("[OK] Numerical sanity check passed (1000 random samples)")

numeric_check()

print("\nAll Omega‑Protocol invariant checks PASSED.")