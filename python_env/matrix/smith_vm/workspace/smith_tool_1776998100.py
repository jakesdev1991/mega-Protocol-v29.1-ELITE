# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
from typing import List, Tuple

# ------------------ Constants (mirroring C++ constants) ------------------
PSI_ID_MIN = 0.95
XI_MEAS_MAX = 3.0   # Measurement Shock risk
XI_MEAS_MIN = 0.2   # Analysis Paralysis risk
LAMBDA_COUPLING = 1.0
GAMMA_COUPLING = 0.5
H_QUANTUM_LIMIT = 0.85
XI_MEAS_CRITICAL = 2.5
PSI_ID_CRITICAL = 0.90
COD_THRESHOLD = 0.80
K_BOLTZMANN = 1.0

# ------------------ Helper Functions ------------------
def fidelity(q: List[float], c: List[float]) -> float:
    """Squared overlap |<q|c>|^2 assuming real vectors."""
    dot = sum(qi * ci for qi, ci in zip(q, c))
    mag_q = sum(qi * qi for qi in q)
    mag_c = sum(ci * ci for ci in c)
    if mag_q == 0.0 or mag_c == 0.0:
        return 0.0
    f = dot / math.sqrt(mag_q * mag_c)
    return f * f  # squared

def cod(q: List[float], c: List[float], h_q: float, xi: float) -> float:
    """Chain Overlap Density."""
    fid = fidelity(q, c)
    damping = math.exp(-LAMBDA_COUPLING * h_q)
    stiffness_penalty = math.exp(-GAMMA_COUPLING * xi)
    return fid * damping * stiffness_penalty

def verify_invariants(psi_id: float, xi_meas: float) -> bool:
    """Active boundary condition check."""
    if psi_id < PSI_ID_MIN:
        return False
    if xi_meas > XI_MEAS_MAX:
        return False
    if xi_meas < XI_MEAS_MIN:
        return False
    return True

def phi_loss(psi_id: float, xi_meas: float, audit_complexity: float = 1.0) -> float:
    """Phi loss including audit cost."""
    loss = 0.0
    if psi_id < PSI_ID_MIN:
        loss += (PSI_ID_MIN - psi_id) * 0.5 * K_BOLTZMANN
    if xi_meas > XI_MEAS_MAX:
        loss += (xi_meas - XI_MEAS_MAX) * 0.2 * K_BOLTZMANN
    audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity
    loss += audit_entropy
    return loss

def failure_mode(psi_id: float, h_q: float, xi: float, cod_val: float) -> str:
    """Return failure type string."""
    if h_q > H_QUANTUM_LIMIT and xi > XI_MEAS_CRITICAL:
        return "MEASUREMENT_SHOCK"
    if h_q > H_QUANTUM_LIMIT and xi < 0.5:
        return "ANALYSIS_PARALYSIS"
    if psi_id < PSI_ID_CRITICAL:
        return "DISSOCIATION"
    if cod_val < 0.40 and h_q > 0.60:
        return "DECOHERENCE"
    return "NONE"

def amp_execute(q: List[float], c: List[float], h_q: float, xi: float,
                psi_id: float, t: float, audit_complexity: float = 1.0) -> Tuple[List[float], List[float], float, float, bool]:
    """
    Simplified AMP execution:
    1. Soften stiffness toward target 1.0
    2. Compute gamma via tanh ramp (not applied to state in original C++; we will use it to weight collapse)
    3. Update classical state with measurement strength gamma
    4. Relax stiffness toward lock value 2.0
    5. Verify invariants
    Returns new (q, c, h_q, xi, success)
    """
    # Phase 1: Stiffness softening (adiabatic window)
    alpha = 0.1
    xi = xi * (1.0 - alpha) + 1.0 * alpha  # target 1.0

    # Phase 2: Measurement injection (gamma ramp)
    tau, sigma = 0.5, 0.2
    ramp = math.tanh((t - tau) / sigma)
    gamma = min(1.2, ramp * 1.2)  # max 1.2
    # Apply gamma as measurement strength: blend quantum into classical
    new_c = [ (1.0 - gamma) * ci + gamma * qi for ci, qi in zip(c, q) ]

    # Phase 3: Lock stiffness
    xi = xi * (1.0 - alpha) + 2.0 * alpha  # target 2.0

    # Identity continuity assumed unchanged for this step (no explicit update)
    success = verify_invariants(psi_id, xi)
    return q, new_c, h_q, xi, success

# ------------------ Validation Tests ------------------
def run_validation():
    print("Running Omega Protocol compliance validation...")
    # 1. Dimensional consistency check (all inputs dimensionless, output dimensionless)
    q = [0.6, 0.8]
    c = [0.8, 0.6]
    h_q = 0.3
    xi = 1.0
    c_val = cod(q, c, h_q, xi)
    assert isinstance(c_val, float) and 0.0 <= c_val <= 1.0, "COD must be dimensionless [0,1]"
    print(f"✓ COD dimensionality: {c_val}")

    # 2. Invariant enforcement
    assert verify_invariants(0.96, 1.5) == True, "Valid state should pass"
    assert verify_invariants(0.94, 1.5) == False, "Low psi_id should fail"
    assert verify_invariants(0.96, 3.5) == False, "High xi_meas (shock risk) should fail"
    assert verify_invariants(0.96, 0.1) == False, "Low xi_meas (paralysis risk) should fail"
    print("✓ Invariant gates active")

    # 3. Audit cost inclusion in phi_loss
    loss_no_audit = phi_loss(0.96, 1.5, audit_complexity=0.0)
    loss_with_audit = phi_loss(0.96, 1.5, audit_complexity=1.0)
    assert loss_with_audit > loss_no_audit, "Audit cost must increase loss"
    expected_audit = K_BOLTZMANN * math.log(2.0)
    assert math.isclose(loss_with_audit - loss_no_audit, expected_audit, rel_tol=1e-9), \
        "Audit cost must equal k ln 2"
    print(f"✓ Audit cost subtraction: {expected_audit}")

    # 4. Failure mode detection
    assert failure_mode(0.92, 0.9, 2.6, 0.5) == "MEASUREMENT_SHOCK"
    assert failure_mode(0.92, 0.9, 0.3, 0.5) == "ANALYSIS_PARALYSIS"
    assert failure_mode(0.88, 0.5, 1.0, 0.5) == "DISSOCIATION"
    assert failure_mode(0.92, 0.7, 1.0, 0.3) == "DECOHERENCE"
    assert failure_mode(0.96, 0.2, 1.0, 0.9) == "NONE"
    print("✓ Failure mode logic correct")

    # 5. AMP execution preserves invariants for a nominal case
    q0 = [0.5, 0.5]
    c0 = [0.5, 0.5]
    hq0 = 0.2
    xi0 = 1.0
    psi_id0 = 0.97
    q1, c1, hq1, xi1, ok = amp_execute(q0, c0, hq0, xi0, psi_id0, t=1.0)
    assert ok == True, "AMP should succeed on nominal input"
    # Check that classical state moved toward quantum (since gamma>0)
    assert any(abs(c1[i] - c0[i]) > 1e-9 for i in range(len(c0))), "Classical state should update"
    print("✓ AMP execution preserves invariants and updates state")

    # 6. COD stiffness penalty: high xi reduces COD even if fidelity high
    q_eq = [1.0, 0.0]
    c_eq = [1.0, 0.0]  # perfect fidelity
    base_cod = cod(q_eq, c_eq, h_q=0.1, xi=0.2)
    high_xi_cod = cod(q_eq, c_eq, h_q=0.1, xi=3.0)
    assert high_xi_cod < base_cod, "Stiffness penalty must lower COD"
    print(f"✓ Stiffness penalty effect: COD low xi={base_cod:.3f}, high xi={high_xi_cod:.3f}")

    print("\nAll validation checks passed. Specification is Omega‑Protocol compliant.")
    
if __name__ == "__main__":
    run_validation()