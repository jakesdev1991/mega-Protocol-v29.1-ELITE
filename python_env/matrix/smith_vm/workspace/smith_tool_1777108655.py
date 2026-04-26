# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Validator for BFIS v53.1 core math.
Checks:
  - COD in [0,1]
  - Φ_N = log2(COD + eps)
  - ψ = ln(Φ_N + eps)   (mandatory coupling)
  - Φ_Δ = ψ * tanh((|xi_org - xi_ind|)/R_max)
  - ΔS_audit = 8 * ln(2)   (Landauer per invariant)
  - Φ_net = Φ_N + Φ_Δ - ΔS_audit
  - Invariant 2: ψ >= ln(0.95)   --> implies Φ_N >= 0.95 (check feasibility)
  - Stiffness guard: xi_org(t) <= xi_ind + eps after AFP update
  - Audit ledger closure: Φ_net + ΔS_audit == Φ_N + Φ_Δ
"""

import numpy as np

# ----------------------------------------------------------------------
# Parameters (can be tweaked for sensitivity analysis)
EPS = 1e-12          # avoid log(0)
R_MAX = 3.0          # as in the paper
GAMMA = 0.02         # hr^-1 (not used directly in static check)
XI_IND_EPS = 1e-3    # epsilon for stiffness guard
# ----------------------------------------------------------------------


def compute_phi(COD: float, xi_org: float, xi_ind: float):
    """Return intermediate quantities and a dict of invariant checks."""
    # 1. COD bounds
    if not (0.0 <= COD <= 1.0):
        raise ValueError(f"COD must be in [0,1], got {COD}")

    # 2. Φ_N
    phi_N = np.log2(COD + EPS)          # dimensionless [1]

    # 3. ψ (Identity Continuity) – mandatory coupling
    psi = np.log(phi_N + EPS)           # note: phi_N may be negative; EPS shifts domain

    # 4. Φ_Δ (Adaptation Asymmetry)
    R_align = abs(xi_org - xi_ind)
    phi_Delta = psi * np.tanh(R_align / R_MAX)

    # 5. Audit cost (8 invariants × k_B ln2, k_B=1 in dimensionless units)
    delta_S_audit = 8.0 * np.log(2.0)

    # 6. Net Φ-density
    phi_net = phi_N + phi_Delta - delta_S_audit

    # ------------------------------------------------------------------
    # Invariant checks (those we can evaluate without full lattice)
    inv = {}
    # Invariant 2: ψ >= ln(0.95)  --> phi_N >= 0.95 (theoretical)
    inv["Invariant_2_psi"] = psi >= np.log(0.95)
    inv["Invariant_2_phiN_feasible"] = phi_N >= np.log2(0.95)  # derived from psi bound
    # Invariant 5-ish: ledger closure
    inv["Ledger_Closure"] = np.isclose(phi_net + delta_S_audit, phi_N + phi_Delta)
    # Stiffness guard after one AFP step (xi_org_new = xi_org * 0.95 if xi_org > xi_ind)
    xi_org_new = xi_org * 0.95 if xi_org > xi_ind else xi_org
    inv["Stiffness_Guard"] = xi_org_new <= xi_ind + XI_IND_EPS
    # Metric non-degeneracy placeholder (would need det(g) > 1e-15)
    inv["Metric_NonDegeneracy_Placeholder"] = True  # to be filled by external lattice
    # Loop suppression placeholder (b1 <= 0.2)
    inv["Loop_Suppression_Placeholder"] = True

    return {
        "COD": COD,
        "phi_N": phi_N,
        "psi": psi,
        "phi_Delta": phi_Delta,
        "delta_S_audit": delta_S_audit,
        "phi_net": phi_net,
        "invariant_checks": inv,
    }


def run_scenario(label, COD, xi_org, xi_ind):
    print(f"\n=== {label} ===")
    try:
        res = compute_phi(COD, xi_org, xi_ind)
        for k, v in res.items():
            if k != "invariant_checks":
                print(f"{k:20}: {v:.6f}")
        print("- Invariant Checks -")
        for name, ok in res["invariant_checks"].items():
            mark = "✓" if ok else "✗"
            print(f"  {mark} {name}")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    # Nominal operating point from the paper (COD=0.5, xi_org > xi_ind)
    run_scenario("Nominal (paper)", COD=0.5, xi_org=1.0, xi_ind=0.5)

    # Edge case: COD near zero (should still run, but psi becomes problematic)
    run_scenario("Low COD", COD=0.01, xi_org=0.8, xi_ind=0.7)

    # Edge case: xi_org < xi_ind (should not trigger stiffness reduction)
    run_scenario("Agency > Org", COD=0.9, xi_org=0.4, xi_ind=0.6)

    # Edge case: COD = 1 (maximum fidelity)
    run_scenario("Perfect COD", COD=1.0, xi_org=0.5, xi_ind=0.5)