# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for Quantum‑Enhanced Children's Footwear (Q‑FAN) style proposals.

The script checks:
  • Φ‑1 (causal fidelity)   – max signal propagation speed ≤ c
  • Φ‑2 (entropy bound)     – total entropy increase ≤ allowed_frac * S_initial
  • Φ‑3 (topological integrity) – mesh must be homotopy‑equivalent to S^3
  • Rubric elements:
        - covariant mode split (Φ_K, Φ_Σ present as separate variables)
        - invariant canonical form (psi, xi_K, xi_S)
        - shredding event threshold and response
        - Shannon entropy reference for gait deviations
        - equation‑level derivation link to TOE Step 3 (crossed‑product)

All checks are deliberately strict: missing or non‑numeric fields cause FAIL.
"""

import json
import math
import sys
from typing import Any, Dict, Tuple

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def log(msg: str, level: str = "INFO"):
    print(f"[{level}] {msg}")

def safe_get(data: Dict, *keys, default=None):
    """Retrieve nested dict value; return default if any key missing."""
    d = data
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d

def is_positive_number(x):
    return isinstance(x, (int, float)) and x > 0

def is_number(x):
    return isinstance(x, (int, float))

# ----------------------------------------------------------------------
# Core validation functions
# ----------------------------------------------------------------------
def validate_phi1(spec: Dict) -> Tuple[bool, str]:
    """Φ‑1: No superluminal topological adjustment."""
    max_adjust_speed = safe_get(spec, "physics", "max_adjust_speed")  # m/s
    if not is_positive_number(max_adjust_speed):
        return False, "Missing or invalid max_adjust_speed (m/s)."
    c = 299_792_458  # speed of light, m/s
    if max_adjust_speed > c:
        return False, f"Adjustment speed {max_adjust_speed} m/s exceeds c ({c} m/s)."
    # Also check latency bound if provided
    max_latency = safe_get(spec, "physics", "max_latency_sec")
    if max_latency is not None:
        if not is_positive_number(max_latency):
            return False, "Invalid max_latency_sec."
        # latency * c gives max distance that could be influenced
        max_dist = max_latency * c
        # If a distance scale is given, ensure consistency
        char_length = safe_get(spec, "physics", "characteristic_length_m")
        if char_length is not None and not is_positive_number(char_length):
            return False, "Invalid characteristic_length_m."
        if char_length is not None and max_dist < char_length:
            return False, (
                f"Latency {max_latency}s allows influence over {max_dist:.2f} m, "
                f"but characteristic length is {char_length} m (possible superluminal)."
            )
    return True, "Φ‑1 satisfied."

def validate_phi2(spec: Dict) -> Tuple[bool, str]:
    """Φ‑2: Entropy increase ≤ allowed fraction."""
    S_init = safe_get(spec, "thermodynamics", "initial_entropy_J_per_K")
    if not is_positive_number(S_init):
        return False, "Missing or invalid initial_entropy_J_per_K."
    S_final = safe_get(spec, "thermodynamics", "final_entropy_J_per_K")
    if S_final is None:
        # Try to compute from risk reduction % (not acceptable per spec)
        return False, "Missing final_entropy_J_per_K; risk‑reduction % cannot substitute."
    if not is_number(S_final):
        return False, "Invalid final_entropy_J_per_K."
    allowed_frac = safe_get(spec, "thermodynamics", "allowed_entropy_increase_frac")
    if allowed_frac is None:
        return False, "Missing allowed_entropy_increase_frac (dimensionless)."
    if not (0 <= allowed_frac <= 1):
        return False, "allowed_entropy_increase_frac must be in [0,1]."
    delta_S = S_final - S_init
    max_allowed = allowed_frac * S_init
    if delta_S > max_allowed + 1e-12:  # tiny tolerance for FP
        return False, (
            f"Entropy increase {delta_S:.3e} J/K exceeds allowed {max_allowed:.3e} J/K "
            f"(frac={allowed_frac})."
        )
    return True, "Φ‑2 satisfied."

def validate_phi3(spec: Dict) -> Tuple[bool, str]:
    """Φ‑3: Topology must be homotopy‑equivalent to S^3."""
    # Expect a boolean from persistent homology test
    is_s3 = safe_get(spec, "topology", "is_homotopy_S3")
    if is_s3 is None:
        return False, "Missing topology.is_homotopy_S3 boolean."
    if not isinstance(is_s3, bool):
        return False, "topology.is_homotopy_S3 must be boolean."
    if not is_s3:
        return False, "Mesh is not homotopy‑equivalent to a 3‑sphere."
    return True, "Φ‑3 satisfied."

def validate_rubric(spec: Dict) -> Tuple[bool, str]:
    """Check all Omega Physics Rubric items."""
    # 1. Covariant mode split
    phi_K = safe_get(spec, "rubric", "covariant_modes", "Phi_K")
    phi_S = safe_get(spec, "rubric", "covariant_modes", "Phi_S")
    if phi_K is None or phi_S is None:
        return False, "Rubric: covariant_modes.Phi_K and/or Phi_S missing."
    # They should be callable expressions or at least placeholders; we just require presence.
    # 2. Invariant canonical form
    psi = safe_get(spec, "rubric", "invariants", "psi")
    xi_K = safe_get(spec, "rubric", "invariants", "xi_K")
    xi_S = safe_get(spec, "rubric", "invariants", "xi_S")
    if psi is None or xi_K is None or xi_S is None:
        return False, "Rubric: invariants.psi, xi_K, or xi_S missing."
    # 3. Shredding event
    shred_thresh = safe_get(spec, "rubric", "shredding_event", "threshold_phi_S")
    shred_action = safe_get(spec, "rubric", "shredding_event", "action")
    if shred_thresh is None:
        return False, "Rubric: shredding_event.threshold_phi_S missing."
    if not is_number(shred_thresh) or shred_thresh < 0:
        return False, "shredding_event.threshold_phi_S must be a non‑negative number."
    if shred_action is None or not isinstance(shred_action, str):
        return False, "Rubric: shredding_event.action missing or not a string."
    # 4. Entropy reference (Shannon entropy of gait deviations)
    shannon_ref = safe_get(spec, "rubric", "entropy_reference", "shannon_gait")
    if shannon_ref is None:
        return False, "Rubric: entropy_reference.shannon_gait missing."
    if not is_number(shannon_ref) or shannon_ref < 0:
        return False, "entropy_reference.shannon_gait must be a non‑negative number."
    # 5. Equation‑level TOE Step 3 derivation
    toe_step3_eq = safe_get(spec, "rubric", "toe_step3_derivation", "equation")
    toe_step3_desc = safe_get(spec, "rubric", "toe_step3_derivation", "description")
    if toe_step3_eq is None:
        return False, "Rubric: toe_step3_derivation.equation missing."
    if not isinstance(toe_step3_eq, str) or len(toe_step3_eq.strip()) == 0:
        return False, "toe_step3_derivation.equation must be a non‑empty string."
    if toe_step3_desc is None:
        return False, "Rubric: toe_step3_derivation.description missing."
    # If all passed:
    return True, "All rubric elements present and minimally valid."

def validate_phi_density(spec: Dict) -> Tuple[bool, str]:
    """Optional: check that claimed Φ‑gain matches sum of contributions."""
    claimed = safe_get(spec, "phi_density", "claimed_gain")
    if claimed is None:
        return True, "No Φ‑density claim supplied – skipping."  # not mandatory for compliance
    if not is_number(claimed):
        return False, "phi_density.claimed_gain must be numeric."
    contrib = safe_get(spec, "phi_density", "contributions")
    if contrib is None or not isinstance(contrib, dict):
        return False, "phi_density.contributions missing or not a dict."
    total = 0.0
    for label, val in contrib.items():
        if not is_number(val):
            return False, f"Contribution '{label}' is not numeric."
        total += val
    if not math.isclose(total, claimed, rel_tol=1e-3, abs_tol=1e-6):
        return False, (
            f"Sum of contributions ({total:.3f}) does not match claimed gain ({claimed:.3f})."
        )
    return True, "Φ‑density accounting consistent."

# ----------------------------------------------------------------------
# Main driver
# ----------------------------------------------------------------------
def validate_proposal(spec_json: str) -> Dict[str, Any]:
    try:
        spec = json.loads(spec_json)
    except json.JSONDecodeError as e:
        return {"pass": False, "reason": f"Invalid JSON: {e}"}

    checks = [
        ("Φ‑1", validate_phi1),
        ("Φ‑2", validate_phi2),
        ("Φ‑3", validate_phi3),
        ("Rubric", validate_rubric),
        ("Φ‑density", validate_phi_density),
    ]

    overall_pass = True
    details = {}
    for name, func in checks:
        ok, msg = func(spec)
        details[name] = {"pass": ok, "message": msg}
        if not ok:
            overall_pass = False

    return {
        "pass": overall_pass,
        "details": details,
    }

# ----------------------------------------------------------------------
# Example usage (can be removed when integrated into the Engine)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example spec that would PASS if all fields were filled correctly.
    example_spec = {
        "physics": {
            "max_adjust_speed": 10.0,          # m/s, well below c
            "max_latency_sec": 0.001,          # 1 ms
            "characteristic_length_m": 0.05    # 5 cm
        },
        "thermodynamics": {
            "initial_entropy_J_per_K": 1.0e-3,
            "final_entropy_J_per_K": 1.001e-3,
            "allowed_entropy_increase_frac": 0.021  # 2.1%
        },
        "topology": {
            "is_homotopy_S3": True
        },
        "rubric": {
            "covariant_modes": {
                "Phi_K": "biomechanics_field",
                "Phi_S": "terrain_stress_field"
            },
            "invariants": {
                "psi": "ln(phi_K)",
                "xi_K": "causal_bound",
                "xi_S": "entropy_cap"
            },
            "shredding_event": {
                "threshold_phi_S": 0.04,
                "action": "trigger_safe_mode_and_alert_guardian"
            },
            "entropy_reference": {
                "shannon_gait": 0.0023  # bits per step (example)
            },
            "toe_step3_derivation": {
                "equation": "M x N -> M' x N'  s.t. dim(M' ∩ N') ≥ 3",
                "description": "Crossed‑product dynamics linking biomechanics (M) and terrain (N)."
            }
        },
        "phi_density": {
            "claimed_gain": 4.9,
            "contributions": {
                "quantum_biomech_prediction": 1.2,
                "entanglement_swapped_coherence": 1.8,
                "TOE_compliance": 1.5,
                "invariant_adherence": 0.4
            }
        }
    }

    result = validate_proposal(json.dumps(example_spec, indent=2))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["pass"] else 1)