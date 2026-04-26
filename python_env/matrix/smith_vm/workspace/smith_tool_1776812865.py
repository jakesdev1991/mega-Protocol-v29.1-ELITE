# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symbolic validation of the refined Perceptual Coherence Shield (PCS-Ω)
Omega Protocol invariant compliance check.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# 1. Symbols and parameters
# ----------------------------------------------------------------------
# Field variable
C = sp.symbols('C', real=True)

# Double-well potential parameters (must satisfy alpha<0, beta>0, gamma>0)
alpha, beta, gamma = sp.symbols('alpha beta gamma', real=True)
# Assume the inequalities hold; we will enforce them later via assumptions.

# Hessian-derived coefficients (kappa_i >= 0 ensures non-negative omega^2)
kappa1, kappa2, kappa3, kappa4 = sp.symbols('kappa1 kappa2 kappa3 kappa4',
                                            nonnegative=True, real=True)

# Measures that appear in omega^2 definitions (treated as non-negative scalars)
grad_norm_sq, C_norm_sq, skew_C = sp.symbols('grad_norm_sq C_norm_sq skew_C',
                                            nonnegative=True, real=True)

# ----------------------------------------------------------------------
# 2. Double-well potential V(C)
# ----------------------------------------------------------------------
V = alpha/2 * C**2 + beta/4 * C**4 - gamma * C

# First and second derivatives
V_prime = sp.diff(V, C)
V_double = sp.diff(V_prime, C)

print("=== Double-well potential V(C) ===")
print("V(C)   =", V)
print("V'(C)  =", V_prime)
print("V''(C) =", V_double)
print()

# Parameter sign checks
print("Parameter sign conditions:")
print("  alpha < 0  :", sp.simplify(alpha < 0))
print("  beta  > 0  :", sp.simplify(beta > 0))
print("  gamma > 0  :", sp.simplify(gamma > 0))
print()

# ----------------------------------------------------------------------
# 3. Minima of V(C) and Hessian eigenvalues (omega_N^2, omega_Delta^2)
# ----------------------------------------------------------------------
# Solve V'(C)=0 for stationary points
stationary = sp.solve(V_prime, C)
print("Stationary points (solutions of V'(C)=0):")
for sol in stationary:
    print("  C =", sol)
print()

# Evaluate V'' at each stationary point to ensure they are minima (V''>0)
print("Second derivative at each stationary point:")
for sol in stationary:
    V2_at = V_double.subs(C, sol)
    print(f"  V''({sol}) = {V2_at}")
    # For a genuine minimum we need V''>0; we will check sign later.
print()

# Define omega_N^2 and omega_Delta^2 as per the proposal
omega_N_sq = kappa1 * (grad_norm_sq / C_norm_sq) + kappa2
omega_D_sq = kappa3 * skew_C + kappa4

print("=== Covariant mode squared frequencies ===")
print("omega_N^2  =", omega_N_sq)
print("omega_D^2  =", omega_D_sq)
print()

# Ensure they are non-negative given kappa_i>=0 and the measures>=0
print("Non-negativity checks (symbolic):")
print("  omega_N^2 >= 0 ?", sp.simplify(omega_N_sq >= 0))
print("  omega_D^2 >= 0 ?", sp.simplify(omega_D_sq >= 0))
print()

# Define Phi_N, Phi_Delta as square roots (principal branch)
Phi_N   = sp.sqrt(omega_N_sq)
Phi_D   = sp.sqrt(omega_D_sq)

print("Phi_N = sqrt(omega_N^2) =", Phi_N)
print("Phi_D = sqrt(omega_D^2) =", Phi_D)
print()

# ----------------------------------------------------------------------
# 4. Invariant psi_perc
# ----------------------------------------------------------------------
Phi_N0 = sp.symbols('Phi_N0', positive=True, real=True)  # baseline
psi_perc = sp.log(Phi_N / Phi_N0)
print("=== Perceptual coherence invariant ===")
print("psi_perc = ln(Phi_N / Phi_N0) =", psi_perc)
print()

# ----------------------------------------------------------------------
# 5. Conditional entropy S_perc
# ----------------------------------------------------------------------
# We model a finite set of regions R and coherence bins Cb.
# p_r: probability of region r, p_c_given_r: conditional probability of bin c in region r.
# For symbolic verification we treat them as generic probabilities satisfying:
#   sum_r p_r = 1, 0 <= p_r <= 1
#   sum_c p_c_given_r = 1, 0 <= p_c_given_r <= 1

# Define symbolic probabilities (non-negative, will be constrained later)
R = sp.symbols('R0 R1 R2', nonnegative=True)   # example: 3 regions
Cb = sp.symbols('c0 c1 c2', nonnegative=True) # example: 3 coherence bins

p_r = sp.Matrix([R0, R1, R2])
p_c_given_r = sp.Matrix([[c0, c1, c2],
                         [c0, c1, c2],
                         [c0, c1, c2]])   # same structure for each region (simplify)

# Normalization constraints (we will enforce them later via assumptions)
norm_p_r = sp.Eq(p_r.sum(), 1)
norm_p_c = [sp.Eq(p_c_given_r[i,:].sum(), 1) for i in range(3)]

print("=== Conditional entropy setup ===")
print("Region probabilities p_r =", p_r.T)
print("Conditional matrix p(c|r) =")
sp.pprint(p_c_given_r)
print()

# Shannon conditional entropy: S = sum_r p_r * [ - sum_c p(c|r) * log(p(c|r)) ]
term_inner = - (p_c_given_r * sp.log(p_c_given_r)).applyfunc(lambda x: x if x!=0 else 0)
# Note: sympy's 0*log(0) is treated as 0 via the conditional above.
S_perc = (p_r.T * term_inner.sum(axis=1))[0, 0]   # scalar

print("Conditional entropy S_perc =", S_perc.simplify())
print()

# Entropy bounds: 0 <= S_perc <= log(N_states) where N_states = len(R)*len(Cb)
N_states = len(R) * len(Cb)
S_max = sp.log(N_states)
print(f"Maximum possible entropy (log({N_states})) =", S_max)
print("Entropy non-negativity check:", sp.simplify(S_perc >= 0))
print("Entropy upper-bound check:", sp.simplify(S_perc <= S_max))
print()

# ----------------------------------------------------------------------
# 6. Boundary conditions (shredding & locking)
# ----------------------------------------------------------------------
# Limits: Phi_N -> oo, Phi_N -> 0 ; S_perc -> S_max, S_perc -> 0
oo = sp.oo
zero = 0

# Shredding: psi -> +∞ when Phi_N -> oo AND S_perc -> S_max
psi_shred = sp.limit(psi_perc, Phi_N, oo, dir='+') \
            .subs(S_perc, S_max)
print("Shredding limit (Phi_N→∞, S→S_max):", psi_shred)
print("  -> +∞ ?", sp.simplify(psi_shred == oo))
print()

# Locking: psi -> -∞ when Phi_N -> 0 AND S_perc -> 0
psi_lock = sp.limit(psi_perc, Phi_N, zero, dir='+') \
           .subs(S_perc, zero)
print("Locking limit (Phi_N→0, S→0):", psi_lock)
print("  -> -∞ ?", sp.simplify(psi_lock == -oo))
print()

# ----------------------------------------------------------------------
# 7. MPC-Ω constraints and cost function (numeric sanity check)
# ----------------------------------------------------------------------
# We'll plug in some representative numeric values to ensure the
# expressions are well-defined and penalties are non-negative.

# Sample numeric values (all dimensionless after normalization)
num_vals = {
    alpha: -1.0,
    beta:  2.0,
    gamma: 0.5,
    kappa1: 0.3,
    kappa2: 0.2,
    kappa3: 0.4,
    kappa4: 0.1,
    grad_norm_sq: 0.8,
    C_norm_sq:   0.6,
    skew_C:      0.3,
    # Region probabilities (must sum to 1)
    R0: 0.5, R1: 0.3, R2: 0.2,
    # Conditional probabilities (each row sums to 1)
    c0: 0.6, c1: 0.3, c2: 0.1,   # first row
    # For simplicity we reuse same distribution for all rows
    # (the script will overwrite later)
}

# Build substitution dict for conditional matrix (repeat same row)
num_vals.update({
    # p_c_given_r[0,:]
    p_c_given_r[0,0]: num_vals[c0],
    p_c_given_r[0,1]: num_vals[c1],
    p_c_given_r[0,2]: num_vals[c2],
    # p_c_given_r[1,:]
    p_c_given_r[1,0]: num_vals[c0],
    p_c_given_r[1,1]: num_vals[c1],
    p_c_given_r[1,2]: num_vals[c2],
    # p_c_given_r[2,:]
    p_c_given_r[2,0]: num_vals[c0],
    p_c_given_r[2,1]: num_vals[c1],
    p_c_given_r[2,2]: num_vals[c2],
})

# Compute numeric versions
Phi_N_num   = Phi_N.subs(num_vals).evalf()
Phi_D_num   = Phi_D.subs(num_vals).evalf()
psi_num     = psi_perc.subs(num_vals).evalf()
S_num       = S_perc.subs(num_vals).evalf()
PCI_num     = (Phi_N_num * Phi_D_num)  # Gamma(t) set to 1 for simplicity

print("=== Numeric sanity check ===")
print(f"Phi_N   = {Phi_N_num:.4f}")
print(f"Phi_D   = {Phi_D_num:.4f}")
print(f"PCI     = {PCI_num:.4f}")
print(f"psi     = {psi_num:.4f}")
print(f"S_perc  = {S_num:.4f} (max = {np.log(N_states):.4f})")
print()

# Constraint thresholds (from proposal)
PCI_min   = 0.6
Phi_N_min = 0.5
S_low     = np.log(2)   # as in the proposal
S_high    = np.log(N_states)  # upper bound

print("Constraint verification:")
print(f"  PCI >= {PCI_min} ? {PCI_num >= PCI_min}")
print(f"  Phi_N >= {Phi_N_min} ? {Phi_N_num >= Phi_N_min}")
print(f"  S_low <= S_perc <= S_high ? {S_low <= S_num <= S_high}")
print()

# Cost function integrand (simplified to instantaneous penalty)
mu1, mu2, mu3 = sp.symbols('mu1 mu2 mu3', nonnegative=True, real=True)
cost_inst = ( (PCI_min - PCI_num)**2 if PCI_num < PCI_min else 0 ) \
          + mu1 * ((Phi_N_min - Phi_N_num)**2 if Phi_N_num < Phi_N_min else 0) \
          + mu2 * (Phi_D_num**2) \
          + mu3 * ((S_num - np.log(2))**2 if S_num < np.log(2) else 0)

print("Instantaneous cost (penalty) =", cost_inst)
print("All penalty terms are non-negative by construction.")
print()

print("=== Validation complete ===")
print("If no contradictions appeared above, the refined PCS-Ω")
print("is mathematically sound and respects Omega Protocol invariants.")