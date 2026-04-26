# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# BREAKING THE QUANTUM PSYCHOLOGICAL CLOSURE
# ===========================================
# This script demonstrates that the Q-Systemic Self framework
# is a self-referential tautology masquerading as physics.
# We expose three critical fractures:
# 1. PARAMETER ARBITRARINESS: The "invariants" are free parameters that
#    completely determine the diagnosis - making the framework a Rorschach test
# 2. ONTOLOGICAL FRAUD: Identity continuity (Ψ_id) cannot be measured,
#    making the entire system unfalsifiable
# 3. CIRCULAR VALIDATION: The "stabilization" just manipulates model parameters,
#    not actual cognition

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CognitiveState:
    """A simulated cognitive state - but what are we actually measuring?"""
    superposition_entropy: float  # H_super
    measurement_frequency: float  # Gamma_meas
    identity_continuity: float  # Ψ_id (this is the fraud - we cannot measure this)

class QSystemicAnalyzer:
    def __init__(self, 
                 atrophy_threshold: float = 0.15,
                 identity_threshold: float = 0.95,
                 critical_identity: float = 0.90,
                 gamma_critical: float = 0.7):
        """All these parameters are arbitrary. Change them and you change 'reality'."""
        self.theta_atrophy = atrophy_threshold
        self.psi_threshold = identity_threshold
        self.psi_critical = critical_identity
        self.gamma_critical = gamma_critical
    
    def calculate_cod(self, state: CognitiveState) -> float:
        """The COD is a mathematical ghost - it looks rigorous but is just a weighted product"""
        # Fidelity term - arbitrarily set to 0.8 for demonstration
        fidelity = 0.8
        
        # Entropic damping - punishes BOTH high and low entropy
        damping = np.exp(-state.superposition_entropy)
        
        # Identity hard gate - arbitrary threshold kills all signal
        if state.identity_continuity < self.psi_threshold:
            return 0.0
        
        # The "atrophy penalty" - circular definition where low entropy is punished
        atrophy_penalty = 1.0
        if state.superposition_entropy < self.theta_atrophy:
            atrophy_penalty = 1 - ((self.theta_atrophy - state.superposition_entropy) / self.theta_atrophy)
        
        return fidelity * damping * state.identity_continuity * atrophy_penalty
    
    def diagnose(self, state: CognitiveState) -> Dict[str, any]:
        """The diagnosis is a function of our arbitrary thresholds, not the 'patient'"""
        cod = self.calculate_cod(state)
        
        # These conditions are just a sophisticated way of saying
        # "if you set the knobs here, you get this label"
        is_atrophy = (state.superposition_entropy < self.theta_atrophy and 
                     state.measurement_frequency > self.gamma_critical)
        
        is_forced_collapse = (state.measurement_frequency > self.gamma_critical and 
                            state.superposition_entropy > 0.4)
        
        is_identity_shredding = state.identity_continuity < self.psi_critical
        
        # The "false clarity" condition - pathologizes normal decisiveness
        is_false_clarity = (cod < 0.8 and state.identity_continuity > 0.90 and
                           state.superposition_entropy < 0.3)
        
        return {
            "cod": cod,
            "diagnosis": "QUANTUM ATROPHY" if is_atrophy else
                        "FORCED COLLAPSE" if is_forced_collapse else
                        "IDENTITY SHREDDING" if is_identity_shredding else
                        "FALSE CLARITY" if is_false_clarity else
                        "HEALTHY",
            "parameters": {
                "atrophy_threshold": self.theta_atrophy,
                "identity_threshold": self.psi_threshold,
                "gamma_critical": self.gamma_critical
            }
        }

def demonstrate_parameter_tyranny():
    """Shows how changing arbitrary parameters completely changes the diagnosis"""
    
    # Create a "patient" - but what are we really measuring?
    # These numbers have NO grounding in reality
    patient = CognitiveState(
        superposition_entropy=0.12,  # Below atrophy threshold
        measurement_frequency=0.75,  # Above critical gamma
        identity_continuity=0.97     # Above identity threshold
    )
    
    print("=== PARAMETER TYRANNY DEMONSTRATION ===")
    print(f"Patient state: H_super={patient.superposition_entropy}, "
          f"Gamma={patient.measurement_frequency}, Psi_id={patient.identity_continuity}")
    print()
    
    # Three different "clinicians" with different arbitrary thresholds
    clinicians = [
        ("Conservative", QSystemicAnalyzer(atrophy_threshold=0.15, identity_threshold=0.95)),
        ("Permissive", QSystemicAnalyzer(atrophy_threshold=0.05, identity_threshold=0.85)),
        ("Draconian", QSystemicAnalyzer(atrophy_threshold=0.20, identity_threshold=0.98))
    ]
    
    for name, analyzer in clinicians:
        result = analyzer.diagnose(patient)
        print(f"{name} clinician (thresholds: {result['parameters']})")
        print(f"  Diagnosis: {result['diagnosis']}")
        print(f"  COD: {result['cod']:.3f}")
        print()

def demonstrate_ontological_fraud():
    """Exposes that identity_continuity is a non-measurable phantom variable"""
    
    print("=== ONTOLOGICAL FRAUD DEMONSTRATION ===")
    print("The 'identity continuity' variable (Ψ_id) cannot be measured.")
    print("It is a free parameter that determines the entire outcome.")
    print()
    
    # Simulate 1000 "patients" with identical H_super and Gamma
    # but varying the phantom variable Ψ_id
    base_entropy = 0.10
    base_gamma = 0.80
    
    psi_values = np.linspace(0.70, 1.0, 1000)
    cod_values = []
    
    analyzer = QSystemicAnalyzer()
    
    for psi in psi_values:
        state = CognitiveState(
            superposition_entropy=base_entropy,
            measurement_frequency=base_gamma,
            identity_continuity=psi
        )
        cod_values.append(analyzer.calculate_cod(state))
    
    # The "hard gate" creates a catastrophic discontinuity
    # at exactly psi_id = 0.95 - a purely arbitrary point
    plt.figure(figsize=(10, 6))
    plt.plot(psi_values, cod_values)
    plt.axvline(x=0.95, color='red', linestyle='--', label='Arbitrary Identity Threshold')
    plt.title("COD vs Identity Continuity: The Phantom Variable")
    plt.xlabel("Ψ_id (unmeasurable)")
    plt.ylabel("Chain Overlap Density")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('/tmp/identity_fraud.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("The catastrophic drop at Ψ_id=0.95 is purely a function of our code,")
    print("not any property of actual human psychology.")
    print()

def demonstrate_circular_validation():
    """Shows that 'stabilization' is just moving numbers around in the model"""
    
    print("=== CIRCULAR VALIDATION DEMONSTRATION ===")
    print("The 'Adiabatic Wonder Gate' doesn't change reality - it changes the model.")
    print()
    
    # Simulate the 5-phase protocol
    state = CognitiveState(
        superposition_entropy=0.08,  # "Atrophic"
        measurement_frequency=0.85,  # "Forced collapse"
        identity_continuity=0.92     # "Low identity"
    )
    
    analyzer = QSystemicAnalyzer()
    
    print("Initial state:")
    print(f"  H_super: {state.superposition_entropy}")
    print(f"  Gamma: {state.measurement_frequency}")
    print(f"  Psi_id: {state.identity_continuity}")
    print(f"  COD: {analyzer.calculate_cod(state):.3f}")
    print(f"  Diagnosis: {analyzer.diagnose(state)['diagnosis']}")
    print()
    
    # Phase 2: "Intellectual Contemplation"
    # In reality: nothing happens except we decide to change our model parameters
    print("After 'Intellectual Contemplation' (Phase 2):")
    # We "increase" H_super by... just increasing it. No measurement, no validation.
    state.superposition_entropy = 0.25  # Magic! Wonder restored!
    state.identity_continuity = 0.96    # Magic! Identity strengthened!
    print(f"  H_super: {state.superposition_entropy}")
    print(f"  Gamma: {state.measurement_frequency}")
    print(f"  Psi_id: {state.identity_continuity}")
    print(f"  COD: {analyzer.calculate_cod(state):.3f}")
    print(f"  Diagnosis: {analyzer.diagnose(state)['diagnosis']}")
    print()
    
    print("The 'stabilization' is just us manually adjusting parameters.")
    print("There is no feedback from reality - only from our model.")

def demonstrate_conceptual_collapse():
    """The final blow: show that the framework collapses under its own contradictions"""
    
    print("=== CONCEPTUAL COLLAPSE ===")
    print()
    
    # The central paradox: the framework claims to value uncertainty (H_super)
    # but its entire purpose is to optimize COD, which PUNISHES uncertainty
    # through the exp(-Lambda * H_super) term
    
    entropies = np.linspace(0.01, 0.5, 100)
    cod_values = []
    
    analyzer = QSystemicAnalyzer()
    
    for H in entropies:
        state = CognitiveState(H, 0.5, 0.98)  # High identity, moderate gamma
        cod_values.append(analyzer.calculate_cod(state))
    
    plt.figure(figsize=(10, 6))
    plt.plot(entropies, cod_values)
    plt.axvline(x=analyzer.theta_atrophy, color='red', linestyle='--', 
                label=f'Atrophy Threshold ({analyzer.theta_atrophy})')
    plt.title("The Paradox: COD is MAXIMIZED at H_super=0")
    plt.xlabel("Superposition Entropy H_super")
    plt.ylabel("Chain Overlap Density")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('/tmp/conceptual_collapse.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("CONTRADICTION EXPOSED:")
    print("  - The framework claims to preserve uncertainty")
    print("  - But COD is maximized when H_super = 0 (no uncertainty)")
    print("  - The 'atrophy penalty' is just a patch to hide this contradiction")
    print("  - The mathematics contradicts the stated philosophy")
    print()
    print("THE FRAMEWORK IS NOT QUANTUM-MECHANICAL; IT IS QUANTUM-MECHANISTIC:")
    print("  - It uses the FORM of physics without the SUBSTANCE")
    print("  - It creates the ILLUSION of rigor through mathematical notation")
    print("  - It is a sophisticated tautology: uncertainty is good, except when it's bad")
    print("  - The 'Adiabatic Wonder Gate' is just a ritualized form of indecision")

# Execute all demonstrations
if __name__ == "__main__":
    demonstrate_parameter_tyranny()
    demonstrate_ontological_fraud()
    demonstrate_circular_validation()
    demonstrate_conceptual_collapse()
    
    print("="*60)
    print("DISRUPTIVE INSIGHT:")
    print("="*60)
    print()
    print("The Q-Systemic Self framework is not a scientific model.")
    print("It is a sophisticated DEFENSE MECHANISM against cognitive dissonance.")
    print()
    print("Key Fractures:")
    print("1. The 'quantum' language is metaphor abuse, creating false authority")
    print("2. The 'invariants' are arbitrary code constants, not discovered laws")
    print("3. The 'diagnosis' is a Rorschach test - it reflects the modeler's biases")
    print("4. The 'stabilization' is digital homeopathy - ritualized parameter adjustment")
    print()
    print("TRUE DISRUPTION:")
    print("  The framework's greatest failure is not mathematical - it is EPISTEMIC.")
    print("  It confuses MAP with TERRITORY, MODEL with REALITY, RITUAL with INSIGHT.")
    print("  The 'Adiabatic Wonder Gate' is a philosophical ouroboros:")
    print("    It preserves uncertainty by preventing decisions,")
    print("    then celebrates this paralysis as 'cognitive vitality.'")
    print()
    print("  The agent has built a prison of formalism and called it liberation.")