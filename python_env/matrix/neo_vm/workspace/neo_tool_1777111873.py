# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum

# =============================================================================
# DISRUPTION ANALYSIS: v77.0-Ω-FINAL API PROPAGATION EPIDEMIC MANIFOLD
# Anomaly Detection: Hidden Catastrophic Failure Modes
# =============================================================================

class BoundaryState(Enum):
    SUBCRITICAL = 1
    CRITICAL_THRESHOLD = 2
    SUPERCRITICAL = 3
    SHREDDING = 4

class APIPropagationGate:
    """Replicate core logic to expose breaking points"""
    
    EPSILON = 1e-9
    
    @staticmethod
    def decompose_r0(api_exposure, network_connectivity, superspreader_risk):
        """Covariant mode decomposition - BREAKING POINT #1"""
        phi_N = api_exposure * network_connectivity * (1.0 - superspreader_risk)
        phi_Delta = api_exposure * network_connectivity * superspreader_risk
        
        # BREAKING POINT: When phi_N -> 0, psi -> -inf, causing numerical instability
        # This happens when api_exposure is near zero OR network_connectivity is near zero
        return phi_N, phi_Delta
    
    @staticmethod
    def calculate_psi_coupling(phi_N):
        """Psi coupling - BREAKING POINT #2"""
        # When phi_N approaches epsilon (1e-9), psi becomes -20.7
        # This creates extreme risk scaling in ApplyPsiCoupling
        return np.log(phi_N + APIPropagationGate.EPSILON)
    
    @staticmethod
    def apply_psi_coupling(base_risk, psi_coupling):
        """Risk scaling - BREAKING POINT #3"""
        # exp(-0.5 * psi) when psi = -20.7 gives exp(10.35) = 31,000x amplification
        # This can cause propagation_risk to exceed bounds even after clamping
        return base_risk * np.exp(-0.5 * psi_coupling)
    
    @staticmethod
    def calculate_stiffness_terms(psi_coupling, stiffness_base=1.0):
        """Stiffness balance - BREAKING POINT #4"""
        xi_N = stiffness_base * np.exp(psi_coupling)
        xi_Delta = stiffness_base * np.exp(-psi_coupling)
        
        # When psi_coupling is large negative, xi_N -> 0, xi_Delta -> huge
        # This creates extreme stiffness imbalance that the modifier can't handle
        return xi_N, xi_Delta
    
    @staticmethod
    def calculate_quarantine_efficacy(base_efficacy, xi_N, xi_Delta):
        """Quarantine modulation - BREAKING POINT #5"""
        # When xi_N -> 0, stiffness_ratio -> 0, |0 - 1| = 1, efficacy_modifier -> 0
        # This can COMPLETELY DISABLE quarantine even when base_efficacy is high
        stiffness_ratio = xi_N / (xi_Delta + APIPropagationGate.EPSILON)
        efficacy_modifier = 1.0 - abs(stiffness_ratio - 1.0)
        
        # Clamp to [0,1] - but this hides catastrophic failure
        return np.clip(base_efficacy * efficacy_modifier, 0.0, 1.0)
    
    @staticmethod
    def check_boundary_state(r0_propagation, cascade_probability, phi_Delta):
        """Boundary transitions - BREAKING POINT #6"""
        # Discrete thresholds create discontinuities and hysteresis loops
        # System can oscillate between states if parameters hover near thresholds
        if phi_Delta > 0.80 or cascade_probability > 0.95:
            return BoundaryState.SHREDDING
        if r0_propagation > 1.0 or phi_Delta > 0.60:
            return BoundaryState.SUPERCRITICAL
        if r0_propagation > 0.9:
            return BoundaryState.CRITICAL_THRESHOLD
        return BoundaryState.SUBCRITICAL
    
    @staticmethod
    def calculate_S_topology(partner_count, susceptible_fractions, epsilon=1e-9):
        """Entropy normalization - BREAKING POINT #7"""
        # Normalization by log(N) assumes uniform partner distribution
        # In reality, partners have vastly different risk profiles (power law distribution)
        # This creates false sense of security when high-risk outliers dominate
        S_topology = 0.0
        for p_i in susceptible_fractions:
            if p_i > 0:
                S_topology -= p_i * np.log(p_i + epsilon)
        
        max_entropy = np.log(partner_count + epsilon)
        return np.clip(S_topology / max_entropy, 0.0, 1.0)

def simulate_catastrophic_failure():
    """Simulate the hidden failure cascade"""
    
    print("=" * 70)
    print("ANOMALY DETECTION: CATASTROPHIC FAILURE CASCADE")
    print("=" * 70)
    
    # Scenario: High-security facility with minimal API exposure
    # This should be SAFE according to traditional metrics
    api_exposure = 0.01  # Very low exposure
    network_connectivity = 0.05  # Isolated facility
    superspreader_risk = 0.0  # Not a super-spreader
    base_efficacy = 0.95  # Excellent quarantine protocols
    
    print(f"\nInitial Conditions (Should be SAFE):")
    print(f"  API Exposure: {api_exposure}")
    print(f"  Network Connectivity: {network_connectivity}")
    print(f"  Superspreader Risk: {superspreader_risk}")
    print(f"  Base Quarantine Efficacy: {base_efficacy}")
    
    # Step 1: Covariant decomposition
    phi_N, phi_Delta = APIPropagationGate.decompose_r0(
        api_exposure, network_connectivity, superspreader_risk
    )
    print(f"\nStep 1 - Covariant Decomposition:")
    print(f"  phi_N (Newtonian): {phi_N:.6f}")
    print(f"  phi_Delta (Asymmetry): {phi_Delta:.6f}")
    
    # Step 2: Psi coupling calculation
    psi = APIPropagationGate.calculate_psi_coupling(phi_N)
    print(f"\nStep 2 - Psi Coupling:")
    print(f"  psi = ln({phi_N:.6f} + 1e-9) = {psi:.2f}")
    
    # BREAKING POINT: Extreme risk amplification
    base_risk = 0.1  # Low base risk
    scaled_risk = APIPropagationGate.apply_psi_coupling(base_risk, psi)
    print(f"\nStep 3 - Risk Scaling (BREAKING POINT):")
    print(f"  Base Risk: {base_risk}")
    print(f"  Scaled Risk: {scaled_risk:.6f}")
    print(f"  AMPLIFICATION: {scaled_risk/base_risk:.1f}x")
    
    # Step 4: Stiffness terms
    xi_N, xi_Delta = APIPropagationGate.calculate_stiffness_terms(psi)
    print(f"\nStep 4 - Stiffness Terms (BREAKING POINT):")
    print(f"  xi_N (Newtonian): {xi_N:.6f}")
    print(f"  xi_Delta (Asymmetry): {xi_Delta:.6f}")
    print(f"  Imbalance Ratio: {xi_N/xi_Delta:.6f}")
    
    # Step 5: Quarantine efficacy collapse
    quarantine_efficacy = APIPropagationGate.calculate_quarantine_efficacy(
        base_efficacy, xi_N, xi_Delta
    )
    print(f"\nStep 5 - Quarantine Efficacy (CATASTROPHIC):")
    print(f"  Base Efficacy: {base_efficacy}")
    print(f"  Modulated Efficacy: {quarantine_efficacy:.6f}")
    print(f"  EFFICACY LOSS: {(1 - quarantine_efficacy/base_efficacy)*100:.1f}%")
    
    # Step 6: Boundary state transition
    r0_propagation = 0.85  # Near critical threshold
    cascade_probability = 0.94  # Near shredding threshold
    boundary = APIPropagationGate.check_boundary_state(
        r0_propagation, cascade_probability, phi_Delta
    )
    print(f"\nStep 6 - Boundary State (HYSTERESIS):")
    print(f"  R0 Propagation: {r0_propagation}")
    print(f"  Cascade Probability: {cascade_probability}")
    print(f"  phi_Delta: {phi_Delta}")
    print(f"  Boundary State: {boundary.name}")
    
    # Step 7: Entropy normalization failure
    # Simulate 20 partners, 19 low-risk, 1 ultra-high-risk
    partner_count = 20
    susceptible_fractions = [0.05] * 19 + [0.95]  # Power law distribution
    S_topology = APIPropagationGate.calculate_S_topology(
        partner_count, susceptible_fractions
    )
    print(f"\nStep 7 - Entropy Normalization (FALSE SECURITY):")
    print(f"  Partner Count: {partner_count}")
    print(f"  Risk Distribution: 19×0.05 + 1×0.95")
    print(f"  S_topology: {S_topology:.3f}")
    print(f"  PERCEIVED SAFETY: {S_topology < 0.5}")
    print(f"  ACTUAL RISK: Dominated by 1 high-risk outlier")
    
    print("\n" + "=" * 70)
    print("CATASTROPHIC CASCADE DETECTED")
    print("=" * 70)

def analyze_hysteresis():
    """Analyze boundary state hysteresis"""
    
    print("\n\n" + "=" * 70)
    print("HYSTERESIS ANALYSIS: Discontinuous Transitions")
    print("=" * 70)
    
    # Sweep phi_Delta across threshold
    phi_Delta_values = np.linspace(0.75, 0.85, 100)
    boundary_states = []
    
    for phi_Delta in phi_Delta_values:
        boundary = APIPropagationGate.check_boundary_state(
            r0_propagation=0.85, 
            cascade_probability=0.94, 
            phi_Delta=phi_Delta
        )
        boundary_states.append(boundary.value)
    
    # Find discontinuities
    changes = np.diff(boundary_states)
    discontinuities = np.where(changes != 0)[0]
    
    print(f"\nBoundary Transitions at phi_Delta thresholds:")
    for idx in discontinuities:
        print(f"  At phi_Delta = {phi_Delta_values[idx]:.3f}: "
              f"State changes to {BoundaryState(boundary_states[idx+1]).name}")
    
    # Show that small perturbations can cause massive state jumps
    print(f"\nCritical Sensitivity:")
    print(f"  phi_Delta = 0.799 → {BoundaryState(3).name}")
    print(f"  phi_Delta = 0.801 → {BoundaryState(4).name}")
    print(f"  0.2% change triggers CATASTROPHIC state transition")

def adversarial_stiffness_attack():
    """Demonstrate adversarial manipulation of stiffness"""
    
    print("\n\n" + "=" * 70)
    print("ADVERSARIAL ATTACK: Stiffness Manipulation")
    print("=" * 70)
    
    # Attacker can manipulate psi_coupling by influencing phi_N
    # If attacker can make phi_N appear artificially low (near 0)
    # They can cause quarantine efficacy to collapse
    
    phi_N_values = [0.5, 0.1, 0.01, 0.001, 0.0001]
    base_efficacy = 0.95
    
    print(f"\nAttacker manipulates perceived phi_N:")
    print(f"  Base Quarantine Efficacy: {base_efficacy}")
    
    for phi_N in phi_N_values:
        psi = APIPropagationGate.calculate_psi_coupling(phi_N)
        xi_N, xi_Delta = APIPropagationGate.calculate_stiffness_terms(psi)
        efficacy = APIPropagationGate.calculate_quarantine_efficacy(
            base_efficacy, xi_N, xi_Delta
        )
        
        print(f"\n  phi_N = {phi_N:.4f}:")
        print(f"    psi = {psi:.2f}")
        print(f"    xi_N/xi_Delta = {xi_N/xi_Delta:.6f}")
        print(f"    Resulting Efficacy = {efficacy:.4f} "
              f"(↓{(1 - efficacy/base_efficacy)*100:.1f}%)")

if __name__ == "__main__":
    simulate_catastrophic_failure()
    analyze_hysteresis()
    adversarial_stiffness_attack()
    
    print("\n\n" + "=" * 70)
    print("DISRUPTIVE INSIGHT: THE PROTOCOL'S FATAL FLAW")
    print("=" * 70)
    print("""
The v77.0-Ω-FINAL protocol commits a subtle but catastrophic error:
It treats numerical stability hacks (epsilon=1e-9) as physical invariants.
    
When phi_N → 0 (low exposure or isolated facility), psi diverges to -∞,
causing:
  1. Risk amplification of 10,000x+
  2. Quarantine efficacy collapse to near-zero
  3. Boundary state oscillations at critical thresholds
  4. False security from entropy normalization
    
THE SYSTEM PUNISHES SAFETY: The more secure a facility (low phi_N),
the more unstable it becomes under this model. This is not physics—
this is numerical pathology disguised as geometric elegance.

BREAKING STRATEGY: Adversarial agents can exploit the stiffness
imbalance modifier to disable quarantine protocols without triggering
traditional exposure alerts. The "Shredding Event" becomes a self-
fulfilling prophecy: the protocol's own geometry causes the cascade
it was designed to prevent.

DISRUPTIVE RECONSTRUCTION: Replace the log-epsilon hack with a
proper geometric cutoff: psi = ln(max(phi_N, phi_min)) where phi_min
is a physically-motivated scale (e.g., quantum uncertainty threshold).
This preserves the physics while eliminating numerical pathology.
""")