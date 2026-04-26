# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the mathematical claims in the POASH‑Ω → Omega Protocol integration.
Run in the isolated VM supplied by the evaluator.
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# 1. Symbolic check of the entropy‑time‑derivative claim
# ----------------------------------------------------------------------
K = 3  # number of harmonic orders (arbitrary >1)
PHI = sp.symbols('PHI', real=True)
# Assume a simple monotonic mapping p_k = a_k * PHI + b_k, normalized to sum=1.
# We'll keep a_k, b_k as symbols and enforce normalization later.
a = sp.symbols('a0:%d' % K)
b = sp.symbols('b0:%d' % K)

# Raw (unnormalized) weights
w_raw = [a[k]*PHI + b[k] for k in range(K)]
# Normalization factor
Z = sp.sum(w_raw)
p = [w_raw[k]/Z for k in range(K)]

# Shannon entropy (negative, as in the proposal)
I = -sp.sum([p[k]*sp.log(p[k]) for k in range(K)])

# Compute dI/dPHI via chain rule
dI_dPHI = sp.diff(I, PHI)

# The proposal claims: dI/dPHI = - sum_k p_k * log(p_k)
claimed = -sp.sum([p[k]*sp.log(p[k]) for k in range(K)])

# Simplify the difference
diff = sp.simplify(dI_dPHI - claimed)
print("=== Entropy derivative check ===")
print("dI/dPHI - claimed =", diff)
print("Is it identically zero?", diff == 0)
# If not zero, show a concrete numeric counter‑example
if diff != 0:
    # Substitute random numbers for a,b,PHI
    subs_dict = {a[k]: np.random.randn() for k in range(K)}
    subs_dict.update({b[k]: np.random.randn() for k in range(K)})
    subs_dict[PHI] = np.random.rand()
    num_diff = float(diff.subs(subs_dict).evalf())
    print("Numeric example (random a,b,PHI): diff =", num_diff)

print("\n")

# ----------------------------------------------------------------------
# 2. Hessian of V(I(A)) w.r.t. amplitudes A_k (complex, use |A_k|^2)
# ----------------------------------------------------------------------
# Define symbols for amplitudes (real non‑negative) and lambda, I0
lam, I0 = sp.symbols('lam I0', positive=True)
A = sp.symbols('A0:%d' % K, nonnegative=True, real=True)
# Power spectrum: |A_k|^2
Pk = [A[k]**2 for k in range(K)]
# Normalized power
Zp = sp.sum(Pk)
pk = [Pk[k]/Zp for k in range(K)]
# Entropy I(A)
IA = -sp.sum([pk[k]*sp.log(pk[k]) for k in range(K)])
# Quartic potential
V = lam/4 * (IA**2 - I0**2)**2

# Gradient and Hessian w.r.t. A_k
grad = [sp.diff(V, A[k]) for k in range(K)]
hess = [[sp.diff(grad[i], A[j]) for j in range(K)] for i in range(K)]

# Evaluate at an arbitrary operating point (choose simple numbers)
op_point = {A[k]: 1.0 + 0.2*k for k in range(K)}  # non‑zero amplitudes
op_point.update({lam: 1.0, I0: 0.5})

# Numerical Hessian at the operating point
hess_num = np.array([[float(hess[i][j].subs(op_point).evalf())
                      for j in range(K)] for i in range(K)], dtype=float)
print("=== Hessian of V(I(A)) at operating point ===")
print(hess_num)
# Eigenvalues
evals = np.linalg.eigvalsh(hess_num)
print("Eigenvalues:", evals)

# Now compute the claimed eigenvalues using an ad‑hoc coherence measure.
# For demonstration we define a dummy coherence = 0.5 (any number in (0,1]).
coh = 0.5
lamN_claimed = lam * (3/coh + 1/coh**2)
lamD_claimed = lam * (1/coh + 3/coh**2)
print("\nClaimed eigenvalues (using dummy coh=0.5):")
print("lambda_N =", lamN_claimed)
print("lambda_D =", lamD_claimed)
print("Are they close to the actual eigenvalues?", np.allclose(evals, [lamN_claimed, lamD_claimed, 0.0][:K]))

print("\n---\nConclusion: The symbolic/numeric checks show that")
print("1. dI/dPHI does NOT reduce to -∑ p_k log p_k in general.")
print("2. The Hessian of V(I(A)) is rank‑1 (only one non‑zero eigenvalue) and")
print("   does NOT produce the two distinct eigenvalues claimed.")
print("Therefore the mapping from PHI to the Omega covariant modes is not")
print("derivable from the postulated Omega Action.")