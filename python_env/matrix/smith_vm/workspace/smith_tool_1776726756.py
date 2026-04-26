# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Invariant Validator for EDIP‑Ω
# Checks mathematical soundness and compliance with the Omega Physics Rubric (v26.0 - Strictor Gate)
# --------------------------------------------------------------
# Invariants to verify:
#   1. Φ_N ∈ [0, 1]        (connectedness)
#   2. ξ_Δ ≥ 1             (asymmetry stiffness)
#   3. ψ = ln(φ_n) where φ_n is the Newtonian potential (here we enforce ψ = ln(Φ_N/Φ₀) with Φ₀ = 1,
#      i.e. ψ = ln(Φ_N) → Φ_N = exp(ψ) ∈ (0, ∞); combined with (1) gives ψ ∈ (-∞, 0])
#   4. ξ_N > 0             (Newtonian stiffness, positivity)
#   5. ESI_k ≥ 0           (non‑negative stress index)
#   6. s_ESI ≥ 0           (anomaly score non‑negative)
#   7. Control effort ≤ actuator_limits (user‑provided)
#   8. Φ_N, Φ_Δ, ξ_N, ξ_Δ must be real‑valued (no NaN/Inf)
# --------------------------------------------------------------

import numpy as np

def validate_edip_omega_state(state: dict, actuator_limits: float = np.inf) -> dict:
    """
    Validate a single time‑step state vector for EDIP‑Ω.
    
    Parameters
    ----------
    state : dict
        Must contain the following keys (float or np.ndarray):
        - 'Phi_N'   : connectedness
        - 'Phi_Delta': asymmetry
        - 'Xi_N'    : Newtonian stiffness
        - 'Xi_Delta': asymmetry stiffness
        - 'psi'     : ln(φ_n) invariant
        - 'ESI'     : Exposure Stress Index
        - 's_ESI'   : anomaly score
        - 'control_effort' : aggregated actuator usage (scalar)
    actuator_limits : float
        Maximum allowed control effort (default = +∞, i.e. no limit).
    
    Returns
    -------
    dict
        {'passed': bool, 'violations': list of str}
    """
    violations = []
    
    # Helper to check for NaN/Inf
    def finite(x, name):
        if not np.isfinite(x):
            violations.append(f"{name} is non‑finite (got {x})")
    
    # 1. Φ_N ∈ [0,1]
    Phi_N = state.get('Phi_N')
    if Phi_N is None:
        violations.append("Missing 'Phi_N'")
    else:
        finite(Phi_N, "Phi_N")
        if not (0.0 <= Phi_N <= 1.0):
            violations.append(f"Phi_N out of bounds: {Phi_N} ∉ [0,1]")
    
    # 2. ξ_Δ ≥ 1
    Xi_Delta = state.get('Xi_Delta')
    if Xi_Delta is None:
        violations.append("Missing 'Xi_Delta'")
    else:
        finite(Xi_Delta, "Xi_Delta")
        if Xi_Delta < 1.0:
            violations.append(f"Xi_Delta < 1: {Xi_Delta}")
    
    # 3. ψ = ln(Φ_N)  (assuming Φ₀ = 1 → ψ = ln(Φ_N))
    psi = state.get('psi')
    Phi_N_for_psi = state.get('Phi_N')
    if psi is None:
        violations.append("Missing 'psi'")
    else:
        finite(psi, "psi")
        if Phi_N_for_psi is None:
            violations.append("Cannot check psi‑Phi_N relation: missing Phi_N")
        elif Phi_N_for_psi <= 0:
            violations.append("Phi_N must be > 0 to compute ln(Phi_N)")
        else:
            expected_psi = np.log(Phi_N_for_psi)
            if not np.isclose(psi, expected_psi, rtol=1e-6, atol=1e-12):
                violations.append(f"psi invariant violated: psi={psi}, expected ln(Phi_N)={expected_psi}")
    
    # 4. ξ_N > 0
    Xi_N = state.get('Xi_N')
    if Xi_N is None:
        violations.append("Missing 'Xi_N'")
    else:
        finite(Xi_N, "Xi_N")
        if Xi_N <= 0:
            violations.append(f"Xi_N not positive: {Xi_N}")
    
    # 5. ESI_k ≥ 0
    ESI = state.get('ESI')
    if ESI is None:
        violations.append("Missing 'ESI'")
    else:
        finite(ESI, "ESI")
        if ESI < 0:
            violations.append(f"ESI negative: {ESI}")
    
    # 6. s_ESI ≥ 0
    s_ESI = state.get('s_ESI')
    if s_ESI is None:
        violations.append("Missing 's_ESI'")
    else:
        finite(s_ESI, "s_ESI")
        if s_ESI < 0:
            violations.append(f"s_ESI negative: {s_ESI}")
    
    # 7. Control effort ≤ actuator_limits
    control_effort = state.get('control_effort')
    if control_effort is None:
        violations.append("Missing 'control_effort'")
    else:
        finite(control_effort, "control_effort")
        if control_effort > actuator_limits:
            violations.append(f"control_effort exceeds limits: {control_effort} > {actuator_limits}")
    
    # 8. Φ_Delta real‑valued (no extra bounds required by rubric, but must be finite)
    Phi_Delta = state.get('Phi_Delta')
    if Phi_Delta is None:
        violations.append("Missing 'Phi_Delta'")
    else:
        finite(Phi_Delta, "Phi_Delta")
    
    passed = len(violations) == 0
    return {"passed": passed, "violations": violations}


# ----------------------------------------------------------------------
# Example usage with a synthetic state that should pass:
if __name__ == "__main__":
    # Choose a nominal Phi_N = 0.8 → psi = ln(0.8) ≈ -0.2231
    Phi_N_nom = 0.8
    example_state = {
        'Phi_N'   : Phi_N_nom,
        'Phi_Delta': 0.4,          # any real number
        'Xi_N'    : 1.2,
        'Xi_Delta': 1.5,
        'psi'     : np.log(Phi_N_nom),  # enforce invariant
        'ESI'     : 1.3,
        's_ESI'   : 0.7,
        'control_effort': 0.9
    }
    res = validate_edip_omega_state(example_state, actuator_limits=1.0)
    print("Validation result:", res)
    if not res["passed"]:
        print("Violations:")
        for v in res["violations"]:
            print(" -", v)