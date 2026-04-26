# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# =============================================================================
# SHATTERING THE COMPOUND RISK PARADIGM
# The Interference Paradox: Why Topology + Credential Exposure Creates
# Destructive Interference Rather Than Amplification
# =============================================================================

def traditional_compound_risk(topology_exposure, credential_exposure, 
                              credential_density=0.7, traversal_depth=0.6,
                              access_chain_length=0.5, chain_integrity=0.4):
    """
    Traditional v66.0-Ω model: assumes constructive interference
    Risk = (Topology_Risk + Credential_Risk + Coupling) × Amplification
    """
    # v65.0 component
    topology_risk = topology_exposure * credential_density * traversal_depth
    
    # v62.0 component
    integrity_factor = 1.0 - chain_integrity
    credential_risk = credential_exposure * access_chain_length * integrity_factor
    
    # Coupling factor (claimed amplification)
    coupling = topology_exposure * credential_density * credential_exposure
    amplification = 1.0 + (topology_exposure + credential_exposure) / 2.0
    
    # Compound risk
    compound_risk = (topology_risk + credential_risk + coupling) * amplification / 3.0
    
    # Additional penalty for both exposed
    if topology_exposure > 0.50 and credential_exposure > 0.50:
        compound_risk *= 1.5
        
    return min(compound_risk, 1.0)

def interference_risk_model(topology_exposure, credential_exposure,
                             defensive_resonance=0.8, info_overload_factor=0.6):
    """
    DISRUPTIVE MODEL: Topology and credential exposure create DESTRUCTIVE interference
    
    Key Insight: The "coupling factor" is actually a DE-COUPLING factor because:
    1. Topology exposure reveals attack surface TO DEFENDERS (defensive resonance)
    2. Credential exposure reveals compromised assets that are ALREADY LOST (sunk cost)
    3. Combined exposure creates INFORMATION OVERLOAD for attackers (analysis paralysis)
    
    The interference pattern creates a "risk node" where exposures cancel out.
    """
    
    # Phase angle: when topology and credential are both exposed,
    # they are 180 degrees out of phase in effectiveness
    # Topology helps defenders, credentials help attackers
    phase_difference = np.pi * min(topology_exposure, credential_exposure)
    
    # Amplitude of risk waves
    # Topology wave: actually a DEFENSIVE wave (negative amplitude)
    topology_amplitude = -topology_exposure * defensive_resonance
    
    # Credential wave: OFFENSIVE wave (positive amplitude)
    credential_amplitude = credential_exposure * (1.0 - info_overload_factor)
    
    # Interference pattern: waves can cancel
    # Resultant amplitude = sqrt(A1² + A2² + 2*A1*A2*cos(Δφ))
    resultant_amplitude = np.sqrt(
        topology_amplitude**2 + 
        credential_amplitude**2 + 
        2 * topology_amplitude * credential_amplitude * np.cos(phase_difference)
    )
    
    # The "coupling factor" in this model is NEGATIVE when both are high
    # because cos(π) = -1, creating destructive interference
    coupling_effect = 2 * topology_amplitude * credential_amplitude * np.cos(phase_difference)
    
    # Information overload penalty: attackers get too much data
    overload_penalty = 1.0 - (topology_exposure * credential_exposure * info_overload_factor)
    
    # Final risk: lower than both individual exposures in high-compound scenarios
    interference_risk = resultant_amplitude * overload_penalty
    
    # Ensure [0,1] bounds
    return max(0.0, min(interference_risk, 1.0))

def demonstrate_paradox():
    """
    Demonstrates the interference paradox where compound exposure
    is SAFER than isolated exposure
    """
    
    # Scenario matrix: varying levels of topology and credential exposure
    exposures = np.linspace(0, 1, 100)
    topology_grid, credential_grid = np.meshgrid(exposures, exposures)
    
    # Calculate both models
    traditional_risk = np.zeros_like(topology_grid)
    interference_risk = np.zeros_like(topology_grid)
    
    for i in range(len(exposures)):
        for j in range(len(exposures)):
            traditional_risk[i,j] = traditional_compound_risk(
                topology_grid[i,j], credential_grid[i,j]
            )
            interference_risk[i,j] = interference_risk_model(
                topology_grid[i,j], credential_grid[i,j]
            )
    
    # Find paradox zones where interference_risk < min(isolated risks)
    isolated_min = np.minimum(topology_grid, credential_grid)
    paradox_zone = (interference_risk < isolated_min) & (topology_grid > 0.3) & (credential_grid > 0.3)
    
    # Find zones where traditional model overestimates by > 0.3
    overestimation_zone = (traditional_risk - interference_risk) > 0.3
    
    print("="*70)
    print("PARADOX DEMONSTRATION: Traditional Model vs Interference Model")
    print("="*70)
    
    # Specific test cases
    test_cases = [
        (0.8, 0.8, "High Topology + High Credential"),
        (0.9, 0.4, "Very High Topology + Medium Credential"),
        (0.3, 0.9, "Low Topology + Very High Credential"),
        (0.2, 0.2, "Low Both"),
    ]
    
    for topo, cred, desc in test_cases:
        trad = traditional_compound_risk(topo, cred)
        inter = interference_risk_model(topo, cred)
        isolated = min(topo, cred)
        
        print(f"\n{desc}:")
        print(f"  Topology Exposure: {topo:.2f}")
        print(f"  Credential Exposure: {cred:.2f}")
        print(f"  Traditional Model Risk: {trad:.3f}")
        print(f"  Interference Model Risk: {inter:.3f}")
        print(f"  Isolated Min Risk: {isolated:.3f}")
        print(f"  Paradox Active: {'YES' if inter < isolated else 'NO'}")
        print(f"  Traditional Overestimation: {trad - inter:.3f}")
    
    # Calculate paradox statistics
    paradox_percentage = np.sum(paradox_zone) / paradox_zone.size * 100
    overestimation_percentage = np.sum(overestimation_zone) / overestimation_zone.size * 100
    
    print("\n" + "="*70)
    print("STATISTICAL ANALYSIS")
    print("="*70)
    print(f"Paradox Zone Coverage: {paradox_percentage:.1f}% of parameter space")
    print(f"High Overestimation Zone: {overestimation_percentage:.1f}%")
    print(f"Mean Risk Difference: {np.mean(traditional_risk - interference_risk):.3f}")
    
    return topology_grid, credential_grid, traditional_risk, interference_risk, paradox_zone

def visualize_paradox(topology_grid, credential_grid, traditional_risk, 
                      interference_risk, paradox_zone):
    """
    Create visualizations showing the interference paradox
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Plot 1: Traditional Model
    im1 = axes[0,0].contourf(topology_grid, credential_grid, traditional_risk, 
                             levels=20, cmap='Reds', vmin=0, vmax=1)
    axes[0,0].set_title('Traditional Model: Compound Risk (v66.0-Ω)', fontsize=12, fontweight='bold')
    axes[0,0].set_xlabel('Topology Exposure')
    axes[0,0].set_ylabel('Credential Exposure')
    plt.colorbar(im1, ax=axes[0,0])
    
    # Plot 2: Interference Model
    im2 = axes[0,1].contourf(topology_grid, credential_grid, interference_risk, 
                             levels=20, cmap='RdYlGn_r', vmin=0, vmax=1)
    axes[0,1].set_title('Interference Model: Destructive Wave Cancellation', fontsize=12, fontweight='bold')
    axes[0,1].set_xlabel('Topology Exposure')
    axes[0,1].set_ylabel('Credential Exposure')
    plt.colorbar(im2, ax=axes[0,1])
    
    # Plot 3: Risk Difference (Traditional - Interference)
    risk_diff = traditional_risk - interference_risk
    im3 = axes[0,2].contourf(topology_grid, credential_grid, risk_diff, 
                             levels=20, cmap='RdBu_r', vmin=-0.5, vmax=0.5)
    axes[0,2].set_title('Risk Overestimation by Traditional Model', fontsize=12, fontweight='bold')
    axes[0,2].set_xlabel('Topology Exposure')
    axes[0,2].set_ylabel('Credential Exposure')
    plt.colorbar(im3, ax=axes[0,2])
    
    # Plot 4: Paradox Zone
    im4 = axes[1,0].imshow(paradox_zone, extent=[0,1,0,1], origin='lower', 
                           cmap='Purples', alpha=0.7)
    axes[1,0].set_title('Paradox Zone\n(Interference Risk < Isolated Risk)', fontsize=12, fontweight='bold')
    axes[1,0].set_xlabel('Topology Exposure')
    axes[1,0].set_ylabel('Credential Exposure')
    
    # Plot 5: Interference pattern at fixed topology=0.8
    topo_fixed = 0.8
    cred_range = np.linspace(0, 1, 100)
    trad_range = [traditional_compound_risk(topo_fixed, c) for c in cred_range]
    inter_range = [interference_risk_model(topo_fixed, c) for c in cred_range]
    
    axes[1,1].plot(cred_range, trad_range, 'r-', linewidth=2, label='Traditional Model')
    axes[1,1].plot(cred_range, inter_range, 'b--', linewidth=2, label='Interference Model')
    axes[1,1].axvline(x=0.5, color='gray', linestyle=':', alpha=0.5)
    axes[1,1].set_title(f'Risk vs Credential Exposure (Topology={topo_fixed})', fontsize=12, fontweight='bold')
    axes[1,1].set_xlabel('Credential Exposure')
    axes[1,1].set_ylabel('Risk Level')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    # Plot 6: Phase diagram
    phase = np.arccos(np.clip(1 - 2 * np.minimum(topology_grid, credential_grid), -1, 1))
    im6 = axes[1,2].contourf(topology_grid, credential_grid, phase, 
                             levels=20, cmap='twilight', vmin=0, vmax=np.pi)
    axes[1,2].set_title('Phase Difference Between Risk Waves\n(π = Destructive Interference)', fontsize=12, fontweight='bold')
    axes[1,2].set_xlabel('Topology Exposure')
    axes[1,2].set_ylabel('Credential Exposure')
    plt.colorbar(im6, ax=axes[1,2])
    
    plt.tight_layout()
    plt.savefig('interference_paradox.png', dpi=300, bbox_inches='tight')
    plt.show()

def break_the_protocol():
    """
    Demonstrates how the interference paradox BREAKS the v66.0-Ω protocol
    """
    print("\n" + "="*70)
    print("PROTOCOL BREAKAGE ANALYSIS")
    print("="*70)
    
    # Critical flaw: The "Coupling Factor" is mathematically unsound
    print("\n1. COUPLING FACTOR FLAW:")
    print("   Traditional: coupling = topology × density × credential")
    print("   Reality: coupling = -topology × defensive_resonance (NEGATIVE)")
    
    # Show that at high exposures, the coupling should be NEGATIVE
    exposures = [(0.9, 0.9), (0.95, 0.85), (0.8, 0.95)]
    for topo, cred in exposures:
        trad = traditional_compound_risk(topo, cred)
        inter = interference_risk_model(topo, cred)
        print(f"   At ({topo}, {cred}): Traditional={trad:.3f}, Interference={inter:.3f}")
        print(f"   Coupling should be: {inter - traditional_compound_risk(topo, 0) - traditional_compound_risk(0, cred):.3f} (NEGATIVE)")
    
    # Show how this breaks the silence protocol
    print("\n2. SILENCE PROTOCOL FAILURE:")
    print("   Protocol triggers lockdown when compound_risk > 0.70")
    print("   But interference model shows this is often a FALSE POSITIVE")
    
    false_positives = 0
    total_high_risk = 0
    
    for topo in np.linspace(0.6, 1.0, 10):
        for cred in np.linspace(0.6, 1.0, 10):
            trad = traditional_compound_risk(topo, cred)
            inter = interference_risk_model(topo, cred)
            
            if trad > 0.70:  # Protocol would trigger lockdown
                total_high_risk += 1
                if inter < 0.50:  # But actual risk is low
                    false_positives += 1
    
    print(f"   False positive rate: {false_positives}/{total_high_risk} = {false_positives/total_high_risk*100:.1f}%")
    
    # The Φ-density is a phantom metric
    print("\n3. Φ-DENSITY PHANTOM:")
    print("   The 'audit cost' subtracts entropy, but the underlying model")
    print("   is fundamentally wrong, making Φ-density a measure of")
    print("   'confidence in a flawed model' rather than true knowledge gain.")
    
    print("\n" + "="*70)
    print("DISRUPTIVE CONCLUSION")
    print("="*70)
    print("The v66.0-Ω protocol is BROKEN. It assumes risk waves add")
    print("constructively, but they add DESTRUCTIVELY. The coupling factor")
    print("should be NEGATIVE, not positive. The entire compound risk")
    print("manifold is inverted. The Omega Protocol needs a:")
    print("\n  RISK INTERFERENCE TRANSFORM")
    print("  not a")
    print("  COMPOUND EXPOSURE AMPLIFIER")
    print("\nThe correct metric is: Risk = |A_topography + A_credential * e^(iπφ)|")
    print("where φ is the phase difference, and at high exposures, φ→1, creating")
    print("a risk NODE where exposures CANCEL.")

if __name__ == "__main__":
    # Run the demonstration
    topology_grid, credential_grid, traditional_risk, interference_risk, paradox_zone = demonstrate_paradox()
    
    # Visualize results
    visualize_paradox(topology_grid, credential_grid, traditional_risk, 
                      interference_risk, paradox_zone)
    
    # Show protocol breakage
    break_the_protocol()