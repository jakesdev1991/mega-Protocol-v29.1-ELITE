# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
TDIS-Ω mathematical sanity checker.
Verifies:
  * Positivity of invariants (Phi_N, Phi_Delta, S_backup)
  * BII range and ability to satisfy constraint BII >= 0.9
  * Double-well potential shape (two minima at B~0 and B~1)
  * Current conservation ∂_μ J^μ = 0 for the given J^mu form
  * Non-negative action density (kinetic + potential >= 0)
"""

import numpy as np

# ------------------ User‑definable parameters ------------------
# These are placeholders; in a real audit they'd be extracted from the proposal.
alpha   = -0.5      # quadratic coeff of V(B) – must be <0 for double-well
beta    = 2.0       # quartic coeff (>0)
B_opt   = 0.5       # expected centre of the wells
PhiN0   = 1.0       # reference Phi_N
eta1    = 0.3
eta2    = 0.2
alpha_BII, beta_BII, gamma_BII = 1.0, 1.0, 1.0   # gains in BII tanh
# --------------------------------------------------------------

def V(B):
    """Double‑well potential."""
    return 0.5*alpha*(B-B_opt)**2 + 0.25*beta*(B-B_opt)**4

def BII(val_cons, PhiN, PhiDelta):
    """Backup Integrity Index as defined in the proposal."""
    arg = alpha_BII*val_cons + beta_BII*PhiN - gamma_BII*PhiDelta
    return np.tanh(arg)

def check_potential():
    """Inspect V(B) for two minima near 0 and 1."""
    Bs = np.linspace(0, 1, 1001)
    Vs = V(Bs)
    # locate minima (simple discrete approximation)
    mins = []
    for i in range(1, len(Bs)-1):
        if Vs[i] < Vs[i-1] and Vs[i] < Vs[i+1]:
            mins.append(Bs[i])
    print(f"Potential minima at B ≈ {mins}")
    # Expect minima close to 0 and 1
    ok = any(abs(m-0.0)<0.15 for m in mins) and any(abs(m-1.0)<0.15 for m in mins)
    if not ok:
        print("  ❌ Potential does NOT exhibit wells at ~0 and ~1.")
    else:
        print("  ✅ Potential shape compatible with claimed basins.")
    return ok

def check_invariants(sample_vals):
    """Check that derived invariants stay in admissible ranges."""
    PhiN, PhiDelta, S, BII_val = sample_vals
    issues = []
    if PhiN <= 0:
        issues.append(f"Phi_N = {PhiN} ≤ 0")
    if not np.isfinite(PhiDelta):
        issues.append(f"Phi_Delta not finite: {PhiDelta}")
    if S < 0:
        issues.append(f"S_backup = {S} < 0")
    if not (-1.0 <= BII_val <= 1.0):
        issues.append(f"BII = {BII_val} outside [-1,1]")
    if issues:
        print("  ❌ Invariant violations:", "; ".join(issues))
        return False
    else:
        print("  ✅ All invariants within expected bounds.")
        return True

def check_current_conservation(PhiDelta_t):
    """∂_μ J^μ = ∂_0 (sqrt(2) PhiDelta) must vanish."""
    # Approximate time derivative via finite difference
    dt = PhiDelta_t[1] - PhiDelta_t[0]
    dPhiDt = np.gradient(PhiDelta_t, dt)
    divJ = np.sqrt(2) * dPhiDt   # only time component contributes
    max_div = np.max(np.abs(divJ))
    print(f"  Max |∂_μ J^μ| = {max_div:.3e}")
    if max_div > 1e-6:
        print("  ❌ Current not conserved (Φ_Δ varying in time).")
        return False
    else:
        print("  ✅ Current conservation satisfied (Φ_Δ constant).")
        return True

def check_BII_feasibility():
    """See if there exists a plausible (val_cons, PhiN, PhiDelta) giving BII>=0.9."""
    # Scan a reasonable hyper‑cube
    val_cons = np.linspace(-2, 2, 401)
    PhiN_vals = np.linspace(0, 2, 401)
    PhiDelta_vals = np.linspace(-2, 2, 401)
    feasible = False
    for vc in val_cons:
        for pn in PhiN_vals:
            for pd in PhiDelta_vals:
                if BII(vc, pn, pd) >= 0.9:
                    feasible = True
                    break
            if feasible: break
        if feasible: break
    if feasible:
        print("  ✅ BII ≥ 0.9 achievable for some inputs.")
    else:
        print("  ❌ BII ≥ 0.9 NOT reachable with current gain choices.")
    return feasible

def main():
    print("=== TDIS-Ω Mathematical Sanity Check ===\n")
    # 1. Potential shape
    pot_ok = check_potential()
    print()
    # 2. Invariant sanity (example point)
    sample = (PhiN0 - eta1*(1-0.8) + eta2*0.7,   # PhiN from mapping with BII~0.8, S~0.7
              0.5,                               # PhiDelta placeholder
              0.7,                               # S_backup > ln(2)~0.693
              BII(0.0, sample[0], sample[1]))    # BII at zero validation consistency
    inv_ok = check_invariants(sample)
    print()
    # 3. Current conservation (assume we test a time series)
    PhiDelta_series = np.full(10, 0.5)   # constant → should pass
    curr_ok = check_current_conservation(PhiDelta_series)
    print()
    # 4. BII feasibility
    bii_ok = check_BII_feasibility()
    print()
    # Overall verdict
    all_ok = pot_ok and inv_ok and curr_ok and bii_ok
    print("=== RESULT ===")
    if all_ok:
        print("PASS – No obvious mathematical violations detected.")
    else:
        print("FAIL – One or more checks failed. See above for details.")

if __name__ == "__main__":
    main()