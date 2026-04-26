# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, beta

def epistemic_circularity_demo():
    """
    Demonstrates that the Q-Systemic framework is unfalsifiable:
    COD is reverse-engineered from outcomes, not predictive.
    """
    np.random.seed(42)
    
    # Generate 100 random "sales opportunities" with random features
    n = 100
    features = np.random.randn(n, 5)  # Fake CRM/call data
    
    # Random outcomes (30% win rate)
    outcomes = np.random.choice(['win', 'loss'], n, p=[0.3, 0.7])
    
    def engineer_cod(outcomes):
        """Engineer COD to perfectly correlate with outcomes post-hoc"""
        cod = np.zeros(n)
        cod[outcomes == 'win'] = beta.rvs(2, 5, size=np.sum(outcomes == 'win')) * 0.3 + 0.7
        cod[outcomes == 'loss'] = beta.rvs(5, 2, size=np.sum(outcomes == 'loss')) * 0.3
        return cod
    
    cod = engineer_cod(outcomes)
    
    # Calculate fake "invariants" (circular logic)
    coherence = np.mean(cod)
    lambda_const = 1.0
    lambda_N = lambda_const * (3/coherence + 1/coherence**2)
    lambda_Delta = lambda_const * (1/coherence + 3/coherence**2)
    xi = np.sqrt(1/lambda_N * 1/lambda_Delta)
    
    # Visualize the tautology
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: COD perfectly separates wins/losses (because it was engineered to)
    win_cod = cod[outcomes == 'win']
    loss_cod = cod[outcomes == 'loss']
    ax1.hist([win_cod, loss_cod], bins=15, label=['Wins', 'Losses'], alpha=0.7)
    ax1.axvline(x=0.5, color='r', linestyle='--', label='Critical Threshold')
    ax1.set_xlabel('Chain Overlap Density (COD)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('COD Perfectly Predicts Outcomes (Post-Hoc)')
    ax1.legend()
    
    # Plot 2: "Phase diagram" showing how any point can be explained
    xi_vals = np.linspace(0.1, 2.0, 100)
    psi_vals = np.log(xi_vals / 0.5)
    
    # Create fake regions
    shred_region = psi_vals < -0.5
    freeze_region = psi_vals > 0.5
    stable_region = ~shred_region & ~freeze_region
    
    ax2.scatter(xi_vals[stable_region], psi_vals[stable_region], c='g', s=10, label='Stable')
    ax2.scatter(xi_vals[shred_region], psi_vals[shred_region], c='r', s=10, label='Shredding')
    ax2.scatter(xi_vals[freeze_region], psi_vals[freeze_region], c='b', s=10, label='Freeze')
    ax2.axvline(x=xi, color='k', linewidth=3, label='Current State')
    ax2.set_xlabel('Correlation Length ξ')
    ax2.set_ylabel('Invariant ψ')
    ax2.set_title('Unfalsifiable Phase Space (Any ξ→ψ can be rationalized)')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('epistemic_circularity.png', dpi=150)
    plt.show()
    
    # Print the smoking gun
    print("=== EPISTEMIC CIRCULARITY DEMONSTRATED ===")
    print(f"Win rate: {np.mean(outcomes == 'win'):.3f}")
    print(f"Mean COD (wins): {np.mean(win_cod):.3f}")
    print(f"Mean COD (losses): {np.mean(loss_cod):.3f}")
    print(f"Fake invariant ξ: {xi:.3f}")
    print("\nCRITICAL FLAW: COD is defined as overlap integral but measured as outcome probability.")
    print("The physics formalism is metaphorical camouflage for a tautology.")
    return cod, outcomes

def cognitive_dissonance_disruption():
    """
    The disruption: Strategic Dissonance Protocol.
    Instead of maximizing resonance (COD), maximize productive uncertainty.
    """
    np.random.seed(1337)
    
    n_sellers = 1000
    n_steps = 30
    
    # State variables
    certainty = np.random.uniform(0.7, 0.9, n_sellers)
    engagement = np.random.uniform(0.1, 0.2, n_sellers)
    
    # Traditional resonance approach
    trad_certainty = certainty.copy()
    trad_engagement = engagement.copy()
    trad_conversions = np.zeros(n_sellers)
    
    # Dissonance protocol
    diss_certainty = certainty.copy()
    diss_engagement = engagement.copy()
    diss_conversions = np.zeros(n_sellers)
    
    for step in range(n_steps):
        # Traditional: smooth convergence
        trad_engagement += 0.002
        trad_certainty += 0.001
        trad_prob = 0.3 * trad_engagement * (trad_certainty - 0.5)
        
        # Dissonance: controlled destabilization
        # Introduce surprise that forces cognitive investment
        surprise = 0.4 * np.sin(step * np.pi / n_steps) * (1 - diss_certainty)
        diss_engagement += 0.015 * surprise
        diss_certainty -= 0.008 * surprise
        diss_certainty = np.clip(diss_certainty, 0.3, 0.95)
        
        # Conversion peaks at moderate certainty + high engagement
        optimal = 0.55
        certainty_factor = np.exp(-((diss_certainty - optimal)**2) / 0.08)
        diss_prob = 0.65 * diss_engagement * certainty_factor
        
        # Simulate
        trad_conversions += np.random.rand(n_sellers) < trad_prob
        diss_conversions += np.random.rand(n_sellers) < diss_prob
    
    trad_rate = np.mean(trad_conversions)
    diss_rate = np.mean(diss_conversions)
    
    print(f"\n=== COGNITIVE DISSONANCE DISRUPTION ===")
    print(f"Traditional Resonance conversion rate: {trad_rate:.3f}")
    print(f"Strategic Dissonance conversion rate: {diss_rate:.3f}")
    print(f"Improvement: {((diss_rate - trad_rate) / trad_rate * 100):.1f}%")
    print("\nMECHANISM: Uncertainty → Cognitive Investment → Internal Justification")
    
    # Plot the dynamics
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    steps = np.arange(n_steps)
    avg_trad_eng = 0.15 + 0.002 * steps
    avg_diss_eng = 0.15 + 0.008 * steps * np.sin(steps * np.pi / n_steps)
    
    axes[0, 0].plot(steps, avg_trad_eng, 'g--', label='Traditional')
    axes[0, 0].plot(steps, avg_diss_eng, 'r-', label='Dissonance')
    axes[0, 0].set_title("Engagement Dynamics")
    axes[0, 0].set_ylabel("Cognitive Investment")
    axes[0, 0].legend()
    
    avg_trad_cert = 0.8 + 0.001 * steps
    avg_diss_cert = 0.8 - 0.004 * steps * np.sin(steps * np.pi / n_steps)
    avg_diss_cert = np.clip(avg_diss_cert, 0.3, 0.95)
    
    axes[0, 1].plot(steps, avg_trad_cert, 'g--', label='Traditional')
    axes[0, 1].plot(steps, avg_diss_cert, 'r-', label='Dissonance')
    axes[0, 1].axhline(y=0.55, color='k', linestyle=':', label='Optimal Uncertainty')
    axes[0, 1].set_title("Certainty Dynamics")
    axes[0, 1].set_ylabel("Buyer Certainty")
    axes[0, 1].legend()
    
    # Cumulative conversions
    axes[1, 0].plot(steps, np.cumsum(avg_trad_eng * 0.3), 'g--', label='Traditional')
    axes[1, 0].plot(steps, np.cumsum(avg_diss_eng * 0.65 * np.exp(-((avg_diss_cert - 0.55)**2) / 0.08)), 'r-', label='Dissonance')
    axes[1, 0].set_title("Cumulative Conversion Probability")
    axes[1, 0].set_ylabel("Conversion Rate")
    axes[1, 0].legend()
    
    # Phase space trajectory
    axes[1, 1].plot(avg_trad_cert, avg_trad_eng, 'g--', label='Traditional (Resonance)')
    axes[1, 1].plot(avg_diss_cert, avg_diss_eng, 'r-', label='Dissonance Protocol')
    axes[1, 1].set_xlabel("Buyer Certainty")
    axes[1, 1].set_ylabel("Buyer Engagement")
    axes[1, 1].set_title("Phase Space: Traditional vs Disruption")
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig('dissonance_disruption.png', dpi=150)
    plt.show()
    
    return trad_rate, diss_rate

# Execute both demonstrations
print("=" * 60)
print("AGENT NEO: INITIATING PARADIGM DECONSTRUCTION")
print("=" * 60)

cod_data, outcome_data = epistemic_circularity_demo()
traditional_conv, dissonance_conv = cognitive_dissonance_disruption()

print("\n" + "=" * 60)
print("DISRUPTIVE INSIGHT SYNTHESIS")
print("=" * 60)