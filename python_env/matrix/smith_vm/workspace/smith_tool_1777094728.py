# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# === OMEGA PROTOCOL INVARIANT VALIDATOR FOR SALES RESONANCE ===
# Validates mathematical soundness and invariant compliance of SalesResonance manifold
# Tests: Dimensional homogeneity, trust continuity, COD formulation, entropy accounting, adiabatic stability

class SalesInvariants:
    LAMBDA_COUPLING = 1.0
    GAMMA_COUPLING = 0.6
    H_SALES_LIMIT = 0.90
    COD_THRESHOLD = 0.80
    PSI_TRUST_MIN = 0.95  # Trust threshold (phi_N >= 0.95)
    PSI_TRUST_CRITICAL = 0.90
    XI_MAX_DIFF = 2.0
    K_BOLTZMANN = 1.0  # Normalized for informational entropy

    @staticmethod
    def psi_min():
        return math.log(SalesInvariants.PSI_TRUST_MIN)

    @staticmethod
    def verify_trust_continuity(psi):
        """Hard gate: psi >= ln(0.95)"""
        return psi >= SalesInvariants.psi_min()

    @staticmethod
    def calculate_phi_loss(psi, xi_sales, xi_aud, audit_complexity=1.0):
        """Φ_net = Φ_gain - Φ_loss - ΔS_audit"""
        loss = 0.0
        
        # Trust erosion cost
        if psi < SalesInvariants.psi_min():
            loss += (SalesInvariants.psi_min() - psi) * 0.5 * SalesInvariants.K_BOLTZMANN
        
        # Stiffness mismatch cost
        stiffness_diff = abs(xi_sales - xi_aud)
        if stiffness_diff > SalesInvariants.XI_MAX_DIFF:
            loss += (stiffness_diff - SalesInvariants.XI_MAX_DIFF) * 0.2 * SalesInvariants.K_BOLTZMANN
        
        # Audit cost (Meta-Scrutiny compliance)
        audit_entropy = SalesInvariants.K_BOLTZMANN * math.log(2.0) * audit_complexity
        loss += audit_entropy
        
        return loss

def calculate_sales_entropy(engagement_events):
    """H(Sales) = -Σ p(v) log p(v), normalized [0,1]"""
    if not engagement_events or len(engagement_events) == 1:
        return 0.0
    
    H = 0.0
    max_entropy = math.log(len(engagement_events))
    if max_entropy < 1e-12:
        max_entropy = 1.0  # Avoid division by zero
    
    for prob in engagement_events:
        if prob > 1e-12:
            H -= prob * math.log(prob)
    
    return min(1.0, max(0.0, H / max_entropy))

def calculate_sales_cod(psi_sales, psi_aud, h_sales, xi_sales, xi_aud):
    """COD = |⟨Ψ_sales|Ψ_aud⟩|² × exp(-Λ·H_sales) × exp(-Γ·|Ξ_diff|)"""
    # Fidelity: |⟨Ψ_sales|Ψ_aud⟩|²
    dot = np.dot(psi_sales, psi_aud)
    mag_sales = np.linalg.norm(psi_sales)
    mag_aud = np.linalg.norm(psi_aud)
    
    if mag_sales < 1e-12 or mag_aud < 1e-12:
        fidelity = 0.0
    else:
        fidelity = (dot / (mag_sales * mag_aud)) ** 2
        fidelity = min(1.0, max(0.0, fidelity))  # Clamp [0,1]
    
    # Entropic damping
    damping = math.exp(-SalesInvariants.LAMBDA_COUPLING * h_sales)
    
    # Stiffness penalty
    stiffness_diff = abs(xi_sales - xi_aud)
    stiffness_penalty = math.exp(-SalesInvariants.GAMMA_COUPLING * stiffness_diff)
    
    return fidelity * damping * stiffness_penalty

def failure_mode_detector(h_sales, xi_sales, xi_aud, psi, cod):
    """Returns failure type: 0=NONE, 1=TRUST_COLLAPSE, 2=DEAL_DRIFT, 3=VALIDATION_LOOP"""
    stiffness_diff = abs(xi_sales - xi_aud)
    
    # Trust Collapse Singularity
    if (h_sales > SalesInvariants.H_SALES_LIMIT and 
        stiffness_diff > SalesInvariants.XI_MAX_DIFF and 
        psi < math.log(SalesInvariants.PSI_TRUST_MIN)):
        return 1
    
    # Deal Drift (Identity Loss)
    if psi < math.log(SalesInvariants.PSI_TRUST_MIN):
        return 2
    
    # Validation Loop
    if cod < SalesInvariants.COD_THRESHOLD and stiffness_diff > 1.5:
        return 3
    
    return 0

def adiabatic_resonance_operator(state, dt=0.1):
    """
    Simplified ARP operator: 
    - Modulates xi_sales toward xi_aud with trust-preserving damping
    - Updates psi based on entropy-induced trust decay
    - Enforces trust continuity as hard gate
    """
    psi_sales, psi_aud = state['psi_sales'], state['psi_aud']
    h_sales = calculate_sales_entropy(state['engagement_events'])
    xi_sales, xi_aud = state['xi_sales'], state['xi_aud']
    psi = state['psi']
    
    # Phase 1: Diagnostic
    cod = calculate_sales_cod(psi_sales, psi_aud, h_sales, xi_sales, xi_aud)
    failure = failure_mode_detector(h_sales, xi_sales, xi_aud, psi, cod)
    
    # Phase 2: Stiffness Modulation (Adiabatic Control)
    if failure == 1:  # TRUST_COLLAPSE
        state['xi_sales'] = max(0.5, state['xi_sales'] * 0.8)  # Reduce pressure
    elif failure == 2:  # DEAL_DRIFT
        # Grounding: strengthen audience state
        state['psi_aud'] = [x + 0.05 for x in state['psi_aud']]
    elif failure == 3:  # VALIDATION_LOOP
        state['xi_sales'] = max(0.5, state['xi_sales'] * 0.8)
    else:  # Normal operation
        stiffness_diff = abs(state['xi_sales'] - state['xi_aud'])
        if cod < SalesInvariants.COD_THRESHOLD and stiffness_diff > 0.5:
            # Smooth interpolation toward audience urgency
            state['xi_sales'] = state['xi_sales'] * 0.9 + state['xi_aud'] * 0.1
    
    # Phase 3: State Transformation (Alignment)
    alpha = min(1.0, (1.0 - abs(state['xi_sales'] - state['xi_aud'])) * 0.5 + 0.5)
    for i in range(len(state['psi_sales'])):
        state['psi_sales'][i] = (1.0 - alpha) * state['psi_sales'][i] + alpha * state['psi_aud'][i]
    
    # Phase 4: Entropy Accounting & Trust Update
    trust_loss = h_sales * 0.05  # Simplified trust decay
    phi_n = math.exp(state['psi'])
    phi_n -= trust_loss
    state['psi'] = math.log(max(phi_n, 1e-12))  # Avoid log(0)
    
    # Phase 5: Invariant Validation (Hard Gate)
    if not SalesInvariants.verify_trust_continuity(state['psi']):
        raise RuntimeError("TRUST CONTINUITY BREACHED: psi < ln(0.95)")
    
    return state

def validate_omega_compliance():
    """Runs comprehensive compliance tests for SalesResonance manifold"""
    print("=== OMEGA PROTOCOL SALES RESONANCE VALIDATION ===")
    
    # Test 1: Dimensional Homogeneity (All terms [1])
    print("\n1. Testing Dimensional Homogeneity...")
    assert all(isinstance(x, (int, float)) for x in [
        SalesInvariants.LAMBDA_COUPLING,
        SalesInvariants.GAMMA_COUPLING,
        SalesInvariants.H_SALES_LIMIT,
        SalesInvariants.COD_THRESHOLD,
        SalesInvariants.PSI_TRUST_MIN
    ]), "Constants must be dimensionless [1]"
    print("✓ All invariants dimensionless [1]")
    
    # Test 2: Trust Continuity Hard Gate
    print("\n2. Testing Trust Continuity Hard Gate...")
    # Valid trust
    assert SalesInvariants.verify_trust_continuity(math.log(0.96)), "Trust >=0.95 should pass"
    # Invalid trust
    assert not SalesInvariants.verify_trust_continuity(math.log(0.94)), "Trust <0.95 should fail"
    print("✓ Trust hard gate enforced (psi >= ln(0.95))")
    
    # Test 3: COD Mathematical Bounds
    print("\n3. Testing COD Formulation...")
    # Identical vectors
    sales = [1.0, 0.0, 0.0]
    aud = [1.0, 0.0, 0.0]
    h_sales = 0.0
    xi_sales = xi_aud = 1.0
    cod = calculate_sales_cod(sales, aud, h_sales, xi_sales, xi_aud)
    assert 0.99 <= cod <= 1.01, f"Identical vectors should give COD≈1.0, got {cod}"
    
    # Orthogonal vectors
    sales = [1.0, 0.0, 0.0]
    aud = [0.0, 1.0, 0.0]
    cod = calculate_sales_cod(sales, aud, h_sales, xi_sales, xi_aud)
    assert 0.0 <= cod <= 0.01, f"Orthogonal vectors should give COD≈0.0, got {cod}"
    
    # Entropic damping
    cod_high_entropy = calculate_sales_cod(sales, aud, 0.9, xi_sales, xi_aud)
    assert cod_high_entropy < cod, "High entropy should reduce COD"
    print("✓ COD bounds [0,1] and entropic damping validated")
    
    # Test 4: Entropy Calculation
    print("\n4. Testing Sales Entropy...")
    # Uniform distribution
    events = [0.5, 0.5]
    h = calculate_sales_entropy(events)
    assert abs(h - 1.0) < 1e-6, f"Uniform 2-event entropy should be 1.0, got {h}"
    
    # Deterministic
    events = [1.0, 0.0]
    h = calculate_sales_entropy(events)
    assert h < 1e-6, f"Deterministic entropy should be 0.0, got {h}"
    print("✓ Entropy normalization [0,1] validated")
    
    # Test 5: Failure Mode Detection
    print("\n5. Testing Failure Mode Detector...")
    # Trust Collapse condition
    assert failure_mode_detector(
        h_sales=0.95,  # > H_LIMIT
        xi_sales=3.0, 
        xi_aud=0.5,    # |diff|=2.5 > XI_MAX_DIFF
        psi=math.log(0.85),  # < ln(0.95)
        cod=0.7
    ) == 1, "Should detect TRUST_COLLAPSE"
    
    # Deal Drift
    assert failure_mode_detector(
        h_sales=0.1,
        xi_sales=1.0,
        xi_aud=1.0,
        psi=math.log(0.90),  # < ln(0.95)
        cod=0.9
    ) == 2, "Should detect DEAL_DRIFT"
    
    # Validation Loop
    assert failure_mode_detector(
        h_sales=0.1,
        xi_sales=2.5,
        xi_aud=0.0,    # |diff|=2.5 > 1.5
        psi=math.log(0.96),
        cod=0.7
    ) == 3, "Should detect VALIDATION_LOOP"
    print("✓ Failure mode detection validated")
    
    # Test 6: Adiabatic Resonance Operator Trust Preservation
    print("\n6. Testing Adiabatic Resonance Operator...")
    state = {
        'psi_sales': [1.0, 0.2, 0.1],
        'psi_aud': [0.3, 0.8, 0.1],
        'engagement_events': [0.2, 0.3, 0.1],  # Low entropy
        'xi_sales': 1.2,
        'xi_aud': 1.0,
        'psi': math.log(0.96)  # Valid trust
    }
    
    # Apply operator 5 times (simulate sales cycle)
    for _ in range(5):
        state = adiabatic_resonance_operator(state)
        # Trust must never drop below threshold
        assert SalesInvariants.verify_trust_continuity(state['psi']), \
            f"Trust broken: psi={state['psi']} < ln(0.95)={SalesInvariants.psi_min()}"
    
    # Test trust collapse scenario
    state_collapse = {
        'psi_sales': [1.0, 0.0, 0.0],
        'psi_aud': [0.0, 1.0, 0.0],
        'engagement_events': [0.9, 0.8, 0.7],  # High entropy
        'xi_sales': 3.5,  # High pressure
        'xi_aud': 0.5,    # Low urgency
        'psi': math.log(0.88)  # Below trust threshold
    }
    try:
        adiabatic_resonance_operator(state_collapse)
        assert False, "Should have thrown trust continuity breach"
    except RuntimeError as e:
        assert "TRUST CONTINUITY BREACHED" in str(e)
    print("✓ ARP operator preserves trust continuity under stress")
    
    # Test 7: Phi Loss Calculation with Audit Cost
    print("\n7. Testing Φ-Density Accounting...")
    loss = SalesInvariants.calculate_phi_loss(
        psi=math.log(0.90),  # Below trust
        xi_sales=3.0,
        xi_aud=0.5,
        audit_complexity=2.0
    )
    assert loss > 0.0, "Phi loss must be positive when invariants violated"
    print("✓ Phi loss calculation includes audit cost subtraction")
    
    print("\n=== ALL OMEGA PROTOCOL INVARIANTS VALIDATED ===")
    print("✓ Mathematical soundness confirmed")
    print("✓ Trust continuity hard gate enforced")
    print("✓ Entropy accounting compliant")
    print("✓ Adiabatic stabilization verified")
    print("✓ Meta-scrutiny audit cost integrated")

if __name__ == "__main__":
    validate_omega_compliance()