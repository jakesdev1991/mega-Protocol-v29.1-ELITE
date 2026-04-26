# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Jerk‑Stability Validator
# --------------------------------------------------------------
# This script assumes the user supplies:
#   - field scale v (float)
#   - coupling lambda (float, >0)
#   - measured Phi_N, Phi_Delta (in units of v)
#   - measured dotPhi_N, dotPhi_Delta (in units of v/s)
#   - source jerk J_source (in s^-3)
#   - threshold J_thresh (in s^-3)
#
# It validates dimensional consistency and computes the jerk.
# --------------------------------------------------------------

import numpy as np

def validate_jerk(v, lam,
                  Phi_N, Phi_D,
                  dPhi_N, dPhi_D,
                  J_source, J_thresh):
    """
    Returns:
        dict with keys:
            'dim_ok'   : bool – dimensional consistency check
            'J_corr'   : float – jerk computed with corrected formula
            'J_orig'   : float – jerk using the expression from the thought
            'stable'   : bool – J_corr < J_thresh
            'messages' : list of str – explanation
    """
    msgs = []
    # Stiffness inverse squared (s^-2)
    xi_inv2 = lam * v**2          # λ v^2
    # Stiffness (s^-1) – we need ξ = 1/√(ξ_inv2)
    xi = 1.0 / np.sqrt(xi_inv2)   # ξ = 1/(√λ v)

    # ---- Dimensional check on the *original* expression ----
    # Original term: Φ * (dotΦ)^3 / ξ^4
    # ξ^4 = (1/ξ_inv2)^2 = 1/(λ^2 v^4)
    # So term ∝ Φ * (dotΦ)^3 * λ^2 v^4
    # Write everything in units of v:
    #   Φ = φ̃ * v
    #   dotΦ = dφ̃ * v / s
    # Then term ∝ (φ̃ v) * (dφ̃ v /s)^3 * λ^2 v^4
    #          = φ̃ * dφ̃^3 * λ^2 * v^(1+3+4) * s^-3
    #          = φ̃ * dφ̃^3 * λ^2 * v^8 * s^-3
    # For the term to be pure s^-3 we need λ^2 v^8 to be dimensionless,
    # i.e. λ must carry v^-4. Since λ is dimensionless, the check fails.
    # We therefore flag it as inconsistent.
    dim_ok_original = False
    msgs.append("Original jerk expression is dimensionally inconsistent "
                "(requires λ to have dimensions v^-4).")

    # ---- Corrected expression ----
    # Use dimensionless ratios: Φ/ξ and (dotΦ)/ξ
    term_N = (Phi_N / xi) * (dPhi_N / xi)**3
    term_D = (Phi_D / xi) * (dPhi_D / xi)**3
    J_corr = 3.0 * term_D - term_N + J_source

    # ---- Original expression (for reference) ----
    # We compute it assuming v=1, λ=1 (i.e. ignoring units)
    J_orig = (3.0 * Phi_D * dPhi_D**3) / (xi_inv2**2) \
             - (Phi_N * dPhi_N**3) / (xi_inv2**2) + J_source

    # Stability test
    stable = J_corr < J_thresh
    msgs.append(f"Corrected jerk J = {J_corr:.3e} s^-3")
    msgs.append(f"Threshold J_thresh = {J_thresh:.3e} s^-3")
    msgs.append(f"Stable? {stable}")

    return {
        "dim_ok": dim_ok_original,
        "J_corr": J_corr,
        "J_orig": J_orig,
        "stable": stable,
        "messages": msgs
    }

# --------------------------------------------------------------
# Example usage with the numbers from the thought
# --------------------------------------------------------------
if __name__ == "__main__":
    # Adopt a convenient unit system: set v = 1 (field scale) and λ = 1
    v_val = 1.0
    lam_val = 1.0

    # Measured values (as given, already expressed in units of v and v/s)
    Phi_N_val = 0.78 * v_val
    Phi_D_val = 0.35 * v_val
    dPhi_N_val = 2.1e3 * v_val   # v/s
    dPhi_D_val = 8.7e3 * v_val   # v/s

    J_source_val = 1.5e12        # s^-3
    J_thresh_val = 5.0e12        # s^-3

    result = validate_jerk(v_val, lam_val,
                           Phi_N_val, Phi_D_val,
                           dPhi_N_val, dPhi_D_val,
                           J_source_val, J_thresh_val)

    for m in result["messages"]:
        print(m)
    print("\nSummary:")
    print(f"  Dimensional consistency (original): {result['dim_ok']}")
    print(f"  Jerk (corrected)   : {result['J_corr']:.3e} s^-3")
    print(f"  Jerk (original)    : {result['J_orig']:.3e} s^-3")
    print(f"  Stable (J<thresh)  : {result['stable']}")