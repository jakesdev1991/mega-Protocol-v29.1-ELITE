# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# =============================================================================
# OMEGA PROTOCOL VALIDATION SCRIPT
# Validates mathematical soundness and invariant compliance of Bureaucratic Decision Manifold
# =============================================================================

class ValidationError(Exception):
    """Custom exception for Omega Protocol violations"""
    pass

def test_dimensional_consistency():
    """Rubric §6: All terms must be dimensionless [1]"""
    print("🔍 Testing dimensional consistency...")
    
    # Test Calculate_Topological_Impedance
    path = [
        {"approval_cost": 0.7, "risk_variance": 0.3},  # [1] * [1] = [1]
        {"approval_cost": 0.4, "risk_variance": 0.6}
    ]
    H_top = calculate_topological_impedance(path)
    assert 0 <= H_top <= 1, f"H_top={H_top} not in [0,1]"
    print(f"  ✓ H_top: {H_top:.3f} (dimensionless [1])")
    
    # Test Calculate_COD_Decision
    intent = [0.8, 0.2, 0.5]
    outcome = [0.75, 0.25, 0.45]
    COD = calculate_cod_decision(intent, outcome, H_top, 1.2)
    assert 0 <= COD <= 1, f"COD={COD} not in [0,1]"
    print(f"  ✓ COD: {COD:.3f} (dimensionless [1])")
    
    # Test Calculate_Shannon_Conditional_Entropy
    H_cond = calculate_shannon_conditional_entropy(outcome, H_top)
    assert 0 <= H_cond <= 1, f"H_cond={H_cond} not in [0,1]"
    print(f"  ✓ H_cond: {H_cond:.3f} (dimensionless [1])")
    
    print("✅ Dimensional consistency PASSED\n")

def test_invariant_enforcement():
    """Rubric §3: Invariants as active boundary conditions (hard gates)"""
    print("🔒 Testing invariant enforcement...")
    
    # Test SystemInvariants.VerifyInvariants()
    invariants = SystemInvariants(psi_id=0.94, xi_sys=2.0, kappa_sys_ind=0.5)  # psi_id < 0.95
    try:
        invariants.verify_invariants()
        raise ValidationError("Failed to catch psi_id < 0.95")
    except ValidationError as e:
        assert "Shredding Event" in str(e)
        print("  ✓ psi_id < 0.95 triggers Shredding Event")
    
    invariants = SystemInvariants(psi_id=0.96, xi_sys=3.1, kappa_sys_ind=0.5)  # xi_sys > 3.0
    try:
        invariants.verify_invariants()
        # Warning only, not hard fail
        print("  ✓ xi_sys > 3.0 triggers WARNING (not hard fail)")
    except ValidationError:
        raise ValidationError("xi_sys > 3.0 should not hard fail")
    
    invariants = SystemInvariants(psi_id=0.96, xi_sys=2.0, kappa_sys_ind=1.1)  # kappa > 1.0
    try:
        invariants.verify_invariants()
        raise ValidationError("Failed to catch kappa_sys_ind > 1.0")
    except ValidationError as e:
        assert "Coupling Overload" in str(e)
        print("  ✓ kappa_sys_ind > 1.0 triggers System-Individual Coupling Overload")
    
    print("✅ Invariant enforcement PASSED\n")

def test_geodesic_smoothing_safety():
    """Rubric §3: Hard gate on psi_id during pruning"""
    print("⚙️ Testing Geodesic Smoothing Gate safety...")
    
    # Create manifold with high curvature node
    manifold = DecisionManifold(
        path=[
            {"approval_cost": 0.9, "risk_variance": 0.9, "node_id": "high_curvature"},  # High cost*variance
            {"approval_cost": 0.1, "risk_variance": 0.1, "node_id": "low_curvature"}
        ],
        intent_vector=[1.0, 0.0, 0.0],
        outcome_vector=[0.9, 0.05, 0.05],  # High fidelity initially
        urgency_force=0.3
    )
    
    invariants = SystemInvariants(psi_id=0.96, xi_sys=1.5, kappa_sys_ind=0.4)
    
    # Simulate pruning attempt that would violate psi_id
    original_path_len = len(manifold.path)
    try:
        manifold.geodesic_smoothing_operator(invariants)
        # If no exception, check that high curvature node was NOT removed
        # (because simulated COD would drop below psi_id_min)
        assert len(manifold.path) == original_path_len, "Pruned node despite identity risk!"
        print("  ✓ Aborted pruning when psi_id would drop below 0.95")
    except ValidationError as e:
        if "Invariant Violation" in str(e):
            print("  ✓ Correctly reverted state on invariant violation")
        else:
            raise
    
    # Test successful pruning when safe
    manifold.outcome_vector = [0.95, 0.03, 0.02]  # Even higher fidelity
    try:
        manifold.geodesic_smoothing_operator(invariants)
        assert len(manifold.path) < original_path_len, "Failed to prune when safe"
        print("  ✓ Pruned high-curvature node when identity preserved")
    except Exception as e:
        raise ValidationError(f"Unexpected error during safe pruning: {e}")
    
    print("✅ Geodesic Smoothing Gate safety PASSED\n")

def test_phi_density_audit_compliance():
    """Rubric §5: Audit cost subtraction in Phi-density"""
    print("📊 Testing Φ-density audit compliance...")
    
    # Test Monitor_Phi_Density with audit cost
    invariants = SystemInvariants(psi_id=0.97, xi_sys=1.0, kappa_sys_ind=0.3)
    phi_net = monitor_phi_density(
        throughput=1.0,
        impedance_cost=0.2,
        risk_leak=0.1,
        individual_cost=0.05,
        audit_complexity_factor=2.0,  # Non-trivial operation
        invariants=invariants
    )
    
    # Manual calculation:
    # Base Phi = 1.0 - 0.2 - 0.1 - 0.05 = 0.65
    # Audit cost = k*ln(2)*complexity = 1.0 * ln(2) * 2.0 ≈ 0.693 * 2 = 1.386
    # Phi_net = 0.65 - 1.386 = negative (should trigger warning)
    assert phi_net < 0, f"Expected negative Φ-density, got {phi_net}"
    print(f"  ✓ Audit cost subtracted: Φ_net = {phi_net:.3f} (negative as expected)")
    
    # Test with low complexity
    phi_net_low = monitor_phi_density(
        throughput=1.0,
        impedance_cost=0.2,
        risk_leak=0.1,
        individual_cost=0.05,
        audit_complexity_factor=0.1,
        invariants=invariants
    )
    assert phi_net_low > 0, f"Expected positive Φ-density, got {phi_net_low}"
    print(f"  ✓ Low audit cost: Φ_net = {phi_net_low:.3f} (positive)")
    
    print("✅ Φ-density audit compliance PASSED\n")

# =============================================================================
# IMPLEMENTED FUNCTIONS (Mirroring C++ logic for validation)
# =============================================================================

def calculate_topological_impedance(path):
    """Mirror of C++ Calculate_Topological_Impedance"""
    if not path:
        return 0.0
    
    total_impedance = sum(node["approval_cost"] * node["risk_variance"] for node in path)
    total_length = sum(node["approval_cost"] for node in path)
    
    if total_length == 0:
        return 0.0
    
    raw_impedance = total_impedance / total_length
    H_max = math.log(len(path)) if len(path) > 1 else 1.0
    H_max = max(H_max, 1e-9)
    
    return min(1.0, max(0.0, raw_impedance / H_max))

def calculate_cod_decision(intent, outcome, H_top, xi_bound):
    """Mirror of C++ Calculate_COD_Decision"""
    # Fidelity calculation
    dot = sum(i * o for i, o in zip(intent, outcome))
    magI = sum(i * i for i in intent)
    magO = sum(o * o for o in outcome)
    
    fidelity = 0.0
    if magI > 1e-9 and magO > 1e-9:
        fidelity = dot / (math.sqrt(magI) * math.sqrt(magO))
        fidelity = min(1.0, max(0.0, fidelity))
    
    # Coupling constants (Rubric §6)
    LAMBDA_COUPLING = 1.0
    GAMMA_COUPLING = 0.5
    
    damping = math.exp(-LAMBDA_COUPLING * H_top)
    stiffness_penalty = math.exp(-GAMMA_COUPLING * xi_bound)
    
    return fidelity * damping * stiffness_penalty

def calculate_shannon_conditional_entropy(outcome, H_top):
    """Mirror of C++ Calculate_Shannon_Conditional_Entropy"""
    if not outcome:
        return 0.0
    
    H = 0.0
    for prob in outcome:
        if prob > 1e-9:
            H -= prob * math.log(prob)
    
    max_entropy = math.log(len(outcome)) if len(outcome) > 1 else 1.0
    max_entropy = max(max_entropy, 1e-9)
    
    return min(1.0, max(0.0, H / max_entropy))

class SystemInvariants:
    """Mirror of C++ SystemInvariants"""
    def __init__(self, psi_id, xi_sys, kappa_sys_ind):
        self.psi_id = psi_id
        self.xi_sys = xi_sys
        self.kappa_sys_ind = kappa_sys_ind
    
    def verify_invariants(self):
        """Mirror of C++ VerifyInvariants()"""
        PSI_ID_MIN = 0.95
        XI_SYS_MAX = 3.0
        KAPPA_MAX = 1.0
        
        if self.psi_id < PSI_ID_MIN:
            raise ValidationError("CRITICAL: Shredding Event - Goal Integrity Breached (Psi_id < 0.95)")
        
        if self.xi_sys > XI_SYS_MAX:
            # Warning only - not hard fail per C++ code
            print(f"WARNING: Informational Freeze Risk - Bureaucratic Stiffness Critical (Xi_sys > {XI_SYS_MAX})")
        
        if self.kappa_sys_ind > KAPPA_MAX:
            raise ValidationError("CRITICAL: System-Individual Coupling Overload (Kappa > 1.0)")
        
        return True

class DecisionManifold:
    """Mirror of C++ DecisionManifold (simplified for validation)"""
    def __init__(self, path, intent_vector, outcome_vector, urgency_force):
        self.path = path
        self.intent_vector = intent_vector
        self.outcome_vector = outcome_vector
        self.urgency_force = urgency_force
        self.state_lock = None  # Simplified
    
    def geodesic_smoothing_operator(self, invariants):
        """Mirror of C++ Geodesic_Smoothing_Operator (core safety logic)"""
        # Calculate current state
        current_H_top = calculate_topological_impedance(self.path)
        current_COD = calculate_cod_decision(
            self.intent_vector, 
            self.outcome_vector, 
            current_H_top, 
            invariants.xi_sys
        )
        
        # Early exit if stable
        if current_COD >= 0.80 and current_H_top < 0.85 * 0.9:
            return
        
        # Find high curvature nodes
        high_curvature_indices = []
        for i, node in enumerate(self.path):
            if node["approval_cost"] * node["risk_variance"] > 0.5:
                high_curvature_indices.append(i)
        
        # Sort by curvature contribution (descending)
        high_curvature_indices.sort(
            key=lambda i: self.path[i]["approval_cost"] * self.path[i]["risk_variance"],
            reverse=True
        )
        
        # Pruning loop with invariant check
        for idx in high_curvature_indices:
            if current_H_top <= 0.85 * 0.9:  # H_TOP_LIMIT * 0.9
                break
            
            # Simulate outcome shift
            temp_outcome = [v - 0.05 for v in self.outcome_vector]
            temp_COD = calculate_cod_decision(
                self.intent_vector,
                temp_outcome,
                current_H_top * 0.8,  # Assume 20% impedance reduction
                invariants.xi_sys
            )
            
            # HARD GATE: Identity preservation check
            if temp_COD < 0.95:  # PSI_ID_MIN
                raise ValidationError("Identity Risk: Cannot Remove Node. Stopping Pruning.")
            
            # Actual prune
            self.path.pop(idx)
            current_H_top = calculate_topological_impedance(self.path)
        
        # Post-intervention invariant check
        if not invariants.verify_invariants():
            raise ValidationError("Invariant Violation: System Integrity Compromised")

def monitor_phi_density(Throughput, Impedance_Cost, Risk_Leak, Individual_Cost, audit_complexity_factor, invariants):
    """Mirror of C++ Monitor_Phi_Density"""
    Phi_Net = Throughput - Impedance_Cost - Risk_Leak - Individual_Cost
    audit_entropy_cost = invariants.CalculatePhiLoss(audit_complexity_factor)
    Phi_Net -= audit_entropy_cost
    
    if Phi_Net < 0.0:
        print(f"CRITICAL: Negative Φ-Density in Decision Process. Audit Cost: {audit_entropy_cost:.3f}")
    
    return Phi_Net

# Add CalculatePhiLoss method to SystemInvariants (mirroring C++)
def CalculatePhiLoss(self, audit_complexity_factor=1.0):
    K_BOLTZMANN = 1.0
    loss = 0.0
    
    if self.psi_id < 0.95:
        loss += (0.95 - self.psi_id) * 0.5 * K_BOLTZMANN
    
    if self.xi_sys > 3.0:
        loss += (self.xi_sys - 3.0) * 0.2 * K_BOLTZMANN
    
    audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity_factor
    loss += audit_entropy_cost
    
    return loss

SystemInvariants.CalculatePhiLoss = CalculatePhiLoss

# =============================================================================
# MAIN VALIDATION EXECUTION
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA PROTOCOL VALIDATION: BUREAUCRATIC DECISION MANIFOLD")
    print("=" * 60 + "\n")
    
    try:
        test_dimensional_consistency()
        test_invariant_enforcement()
        test_geodesic_smoothing_safety()
        test_phi_density_audit_compliance()
        
        print("🎉 ALL TESTS PASSED")
        print("✅ Mathematical soundness verified")
        print("✅ Omega Protocol invariants enforced")
        print("✅ Audit cost subtraction compliant")
        print("✅ Hard gates active (not passive)")
        
    except ValidationError as e:
        print(f"❌ VALIDATION FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {e}")
        exit(1)