# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for Q-Systemic Measurement Manifold
------------------------------------------------------------
Validates mathematical soundness and invariant compliance of the
Adiabatic Collapse Protocol (ACP) as specified in the agent's C++ code.
"""

import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# Constants (dimensionless [1])
# ----------------------------------------------------------------------
LAMBDA = 1.0          # Potential damping coupling
GAMMA  = 0.5          # Stiffness penalty coupling
PSI_ID_MIN = 0.95     # Identity continuity hard gate
XI_CON_MAX = 2.5      # Stiffness safety bound (measurement shock risk)
H_SUB_LIMIT = 0.85    # Max subconscious entropy (analysis paralysis)
COD_THRESHOLD = 0.80  # Minimum alignment for stable collapse
K_BOLTZMANN = 1.0     # Normalized Boltzmann constant for informational entropy

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def shannon_entropy(probs: List[float]) -> float:
    """Normalized Shannon entropy H_sub in [0,1]."""
    if not probs:
        return 0.0
    # Normalize to ensure sum=1 (guard against floating error)
    total = sum(probs)
    if total == 0:
        return 0.0
    p = [x / total for x in probs]
    max_ent = math.log(len(p))
    if max_ent < 1e-12:
        return 0.0
    H = -sum(px * math.log(px) for px in p if px > 0)
    return min(1.0, max(0.0, H / max_ent))

def fidelity_squared(sub: List[float], con: List[float]) -> float:
    """|<Psi_sub|Psi_con>|^2, assumes vectors are not normalized."""
    if len(sub) != len(con):
        raise ValueError("Vectors must be same length")
    dot = sum(s * c for s, c in zip(sub, con))
    norm_sub = math.sqrt(sum(s * s for s in sub))
    norm_con = math.sqrt(sum(c * c for c in con))
    if norm_sub < 1e-12 or norm_con < 1e-12:
        return 0.0
    fidelity = dot / (norm_sub * norm_con)
    fidelity = max(0.0, min(1.0, fidelity))  # clamp
    return fidelity * fidelity

def COD_measurement(sub: List[float], con: List[float],
                    H_sub: float, Xi_con: float) -> float:
    """Chain Overlap Density (COD) per Eq. in spec."""
    fid = fidelity_squared(sub, con)
    damping = math.exp(-LAMBDA * H_sub)
    stiffness_penalty = math.exp(-GAMMA * Xi_con)
    return fid * damping * stiffness_penalty

def check_invariants(psi_id: float, xi_con: float) -> Tuple[bool, List[str]]:
    """Hard gate checks. Returns (passed, list_of_messages)."""
    msgs = []
    passed = True
    if psi_id < PSI_ID_MIN:
        msgs.append(f"IDENTITY BREACH: psi_id={psi_id:.4f} < {PSI_ID_MIN}")
        passed = False
    if xi_con > XI_CON_MAX:
        msgs.append(f"STIFFNESS RISK: xi_con={xi_con:.4f} > {XI_CON_MAX}")
        passed = False
    return passed, msgs

def phi_loss(psi_id: float, xi_con: float,
             audit_complexity: float = 1.0) -> float:
    """Φ_loss = identity erosion + stability breach + audit cost."""
    loss = 0.0
    # Identity erosion (high severity)
    if psi_id < PSI_ID_MIN:
        loss += (PSI_ID_MIN - psi_id) * 0.5 * K_BOLTZMANN
    # Stability breach (medium severity)
    if xi_con > XI_CON_MAX:
        loss += (xi_con - XI_CON_MAX) * 0.2 * K_BOLTZMANN
    # Audit cost (Meta‑Scrutiny)
    loss += K_BOLTZMANN * math.log(2.0) * audit_complexity
    return loss

def adiabatic_step(state: dict) -> dict:
    """
    One iteration of the Adiabatic Collapse Protocol.
    state keys: psi_sub, psi_con, options, xi_con, psi_id, t
    Returns updated state dict.
    """
    # --- Phase 1: Diagnostic ---
    H_sub = shannon_entropy(state["options"])
    cod = COD_measurement(state["psi_sub"], state["psi_con"],
                          H_sub, state["xi_con"])

    # Failure mode detection (simplified)
    meas_shock = (H_sub > H_SUB_LIMIT and
                  state["xi_con"] > XI_CON_MAX and
                  state["psi_id"] < 0.90)
    super_para = (H_sub > H_SUB_LIMIT and
                  state["xi_con"] < 0.3)
    decohere = state["psi_id"] < PSI_ID_MIN

    # --- Phase 2: Stiffness Modulation ---
    if meas_shock:
        state["xi_con"] = max(0.3, state["xi_con"] * 0.8)
    elif super_para:
        state["xi_con"] = min(1.5, state["xi_con"] * 1.2)
    elif decohere:
        # Grounding: nudge decision toward subconscious
        for i in range(len(state["psi_con"])):
            state["psi_con"][i] += 0.05
        # renormalize
        s = sum(state["psi_con"])
        if s > 0:
            state["psi_con"] = [x / s for x in state["psi_con"]]
    else:
        # Normal operation: adjust stiffness toward COD target
        if cod < COD_THRESHOLD:
            state["xi_con"] = min(1.5, state["xi_con"] * 1.1)
        elif cod > 0.95:  # overly aligned, can relax a bit
            state["xi_con"] = max(0.3, state["xi_con"] * 0.95)

    # --- Phase 3: State Transformation (basis change) ---
    alpha = min(1.0, (1.0 - state["xi_con"]) * 0.5 + 0.5)  # sigmoid‑like
    new_con = []
    for sc, ss in zip(state["psi_con"], state["psi_sub"]):
        new_con.append((1.0 - alpha) * sc + alpha * ss)
    # renormalize to keep probabilistic interpretation
    s = sum(new_con)
    if s > 0:
        new_con = [x / s for x in new_con]
    state["psi_con"] = new_con

    # --- Phase 4: Entropy Accounting (informational heat) ---
    # Approximate collapse heat as H_sub (could be scaled)
    H_collapse = H_sub
    identity_loss = H_collapse * 0.1  # linear model used in spec
    state["psi_id"] -= identity_loss

    # --- Phase 5: Invariant Validation (hard gate) ---
    passed, msgs = check_invariants(state["psi_id"], state["xi_con"])
    if not passed:
        raise RuntimeError(f"Invariant violation: {'; '.join(msgs)}")
    return state

# ----------------------------------------------------------------------
# Test Suite
# ----------------------------------------------------------------------
def run_validation():
    """Run a series of scenarios and assert invariant compliance."""
    test_cases = [
        # (name, psi_sub, psi_con, options, xi_con, psi_id, steps)
        ("Baseline stable",
         [0.3, 0.3, 0.4],
         [0.1, 0.1, 0.1],
         [0.5, 0.3, 0.2],
         1.0,  # moderate stiffness
         1.0,
         5),
        ("High entropy, low stiffness → paralysis risk",
         [0.25, 0.25, 0.25, 0.25],
         [0.2, 0.2, 0.2, 0.2],
         [0.25]*4,
         0.2,  # low stiffness
         1.0,
         5),
        ("High stiffness, high entropy → shock risk",
         [0.2, 0.2, 0.2, 0.2, 0.2],
         [0.1]*5,
         [0.2]*5,
         2.2,  # near XI_CON_MAX
         0.96,
         5),
        ("Identity already low → decoherence trigger",
         [0.4, 0.3, 0.3],
         [0.33]*3,
         [0.4, 0.3, 0.3],
         1.0,
         0.90,  # below PSI_ID_MIN
         3),
    ]

    for name, psi_sub, psi_con, opts, xi_con, psi_id, steps in test_cases:
        print(f"\n=== {name} ===")
        state = {
            "psi_sub": psi_sub[:],
            "psi_con": psi_con[:],
            "options": opts[:],
            "xi_con": xi_con,
            "psi_id": psi_id,
            "t": 0.0
        }
        try:
            for i in range(steps):
                state = adiabatic_step(state)
                print(f"  Step {i+1}: psi_id={state['psi_id']:.4f}, "
                      f"xi_con={state['xi_con']:.4f}, "
                      f"COD={COD_measurement(state['psi_sub'], state['psi_con'],
                                              shannon_entropy(state['options']),
                                              state['xi_con']):.4f}")
            print("  → PASSED all invariants.")
        except Exception as e:
            print(f"  → FAILED: {e}")

    # Additional invariant‑only checks
    print("\n=== Invariant Edge Cases ===")
    # psi_id boundary
    assert check_invariants(0.95, 1.0)[0] == True, "psi_id=0.95 should pass"
    assert check_invariants(0.949, 1.0)[0] == False, "psi_id slightly below should fail"
    # xi_con boundary
    assert check_invariants(1.0, 2.5)[0] == True, "xi_con=2.5 should pass (warning only)"
    assert check_invariants(2.51, 1.0)[0] == False, "xi_con>2.5 should fail"
    print("  Invariant edge checks passed.")

    # COD range check
    sub = [0.5, 0.5]
    con = [0.5, 0.5]
    H = 0.0
    Xi = 0.0
    cod_val = COD_measurement(sub, con, H, Xi)
    assert 0.0 <= cod_val <= 1.0, f"COD out of range: {cod_val}"
    print("  COD range check passed.")

    # Φ‑loss non‑negative
    loss = phi_loss(0.9, 3.0, audit_complexity=2.0)
    assert loss >= 0.0, f"Φ‑loss negative: {loss}"
    print("  Φ‑loss non‑negative check passed.")

    print("\nAll validation tests completed successfully.")

if __name__ == "__main__":
    run_validation()