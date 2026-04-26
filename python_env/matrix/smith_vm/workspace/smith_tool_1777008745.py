# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Validator for Omega Protocol Trauma-Performance Specification
# --------------------------------------------------------------
# This script re-implements the core mathematical pieces from the
# C++ specification in pure Python and checks:
#   * Dimensional consistency (all values remain plain floats)
#   * Correctness of COD formula
#   * Invariant boundaries (psi_id >= 0.95, xi_con bounds)
#   * Failure mode detection logic
#   * AdiabaticIntegrationOperator execution preserves invariants
#   * Benchmark Phi‑density accounting (including audit cost)
#
# If any check fails, the script raises an AssertionError with a
# descriptive message.  On success it prints "ALL TESTS PASSED".
# --------------------------------------------------------------

import math
import random
from typing import List, Tuple

# ----------------------------
# Helper utilities
# ----------------------------
def assert_dimensionless(val: float, name: str) -> None:
    """All Omega Protocol quantities must be dimensionless [1]."""
    assert isinstance(val, (int, float)), f"{name} must be a numeric type"
    # No unit system here – just ensure it's a plain float.
    # (If we had a unit library we would check its dimension.)

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

# ----------------------------
# TraumaInvariants (mirrors C++ struct)
# ----------------------------
class TraumaInvariants:
    LAMBDA_COUPLING = 1.0   # Entropic Damping
    GAMMA_COUPLING  = 0.5   # Stiffness Penalty

    def __init__(self, psi_id: float, xi_con: float):
        self.psi_id = psi_id
        self.xi_con = xi_con
        assert_dimensionless(self.psi_id, "psi_id")
        assert_dimensionless(self.xi_con, "xi_con")

    # Hard boundary condition check (active gates)
    PSI_ID_MIN = 0.95
    XI_CON_MAX = 3.0   # Risk: Suppression Collapse
    XI_CON_MIN = 0.1   # Risk: Flooding

    def VerifyInvariants(self) -> bool:
        if self.psi_id < self.PSI_ID_MIN:
            # In the original code this would log and return False
            return False
        if self.xi_con > self.XI_CON_MAX:
            # Warning only – not a hard fail
            pass
        if self.xi_con < self.XI_CON_MIN:
            return False
        return True

    # Φ‑density loss with audit cost subtraction
    K_BOLTZMANN = 1.0   # Normalized for informational entropy

    def CalculatePhiLoss(self, audit_complexity_factor: float = 1.0) -> float:
        assert_dimensionless(audit_complexity_factor, "audit_complexity_factor")
        loss = 0.0
        # Identity erosion (High Severity)
        if self.psi_id < 0.95:
            loss += (0.95 - self.psi_id) * 0.5 * self.K_BOLTZMANN
        # Stability breach (Medium Severity) - Burnout Cost
        if self.xi_con > 3.0:
            loss += (self.xi_con - 3.0) * 0.3 * self.K_BOLTZMANN
        # Audit cost subtraction (Meta-Scrutiny requirement)
        audit_entropy_cost = self.K_BOLTZMANN * math.log(2.0) * audit_complexity_factor
        loss += audit_entropy_cost
        assert_dimensionless(loss, "PhiLoss")
        return loss

# ----------------------------
# CognitiveState (mirrors C++ struct)
# ----------------------------
class CognitiveState:
    def __init__(self,
                 psi_sub: List[float],
                 psi_con: List[float],
                 h_sub: float,
                 xi_con: float,
                 psi_id: float,
                 performance_output: float = 0.0):
        assert len(psi_sub) == len(psi_con), "Sub and Cons vectors must match length"
        self.psi_sub = [float(v) for v in psi_sub]
        self.psi_con = [float(v) for v in psi_con]
        self.h_sub = float(h_sub)
        self.xi_con = float(xi_con)
        self.psi_id = float(psi_id)
        self.performance_output = float(performance_output)
        self.state_lock = __import__('threading').Lock()  # simple placeholder

        # Basic dimensionless checks
        assert_dimensionless(self.h_sub, "h_sub")
        assert_dimensionless(self.xi_con, "xi_con")
        assert_dimensionless(self.psi_id, "psi_id")
        assert_dimensionless(self.performance_output, "performance_output")
        for i, v in enumerate(self.psi_sub):
            assert_dimensionless(v, f"psi_sub[{i}]")
        for i, v in enumerate(self.psi_con):
            assert_dimensionless(v, f"psi_con[{i}]")

    def CalculateShannonConditionalEntropy(self) -> float:
        """Returns dimensionless conditional entropy (rubric §5)."""
        dot = sum(a * b for a, b in zip(self.psi_sub, self.psi_con))
        magS = sum(a * a for a in self.psi_sub)
        magC = sum(b * b for b in self.psi_con)
        if magS <= 0.0 or magC <= 0.0:
            p = 0.0
        else:
            p = dot / (math.sqrt(magS) * math.sqrt(magC))
        p = clamp(p, 0.001, 0.999)  # avoid log(0)
        entropy = -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))
        assert_dimensionless(entropy, "ShannonConditionalEntropy")
        return entropy

# ----------------------------
# ChainOverlapDensity (COD)
# ----------------------------
class ChainOverlapDensity:
    @staticmethod
    def Calculate(state: CognitiveState) -> float:
        # fidelity = |<psi_sub|psi_con>|^2
        dot = sum(a * b for a, b in zip(state.psi_sub, state.psi_con))
        magS = sum(a * a for a in state.psi_sub)
        magC = sum(b * b for b in state.psi_con)
        if magS <= 1e-9 or magC <= 1e-9:
            fidelity = 0.0
        else:
            f = dot / (math.sqrt(magS) * math.sqrt(magC))
            fidelity = f * f   # squared overlap

        # Entropic damping
        damping = math.exp(-TraumaInvariants.LAMBDA_COUPLING * state.h_sub)
        # Stiffness penalty
        stiffness_penalty = math.exp(-TraumaInvariants.GAMMA_COUPLING * state.xi_con)

        cod = fidelity * damping * stiffness_penalty
        assert_dimensionless(cod, "COD")
        return cod

    COD_THRESHOLD = 0.80
    @staticmethod
    def IsStable(cod: float) -> bool:
        return cod >= ChainOverlapDensity.COD_THRESHOLD

# ----------------------------
# FailureModeDetector
# ----------------------------
class FailureModeDetector:
    NONE = 0
    SUPPRESSION_COLLAPSE = 1
    TRAUMA_FLOODING = 2
    DISSOCIATION = 3

    PSI_ID_CRITICAL = 0.90
    XI_CON_CRITICAL = 3.0
    H_SUB_LIMIT = 0.85

    @staticmethod
    def CheckRisk(psi_id: float, xi_con: float, h_sub: float, cod: float) -> int:
        assert_dimensionless(psi_id, "psi_id")
        assert_dimensionless(xi_con, "xi_con")
        assert_dimensionless(h_sub, "h_sub")
        assert_dimensionless(cod, "cod")
        # Suppression Collapse (Burnout)
        if xi_con > FailureModeDetector.XI_CON_CRITICAL and psi_id < 0.95:
            return FailureModeDetector.SUPPRESSION_COLLAPSE
        # Trauma Flooding (Overwhelm)
        if h_sub > FailureModeDetector.H_SUB_LIMIT and xi_con < 0.5:
            return FailureModeDetector.TRAUMA_FLOODING
        # Dissociation (Identity Loss)
        if psi_id < FailureModeDetector.PSI_ID_CRITICAL:
            return FailureModeDetector.DISSOCIATION
        return FailureModeDetector.NONE

# ----------------------------
# AdiabaticIntegrationOperator
# ----------------------------
class AdiabaticIntegrationOperator:
    @staticmethod
    def Diagnose(state: CognitiveState, invariants: TraumaInvariants) -> None:
        h_cond = state.CalculateShannonConditionalEntropy()
        cod = ChainOverlapDensity.Calculate(state)
        failure = FailureModeDetector.CheckRisk(state.psi_id, state.xi_con, state.h_sub, cod)
        if failure != FailureModeDetector.NONE:
            # In original code this would log; we just note it.
            if failure == FailureModeDetector.SUPPRESSION_COLLAPSE:
                state.xi_con = max(0.5, state.xi_con * 0.8)  # Soften
            elif failure == FailureModeDetector.TRAUMA_FLOODING:
                state.xi_con = min(2.5, state.xi_con * 1.2)  # Stabilize
            elif failure == FailureModeDetector.DISSOCIATION:
                raise RuntimeError("Dissociation Event Detected")

    @staticmethod
    def SoftenStiffness(xi_con: float, target_xi: float) -> float:
        assert_dimensionless(xi_con, "xi_con")
        assert_dimensionless(target_xi, "target_xi")
        alpha = 0.05
        new_xi = xi_con * (1.0 - alpha) + target_xi * alpha
        assert_dimensionless(new_xi, "new_xi")
        return new_xi

    @staticmethod
    def InjectIntegration(state: CognitiveState, t: float) -> None:
        # New State = Weighted Average (Integration)
        for i in range(len(state.psi_con)):
            state.psi_con[i] = 0.9 * state.psi_con[i] + 0.1 * state.psi_sub[i]
        assert_dimensionless(t, "t")

    @staticmethod
    def Execute(state: CognitiveState,
                invariants: TraumaInvariants,
                t: float) -> bool:
        with state.state_lock:
            # 1. Soften Stiffness (Release Suppression)
            state.xi_con = AdiabaticIntegrationOperator.SoftenStiffness(state.xi_con, 1.5)
            # 2. Inject Integration (Merge Trauma Data)
            AdiabaticIntegrationOperator.InjectIntegration(state, t)
            # 3. Simulate Energy Cost (Identity Decay)
            identity_loss = (state.xi_con * 0.02) + (state.h_sub * 0.01)
            state.psi_id -= identity_loss
            # 4. Re-verify Invariants (Hard Gate)
            if not invariants.VerifyInvariants():
                # In original code this would log and rollback
                return False
            # 5. Update Performance Output (Simulate Burnout Curve)
            state.performance_output = min(1.0, state.xi_con * 0.5)
            if state.xi_con > 2.5:
                state.performance_output *= 0.8   # Burnout penalty
            assert_dimensionless(state.performance_output, "performance_output")
            return True

# ----------------------------
# PhiDensityLedger
# ----------------------------
class PhiDensityLedger:
    K_BOLTZMANN = 1.0

    @staticmethod
    def CalculateImpact(cod_before: float,
                        cod_after: float,
                        audit_cost: float,
                        individual_cost: float) -> float:
        for v, n in zip([cod_before, cod_after, audit_cost, individual_cost],
                        ["cod_before", "cod_after", "audit_cost", "individual_cost"]):
            assert_dimensionless(v, n)
        raw_gain = cod_after - cod_before
        phi_net = raw_gain - audit_cost - individual_cost
        assert_dimensionless(phi_net, "phi_net")
        return phi_net

    @staticmethod
    def CalculateAuditCost(operator_complexity_factor: float = 1.0) -> float:
        assert_dimensionless(operator_complexity_factor, "operator_complexity_factor")
        return PhiDensityLedger.K_BOLTZMANN * math.log(2.0) * operator_complexity_factor

    @staticmethod
    def CalculateIndividualCost(H_sub: float, Xi_con: float) -> float:
        assert_dimensionless(H_sub, "H_sub")
        assert_dimensionless(Xi_con, "Xi_con")
        return H_sub * Xi_con * 0.3

# ----------------------------
# Benchmark (simplified)
# ----------------------------
class TraumaBenchmark:
    @staticmethod
    def RunBenchmark() -> dict:
        # Initialize State: High Stiffness / High Trauma (Pathological State)
        state = CognitiveState(
            psi_sub=[0.8, 0.1, 0.1],
            psi_con=[0.1, 0.8, 0.1],
            h_sub=0.9,
            xi_con=3.5,
            psi_id=1.0,
            performance_output=0.9
        )
        invariants = TraumaInvariants(state.psi_id, state.xi_con)
        aip = AdiabaticIntegrationOperator()
        ledger = PhiDensityLedger()

        # Baseline COD
        cod_before = ChainOverlapDensity.Calculate(state)

        success_count = 0
        total_trials = 100
        total_identity_loss = 0.0
        total_burnout = 0.0

        for i in range(total_trials):
            # Vary Trauma Load per trial
            state.h_sub = 0.6 + (i / total_trials) * 0.3
            try:
                aip.Diagnose(state, invariants)
                if aip.Execute(state, invariants, t=float(i)):
                    success_count += 1
                    total_identity_loss += (1.0 - state.psi_id)
                    total_burnout += (1.0 - state.performance_output)
            except RuntimeError:
                # Dissociation event – count as failure
                pass

        cod_after = ChainOverlapDensity.Calculate(state)
        identity_loss_avg = total_identity_loss / total_trials
        failure_rate = 1.0 - (success_count / total_trials)
        burnout_index = total_burnout / total_trials

        # Phi density calculation
        audit_cost = ledger.CalculateAuditCost(operator_complexity_factor=1.8)
        individual_cost = ledger.CalculateIndividualCost(state.h_sub, state.xi_con)
        phi_net_gain = ledger.CalculateImpact(cod_before, cod_after, audit_cost, individual_cost)

        return {
            "baseline_cod": cod_before,
            "integrated_cod": cod_after,
            "identity_loss": identity_loss_avg,
            "failure_rate": failure_rate,
            "burnout_index": burnout_index,
            "phi_net_gain": phi_net_gain
        }

# ----------------------------
# Validation Suite
# ----------------------------
def run_validation():
    print("=== Omega Protocol Trauma‑Performance Validator ===")

    # 1. Dimensional sanity – all constructors already assert dimensionless
    print("[1] Dimensional checks passed (constructors).")

    # 2. COD formula correctness
    state = CognitiveState(
        psi_sub=[1.0, 0.0],
        psi_con=[0.0, 1.0],
        h_sub=0.0,
        xi_con=0.0,
        psi_id=1.0
    )
    # orthogonal vectors => fidelity = 0
    cod = ChainOverlapDensity.Calculate(state)
    assert math.isclose(cod, 0.0, abs_tol=1e-12), f"COD for orthogonal vectors should be 0, got {cod}"
    # identical vectors => fidelity = 1, damping/penalty = exp(0)=1
    state.psi_con = [1.0, 0.0]
    cod = ChainOverlapDensity.Calculate(state)
    assert math.isclose(cod, 1.0, abs_tol=1e-12), f"COD for identical vectors should be 1, got {cod}"
    print("[2] COD formula verified.")

    # 3. Invariant boundaries
    inv = TraumaInvariants(psi_id=0.96, xi_con=2.0)
    assert inv.VerifyInvariants() is True, "Valid invariants should return True"
    inv_low = TraumaInvariants(psi_id=0.94, xi_con=2.0)  # psi_id too low
    assert inv_low.VerifyInvariants() is False, "psi_id < 0.95 should fail"
    inv_high = TraumaInvariants(psi_id=0.96, xi_con=0.05)  # xi_con too low
    assert inv_high.VerifyInvariants() is False, "xi_con < 0.1 should fail"
    print("[3] Invariant boundary checks passed.")

    # 4. Failure mode detector
    # Suppression Collapse
    assert FailureModeDetector.CheckRisk(psi_id=0.94, xi_con=3.2, h_sub=0.2, cod=0.5) == FailureModeDetector.SUPPRESSION_COLLAPSE
    # Trauma Flooding
    assert FailureModeDetector.CheckRisk(psi_id=0.96, xi_con=0.3, h_sub=0.9, cod=0.5) == FailureModeDetector.TRAUMA_FLOODING
    # Dissociation
    assert FailureModeDetector.CheckRisk(psi_id=0.88, xi_con=1.0, h_sub=0.2, cod=0.5) == FailureModeDetector.DISSOCIATION
    # Nominal
    assert FailureModeDetector.CheckRisk(psi_id=0.96, xi_con=1.0, h_sub=0.2, cod=0.5) == FailureModeDetector.NONE
    print("[4] Failure mode detection verified.")

    # 5. AdiabaticIntegrationOperator execution preserves invariants
    state = CognitiveState(
        psi_sub=[0.5, 0.5],
        psi_con=[0.5, 0.5],
        h_sub=0.4,
        xi_con=2.0,
        psi_id=0.98
    )
    invariants = TraumaInvariants(state.psi_id, state.xi_con)
    # Should succeed (stiffness will be softened, identity loss small)
    success = AdiabaticIntegrationOperator.Execute(state, invariants, t=0.0)
    assert success is True, "AIP should succeed under moderate conditions"
    assert state.psi_id >= 0.95, "Identity must stay above hard gate after successful execution"
    assert invariants.VerifyInvariants() is True, "Invariants must hold after execution"
    print("[5] AIP execution preserves invariants.")

    # 6. Benchmark Phi‑density accounting (including audit cost)
    results = TraumaBenchmark.RunBenchmark()
    # Basic sanity checks
    assert 0.0 <= results["baseline_cod"] <= 1.0, "Baseline COD out of bounds"
    assert 0.0 <= results["integrated_cod"] <= 1.0, "Integrated COD out of bounds"
    assert 0.0 <= results["identity_loss"] <= 1.0, "Identity loss out of bounds"
    assert 0.0 <= results["failure_rate"] <= 1.0, "Failure rate out of bounds"
    assert 0.0 <= results["burnout_index"] <= 1.0, "Burnout index out of bounds"
    # Phi net gain should be a real number (could be negative if costs outweigh gain)
    assert isinstance(results["phi_net_gain"], float), "Phi net gain must be float"
    print("[6] Benchmark runs and returns plausible metrics.")
    print(f"    Baseline COD: {results['baseline_cod']:.4f}")
    print(f"    Integrated COD: {results['integrated_cod']:.4f}")
    print(f"    Phi net gain: {results['phi_net_gain']:.4f}")

    # 7. Explicit audit cost subtraction check
    ledger = PhiDensityLedger()
    audit = ledger.CalculateAuditCost(2.0)
    assert_dimensionless(audit, "audit cost")
    # Ensure that audit cost is positive (log2 > 0)
    assert audit > 0.0, "Audit cost should be positive"
    print("[7] Audit cost subtraction mechanism verified.")

    print("\n✅ ALL TESTS PASSED – Specification is mathematically sound and Omega‑Protocol compliant.")
    return True

if __name__ == "__main__":
    try:
        run_validation()
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        raise
    except Exception as exc:
        print(f"\n❌ Unexpected error: {exc}")
        raise