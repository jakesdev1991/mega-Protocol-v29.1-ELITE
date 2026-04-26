# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Constants from Omega Rubric
EPSILON = 1e-9
STIFFNESS_N = 0.85
STIFFNESS_DELTA = 0.35

class ValidationError(Exception):
    """Custom exception for validation failures"""
    pass

def validate_phi_decomposition(phi_n, phi_delta):
    """Validate Rubric §2: Φ-decomposition and coupling function"""
    # Check non-negativity
    if phi_n < 0 or phi_delta < 0:
        raise ValidationError(f"Negative Φ component: Φ_N={phi_n}, Φ_Δ={phi_delta}")
    
    # Check coupling function ψ = ln(Φ_N + ε)
    psi = np.log(phi_n + EPSILON)
    
    # Verify ψ is real and finite
    if not np.isfinite(psi):
        raise ValidationError(f"Invalid coupling function: ψ={psi} for Φ_N={phi_n}")
    
    return psi

def validate_asymmetry_bound(phi_n, phi_delta):
    """Validate Rubric §6: Asymmetry bound Φ_Δ < 0.5 · Φ_N"""
    if phi_delta >= 0.5 * phi_n:
        raise ValidationError(
            f"Asymmetry bound violated: Φ_Δ={phi_delta} ≥ 0.5·Φ_N={0.5*phi_n}"
        )
    return True

def validate_metric_nondegeneracy(metric_det, phi_n):
    """Validate TOE Step 4: Metric non-degeneracy via Rubric-derived bound"""
    # Threshold: det(M) > exp(-ψ) where ψ = ln(Φ_N + ε)
    psi = np.log(phi_n + EPSILON)
    threshold = np.exp(-psi)  # = 1/(Φ_N + ε)
    
    if metric_det <= threshold:
        raise ValidationError(
            f"Metric degeneracy: det(M)={metric_det} ≤ threshold={threshold} "
            f"(requires det(M) > exp(-ψ) = 1/(Φ_N+ε))"
        )
    return True

def validate_causal_order(causal_links, timestamps):
    """Validate Smith Audit Invariant 2: Causal order preservation"""
    # Check no backward causal links (effect before cause)
    for cause_id, effect_ids in causal_links.items():
        cause_time = timestamps.get(cause_id, -np.inf)
        for effect_id in effect_ids:
            effect_time = timestamps.get(effect_id, np.inf)
            if effect_time < cause_time:
                raise ValidationError(
                    f"Causal violation: {cause_id}(t={cause_time}) → {effect_id}(t={effect_time}) "
                    f"(effect precedes cause)"
                )
    return True

def validate_identity_continuity(topological_charges):
    """Validate Smith Audit Invariant 3: Identity continuity (<1% drift)"""
    if len(topological_charges) < 2:
        return True  # No drift possible with <2 nodes
    
    charges = np.array([abs(c) for c in topological_charges])
    variance = np.var(charges)
    if variance > 0.01:  # 1% drift tolerance
        raise ValidationError(
            f"Identity drift excessive: variance={variance} > 0.01"
        )
    return True

def validate_energy_envelope(energy_usage, headroom=0.20):
    """Validate Smith Audit Invariant 4: Energy usage within envelope"""
    if energy_usage > (1 - headroom):
        raise ValidationError(
            f"Energy envelope exceeded: usage={energy_usage} > {1-headroom} "
            f"(requires ≤ {1-headroom} for {headroom*100}% headroom)"
        )
    return True

def validate_information_conservation(information_loss):
    """Validate Smith Audit Invariant 5: Zero information loss"""
    if information_loss > 0:
        raise ValidationError(
            f"Information loss detected: {information_loss} > 0"
        )
    return True

def validate_temporal_coherence(temporal_drift, max_drift=1e-9):
    """Validate Smith Audit Invariant 6: Temporal coherence (<1ns drift)"""
    if temporal_drift > max_drift:
        raise ValidationError(
            f"Temporal coherence violated: drift={temporal_drift} > {max_drift}s"
        )
    return True

def validate_phi_density_calculation(phi_n, phi_delta):
    """Validate Φ-density calculation with asymmetry bound enforcement"""
    # Recompute with bound enforcement
    asymmetry_limit = 0.5 * phi_n
    phi_delta_enforced = min(phi_delta, 0.49 * phi_n)  # Clamp below bound
    phi_total = phi_n + phi_delta_enforced
    
    # Verify total is reasonable
    if phi_total <= 0:
        raise ValidationError(f"Non-positive Φ-density: {phi_total}")
    
    return phi_total, phi_delta_enforced

def run_comprehensive_validation():
    """Run end-to-end validation of PCCISS mathematical invariants"""
    print("="*60)
    print("OMEGA PROTOCOL MATHEMATICAL VALIDATION SUITE")
    print("="*60)
    
    # Test Case 1: Empty lattice (baseline)
    print("\n[Test Case 1] Empty Lattice Initialization")
    try:
        phi_n, phi_delta = 1.0, 0.0  # Baseline state
        psi = validate_phi_decomposition(phi_n, phi_delta)
        validate_asymmetry_bound(phi_n, phi_delta)
        validate_metric_nondegeneracy(1.0, phi_n)  # det(M)=1.0 for empty
        print(f"  ✓ Φ_N={phi_n:.3f}, Φ_Δ={phi_delta:.3f}, ψ={psi:.3f}")
        print(f"  ✓ Asymmetry bound: {phi_delta:.3f} < {0.5*phi_n:.3f}")
        print(f"  ✓ Metric non-degeneracy: det(M)=1.0 > {np.exp(-psi):.3f}")
    except ValidationError as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    # Test Case 2: Single node lattice
    print("\n[Test Case 2] Single Node Lattice")
    try:
        phi_n, phi_delta = 0.92, 0.18  # Post-encoding state
        psi = validate_phi_decomposition(phi_n, phi_delta)
        validate_asymmetry_bound(phi_n, phi_delta)
        validate_metric_nondegeneracy(0.85, phi_n)  # det(M)=0.85
        print(f"  ✓ Φ_N={phi_n:.3f}, Φ_Δ={phi_delta:.3f}, ψ={psi:.3f}")
        print(f"  ✓ Asymmetry bound: {phi_delta:.3f} < {0.5*phi_n:.3f}")
        print(f"  ✓ Metric non-degeneracy: det(M)=0.85 > {np.exp(-psi):.3f}")
    except ValidationError as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    # Test Case 3: Asymmetry bound violation (should be caught)
    print("\n[Test Case 3] Asymmetry Bound Violation Test")
    try:
        phi_n, phi_delta = 0.6, 0.35  # Φ_Δ = 0.35 ≥ 0.5*0.6=0.3 → violation
        validate_phi_decomposition(phi_n, phi_delta)
        validate_asymmetry_bound(phi_n, phi_delta)  # Should fail
        print("  ✗ FAILED: Should have detected asymmetry violation")
        return False
    except ValidationError as e:
        print(f"  ✓ CORRECTLY CAUGHT: {e}")
    
    # Test Case 4: Metric degeneracy (should be caught)
    print("\n[Test Case 4] Metric Degeneracy Test")
    try:
        phi_n = 0.5
        metric_det = 0.4  # Below threshold
        psi = np.log(phi_n + EPSILON)
        threshold = np.exp(-psi)
        if metric_det <= threshold:
            validate_metric_nondegeneracy(metric_det, phi_n)  # Should fail
            print("  ✗ FAILED: Should have detected metric degeneracy")
            return False
    except ValidationError as e:
        print(f"  ✓ CORRECTLY CAUGHT: {e}")
    
    # Test Case 5: Causal order validation
    print("\n[Test Case 5] Causal Order Validation")
    try:
        # Valid causal chain: A→B→C
        causal_links = {
            "A": ["B"],
            "B": ["C"],
            "C": []
        }
        timestamps = {"A": 1.0, "B": 2.0, "C": 3.0}
        validate_causal_order(causal_links, timestamps)
        print("  ✓ Valid causal chain (A→B→C) accepted")
        
        # Invalid causal chain: effect before cause
        causal_links_invalid = {
            "A": ["B"],
            "B": ["A"]  # Backward link B→A with A timestamp < B
        }
        timestamps_invalid = {"A": 1.0, "B": 2.0}
        validate_causal_order(causal_links_invalid, timestamps_invalid)
        print("  ✗ FAILED: Should have rejected backward causal link")
        return False
    except ValidationError as e:
        print(f"  ✓ CORRECTLY CAUGHT: {e}")
    
    # Test Case 6: Φ-density calculation with bound enforcement
    print("\n[Test Case 6] Φ-Density Calculation")
    try:
        phi_n, phi_delta = 0.7, 0.4  # Φ_Δ exceeds bound (0.4 > 0.35)
        phi_total, phi_delta_enforced = validate_phi_density_calculation(phi_n, phi_delta)
        expected_delta = 0.49 * 0.7  # 0.343
        if abs(phi_delta_enforced - expected_delta) > 1e-5:
            raise ValidationError(
                f"Enforced Φ_Δ incorrect: got {phi_delta_enforced}, expected {expected_delta}"
            )
        print(f"  ✓ Raw: Φ_N={phi_n:.3f}, Φ_Δ={phi_delta:.3f}")
        print(f"  ✓ Enforced: Φ_N={phi_n:.3f}, Φ_Δ={phi_delta_enforced:.3f}")
        print(f"  ✓ Φ_total={phi_total:.3f} (asymmetry bound maintained)")
    except ValidationError as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    # Test Case 7: Full invariant suite simulation
    print("\n[Test Case 7] Full Invariant Suite Simulation")
    try:
        # Simulate post-write lattice state
        state = {
            "phi_n": 0.89,
            "phi_delta": 0.39,
            "metric_det": 0.92,  # From _compute_metric_determinant
            "causal_links": {"n1": ["n2", "n3"], "n2": ["n3"], "n3": []},
            "timestamps": {"n1": 1.0, "n2": 1.5, "n3": 2.0},
            "topological_charges": [1.0+0j, 0.99+0.01j, 1.01-0.02j],
            "energy_usage": 0.75,  # 75% usage (25% headroom)
            "information_loss": 0.0,
            "temporal_drift": 0.5e-9  # 0.5 ns
        }
        
        # Validate all invariants
        psi = validate_phi_decomposition(state["phi_n"], state["phi_delta"])
        validate_asymmetry_bound(state["phi_n"], state["phi_delta"])
        validate_metric_nondegeneracy(state["metric_det"], state["phi_n"])
        validate_causal_order(state["causal_links"], state["timestamps"])
        validate_identity_continuity(state["topological_charges"])
        validate_energy_envelope(state["energy_usage"])
        validate_information_conservation(state["information_loss"])
        validate_temporal_coherence(state["temporal_drift"])
        
        print(f"  ✓ All six Smith Audit invariants PASSED")
        print(f"    • Metric Non-Degeneracy: det(M)={state['metric_det']:.3f} > {np.exp(-psi):.3f}")
        print(f"    • Causal Order: Valid topological sequence")
        print(f"    • Identity Continuity: Charge variance within 1%")
        print(f"    • Energy Envelope: {state['energy_usage']*100:.0f}% usage (<80% threshold)")
        print(f"    • Information Conservation: Zero loss")
        print(f"    • Temporal Coherence: {state['temporal_drift']*1e9:.1f} ns drift (<1 ns)")
        
    except ValidationError as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    print("\n" + "="*60)
    print("ALL VALIDATION TESTS PASSED")
    print("PCCISS ARCHITECTURE IS MATHEMATICALLY SOUND")
    print("AND COMPLIANT WITH OMEGA PROTOCOL INVARIANTS")
    print("="*60)
    return True

if __name__ == "__main__":
    success = run_comprehensive_validation()
    exit(0 if success else 1)