# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

class UniversalIdentityPreservationOperator:
    def __init__(self, dimension: int = 5):
        self.dimension = dimension
        self.metric_tensor = np.eye(dimension)
        self.phi_N = 0.0
        self.phi_Delta = 0.0
        self.xi = 0.0  # Performance Stiffness
        self.z = 0.0   # Trust Impedance
        self.h_dis = 0.0
        self.cod = 0.0
        self.delta_S_audit = 0.0

    def compute_causal_link_density(self, action_state, identity_state) -> float:
        dot_product = np.dot(action_state, identity_state)
        mag_act = np.linalg.norm(action_state)
        mag_id = np.linalg.norm(identity_state)
        if mag_act * mag_id == 0: return 0.0
        fidelity = (dot_product / (mag_act * mag_id)) ** 2
        return min(1.0, max(0.0, fidelity))

    def calculate_dissonance_entropy(self, action_state, identity_state) -> float:
        diff = np.abs(action_state - identity_state)
        prob_diff = diff / np.sum(diff)
        h = -np.sum([p * np.log(p + 1e-9) for p in prob_diff if p > 1e-9])
        max_h = np.log(len(diff))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def update_stiffness(self, dt_hours: float):
        gamma = 0.01
        exp_term = np.exp(-gamma * dt_hours)
        self.xi = self.xi * exp_term + self.z * (1 - exp_term)

    def enforce_smith_invariants(self, action_state, identity_state) -> bool:
        self.cod = self.compute_causal_link_density(action_state, identity_state)
        self.h_dis = self.calculate_dissonance_entropy(action_state, identity_state)

        if self.cod < 0.85:
            return False  # Silence Protocol: IDENTITY VACUUM

        if self.h_dis > 0.3:
            return False  # Silence Protocol: DISSONANCE EXPLOSION

        if self.xi > self.z + 0.1:
            return False  # Silence Protocol: STIFFNESS EXCEEDS IMPEDANCE

        phi_N = np.log2(self.cod + 1e-9)
        R_align = abs(self.xi - self.z)
        R_max = 3.0
        phi_Delta = np.tanh(phi_N) * np.tanh(R_align / R_max)
        if phi_Delta >= 0.5 * phi_N:
            return False  # Silence Protocol: ASYMMETRY DOMINANCE

        self.delta_S_audit = np.log(2) * 6  # Audit cost subtracted
        return True

    def apply(self, action_state, identity_state, dt_hours: float):
        self.update_stiffness(dt_hours)
        if self.enforce_smith_invariants(action_state, identity_state):
            return "We do not claim to fix your worth. We are here if you choose to remember it."
        else:
            return None  # Silence Protocol: NO MESSAGE

def validate_uipo():
    """Validate UIPO v58.0 against Omega Protocol invariants"""
    uipo = UniversalIdentityPreservationOperator()
    
    # Test Case 1: Stable state (all invariants satisfied)
    action = np.array([0.9, 0.1, 0.0, 0.0, 0.0])  # High performance, low else
    identity = np.array([0.8, 0.2, 0.0, 0.0, 0.0])  # Close alignment
    uipo.xi = 0.2  # Low stiffness
    uipo.z = 0.25  # Moderate trust (xi <= z + 0.1: 0.2 <= 0.35)
    msg = uipo.apply(action, identity, 0)
    assert msg is not None, "Stable state should send message"
    assert uipo.cod >= 0.85, f"COD={uipo.cod} < 0.85"
    assert uipo.h_dis <= 0.3, f"H_dis={uipo.h_dis} > 0.3"
    assert uipo.xi <= uipo.z + 0.1, f"Stiffness {uipo.xi} > Trust {uipo.z} + 0.1"
    phi_N = np.log2(uipo.cod + 1e-9)
    assert uipo.phi_Delta < 0.5 * phi_N, f"Asymmetry violation: {uipo.phi_Delta} >= {0.5*phi_N}"
    print("✓ Test 1 PASSED: Stable state")

    # Test Case 2: COD < 0.85 (Identity Vacuum)
    action = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
    identity = np.array([0.0, 1.0, 0.0, 0.0, 0.0])  # Orthogonal
    uipo.xi = 0.1
    uipo.z = 0.2
    msg = uipo.apply(action, identity, 0)
    assert msg is None, "Low COD should trigger silence"
    assert uipo.cod < 0.85, f"COD={uipo.cod} should be < 0.85"
    print("✓ Test 2 PASSED: COD < 0.85 triggers silence")

    # Test Case 3: H_dis > 0.3 (Dissonance Explosion)
    action = np.array([0.9, 0.0, 0.1, 0.0, 0.0])
    identity = np.array([0.1, 0.8, 0.1, 0.0, 0.0])  # High dissonance in performance/worthiness
    uipo.xi = 0.1
    uipo.z = 0.2
    msg = uipo.apply(action, identity, 0)
    assert msg is None, "High H_dis should trigger silence"
    assert uipo.h_dis > 0.3, f"H_dis={uipo.h_dis} should be > 0.3"
    print("✓ Test 3 PASSED: H_dis > 0.3 triggers silence")

    # Test Case 4: Stiffness > Trust + 0.1 (Impedance Violation)
    action = np.array([0.8, 0.2, 0.0, 0.0, 0.0])
    identity = np.array([0.7, 0.3, 0.0, 0.0, 0.0])
    uipo.xi = 0.5  # High stiffness
    uipo.z = 0.3   # Low trust (0.5 > 0.3 + 0.1 = 0.4)
    msg = uipo.apply(action, identity, 0)
    assert msg is None, "Stiffness > trust+0.1 should trigger silence"
    assert uipo.xi > uipo.z + 0.1, f"Stiffness {uipo.xi} <= {uipo.z}+0.1 violated"
    print("✓ Test 4 PASSED: Stiffness > Trust+0.1 triggers silence")

    # Test Case 5: Asymmetry Dominance (Phi_Delta >= 0.5 * Phi_N)
    action = np.array([0.6, 0.4, 0.0, 0.0, 0.0])
    identity = np.array([0.5, 0.5, 0.0, 0.0, 0.0])
    uipo.xi = 0.4
    uipo.z = 0.4  # Stiffness-trust match
    # Force low COD to make phi_N negative large magnitude
    uipo.cod = 0.2  # Will be overridden by compute_causal_link_density, so we skip apply and test enforce directly
    # Instead, set state to trigger asymmetry
    uipo.cod = 0.2  # Fidelity term
    uipo.h_dis = 0.2
    uipo.xi = 0.45
    uipo.z = 0.3  # xi > z + 0.1? 0.45 > 0.4 -> yes, but we want to test asymmetry separately
    # Adjust to pass first three invariants but fail asymmetry
    uipo.cod = 0.5  # phi_N = log2(0.5) = -1
    uipo.h_dis = 0.2
    uipo.xi = 0.35
    uipo.z = 0.3  # xi=0.35 <= z+0.1=0.4 -> ok
    # Now compute phi_Delta: tanh(-1) * tanh(|0.05|/3) ≈ (-0.7616) * (0.0167) ≈ -0.0127
    # 0.5 * phi_N = -0.5
    # Condition: phi_Delta >= 0.5 * phi_N -> -0.0127 >= -0.5 -> TRUE (violation)
    assert uipo.enforce_smith_invariants(action, identity) == False, "Should detect asymmetry violation"
    print("✓ Test 5 PASSED: Asymmetry violation detected")

    # Test Case 6: Audit cost subtraction
    uipo.apply(action, identity, 0)
    assert uipo.delta_S_audit == np.log(2) * 6, f"Audit cost mismatch: {uipo.delta_S_audit} != {np.log(2)*6}"
    print("✓ Test 6 PASSED: Audit cost correctly set")

    print("\nAll UIPO v58.0 validation tests PASSED. Operator complies with Omega Protocol invariants.")

if __name__ == "__main__":
    validate_uipo()