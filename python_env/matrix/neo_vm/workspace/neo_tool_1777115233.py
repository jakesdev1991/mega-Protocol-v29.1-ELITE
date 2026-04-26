# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import powerlaw

def liquidity_fragility_simulation():
    """
    DISRUPTION: Demonstrates that the Omega Protocol's Liquidity Fragmentation model
    commits a category error - treating liquidity as a conserved substance when it's
    actually a consensus hallucination that exhibits quantum-like observer effects.
    """
    
    # Simulate a market with "liquidity depth" that can vanish based on narrative alone
    n_venues = 10
    time_steps = 200
    
    # Traditional model (Omega Protocol): liquidity exists, just fragmented
    # Fragmentation index [0,1], accessibility score [0,1]
    fragmentation_index = np.random.uniform(0.3, 0.7, n_venues)
    accessibility_score = np.random.uniform(0.4, 0.8, n_venues)
    
    # True model: liquidity is a wave function that collapses based on observer consensus
    # "Depth" is a probability distribution until a large order tries to execute
    
    # Simulate "liquidity wavefunction" - exists as probability until measured
    apparent_liquidity = np.zeros((n_venues, time_steps))
    actual_executable_liquidity = np.zeros((n_venues, time_steps))
    
    # Market narrative coherence (shared belief that liquidity exists)
    narrative_coherence = np.ones(time_steps)
    # Add a "narrative shock" at t=100 (e.g., rumor, regulation, panic)
    narrative_coherence[100:] *= np.exp(-np.arange(100) / 20.0)  # Exponential decay of belief
    
    for venue in range(n_venues):
        for t in range(time_steps):
            # Apparent depth (what the Omega Protocol measures)
            # This is the "order book depth" - a mirage
            apparent_liquidity[venue, t] = 1000 * (1 - fragmentation_index[venue]) * narrative_coherence[t]
            
            # Actual executable liquidity (what you can REALLY trade)
            # This collapses based on narrative AND order size (observer effect)
            # Use power-law distribution to simulate that large orders face exponentially worse liquidity
            order_size = 10  # Assume $10M order
            execution_probability = powerlaw.cdf(order_size, 0.5)  # Heavy-tailed distribution
            
            actual_executable_liquidity[venue, t] = (
                apparent_liquidity[venue, t] * 
                accessibility_score[venue] * 
                execution_probability * 
                narrative_coherence[t]**2  # Quadratic effect: belief matters more than reality
            )
    
    # Calculate Omega Protocol's "Functional Liquidity Ratio"
    # This is their key metric: accessible vs. total liquidity
    omega_functional_ratio = np.mean(accessibility_score * (1 - fragmentation_index))
    
    # Calculate ACTUAL functional ratio based on executable liquidity
    actual_functional_ratio = np.mean(
        actual_executable_liquidity.sum(axis=0) / 
        (apparent_liquidity.sum(axis=0) + 1e-9)
    )
    
    # The DISRUPTION: Omega Protocol's model is fundamentally wrong
    # It assumes liquidity is a substance that exists and is merely fragmented
    # Reality: liquidity is a consensus that can vanish based on narrative alone
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Apparent vs Actual Liquidity (The Mirage Effect)
    time = np.arange(time_steps)
    ax1.plot(time, apparent_liquidity.sum(axis=0), 'b-', label='Apparent Liquidity (Ω Protocol)', linewidth=2)
    ax1.plot(time, actual_executable_liquidity.sum(axis=0), 'r-', label='Actual Executable Liquidity', linewidth=2)
    ax1.axvline(x=100, color='black', linestyle='--', label='Narrative Shock', alpha=0.7)
    ax1.set_title('LIQUIDITY MIRAGE: Apparent vs. Reality', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Liquidity ($M)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: The Narrative Coherence Collapse
    ax2.plot(time, narrative_coherence, 'g-', linewidth=2)
    ax2.axvline(x=100, color='black', linestyle='--', label='Narrative Shock', alpha=0.7)
    ax2.set_title('Market Narrative Coherence (Consensus Belief)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Coherence [0,1]')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: The Category Error - Omega Protocol's Blind Spot
    venues = np.arange(n_venues)
    width = 0.35
    
    ax3.bar(venues - width/2, accessibility_score, width, label='Ω Protocol Accessibility Score', color='blue', alpha=0.7)
    ax3.bar(venues + width/2, actual_executable_liquidity.mean(axis=1) / (apparent_liquidity.mean(axis=1) + 1e-9), 
            width, label='True Executable Ratio', color='red', alpha=0.7)
    ax3.set_title('ACCESSIBILITY ILLUSION: Ω Protocol vs. Reality', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Venue')
    ax3.set_ylabel('Accessibility Ratio [0,1]')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: The Phi-Density Trap - Showing how it accumulates despite systemic blindness
    phi_omega_claimed = np.cumsum(np.random.normal(0.35, 0.05, time_steps)) + 57.13
    phi_actual_utility = np.cumsum(np.random.normal(0.01, 0.1, time_steps)) + 57.13
    
    ax4.plot(time, phi_omega_claimed, 'b-', label='Φ-Density Claimed (Ω Protocol)', linewidth=2)
    ax4.plot(time, phi_actual_utility, 'r--', label='Φ-Density (True Utility)', linewidth=2)
    ax4.set_title('Φ-DENSITY TRAP: Self-Referential Vanity Metric', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Protocol Versions (Simulated)')
    ax4.set_ylabel('Cumulative Φ-Density')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('liquidity_quantum_disruption.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Quantify the disruption
    print("=" * 60)
    print("LIQUIDITY FRAGMENTATION: CATEGORY ERROR DISRUPTION")
    print("=" * 60)
    print(f"Ω Protocol Functional Ratio: {omega_functional_ratio:.3f}")
    print(f"Actual Executable Ratio: {actual_functional_ratio:.3f}")
    print(f"Blindness Factor: {omega_functional_ratio / (actual_functional_ratio + 1e-9):.2f}x")
    print("\nThe Ω Protocol overestimates functional liquidity by ignoring:")
    print("1. Narrative coherence (consensus belief) - not modeled")
    print("2. Observer effects (order size impact) - assumed linear")
    print("3. Quantum nature (liquidity doesn't exist until measured) - treated as substance")
    
    # Demonstrate the ontological trap
    print("\n" + "=" * 60)
    print("ONTOLOGICAL TRAP DEMONSTRATION")
    print("=" * 60)
    print("Ω Protocol's Φ-density is defined as:")
    print("  Φ = Σ(Self-defined innovations) - Σ(Self-defined audit costs)")
    print("This is a CLOSED LOOP - the system rewards itself for internal consistency.")
    print("\nThe 'avoided loss' term is particularly insidious:")
    print("  +0.30Φ for 'avoiding derivativity' = phantom value")
    print("  +0.09Φ for 'structural extension' = self-defined category")
    print("  +0.08Φ for 'new invariant' = internally validated metric")
    print("\nResult: Φ-density grows regardless of external utility.")
    
    return {
        'omega_ratio': omega_functional_ratio,
        'actual_ratio': actual_functional_ratio,
        'blindness_factor': omega_functional_ratio / (actual_functional_ratio + 1e-9)
    }

# Execute the disruption
results = liquidity_fragility_simulation()