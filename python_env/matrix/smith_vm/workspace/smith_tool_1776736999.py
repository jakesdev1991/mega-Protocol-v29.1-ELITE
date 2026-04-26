# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol – Dimensional Consistency Validator
# --------------------------------------------------------------
import sympy as sp

# ------------------------------------------------------------------
# 1. Define base dimensions (natural units: [M] = [L]^-1 = [T]^-1)
#    We'll use mass dimension as the primary unit.
# ------------------------------------------------------------------
M = sp.symbols('M', positive=True)   # mass dimension
# In natural units: length ~ M^-1, time ~ M^-1
L = M**(-1)
T = M**(-1)

# ------------------------------------------------------------------
# 2. Symbolic fields and parameters with their mass dimensions
# ------------------------------------------------------------------
# alpha_fs : dimensionless
alpha = sp.symbols('alpha', dimensionless=True)

# q^2 : momentum squared -> [M]^2
q2 = sp.symbols('q2', dimension=M**2)

# m_e^2 : electron mass squared -> [M]^2
me2 = sp.symbols('me2', dimension=M**2)

# Lambda_Delta^2 : Archive cutoff -> [M]^2
LDelta2 = sp.symbols('LDelta2', dimension=M**2)

# xi_N, xi_Delta : stiffness (length) -> [L] = M^-1
xi_N = sp.symbols('xi_N', dimension=L)
xi_Delta = sp.symbols('xi_Delta', dimension=L)
xi_0   = sp.symbols('xi_0',   dimension=L)   # reference scale

# Phi_N, Phi_Delta : covariant modes (dimensionless)
Phi_N = sp.symbols('Phi_N', dimensionless=True)
Phi_Delta = sp.symbols('Phi_Delta', dimensionless=True)

# I0 : equilibrium field value (dimensionless)
I0 = sp.symbols('I0', dimensionless=True)

# lambda (coupling in V(I)) : [M]^2 because V ~ [M]^4 and I dimensionless
lam = sp.symbols('lam', dimension=M**2)

# eta_N, eta_Delta, kappa : anomalous dimensions (dimensionless)
eta_N = sp.symbols('eta_N', dimensionless=True)
eta_D = sp.symbols('eta_D', dimensionless=True)
kappa = sp.symbols('kappa', dimensionless=True)

# ------------------------------------------------------------------
# 3. Helper to check dimensionlessness
# ------------------------------------------------------------------
def is_dimensionless(expr):
    """Return True if expr has overall mass dimension M^0."""
    dim = sp.simplify(expr.dim) if hasattr(expr, 'dim') else None
    # If the expression carries a 'dim' attribute (we set it manually), compare.
    # Otherwise, compute dimension via substitution of base symbols.
    if dim is not None:
        return dim == 1
    # Fallback: replace each symbol with its dimension and see if result is 1
    subs_dict = {
        alpha: 1,
        q2: M**2,
        me2: M**2,
        LDelta2: M**2,
        xi_N: L,
        xi_Delta: L,
        xi_0: L,
        Phi_N: 1,
        Phi_Delta: 1,
        I0: 1,
        lam: M**2,
        eta_N: 1,
        eta_D: 1,
        kappa: 1,
    }
    # Evaluate dimension by taking log of magnitude (since we only care about powers of M)
    # Use sympy's .replace to substitute each symbol with its dimension power.
    dim_expr = expr.replace(
        lambda s: s in subs_dict,
        lambda s: subs_dict[s]
    )
    # Simplify to see if any M remains
    dim_expr = sp.simplify(dim_expr)
    return dim_expr == 1

# ------------------------------------------------------------------
# 4. Build the key expressions
# ------------------------------------------------------------------
# One-loop Newtonian part
Pi_N = (alpha/(3*sp.pi)) * sp.log(q2/me2)          # dimensionless log

# One-loop Archive part (psi = ln(xi_Delta/xi_0))
psi = sp.log(xi_Delta/xi_0)
Pi_Delta = (alpha/(2*sp.pi)) * psi * sp.log(q2/LDelta2)

# Two-loop mixing term
Pi_mix = (alpha**2/(sp.pi**2)) * (Phi_Delta/Phi_N) * (sp.log(q2/me2))**2

# Total polarization (up to O(alpha^2))
Pi_total = Pi_N + Pi_Delta + Pi_mix

# RG beta functions (dimensionless Phi per d ln q)
beta_N = eta_N*Phi_N*(1 - Phi_N**2/I0**2) - kappa*Phi_Delta**2
beta_D = eta_D*Phi_Delta*(1 - Phi_Delta**2/I0**2) + kappa*Phi_N*Phi_Delta

# ------------------------------------------------------------------
# 5. Dimensional checks
# ------------------------------------------------------------------
checks = {
    "Pi_N": Pi_N,
    "Pi_Delta": Pi_Delta,
    "Pi_mix": Pi_mix,
    "Pi_total": Pi_total,
    "psi": psi,
    "beta_N": beta_N,
    "beta_D": beta_D,
}

print("=== Dimensional Consistency Check ===")
for name, expr in checks.items():
    ok = is_dimensionless(expr)
    print(f"{name:12}: {'PASS' if ok else 'FAIL'} (dimensionless? {ok})")

# ------------------------------------------------------------------
# 6. Additional invariant check: psi = ln(xi_Delta/xi_0) must be dimensionless
# ------------------------------------------------------------------
print("\nInvariant psi dimension:", is_dimensionless(psi))
print("xi_Delta/xi_0 dimension:", is_dimensionless(xi_Delta/xi_0))

# ------------------------------------------------------------------
# 7. Boundary condition: Shredding when Phi_Delta -> ∞ => beta_D -> 0?
#    We simply verify that beta_D contains Phi_Delta linearly and quadratically,
#    so a fixed point Phi_Delta* = 0 or solving beta_D=0 is possible.
# ------------------------------------------------------------------
print("\nBeta_D structure (should allow fixed points):")
print(sp.factor(beta_D))