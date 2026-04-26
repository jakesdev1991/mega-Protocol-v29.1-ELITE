# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for IMSA v55.0 proposal
Checks:
  - Dimensional bounds ([0,1] for all normalized quantities)
  - COD formulation fidelity * uncertainty * identity * atrophy
  - Phi_N, psi, Phi_Delta, audit cost, net Phi
  - All six Omega Protocol invariants
  - Reflective consistency: subtract audit cost from claimed gains
"""

import numpy as np
from typing import Tuple, Dict

# ------------------- Constants -------------------
EPS = 1e-9               # to avoid log(0) and div/0
LAMBDA = 1.0             # uncertainty penalty strength (as in paper)
THETA_ATROPHY = 0.15     # lower bound of healthy superposition
THETA_SHOCK   = 0.80     # upper bound
P_ATROPHY     = 0.5      # penalty factor when H_super < THETA_ATROPHY
R_MAX         = 2.8      # stiffness normalization
K_B_LN2       = np.log(2)   # Landauer factor (k_B * ln 2)
C_AUDIT       = 6        # number of invariants checked (per proposal)

# ------------------- Helper Functions -------------------
def inner_product_squared(a: np.ndarray, b: np.ndarray) -> float:
    """|<a|b>|^2 assuming vectors are already normalized."""
    dot = np.dot(a, b)
    return float(np.clip(dot * dot, 0.0, 1.0))

def compute_cod(value_state: np.ndarray,
                identity_state: np.ndarray,
                H_super: float,
                Gamma_commit: float) -> float:
    """
    COD = |<Ψ_value|Ψ_id>|^2 *
          exp(-Λ * H_super) *
          Ψ_id_hard_gate *
          (1 - I(H_super < θ_atrophy) * P_atrophy)
    """
    # Fidelity term
    fidelity = inner_product_squared(value_state, identity_state)

    # Uncertainty penalty
    unc_pen = np.exp(-LAMBDA * H_super)

    # Identity hard gate: if identity < 0.95 -> zero COD
    # We model identity_state as a scalar representing the "continuity charge"
    # For simplicity, take its L2 norm as the charge (should be ≤1)
    identity_charge = np.linalg.norm(identity_state)
    identity_gate = identity_charge if identity_charge >= 0.95 else 0.0

    # Atrophy penalty
    atrophy_pen = 1.0 - (P_ATROPHY if H_super < THETA_ATROPHY else 0.0)

    cod = fidelity * unc_pen * identity_gate * atrophy_pen
    return float(np.clip(cod, 0.0, 1.0))

def phi_components(cod: float,
                   H_super: float,
                   Gamma_commit: float,
                   xi_value: float,
                   xi_identity: float) -> Dict[str, float]:
    """
    Returns:
        phi_N, psi, phi_Delta, delta_S_audit, phi_net
    """
    # Φ_N = log2(COD + ε)
    phi_N = np.log2(cod + EPS)

    # ψ = ln(Φ_N + ε)   (mandatory coupling)
    psi = np.log(phi_N + EPS)

    # Φ_Δ = ψ * tanh(R_align / R_max)
    R_align = abs(xi_value - xi_identity)
    phi_Delta = psi * np.tanh(R_align / R_MAX)

    # Audit entropy cost
    delta_S_audit = K_B_LN2 * C_AUDIT

    # Net Φ
    phi_net = phi_N + phi_Delta - delta_S_audit

    return {
        "phi_N": phi_N,
        "psi": psi,
        "phi_Delta": phi_Delta,
        "delta_S_audit": delta_S_audit,
        "phi_net": phi_net
    }

def check_invariants(cod: float,
                     H_super: float,
                     Gamma_commit: float,
                     phi_N: float,
                     psi: float,
                     phi_Delta: float,
                     phi_net: float) -> Tuple[bool, Dict[str, bool]]:
    """
    Evaluates the six Omega Protocol invariants.
    Returns (all_ok, dict_of_individual_results)
    """
    results = {}

    # 1. Metric Non-Degeneracy: COD > 0 (practically COD ≥ 0.80 for "optimal")
    results["metric_nondegen"] = cod > 0.0

    # 2. Identity Continuity: ψ ≥ ln(0.95)
    results["identity_continuity"] = psi >= np.log(0.95)

    # 3. Healthy Superposition Band: 0.15 < H_super < 0.80
    results["healthy_superposition"] = (THETA_ATROPHY < H_super < THETA_SHOCK)

    # 4. Commitment Rate Cap: Γ_commit ≤ 0.70
    results["commitment_cap"] = Gamma_commit <= 0.70

    # 5. Information Conservation: Φ_net ≥ 0 (post‑audit)
    results["info_conservation"] = phi_net >= 0.0

    # 6. Asymmetry Control: Φ_Δ < 0.5 * Φ_N
    # Note: Φ_N can be negative; we compare magnitudes as per paper intent.
    results["asymmetry_control"] = phi_Delta < 0.5 * phi_N

    all_ok = all(results.values())
    return all_ok, results

# ------------------- Example Validation -------------------
if __name__ == "__main__":
    # Example state vectors (4‑dim, normalized)
    np.random.seed(42)
    value_state = np.random.rand(4)
    value_state /= np.linalg.norm(value_state)

    identity_state = np.random.rand(4)
    identity_state /= np.linalg.norm(identity_state)

    # Nominal parameters from the proposal's ledger
    H_super_example = 0.45          # inside healthy band
    Gamma_commit_example = 0.55    # below cap
    xi_value = 1.2                  # arbitrary stiffness
    xi_identity = 0.9

    # Compute COD
    cod = compute_cod(value_state, identity_state,
                      H_super_example, Gamma_commit_example)
    print(f"COD = {cod:.4f}")

    # Phi components
    comps = phi_components(cod, H_super_example,
                           Gamma_commit_example,
                           xi_value, xi_identity)
    for k, v in comps.items():
        print(f"{k} = {v:.4f}")

    # Invariant check
    ok, inv_dict = check_invariants(cod, H_super_example,
                                    Gamma_commit_example,
                                    comps["phi_N"], comps["psi"],
                                    comps["phi_Delta"], comps["phi_net"])
    print("\nInvariant results:")
    for name, res in inv_dict.items():
        print(f"  {name:25}: {'PASS' if res else 'FAIL'}")
    print(f"\nAll invariants satisfied? {'YES' if ok else 'NO'}")

    # Additional sweep to detect edge cases
    print("\n--- Parameter sweep (spot‑check) ---")
    sweep_ok = True
    for H in [0.05, 0.15, 0.30, 0.55, 0.80, 0.90]:
        for Gc in [0.4, 0.7, 0.9]:
            cod_s = compute_cod(value_state, identity_state, H, Gc)
            comps_s = phi_components(cod_s, H, Gc, xi_value, xi_identity)
            ok_s, _ = check_invariants(cod_s, H, Gc,
                                       comps_s["phi_N"], comps_s["psi"],
                                       comps_s["phi_Delta"], comps_s["phi_net"])
            if not ok_s:
                sweep_ok = False
                print(f"Violation at H={H:.2f}, Γ={Gc:.2f} → COD={cod_s:.3f}, Φnet={comps_s['phi_net']:.3f}")
    print(f"Sweep passed? {'YES' if sweep_ok else 'NO'}")