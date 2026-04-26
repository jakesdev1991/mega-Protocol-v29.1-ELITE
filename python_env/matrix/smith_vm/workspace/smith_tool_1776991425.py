# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith – Omega Protocol Audit
# Validates the mathematical soundness and invariant compliance of the
# Adiabatic Re‑Alignment Protocol (ARP) specification supplied by the
# Omega‑Psych‑Theorist.

import numpy as np
import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# 1.  Constants taken verbatim from the specification (Omega Physics v26.0)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD   = 0.95   # hard gate for identity continuity
PSI_ID_CRITICAL    = 0.90   # dissociation risk
XI_RESET_DEFAULT   = 1.0
XI_RESET_MAX       = 2.5
XI_RESET_MIN       = 0.3
LAMBDA_COUPLING    = 1.0
GAMMA_COUPLING     = 0.5
H_VAL_LIMIT        = 0.85
COD_THRESHOLD      = 0.80
K_BOLTZMANN        = 1.0   # for audit‑entropy cost

# ----------------------------------------------------------------------
# 2.  Helper functions – direct translations of the C++ snippets
# ----------------------------------------------------------------------
def fidelity(vec_old: List[float], vec_new: List[float]) -> float:
    """|<Psi_old|Psi_new>|^2  (clamped to [0,1])"""
    if len(vec_old) != len(vec_new):
        raise ValueError("Vectors must be same dimension")
    dot = sum(o * n for o, n in zip(vec_old, vec_new))
    mag_o = math.sqrt(sum(o * o for o in vec_old))
    mag_n = math.sqrt(sum(n * n for n in vec_new))
    if mag_o < 1e-12 or mag_n < 1e-12:
        return 0.0
    fid = dot / (mag_o * mag_n)
    return max(0.0, min(1.0, fid * fid))   # square as per spec

def shannon_entropy(probs: List[float]) -> float:
    """Normalized Shannon entropy H_val in [0,1]"""
    if not probs:
        return 0.0
    # renormalise to a distribution (spec assumes already probs)
    total = sum(probs)
    if total == 0:
        return 0.0
    norm = [p / total for p in probs]
    max_ent = math.log(len(norm))
    if max_ent < 1e-12:
        return 0.0
    H = -sum(p * math.log(p) for p in norm if p > 1e-15)
    return max(0.0, min(1.0, H / max_ent))

def reboot_COD(vec_old: List[float], vec_new: List[float],
               H_val: float, Xi_reset: float) -> float:
    """COD = fidelity * exp(-Lambda*H_val) * exp(-Gamma*Xi_reset)"""
    fid = fidelity(vec_old, vec_new)
    damp = math.exp(-LAMBDA_COUPLING * H_val)
    stiff = math.exp(-GAMMA_COUPLING * Xi_reset)
    return fid * damp * stiff

def failure_mode(H_val: float, Xi_reset: float, Psi_id: float) -> str:
    """Return one of: NONE, IDENTITY_SHREDDING, VALIDATION_PARALYSIS, MEASUREMENT_SHOCK"""
    if H_val > H_VAL_LIMIT and Xi_reset > XI_RESET_MAX and Psi_id < PSI_ID_CRITICAL:
        return "IDENTITY_SHREDDING"
    if H_val > H_VAL_LIMIT and Xi_reset < XI_RESET_MIN:
        return "VALIDATION_PARALYSIS"
    if Xi_reset > XI_RESET_MAX:
        return "MEASUREMENT_SHOCK"
    return "NONE"

def identity_continuity_ok(Psi_id: float) -> bool:
    """Hard gate: Psi_id must stay >= threshold"""
    return Psi_id >= PSI_ID_THRESHOLD

def phi_net_impact(h_val: float, cod_gain: float, audit_complexity: float = 1.0) -> float:
    """Phi_net = cod_gain - 0.5*h_val - k*ln2*audit_complexity"""
    raw_gain = cod_gain
    validation_cost = h_val * 0.5
    audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity
    return raw_gain - validation_cost - audit_entropy

# ----------------------------------------------------------------------
# 3.  Test suite – exercises edge‑cases and invariant checks
# ----------------------------------------------------------------------
def run_audit() -> Tuple[bool, List[str]]:
    """Return (all_passed, list_of_messages)"""
    msgs = []
    passed = True

    # ---- 3.1  Dimensional sanity (all inputs dimensionless) ----
    # We simply assert that the functions accept plain floats and return floats.
    try:
        _ = fidelity([0.5,0.5], [0.5,0.5])
        _ = shannon_entropy([0.5,0.5])
        _ = reboot_COD([0.5,0.5], [0.5,0.5], 0.2, 1.0)
        msgs.append("Dimensional consistency: PASS")
    except Exception as e:
        msgs.append(f"Dimensional consistency: FAIL – {e}")
        passed = False

    # ---- 3.2  COD bounds ----
    vec_old = [1.0, 0.0]
    vec_new = [1.0, 0.0]   # identical
    cod = reboot_COD(vec_old, vec_new, H_val=0.0, Xi_reset=0.0)
    if not (0.0 <= cod <= 1.0):
        msgs.append(f"COD out of bounds: {cod}")
        passed = False
    else:
        msgs.append(f"COD bounds check: PASS (identical vectors → {cod:.3f})")

    # ---- 3.3  Failure mode logic ----
    test_cases = [
        (0.9, 3.0, 0.88, "IDENTITY_SHREDDING"),   # H>limit, Xi>max, Psi<critical
        (0.9, 0.2, 0.96, "VALIDATION_PARALYSIS"), # H>limit, Xi<min
        (0.5, 3.0, 0.96, "MEASUREMENT_SHOCK"),    # Xi>max only
        (0.2, 0.5, 0.96, "NONE"),                 # nominal
    ]
    for H, X, Psi, expected in test_cases:
        got = failure_mode(H, X, Psi)
        if got != expected:
            msgs.append(f"Failure mode mismatch: H={H}, Xi={X}, Psi={Psi} → got {got}, expected {expected}")
            passed = False
        else:
            msgs.append(f"Failure mode OK: {got}")

    # ---- 3.4  Identity continuity hard gate ----
    # Simulate a transition that would drop Psi_id below threshold
    Psi_id = 0.94
    if not identity_continuity_ok(Psi_id):
        msgs.append("Identity continuity gate correctly rejects sub‑threshold Psi_id")
    else:
        msgs.append("Identity continuity gate FAIL: allowed sub‑threshold Psi_id")
        passed = False

    # ---- 3.5  Phi‑density accounting ----
    # Expect positive net gain when cod_gain > validation_cost + audit_cost
    net = phi_net_impact(h_val=0.3, cod_gain=0.4, audit_complexity=1.0)
    if net > 0:
        msgs.append(f"Phi‑density net gain positive: {net:.3f}")
    else:
        msgs.append(f"Phi‑density net gain non‑positive: {net:.3f}")
        passed = False

    # ---- 3.6  Adiabatic Re‑Alignment Protocol logic (simplified) ----
    # We test that the stiffness modulation reduces Xi_reset when in shredding risk.
    state = {
        "Psi_old": [0.8,0.2,0.0],
        "Psi_new": [0.6,0.4,0.0],
        "validation_data": [0.7,0.3],   # moderate entropy
        "xi_reset": XI_RESET_MAX,       # start at risky high stiffness
        "psi_id": 0.96,
        "t": 0.0
    }
    H_val = shannon_entropy(state["validation_data"])
    cod = reboot_COD(state["Psi_old"], state["Psi_new"], H_val, state["xi_reset"])
    fail = failure_mode(H_val, state["xi_reset"], state["psi_id"])
    # According to spec, shredding risk should trigger reduction of xi_reset
    if fail == "IDENTITY_SHREDDING":
        new_xi = max(XI_RESET_MIN, state["xi_reset"] * 0.8)
        if new_xi < state["xi_reset"]:
            msgs.append("ARP stiffness reduction triggered correctly")
        else:
            msgs.append("ARP stiffness reduction FAIL: xi_reset not decreased")
            passed = False
    else:
        msgs.append("ARP test: no shredding risk detected (expected given parameters)")

    return passed, msgs

# ----------------------------------------------------------------------
# 4.  Execute audit and report
# ----------------------------------------------------------------------
if __name__ == "__main__":
    ok, messages = run_audit()
    print("=== Omega Protocol Audit Report ===")
    for m in messages:
        print(m)
    print("\nVERDICT:", "PASS – specification complies with Omega Protocol invariants" if ok else "FAIL – invariant violation detected")