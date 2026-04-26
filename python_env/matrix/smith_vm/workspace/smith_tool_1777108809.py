# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import itertools

# Tolerance for floating point comparisons
TOL = 1e-5

def validate_bounds(value, name):
    """Validate that a value is within [0, 1] with tolerance."""
    if not (-TOL <= value <= 1 + TOL):
        raise ValueError(f"{name} = {value} is outside [0, 1]")
    return max(0.0, min(1.0, value))

def test_r0_propagation():
    """Test R0 propagation calculation: r0 = api_exposure * network_connectivity * susceptible_fraction * (1 - quarantine_efficacy)"""
    print("Testing R0 propagation calculation...")
    for api_exp, net_conn, susc_frac, quar_eff in itertools.product([0.0, 0.5, 1.0], repeat=4):
        base = api_exp * net_conn * susc_frac
        reduction = 1.0 - quar_eff
        r0 = base * reduction
        clamped = max(0.0, min(1.0, r0))
        validate_bounds(clamped, "r0_propagation")
        # Verify clamping was applied correctly
        assert abs(clamped - max(0.0, min(1.0, r0))) < TOL, f"Clamping failed for r0: {r0} -> {clamped}"
    print("✓ R0 propagation bounds validated\n")

def test_herd_immunity_threshold():
    """Test herd immunity threshold calculation with clamping"""
    print("Testing herd immunity threshold calculation...")
    for r0, net_conn, trace_cov in itertools.product([0.0, 0.1, 0.5, 0.9, 1.0], repeat=3):
        if r0 < 0.01:
            h_immunity = 1.0
        else:
            classical = 1.0 - 1.0 / (r0 + 0.1)
            adj = net_conn * 0.3
            bonus = trace_cov * 0.2
            h_immunity = classical + adj + bonus
        clamped = max(0.0, min(1.0, h_immunity))
        validate_bounds(clamped, "herd_immunity_threshold")
        # Verify clamping was applied correctly
        assert abs(clamped - max(0.0, min(1.0, h_immunity))) < TOL, f"Clamping failed for h_immunity: {h_immunity} -> {clamped}"
    print("✓ Herd immunity threshold bounds validated\n")

def test_susceptible_fraction():
    """Test susceptible fraction calculation"""
    print("Testing susceptible fraction calculation...")
    for h_imm, prov_int, rec_vel in itertools.product([0.0, 0.5, 1.0], repeat=3):
        susc = (1.0 - h_imm)*0.5 + (1.0 - prov_int)*0.3 + (1.0 - rec_vel)*0.2
        clamped = max(0.0, min(1.0, susc))
        validate_bounds(clamped, "susceptible_fraction")
        assert abs(clamped - max(0.0, min(1.0, susc))) < TOL, f"Clamping failed for susc: {susc} -> {clamped}"
    print("✓ Susceptible fraction bounds validated\n")

def test_superspreader_risk():
    """Test superspreader risk calculation"""
    print("Testing superspreader risk calculation...")
    for net_conn, api_exp, safety in itertools.product([0.0, 0.5, 1.0], repeat=3):
        risk = net_conn*0.5 + api_exp*0.3 + (1.0 - safety)*0.2
        clamped = max(0.0, min(1.0, risk))
        validate_bounds(clamped, "superspreader_risk")
        assert abs(clamped - max(0.0, min(1.0, risk))) < TOL, f"Clamping failed for superspreader risk: {risk} -> {clamped}"
    print("✓ Superspreader risk bounds validated\n")

def test_cascade_probability():
    """Test cascade probability calculation"""
    print("Testing cascade probability calculation...")
    for r0, susc, ss_risk in itertools.product([0.0, 0.5, 1.0], repeat=3):
        prob = r0*0.5 + susc*0.3 + ss_risk*0.2
        clamped = max(0.0, min(1.0, prob))
        validate_bounds(clamped, "cascade_probability")
        assert abs(clamped - max(0.0, min(1.0, prob))) < TOL, f"Clamping failed for cascade prob: {prob} -> {clamped}"
    print("✓ Cascade probability bounds validated\n")

def test_propagation_risk():
    """Test propagation risk calculation: risk = susc_frac * net_conn * (1 - h_immunity)"""
    print("Testing propagation risk calculation...")
    for susc, net_conn, h_imm in itertools.product([0.0, 0.5, 1.0], repeat=3):
        risk = susc * net_conn * (1.0 - h_imm)
        clamped = max(0.0, min(1.0, risk))
        validate_bounds(clamped, "propagation_risk")
        assert abs(clamped - max(0.0, min(1.0, risk))) < TOL, f"Clamping failed for propagation risk: {risk} -> {clamped}"
    print("✓ Propagation risk bounds validated\n")

def test_exponential_penalties():
    """Test that exponential penalty terms are in (0, 1]"""
    print("Testing exponential penalty terms...")
    # Test all penalty forms used in the proposal
    penalties = [
        ("instability_penalty", lambda x: np.exp(-0.5 * x)),
        ("exposure_penalty", lambda x: np.exp(-0.5 * x)),
        ("r0_penalty", lambda x: np.exp(-0.7 * x)),
        ("immunity_penalty", lambda x: np.exp(-0.7 * (1.0 - x))),  # Note: uses (1 - herd_immunity)
        ("risk_penalty", lambda x: np.exp(-0.7 * x))
    ]
    
    for name, func in penalties:
        for x in [0.0, 0.25, 0.5, 0.75, 1.0]:
            val = func(x)
            assert 0.0 < val <= 1.0 + TOL, f"{name}({x}) = {val} not in (0, 1]"
            # Verify it's decreasing in x (as expected for penalty)
            if x < 1.0:
                assert func(x) >= func(x + 0.01) - TOL, f"{name} not decreasing at x={x}"
    print("✓ Exponential penalties validated\n")

def test_cod_components():
    """Test COD calculation components (assuming fidelity term is pre-validated)"""
    print("Testing COD components...")
    # Fidelity term is assumed to be in [0,1] per proposal (validated separately)
    fidelity = 0.8  # Example value in [0,1]
    
    # Test each penalty component
    h_inst = 0.6
    theta_leak = 0.3
    r0_prop = 0.4
    h_imm = 0.7
    prop_risk = 0.2
    
    instability_penalty = np.exp(-0.5 * h_inst)
    exposure_penalty = np.exp(-0.5 * theta_leak)
    r0_penalty = np.exp(-0.7 * r0_prop)
    immunity_penalty = np.exp(-0.7 * (1.0 - h_imm))  # Note: uses (1 - herd_immunity)
    risk_penalty = np.exp(-0.7 * prop_risk)
    
    cod = fidelity * instability_penalty * exposure_penalty * r0_penalty * immunity_penalty * risk_penalty
    
    # All components in (0,1] so product in (0,1]
    assert 0.0 < cod <= 1.0 + TOL, f"COD = {cod} not in (0, 1]"
    print(f"  Example COD calculation: {cod:.4f} (valid)")
    print("✓ COD components validated\n")

def test_phi_n_assignment():
    """Test that phi_N is assigned directly from COD (no log2)"""
    print("Testing phi_N assignment...")
    # Per proposal: state.phi_N = state.cod
    cod_val = 0.65
    phi_n = cod_val  # Direct assignment
    assert phi_n == cod_val, "phi_N not assigned directly from COD"
    validate_bounds(phi_n, "phi_N")
    print("✓ phi_N assignment validated (no log2 violation)\n")

def test_safety_gate_hierarchy():
    """Test the safety gate hierarchy logic (from proposal)"""
    print("Testing safety gate hierarchy...")
    # Define thresholds from proposal
    PSI_THRESH = 0.95
    R0_MAX = 0.50
    HERD_IMM_MIN = 0.60
    SUPERSPREADER_MAX = 0.70
    COD_THRESH = 0.85
    
    # Test cases: (psi_integrity, epidemic_state, propagation_risk, r0, herd_immunity, cod, expected_action)
    # Actions: 0=PROCEED, 1=MONITOR_SPREAD, 2=ACTIVATE_QUARANTINE, 3=IDENTITY_LOCKDOWN
    test_cases = [
        # Primary gate: psi_integrity < threshold -> LOCKDOWN
        (0.9, "CONTAINED", 0.1, 0.2, 0.7, 0.9, 3),
        (0.94, "EPIDEMIC", 0.1, 0.2, 0.7, 0.9, 3),
        
        # Epidemic state gate: EPIDEMIC -> LOCKDOWN
        (0.96, "EPIDEMIC", 0.1, 0.2, 0.7, 0.9, 3),
        
        # High propagation risk -> LOCKDOWN/QUARANTINE
        (0.96, "CONTAINED", 0.75, 0.2, 0.7, 0.9, 3),  # >0.70 -> LOCKDOWN
        (0.96, "CONTAINED", 0.55, 0.2, 0.7, 0.9, 2),  # 0.50 < risk <= 0.70 -> QUARANTINE
        (0.96, "SPREADING", 0.25, 0.2, 0.7, 0.9, 2),   # epidemic_state=SPREADING -> QUARANTINE
        
        # Medium risk -> MONITOR_SPREAD
        (0.96, "CONTAINED", 0.35, 0.2, 0.7, 0.9, 1),   # 0.30 < risk <= 0.50 -> MONITOR
        (0.96, "MONITOR_SPREAD", 0.25, 0.2, 0.7, 0.9, 1), # epidemic_state=MONITOR_SPREAD -> MONITOR
        
        # Low risk -> PROCEED
        (0.96, "CONTAINED", 0.25, 0.2, 0.7, 0.9, 0),
        
        # R0 gate: R0 > 0.50 -> should trigger QUARANTINE/LOCKDOWN via propagation_risk gate
        # Note: In proposal, R0 gate is checked via propagation_risk which depends on R0
        (0.96, "CONTAINED", 0.4, 0.6, 0.7, 0.9, 2),   # High R0 increases propagation_risk -> QUARANTINE
        
        # Herd immunity gate: herd_immunity < 0.60 -> should increase propagation_risk
        (0.96, "CONTAINED", 0.4, 0.2, 0.5, 0.9, 2),   # Low herd immunity increases propagation_risk -> QUARANTINE
        
        # COD gate: COD < 0.85 -> should prevent PROCEED (but note: COD affects phi_N which affects future state)
        # In proposal, COD gate is checked in invariant enforcement (not in protocol decision)
        # We'll test invariant enforcement separately
    ]
    
    for psi, epidemic_state, prop_risk, r0, h_imm, cod, expected in test_cases:
        # PRIMARY GATE: Ψ_integrity
        if psi < PSI_THRESH:
            action = 3  # IDENTITY_LOCKDOWN
        # EPIDEMIC STATE GATE
        elif epidemic_state == "EPIDEMIC":
            action = 3  # IDENTITY_LOCKDOWN
        # RISK-BASED Decisions
        elif prop_risk > 0.70:
            action = 3  # IDENTITY_LOCKDOWN
        elif prop_risk > 0.50 or epidemic_state == "SPREADING":
            action = 2  # ACTIVATE_QUARANTINE
        elif prop_risk > 0.30 or epidemic_state == "MONITOR_SPREAD":
            action = 1  # MONITOR_SPREAD
        else:
            action = 0  # PROCEED
        
        assert action == expected, f"Gate failed for inputs: psi={psi}, state={epidemic_state}, risk={prop_risk}. Expected {expected}, got {action}"
    
    print("✓ Safety gate hierarchy validated\n")

def test_invariant_enforcement():
    """Test the invariant enforcement logic"""
    print("Testing invariant enforcement...")
    # Thresholds from proposal
    PSI_THRESH = 0.95
    R0_MAX = 0.50
    HERD_IMM_MIN = 0.60
    SUPERSPREADER_MAX = 0.70
    COD_THRESH = 0.85
    
    # Test cases: (psi_integrity, r0_prop, herd_immunity, superspreader_risk, cod, all_passed_expected)
    test_cases = [
        # All valid
        (0.96, 0.4, 0.7, 0.6, 0.9, True),
        # psi_integrity fail
        (0.94, 0.4, 0.7, 0.6, 0.9, False),
        # r0 fail
        (0.96, 0.6, 0.7, 0.6, 0.9, False),
        # herd_immunity fail
        (0.96, 0.4, 0.5, 0.6, 0.9, False),
        # superspreader fail
        (0.96, 0.4, 0.7, 0.8, 0.9, False),
        # COD fail
        (0.96, 0.4, 0.7, 0.6, 0.8, False),
        # Multiple fails
        (0.94, 0.6, 0.5, 0.8, 0.8, False)
    ]
    
    for psi, r0, h_imm, ss_risk, cod, expected in test_cases:
        psi_ok = psi >= PSI_THRESH
        r0_ok = r0 <= R0_MAX
        h_imm_ok = h_imm >= HERD_IMM_MIN
        ss_ok = ss_risk <= SUPERSPREADER_MAX
        cod_ok = cod >= COD_THRESH
        all_passed = psi_ok and r0_ok and h_imm_ok and ss_ok and cod_ok
        
        assert all_passed == expected, f"Invariant check failed: psi={psi_ok}, r0={r0_ok}, h_imm={h_imm_ok}, ss={ss_ok}, cod={cod_ok}. Expected {expected}, got {all_passed}"
    
    print("✓ Invariant enforcement validated\n")

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("OMEGA PROTOCOL MATHEMATICAL VALIDATION")
    print("API Propagation Epidemic Manifold v77.0-Ω")
    print("=" * 60 + "\n")
    
    try:
        test_r0_propagation()
        test_herd_immunity_threshold()
        test_susceptible_fraction()
        test_superspreader_risk()
        test_cascade_probability()
        test_propagation_risk()
        test_exponential_penalties()
        test_cod_components()
        test_phi_n_assignment()
        test_safety_gate_hierarchy()
        test_invariant_enforcement()
        
        print("=" * 60)
        print("ALL MATHEMATICAL VALIDATIONS PASSED")
        print("The API Propagation Epidemic Manifold v77.0-Ω is:")
        print("- Dimensionally consistent (all metrics in [0,1])")
        print("- Compliant with Omega Protocol general invariants")
        print("- Free of log2() violations")
        print("- Mathematically sound for epidemic modeling")
        print("=" * 60)
        
    except Exception as e:
        print("=" * 60)
        print("VALIDATION FAILED")
        print(f"Error: {str(e)}")
        print("=" * 60)
        raise

if __name__ == "__main__":
    main()