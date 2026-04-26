# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Validator for CSTCL‑Ω
Checks:
  1. Invariant ψ = ln(phi_n) matches RG scaling.
  2. Boundary orientation (Shredding vs Freeze).
  3. Control-law sign yields increasing distance from criticality.
"""

import numpy as np

# ----------------------------------------------------------------------
# User‑defined parameters (representative values)
# ----------------------------------------------------------------------
S_crit   = 1.0      # critical shear flow (arb. units)
nu_S     = 0.5      # critical exponent for shear flow
gamma    = 0.1      # control gain (>0)
m0       = 1.0      # reference mass scale
C_const  = 0.0      # additive constant in RG psi expression (absorbed)
# ----------------------------------------------------------------------


def phi_n_from_S(S):
    """
    Effective mass ratio φ_n = m_eff / m0.
    Near the fixed point m_eff^2 ∝ |S - S_crit|^(2*nu_S)  →  m_eff ∝ |S-S_crit|^nu_S
    (up to a positive constant which we set to 1 for the test).
    """
    return np.abs(S - S_crit) ** nu_S   # φ_n ∝ |ΔS|^ν_S


def psi_from_phi_n(phi_n):
    """Rubric‑exact invariant."""
    return np.log(phi_n)               # ψ = ln(φ_n)


def psi_from_RG(S):
    """RG‑derived expression (should match psi_from_phi_n up to const)."""
    return -nu_S * np.log(np.abs(S - S_crit)) + C_const


def control_law_dotS(S, psi):
    """
    Control law as written in the proposal:
        dotS = -gamma * sign(S - S_crit) * exp(-psi/nu_S)
    Returns the derivative dS/dt.
    """
    return -gamma * np.sign(S - S_crit) * np.exp(-psi / nu_S)


def distance_derivative(S, dotS):
    """
    d|ΔS|/dt = sign(ΔS) * dotS.
    Positive → distance from criticality grows.
    """
    return np.sign(S - S_crit) * dotS


def run_tests():
    print("=== Ω‑Protocol CSTCL‑Ω Validator ===\n")
    test_points = [0.5, 0.8, 0.9, 1.1, 1.2, 1.5]  # S values around S_crit

    all_ok = True
    for S in test_points:
        phi_n = phi_n_from_S(S)
        psi_phi = psi_from_phi_n(phi_n)
        psi_rg  = psi_from_RG(S)

        # 1. Invariant consistency (allow tolerance)
        inv_ok = np.isclose(psi_phi, psi_rg, atol=1e-6)
        if not inv_ok:
            all_ok = False
            print(f"[FAIL] S={S:.3f}: ψ mismatch "
                  f"(ψ_phi={psi_phi:.6f}, ψ_RG={psi_rg:.6f})")

        # 2. Boundary orientation
        #   Shredding (ξ→∞) ↔ φ_n→0 ↔ ψ→ -∞
        #   Freeze   (ξ→0)  ↔ φ_n→∞ ↔ ψ→ +∞
        #   We simply check monotonicity: ψ decreases as |ΔS|→0.
        #   For two points closer/farther we can test numerically.
        #   Here we assert that ψ_phi is decreasing with decreasing |ΔS|.
        #   (We'll test pairwise later.)

        # 3. Control‑law stability
        dotS = control_law_dotS(S, psi_phi)
        d_dist = distance_derivative(S, dotS)
        stable = d_dist > 0  # should increase distance
        if not stable:
            all_ok = False
            print(f"[FAIL] S={S:.3f}: control law drives *toward* criticality "
                  f"(d|ΔS|/dt={d_dist:.6f})")

        # Optional: print diagnostics
        print(f"S={S:.3f}: φ_n={phi_n:.4f}, ψ={psi_phi:.4f}, "
              f"dotS={dotS:.4f}, d|ΔS|/dt={d_dist:.4f}")

    # Pairwise monotonicity check for ψ vs |ΔS|
    print("\n--- Monotonicity of ψ vs |ΔS| ---")
    sorted_S = sorted(test_points, key=lambda x: np.abs(x - S_crit))
    prev_psi = None
    for S in sorted_S:
        psi = psi_from_phi_n(phi_n_from_S(S))
        if prev_psi is not None:
            # As |ΔS| gets smaller, ψ should decrease (more negative)
            if psi > prev_psi + 1e-12:   # allow tiny numerical noise
                all_ok = False
                print(f"[FAIL] ψ not monotonic decreasing: "
                      f"|ΔS|={np.abs(S-S_crit):.4f} → ψ={psi:.4f} "
                      f"(prev ψ={prev_psi:.4f})")
            else:
                print(f"OK  |ΔS|={np.abs(S-S_crit):.4f} → ψ={psi:.4f}")
        prev_psi = psi

    print("\n=== RESULT ===")
    if all_ok:
        print("PASS: All Ω‑invariant checks satisfied.")
    else:
        print("FAIL: One or more Ω‑invariant checks violated.")
    return all_ok


if __name__ == "__main__":
    run_tests()