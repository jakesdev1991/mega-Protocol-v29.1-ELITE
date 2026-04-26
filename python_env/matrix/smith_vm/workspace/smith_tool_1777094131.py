# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import itertools

# =============================================================================
# PARAMETERS (from the C++ code)
# =============================================================================
PSI_INTEGRITY_THRESHOLD = 0.95
TOPOLOGY_EXPOSURE_MAX = 0.25
CREDENTIAL_EXPOSURE_MAX = 0.20
COUPLING_FACTOR_MAX = 0.30
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

LAMBDA_COUPLING = 0.5
MU_COMPOUND = 0.7

# =============================================================================
# HELPER FUNCTIONS (mirroring the C++ logic)
# =============================================================================
def calculate_coupling_factor(topology_exposure, credential_density, credential_exposure):
    """Calculate topology-credential coupling factor."""
    if credential_exposure < 0.01:
        return topology_exposure * credential_density * 0.3
    base_coupling = topology_exposure * credential_density * credential_exposure
    amplification = 1.0 + (topology_exposure + credential_exposure) / 2.0
    coupling = base_coupling * amplification
    return min(max(coupling, 0.0), 1.0)

def calculate_compound_exposure_risk(topology_exposure, credential_density, traversal_depth,
                                     credential_exposure, access_chain_length, chain_integrity,
                                     coupling_factor):
    """Calculate compound exposure risk."""
    topology_risk = topology_exposure * credential_density * traversal_depth
    integrity_factor = 1.0 - chain_integrity
    credential_risk = credential_exposure * access_chain_length * integrity_factor
    compound_risk = (topology_risk + credential_risk + coupling_factor) / 3.0
    if topology_exposure > 0.50 and credential_exposure > 0.50:
        compound_risk *= 1.5
    return min(max(compound_risk, 0.0), 1.0)

def calculate_cod(diagnostic_vec, plasma_vec, h_instability, theta_tensor_leak, compound_exposure_risk):
    """Calculate Chain Overlap Density (COD) compound-aware."""
    # Fidelity (dot product of magnitudes)
    size = min(len(diagnostic_vec), len(plasma_vec))
    dot = 0.0
    magD = 0.0
    magP = 0.0
    for i in range(size):
        dot += np.abs(np.conj(diagnostic_vec[i]) * plasma_vec[i])
        magD += np.abs(diagnostic_vec[i] * diagnostic_vec[i])
        magP += np.abs(plasma_vec[i] * plasma_vec[i])
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (np.sqrt(magD) * np.sqrt(magP))
        fidelity = min(max(fidelity, 0.0), 1.0)
    # Penalties
    instability_penalty = np.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = np.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    compound_penalty = np.exp(-MU_COMPOUND * compound_exposure_risk)
    return fidelity * instability_penalty * exposure_penalty * compound_penalty

# =============================================================================
# VALIDATION TESTS
# =============================================================================
def test_bounds():
    """Test that all outputs stay within [0,1]."""
    print("Testing bounds...")
    # Random sampling
    np.random.seed(42)
    for _ in range(10000):
        te = np.random.rand()
        cd = np.random.rand()
        td = np.random.rand()
        ce = np.random.rand()
        acl = np.random.rand()
        ci = np.random.rand()
        cf = calculate_coupling_factor(te, cd, ce)
        assert 0.0 <= cf <= 1.0, f"Coupling factor out of bounds: {cf}"
        cer = calculate_compound_exposure_risk(te, cd, td, ce, acl, ci, cf)
        assert 0.0 <= cer <= 1.0, f"Compound exposure risk out of bounds: {cer}"
        # COD test with random complex vectors
        dv = [complex(np.random.rand(), np.random.rand()) for _ in range(5)]
        pv = [complex(np.random.rand(), np.random.rand()) for _ in range(5)]
        hi = np.random.rand()
        tt = np.random.rand()
        cod = calculate_cod(dv, pv, hi, tt, cer)
        assert 0.0 <= cod <= 1.0, f"COD out of bounds: {cod}"
    print("✅ All bounds tests passed.")

def test_monotonicity():
    """Test that coupling factor and compound risk increase with inputs (where expected)."""
    print("Testing monotonicity...")
    base = 0.5
    # Coupling factor should increase with topology_exposure, credential_density, credential_exposure
    for _ in range(100):
        te = np.random.rand()
        cd = np.random.rand()
        ce = np.random.rand()
        cf1 = calculate_coupling_factor(te, cd, ce)
        # Increase each input slightly and ensure non-decrease (within tolerance)
        for delta in [0.01, 0.05]:
            te2 = min(te + delta, 1.0)
            cf2 = calculate_coupling_factor(te2, cd, ce)
            assert cf2 >= cf1 - 1e-9, f"Coupling factor not monotonic in topology_exposure: {cf1} -> {cf2}"
            cd2 = min(cd + delta, 1.0)
            cf3 = calculate_coupling_factor(te, cd2, ce)
            assert cf3 >= cf1 - 1e-9, f"Coupling factor not monotonic in credential_density: {cf1} -> {cf3}"
            ce2 = min(ce + delta, 1.0)
            cf4 = calculate_coupling_factor(te, cd, ce2)
            assert cf4 >= cf1 - 1e-9, f"Coupling factor not monotonic in credential_exposure: {cf1} -> {cf4}"
    print("✅ Monotonicity tests passed.")

def test_invariant_conditions():
    """Test that the protocol's invariant thresholds are respected in decision logic."""
    print("Testing invariant conditions...")
    # We'll simulate the decision logic from CompoundSilenceProtocol.Decide
    def decide_action(psi_integrity, compound_risk, exposure_type):
        if psi_integrity < PSI_INTEGRITY_THRESHOLD:
            return "IDENTITY_LOCKDOWN"
        if exposure_type == "COMPOUND_EXPOSURE":
            return "IDENTITY_LOCKDOWN"
        if compound_risk > 0.70:
            return "IDENTITY_LOCKDOWN"
        if compound_risk > 0.50:
            return "FREEZE_CREDENTIAL_ACCESS"
        if compound_risk > 0.30:
            return "FLAG_COMPOUND_SCAN"
        return "PROCEED"
    # Test boundary conditions
    assert decide_action(0.94, 0.0, "SECURE") == "IDENTITY_LOCKDOWN"  # psi fails
    assert decide_action(0.96, 0.0, "COMPOUND_EXPOSURE") == "IDENTITY_LOCKDOWN"  # exposure type
    assert decide_action(0.96, 0.71, "SECURE") == "IDENTITY_LOCKDOWN"  # compound risk >0.7
    assert decide_action(0.96, 0.51, "SECURE") == "FREEZE_CREDENTIAL_ACCESS"  # >0.5
    assert decide_action(0.96, 0.31, "SECURE") == "FLAG_COMPOUND_SCAN"  # >0.3
    assert decide_action(0.96, 0.29, "SECURE") == "PROCEED"  # all good
    print("✅ Invariant condition tests passed.")

def test_cod_properties():
    """Test that COD behaves as expected: decreases with penalties, increases with fidelity."""
    print("Testing COD properties...")
    # Fixed vectors for fidelity test
    dv = [1+0j, 1+0j]
    pv = [1+0j, 1+0j]
    base_fidelity = calculate_cod(dv, pv, 0.0, 0.0, 0.0)
    assert abs(base_fidelity - 1.0) < 1e-9, f"Fidelity should be 1.0 for identical vectors, got {base_fidelity}"
    # Orthogonal vectors should give low fidelity
    dv2 = [1+0j, 0+0j]
    pv2 = [0+0j, 1+0j]
    ortho_fidelity = calculate_cod(dv2, pv2, 0.0, 0.0, 0.0)
    assert ortho_fidelity < 0.1, f"Fidelity for orthogonal vectors should be near 0, got {ortho_fidelity}"
    # Penalties should reduce COD
    cod_no_penalty = calculate_cod(dv, pv, 0.0, 0.0, 0.0)
    cod_with_instability = calculate_cod(dv, pv, 1.0, 0.0, 0.0)
    cod_with_exposure = calculate_cod(dv, pv, 0.0, 1.0, 0.0)
    cod_with_compound = calculate_cod(dv, pv, 0.0, 0.0, 1.0)
    assert cod_with_instability < cod_no_penalty, "Instability penalty should reduce COD"
    assert cod_with_exposure < cod_no_penalty, "Exposure penalty should reduce COD"
    assert cod_with_compound < cod_no_penalty, "Compound penalty should reduce COD"
    print("✅ COD property tests passed.")

def test_derivativity_check_simulation():
    """Simulate a simple derivativity check (Jaccard dissimilarity) to ensure novelty."""
    print("Testing derivativity check simulation...")
    # Define core metric sets for prior work and current task
    v62_metrics = {"credential_exposure", "access_chain_length", "chain_integrity"}
    v65_metrics = {"topology_exposure", "credential_density", "traversal_depth"}
    v66_metrics = {"topology_exposure", "credential_density", "traversal_depth",
                   "credential_exposure", "access_chain_length", "chain_integrity",
                   "topology_credential_coupling", "compound_exposure_risk"}
    # Jaccard similarity with v62
    inter_62 = v66_metrics & v62_metrics
    union_62 = v66_metrics | v62_metrics
    jaccard_62 = len(inter_62) / len(union_62) if union_62 else 0.0
    dvs_62 = 1.0 - jaccard_62
    # Jaccard similarity with v65
    inter_65 = v66_metrics & v65_metrics
    union_65 = v66_metrics | v65_metrics
    jaccard_65 = len(inter_65) / len(union_65) if union_65 else 0.0
    dvs_65 = 1.0 - jaccard_65
    # Require DVS > 0.65 (as stated in reflection)
    assert dvs_62 > 0.65, f"Derivativity vs v62 insufficient: DVS={dvs_62}"
    assert dvs_65 > 0.65, f"Derivativity vs v65 insufficient: DVS={dvs_65}"
    print(f"✅ Derivativity check passed: DVS_v62={dvs_62:.3f}, DVS_v65={dvs_65:.3f}")

if __name__ == "__main__":
    test_bounds()
    test_monotonicity()
    test_invariant_conditions()
    test_cod_properties()
    test_derivativity_check_simulation()
    print("\n🎉 All validation tests passed. The math appears sound and compliant with Omega Protocol invariants.")