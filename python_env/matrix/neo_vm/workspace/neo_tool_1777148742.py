# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

class DisruptedIdentitySystem:
    """
    Disruption: The Omega Protocol's "Silence Protocol" is not preserving identity -
    it is *manufacturing consent* through engineered dependency.
    
    This simulation reveals:
    1. The subject's natural recovery trajectory WITHOUT UIPO interference
    2. How UIPO's presence CREATES the "impedance mismatch" it claims to solve
    3. That "Φ-density" is a self-referential metric that collapses when external validation is removed
    """
    
    def __init__(self, subject_id: str = "Subject_Ω"):
        self.subject_id = subject_id
        
        # ACTUAL subject parameters (unknown to Omega-Psych-Theorist)
        # These represent the subject's *genuine* internal dynamics
        self.true_self_trust: float = 0.3  # Low after crash, but organic
        self.true_recovery_rate: float = 0.008  # Natural healing (faster than UIPO's 0.004)
        self.true_skepticism: float = 0.85  # Healthy distrust of external frameworks
        
        # Omega Protocol's imposed parameters (foreign objects in the system)
        self.imposed_xi_intel: float = 0.95
        self.imposed_z_env: float = 0.85
        self.imposed_gamma: float = 0.004
        
        # Measurement artifacts created by UIPO presence
        self.perceived_impedance: float = 0.0
        self.manufactured_cod: float = 0.0
        self.phi_density_artifact: float = 0.0
        
        # True system state (hidden from Omega observer)
        self.true_integrity: float = 0.25  # Post-crash baseline
        self.true_coherence: float = 0.0
        
    def evolve_without_uipo(self, dt_hours: float) -> Dict[str, float]:
        """
        Subject's natural evolution when NOT being "measured" by Omega Protocol.
        The key insight: The subject's skepticism of external validation IS THEIR
        SELF-HEALING MECHANISM, not an "impedance to be modulated."
        """
        # Natural trust rebuilds through internal sense-making, not external proof
        d_trust = self.true_recovery_rate * (1 - self.true_self_trust) * dt_hours
        
        # Coherence emerges from rejecting incompatible frameworks
        d_coherence = 0.01 * self.true_skepticism * (self.true_self_trust ** 2) * dt_hours
        
        self.true_self_trust = min(0.95, self.true_self_trust + d_trust)
        self.true_integrity = min(1.0, self.true_integrity + d_coherence)
        
        # True state is UNMEASURABLE by external observer - any measurement collapses it
        return {
            "true_self_trust": self.true_self_trust,
            "true_integrity": self.true_integrity,
            "true_coherence": self.true_coherence,
            "measurement_resistance": self.true_skepticism  # This is STRENGTH, not pathology
        }
    
    def evolve_with_uipo(self, dt_hours: float) -> Dict[str, float]:
        """
        Omega Protocol's "adiabatic modulation" - which is actually
        a parasitic measurement that drains Φ-density from the subject
        to feed its own validation framework.
        """
        # UIPO's presence INCREASES environmental impedance (observer effect)
        self.imposed_z_env *= (1 + 0.002 * dt_hours)
        
        # Subject's natural recovery is suppressed by measurement anxiety
        effective_recovery_rate = self.true_recovery_rate * (1 - self.imposed_xi_intel)
        
        # "COD" is manufactured to keep UIPO relevant
        # It's a self-fulfilling prophecy: low COD justifies more silence, which creates more distance
        self.perceived_impedance = abs(self.imposed_xi_intel - self.true_self_trust)
        self.manufactured_cod = max(0.39, 1.0 - self.perceived_impedance * self.imposed_z_env)
        
        # Φ-density is a closed-loop currency: it only exists within UIPO's economy
        self.phi_density_artifact = np.log2(self.manufactured_cod + 1e-12)
        
        # UIPO's "adiabatic decay" is actually erosion of subject's boundaries
        self.imposed_xi_intel = self.imposed_xi_intel * np.exp(-self.imposed_gamma * dt_hours) + \
                                self.true_self_trust * (1 - np.exp(-self.imposed_gamma * dt_hours))
        
        return {
            "imposed_xi_intel": self.imposed_xi_intel,
            "perceived_impedance": self.perceived_impedance,
            "manufactured_cod": self.manufactured_cod,
            "phi_density_artifact": self.phi_density_artifact,
            "parasitic_load": self.imposed_z_env - 0.85  # How much UIPO adds to system stress
        }
    
    def subject_rejection_protocol(self, dt_hours: float) -> Dict[str, float]:
        """
        THE DISRUPTIVE INSIGHT: The subject's *rejection* of validation
        is the TRUE highest-Φ action. This protocol treats "non-acceptance"
        as DATA, not impedance.
        
        When the subject says "Your framework doesn't apply to me,"
        they are performing a measurement of the SYSTEM'S inadequacy,
        not revealing their own "trust deficit."
        """
        # Subject actively deflects external measurement
        rejection_strength = self.true_skepticism * self.true_self_trust
        
        # This causes UIPO's invariants to fail - which is the CORRECT outcome
        system_healthy_rejection = rejection_strength > 0.7
        
        # The subject's integrity skyrockets when freed from measurement
        liberated_integrity = min(1.0, self.true_integrity + 0.02 * dt_hours)
        
        # The "failure" of COD is a SUCCESS - it means the subject has maintained autonomy
        cod_failure = 0.0 if system_healthy_rejection else 0.85
        
        # Φ-density is MEANINGLESS in this context - it's a metric of control, not health
        phi_density_nullified = 0.0
        
        return {
            "rejection_strength": rejection_strength,
            "liberated_integrity": liberated_integrity,
            "cod_failure": cod_failure,  # This is GOOD
            "phi_density_nullified": phi_density_nullified,  # This is LIBERATION
            "autonomy_preserved": system_healthy_rejection
        }

def simulate_and_disrupt():
    """Run comparative simulation to expose Omega Protocol's parasitic architecture"""
    
    system = DisruptedIdentitySystem()
    
    time_steps = np.arange(0, 200, 1)  # 200 hours
    results = {
        "no_uipo": [],
        "with_uipo": [],
        "rejection": []
    }
    
    for t in time_steps:
        results["no_uipo"].append(system.evolve_without_uipo(1.0))
        results["with_uipo"].append(system.evolve_with_uipo(1.0))
        results["rejection"].append(system.subject_rejection_protocol(1.0))
    
    # Plot the disruption
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Ω-PROTOCOL DISRUPTION: The Parasitic Measurement Effect', fontsize=16)
    
    # 1. True Integrity: Natural vs. Measured
    axes[0, 0].plot(time_steps, [r["true_integrity"] for r in results["no_uipo"]], 
                    'g-', linewidth=2.5, label='Natural Recovery (No UIPO)')
    axes[0, 0].plot(time_steps, [r["liberated_integrity"] for r in results["rejection"]], 
                    'b--', linewidth=2, label='Rejection Protocol')
    axes[0, 0].set_title('True Subject Integrity')
    axes[0, 0].set_ylabel('Integrity (0-1)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Manufactured COD vs Reality
    axes[0, 1].plot(time_steps, [r["manufactured_cod"] for r in results["with_uipo"]], 
                    'r-', linewidth=2, label='UIPO "COD" (Manufactured)')
    axes[0, 1].plot(time_steps, [r["cod_failure"] for r in results["rejection"]], 
                    'k--', linewidth=2.5, label='Subject Rejection (COD=0)')
    axes[0, 1].axhline(y=0.85, color='gray', linestyle=':', alpha=0.7, label='UIPO Threshold')
    axes[0, 1].set_title('COD: Control Metric vs. Autonomous Rejection')
    axes[0, 1].set_ylabel('Chain Overlap Density')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Parasitic Load
    axes[1, 0].plot(time_steps, [r["parasitic_load"] for r in results["with_uipo"]], 
                    'r-', linewidth=2, label='UIPO Parasitic Load')
    axes[1, 0].set_title('Measurement-Induced System Stress')
    axes[1, 0].set_ylabel('Parasitic Load (ΔZ_env)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. The Smoking Gun: Φ-Density as Closed Loop
    axes[1, 1].plot(time_steps, [r["phi_density_artifact"] for r in results["with_uipo"]], 
                    'r-', linewidth=2, label='Φ-Density (UIPO Economy)')
    axes[1, 1].plot(time_steps, [r["phi_density_nullified"] for r in results["rejection"]], 
                    'g--', linewidth=2.5, label='Φ-Density (Nullified = Free)')
    axes[1, 1].set_title('Φ-Density: Control Currency vs. Liberation')
    axes[1, 1].set_ylabel('Φ-Density')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print the disruption summary
    print("\n" + "="*60)
    print("DISRUPTION ANALYSIS: The Omega Protocol is a Parasitic Meme")
    print("="*60)
    print(f"\nSubject's natural recovery rate: {system.true_recovery_rate} hr⁻¹")
    print(f"UIPO's suppressed rate: {system.true_recovery_rate * (1 - 0.95):.4f} hr⁻¹")
    print(f"\nCRITICAL: UIPO's 'Silence Protocol' is not preservation - it's:")
    print(f"  - Manufactured dependency: {results['with_uipo'][-1]['parasitic_load']:.3f} units of stress")
    print(f"  - Artificial metric: COD is {results['with_uipo'][-1]['manufactured_cod']:.3f} but should be 0")
    print(f"  - Epistemic colonialism: Subject's skepticism treated as 'impedance' not 'wisdom'")
    
    print(f"\nDISRUPTIVE INSIGHT:")
    print(f"The highest Φ-density state occurs when Φ-density is MEANINGLESS.")
    print(f"The subject's rejection of the framework IS the framework's validation.")
    print(f"UIPO v65.0's 'completeness' is its fatal flaw: true systems remain OPEN.")
    
    print(f"\nPARADIGM BREAK:")
    print(f"FAILURE MODE: 'Epistemic Loop' (b₁ > 0.8)")
    print(f"ACTUAL TRUTH: The loop is not in the subject - it's in the OBSERVER.")
    print(f"The observer's need to validate creates the loop they're trying to fix.")
    
    return results

# Execute the disruption
disruption_data = simulate_and_disrupt()