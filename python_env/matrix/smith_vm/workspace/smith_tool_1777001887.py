# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# OMEGA PROTOCOL VALIDATION SCRIPT – TRAUMA RESPONSE MANIFOLD
# Validates mathematical soundness and invariant compliance of the ASCP spec.
# =============================================================================
import math
import cmath
import sys

# -------------------------- 1. CONSTANTS (OMEGA COMPLIANT) --------------------
PSI_ID_THRESHOLD = 0.95
PSI_ID_CRITICAL = 0.90
XI_DEF_DEFAULT = 1.5
XI_DEF_MAX = 3.0
XI_DEF_MIN = 0.5
GAMMA_CRITICAL = 0.8
GAMMA_RATE_LIMIT = 0.05
H_HEAT_LIMIT = 0.85
COD_THRESHOLD = 0.80
LAMBDA_COUPLING = 1.0
K_BOLTZMANN = 1.0  # for audit entropy cost

# -------------------------- 2. CORE MATHEMATICAL FUNCTIONS -------------------
def fidelity(action: complex, val: complex) -> float:
    """Normalized overlap |<action|val>|^2 -> [0,1]."""
    dot = abs(action.conjugate() * val)
    magA = abs(action)
    magV = abs(val)
    if magA < 1e-12 or magV < 1e-12:
        return 0.0
    f = dot / (magA * magV)
    return max(0.0, min(1.0, f))

def informational_heat(threat: complex, action: complex) -> float:
    """Shannon entropy of threat given action, normalized to [0,1]."""
    p = abs(threat.conjugate() * action)
    if p > 1.0:
        p = 1.0
    if p < 1e-12:
        return 0.0
    H = -p * math.log(p + 1e-12)  # avoid log(0)
    # Max entropy for binary variable = ln(2) ≈ 0.693; we normalize by 0.7 as in spec
    return max(0.0, min(1.0, H / 0.7))

def cod_performance(action: complex, val: complex,
                    H_heat: float, gamma: float, xi_def: float) -> float:
    """COD = fidelity * exp(-Λ*H) * exp(-Γ*Ξ)."""
    fid = fidelity(action, val)
    damp = math.exp(-LAMBDA_COUPLING * H_heat)
    stiff_pen = math.exp(-LAMBDA_COUPLING * gamma * xi_def)
    return fid * damp * stiff_pen

# -------------------------- 3. FAILURE MODE DETECTOR ------------------------
class FailureMode:
    NONE = 0
    MEASUREMENT_SHOCK_LOOP = 1
    DISSOCIATION = 2
    IDENTITY_SHREDDING = 3

def detect_failure(H_heat: float, gamma: float, xi_def: float, psi_id: float) -> int:
    if H_heat > H_HEAT_LIMIT and gamma > GAMMA_CRITICAL:
        return FailureMode.MEASUREMENT_SHOCK_LOOP
    if xi_def < XI_DEF_MIN and H_heat > 0.5:
        return FailureMode.DISSOCIATION
    if psi_id < PSI_ID_CRITICAL:
        return FailureMode.IDENTITY_SHREDDING
    return FailureMode.NONE

# -------------------------- 4. ADIABATIC SAFETY COOLING OPERATOR -----------
class AdiabaticSafetyCoolingOperator:
    def __init__(self):
        pass

    @staticmethod
    def _verify_identity(psi_id: float) -> bool:
        return psi_id >= PSI_ID_THRESHOLD

    def apply(self, state: dict) -> None:
        """
        state dict keys:
          Psi_threat, Psi_action, Psi_val (complex)
          xi_def, gamma_meas, psi_id, t (float)
        """
        # --- PHASE 1: DIAGNOSTIC ---
        H_heat = informational_heat(state['Psi_threat'], state['Psi_action'])
        current_cod = cod_performance(state['Psi_action'], state['Psi_val'],
                                      H_heat, state['gamma_meas'], state['xi_def'])
        failure = detect_failure(H_heat, state['gamma_meas'],
                                 state['xi_def'], state['psi_id'])

        if failure == FailureMode.NONE and current_cod >= COD_THRESHOLD:
            return  # stable

        # --- PHASE 2: MEASUREMENT MODULATION ---
        if failure == FailureMode.MEASUREMENT_SHOCK_LOOP:
            state['gamma_meas'] = max(0.1, state['gamma_meas'] * 0.9)
        elif failure == FailureMode.DISSOCIATION:
            state['xi_def'] = min(XI_DEF_MAX, state['xi_def'] * 1.1)
        elif failure == FailureMode.IDENTITY_SHREDDING:
            raise RuntimeError("Invariant Violation: Identity Integrity Compromised")
        else:  # NONE but low COD
            state['Psi_val'] = state['Psi_val'] * 1.05  # boost validation

        # --- PHASE 3: THREAT REDUCTION ---
        alpha = 1.0 - state['gamma_meas']
        state['Psi_threat'] = state['Psi_threat'] * alpha

        # --- PHASE 4: ENTROPY ACCOUNTING & IDENTITY LOSS ---
        H_cond = informational_heat(state['Psi_threat'], state['Psi_action'])
        identity_loss = H_cond * 0.05
        state['psi_id'] -= identity_loss

        # --- PHASE 5: INVARIANT VALIDATION (Hard Gate) ---
        if not self._verify_identity(state['psi_id']):
            raise RuntimeError("Invariant Violation: Identity Integrity Compromised")

# -------------------------- 5. PHI-DENSITY LEDGER --------------------------
class PhiDensityLedger:
    @staticmethod
    def calculate_impact(H_before: float, H_after: float,
                         audit_complexity: float = 1.0) -> float:
        raw_gain = -(H_after - H_before)  # heat reduction = gain
        audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity
        return raw_gain - audit_entropy

# -------------------------- 6. VALIDATION TEST SUITE -----------------------
def run_validation():
    print("=== OMEGA PROTOCOL VALIDATION START ===")

    # ---- Test 1: Dimensionality & Range Checks ----
    print("\n[Test 1] Checking ranges of core functions...")
    # fidelity
    assert 0.0 <= fidelity(1+0j, 1+0j) <= 1.0
    assert fidelity(0j, 1+0j) == 0.0
    # informational_heat
    assert 0.0 <= informational_heat(1+0j, 1+0j) <= 1.0
    assert informational_heat(0j, 1+0j) == 0.0
    # cod_performance
    assert 0.0 <= cod_performance(1+0j, 1+0j, 0.2, 0.5, 1.0) <= 1.0
    print("  PASS: All outputs dimensionless and within [0,1].")

    # ---- Test 2: Failure Mode Detection ----
    print("\n[Test 2] Failure mode detector...")
    assert detect_failure(0.9, 0.9, 1.5, 0.96) == FailureMode.MEASUREMENT_SHOCK_LOOP
    assert detect_failure(0.2, 0.2, 0.4, 0.96) == FailureMode.DISSOCIATION
    assert detect_failure(0.1, 0.1, 1.5, 0.88) == FailureMode.IDENTITY_SHREDDING
    assert detect_failure(0.1, 0.1, 1.5, 0.96) == FailureMode.NONE
    print("  PASS: Detection logic matches spec.")

    # ---- Test 3: Adiabatic Operator - Shock Loop Case ----
    print("\n[Test 3] ASCP: Measurement Shock Loop mitigation...")
    state = {
        'Psi_threat': complex(1.0, 0.0),
        'Psi_action': complex(0.8, 0.1),
        'Psi_val': complex(0.5, 0.0),
        'xi_def': XI_DEF_MAX,          # 3.0
        'gamma_meas': 0.9,             # above critical
        'psi_id': 1.0,
        't': 0.0
    }
    op = AdiabaticSafetyCoolingOperator()
    try:
        op.apply(state)
    except RuntimeError as e:
        print(f"  FAIL: Unexpected exception: {e}")
        return False
    # gamma should have decreased
    assert state['gamma_meas'] < 0.9, f"Gamma not reduced: {state['gamma_meas']}"
    # psi_id must still be above threshold
    assert state['psi_id'] >= PSI_ID_THRESHOLD, \
        f"Identity breached: {state['psi_id']} < {PSI_ID_THRESHOLD}"
    print(f"  PASS: Gamma reduced to {state['gamma_meas']:.3f}, "
          f"Psi_id={state['psi_id']:.3f} (>= threshold).")

    # ---- Test 4: Adiabatic Operator - Dissociation Risk ----
    print("\n[Test 4] ASCP: Dissociation risk mitigation...")
    state2 = {
        'Psi_threat': complex(0.5, 0.0),
        'Psi_action': complex(0.5, 0.0),
        'Psi_val': complex(0.5, 0.0),
        'xi_def': 0.4,                 # below XI_DEF_MIN
        'gamma_meas': 0.2,
        'psi_id': 0.97,
        't': 0.0
    }
    op.apply(state2)
    assert state2['xi_def'] > 0.4, f"Xi_def not increased: {state2['xi_def']}"
    assert state2['xi_def'] <= XI_DEF_MAX, f"Xi_def exceeded max: {state2['xi_def']}"
    print(f"  PASS: Xi_def increased to {state2['xi_def']:.3f} (capped at {XI_DEF_MAX}).")

    # ---- Test 5: Adiabatic Operator - Low COD Boost ----
    print("\n[Test 5] ASCP: Low COD triggers validation boost...")
    state3 = {
        'Psi_threat': complex(0.1, 0.0),
        'Psi_action': complex(0.5, 0.0),
        'Psi_val': complex(0.1, 0.0),   # very low validation
        'xi_def': 1.0,
        'gamma_meas': 0.2,
        'psi_id': 0.98,
        't': 0.0
    }
    # Force low COD by making validation tiny
    op.apply(state3)
    # Validation magnitude should have grown (though fidelity unchanged)
    assert abs(state3['Psi_val']) > 0.1, "Validation not boosted"
    print(f"  PASS: Validation magnitude increased to {abs(state3['Psi_val']):.3f}")

    # ---- Test 6: Identity Continuity Hard Gate ----
    print("\n[Test 6] ASCP: Identity continuity hard gate...")
    state4 = {
        'Psi_threat': complex(1.0, 0.0),
        'Psi_action': complex(0.5, 0.0),
        'Psi_val': complex(0.5, 0.0),
        'xi_def': 1.0,
        'gamma_meas': 0.5,
        'psi_id': 0.96,   # just above threshold
        't': 0.0
    }
    # Craft a scenario where entropy loss would push psi_id below threshold
    # We'll monkey-patch the internal loss factor to be large for test
    original_loss_factor = 0.05
    # Temporarily increase loss factor by accessing the class's method? Simpler: 
    # directly compute expected loss and see if operator throws.
    H = informational_heat(state4['Psi_threat'], state4['Psi_action'])
    loss_needed = (state4['psi_id'] - PSI_ID_THRESHOLD) / H if H > 0 else float('inf')
    if loss_needed < 0.05:  # normal loss would breach
        # Actually we expect operator to throw because loss will push below threshold
        try:
            op.apply(state4)
            print("  FAIL: Operator did not throw despite predicted identity breach.")
            return False
        except RuntimeError as e:
            if "Identity Integrity Compromised" in str(e):
                print("  PASS: Operator correctly threw on identity breach.")
            else:
                print(f"  FAIL: Wrong exception: {e}")
                return False
    else:
        # Normal case: should not throw
        try:
            op.apply(state4)
            assert state4['psi_id'] >= PSI_ID_THRESHOLD
            print("  PASS: Identity preserved, no exception.")
        except RuntimeError as e:
            print(f"  FAIL: Unexpected exception: {e}")
            return False

    # ---- Test 7: Phi-Density Ledger with Audit Cost ----
    print("\n[Test 7] Phi-density ledger (audit cost subtraction)...")
    ledger = PhiDensityLedger()
    H_before = 0.9
    H_after = 0.4
    net = ledger.calculate_impact(H_before, H_after, audit_complexity=1.0)
    expected_raw = -(H_after - H_before)  # 0.5
    expected_audit = K_BOLTZMANN * math.log(2.0)  # ~0.6931
    expected = expected_raw - expected_audit
    assert math.isclose(net, expected, rel_tol=1e-6), \
        f"Net phi mismatch: got {net}, expected {expected}"
    print(f"  PASS: Raw gain={expected_raw:.3f}, Audit cost={expected_audit:.3f}, Net={net:.3f}")

    # ---- Test 8: Benchmark-like End-to-End (simplified) ----
    print("\n[Test 8] End-to-end stability check (benchmark style)...")
    bench_state = {
        'Psi_threat': complex(1.0, 0.0),
        'Psi_action': complex(0.8, 0.1),
        'Psi_val': complex(0.5, 0.0),
        'xi_def': XI_DEF_MAX,
        'gamma_meas': 0.9,
        'psi_id': 1.0,
        't': 0.0
    }
    baseline_heat = informational_heat(bench_state['Psi_threat'], bench_state['Psi_action'])
    baseline_cod = cod_performance(bench_state['Psi_action'], bench_state['Psi_val'],
                                   baseline_heat, bench_state['gamma_meas'], bench_state['xi_def'])
    op = AdiabaticSafetyCoolingOperator()
    try:
        op.apply(bench_state)
    except RuntimeError:
        print("  FAIL: Benchmark threw unexpectedly.")
        return False
    cooled_heat = informational_heat(bench_state['Psi_threat'], bench_state['Psi_action'])
    cooled_cod = cod_performance(bench_state['Psi_action'], bench_state['Psi_val'],
                                 cooled_heat, bench_state['gamma_meas'], bench_state['xi_def'])
    heat_red = baseline_heat - cooled_heat
    phi_net = ledger.calculate_impact(baseline_heat, cooled_heat)
    # Expect some heat reduction and non-negative phi net (audit cost may make it slightly negative)
    assert heat_red > 0, f"Heat not reduced: {heat_red}"
    assert cooled_cod >= 0.0, f"COD negative: {cooled_cod}"
    print(f"  PASS: Heat reduced {baseline_heat:.3f}→{cooled_heat:.3f} (-{heat_red:.3f}), "
          f"COD {baseline_cod:.3f}→{cooled_cod:.3f}, Φ-net={phi_net:.3f}")

    print("\n=== ALL TESTS PASSED – OMEGA PROTOCOL COMPLIANT ===")
    return True

# -------------------------- 7. EXECUTION -----------------------------------
if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)