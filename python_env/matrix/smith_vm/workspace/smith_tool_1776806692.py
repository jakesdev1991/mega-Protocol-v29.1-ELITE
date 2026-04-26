# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol invariant validator for the Higher‑Order Lattice Polarization
derivation (Phi_N, Phi_Delta, J*).

Checks:
  1. Metric positivity:          1 + Phi_Delta > eps_metric
  2. Poisson‑recovery invariant: C = Phi_N * (1 + Phi_Delta) ≈ const
  3. Effective‑coupling unitarity: Re[Denom] > 0 and Im[Denom] == 0 (within tol)

If any check fails, a RuntimeError is raised with a diagnostic message.
"""

import sympy as sp

# ----------------------------------------------------------------------
# User‑adjustable tolerances (set by the Omega‑Protocol configuration)
# ----------------------------------------------------------------------
EPS_METRIC = 1e-6      # minimal allowed value of 1+Phi_Delta
EPS_CONST  = 1e-8      # tolerance on conservation of C
EPS_DENOM  = 1e-10     # tolerance on imaginary part of denominator
EPS_POS    = 0.0       # denominator must be strictly positive (real part)

# ----------------------------------------------------------------------
# Symbolic placeholders (the master node will substitute actual numbers)
# ----------------------------------------------------------------------
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)
# Polarisation functions – treat as generic real functions of Phi_N (and possibly momentum)
Pi_T = sp.Function('Pi_T')(Phi_N)          # isotropic polarisation
Pi_L = sp.Function('Pi_L')(Phi_N)          # longitudinal
Pi_M = sp.Function('Pi_M')(Phi_N)          # mixed

# ----------------------------------------------------------------------
# 1. Metric positivity
# ----------------------------------------------------------------------
metric_factor = 1 + Phi_Delta
metric_cond = sp.GreaterThan(metric_factor, EPS_METRIC)

# ----------------------------------------------------------------------
# 2. Poisson‑recovery invariant: C = Phi_N * (1+Phi_Delta) = const
#    We enforce that its time‑derivative (or any variation) vanishes.
#    For a static check we simply require that C does not deviate from a
#    reference value C0 supplied by the master node.
# ----------------------------------------------------------------------
C = Phi_N * metric_factor
# In practice the master node will provide C0; here we keep it symbolic.
C0 = sp.symbols('C0', real=True)
C_cond = sp.Eq(C, C0)   # equality up to EPS_CONST will be tested numerically

# ----------------------------------------------------------------------
# 3. Effective coupling denominator
#    Denom = 1 + Pi_T + Phi_Delta * (Pi_L + 2*Pi_M)
# ----------------------------------------------------------------------
Denom = 1 + Pi_T + Phi_Delta * (Pi_L + 2*Pi_M)
# Split into real and imaginary parts (sympy assumes real unless told otherwise)
Denom_re = sp.re(Denom)
Denom_im = sp.im(Denom)

denom_pos_cond = sp.GreaterThan(Denom_re, EPS_POS)
denom_imag_cond = sp.LessThan(abs(Denom_im), EPS_DENOM)

# ----------------------------------------------------------------------
# Validation function – to be called with concrete numeric substitutions
# ----------------------------------------------------------------------
def validate_omega_invariants(subs_dict, C0_val):
    """
    Parameters
    ----------
    subs_dict : dict
        Mapping {Phi_N: value, Phi_Delta: value, ...} for all symbols that
        appear in the expressions (including any needed for Pi_T, Pi_L, Pi_M).
    C0_val : float
        The reference value of the invariant C = Phi_N*(1+Phi_Delta) expected
        from the vacuum or previous timestep.

    Returns
    -------
    None
        Raises RuntimeError with a descriptive message if any invariant fails.
    """
    # Substitute numeric values
    metric_val   = metric_factor.subs(subs_dict).evalf()
    C_val        = C.subs(subs_dict).evalf()
    Denom_val    = Denom.subs(subs_dict).evalf()
    Denom_re_val = sp.re(Denom_val).evalf()
    Denom_im_val = sp.im(Denom_val).evalf()

    # 1. Metric positivity
    if metric_val <= EPS_METRIC:
        raise RuntimeError(
            f"Metric collapse: 1+Phi_Delta = {metric_val:.3e} ≤ {EPS_METRIC:.3e}"
        )

    # 2. Poisson‑recovery (C conservation)
    if abs(C_val - C0_val) > EPS_CONST:
        raise RuntimeError(
            f"Poisson‑recovery violation: C = {C_val:.6e}, "
            f"expected C0 = {C0_val:.6e} (diff > {EPS_CONST:.3e})"
        )

    # 3. Effective coupling unitarity
    if Denom_re_val <= EPS_POS:
        raise RuntimeError(
            f"Effective coupling denominator non‑positive: Re[Denom] = {Denom_re_val:.3e}"
        )
    if abs(Denom_im_val) > EPS_DENOM:
        raise RuntimeError(
            f"Effective coupling denominator has imaginary part: "
            f"Im[Denom] = {Denom_im_val:.3e} (tol {EPS_DENOM:.3e})"
        )

    # All checks passed
    return True

# ----------------------------------------------------------------------
# Example usage (for illustration only – will be replaced by real data)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Dummy numeric test – replace with actual lattice‑QCD measurements
    example_subs = {
        Phi_N: 0.02,
        Phi_Delta: -0.3,          # safely > -1
        # For the placeholder functions we give simple numbers:
        Pi_T: 0.001,
        Pi_L: 0.0005,
        Pi_M: 0.0002,
    }
    example_C0 = example_subs[Phi_N] * (1 + example_subs[Phi_Delta])

    try:
        validate_omega_invariants(example_subs, example_C0)
        print("✓ All Omega‑Protocol invariants satisfied.")
    except RuntimeError as err:
        print("✗ Invariant violation:", err)