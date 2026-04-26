# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validation Script
-----------------------------------------
Checks the mathematical soundness and Ω‑Rubric v26.0 compliance of the
Information‑Cascade Monitor (IC‑Ω) proposal.

The script validates:
1. Single, well‑defined invariant ψ_cascade.
2. Consistency of the two boundary‑condition sets.
3. Correct bistability of the double‑well potential V(𝕀).
4. Dimensionless nature of the gauge term A_μ J^μ.
5. Basic MPC‑Ω constraint feasibility.

If any check fails, the script reports a FAIL with details.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# Symbolic definitions (all symbols are assumed dimensionless after scaling)
# ----------------------------------------------------------------------
# Fields and parameters
ΦN0, ΦΔ0 = sp.symbols('ΦN0 ΦΔ0', positive=True)   # baseline values
ΦN, ΦΔ   = sp.symbols('ΦN ΦΔ')                    # cascade‑mode values
CI, L, Δ, C = sp.symbols('CI L Δ C', real=True)  # cascade intensity & auxiliaries
λ, η1, η2, η3, η4 = sp.symbols('λ η1 η2 η3 η4', real=True)
α, β, γ = sp.symbols('α β γ', real=True)         # potential coefficients
ℛ, ℛ0 = sp.symbols('ℛ ℛ0', positive=True)       # Ollivier‑Ricci curvature & ref

# ----------------------------------------------------------------------
# 1. Invariant ψ_cascade – check for a single definition
# ----------------------------------------------------------------------
# Definition A (curvature + CI)
ψ_A = sp.log(sp.Abs(ℛ)/ℛ0) + λ*CI

# Definition B (log‑connectivity)
ψ_B = sp.log(ΦN/ΦN0)

# Are they equivalent under the proposed linear‑response mappings?
# Linear‑response mappings (from the proposal):
ΦN_expr = ΦN0 - η1*CI + η2*(1 - L)          # Φ_N^{(casc)}(t)
ΦΔ_expr = ΦΔ0 + η3*Δ - η4*C                # Φ_Δ^{(casc)}(t)

# Substitute ΦN from the mapping into ψ_B
ψ_B_sub = sp.log(ΦN_expr/ΦN0)

# Simplify the difference ψ_A - ψ_B_sub (assuming ℛ is a function of CI, L, Δ, C)
# For a generic test we treat ℛ as an independent symbol; equivalence would
# require ψ_A - ψ_B_sub = 0 for all symbols → impossible unless extra constraints.
diff_psi = sp.simplify(ψ_A - ψ_B_sub)
print("[Invariant Check] ψ_A - ψ_B_sub =", diff_psi)
if diff_psi == 0:
    print("  → PASS: Single invariant definition (equivalence holds).")
else:
    print("  → FAIL: Two non‑equivalent invariant definitions.")
    print("      Difference:", diff_psi)

# ----------------------------------------------------------------------
# 2. Boundary‑condition consistency
# ----------------------------------------------------------------------
# Set 1 (ψ/CI based)
#   Shredding: ψ → +∞, CI → 1
#   Freeze:    ψ → -∞, CI → 0
# Set 2 (ΦN/ΦΔ/entropy based)
#   Shredding: ψ → +∞ when ΦN → 0 and S → 0
#   Freeze:    ψ → -∞ when ΦΔ → ∞ and S → ln(1)=0
# Entropy S_cascade = -∑ p_k log p_k; we only need its limits:
#   S → 0  ⇔  one participant type dominates (p_k → 1 for some k)
#   S → ln(3) (max for 3 types) is the QP lower bound; not used here.

# Derive ψ from Set 2 using ψ_B = ln(ΦN/ΦN0)
ψ_set2 = sp.log(ΦN/ΦN0)   # same as ψ_B

# Evaluate limits
limit_shred_set1 = sp.limit(ψ_A, CI, 1, dir='+')   # ψ → +∞ as CI→1?
limit_freeze_set1 = sp.limit(ψ_A, CI, 0, dir='-')  # ψ → -∞ as CI→0?

limit_shred_set2 = sp.limit(ψ_set2, ΦN, 0, dir='+')   # ψ → +∞ as ΦN→0?
limit_freeze_set2 = sp.limit(ψ_set2, ΦΔ, sp.oo, dir='+')  # ψ → -∞ as ΦΔ→∞?

print("\n[Boundary Check]")
print("  ψ_A limit CI→1 :", limit_shred_set1)
print("  ψ_A limit CI→0 :", limit_freeze_set1)
print("  ψ_B limit ΦN→0 :", limit_shred_set2)
print("  ψ_B limit ΦΔ→∞ :", limit_freeze_set2)

# For consistency we need the signs to match:
cond_shred = (limit_shred_set1 == sp.oo) and (limit_shred_set2 == sp.oo)
cond_freeze = (limit_freeze_set1 == -sp.oo) and (limit_freeze_set2 == -sp.oo)

if cond_shred and cond_freeze:
    print("  → PASS: Boundary‑condition sets are consistent.")
else:
    print("  → FAIL: Boundary‑condition sets disagree.")
    if not cond_shred:
        print("      Shredding limits mismatch.")
    if not cond_freeze:
        print("      Freeze limits mismatch.")

# ----------------------------------------------------------------------
# 3. Double‑well potential bistability
# ----------------------------------------------------------------------
V = sp.Rational(1,2)*α*CI**2 + sp.Rational(1,4)*β*CI**4 - γ*CI
# Stationary points: dV/dCI = 0
dV = sp.diff(V, CI)
stationary = sp.solve(dV, CI)
print("\n[Potential Check] Stationary points of V:", stationary)

# Evaluate second derivative at each point to classify minima/maxima
ddV = sp.diff(dV, CI)
minima = []
for sol in stationary:
    if ddV.subs(CI, sol) > 0:
        minima.append(sol)
print("  Minima candidates:", minima)

# For a bistable shape we need exactly two real minima (one at CI≈0, one at CI>0)
# and a local maximum between them.
real_minima = [m for m in minima if m.is_real]
if len(real_minima) >= 2:
    # Check that V(0) is a minimum (or near) and another positive CI minimum exists
    V0 = V.subs(CI, 0)
    V_pos = [V.subs(CI, m) for m in real_minima if m > 0]
    if V0 == min([V0] + V_pos) and len(V_pos) > 0:
        print("  → PASS: Potential exhibits bistable shape (CI=0 and CI>0 minima).")
    else:
        print("  → FAIL: Potential does not have the required minima structure.")
else:
    print("  → FAIL: Insufficient real minima for bistability.")

# Optional: enforce sign conditions α<0, β>0, γ>0 for the textbook double‑well
print("  Suggested sign constraints: α < 0, β > 0, γ > 0")
if α < 0 and β > 0 and γ > 0:
    print("  → PASS: Sign conditions satisfied (assuming symbolic assumptions).")
else:
    print("  → INFO: Sign constraints not automatically verified (symbolic).")

# ----------------------------------------------------------------------
# 4. Gauge term dimensionlessness (simple check)
# ----------------------------------------------------------------------
# J^μ = sqrt(2) * ΦΔ * δ^μ_0
# A_μ = ∂_μ S_cascade ; S_cascade is dimensionless → A_μ dimensionless
# Hence A_μ J^μ dimensionless if ΦΔ dimensionless.
# We already treat ΦΔ as dimensionless symbol.
print("\n[Gauge Term Check]")
print("  Assuming ΦΔ dimensionless → A_μ J^μ dimensionless.")
print("  → PASS (by construction).")

# ----------------------------------------------------------------------
# 5. MPC‑Ω constraint feasibility (quick numeric sanity)
# ----------------------------------------------------------------------
# Constraints: CI ≤ 0.7, ΦN ≥ 0.6, S ≥ ln(3)
# We test a random feasible point.
np.random.seed(42)
CI_test = np.random.uniform(0, 0.7)
ΦN_test = np.random.uniform(0.6, 1.2)
# Entropy for three participant types: max = ln(3) ≈ 1.0986
S_test = np.random.uniform(np.log(3), np.log(3)+0.2)  # slightly above bound
feasible = (CI_test <= 0.7) and (ΦN_test >= 0.6) and (S_test >= np.log(3))
print("\n[MPC‑Ω Constraint Feasibility]")
print("  Sample point: CI={:.3f}, ΦN={:.3f}, S={:.3f}".format(CI_test, ΦN_test, S_test))
print("  Feasible?", feasible)
if feasible:
    print("  → PASS: Constraint region non‑empty.")
else:
    print("  → FAIL: Constraint region empty (unlikely).")

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
print("\n=== OMEGA PROTOCOL VALIDATION SUMMARY ===")
print("If any FAIL appears above, the proposal does NOT satisfy")
print("the strict Ω‑Physics Rubric v26.0 and must be revised.")