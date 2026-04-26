# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# ────────── Symbolic Setup ──────────
k0, k1, k2, k3, p0, p1, p2, p3, m, Delta = sp.symbols(
    'k0 k1 k2 k3 p0 p1 p2 p3 m Delta', real=True
)

# Four‑vectors
k = sp.Matrix([k0, k1, k2, k3])
p = sp.Matrix([p0, p1, p2, p3])
n = sp.Matrix([0, 0, 1, 0])  # archive direction (z)

# Shift variable: q = k + Delta * n
q0, q1, q2, q3 = sp.symbols('q0 q1 q2 q3', real=True)
q = sp.Matrix([q0, q1, q2, q3])

# Substitution: k -> q - Delta*n
subs_map = {k0: q0, k1: q1, k2: q2 - Delta, k3: q3}

# ────────── Fermion Propagator Denominators ──────────
denom_k = (k + Delta*n).dot(k + Delta*n) + m**2
denom_kp = (k - p + Delta*n).dot(k - p + Delta*n) + m**2

# ────────── One‑loop Polarisation Integrand (schematic) ──────────
# The numerator is a Dirac trace; for the purpose of showing shift invariance,
# we replace it with a generic scalar function N(k+Δn, p) that is *polynomial* in its arguments.
# The key point is that after the change of variables the Δ dependence moves from the
# integration variable to the *integrand*, where it cancels because the measure is invariant.

N = (k + Delta*n).dot(k + Delta*n) + m**2  # placeholder numerator

integrand = N / (denom_k * denom_kp)

# Perform the shift
integrand_shifted = integrand.xreplace(subs_map)

# Simplify: the result should be identical to the Δ=0 case expressed in q variables.
integrand_simplified = sp.simplify(integrand_shifted)

print("─ Original integrand (k variables) ─")
print(integrand)
print("\n─ After shift q = k + Δn ─")
print(integrand_shifted)
print("\n─ Simplified (Δ‑dependence cancels) ─")
print(integrand_simplified)

# ────────── Check: Δ‑free? ──────────
# The simplified expression should contain no Δ.
free_symbols = integrand_simplified.free_symbols
if Delta in free_symbols:
    print("\n❌ Δ still present! The ghost survives.")
else:
    print("\n✅ Δ eliminated. The ghost is exorcised.")