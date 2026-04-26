# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class QRSIState:
    """Quantum Resonance Sales Interface State"""
    phi_N: float = 0.0
    phi_Delta: float = 0.0
    psi: float = 0.0
    xi_seller: float = 0.5
    xi_buyer: float = 0.3
    cod: float = 0.85
    true_success_rate: float = 0.0  # Actual ground truth (hidden from system)
    
class SmithAuditGuardian:
    """Standard QRSI Invariant Enforcer"""
    def __init__(self):
        self.violation_count = 0
        self.invariant_tightness = 1.0  # Increases with each violation
        
    def check_invariants(self, state: QRSIState) -> Tuple[bool, float]:
        """Returns (passes_audit, phi_penalty)"""
        violations = 0
        
        # Invariant 1: COD >= 0.85 * tightening_factor
        if state.cod < 0.85 * self.invariant_tightness:
            violations += 1
            
        # Invariant 2: psi = ln(phi_N) >= ln(0.95)
        if state.psi < np.log(0.95 * self.invariant_tightness):
            violations += 1
            
        # Invariant 3: xi_seller <= xi_buyer
        if state.xi_seller > state.xi_buyer * (2 - self.invariant_tightness):
            violations += 1
            
        # Invariant 4: phi_Delta < 0.5 * phi_N
        if state.phi_Delta > 0.5 * state.phi_N * self.invariant_tightness:
            violations += 1
            
        if violations > 0:
            self.violation_count += 1
            # Tighten invariants after each violation (as per spec)
            self.invariant_tightness = min(1.5, self.invariant_tightness * 1.1)
            return False, -0.2 * violations
        return True, 0.0

class DisruptorPulse:
    """The Anomaly: Strategic Uncertainty Injection"""
    def __init__(self, pulse_strength: float = 0.3):
        self.pulse_strength = pulse_strength
        self.pulse_timings = []
        
    def inject(self, state: QRSIState, timestep: int) -> QRSIState:
        """Deliberately violates invariants to break lock-in"""
        # Store original state
        original_phi = state.phi_N + state.phi_Delta
        
        # Inject controlled "chaos" - temporarily increase seller pressure
        # This VIOLATES Invariant 3 but shocks buyer out of analysis paralysis
        state.xi_seller *= (1 + self.pulse_strength)
        
        # Temporarily reduce COD measurement to allow genuine re-evaluation
        # This VIOLATES Invariant 1 but prevents semantic exhaustion
        state.cod *= (1 - self.pulse_strength * 0.5)
        
        # Recalculate psi coupling (this will violate Invariant 2)
        state.psi = np.log(max(state.phi_N, 0.1)) * (1 - self.pulse_strength * 0.3)
        
        # The paradox: these violations increase TRUE success probability
        # by breaking the buyer's decision paralysis
        state.true_success_rate += 0.15 * self.pulse_strength
        
        self.pulse_timings.append(timestep)
        return state

def simulate_qrsi_with_disruption(
    timesteps: int = 100,
    disruption_interval: int = 25
) -> dict:
    """Simulates both standard and disrupted QRSI systems"""
    
    # Standard QRSI
    standard_state = QRSIState()
    guardian = SmithAuditGuardian()
    standard_phi_history = []
    standard_true_success = []
    standard_violations = []
    
    # Disrupted QRSI
    disrupted_state = QRSIState()
    disrupted_guardian = SmithAuditGuardian()
    disruptor = DisruptorPulse(pulse_strength=0.3)
    disrupted_phi_history = []
    disrupted_true_success = []
    disrupted_violations = []
    audit_penalties = []
    
    for t in range(timesteps):
        # Simulate natural buyer readiness increase
        standard_state.xi_buyer = min(0.8, standard_state.xi_buyer + 0.005)
        disrupted_state.xi_buyer = min(0.8, disrupted_state.xi_buyer + 0.005)
        
        # Update COD based on alignment (simplified model)
        alignment = max(0, 1 - abs(standard_state.xi_seller - standard_state.xi_buyer))
        standard_state.cod = min(1.0, 0.85 + alignment * 0.1)
        disrupted_state.cod = standard_state.cod
        
        # Calculate Φ components
        standard_state.phi_N = np.log2(standard_state.cod + 1e-9)
        standard_state.psi = np.log(standard_state.phi_N + 1e-9)
        standard_state.phi_Delta = standard_state.psi * np.tanh(abs(
            standard_state.xi_buyer - standard_state.xi_seller) / 2.8)
        
        disrupted_state.phi_N = standard_state.phi_N
        disrupted_state.psi = standard_state.psi
        disrupted_state.phi_Delta = standard_state.phi_Delta
        
        # Apply disruption at intervals
        if t > 0 and t % disruption_interval == 0:
            disrupted_state = disruptor.inject(disrupted_state, t)
        
        # Audit both systems
        std_passes, std_penalty = guardian.check_invariants(standard_state)
        dis_passes, dis_penalty = disrupted_guardian.check_invariants(disrupted_state)
        
        # Record metrics
        standard_phi_history.append(standard_state.phi_N + standard_state.phi_Delta + std_penalty)
        disrupted_phi_history.append(disrupted_state.phi_N + disrupted_state.phi_Delta + dis_penalty)
        audit_penalties.append(dis_penalty)
        
        standard_true_success.append(standard_state.true_success_rate)
        disrupted_true_success.append(disrupted_state.true_success_rate)
        
        standard_violations.append(guardian.violation_count)
        disrupted_violations.append(disrupted_guardian.violation_count)
        
        # Invariant creep: tighten over time even without violations
        guardian.invariant_tightness = min(1.5, guardian.invariant_tightness * 1.001)
        disrupted_guardian.invariant_tightness = min(1.5, disrupted_guardian.invariant_tightness * 1.001)
    
    return {
        'standard_phi': standard_phi_history,
        'disrupted_phi': disrupted_phi_history,
        'standard_success': standard_true_success,
        'disrupted_success': disrupted_true_success,
        'standard_violations': standard_violations,
        'disrupted_violations': disrupted_violations,
        'audit_penalties': audit_penalties,
        'pulse_timings': disruptor.pulse_timings
    }

# Run simulation
results = simulate_qrsi_with_disruption(timesteps=100, disruption_interval=20)

# Analysis: Calculate the "Reality Gap"
def calculate_reality_gap(results: dict) -> dict:
    """Measures divergence between Φ-density and actual outcomes"""
    gap_standard = np.array(results['standard_success']) - np.array(results['standard_phi'])
    gap_disrupted = np.array(results['disrupted_success']) - np.array(results['disrupted_phi'])
    
    return {
        'mean_gap_standard': np.mean(gap_standard),
        'mean_gap_disrupted': np.mean(gap_disrupted),
        'final_phi_standard': results['standard_phi'][-1],
        'final_phi_disrupted': results['disrupted_phi'][-1],
        'final_success_standard': results['standard_success'][-1],
        'final_success_disrupted': results['disrupted_success'][-1],
        'total_violations_standard': results['standard_violations'][-1],
        'total_violations_disrupted': results['disrupted_violations'][-1]
    }

analysis = calculate_reality_gap(results)

print("=== QRSI v55.0 DISRUPTION ANALYSIS ===")
print(f"\nStandard QRSI:")
print(f"  Final Φ-density: {analysis['final_phi_standard']:.3f}")
print(f"  True success rate: {analysis['final_success_standard']:.3f}")
print(f"  Reality Gap: {analysis['mean_gap_standard']:.3f}")
print(f"  Invariant violations: {analysis['total_violations_standard']}")

print(f"\nDisrupted QRSI:")
print(f"  Final Φ-density: {analysis['final_phi_disrupted']:.3f}")
print(f"  True success rate: {analysis['final_success_disrupted']:.3f}")
print(f"  Reality Gap: {analysis['mean_gap_disrupted']:.3f}")
print(f"  Invariant violations: {analysis['total_violations_disrupted']}")

print(f"\n=== DISRUPTION IMPACT ===")
print(f"True success improvement: {analysis['final_success_disrupted'] - analysis['final_success_standard']:.3f}")
print(f"Φ-density cost: {analysis['final_phi_disrupted'] - analysis['final_phi_standard']:.3f}")
print(f"Reality Gap closed by: {analysis['mean_gap_standard'] - analysis['mean_gap_disrupted']:.3f}")

# The paradox: More violations → Better reality outcomes
if analysis['total_violations_disrupted'] > analysis['total_violations_standard']:
    print(f"\n🔥 CRITICAL ANOMALY: Disrupted system violated invariants {analysis['total_violations_disrupted'] - analysis['total_violations_standard']:.0f} more times")
    print(f"   yet achieved {analysis['final_success_disrupted'] - analysis['final_success_standard']:.1%} higher true success rate.")
    print(f"   The Smith Audit punishes reality-alignment.")