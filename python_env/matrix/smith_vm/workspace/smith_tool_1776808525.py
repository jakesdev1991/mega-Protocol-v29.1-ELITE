# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Compliance Checker for the Information‑Cascade Monitor (IC‑Ω) proposal.
Run in the isolated VM provided by the Matrix Guardian.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# 1. SYMBOLIC DEFINITIONS (as given in the proposal)
# ----------------------------------------------------------------------
# Base constants (dimensionless after scaling)
Phi_N0, Phi_Delta0 = sp.symbols('Phi_N0 Phi_Delta0', positive=True)
# Time‑lagged variables (τ ≈ 1‑2 weeks)
tau = sp.symbols('tau', positive=True)
# Cascade Intensity Index (CI) ∈ [0,1] via tanh
CI = sp.symbols('CI', real=True)          # we will later enforce 0 <= CI <= 1
# Liquidity withdrawal L, trader‑response skew Δ, cross‑ETF propagation C
L, Delta, C = sp.symbols('L Delta C', real=True)
# Coupling coefficients (positive constants)
eta1, eta2, eta3, eta4 = sp.symbols('eta1 eta2 eta3 eta4', positive=True)
# Curvature term (Ollivier‑Ricci) and its reference value
R_cascade, R0 = sp.symbols('R_cascade R0', positive=True)
lambda_ = sp.symbols('lambda_', real=True)   # curvature‑CI coupling

# ----------------------------------------------------------------------
# 2. INVARIANT CANDIDATES
# ----------------------------------------------------------------------
# Candidate A: curvature + CI (as first presented)
psi_A = sp.log(sp.Abs(R_cascade) / R0) + lambda_ * CI

# Candidate B: log‑connectivity (as later presented)
Phi_N_casc = Phi_N0 - eta1 * CI + eta2 * (1 - L)   # linear response (t‑τ omitted for brevity)
psi_B = sp.log(Phi_N_casc / Phi_N0)

# ----------------------------------------------------------------------
# 3. BOUNDARY CONDITIONS (as stated in the proposal)
# ----------------------------------------------------------------------
# Set 1 – ψ/CI based
bc_set1 = {
    'shredding': sp.Eq(psi_A, sp.oo),   # ψ → +∞
    'freeze'   : sp.Eq(psi_A, -sp.oo)   # ψ → -∞
}
# Set 2 – Φ_N, Φ_Δ, entropy based
# Entropy S_cascade ≥ ln(3)  →  S_cascade = ln(3) at boundary
S_cascade = sp.symbols('S_cascade', real=True)
Phi_Delta_casc = Phi_Delta0 + eta3 * Delta - eta4 * C   # linear response
bc_set2 = {
    'shredding': sp.And(sp.Eq(Phi_N_casc, 0), sp.Eq(S_cascade, 0)),
    'freeze'   : sp.And(sp.Eq(Phi_Delta_casc, sp.oo), sp.Eq(S_cascade, 0))
}

# ----------------------------------------------------------------------
# 4. DOUBLE‑WELL POTENTIAL
# ----------------------------------------------------------------------
I = sp.symbols('I', real=True)   # field 𝕀
alpha, beta, gamma = sp.symbols('alpha beta gamma', real=True)
V = alpha/2 * I**2 + beta/4 * I**4 - gamma * I

# Minima of V: solve dV/dI = 0
dV_dI = sp.diff(V, I)
crit_points = sp.solve(dV_dI, I)
# We expect two real minima: I≈0 and I≈sqrt(gamma/beta) (with alpha<0, beta>0, gamma>0)

# ----------------------------------------------------------------------
# 5. GAUGE TERM DIMENSIONLESSNESS CHECK
# ----------------------------------------------------------------------
# Assume scaling: x → x/L, t → t/Λ₀, ∂ → (1/L)∂̃, etc.
# After scaling, all fields must be dimensionless.
# We introduce dimensionless versions:
Phi_Delta_tilde = sp.symbols('Phi_Delta_tilde')   # claimed dimensionless
# Original Φ_Δ has dimension [time]^{-1/2} (skewness of a time distribution)
# To be dimensionless we need a characteristic time T0:
T0 = sp.symbols('T0', positive=True)
Phi_Delta_dim = Phi_Delta_tilde / sp.sqrt(T0)   # placeholder to show dimension
J_mu = sp.sqrt(2) * Phi_Delta_dim   # gauge current (μ=0 component)
# For J^μ to be dimensionless we need Phi_Delta_tilde to carry sqrt(T0)
# i.e. Phi_Delta_tilde must be √T0 * (dimensionless). We'll test this condition.

# ----------------------------------------------------------------------
# 6. VALIDATION ROUTINES
# ----------------------------------------------------------------------
def check_invariant_equivalence():
    """Return True if ψ_A and ψ_B are provably equal under the given mappings."""
    # We attempt to solve for R_cascade that makes ψ_A == ψ_B
    sol_R = sp.solve(sp.Eq(psi_A, psi_B), R_cascade)
    if not sol_R:
        return False, "No solution for R_cascade that makes the two invariants equal."
    # Check if the solution is independent of CI, L, Delta, C (i.e. universal)
    # If it still depends on those variables, the equivalence is not generic.
    depends = any(sym in sol_R[0].free_symbols for sym in (CI, L, Delta, C))
    return not depends, f"R_cascade = {sol_R[0]} (depends on dynamical vars? {depends})"

def check_boundary_consistency(psi_expr):
    """Derive ψ→±∞ conditions from psi_expr and compare with bc_set2."""
    # ψ → +∞ when its argument → 0+ (for log) or argument → +∞ (for additive CI term)
    # We'll test both possibilities generically.
    # For simplicity, we check if ψ_expr can be written as log(something) + const*CI
    # and see if something→0 yields ψ→ -∞, something→∞ yields ψ→ +∞.
    if psi_expr.has(sp.log):
        log_part = sp.log(sp.Abs(R_cascade) / R0) if psi_A == psi_expr else None
        # For psi_A:
        cond_plus = sp.Eq(R_cascade, 0)   # log(0) → -∞, but plus λ*CI may offset
        cond_minus = sp.Eq(R_cascade, sp.oo)  # log(∞) → +∞
        # However, the proposal's Set 2 ties shredding to Φ_N→0 and S→0.
        # We'll test if Φ_N→0 forces R_cascade→0 or ∞ under a assumed relation.
        # Since no explicit R_cascade(Φ_N) relation is given, we flag inconsistency.
        return False, "No explicit link between R_cascade and Φ_N/Φ_Δ; boundary sets cannot be reconciled."
    else:
        # psi_B case: ψ = log(Φ_N_casc/Φ_N0)
        cond_plus = sp.Eq(Phi_N_casc, 0)   # log(0) → -∞
        cond_minus = sp.Eq(Phi_N_casc, sp.oo) # log(∞) → +∞
        # Compare with bc_set2
        shred_match = sp.simplify(cond_plus - bc_set2['shredding'].args[0].lhs) == 0
        freeze_match = sp.simplify(cond_minus - bc_set2['freeze'].args[0].lhs) == 0
        return shred_match and freeze_match, f"Shred match: {shred_match}, Freeze match: {freeze_match}"

def check_potential_signs():
    """Return constraints on alpha,beta,gamma for the desired minima."""
    # Evaluate V at I=0 and I=I0 = sqrt(gamma/beta)
    I0 = sp.sqrt(gamma/beta)
    V0 = V.subs(I, 0)
    V_I0 = V.subs(I, I0)
    # For I=0 to be a local minimum: V''(0) > 0
    V2 = sp.diff(V, I, 2)
    cond_V0 = V2.subs(I, 0) > 0   # => alpha > 0
    # For I=I0 to be a local minimum: V''(I0) > 0 and V(I0) < V(0) (deeper well)
    cond_VI0 = V2.subs(I, I0) > 0
    cond_depth = sp.simplify(V_I0 - V0) < 0
    # Solve inequalities
    sol = sp.solve([cond_V0, cond_VI0, cond_depth], [alpha, beta, gamma])
    return sol

def check_gauge_dimensionless():
    """Return condition on Phi_Delta_tilde for J^μ to be dimensionless."""
    # J^μ dimensionless ↔ Phi_Delta_dim dimensionless
    # Phi_Delta_dim = Phi_Delta_tilde / sqrt(T0)
    # So we need Phi_Delta_tilde ∝ sqrt(T0)
    cond = sp.Eq(Phi_Delta_tilde**2, T0)   # up to a dimensionless constant
    return cond

# ----------------------------------------------------------------------
# 7. RUN CHECKS & REPORT
# ----------------------------------------------------------------------
print("=== Ω‑Protocol Compliance Check ===\n")

# 1) Invariant uniqueness
equiv, msg = check_invariant_equivalence()
print(f"Invariant equivalence (ψ_A == ψ_B)? {'PASS' if equiv else 'FAIL'}")
print(f"  Detail: {msg}\n")

# 2) Boundary consistency (we test both candidates)
for name, psi in [('psi_A', psi_A), ('psi_B', psi_B)]:
    consistent, msg2 = check_boundary_consistency(psi)
    print(f"Boundary consistency for {name}? {'PASS' if consistent else 'FAIL'}")
    print(f"  Detail: {msg2}\n")

# 3) Potential well signs
print("Potential well sign constraints (alpha,beta,gamma):")
sol = check_potential_signs()
print(f"  Solution set: {sol}\n")

# 4) Gauge dimensionless condition
print("Gauge term dimensionless condition:")
gauge_cond = check_gauge_dimensionless()
print(f"  Required: {gauge_cond}\n")

print("=== End of Check ===")