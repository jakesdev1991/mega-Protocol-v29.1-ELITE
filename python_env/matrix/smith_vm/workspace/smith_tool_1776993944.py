# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Agent Smith – Omega Protocol Audit
# Validation of the "Systemic Reboot via Intellectual Validation"
# specification (v26.0-Ω-POLARIZED) for mathematical soundness
# and invariant compliance.
# --------------------------------------------------------------

import math
from typing import List, Tuple

# ------------------- 1. Protocol Constants (as given) -------------------
PSI_ID_THRESHOLD   = 0.95   # hard gate for identity continuity
PSI_ID_CRITICAL    = 0.90   # dissociation risk
XI_RESET_DEFAULT   = 1.0
XI_RESET_MAX       = 2.5
XI_RESET_MIN       = 0.3
LAMBDA_COUPLING    = 1.0
GAMMA_COUPLING     = 0.5
H_VAL_LIMIT        = 0.85
COD_THRESHOLD      = 0.80
K_BOLTZMANN        = 1.0   # for audit‑cost term

# ------------------- 2. Helper Functions -------------------
def fidelity(psi_old: List[float], psi_new: List[float]) -> float:
    """|<Psi_old|Psi_new>|^2  (clamped to [0,1])"""
    if len(psi_old) != len(psi_new):
        raise ValueError("Vectors must be same dimension")
    dot = sum(o * n for o, n in zip(psi_old, psi_new))
    mag_old = sum(o * o for o in psi_old)
    mag_new = sum(n * n for n in psi_new)
    if mag_old == 0 or mag_new == 0:
        return 0.0
    fid = dot / math.sqrt(mag_old * mag_new)
    fid = max(0.0, min(1.0, fid))   # clamp
    return fid * fid                # squared magnitude

def shannon_entropy(probs: List[float]) -> float:
    """Normalized Shannon entropy H_val in [0,1]."""
    if not probs:
        return 0.0
    # ensure probabilities sum to 1 (renormalize)
    s = sum(probs)
    if s == 0:
        return 0.0
    norm = [p / s for p in probs]
    max_ent = math.log(len(norm))
    if max_ent < 1e-12:
        return 0.0
    H = -sum(p * math.log(p) for p in norm if p > 0)
    return max(0.0, min(1.0, H / max_ent))

def calculate_COD(psi_old: List[float],
                  psi_new: List[float],
                  H_val: float,
                  Xi_reset: float) -> float:
    """COD = fidelity * exp(-Λ*H_val) * exp(-Γ*Xi_reset)"""
    fid = fidelity(psi_old, psi_new)
    damping = math.exp(-LAMBDA_COUPLING * H_val)
    stiffness_penalty = math.exp(-GAMMA_COUPLING * Xi_reset)
    return fid * damping * stiffness_penalty

def identity_loss_from_entropy(H_val: float) -> float:
    """Simplified loss used in the spec: ΔΨ_id = 0.1 * H_val"""
    return 0.1 * H_val

def Phi_net_impact(H_val: float, COD_gain: float, audit_complexity: float = 1.0) -> float:
    """Φ_net = COD_gain - 0.5*H_val - k ln2 * audit_complexity"""
    raw_gain = COD_gain
    validation_cost = 0.5 * H_val
    audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity
    return raw_gain - validation_cost - audit_entropy

def failure_mode(H_val: float, Xi_reset: float, Psi_id: float) -> str:
    """Return one of: NONE, IDENTITY_SHREDDING, VALIDATION_PARALYSIS, MEASUREMENT_SHOCK"""
    if H_val > H_VAL_LIMIT and Xi_reset > XI_RESET_MAX and Psi_id < PSI_ID_CRITICAL:
        return "IDENTITY_SHREDDING"
    if H_val > H_VAL_LIMIT and Xi_reset < XI_RESET_MIN:
        return "VALIDATION_PARALYSIS"
    if Xi_reset > XI_RESET_MAX:
        return "MEASUREMENT_SHOCK"
    return "NONE"

# ------------------- 3. Invariant Checks -------------------
def check_invariants(psi_old: List[float],
                     psi_new: List[float],
                     validation_data: List[float],
                     Xi_reset: float,
                     Psi_id: float) -> Tuple[bool, List[str]]:
    """Return (all_ok, list_of_violations)."""
    violations = []
    # 1) Identity continuity hard gate
    if Psi_id < PSI_ID_THRESHOLD:
        violations.append(f"Psi_id={Psi_id} < threshold {PSI_ID_THRESHOLD}")
    # 2) Dimensional consistency – all inputs must be dimensionless [0,1]‑like
    #    We simply check ranges; out‑of‑range values are flagged.
    if not (0.0 <= Xi_reset <= 5.0):   # generous upper bound for testing
        violations.append(f"Xi_reset={Xi_reset} outside plausible range")
    H_val = shannon_entropy(validation_data)
    if not (0.0 <= H_val <= 1.0):
        violations.append(f"H_val={H_val} not normalized [0,1]")
    cod = calculate_COD(psi_old, psi_new, H_val, Xi_reset)
    if not (0.0 <= cod <= 1.0):
        violations.append(f"COD={cod} outside [0,1]")
    # 3) Failure‑mode detection – should not be IDENTITY_SHREDDING if invariants hold
    fm = failure_mode(H_val, Xi_reset, Psi_id)
    if fm == "IDENTITY_SHREDDING":
        violations.append("Invariant breach: Identity Shredding condition met")
    # 4) COD threshold for a successful reboot (soft requirement)
    if cod < COD_THRESHOLD:
        violations.append(f"COD={cod} < COD_THRESHOLD={COD_THRESHOLD}")
    return (len(violations) == 0, violations)

# ------------------- 4. Sample Test Suite -------------------
def run_tests():
    test_cases = [
        # (psi_old, psi_new, validation_data, Xi_reset, Psi_id, description)
        ([1.0, 0.0, 0.0], [0.9, 0.1, 0.0], [0.5, 0.5], 1.0, 1.0, "Nominal case"),
        ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.5, 0.5], 0.2, 0.96, "Low stiffness, high COD"),
        ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.9, 0.1], 3.0, 0.88, "High stiffness → risk"),
        ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.9, 0.1], 0.2, 0.92, "Low stiffness, high entropy → paralysis"),
    ]

    all_passed = True
    for idx, (old, new, val, xi, psi_id, desc) in enumerate(test_cases, 1):
        ok, viol = check_invariants(old, new, val, xi, psi_id)
        H = shannon_entropy(val)
        cod = calculate_COD(old, new, H, xi)
        phi = Phi_net_impact(H, cod - calculate_COD(old, old, H, xi))  # gain vs. no change
        print(f"Test {idx}: {desc}")
        print(f"  H_val={H:.3f}, Xi_reset={xi:.3f}, Psi_id={psi_id:.3f}")
        print(f"  COD={cod:.3f}, Φ_net≈{phi:.3f}")
        if ok:
            print("  ✅ All invariants satisfied.")
        else:
            print("  ❌ Violations:")
            for v in viol:
                print(f"    - {v}")
            all_passed = False
        print("-" * 50)
    return all_passed

if __name__ == "__main__":
    print("=== Omega Protocol Audit: Systemic Reboot Specification ===")
    if run_tests():
        print("\n🟢 OVERALL VERDICT: Specification is mathematically sound and invariant‑compliant.")
    else:
        print("\n🔴 OVERALL VERDICT: Invariant violations detected – specification requires revision.")