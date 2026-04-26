# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol compliance validator for the Information‑Cascade Monitor (IC‑Ω) proposal.
Checks:
 1. Invariant uniqueness
 2. Boundary‑condition consistency
 3. Double‑well potential bistability conditions
 4. Dimensionlessness of gauge current (assuming scaling)
 5. CI range via tanh
Run: python3 validate_ic_omega.py
"""

import sympy as sp

# ----------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------
# Fundamental parameters (real, positive unless noted)
alpha, beta, gamma, lam, eta1, eta2, eta3, eta4 = sp.symbols(
    'alpha beta gamma lam eta1 eta2 eta3 eta4', real=True
)
# Fields / observables
CI, PhiN0, PhiN, PhiD0, PhiD, S, L, Delta, C = sp.symbols(
    'CI PhiN0 PhiN PhiD0 PhiD S L Delta C', real=True, nonnegative=True
)
# Curvature and reference curvature
R, R0 = sp.symbols('R R0', real=True, positive=True)
# Cascade field I (not needed for algebraic checks but kept for completeness)
I = sp.symbols('I', real=True)

# ----------------------------------------------------------------------
# Helper: print result
# ----------------------------------------------------------------------
def check(name, condition, explanation=None):
    """Evaluate sympy Boolean condition; print PASS/FAIL."""
    # Try to simplify to True/False; if indeterminate, treat as FAIL
    try:
        result = sp.simplify(condition)
        if result == True:
            print(f"[PASS] {name}")
            return True
        elif result == False:
            print(f"[FAIL] {name}")
            if explanation:
                print(f"      → {explanation}")
            return False
        else:
            # Could not decide definitively
            print(f"[UNKNOWN] {name} -> {result}")
            if explanation:
                print(f"      → {explanation}")
            return False
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return False

# ----------------------------------------------------------------------
# 1. Invariant uniqueness
# ----------------------------------------------------------------------
psi_curvature = sp.ln(sp.Abs(R)/R0) + lam * CI          # ψ = ln(|ℛ|/ℛ₀) + λ·CI
psi_connectivity = sp.ln(PhiN / PhiN0)                # ψ = ln(Φ_N/Φ_N0)

# They are equal iff their difference is zero for all symbols.
diff_psi = sp.simplify(psi_curvature - psi_connectivity)
check(
    "Invariant uniqueness (ψ curvature == ψ connectivity)",
    sp.Eq(diff_psi, 0),
    "Difference must vanish identically; otherwise two distinct invariants."
)

# ----------------------------------------------------------------------
# 2. Boundary‑condition consistency
# ----------------------------------------------------------------------
# Linear‑response mappings from the proposal
PhiN_expr = PhiN0 - eta1 * CI + eta2 * (1 - L)
PhiD_expr = PhiD0 + eta3 * Delta - eta4 * C

# Entropy bound used in proposal: S >= ln(3)
S_min = sp.log(3)

# Define two candidate boundary statements:
# (A) ψ → +∞  <=>  CI → 1   (and ψ → -∞ <=> CI → 0)
# (B) ψ → +∞  <=>  Φ_N → 0  and S → 0
# (C) ψ → -∞  <=>  Φ_D → ∞  and S → 0

# We test whether the implications hold given the mappings.
# For (A) we need ψ to diverge when CI→1 (or 0). Since ψ = ln(Φ_N/Φ_N0),
# divergence occurs when Φ_N → 0 or Φ_N → ∞.
# Using PhiN_expr we see when CI→1:
PhiN_at_CI1 = PhiN_expr.subs(CI, 1)
PhiN_at_CI0 = PhiN_expr.subs(CI, 0)

check(
    "Boundary A: ψ→+∞ via CI→1  <=>  Φ_N→0",
    sp.Eq(PhiN_at_CI1, 0),
    "Requires PhiN0 - eta1 + eta2*(1-L) = 0 for all L, which is not guaranteed."
)

check(
    "Boundary A: ψ→-∞ via CI→0  <=>  Φ_N→∞",
    sp.Eq(PhiN_at_CI0, sp.oo),
    "Impossible with finite parameters; ψ cannot go to -∞ via CI→0 alone."
)

# For (B) we test ψ→+∞ <=> Φ_N→0 and S→0.
# ψ→+∞ when Φ_N→0 (since ln(0) = -∞, actually gives -∞; need Φ_N→∞ for +∞).
# So the statement is already mismatched.
check(
    "Boundary B: ψ→+∞ <=> Φ_N→0 & S→0",
    False,
    "ln(Φ_N/Φ_N0) → +∞ requires Φ_N→∞, not 0."
)

check(
    "Boundary B: ψ→-∞ <=> Φ_N→0 & S→0",
    sp.Eq(PhiN_expr, 0) & sp.Eq(S, 0),
    "Only holds if PhiN_expr = 0 AND S = 0 simultaneously; not guaranteed."
)

# For (C) we test ψ→-∞ <=> Φ_D→∞ & S→0.
# ψ→-∞ when Φ_N→0 (ln(0) = -∞). No direct Φ_D dependence.
check(
    "Boundary C: ψ→-∞ <=> Φ_D→∞ & S→0",
    False,
    "ψ depends on Φ_N only; Φ_D does not appear in ψ = ln(Φ_N/Φ_N0)."
)

# ----------------------------------------------------------------------
# 3. Double‑well potential bistability
# ----------------------------------------------------------------------
V = alpha/2 * I**2 + beta/4 * I**4 - gamma * I
dV = sp.diff(V, I)          # first derivative
d2V = sp.diff(dV, I)        # second derivative

# Stationary points: solve dV = 0
stationary = sp.solve(dV, I)
# We expect three real roots: I=0 and I=±sqrt(2*gamma/beta) when alpha<0.
# Check conditions on coefficients for the shape.
cond_alpha_neg = sp.Lt(alpha, 0)
cond_beta_pos  = sp.Gt(beta, 0)
cond_gamma_pos = sp.Gt(gamma, 0)

check(
    "Double‑well: α < 0",
    cond_alpha_neg,
    "Needed for local maximum at I=0."
)
check(
    "Double‑well: β > 0",
    cond_beta_pos,
    "Needed for confining quartic term."
)
check(
    "Double‑well: γ > 0",
    cond_gamma_pos,
    "Linear term shifts minima away from zero."
)

# Evaluate second derivative at I=0
d2V_at0 = sp.simplify(d2V.subs(I, 0))
check(
    "Second derivative at I=0 (should be <0 for max)",
    sp.Lt(d2V_at0, 0),
    f"d²V/dI²|_{I=0} = {d2V_at0}"
)

# Evaluate V at the non‑zero stationary points (if they exist)
nonzero_roots = [sol for sol in stationary if sol != 0]
if nonzero_roots:
    I0 = nonzero_roots[0]   # positive root
    V_at_I0 = sp.simplify(V.subs(I, I0))
    check(
        "Potential value at non‑zero stationary point (should be < V(0)=0 for min)",
        sp.Lt(V_at_I0, 0),
        f"V(I0) = {V_at_I0}"
    )
else:
    print("[FAIL] Double‑well: No non‑zero stationary points found (coefficients likely wrong).")

# ----------------------------------------------------------------------
# 4. Gauge current dimensionlessness (assume scaling makes all fields dimensionless)
# ----------------------------------------------------------------------
# After scaling, we treat PhiD as dimensionless.
# J^mu = sqrt(2) * PhiD * delta^mu_0
# Since sqrt(2) and delta^mu_0 are dimensionless, J^mu is dimensionless iff PhiD is.
# We cannot prove dimensionlessness here; we note the assumption.
print("[INFO] Gauge current dimensionlessness assumes Φ_Δ is rendered dimensionless by the L,Λ₀ scaling.")
print("[INFO] Verify analytically that scaling removes any time‑dimension from skewness.")

# ----------------------------------------------------------------------
# 5. CI range via tanh
# ----------------------------------------------------------------------
# CI = tanh(alpha_O*O + beta_L*L + gamma_C*C + delta_D*Delta)
# tanh maps ℝ → (-1,1); with non‑negative arguments we get (0,1).
# We assume the linear combination inside tanh is real.
inner = sp.symbols('inner', real=True)
CI_tanh = sp.tanh(inner)
check(
    "CI bounds from tanh",
    sp.And(CI_tanh >= -1, CI_tanh <= 1),
    "tanh always yields [-1,1]; with non‑negative inner argument CI∈[0,1]."
)

# ----------------------------------------------------------------------
# Final summary
# ----------------------------------------------------------------------
print("\n=== Validation Summary ===")
print("If any [FAIL] appears above, the proposal is NOT Ω‑compliant until the")
print("identified mathematical issues are resolved.")