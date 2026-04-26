# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Strictor Gate (v26.0) validator for meta‑scrutiny Φ‑density accounting.
Checks:
  1. Arithmetic consistency of the ledger entries.
  2. Presence of a valid Φ_N / Φ_Δ decomposition for every claimed Φ‑density.
  3. Asymmetry bound: Φ_Δ < 0.5 * Φ_N.
  4. ψ = ln(Φ_N) coupling (implicitly checked via decomposition).
"""

import math

# ----------------------------------------------------------------------
# Input data from the meta‑scrutiny report (all values in Φ units)
# ----------------------------------------------------------------------
BASE_COST = -0.22          # Cost of Engine's prior failure
GAIN      = +0.05          # Gain from confirming no major violations
COST      = -0.02          # Cost due to minor oversight in Φ‑calc
NET_DELTA = GAIN + COST    # Net effect of the meta‑scrutiny action
CUMULATIVE = BASE_COST + NET_DELTA

# ----------------------------------------------------------------------
# Helper: attempt to decompose a Φ value into (Φ_N, Φ_Δ) satisfying
#   Φ = Φ_N + Φ_Δ   and   Φ_Δ < 0.5 * Φ_N
# Returns a tuple (Φ_N, Φ_Δ) if possible, else None.
# ----------------------------------------------------------------------
def decompose_phi(phi):
    """
    Try to find a decomposition that respects the asymmetry bound.
    We search over a reasonable range for Φ_N > 0.
    """
    if phi <= 0:
        # Non‑positive Φ cannot satisfy ψ = ln(Φ_N) (log undefined) nor the bound.
        return None
    # Scan Φ_N from a small epsilon up to phi (since Φ_Δ = phi - Φ_N must be >=0 for simplicity;
    # negative Φ_Δ is allowed physically but we keep the search simple).
    for phi_n in np.linspace(1e-6, phi, 10000):
        phi_delta = phi - phi_n
        if phi_delta < 0.5 * phi_n:   # asymmetry bound
            # ψ = ln(phi_n) is automatically defined for phi_n>0
            return phi_n, phi_delta
    return None

# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------
import numpy as np  # numpy is available in the VM

def validate():
    print("=== Omega Protocol Strictor Gate Validation ===\n")
    
    # 1. Arithmetic check
    print("1. Arithmetic Consistency")
    print(f"   Base cost          : {BASE_COST:.3f} Φ")
    print(f"   Gain               : {GAIN:.3f} Φ")
    print(f"   Cost (oversight)   : {COST:.3f} Φ")
    print(f"   Net meta‑scrutiny Δ: {NET_DELTA:.3f} Φ  (expected {GAIN+COST:.3f})")
    print(f"   Cumulative ΔΦ      : {CUMULATIVE:.3f} Φ  (expected {BASE_COST+GAIN+COST:.3f})")
    arithmetic_ok = math.isclose(NET_DELTA, GAIN+COST) and \
                    math.isclose(CUMULATIVE, BASE_COST+GAIN+COST)
    print(f"   → Arithmetic OK?   : {arithmetic_ok}\n")
    
    # 2. Decomposition & invariant checks for each claimed Φ‑value
    print("2. Strictor Gate Invariant Checks (Φ_N/Φ_Δ decomposition + asymmetry bound)")
    entries = [
        ("Base Cost (Engine failure)", BASE_COST),
        ("Gain (meta‑scrutiny)", GAIN),
        ("Cost (oversight)", COST),
        ("Net meta‑scrutiny Δ", NET_DELTA),
        ("Cumulative ΔΦ", CUMULATIVE)
    ]
    all_invariant_ok = True
    for name, val in entries:
        print(f"   {name:30} : {val:+.3f} Φ")
        decomp = decompose_phi(val)
        if decomp is None:
            print(f"      → FAIL: No valid (Φ_N, Φ_Δ) decomposition satisfying Φ_Δ < 0.5·Φ_N")
            all_invariant_ok = False
        else:
            phi_n, phi_d = decomp
            psi = math.log(phi_n)
            print(f"      → OK:  Φ_N = {phi_n:+.3f}, Φ_Δ = {phi_d:+.3f}, ψ = ln(Φ_N) = {psi:.3f}")
            # Asymmetry bound already enforced in decompose_phi
    print(f"\n   → All invariant checks passed? : {all_invariant_ok}\n")
    
    # 3. Overall verdict
    print("=== Verdict ===")
    if arithmetic_ok and all_invariant_ok:
        print("PASS – The meta‑scrutiny output is mathematically sound and compliant with Omega Protocol invariants.")
    else:
        print("FAIL – Violations detected (see above).")
        if not arithmetic_ok:
            print("   - Arithmetic inconsistency.")
        if not all_invariant_ok:
            print("   - Missing or invalid Φ_N/Φ_Δ decomposition (Strictor Gate violation).")

if __name__ == "__main__":
    validate()