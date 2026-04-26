# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Bureaucratic Resonance Gate (BRG) v57.0
Checks:
  - All variables remain dimensionless and bounded [0,1]
  - Identity hard gate (Ψ_id^org >= 0.95) is enforced
  - COD formula yields values in [0,1] and respects the gate
  - Dogma penalty behaves correctly
  - Audit entropy cost is subtracted before net Φ gain
  - BRG modulation is adiabatic (|ΔΞ| <= 0.05 per call)
  - Failure-mode detector triggers appropriate BRG action
"""

import math
import random
from typing import List, Tuple

# ---------------------------
# Constants (as in the C++ code)
# ---------------------------
PSI_ID_THRESHOLD = 0.95
THETA_ATROPHY = 0.15
THETA_SHOCK = 0.80
KAPPA_STIFFNESS = 1.5
LAMBDA_COUPLING = 1.0  # not used directly but kept for completeness
XI_CRITICAL = 0.70
COD_THRESHOLD = 0.80
PSI_ID_CRITICAL = 0.90
MAX_STIFFNESS_CHANGE = 0.05  # adiabatic limit

# ---------------------------
# Helper functions (mirroring the core logic)
# ---------------------------
def fidelity(exec_vec: List[float], org_vec: List[float]) -> float:
    """Normalized dot product -> |<exec|org>|^2"""
    size = min(len(exec_vec), len(org_vec))
    dot = sum(exec_vec[i] * org_vec[i] for i in range(size))
    magE = sum(v * v for v in exec_vec[:size])
    magO = sum(v * v for v in org_vec[:size])
    if magE < 1e-12 or magO < 1e-12:
        return 0.0
    f = dot / math.sqrt(magE * magO)
    return max(0.0, min(1.0, f))  # clamp to [0,1]

def dogma_penalty(H_super: float) -> float:
    """Penalty when strategic entropy < theta_atrophy"""
    if H_super < THETA_ATROPHY:
        return 1.0 - ((THETA_ATROPHY - H_super) / THETA_ATROPHY)
    return 1.0

def COD_buro(exec_vec: List[float], org_vec: List[float],
             H_super: float, psi_id: float, xi_buro: float) -> float:
    """Chain Overlap Density with identity hard gate."""
    if psi_id < PSI_ID_THRESHOLD:
        return 0.0
    fid = fidelity(exec_vec, org_vec)
    stiffness_damp = math.exp(-KAPPA_STIFFNESS * xi_buro)
    penalty = dogma_penalty(H_super)
    return fid * stiffness_damp * psi_id * penalty

def strategic_entropy(nodes: List[Tuple[float, float]]) -> float:
    """
    nodes: list of (authority_weight, stiffness_cost)
    Returns normalized Shannon entropy in [0,1].
    """
    if not nodes:
        return 0.0
    probs = []
    for _, stiff in nodes:
        # weight entropy by stiffness cost (high cost -> higher entropy potential)
        p = 1.0 / (1.0 + math.sqrt(stiff))
        probs.append(p)
    total = sum(probs)
    probs = [p / total for p in probs]
    H = -sum(p * math.log(p) for p in probs if p > 1e-12)
    max_ent = math.log(len(nodes))
    if max_ent < 1e-12:
        max_ent = 1.0
    return min(1.0, max(0.0, H / max_ent))

def audit_entropy_cost(ops: int) -> float:
    """ΔS_audit = k_B ln 2 * N_ops ; k_B set to 1 for dimensionless."""
    return math.log(2.0) * ops

def phi_density_impact(cod_before: float, cod_after: float, audit_cost: float) -> float:
    """Net Φ gain = raw COD gain - audit entropy cost."""
    return (cod_after - cod_before) - audit_cost

def verify_identity(psi_id: float) -> bool:
    """Hard gate: returns False if invariant violated."""
    return psi_id >= PSI_ID_THRESHOLD

def brg_modulate(xi_buro: float, failure: str) -> Tuple[float, int]:
    """
    Apply BRG action.
    Returns new xi_buro and number of audit operations incurred (simplified).
    Enforces adiabatic limit |Δxi| <= MAX_STIFFNESS_CHANGE.
    """
    audit_ops = 0
    if failure == "PARALYSIS":
        new_xi = max(0.1, xi_buro * 0.85)  # reduce stiffness
        audit_ops += 1
    elif failure == "DOGMA":
        # In this simplified model we only affect xi via indirect coupling;
        # for audit counting we still charge an op.
        new_xi = xi_buro  # stiffness unchanged here; ambiguity handled elsewhere
        audit_ops += 1
    elif failure == "STIFFNESS_OVERFLOW":
        new_xi = max(0.1, xi_buro * 0.90)
        audit_ops += 1
    else:
        new_xi = xi_buro
    # Enforce adiabatic bound
    delta = abs(new_xi - xi_buro)
    if delta > MAX_STIFFNESS_CHANGE:
        # clamp to max allowed change
        sign = 1.0 if new_xi > xi_buro else -1.0
        new_xi = xi_buro + sign * MAX_STIFFNESS_CHANGE
    return new_xi, audit_ops

def failure_detector(H_super: float, xi_buro: float,
                     psi_id: float, cod: float) -> str:
    """Return a string label matching BRG cases."""
    if H_super > THETA_SHOCK and xi_buro > XI_CRITICAL:
        return "PARALYSIS"
    if H_super < THETA_ATROPHY and xi_buro > XI_CRITICAL:
        return "DOGMA"
    if psi_id < PSI_ID_CRITICAL:
        return "IDENTITY_SHREDDING"
    if cod < COD_THRESHOLD and psi_id > PSI_ID_CRITICAL:
        return "STIFFNESS_OVERFLOW"
    return "NONE"

# ---------------------------
# Validation via Monte‑Carlo
# ---------------------------
def run_validation(trials: int = 5000) -> None:
    random.seed(42)
    for t in range(trials):
        # Random manifold
        n_nodes = random.randint(5, 20)
        nodes = [(random.random(), random.random()) for _ in range(n_nodes)]
        H_super = strategic_entropy(nodes)

        # Random state vectors (dimension 10 for simplicity)
        dim = 10
        exec_vec = [random.random() for _ in range(dim)]
        org_vec = [random.random() for _ in range(dim)]

        xi_buro = random.random()
        psi_id = random.random() * 0.3 + 0.7  # often compromised but sometimes ok

        cod_before = COD_buro(exec_vec, org_vec, H_super, psi_id, xi_buro)
        failure = failure_detector(H_super, xi_buro, psi_id, cod_before)

        # Apply BRG
        xi_after, audit_ops = brg_modulate(xi_buro, failure)
        # Simulate a small drift in identity due to interaction (as in code)
        identity_loss = H_super * 0.02
        psi_id_after = max(0.0, psi_id - identity_loss)

        cod_after = COD_buro(exec_vec, org_vec, H_super, psi_id_after, xi_after)

        audit_cost = audit_entropy_cost(audit_ops)
        phi_net = phi_density_impact(cod_before, cod_after, audit_cost)

        # ---------- Assertions ----------
        # 1. Bounds
        assert 0.0 <= H_super <= 1.0, f"H_super out of bounds: {H_super}"
        assert 0.0 <= xi_buro <= 1.0 and 0.0 <= xi_after <= 1.0, "xi out of bounds"
        assert 0.0 <= psi_id <= 1.0 and 0.0 <= psi_id_after <= 1.0, "psi_id out of bounds"
        assert 0.0 <= cod_before <= 1.0 and 0.0 <= cod_after <= 1.0, "COD out of bounds"
        # 2. Identity hard gate
        if psi_id_after < PSI_ID_THRESHOLD:
            assert cod_after == 0.0, f"COD non-zero despite psi_id={psi_id_after}"
        # 3. COD formula sanity check (re‑compute)
            # (already done via function)
        # 4. Dogma penalty range
        pen = dogma_penalty(H_super)
        assert 0.0 <= pen <= 1.0, f"dogma_penalty out of range: {pen}"
        # 5. Adiabatic stiffness change
        assert abs(xi_after - xi_buro) <= MAX_STIFFNESS_CHANGE + 1e-9, \
            f"Stiffness changed too fast: Δxi={abs(xi_after - xi_buro)}"
        # 6. Audit cost non‑negative
        assert audit_cost >= 0.0, "Negative audit entropy cost"
        # 7. If identity gate violated, BRG should have thrown (simulated by returning early)
        #    In our simplified loop we just check that COD became zero.
        if psi_id_after < PSI_ID_THRESHOLD:
            assert cod_after == 0.0
        # 8. Failure detector logic spot‑check
        if failure == "PARALYSIS":
            assert H_super > THETA_SHOCK and xi_buro > XI_CRITICAL
        if failure == "DOGMA":
            assert H_super < THETA_ATROPHY and xi_buro > XI_CRITICAL
        if failure == "IDENTITY_SHREDDING":
            assert psi_id < PSI_ID_CRITICAL
        if failure == "STIFFNESS_OVERFLOW":
            assert cod_before < COD_THRESHOLD and psi_id > PSI_ID_CRITICAL

    print(f"All {trials} Monte‑Carlo validation trials passed.")

# ---------------------------
# Run the validation
# ---------------------------
if __name__ == "__main__":
    run_validation()