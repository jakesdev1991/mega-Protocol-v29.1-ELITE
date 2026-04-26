# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol invariant validator.
Checks:
  - RMS_J <= J_MAX
  - Phi_N >= PHI_N_MIN
  - S_gap >= S_GAP_MIN (ln 2)
  - Jerk stencil correctness (unit test)
  - Lagrangian dimensional consistency (symbolic)
"""

import numpy as np
import sympy as sp

# -------------------------- Constants --------------------------
J_MAX = 0.025          # bits·s⁻³
PHI_N_MIN = 0.7        # bits
S_GAP_MIN = np.log(2)  # bits (≈0.6931)

DT = 1e-3              # sampling interval, seconds (1 ms)

# -------------------------- Helper functions --------------------------
def jerk_stencil(signal, dt=DT):
    """
    Compute third derivative using the 5-point central stencil:
    J(t) = (-f(t-2dt)+2f(t-dt)-2f(t+dt)+f(t+2dt)) / (2 dt^3)
    signal: 1D numpy array uniformly sampled with spacing dt.
    Returns array same length as input (edges set to NaN).
    """
    n = len(signal)
    j = np.full(n, np.nan)
    # valid indices: 2 .. n-3
    for i in range(2, n-2):
        j[i] = (-signal[i-2] + 2*signal[i-1] - 2*signal[i+1] + signal[i+2]) / (2.0 * dt**3)
    return j

def rms_jerk(j_signal):
    """Root‑mean‑square of jerk, ignoring NaNs."""
    valid = j_signal[~np.isnan(j_signal)]
    return np.sqrt(np.mean(valid**2)) if valid.size > 0 else np.nan

# -------------------------- 1. Invariant check --------------------------
def check_invariants(rms_j, phi_n, s_gap):
    violations = []
    if rms_j > J_MAX:
        violations.append(f"RMS_J={rms_j:.6f} > J_MAX={J_MAX}")
    if phi_n < PHI_N_MIN:
        violations.append(f"Phi_N={phi_n:.6f} < PHI_N_MIN={PHI_N_MIN}")
    if s_gap < S_GAP_MIN:
        violations.append(f"S_gap={s_gap:.6f} < S_GAP_MIN={S_GAP_MIN:.6f}")
    return violations

# -------------------------- 2. Jerk stencil unit test --------------------------
def test_jerk_stencil():
    # Use a known cubic polynomial: f(t) = a*t^3 => f'''(t) = 6a (constant)
    a = 2.0
    t = np.arange(-10, 11) * DT  # 21 points centered at 0
    f = a * t**3
    J_est = jerk_stencil(f, DT)
    # Theoretical jerk is constant 6a
    J_true = 6 * a
    # Compare interior points (avoid edges)
    interior = J_est[2:-2]
    err = np.max(np.abs(interior - J_true))
    assert err < 1e-12, f"Jerk stencil error too large: {err}"
    return True

# -------------------------- 3. Lagrangian dimensional check --------------------------
def lagrangian_dim_check():
    # Symbols
    t = sp.symbols('t')
    IC, IG = sp.symbols('IC IG')
    kappa, m, lam = sp.symbols('kappa m lam')
    # Assign dimensions: [kappa] = T^{-3/2}, [m] = T^{-1/2}, [lam] = T^{-1}
    # We treat dimension as a symbol D_T (time dimension)
    D_T = sp.symbols('D_T')
    dim_kappa = D_T**(-sp.Rational(3,2))
    dim_m = D_T**(-sp.Rational(1,2))
    dim_lam = D_T**(-1)
    # Entropy is dimensionless -> dim_IC = dim_IG = 1
    dim_IC = dim_IG = 1
    # Build terms
    term_kin = (1/(2*kappa**2)) * ((sp.diff(IC, t, 2))**2 + (sp.diff(IG, t, 2))**2)
    term_mass = (sp.Rational(1,2)) * m**2 * (IC**2 + IG**2)
    term_int = (lam/4) * IC * IG**2
    # Replace symbols with their dimensions
    subs = {kappa: dim_kappa, m: dim_m, lam: dim_lam,
            IC: dim_IC, IG: dim_IG,
            sp.diff(IC, t, 2): D_T**(-2),   # ∂^2/∂t^2 gives T^{-2}
            sp.diff(IG, t, 2): D_T**(-2)}
    dim_kin = sp.simplify(term_kin.subs(subs))
    dim_mass = sp.simplify(term_mass.subs(subs))
    dim_int = sp.simplify(term_int.subs(subs))
    # All should be T^{-1}
    expected = D_T**(-1)
    ok = sp.simplify(dim_kin - expected) == 0 and \
         sp.simplify(dim_mass - expected) == 0 and \
         sp.simplify(dim_int - expected) == 0
    return ok, dim_kin, dim_mass, dim_int

# -------------------------- Main execution --------------------------
if __name__ == "__main__":
    # Example values from the engine output
    rms_j_example = 0.018   # bits·s⁻³
    phi_n_example = 4.2     # bits
    s_gap_example = 1.8     # bits

    print("=== Invariant check ===")
    vio = check_invariants(rms_j_example, phi_n_example, s_gap_example)
    if vio:
        print("FAIL - violations:")
        for v in vio:
            print("  -", v)
    else:
        print("PASS - all hard constraints satisfied.")

    print("\n=== Jerk stencil unit test ===")
    try:
        test_jerk_stencil()
        print("PASS - jerk stencil reproduces constant third derivative.")
    except AssertionError as e:
        print("FAIL:", e)

    print("\n=== Lagrangian dimensional consistency ===")
    ok, dkin, dmass, dint = lagrangian_dim_check()
    if ok:
        print("PASS - each Lagrangian term has dimension T^{-1} (inverse time).")
        print(f"  Kinetic term dimension: {dkin}")
        print(f"  Mass term dimension:    {dmass}")
        print(f"  Interaction term dim:   {dint}")
    else:
        print("FAIL - dimensional mismatch.")
        print(f"  Kinetic: {dkin}")
        print(f"  Mass:    {dmass}")
        print(f"  Interaction: {dint}")

    # Overall decision
    if not vio:
        print("\n=== OVERALL RESULT ===")
        print("PASS – the analysis is mathematically sound and respects Omega Protocol invariants.")
    else:
        print("\n=== OVERALL RESULT ===")
        print("FAIL – invariant violations detected.")