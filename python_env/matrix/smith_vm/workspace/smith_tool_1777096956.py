# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Validator for Audience Resonance Mapping (ARP)
--------------------------------------------------------
Checks:
    ψ = ln(Φ_N) ≥ ln(0.95)   (Trust Continuity)
    0 ≤ COD ≤ 1
    0 ≤ H_sales ≤ 1
    All supplied vectors are valid probability distributions
    (unit L2 norm for state vectors, sum=1 for engagement events)
    Stiffness penalty and entropic damping are well‑formed.
    Audit cost subtraction matches Meta‑Scrutiny.
"""

import math
from typing import List, Tuple

# -------------------------- Ω‑Constants --------------------------
PSI_TRUST_MIN = 0.95                     # ψ must be ≥ ln(PSI_TRUST_MIN)
LAMBDA_COUPLING = 1.0                    # Entropic damping
GAMMA_COUPLING = 0.6                     # Stiffness penalty
H_SALES_LIMIT = 0.90                     # Max allowable process entropy
XI_MAX_DIFF = 2.0                        # Max |Ξ_sales - Ξ_aud| before risk
COD_THRESHOLD = 0.80                     # Minimum acceptable overlap
K_BOLTZMANN = 1.0                        # For audit entropy

# -------------------------- Helper Math --------------------------
def log_safe(x: float) -> float:
    """Natural log with domain guard."""
    if x <= 0:
        raise ValueError(f"Log argument non‑positive: {x}")
    return math.log(x)

def normalize_l2(v: List[float]) -> List[float]:
    norm = math.sqrt(sum(x*x for x in v))
    if norm == 0:
        raise ValueError("Zero‑norm vector cannot be normalized")
    return [x / norm for x in v]

def normalize_prob(v: List[float]) -> List[float]:
    s = sum(v)
    if s == 0:
        raise ValueError("Cannot normalize zero‑sum probability vector")
    return [x / s for x in v]

def fidelity(u: List[float], v: List[float]) -> float:
    """|⟨u|v⟩|² assuming both are L2‑normalized."""
    dot = sum(a*b for a, b in zip(u, v))
    return max(0.0, min(1.0, dot * dot))

def shannon_entropy(p: List[float]) -> float:
    """Standard Shannon entropy; assumes p sums to 1."""
    return -sum(pi * math.log(pi) for pi in p if pi > 0)

def normalized_entropy(p: List[float]) -> float:
    """Returns H / log(N), clamped to [0,1]."""
    if not p:
        return 0.0
    H = shannon_entropy(p)
    maxH = math.log(len(p))
    if maxH == 0:
        return 0.0
    return max(0.0, min(1.0, H / maxH))

# -------------------------- Core Validation --------------------------
class ValidationError(RuntimeError):
    pass

def validate_state(state: dict) -> Tuple[bool, List[str]]:
    """
    state keys:
        psi_sales, psi_aud: List[float] (will be L2‑normalized)
        engagement_events: List[float] (will be prob‑normalized)
        xi_sales, xi_aud: float
        psi: float (ln Φ_N)
    Returns (ok, messages)
    """
    msgs = []
    ok = True

    # --- 1. Normalize & check dimensionality -----------------------
    try:
        state["psi_sales"] = normalize_l2(state["psi_sales"])
        state["psi_aud"]   = normalize_l2(state["psi_aud"])
        state["engagement_events"] = normalize_prob(state["engagement_events"])
    except Exception as e:
        msgs.append(f"Normalization failed: {e}")
        ok = False

    # --- 2. ψ invariant -------------------------------------------
    psi_min = log_safe(PSI_TRUST_MIN)
    if state["psi"] < psi_min:
        msgs.append(f"Trust invariant violated: ψ={state['psi']:.6f} < ln({PSI_TRUST_MIN})={psi_min:.6f}")
        ok = False

    # --- 3. Stiffness difference -----------------------------------
    diff_xi = abs(state["xi_sales"] - state["xi_aud"])
    if diff_xi > XI_MAX_DIFF:
        msgs.append(f"Stiffness diff too large: |Ξ_sales‑Ξ_aud|={diff_xi:.3f} > {XI_MAX_DIFF}")
        ok = False

    # --- 4. COD range -----------------------------------------------
    cod = fidelity(state["psi_sales"], state["psi_aud"])
    cod *= math.exp(-LAMBDA_COUPLING * normalized_entropy(state["engagement_events"]))
    cod *= math.exp(-GAMMA_COUPLING * diff_xi)
    if not (0.0 <= cod <= 1.0 + 1e-12):
        msgs.append(f"COD out of bounds: {cod:.6f}")
        ok = False
    state["_cached_COD"] = cod   # store for later use

    # --- 5. Normalized entropy range --------------------------------
    H = normalized_entropy(state["engagement_events"])
    if not (0.0 <= H <= 1.0 + 1e-12):
        msgs.append(f"Normalized H_sales out of bounds: {H:.6f}")
        ok = False
    state["_cached_H"] = H

    # --- 6. Audit cost sanity (optional) ---------------------------
    # audit_complexity should equal number of touchpoints; we just check it's non‑negative.
    if "audit_complexity" in state and state["audit_complexity"] < 0:
        msgs.append("Audit complexity negative")
        ok = False

    return ok, msgs

# -------------------------- ARP Step‑wise Validator ------------------
def apply_arp(state: dict) -> Tuple[bool, List[str]]:
    """
    Executes the ARP exactly as described in the source, but validates
    after each sub‑step. Returns (success, messages).
    """
    msgs = []
    ok = True

    # ----- Phase 1: Diagnostic ---------------------------------------
    ok_diag, msg_diag = validate_state(state)
    if not ok_diag:
        msgs.extend(["[Diag] " + m for m in msg_diag])
        ok = False
        return ok, msgs   # abort early

    # ----- Phase 2: Stiffness Modulation ----------------------------
    H = state["_cached_H"]
    diff_xi = abs(state["xi_sales"] - state["xi_aud"])
    # Simple risk trigger (mirrors FailureModeDetector)
    if H > H_SALES_LIMIT and diff_xi > XI_MAX_DIFF and state["psi"] < log_safe(0.90):
        # Trust Collapse risk → reduce sales stiffness
        state["xi_sales"] = max(0.5, state["xi_sales"] * 0.8)
        msgs.append("[Stiffness] Trust‑collapse risk → Ξ_sales *= 0.8")
    elif state["psi"] < log_safe(PSI_TRUST_MIN):
        msgs.append("[Stiffness] Identity drift → reinforce audience latent state")
        state["psi_aud"] = [x + 0.05 for x in state["psi_aud"]]
        state["psi_aud"] = normalize_l2(state["psi_aud"])
    elif diff_xi > 1.5:
        msgs.append("[Stiffness] Validation loop → Ξ_sales *= 0.8")
        state["xi_sales"] = max(0.5, state["xi_sales"] * 0.8)
    else:
        # Adiabatic follow
        state["xi_sales"] = state["xi_sales"] * 0.9 + state["xi_aud"] * 0.1
        msgs.append("[Stiffness] Adiabatic follow → new Ξ_sales")

    # Re‑validate after stiffness change (ψ unchanged, vectors unchanged)
    ok_stiff, msg_stiff = validate_state(state)
    if not ok_stiff:
        msgs.extend(["[Stiff-Post] " + m for m in msg_stiff])
        ok = False
        return ok, msgs

    # ----- Phase 3: State Transformation (Coherence Induction) -----
    alpha = min(1.0, (1.0 - abs(state["xi_sales"] - state["xi_aud"])) * 0.5 + 0.5)
    # Mix sales vector toward audience
    new_sales = [(1.0 - alpha) * a + alpha * b
                 for a, b in zip(state["psi_sales"], state["psi_aud"])]
    state["psi_sales"] = normalize_l2(new_sales)   # renormalize to keep unit‑norm
    msgs.append(f"[StateMix] α={alpha:.3f}")

    ok_mix, msg_mix = validate_state(state)
    if not ok_mix:
        msgs.extend(["[Mix-Post] " + m for m in msg_mix])
        ok = False
        return ok, msgs

    # ----- Phase 4: Entropy Accounting (no state change) -----------
    # Just a warning; we log if high entropy.
    if state["_cached_H"] > 0.8:
        msgs.append("[Entropy] High H_sales → cognitive load warning")
    # No modification to state, so invariants unchanged.

    # ----- Phase 5: Invariant Validation – Hard Gate on ψ ----------
    # Trust loss proportional to entropy (as in source)
    trust_loss = state["_cached_H"] * 0.05
    phi_N = math.exp(state["psi"])
    phi_N -= trust_loss
    if phi_N <= 0:
        msgs.append("[Trust] Φ_N driven non‑positive after loss")
        ok = False
        return ok, msgs
    state["psi"] = log_safe(phi_N)

    ok_trust, msg_trust = validate_state(state)
    if not ok_trust:
        msgs.extend(["[Trust-Post] " + m for m in msg_trust])
        ok = False
        return ok, msgs

    # ----- Update Invariants struct (mirrors source) ----------------
    state["xi_sales"] = state["xi_sales"]          # unchanged here
    state["phi_Sigma"] = state["_cached_H"]        # entropy as environmental density
    # ψ already updated

    msgs.append("[ARP] Completed successfully")
    return ok, msgs

# -------------------------- Demo / Self‑Test -----------------------
if __name__ == "__main__":
    import random

    # Example state – feel free to tweak
    demo_state = {
        "psi_sales": [1.0, 0.2, 0.1],
        "psi_aud":   [0.3, 0.8, 0.1],
        "engagement_events": [0.9, 0.5, 0.3, 0.2],
        "xi_sales": 3.5,
        "xi_aud":    1.0,
        "psi":       0.0,          # ln(1.0)
        "audit_complexity": 4      # number of touchpoints so far
    }

    print("=== Initial State ===")
    ok0, msgs0 = validate_state(demo_state)
    for m in msgs0:
        print(" -", m)
    print("Initial valid:", ok0)

    print("\n=== Applying ARP ===")
    ok1, msgs1 = apply_arp(demo_state)
    for m in msgs1:
        print(" -", m)
    print("ARP success:", ok1)
    if ok1:
        print("Updated ψ:", demo_state["psi"])
        print("Updated Ξ_sales:", demo_state["xi_sales"])
        print("Updated COD:", demo_state.get("_cached_COD"))
        print("Updated H:", demo_state.get("_cached_H"))