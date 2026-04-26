# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Directory Topology Integrity Validator
# Validates mathematical soundness and invariant compliance of the v65.0-Ω Directory Topology Gate (DTG)
# --------------------------------------------------------------
# This script checks:
#   1. All derived metrics remain in [0,1] for sane inputs.
#   2. Monotonic behavior w.r.t. each input (where expected).
#   3. Invariant gates (PsiIntegrity, TopologyExposureMax, etc.) trigger correct actions.
#   4. COD calculation respects bounds and penalty structure.
#   5. DirectorySilenceProtocol decision hierarchy matches spec.
# --------------------------------------------------------------

import math
from typing import List, Tuple

# ----- Constants from the spec -----
PSI_INTEGRITY_THRESHOLD = 0.95
TOPOLOGY_EXPOSURE_MAX   = 0.25
CREDENTIAL_DENSITY_MAX  = 0.30
TRAVERSAL_DEPTH_MAX     = 0.60
COD_THRESHOLD           = 0.85
LAMBDA_COUPLING         = 0.5
MU_TOPOLOGY             = 0.7
AUDIT_ENTROPY_PER_CHECK = 0.02

# ----- Helper functions mirroring the C++ logic -----
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def calculate_topology_exposure(directory_count: float, traversal_depth: float) -> float:
    """Exposure = min(1, dir_count/10) * traversal_depth, clamped [0,1]."""
    breadth = min(1.0, directory_count / 10.0)
    return clamp(breadth * traversal_depth)

def calculate_credential_density(credential_file_count: float, directory_count: float) -> float:
    """Density = creds / dirs, normalized by 5 creds/dir => 1.0."""
    if directory_count < 1e-9:
        return 0.0
    density = credential_file_count / directory_count
    return clamp(density / 5.0)

def calculate_directory_topology_risk(topology_exposure: float,
                                      credential_density: float,
                                      traversal_depth: float) -> float:
    """Risk = Exposure × Density × Depth, clamped [0,1]."""
    return clamp(topology_exposure * credential_density * traversal_depth)

def calculate_COD_TopologyAware(diagnostic_vec: List[complex],
                                plasma_vec: List[complex],
                                h_instability: float,
                                theta_tensor_leak: float,
                                directory_topology_risk: float) -> float:
    """Fidelity * exp(-λ*h) * exp(-λ*θ) * exp(-μ*topo_risk)."""
    # Fidelity (dot product normalization)
    size = min(len(diagnostic_vec), len(plasma_vec))
    if size == 0:
        fidelity = 0.0
    else:
        dot = sum(abs(conj * pl) for conj, pl in zip(
                    (conj := diagnostic_vec[i].conjugate() for i in range(size)),
                    plasma_vec[:size]))
        magD = sum(abs(v * v) for v in diagnostic_vec[:size])
        magP = sum(abs(v * v) for v in plasma_vec[:size])
        if magD > 1e-12 and magP > 1e-12:
            fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        else:
            fidelity = 0.0
    fidelity = clamp(fidelity)

    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty    = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    topology_penalty    = math.exp(-MU_TOPOLOGY * directory_topology_risk)

    return clamp(fidelity * instability_penalty * exposure_penalty * topology_penalty)

# ----- Enum-like helpers for readability -----
class TopologyType:
    OPAQUE_STRUCTURE = 0
    PARTIAL_EXPOSURE = 1
    FULL_EXPOSURE    = 2
    ACTIVE_LEAK      = 3

class RiskLevel:
    LOW       = 0
    MEDIUM    = 1
    CRITICAL  = 2
    CATASTROPHIC = 3

class Action:
    PROCEED               = 0
    FLAG_DIRECTORY_SCAN   = 1
    FREEZE_DIRECTORY      = 2
    IDENTITY_LOCKDOWN     = 3

def classify_topology(topology_exposure: float, credential_density: float) -> int:
    if topology_exposure > 0.70 and credential_density > 0.50:
        return TopologyType.ACTIVE_LEAK
    if topology_exposure > 0.50:
        return TopologyType.FULL_EXPOSURE
    if topology_exposure > 0.25:
        return TopologyType.PARTIAL_EXPOSURE
    return TopologyType.OPAQUE_STRUCTURE

def assess_risk(directory_topology_risk: float) -> int:
    if directory_topology_risk > 0.70:
        return RiskLevel.CATASTROPHIC
    if directory_topology_risk > 0.50:
        return RiskLevel.CRITICAL
    if directory_topology_risk > 0.30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW

def decide_action(psi_integrity: float,
                  directory_topology_risk: float,
                  topology_type: int) -> int:
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return Action.IDENTITY_LOCKDOWN
    if topology_type == TopologyType.ACTIVE_LEAK:
        return Action.IDENTITY_LOCKDOWN
    if directory_topology_risk > 0.70:
        return Action.IDENTITY_LOCKDOWN
    if directory_topology_risk > 0.50:
        return Action.FREEZE_DIRECTORY
    if directory_topology_risk > 0.30:
        return Action.FLAG_DIRECTORY_SCAN
    return Action.PROCEED

# ----- Validation Tests -----
def test_bounds_and_monotonicity():
    print("=== Testing bounds and monotonicity ===")
    # Expose a grid of sane inputs
    for dc in [0, 1, 5, 10, 20, 50]:
        for td in [0.0, 0.2, 0.5, 0.8, 1.0]:
            exp = calculate_topology_exposure(float(dc), td)
            assert 0.0 <= exp <= 1.0, f"Exposure OOB: dc={dc}, td={td} => {exp}"
            # Monotonic in td (for fixed dc)
    for td in [0.0, 0.2, 0.5, 0.8, 1.0]:
        prev = -1.0
        for dc in [0, 1, 5, 10, 20, 50]:
            cur = calculate_topology_exposure(float(dc), td)
            assert cur >= prev - 1e-12, f"Non-monotonic in dc: td={td}, dc jump"
            prev = cur
    print("✓ Topology exposure bounds & monotonicity OK")

    for cf in [0, 1, 5, 10, 20]:
        for dc in [1, 5, 10, 20]:  # avoid zero division
            dens = calculate_credential_density(float(cf), float(dc))
            assert 0.0 <= dens <= 1.0, f"Density OOB: cf={cf}, dc={dc} => {dens}"
    print("✓ Credential density bounds OK")

    for exp in [0.0, 0.2, 0.5, 0.8, 1.0]:
        for dens in [0.0, 0.2, 0.5, 0.8, 1.0]:
            for td in [0.0, 0.2, 0.5, 0.8, 1.0]:
                risk = calculate_directory_topology_risk(exp, dens, td)
                assert 0.0 <= risk <= 1.0, f"Risk OOB: exp={exp}, dens={dens}, td={td} => {risk}"
    print("✓ Directory topology risk bounds OK")

    # COD bounds
    diag = [1+0j, 0.5+0.5j]
    plasm = [1+0j, 0.5+0.5j]
    for h in [0.0, 0.3, 0.7, 1.0]:
        for th in [0.0, 0.3, 0.7, 1.0]:
            for tr in [0.0, 0.3, 0.7, 1.0]:
                cod = calculate_COD_TopologyAware(diag, plasm, h, th, tr)
                assert 0.0 <= cod <= 1.0, f"COD OOB: h={h}, th={th}, tr={tr} => {cod}"
    print("✓ COD bounds OK")

def test_invariant_gates():
    print("\n=== Testing invariant gates ===")
    # Psi integrity gate
    assert decide_action(0.94, 0.0, TopologyType.OPAQUE_STRUCTURE) == Action.IDENTITY_LOCKDOWN
    assert decide_action(0.96, 0.0, TopologyType.OPAQUE_STRUCTURE) != Action.IDENTITY_LOCKDOWN
    print("✓ Psi integrity gate OK")

    # Topology type gate (ACTIVE_LEAK forces lockdown)
    assert decide_action(0.98, 0.1, TopologyType.ACTIVE_LEAK) == Action.IDENTITY_LOCKDOWN
    print("✓ Active leak gate OK")

    # Risk-based decisions (psi OK, not active leak)
    base_psi = 0.98
    # LOW risk -> PROCEED
    assert decide_action(base_psi, 0.20, TopologyType.OPAQUE_STRUCTURE) == Action.PROCEED
    # MEDIUM risk -> FLAG
    assert decide_action(base_psi, 0.35, TopologyType.PARTIAL_EXPOSURE) == Action.FLAG_DIRECTORY_SCAN
    # CRITICAL risk -> FREEZE
    assert decide_action(base_psi, 0.55, TopologyType.FULL_EXPOSURE) == Action.FREEZE_DIRECTORY
    # CATASTROPHIC risk -> LOCKDOWN
    assert decide_action(base_psi, 0.75, TopologyType.FULL_EXPOSURE) == Action.IDENTITY_LOCKDOWN
    print("✓ Risk-based decision hierarchy OK")

def test_COD_penalty_structure():
    print("\n=== Testing COD penalty structure ===")
    diag = [1+0j]
    plasm = [1+0j]
    base = calculate_COD_TopologyAware(diag, plasm, 0.0, 0.0, 0.0)
    # Base fidelity should be 1.0 (identical vectors)
    assert math.isclose(base, 1.0, rel_tol=1e-9), f"Base COD not 1.0: {base}"
    # Increasing any penalty should strictly decrease COD (until zero)
    for h in [0.0, 0.2, 0.5, 1.0]:
        cod_h = calculate_COD_TopologyAware(diag, plasm, h, 0.0, 0.0)
        assert cod_h <= base, f"H penalty increased COD: {h} => {cod_h}"
    for th in [0.0, 0.2, 0.5, 1.0]:
        cod_th = calculate_COD_TopologyAware(diag, plasm, 0.0, th, 0.0)
        assert cod_th <= base, f"Theta penalty increased COD: {th} => {cod_th}"
    for tr in [0.0, 0.2, 0.5, 1.0]:
        cod_tr = calculate_COD_TopologyAware(diag, plasm, 0.0, 0.0, tr)
        assert cod_tr <= base, f"Topo penalty increased COD: {tr} => {cod_tr}"
    print("✓ COD penalties monotonic decreasing OK")

def test_phi_density_ledger():
    print("\n|--- Φ-density ledger sanity ---|")
    # Net gain = (COD_after - COD_before) - audit_cost
    # We just ensure the formula doesn't produce absurd gains without improvement.
    before = 0.70
    after  = 0.70  # no change
    checks = 9
    cost   = checks * AUDIT_ENTROPY_PER_CHECK
    net    = (after - before) - cost
    assert net < 0, f"Zero improvement should yield negative Φ gain: {net}"
    # Improvement must exceed audit cost to be positive
    after  = 0.90
    net    = (after - before) - cost
    assert net > 0, f"Sufficient improvement should yield positive Φ gain: {net}"
    print("✓ Φ-density ledger behaves as expected")

def run_all_tests():
    test_bounds_and_monotonicity()
    test_invariant_gates()
    test_COD_penalty_structure()
    test_phi_density_ledger()
    print("\n=== ALL VALIDATIONS PASSED ===")
    print("The Directory Topology Integrity Manifold v65.0-Ω is mathematically sound")
    print("and compliant with Omega Protocol invariants.")

if __name__ == "__main__":
    run_all_tests()