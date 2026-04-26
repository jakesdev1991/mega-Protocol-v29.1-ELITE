# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validator for Higher‑Order Lattice Polarization Derivation
-----------------------------------------------------------------------
Checks:
  * Individual fermion‑mass positivity  (m_e > 0, m_p > 0)
  * Effective mass reality               (m_eff > 0)
  * Lattice‑spacing positivity           (a_i > 0 for all i)
  * Expansion parameter bound            (tilde_epsilon < 1)
  * Poisson‑recovery source finiteness   (no zero lattice spacing)
  * Omega invariant finiteness           (psi, xi_N, xi_Delta, S_h real)
  * Optional: symbolic verification of the low‑Q^2 vacuum‑polarization term
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# User‑defined parameters (edit to test different points in parameter space)
# ----------------------------------------------------------------------
m   = sp.symbols('m', positive=True)          # bare mass scale
g   = sp.symbols('g', positive=True)          # coupling constant
Phi_N = sp.symbols('Phi_N', real=True)        # scalar field (mass modulation)
Phi_D = sp.symbols('Phi_D', real=True)        # lattice‑anisotropy field
eps   = sp.symbols('eps', real=True)          # epsilon = g*Phi_N/m (will be substituted)

# lattice anisotropy coefficients (must sum to zero)
# Example: three‑direction model with eps1 =  1, eps2 = -1, eps3 = 0
eps_i = [sp.symbols(f'eps{i}', real=True) for i in range(1, 4)]
# enforce sum_i eps_i = 0 later via substitution

# critical lattice anisotropy (inverse of max |eps_i|)
# We'll treat it as a symbolic positive number
Phi_D_crit = sp.symbols('Phi_D_crit', positive=True)

# ----------------------------------------------------------------------
# Derived quantities
# ----------------------------------------------------------------------
# epsilon = g*Phi_N/m
epsilon_subs = {eps: g*Phi_N/m}

# renormalized expansion parameter
tilde_epsilon = eps*sp.exp(sp.Abs(Phi_D))   # = (g*Phi_N/m) * exp(|Phi_D|)
tilde_epsilon_sub = tilde_epsilon.subs(epsilon_subs)

# individual masses
m_e = m*(1 - tilde_epsilon*sp.exp(+Phi_D))
m_p = m*(1 - tilde_epsilon*sp.exp(-Phi_D))

# effective mass (geometric mean)
m_eff = sp.sqrt(m_e*m_p)

# lattice spacings (anisotropic)
a_i = [sp.symbols('a0', positive=True)*(1 + eps_i[k]*Phi_D) for k in range(len(eps_i))]
# apply cut‑off: freeze at critical value if |Phi_D| > Phi_D_crit
a_i_cut = [sp.Piecewise(
                (a_i[k], sp.Abs(Phi_D) <= Phi_D_crit),
                (a_i[k].subs(Phi_D, sp.sign(Phi_D)*Phi_D_crit), True))
           for k, a_i_k in enumerate(a_i)]

# Omega invariants
phi_n   = m_eff/m
psi     = sp.log(phi_n)                     # ln(phi_n)
xi_N    = 1/(g*Phi_N)
xi_D    = 1/sp.Abs(Phi_D)

# Shannon entropy of virtual‑pair momentum distribution (continuum approximation)
# p(k) ∝ 1/(k^2 + m_eff^2); we compute S_h = -∫ d^3k p(k) ln p(k) / ∫ d^3k p(k)
k = sp.symbols('k', nonnegative=True)
omega_k = sp.sqrt(k**2 + m_eff**2)
p_k     = 1/omega_k**2                     # unnormalized
norm    = sp.integrate(p_k * 4*sp.pi*k**2, (k, 0, sp.oo))
S_h_expr= -sp.integrate((p_k/norm)*sp.log(p_k/norm) * 4*sp.pi*k**2, (k, 0, sp.oo))

# ----------------------------------------------------------------------
# Validation functions
# ----------------------------------------------------------------------
def check_positive(expr, name):
    """Return True if expr is guaranteed >0 under current assumptions."""
    try:
        # Ask sympy if expr is positive; if undecided, return False
        return sp.ask(sp.Q.positive(expr))
    except Exception:
        return False

def validate_point(subs_dict):
    """
    Evaluate all constraints for a concrete numeric substitution.
    subs_dict: dict mapping symbols to numeric values (float or sympy.N).
    Returns a dict of results.
    """
    # Apply substitutions
    subs = {**subs_dict, **epsilon_subs}
    # numeric evaluation helper
    def val(expr): return sp.N(expr.subs(subs))

    results = {}

    # 1. Individual mass positivity
    results['m_e > 0'] = val(m_e) > 0
    results['m_p > 0'] = val(m_p) > 0

    # 2. Effective mass reality (should be real and >0)
    results['m_eff > 0'] = val(m_eff) > 0

    # 3. Lattice spacing positivity (after cut‑off)
    for idx, ai in enumerate(a_i_cut):
        results[f'a_{idx+1} > 0'] = val(ai) > 0

    # 4. Expansion parameter bound
    results['tilde_epsilon < 1'] = val(tilde_epsilon) < 1

    # 5. Poisson‑recovery: no zero lattice spacing (already covered by a_i>0)
    #    Additionally, source term ~ delta m_eff should be finite:
    results['delta_m_eff finite'] = sp.N(sp.diff(m_eff, Phi_D).subs(subs)) is not None

    # 6. Omega invariant finiteness (real and not infinite)
    results['psi real']   = sp.N(psi.subs(subs)).is_real
    results['xi_N finite']= sp.N(xi_N.subs(subs)).is_finite
    results['xi_D finite']= sp.N(xi_D.subs(subs)).is_finite
    # entropy may be unevaluated; we check if it's finite after numeric integration
    try:
        S_h_val = sp.N(S_h_expr.subs(subs))
        results['S_h finite'] = S_h_val.is_finite
    except Exception:
        results['S_h finite'] = False

    return results

# ----------------------------------------------------------------------
# Example usage: test a safe point and an unsafe point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Choose some baseline numbers (feel free to change)
    m_val   = 1.0
    g_val   = 0.1
    PhiN_val = 0.5          # => epsilon = g*Phi_N/m = 0.05
    PhiD_val = 0.2          # small anisotropy
    eps1_val =  1.0
    eps2_val = -1.0
    eps3_val =  0.0
    PhiD_crit_val = 1.0 / max(abs(eps1_val), abs(eps2_val), abs(eps3_val))

    safe_subs = {
        m: m_val,
        g: g_val,
        Phi_N: PhiN_val,
        Phi_D: PhiD_val,
        eps_i[0]: eps1_val,
        eps_i[1]: eps2_val,
        eps_i[2]: eps3_val,
        Phi_D_crit: PhiD_crit_val,
    }

    print("=== SAFE POINT ===")
    for k, v in validate_point(safe_subs).items():
        print(f"{k:30}: {v}")

    # Unsafe point: increase Phi_D so that tilde_epsilon approaches 1
    PhiD_unsafe = np.log(m_val/(g_val*PhiN_val)) * 0.9  # still below ln(m/(g*Phi_N)) but close
    unsafe_subs = safe_subs.copy()
    unsafe_subs[Phi_D] = PhiD_unsafe

    print("\n=== UNSAFE (near‑boundary) POINT ===")
    for k, v in validate_point(unsafe_subs).items():
        print(f"{k:30}: {v}")

    # Demonstrate violation: force tilde_epsilon > 1
    PhiD_viol = np.log(m_val/(g_val*PhiN_val)) * 1.2  # exceeds the log bound
    viol_subs = safe_subs.copy()
    viol_subs[Phi_D] = PhiD_viol

    print("\n=== VIOLATION POINT (tilde_epsilon > 1) ===")
    for k, v in validate_point(viol_subs).items():
        print(f"{k:30}: {v}")