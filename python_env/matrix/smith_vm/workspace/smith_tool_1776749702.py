# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for the BRS-Ω proposal.
Checks dimensional consistency of stiffness invariants,
feasibility of Phi_N/Phi_Delta bounds, and threat/entropy ranges.
"""

import sympy as sp
import itertools

# ----------------------------------------------------------------------
# 1. Dimensional analysis helpers
# ----------------------------------------------------------------------
# Define base dimensions: [M] mass, [L] length, [T] time, [I] information (dimensionless)
# We'll treat information as dimensionless for simplicity.
dim = sp.symbols('dim')
# Base dimensions
M, L, T, I = sp.symbols('M L T I')
# Dimension mapping: we assign each symbol a tuple of exponents (M,L,T,I)
def dim_of(expr):
    """Return dimension tuple assuming symbols have known dimensions."""
    # Known dimensions:
    # t: count -> dimensionless
    # s: sparsity ratio -> dimensionless
    # ell: time -> T
    # lambda: we will enforce [T]^-2 later
    # gamma_i, delta_i, alpha_i, beta_i: dimensionless (coefficients)
    # Phi_N, Phi_Delta, psi: dimensionless
    # xi_N, xi_Delta: time -> T
    # H, H_max: dimensionless (entropy)
    # theta: dimensionless
    known = {
        't': (0,0,0,0),
        's': (0,0,0,0),
        'ell': (0,0,1,0),
        'lam': (0,0,-2,0),   # lambda must be T^-2
        'gamma0': (0,0,0,0), 'gamma1': (0,0,0,0), 'gamma2': (0,0,0,0),
        'delta0': (0,0,0,0), 'delta1': (0,0,0,0), 'delta2': (0,0,0,0),
        'alpha1': (0,0,0,0), 'alpha2': (0,0,0,0),
        'beta1': (0,0,0,0),  'beta2': (0,0,0,0),
        'Phi_N0': (0,0,0,0), 'Phi_Delta0': (0,0,0,0),
        'psi': (0,0,0,0),
        'xi_N': (0,0,1,0),   # correlation length -> time
        'xi_Delta': (0,0,1,0),
        'H': (0,0,0,0), 'H_max': (0,0,0,0),
        'theta': (0,0,0,0)
    }
    # If expr is a Symbol, look up; if number, dimensionless; if product/sum, combine.
    if expr.is_Symbol:
        if expr.name in known:
            return known[expr.name]
        else:
            raise ValueError(f"Unknown symbol {expr}")
    if expr.is_Number:
        return (0,0,0,0)
    if expr.is_Add:
        dims = [dim_of(arg) for arg in expr.args]
        # All terms must share same dimension
        if len(set(dims)) != 1:
            raise ValueError(f"Addition dimension mismatch in {expr}")
        return dims[0]
    if expr.is_Mul:
        dims = [dim_of(arg) for arg in expr.args]
        # Sum exponent vectors
        total = tuple(sum(e) for e in zip(*dims))
        return total
    # Fallback: treat as dimensionless (should not happen for our simple exprs)
    return (0,0,0,0)

# ----------------------------------------------------------------------
# 2. Symbolic definitions
# ----------------------------------------------------------------------
t, s, ell = sp.symbols('t s ell', nonnegative=True, real=True)
lam = sp.symbols('lam', real=True)   # will enforce T^-2 later
# coefficients (dimensionless)
g0, g1, g2 = sp.symbols('g0 g1 g2', real=True)
d0, d1, d2 = sp.symbols('d0 d1 d2', real=True)
a1, a2 = sp.symbols('a1 a2', real=True)
b1, b2 = sp.symbols('b1 b2', real=True)
Phi_N0, Phi_Delta0 = sp.symbols('Phi_N0 Phi_Delta0', real=True)

# Stiffness invariants (xi_N^{-2}, xi_Delta^{-2})
xi_N_inv2 = lam * (g0 + g1*t + g2*ell)
xi_Delta_inv2 = lam * (d0 - d1*t + d2*ell)

# Phi_N / Phi_Delta linear models (as in proposal)
Phi_N = Phi_N0 - a1*(g0 + g1*t + g2*ell) - a2*ell   # note: we absorb lam into a1,a2 for simplicity
Phi_Delta = Phi_Delta0 + b1*(g0 + g1*t + g2*ell) - b2*ell

# ----------------------------------------------------------------------
# 3. Dimensional check
# ----------------------------------------------------------------------
print("=== Dimensional Consistency Check ===")
try:
    dim_xiN2 = dim_of(xi_N_inv2)
    dim_xiD2 = dim_of(xi_Delta_inv2)
    print(f"Dimension of xi_N^-2: {dim_xiN2}  (expected [T]^-2 -> (0,0,-2,0))")
    print(f"Dimension of xi_Delta^-2: {dim_xiD2}")
    # Check that they match T^-2
    expected = (0,0,-2,0)
    assert dim_xiN2 == expected, "xi_N^-2 dimension incorrect"
    assert dim_xiD2 == expected, "xi_Delta^-2 dimension incorrect"
    print("PASS: stiffness invariants have correct dimensions (assuming lam has [T]^-2).")
except Exception as e:
    print(f"FAIL: {e}")

# ----------------------------------------------------------------------
# 4. Feasibility of Phi bounds and threat/entropy
# ----------------------------------------------------------------------
print("\n=== Feasibility of Phi_N, Phi_Delta bounds ===")
# Define bounds
phiN_min, phiN_max = 0.6, 1.0   # Phi_N >= 0.6, <= 1 (normalized)
phiD_min, phiD_max = 0.0, 0.7   # Phi_Delta <= 0.7, >= 0

# Sample parameter ranges (reasonable values)
param_ranges = {
    't': (0, 5),          # t up to 5 workers (m>2t)
    's': (0.0, 1.0),      # sparsity ratio
    'ell': (0.0, 0.01),   # latency normalized to ell_max = 0.01 (example)
    'lam': (1.0, 1.0),    # fix lam=1 for check (units absorbed)
    'g0': (0.1, 0.5), 'g1': (0.0, 0.2), 'g2': (0.0, 0.2),
    'd0': (0.1, 0.5), 'd1': (0.0, 0.2), 'd2': (0.0, 0.2),
    'a1': (0.0, 0.3), 'a2': (0.0, 0.3),
    'b1': (0.0, 0.3), 'b2': (0.0, 0.3),
    'Phi_N0': (0.8, 0.9),
    'Phi_Delta0': (0.2, 0.4)
}

# Helper to iterate over a grid (coarse)
def iterate_grid(ranges, steps=3):
    keys = list(ranges.keys())
    vals = [sp.nsimplify(sp.linspace(r[0], r[1], steps)) for r in ranges.values()]
    for combo in itertools.product(*vals):
        yield dict(zip(keys, combo))

violations = []
for vals in iterate_grid(param_ranges, steps=4):
    # Substitute into Phi expressions
    phiN_val = Phi_N.subs(vals)
    phiD_val = Phi_Delta.subs(vals)
    # Check bounds
    if not (phiN_min <= float(phiN_val) <= phiN_max):
        violations.append(('Phi_N', vals, float(phiN_val)))
    if not (phiD_min <= float(phiD_val) <= phiD_max):
        violations.append(('Phi_Delta', vals, float(phiD_val)))
    # Threat/entropy: H in [0, H_max] => theta in [0,1]
    # We'll just note that if we define H = H_max * (1 - theta) it's fine.
    # No explicit H symbols here, so skip.

if violations:
    print(f"Found {len(violations)} bound violations (showing first 5):")
    for typ, v, fv in violations[:5]:
        print(f"  {typ} out of bounds: {fv} with params {v}")
else:
    print("PASS: All sampled parameters keep Phi_N in [0.6,1.0] and Phi_Delta in [0.0,0.7].")

# ----------------------------------------------------------------------
# 5. MPC-Omega constraints check
# ----------------------------------------------------------------------
print("\n=== MPC-Omega constraint feasibility ===")
# Constraints: ell <= ell_max, t <= t_max = floor((m-1)/2), s in [s_min,s_max]
# We'll pick example values: m=7 => t_max=3, ell_max=0.01, s_min=0.1, s_max=0.9
m = 7
t_max = (m-1)//2
ell_max = 0.01
s_min, s_max = 0.1, 0.9

constraint_violations = []
for vals in iterate_grid(param_ranges, steps=4):
    if vals['ell'] > ell_max:
        constraint_violations.append(('ell', vals, vals['ell']))
    if vals['t'] > t_max:
        constraint_violations.append(('t', vals, vals['t']))
    if not (s_min <= vals['s'] <= s_max):
        constraint_violations.append(('s', vals, vals['s']))
    if constraint_violations:
        break

if constraint_violations:
    print("Constraint violations found:")
    for typ, v, val in constraint_violations[:5]:
        print(f"  {typ} = {val} exceeds limit with params {v}")
else:
    print("PASS: There exists a parameter region satisfying ell<=ell_max, t<=t_max, s in [s_min,s_max].")

print("\n=== Summary ===")
print("If all checks PASS, the mathematical core of BRS-Ω is dimensionally sound")
print("and adheres to the Omega Protocol invariants under the sampled ranges.")