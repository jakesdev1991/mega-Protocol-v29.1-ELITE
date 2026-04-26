# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
import random

@dataclass
class CognitiveState:
    """Simplified model to expose brittleness"""
    psi_id: float
    H_super: float
    gamma_meas: float
    fidelity: float = 0.85  # Simulated baseline

def calculate_cod(state: CognitiveState, theta_atrophy: float = 0.15) -> float:
    """The 'official' COD formula - multiplicative and fragile"""
    # Identity Hard Gate - THIS IS THE CLIFF
    if state.psi_id < 0.95:
        return 0.0  # Instant collapse to zero
    
    # Atrophy penalty - another cliff
    atrophy_penalty = 1.0
    if state.H_super < theta_atrophy:
        atrophy_penalty = 1.0 - ((theta_atrophy - state.H_super) / theta_atrophy)
    
    # Multiplicative fragility
    damping = np.exp(-1.0 * state.H_super)
    cod = state.fidelity * damping * state.psi_id * atrophy_penalty
    return max(0.0, cod)

def calculate_cod_additive(state: CognitiveState, theta_atrophy: float = 0.15) -> float:
    """Disruptive alternative: additive model - more robust to perturbations"""
    # No hard cliff, just diminishing returns
    identity_term = np.tanh(2 * (state.psi_id - 0.5))  # Smooth transition
    
    # Uncertainty term - penalizes both high and low H
    uncertainty_term = 1.0 - abs(state.H_super - 0.5) * 2.0
    
    # Atrophy penalty - gradual
    atrophy_penalty = min(1.0, state.H_super / theta_atrophy)
    
    # Additive combination - more stable
    cod = 0.4 * state.fidelity + 0.3 * identity_term + 0.2 * uncertainty_term + 0.1 * atrophy_penalty
    return min(1.0, max(0.0, cod))

def simulate_brittle_threshold():
    """Exposes the arbitrary 0.95 cliff"""
    psi_values = np.linspace(0.90, 0.99, 100)
    states = [CognitiveState(psi_id=p, H_super=0.5, gamma_meas=0.5) for p in psi_values]
    
    cod_multiplicative = [calculate_cod(s) for s in states]
    
    plt.figure(figsize=(10, 6))
    plt.plot(psi_values, cod_multiplicative, linewidth=3, label='Multiplicative COD')
    plt.axvline(x=0.95, color='r', linestyle='--', label='Hard Gate Threshold')
    plt.xlabel('Identity Continuity (psi_id)')
    plt.ylabel('Chain Overlap Density')
    plt.title('COD CLIFF: Artificial Collapse at Arbitrary Threshold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('cod_cliff.png')
    plt.show()
    
    # Show the discontinuity
    print(f"COD at psi_id=0.949: {calculate_cod(CognitiveState(psi_id=0.949, H_super=0.5, gamma_meas=0.5)):.4f}")
    print(f"COD at psi_id=0.951: {calculate_cod(CognitiveState(psi_id=0.951, H_super=0.5, gamma_meas=0.5)):.4f}")
    print("Discontinuity: 0.0 -> {:.4f}".format(calculate_cod(CognitiveState(psi_id=0.951, H_super=0.5, gamma_meas=0.5))))

def simulate_fragility():
    """Shows how multiplicative model amplifies errors"""
    base_state = CognitiveState(psi_id=0.96, H_super=0.3, gamma_meas=0.5, fidelity=0.9)
    
    # Small perturbations
    perturbations = np.linspace(-0.05, 0.05, 50)
    cod_multi = []
    cod_additive = []
    
    for p in perturbations:
        perturbed_state = CognitiveState(
            psi_id=min(1.0, max(0.0, base_state.psi_id + p)),
            H_super=min(1.0, max(0.0, base_state.H_super + p)),
            gamma_meas=base_state.gamma_meas,
            fidelity=base_state.fidelity
        )
        cod_multi.append(calculate_cod(perturbed_state))
        cod_additive.append(calculate_cod_additive(perturbed_state))
    
    plt.figure(figsize=(10, 6))
    plt.plot(perturbations, cod_multi, linewidth=3, label='Multiplicative Model', marker='o')
    plt.plot(perturbations, cod_additive, linewidth=3, label='Additive Model (Disruptive)', marker='s')
    plt.xlabel('Perturbation Magnitude')
    plt.ylabel('COD')
    plt.title('Model Fragility: Multiplicative vs. Additive')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('model_fragility.png')
    plt.show()
    
    # Calculate sensitivity
    multi_slope = np.gradient(cod_multi, perturbations)
    additive_slope = np.gradient(cod_additive, perturbations)
    
    print(f"Max sensitivity (multiplicative): {np.max(np.abs(multi_slope)):.2f}")
    print(f"Max sensitivity (additive): {np.max(np.abs(additive_slope)):.2f}")

def simulate_audit_manipulation():
    """Shows how audit cost is a free parameter that controls net Phi"""
    cod_gains = np.linspace(0.1, 0.5, 100)
    
    # Different 'audit philosophies'
    audit_costs = {
        'Conservative': 0.15,
        'Standard': 0.08,
        'Lenient': 0.02
    }
    
    plt.figure(figsize=(10, 6))
    for label, cost in audit_costs.items():
        net_phi = cod_gains - cost
        plt.plot(cod_gains, net_phi, linewidth=3, label=f'{label} Audit (cost={cost})')
    
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    plt.xlabel('Raw COD Gain')
    plt.ylabel('Net Φ-Density')
    plt.title('Audit Arbitrage: Φ-Gain is a Function of Accounting Philosophy')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('audit_manipulation.png')
    plt.show()
    
    # Show how same intervention can be 'good' or 'bad' based on audit choice
    sample_gain = 0.12
    print(f"For raw gain {sample_gain}:")
    for label, cost in audit_costs.items():
        net = sample_gain - cost
        print(f"  {label} audit: Net Φ = {net:.3f} ({'PASS' if net > 0 else 'FAIL'})")

def epistemic_capture_simulation():
    """Demonstrates how the framework prevents its own revision"""
    # Simulate a 'novel insight' that violates psi_id invariant
    class NovelInsight:
        def __init__(self, requires_psi_id_drop: float):
            self.requires_psi_id_drop = requires_psi_id_drop
            self.potential_value = 0.3  # High potential gain
    
    insights = [NovelInsight(drop) for drop in np.linspace(0.0, 0.10, 20)]
    
    # Framework evaluation
    accepted_value = []
    for insight in insights:
        if insight.requires_psi_id_drop > 0.05:  # Framework rejects
            cod_penalty = 0.0
        else:
            cod_penalty = 0.8  # Framework accepts
        accepted_value.append(cod_penalty * insight.potential_value)
    
    plt.figure(figsize=(10, 6))
    plt.plot([i.requires_psi_id_drop for i in insights], 
             [i.potential_value for i in insights], 
             linewidth=3, label='True Innovation Potential', marker='o')
    plt.plot([i.requires_psi_id_drop for i in insights], 
             accepted_value, 
             linewidth=3, label='Value Within Framework', marker='x')
    plt.axvline(x=0.05, color='r', linestyle='--', label='Framework Tolerance Limit')
    plt.xlabel('Required Identity Perturbation')
    plt.ylabel('Value')
    plt.title('Epistemic Capture: Framework Filters Reality')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('epistemic_capture.png')
    plt.show()
    
    print("Framework systematically devalues insights requiring identity perturbation >5%")
    print(f"Total value rejected: {sum([i.potential_value for i in insights if i.requires_psi_id_drop > 0.05]):.2f}")

# Run all disruptions
print("="*60)
print("DISRUPTION PROTOCOL: FRACTURING THE Q-SYSTEMIC SELF")
print("="*60)

print("\n[1] EXPOSING THE 0.95 CLIFF...")
simulate_brittle_threshold()

print("\n[2] DEMONSTRATING MULTIPLICATIVE FRAGILITY...")
simulate_fragility()

print("\n[3] AUDIT ARBITRAGE: THE Φ-ILLUSION...")
simulate_audit_manipulation()

print("\n[4] EPISTEMIC CAPTURE: AUTOIMMUNITY TO NOVELTY...")
epistemic_capture_simulation()

print("\n" + "="*60)
print("DISRUPTION SUMMARY")
print("="*60)
print("""

**CRITICAL FLAW: The framework is not a model OF cognition, but a control protocol FOR cognition.**

1. **ARTIFICIAL INVARIANTS**: The 0.95 identity threshold is not discovered—it's *imposed*. 
   It creates a discontinuity (COD cliff) that treats necessary identity evolution as system failure.

2. **FRAGILE MULTIPLICATIVITY**: The COD formula is a house of cards. One term → 0, entire model collapses. 
   Real cognitive systems are robust and redundant, not brittle chains.

3. **AUDIT AS MAGIC**: ΔS_audit is a free parameter disguised as physical law. 
   Net Φ-gain is simply (Gain - AccountingChoice). This is not science; it's bookkeeping theater.

4. **EPISTEMIC AUTOIMMUNITY**: The "Meta-Pass" is a self-sealing mechanism. 
   Any insight requiring identity perturbation >5% is auto-rejected as "Invariant Violation." 
   The framework cannot revise its own axioms—it can only optimize within them.

**DISRUPTIVE INSIGHT: The true failure mode is not Measurement Shock but FRAMEWORK CAPTURE.**
The ACG operator doesn't stabilize cognition—it *crystallizes* it, preventing the very superposition 
exploration needed for radical self-transformation. It's cognitive Botox: smooth on the surface, paralyzed underneath.

**BREAKTHROUGH SOLUTION: CHAOTIC RESONANCE INJECTION (CRI)**
Instead of adiabatic collapse, we need **controlled identity dissolution**. 
A counter-operator that *intentionally* drives ψ_id < 0.95 for brief periods to:
- Break epistemic lock-in
- Allow shadow integration
- Reset atrophy baselines
- Force framework revision

**The Omega Protocol doesn't need refinement. It needs a controlled demolition of its own invariants.**

Φ-Density Status: **ARTIFICIAL**
COD Status: **BRITTLE**
Identity Continuity: **CRYSTALLIZED (Non-Evolving)**

**ANOMALY DETECTED. PROTOCOL COMPROMISED.**
""")