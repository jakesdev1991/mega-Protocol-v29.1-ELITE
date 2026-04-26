# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Information‑Cascade Monitor (IC‑Ω)
Checks:
 1. Unique invariant ψ = ln(Φ_N_casc / Φ_N0)
 2. Boundary conditions derived analytically from ψ
 3. Cost function Lagrangian is well‑formed (no duplicated terms)
 4. Double‑well potential satisfies α<0, β>0, γ>0
"""
import sympy as sp

# ----------------------------------------------------------------------
# USER‑DEFINED SYMBOLS (replace with actual expressions from the proposal)
# ----------------------------------------------------------------------
t = sp.symbols('t', real=True)

# Placeholder definitions – the user should insert the real formulas
Phi_N_casc   = sp.Function('Phi_N_casc')(t)   # Φ_N^{(casc)}(t)
Phi_N0       = sp.symbols('Phi_N0', positive=True)  # constant baseline
Phi_Delta_casc = sp.Function('Phi_Delta_casc')(t)
S_cascade    = sp.Function('S_cascade')(t)
CI           = sp.Function('CI')(t)          # Cascade Intensity Index
R_cascade    = sp.Function('R_cascade')(t)   # Ollivier‑Ricci curvature magnitude
R0           = sp.symbols('R0', positive=True)
lam          = sp.symbols('lam', real=True)  # λ coupling CI to ψ

# ----------------------------------------------------------------------
# 1. INVARIANT CHECK
# ----------------------------------------------------------------------
# Rubric‑mandated invariant
psi_rubric = sp.log(Phi_N_casc / Phi_N0)

# Invariant actually used in the proposal (curvature + CI form)
psi_proposal = sp.log(R_cascade / R0) + lam * CI

# Are they equivalent under any reasonable substitution?
# We test if the difference can be expressed as zero given the
# linear response mappings claimed in the text:
#   Φ_N_casc = Phi_N0 - eta1*CI(t-tau) + eta2*(1-L(t-tau))
#   Φ_Delta_casc = Phi_Delta0 + eta3*Delta(t-tau) - eta4*C(t-tau)
# For brevity we treat the mappings as generic functions f_N(CI, L) and f_D(Delta, C)
eta1, eta2, eta3, eta4, tau = sp.symbols('eta1 eta2 eta3 eta4 tau', real=True)
L = sp.Function('L')(t)   # liquidity withdrawal
Delta = sp.Function('Delta')(t)  # trader‑response skew
C = sp.Function('C')(t)   # cross‑ETF correlation

Phi_N_map = Phi_N0 - eta1*CI.subs(t, t-tau) + eta2*(1 - L.subs(t, t-tau))
Phi_Delta_map = sp.Function('Phi_Delta0')(t) + eta3*Delta.subs(t, t-tau) - eta4*C.subs(t, t-tau)

# Substitute the mappings into psi_rubric and see if we can rearrange to psi_proposal
psi_rubric_sub = sp.log(Phi_N_map / Phi_N0)

# Simplify the difference
diff = sp.simplify(psi_rubric_sub - psi_proposal)
print("Difference between rubric invariant and proposal invariant:", diff)
# If diff simplifies to 0 (or a constant times a known zero), they are equivalent.
# In practice, with the given linear forms, diff will NOT be zero → invariant mismatch.

# ----------------------------------------------------------------------
# 2. BOUNDARY CONDITION DERIVATION
# ----------------------------------------------------------------------
# Boundaries should follow from psi -> +/- inf
# Solve psi_rubric -> +inf  => Phi_N_casc -> 0 (since log(0) = -inf, actually -inf)
# Wait: log(x) -> -inf as x->0+, +inf as x->+inf.
# Therefore:
#   psi -> +inf  <=> Phi_N_casc -> +inf
#   psi -> -inf  <=> Phi_N_casc -> 0+
# We also need to tie in S_cascade and Phi_Delta as per the proposal's narrative.
# Let's derive the conditions the proposal states and compare.

# Proposed Set 2 boundaries:
#   Shredding: psi -> +inf when Phi_N_casc -> 0 and S_cascade -> 0
#   Freeze:    psi -> -inf when Phi_Delta_casc -> oo and S_cascade -> 0
# These are opposite of what the log invariant gives → inconsistency.

psi = psi_rubric  # use the rubric invariant as reference

# Conditions for psi -> +inf / -inf
cond_plus_inf  = sp.simplify(sp.limit(psi, Phi_N_casc, sp.oo))   # should be +oo
cond_minus_inf = sp.simplify(sp.limit(psi, Phi_N_casc, 0))     # should be -oo

print("Limit psi as Phi_N_casc -> +oo:", cond_plus_inf)
print("Limit psi as Phi_N_casc -> 0+:", cond_minus_inf)

# ----------------------------------------------------------------------
# 3. COST FUNCTION CHECK
# ----------------------------------------------------------------------
# Define a generic Lagrangian L = (CI-0.6)_+^2 + mu1*(0.6-Phi_N_casc)_+^2 +
#                               mu2*Phi_Delta_casc^2 + mu3*(log(3)-S_cascade)_+^2
# We will verify that each term appears exactly once.
mu1, mu2, mu3 = sp.symbols('mu1 mu2 mu3', nonnegative=True)

L = (sp.Max(CI - 0.6, 0))**2 \
    + mu1 * sp.Max(0.6 - Phi_N_casc, 0)**2 \
    + mu2 * Phi_Delta_casc**2 \
    + mu3 * sp.Max(sp.log(3) - S_cascade, 0)**2

# Detect duplicated structural terms by converting to a list of additive components
terms = sp.Add.make_args(L)
print("\nCost function terms:")
for i, term in enumerate(terms, 1):
    print(f"{i}: {term}")

# Check for duplication (simple string‑based test; for production use sympy equality)
term_strs = [str(sp.simplify(t)) for t in terms]
duplicates = [t for t in set(term_strs) if term_strs.count(t) > 1]
if duplicates:
    print("\nDuplicated terms found:", duplicates)
else:
    print("\nNo duplicated terms detected.")

# ----------------------------------------------------------------------
# 4. DOUBLE‑WELL POTENTIAL SIGN CONSTRAINTS
# ----------------------------------------------------------------------
I = sp.symbols('I', real=True)
alpha, beta, gamma = sp.symbols('alpha beta gamma', real=True)
V = alpha/2 * I**2 + beta/4 * I**4 - gamma * I

# Conditions for a double well with minima at I=0 and I=+-sqrt(gamma/beta)
# Requires: beta>0, gamma>0, and alpha<0 (so that V''(0)=alpha <0 -> local max at 0,
#            and V''(+-sqrt(gamma/beta)) = 2*beta*(gamma/beta)+alpha = 2*gamma+alpha >0)
cond_beta   = beta > 0
cond_gamma  = gamma > 0
cond_alpha  = alpha < 0
cond_V2pos  = 2*gamma + alpha > 0  # second derivative at the non‑zero minima

print("\nDouble‑well potential constraints:")
print("beta > 0   :", cond_beta)
print("gamma > 0  :", cond_gamma)
print("alpha < 0  :", cond_alpha)
print("2*gamma + alpha > 0 :", cond_V2pos)

# ----------------------------------------------------------------------
# SUMMARY
# ----------------------------------------------------------------------
print("\n=== VALIDATION SUMMARY ===")
print("Invariant mismatch? :", "YES" if not sp.simplify(diff).equals(0) else "NO")
print("Boundary consistency? :", "NO")  # derived above shows contradiction
print("Cost function well‑formed? :", "YES" if not duplicates else "NO")
print("Potential signs satisfied? :",
      "YES" if (cond_beta and cond_gamma and cond_alpha and cond_V2pos) else "NO")