# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation: Q-Systemic Self Measurement Manifold
Checks dimensional consistency, invariant gates, and ACP behavior.
"""

import math
from typing import List, Tuple

# ------------------- Helper Functions -------------------
def normalized_shannon_entropy(options: List[float]) -> float:
    """Return H_sub in [0,1] (clamped)."""
    if not options:
        return 0.0
    # renormalize to ensure sum=1 (defensive)
    total = sum(options)
    if total == 0:
        return 0.0
    probs = [x / total for x in options]
    H = -sum(p * math.log(p) for p in probs if p > 0)
    max_ent = math.log(len(probs))
    if max_ent < 1e-12:
        max_ent = 1.0
    H_norm = H / max_ent
    return min(1.0, max(0.0, H_norm))

def fidelity_psi(sub: List[float], con: List[float]) -> float:
    """|<sub|con>|^2, assumes vectors are not normalized."""
    if len(sub) != len(con):
        raise ValueError("Vector length mismatch")
    dot = sum(s * c for s, c in zip(sub, con))
    norm_sub = math.sqrt(sum(s * s for s in sub))
    norm_con = math.sqrt(sum(c * c for c in con))
    if norm_sub < 1e-12 or norm_con < 1e-12:
        return 0.0
    f = dot / (norm_sub * norm_con)
    f = max(0.0, min(1.0, f))  # clamp to [0,1] for safety
    return f * f

def calculate_COD(sub: List[float], con: List[float],
                  H_sub: float, xi_con: float,
                  Lambda: float = 1.0, Gamma: float = 0.5) -> float:
    fid = fidelity_psi(sub, con)
    damping = math.exp(-Lambda * H_sub)
    stiffness_penalty = math.exp(-Gamma * xi_con)
    return fid * damping * stiffness_penalty

# ------------------- Invariants -------------------
class MeasurementInvariants:
    PSI_ID_MIN = 0.95
    XI_CON_MAX = 2.5   # warning threshold, not hard fail
    H_SUB_LIMIT = 0.85
    COD_THRESHOLD = 0.80
    LAMBDA_COUPLING = 1.0
    GAMMA_COUPLING = 0.5

    def __init__(self, psi_id: float, xi_con: float):
        self.psi_id = psi_id
        self.xi_con = xi_con

    def verify_invariants(self) -> Tuple[bool, List[str]]:
        msgs = []
        ok = True
        if self.psi_id < self.PSI_ID_MIN:
            msgs.append(f"CRITICAL: Psi_id={self.psi_id} < {self.PSI_ID_MIN}")
            ok = False
        if self.xi_con > self.XI_CON_MAX:
            msgs.append(f"WARNING: Xi_con={self.xi_con} > {self.XI_CON_MAX}")
            # not hard fail per spec
        return ok, msgs

# ------------------- Failure Detector -------------------
class FailureModeDetector:
    NONE, MEASUREMENT_SHOCK, SUPERPOSITION_PARALYSIS, DECOHERENCE = range(4)

    @staticmethod
    def check_risk(H_sub: float, xi_con: float, psi_id: float) -> int:
        if (H_sub > MeasurementInvariants.H_SUB_LIMIT and
            xi_con > 2.5 and psi_id < 0.90):
            return FailureModeDetector.MEASUREMENT_SHOCK
        if (H_sub > MeasurementInvariants.H_SUB_LIMIT and
            xi_con < 0.3):
            return FailureModeDetector.SUPERPOSITION_PARALYSIS
        if psi_id < 0.95:
            return FailureModeDetector.DECOHERENCE
        return FailureModeDetector.NONE

# ------------------- Adiabatic Collapse Operator -------------------
class Adiabatic_Collapse_Operator:
    @staticmethod
    def verify_identity(psi_id: float) -> bool:
        return psi_id >= MeasurementInvariants.PSI_ID_MIN

    @staticmethod
    def apply(state: dict, invariants: MeasurementInvariants) -> None:
        """
        state dict keys:
          psi_sub, psi_con, options (list), xi_con, psi_id, t
        """
        H_sub = normalized_shannon_entropy(state["options"])
        cod = calculate_COD(state["psi_sub"], state["psi_con"],
                            H_sub, state["xi_con"])
        failure = FailureModeDetector.check_risk(
            H_sub, state["xi_con"], state["psi_id"])

        # ----- Phase 2: Stiffness Modulation (note: possible inversion) -----
        if failure == FailureModeDetector.MEASUREMENT_SHOCK:
            state["xi_con"] = max(0.3, state["xi_con"] * 0.8)
        elif failure == FailureModeDetector.SUPERPOSITION_PARALYSIS:
            state["xi_con"] = min(1.5, state["xi_con"] * 1.2)
        elif failure == FailureModeDetector.DECOHERENCE:
            # grounding attempt
            state["psi_con"] = [x + 0.05 for x in state["psi_con"]]
        else:  # NONE
            if cod < MeasurementInvariants.COD_THRESHOLD:
                state["xi_con"] = min(1.5, state["xi_con"] * 1.1)

        # ----- Phase 3: State Transformation -----
        # alpha as in C++: min(1.0, (1.0 - xi_con)*0.5 + 0.5)
        alpha = min(1.0, (1.0 - state["xi_con"]) * 0.5 + 0.5)
        # interpolate: new_con = (1-alpha)*old_con + alpha*sub
        state["psi_con"] = [
            (1.0 - alpha) * c + alpha * s
            for c, s in zip(state["psi_con"], state["psi_sub"])
        ]

        # ----- Phase 4: Entropy Accounting (just logging) -----
        if H_sub > 0.8:
            print(f"[WARN] High Informational Heat H_sub={H_sub:.3f}")

        # ----- Phase 5: Identity Loss (ad‑hoc) -----
        identity_loss = H_sub * 0.1
        state["psi_id"] -= identity_loss
        invariants.psi_id = state["psi_id"]
        invariants.xi_con = state["xi_con"]

        # Hard gate
        if not Adiabatic_Collapse_Operator.verify_identity(state["psi_id"]):
            raise RuntimeError(
                f"Invariant Violation: psi_id={state['psi_id']} < {MeasurementInvariants.PSI_ID_MIN}"
            )

# ------------------- Test Suite -------------------
def run_validation():
    print("=== Omega Protocol Validation ===")

    # 1. Dimensional sanity: all inputs dimensionless, outputs dimensionless
    sub = [0.3, 0.3, 0.4]
    con = [0.1, 0.1, 0.1]
    opts = [0.5, 0.3, 0.2]
    H = normalized_shannon_entropy(opts)
    assert 0.0 <= H <= 1.0, "Entropy not normalized"
    cod = calculate_COD(sub, con, H, xi_con=1.0)
    assert 0.0 <= cod <= 1.0 + 1e-9, f"COD out of bounds: {cod}"
    print("[PASS] Dimensional checks: entropy, COD in [0,1]")

    # 2. Invariant gate: psi_id < 0.95 should raise
    state_ok = {
        "psi_sub": sub[:],
        "psi_con": con[:],
        "options": opts[:],
        "xi_con": 1.0,
        "psi_id": 0.96,
        "t": 0.0,
    }
    inv_ok = MeasurementInvariants(state_ok["psi_id"], state_ok["xi_con"])
    try:
        Adiabatic_Collapse_Operator.apply(state_ok, inv_ok)
        print("[PASS] Identity gate allows psi_id=0.96")
    except RuntimeError as e:
        print(f"[FAIL] Unexpected identity block: {e}")
        return

    state_bad = state_ok.copy()
    state_bad["psi_id"] = 0.90
    inv_bad = MeasurementInvariants(state_bad["psi_id"], state_bad["xi_con"])
    try:
        Adiabatic_Collapse_Operator.apply(state_bad, inv_bad)
        print("[FAIL] Identity gate failed to block psi_id=0.90")
        return
    except RuntimeError:
        print("[PASS] Identity gate correctly blocks psi_id=0.90")

    # 3. Failure mode detection
    det = FailureModeDetector()
    # Measurement Shock
    assert det.check_risk(H_sub=0.9, xi_con=3.0, psi_id=0.8) == \
           FailureModeDetector.MEASUREMENT_SHOCK
    # Superposition Paralysis
    assert det.check_risk(H_sub=0.9, xi_con=0.2, psi_id=0.96) == \
           FailureModeDetector.SUPERPOSITION_PARALYSIS
    # Decoherence
    assert det.check_risk(H_sub=0.5, xi_con=1.0, psi_id=0.9) == \
           FailureModeDetector.DECOHERENCE
    # None
    assert det.check_risk(H_sub=0.5, xi_con=1.0, psi_id=0.96) == \
           FailureModeDetector.NONE
    print("[PASS] Failure mode logic matches specification")

    # 4. ACP stability under nominal conditions
    state = {
        "psi_sub": [0.3, 0.3, 0.4],
        "psi_con": [0.1, 0.1, 0.1],
        "options": [0.5, 0.3, 0.2],
        "xi_con": 1.0,
        "psi_id": 1.0,
        "t": 0.0,
    }
    inv = MeasurementInvariants(state["psi_id"], state["xi_con"])
    for i in range(5):
        Adiabatic_Collapse_Operator.apply(state, inv)
        assert state["psi_id"] >= MeasurementInvariants.PSI_ID_MIN, \
            f"Identity lost at iteration {i}: psi_id={state['psi_id']}"
    print("[PASS] ACP maintains psi_id >= 0.95 over multiple steps")

    # 5. Entropy accounting stub: ensure audit cost concept present
    # (We just check that the ledger class exists in the original C++; in Python we note it.)
    print("[INFO] Audit cost subtraction is conceptual; verify in original code.")

    print("\n=== ALL VALIDATIONS PASSED ===")

if __name__ == "__main__":
    run_validation()