# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# OMEGA PROTOCOL VALIDATION SCRIPT – BUREAUCRATIC IMPEDANCE MANIFOLD
# =============================================================================
# This script numerically checks the mathematical soundness and invariant
# compliance of the C++ specification provided by the Omega-Psych-Theorist.
# It reproduces the key formulas in Python and asserts that the Omega
# Protocol invariants (Phi_N, Phi_Delta, J*) are respected.
# =============================================================================

import math
from typing import List, Tuple

# -----------------------------------------------------------------------------
# Helper utilities (dimensionless by construction)
# -----------------------------------------------------------------------------
def normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return [0.0] * len(vec)
    return [x / norm for x in vec]

def fidelity_squared(a: List[float], b: List[float]) -> float:
    """|<a|b>|^2  (vectors need not be normalized)"""
    dot = sum(ai * bi for ai, bi in zip(a, b))
    norm_a = math.sqrt(sum(ai * ai for ai in a))
    norm_b = math.sqrt(sum(bi * bi for bi in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return (dot / (norm_a * norm_b)) ** 2

def shannon_entropy(probs: List[float]) -> float:
    """Shannon entropy, returns value in [0,1] after normalising by log(N)."""
    if not probs:
        return 0.0
    # remove zeros to avoid log(0)
    filtered = [p for p in probs if p > 0]
    if not filtered:
        return 0.0
    raw = -sum(p * math.log(p) for p in filtered)
    max_ent = math.log(len(filtered))
    if max_ent == 0:
        return 0.0
    return raw / max_ent  # now in [0,1]

def psi_invariant(phi_K: float) -> float:
    """ψ = ln(φ_N)  – using φ_K as proxy for φ_N (as in the code)."""
    return math.log(max(phi_K, 1e-10))

# -----------------------------------------------------------------------------
# Core formulas from the specification
# -----------------------------------------------------------------------------
LAMBDA = 1.0          # entropic damping coupling
GAMMA  = 0.6          # stiffness penalty coupling
COD_THRESHOLD = 0.85
PSI_ID_MIN   = 0.95   # identity threshold (φ_N)
XI_RULE_MAX  = 3.0    # stiffness risk threshold
K_BOLTZMANN  = 1.0    # normalized Boltzmann constant

def bureaucratic_COD(
    psi_sub: List[float],
    psi_con: List[float],
    H_proc: float,
    Xi_rule: float,
    Xi_req: float
) -> float:
    """Compute COD exactly as per the Ω‑spec (including squared fidelity)."""
    fid = fidelity_squared(psi_sub, psi_con)
    damp = math.exp(-LAMBDA * H_proc)
    stiff_pen = math.exp(-GAMMA * abs(Xi_rule - Xi_req))
    return fid * damp * stiff_pen

def verify_invariants(psi: float, Xi_rule: float, phi_Sigma: float) -> Tuple[bool, List[str]]:
    """Hard‑gate invariant check. Returns (pass, messages)."""
    msgs = []
    psi_min = math.log(PSI_ID_MIN)
    if psi < psi_min:
        msgs.append(f"CRITICAL: Identity Dissociation — psi={psi:.4f} < ln(0.95)={psi_min:.4f}")
        return False, msgs
    if Xi_rule > XI_RULE_MAX:
        msgs.append(f"CRITICAL: Metric Degeneracy Risk — Xi_rule={Xi_rule:.2f} > {XI_RULE_MAX}")
        return False, msgs
    if phi_Sigma > 0.03:
        msgs.append(f"WARNING: Entropy Cap Breached — phi_Sigma={phi_Sigma:.4f} > 0.03")
    return True, msgs

def audit_entropy_cost(complexity: float = 1.0) -> float:
    """ΔS_audit = k_B ln 2 * C_audit (dimensionless)."""
    return K_BOLTZMANN * math.log(2.0) * complexity

def phi_density_ledger(
    h_proc: float,
    cod_gain: float,
    audit_complexity: float = 1.0
) -> float:
    """Net Φ‑density impact: raw gain − entropy cost − audit cost."""
    entropy_cost = h_proc * 0.5
    audit_cost   = audit_entropy_cost(audit_complexity)
    return cod_gain - entropy_cost - audit_cost

# -----------------------------------------------------------------------------
# Adiabatic Flow Operator (AFP) – simplified Python replica
# -----------------------------------------------------------------------------
class BureaucraticState:
    def __init__(
        self,
        psi_sub: List[float],
        psi_con: List[float],
        approval_chain: List[float],
        phi_K: float,
        phi_Sigma: float,
        Xi_rule: float,
        Xi_req: float,
        t: float = 0.0
    ):
        self.psi_sub = psi_sub[:]
        self.psi_con = psi_con[:]
        self.approval_chain = approval_chain[:]
        self.phi_K = phi_K
        self.phi_Sigma = phi_Sigma
        self.xi_rule = Xi_rule
        self.xi_req = Xi_req
        self.t = t
        self._lock = __import__('threading').Lock()  # dummy, not used in single‑threaded test

    def process_entropy(self) -> float:
        return shannon_entropy(self.approval_chain)

    def psi_value(self) -> float:
        return psi_invariant(self.phi_K)

class AdiabaticFlowOperator:
    def __init__(self):
        pass

    def _verify_identity(self, psi: float) -> bool:
        return psi >= math.log(PSI_ID_MIN)

    def apply(self, state: BureaucraticState) -> None:
        """One adiabatic flow step (mirrors the C++ Apply)."""
        # Phase 1: diagnostic
        H_proc = state.process_entropy()
        cod = bureaucratic_COD(state.psi_sub, state.psi_con, H_proc,
                               state.xi_rule, state.xi_req)

        # Simple failure detection (mirrors FailureModeDetector)
        failure = None
        if (H_proc > 0.90 and state.xi_rule > 3.0 and
                state.psi_value() < math.log(0.90)):
            failure = "METRIC_DEGENERACY"
        elif state.psi_value() < math.log(PSI_ID_MIN):
            failure = "IDENTITY_DRIFT"
        elif cod < COD_THRESHOLD and state.xi_rule > 2.5:
            failure = "DECISION_PARALYSIS"

        # Early exit if stable
        if failure is None and cod >= COD_THRESHOLD:
            return

        # Phase 2: stiffness modulation (adiabatic)
        if failure == "METRIC_DEGENERACY":
            state.xi_rule = max(0.5, state.xi_rule * 0.8)
        elif failure == "IDENTITY_DRIFT":
            # shift conscious vector toward subconscious (simplified)
            state.psi_con = [
                (1.0 - 0.05) * c + 0.05 * s
                for c, s in zip(state.psi_con, state.psi_sub)
            ]
        elif failure == "DECISION_PARALYSIS":
            state.xi_rule = min(2.0, state.xi_rule * 0.9)
            if state.approval_chain:
                state.approval_chain.pop()   # drop one approval layer
        else:  # NONE but low COD
            if cod < COD_THRESHOLD:
                state.xi_rule = min(2.5, state.xi_rule * 1.05)

        # Phase 3: state transformation (alignment)
        alpha = min(1.0, (1.0 - state.xi_rule) * 0.5 + 0.5)
        state.psi_con = [
            (1.0 - alpha) * c + alpha * s
            for c, s in zip(state.psi_con, state.psi_sub)
        ]

        # Phase 4: entropy accounting
        state.phi_Sigma = H_proc

        # Phase 5: invariant validation (hard gate)
        state.psi = state.psi_value()
        ok, msgs = verify_invariants(state.psi, state.xi_rule, state.phi_Sigma)
        if not ok:
            raise RuntimeError("Invariant violation: " + "; ".join(msgs))

# -----------------------------------------------------------------------------
# Validation Tests
# -----------------------------------------------------------------------------
def test_dimensionality():
    """All inputs and outputs are pure numbers (dimensionless)."""
    vec = [0.3, 0.7]
    assert isinstance(fidelity_squared(vec, vec), float)
    assert isinstance(shannon_entropy([0.2, 0.3, 0.5]), float)
    assert isinstance(psi_invariant(0.5), float)
    assert isinstance(bureaucratic_COD(vec, vec, 0.2, 1.0, 1.0), float)
    assert isinstance(verify_invariants(0.0, 1.0, 0.0)[0], bool)
    assert isinstance(audit_entropy_cost(), float)
    assert isinstance(phi_density_ledger(0.1, 0.2), float)

def test_cod_formula():
    """Check that COD matches the spec (including squared fidelity)."""
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    # orthogonal → fidelity = 0 → COD = 0 irrespective of damping/penalty
    assert bureaucratic_COD(a, b, 0.0, 0.0, 0.0) == 0.0
    # identical vectors → fidelity = 1
    identical = [0.6, 0.8]
    cod = bureaucratic_COD(identical, identical, 0.0, 0.0, 0.0)
    assert math.isclose(cod, 1.0, rel_tol=1e-9)
    # introduce entropy damping
    cod_damp = bureaucratic_COD(identical, identical, 0.5, 0.0, 0.0)
    expected = math.exp(-LAMBDA * 0.5)  # fidelity=1, stiff_pen=1
    assert math.isclose(cod_damp, expected, rel_tol=1e-9)
    # introduce stiffness penalty
    cod_stiff = bureaucratic_COD(identical, identical, 0.0, 2.0, 0.0)
    expected = math.exp(-GAMMA * abs(2.0 - 0.0))
    assert math.isclose(cod_stiff, expected, rel_tol=1e-9)

def test_invariant_gates():
    """VerifyInvariants must fail exactly when hard gates are violated."""
    # Identity breach
    ok, msgs = verify_invariants(math.log(0.9) - 0.01, 1.0, 0.0)
    assert not ok and any("Identity Dissociation" in m for m in msgs)
    # Metric degeneracy breach
    ok, msgs = verify_invariants(math.log(0.96), 3.1, 0.0)
    assert not ok and any("Metric Degeneracy Risk" in m for m in msgs)
    # Entropy cap warning only (should still pass)
    ok, msgs = verify_invariants(math.log(0.96), 1.0, 0.04)
    assert ok and any("Entropy Cap Breached" in m for m in msgs)
    # All good
    ok, msgs = verify_invariants(math.log(0.96), 1.0, 0.02)
    assert ok and len(msgs) == 0

def test_audit_cost_subtraction():
    """Audit cost is subtracted from Φ‑density."""
    base = phi_density_ledger(0.2, 0.5, audit_complexity=0.0)  # no audit
    with_audit = phi_density_ledger(0.2, 0.5, audit_complexity=1.0)
    expected_diff = audit_entropy_cost(1.0)
    assert math.isclose(base - with_audit, expected_diff, rel_tol=1e-9)

def test_afp_preserves_invariants():
    """Run a few AFP steps and ensure invariants hold (or exception raised as expected)."""
    # Start in a risky state: high stiffness, moderate entropy, identity OK
    state = BureaucraticState(
        psi_sub=[0.9, 0.1],
        psi_con=[0.2, 0.8],
        approval_chain=[0.7, 0.6, 0.5],   # moderate process entropy
        phi_K=0.9,
        phi_Sigma=0.0,
        xi_rule=3.2,   # above risk threshold
        xi_req=0.2,
        t=0.0
    )
    afp = AdiabaticFlowOperator()
    # First application should detect METRIC_DEGENERACY and stiffen down
    try:
        afp.apply(state)
    except RuntimeError as e:
        # If identity somehow broke, we accept the exception; otherwise we expect success
        if "Identity" in str(e):
            raise
    # After step, invariants must hold
    ok, msgs = verify_invariants(state.psi, state.xi_rule, state.phi_Sigma)
    assert ok, f"Invariant failed after AFP: {msgs}"
    # Second step should move toward stability
    afp.apply(state)
    ok, msgs = verify_invariants(state.psi, state.xi_rule, state.phi_Sigma)
    assert ok, f"Invariant failed after second AFP: {msgs}"
    # Ensure psi did not drop below identity threshold
    assert state.psi >= math.log(PSI_ID_MIN), "Identity continuity lost"

def test_benchmark_phi_net():
    """Replicate the benchmark's Φ‑density gain calculation."""
    # Baseline: high stiffness, high process load
    approval = [0.9, 0.8, 0.7, 0.6, 0.5]
    H_proc = shannon_entropy(approval)
    # Assume some arbitrary COD values for illustration
    baseline_cod = 0.4
    flowed_cod   = 0.7
    cod_gain = flowed_cod - baseline_cod
    phi_net = phi_density_ledger(H_proc, cod_gain, audit_complexity=1.0)
    # Manual check
    expected = cod_gain - (H_proc * 0.5) - audit_entropy_cost(1.0)
    assert math.isclose(phi_net, expected, rel_tol=1e-9)
    # Phi net should be positive for a successful flow in this example
    assert phi_net > 0.0, "Benchmark Φ‑density gain unexpectedly non‑positive"

def run_all():
    test_dimensionality()
    test_cod_formula()
    test_invariant_gates()
    test_audit_cost_subtraction()
    test_afp_preserves_invariants()
    test_benchmark_phi_net()
    print("✅ All Omega‑Protocol validation tests passed.")

if __name__ == "__main__":
    run_all()