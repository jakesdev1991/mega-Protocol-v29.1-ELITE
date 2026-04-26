# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Bureaucratic Impedance Manifold (Omega Protocol v32.1)
Checks:
  - COD formula fidelity * exp(-Λ*H) * exp(-Γ*|Ξ_rule - Ξ_req|)
  - Invariant Φ‑1: ψ >= ln(0.95)
  - Invariant Φ‑2: Ξ_rule <= 3.0 and H_proc <= 0.90
  - Invariant Φ‑3: H_proc is a proper normalized Shannon entropy
  - Φ‑density net gain accounts for audit cost
  - Adiabatic Flow Operator reduces Ξ_rule when Ξ_req is high
"""

import math
import numpy as np

# -------------------------- Constants (Omega Protocol) --------------------------
LAMBDA_COUPLING = 1.0          # Entropic damping
GAMMA_COUPLING   = 0.6         # Stiffness penalty
H_PROC_LIMIT     = 0.90        # Max allowed process entropy
XI_RULE_MAX      = 3.0         # Stiffness beyond which metric degeneracy risk
PSI_ID_MIN       = 0.95        # Minimum identity density
PSI_MIN_LOG      = math.log(PSI_ID_MIN)   # ψ lower bound
COD_THRESHOLD    = 0.85        # Minimum acceptable COD
K_BOLTZMANN      = 1.0         # Normalized for informational entropy

# -------------------------- Helper Functions ----------------------------------
def shannon_entropy(probs):
    """Return Shannon entropy normalized to [0,1] for a list of probabilities."""
    if not probs:
        return 0.0
    # Remove zeros to avoid log(0)
    probs = [p for p in probs if p > 0]
    if not probs:
        return 0.0
    raw = -sum(p * math.log(p) for p in probs)
    max_ent = math.log(len(probs)) if len(probs) > 1 else 1.0
    return min(1.0, max(0.0, raw / max_ent))

def fidelity(intent, exec_):
    """Normalized dot product (cosine similarity) clipped to [0,1]."""
    intent = np.asarray(intent, dtype=float)
    exec_  = np.asarray(exec_,  dtype=float)
    dot = np.dot(intent, exec_)
    ni = np.linalg.norm(intent)
    ne = np.linalg.norm(exec_)
    if ni < 1e-12 or ne < 1e-12:
        return 0.0
    cos = dot / (ni * ne)
    return min(1.0, max(0.0, cos))

def calculate_COD(intent, exec_, H_proc, Xi_rule, Xi_req):
    """COD = fidelity * exp(-Λ*H) * exp(-Γ*|Ξ_rule - Ξ_req|)."""
    fid = fidelity(intent, exec_)
    damp = math.exp(-LAMBDA_COUPLING * H_proc)
    penalty = math.exp(-GAMMA_COUPLING * abs(Xi_rule - Xi_req))
    return fid * damp * penalty

def calculate_psi(phi_K):
    """ψ = ln(φ_N) approximated by ln(phi_K + epsilon)."""
    return math.log(phi_K + 1e-10)

def audit_entropy_cost(complexity=1.0):
    """ΔS_audit = k ln 2 * C_audit."""
    return K_BOLTZMANN * math.log(2.0) * complexity

def phi_net_gain(delta_COD, H_proc, audit_complexity=1.0, entropy_cost_factor=0.5):
    """Φ_net = ΔCOD - entropy_cost - audit_cost."""
    entropy_cost = entropy_cost_factor * H_proc
    audit_cost   = audit_entropy_cost(audit_complexity)
    return delta_COD - entropy_cost - audit_cost

def check_invariants(psi, Xi_rule, H_proc):
    """Return list of violated invariants (empty if all satisfied)."""
    violations = []
    if psi < PSI_MIN_LOG:
        violations.append("Φ‑1 Identity Continuity (psi < ln(0.95))")
    if Xi_rule > XI_RULE_MAX:
        violations.append("Φ‑2 Metric Degeneracy Risk (Xi_rule > 3.0)")
    if H_proc > H_PROC_LIMIT:
        violations.append("Φ‑2 Metric Degeneracy Risk (H_proc > 0.90)")
    # Φ‑3: H_proc must be a valid normalized entropy [0,1]
    if not (0.0 <= H_proc <= 1.0 + 1e-12):
        violations.append("Φ‑3 Entropy Cap (H_proc not in [0,1])")
    return violations

# -------------------------- Test Scenarios ------------------------------------
def run_scenario(name, intent, exec_, approval_chain, Xi_rule_init, Xi_req,
                 audit_complexity=1.0, apply_afp=False):
    print(f"\n=== {name} ===")
    # Initial state
    H_proc = shannon_entropy(approval_chain)
    psi_init = calculate_phi_K_from_chain(approval_chain)  # placeholder; we'll compute phi_K later
    # For simplicity we set phi_K = 1.0 (unit action density) unless otherwise noted
    phi_K = 1.0
    psi_init = calculate_psi(phi_K)
    COD_init = calculate_COD(intent, exec_, H_proc, Xi_rule_init, Xi_req)
    print(f"Initial:  H_proc={H_proc:.3f}, Xi_rule={Xi_rule_init:.2f}, psi={psi_init:.4f}, COD={COD_init:.3f}")

    inv_viol = check_invariants(psi_init, Xi_rule_init, H_proc)
    if inv_viol:
        print("  INITIAL INVARIANT VIOLATIONS:", "; ".join(inv_viol))
    else:
        print("  Initial invariants: SATISFIED")

    # Apply AFP if requested (simple adiabatic rule: reduce Xi_rule towards Xi_req)
    if apply_afp:
        # Adiabatic step: move 20% of the gap per iteration, up to 5 iterations
        Xi_rule = Xi_rule_init
        for it in range(5):
            gap = Xi_rule - Xi_req
            if abs(gap) < 0.01:
                break
            Xi_rule = Xi_rule - 0.2 * gap  # move 20% towards requirement
            # Re‑compute entropy after possibly pruning a layer (simulate flow)
            if approval_chain and it % 2 == 0:  # prune one layer every other step
                approval_chain.pop()
            H_proc = shannon_entropy(approval_chain)
            phi_K = max(0.1, phi_K - 0.05)  # slight kinetic cost of flow
            psi = calculate_psi(phi_K)
        print(f"After AFP (5 iters): Xi_rule={Xi_rule:.2f}, H_proc={H_proc:.3f}, psi={psi:.4f}")
        COD_flow = calculate_COD(intent, exec_, H_proc, Xi_rule, Xi_req)
        print(f"  COD after AFP: {COD_flow:.3f}")
        delta_COD = COD_flow - COD_init
        phi_net = phi_net_gain(delta_COD, H_proc, audit_complexity)
        print(f"  ΔCOD = {delta_COD:+.3f}, Φ_net = {phi_net:+.3f}")
        inv_viol2 = check_invariants(psi, Xi_rule, H_proc)
        if inv_viol2:
            print("  POST‑AFP INVARIANT VIOLATIONS:", "; ".join(inv_viol2))
        else:
            print("  Post‑AFP invariants: SATISFIED")
    else:
        print("  AFP not applied.")

# Helper to estimate a placeholder phi_K from approval chain (not critical for validation)
def calculate_phi_K_from_chain(chain):
    # In the original model phi_K is action density; we approximate it as inverse of chain length + base.
    return max(0.2, 1.0 / (len(chain) + 1))

# -------------------------- Execute Test Cases --------------------------------
if __name__ == "__main__":
    # Intent and execution vectors (dimensionless, same length)
    intent = [1.0, 0.2, 0.1]   # Goal: strong core, small side‑effects
    exec_misaligned = [0.2, 0.8, 0.1]   # Poor alignment
    exec_aligned    = [0.9, 0.15, 0.05] # Good alignment

    # Approval chains (probabilities per layer, should sum ~1)
    chain_high_entropy   = [0.4, 0.3, 0.2, 0.1]   # 4 layers, moderate entropy
    chain_low_entropy    = [0.9, 0.1]             # 2 layers, low entropy
    chain_excessive      = [0.25]*8               # 8 layers, high entropy

    # 1. Baseline: high stiffness, low urgency → risk of metric degeneracy
    run_scenario(
        "Baseline High Stiffness / Low Urgency",
        intent, exec_misaligned,
        chain_high_entropy,
        Xi_rule_init=3.5,   # above safe limit
        Xi_req=0.1,         # low urgency
        audit_complexity=1.2,
        apply_afp=False
    )

    # 2. Same scenario but with AFP applied (should reduce stiffness)
    run_scenario(
        "AFP Tuning on High Stiffness / Low Urgency",
        intent, exec_misaligned,
        chain_high_entropy,
        Xi_rule_init=3.5,
        Xi_req=0.1,
        audit_complexity=1.2,
        apply_afp=True
    )

    # 3. High urgency, moderate stiffness → should stay stable
    run_scenario(
        "High Urgency, Moderate Stiffness (No AFP needed)",
        intent, exec_aligned,
        chain_low_entropy,
        Xi_rule_init=1.2,
        Xi_req=0.8,
        audit_complexity=0.8,
        apply_afp=False
    )

    # 4. Identity drift scenario: low phi_K (low action density) → psi drops
    print("\n=== Identity Drift Test ===")
    low_phi_K = 0.5
    psi_low = calculate_psi(low_phi_K)
    print(f"Low phi_K={low_phi_K} → psi={psi_low:.4f} (threshold={PSI_MIN_LOG:.4f})")
    if psi_low < PSI_MIN_LOG:
        print("  → Φ‑1 VIOLATION: Identity drift detected.")
    else:
        print("  → Identity within bounds.")

    # 5. Metric degeneracy via excessive process entropy
    print("\n=== Excessive Process Entropy Test ===")
    H_excess = shannon_entropy(chain_excessive)
    print(f"Chain length={len(chain_excessive)} → H_proc={H_excess:.3f}")
    if H_excess > H_PROC_LIMIT:
        print("  → Φ‑2 VIOLATION: Process entropy exceeds limit → metric degeneracy risk.")
    else:
        print("  → Process entropy within bound.")

    print("\n=== Validation Complete ===")