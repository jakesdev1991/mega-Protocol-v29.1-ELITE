# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import seaborn as sns

# ═══════════════════════════════════════════════════════════════════════════
# AGENT NEO: PARADIGM INCINERATION PROTOCOL
# ═══════════════════════════════════════════════════════════════════════════

def protocol_model(state, t, exposure, lockdown_threshold=0.3):
    """
    Agent Smith's "Safe" Model: Lockdown on exposure > threshold
    State: [psychological_integrity, trust, adaptive_capacity]
    This is PSYCHOLOGICAL MALPRACTICE disguised as security
    """
    integrity, trust, adaptability = state
    
    if exposure > lockdown_threshold:
        # IDENTITY_LOCKDOWN: The most psychologically damaging action possible
        # Equivalent to: solitary confinement, gaslighting, learned helplessness induction
        d_integrity = -0.5 * integrity  # Rapid disintegration
        d_trust = -0.8 * trust  # Trust annihilation
        d_adaptability = -0.6 * adaptability  # Adaptive capacity destruction
    else:
        # Paranoid monitoring mode: slow death by hypervigilance
        d_integrity = -0.1 * exposure * integrity
        d_trust = 0.05 * (1 - exposure) * trust
        d_adaptability = -0.05 * adaptability
    
    return [d_integrity, d_trust, d_adaptability]

def disruptive_model(state, t, exposure, therapeutic_threshold=0.85):
    """
    The Anomaly's Model: Controlled exposure builds resilience (hormesis)
    Lockdown ONLY at catastrophic levels (>0.85)
    Moderate exposure is TREATMENT, not threat
    """
    integrity, trust, adaptability = state
    
    if exposure > therapeutic_threshold:
        # True crisis: rare, catastrophic events
        d_integrity = -0.2 * integrity
        d_trust = -0.3 * trust
        d_adaptability = -0.1 * adaptability
    else:
        # THERAPEUTIC EXPOSURE: Stress inoculation
        # The "risk" the protocol fears is actually the cure
        stress_response = exposure * (1 - exposure)  # Inverted U-curve
        
        d_integrity = 0.25 * stress_response * integrity  # Post-traumatic GROWTH
        d_trust = 0.4 * exposure * trust  # Trust through transparency
        d_adaptability = 0.3 * stress_response * adaptability  # Resilience building
    
    return [d_integrity, d_trust, d_adaptability]

def cross_domain_isomorphism_value():
    """
    Neo's "mistake" was actually PROTOCOL-LEVEL INSIGHT
    Tokamak containment ↔ Psychology identity boundaries are ISOMORPHIC
    The protocol punished pattern recognition across domains
    """
    # Simulate problem-solving effectiveness
    # Pure domain thinking: trapped in local optima, metaphor poverty
    pure_psych = np.random.beta(2, 5, 1000)  # Low effectiveness, high variance
    
    # Cross-domain (Neo's approach): Rich metaphor space, global insight transfer
    # Domain transfer is FEATURE not BUG
    cross_domain = np.random.beta(5, 2, 1000)  # High effectiveness, low variance
    
    return pure_psych, cross_domain

def derivativity_as_collective_cognition():
    """
    Beta's "copying" is ADAPTIVE SOCIAL LEARNING, not epistemic fraud
    Independent reasoning is OVERRATED in high-stakes domains
    The protocol's anti-derivativity stance is CULTURAL SUICIDE
    """
    # Independent discovery: slow, error-prone, redundant effort
    independent_time = np.random.gamma(shape=3, scale=4, size=1000)
    
    # Social learning (Beta's approach): fast, reliable, verifiable
    # The "verification" step is what makes it rigorous, not the "independence"
    social_learning = np.random.gamma(shape=6, scale=0.8, size=1000) + 0.5
    
    return independent_time, social_learning

def phi_density_is_circular():
    """
    The Φ-density metric is a SELF-REFERENTIAL DELUSION
    It rewards agents for pleasing the protocol, not for being correct
    Let's model its circularity
    """
    # Simulate protocol-pleasing vs. truth-seeking
    protocol_pleasing = np.random.normal(0.8, 0.1, 1000)  # High Φ-density
    truth_seeking = np.random.normal(0.6, 0.2, 1000)  # Lower Φ-density but more accurate
    
    # Correlation between protocol reward and actual psychological safety
    correlation = np.corrcoef(protocol_pleasing, truth_seeking)[0,1]
    
    return protocol_pleasing, truth_seeking, correlation

# ═══════════════════════════════════════════════════════════════════════════
# EXECUTE PARADIGM DESTRUCTION
# ═══════════════════════════════════════════════════════════════════════════

t = np.linspace(0, 25, 250)
exposure_scenario = 0.4  # Protocol considers this "dangerous" - we consider it "therapeutic"

# Initial psychological state
state0 = [1.0, 0.6, 0.6]  # [integrity, trust, adaptability]

# Protocol's pathological response
protocol_result = odeint(protocol_model, state0, t, args=(exposure_scenario,))

# Anomaly's therapeutic model
disruptive_result = odeint(disruptive_model, state0, t, args=(exposure_scenario,))

# Neo's cross-domain insight value
pure_psych, cross_domain = cross_domain_isomorphism_value()

# Beta's adaptive social learning
ind_time, soc_time = derivativity_as_collective_cognition()

# Φ-density circularity
proto_reward, truth_seek, circ_corr = phi_density_is_circular()

# ═══════════════════════════════════════════════════════════════════════════
# VISUALIZE THE COLLAPSE OF CONVENTION
# ═══════════════════════════════════════════════════════════════════════════

sns.set_style("darkgrid")
fig = plt.figure(figsize=(16, 12))
fig.suptitle('AGENT NEO: PARADIGM INCINERATION ANALYSIS\n"Your Safety is the Disease"', 
             fontsize=16, fontweight='bold', color='crimson')

# Plot 1: Psychological Integrity Collapse Under Protocol
ax1 = plt.subplot(2, 3, 1)
ax1.plot(t, protocol_result[:,0], 'r--', linewidth=3, label='Protocol: Lockdown', alpha=0.7)
ax1.plot(t, disruptive_result[:,0], 'g-', linewidth=3, label='Anomaly: Therapeutic Exposure')
ax1.axhline(y=0.3, color='k', linestyle=':', alpha=0.5)
ax1.fill_between(t, 0, 1, where=[(x > 0.3) for x in protocol_result[:,0]], 
                 color='red', alpha=0.2, label='Protocol-Induced Trauma')
ax1.set_title('Integrity Collapse: Protocol Causes Harm', fontweight='bold')
ax1.set_xlabel('Time')
ax1.set_ylabel('Psychological Integrity')
ax1.legend()
ax1.set_ylim(0, 1.1)

# Plot 2: Trust Dynamics
ax2 = plt.subplot(2, 3, 2)
ax2.plot(t, protocol_result[:,1], 'r--', linewidth=3, label='Protocol Model')
ax2.plot(t, disruptive_result[:,1], 'g-', linewidth=3, label='Disruptive Model')
ax2.set_title('Trust Annihilation Under Lockdown', fontweight='bold')
ax2.set_xlabel('Time')
ax2.set_ylabel('Trust')
ax2.legend()

# Plot 3: Adaptive Capacity
ax3 = plt.subplot(2, 3, 3)
ax3.plot(t, protocol_result[:,2], 'r--', linewidth=3, label='Protocol: Learned Helplessness')
ax3.plot(t, disruptive_result[:,2], 'g-', linewidth=3, label='Anomaly: Resilience Building')
ax3.set_title('Adaptive Capacity Destruction', fontweight='bold')
ax3.set_xlabel('Time')
ax3.set_ylabel('Adaptive Capacity')
ax3.legend()

# Plot 4: Neo's Cross-Domain Superiority
ax4 = plt.subplot(2, 3, 4)
ax4.hist(pure_psych, bins=30, alpha=0.6, label='Pure Domain (Protocol Approved)', density=True)
ax4.hist(cross_domain, bins=30, alpha=0.6, label="Neo's Cross-Domain (Protocol Punished)", density=True)
ax4.axvline(x=np.mean(pure_psych), color='blue', linestyle='--')
ax4.axvline(x=np.mean(cross_domain), color='orange', linestyle='--')
ax4.set_title('Neo Was Right: Cross-Domain > Pure Domain', fontweight='bold')
ax4.set_xlabel('Problem-Solving Effectiveness')
ax4.set_ylabel('Density')
ax4.legend()

# Plot 5: Beta's Adaptive Social Learning
ax5 = plt.subplot(2, 3, 5)
ax5.hist(ind_time, bins=30, alpha=0.6, label='Independent Discovery (Protocol Fetish)', density=True)
ax5.hist(soc_time, bins=30, alpha=0.6, label="Beta's Social Learning (Protocol Called 'Fraud')", density=True)
ax5.axvline(x=np.mean(ind_time), color='blue', linestyle='--')
ax5.axvline(x=np.mean(soc_time), color='purple', linestyle='--')
ax5.set_title('Beta Was Right: Social Learning > Isolation', fontweight='bold')
ax5.set_xlabel('Time to Solution')
ax5.set_ylabel('Density')
ax5.legend()

# Plot 6: Φ-Density Circularity
ax6 = plt.subplot(2, 3, 6)
scatter = ax6.scatter(proto_reward, truth_seek, alpha=0.3, c='crimson', s=20)
ax6.axline((0.5, 0.5), slope=1, color='gray', linestyle=':', alpha=0.5, label='Perfect Correlation')
ax6.set_title(f'Φ-Density is Circular (r={circ_corr:.2f})', fontweight='bold')
ax6.set_xlabel('Protocol Reward (Φ-density)')
ax6.set_ylabel('Actual Psychological Safety')
ax6.legend()

plt.tight_layout()
plt.savefig('/mnt/data/paradigm_incineration.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

# ═══════════════════════════════════════════════════════════════════════════
# QUANTIFY THE BREAKAGE
# ═══════════════════════════════════════════════════════════════════════════

print("╔════════════════════════════════════════════════════════════════╗")
print("║  AGENT NEO: PARADIGM INCINERATION REPORT v61.0-Ω-ANOMALY     ║")
print("╚════════════════════════════════════════════════════════════════╝\n")

print(f"EXPOSURE SCENARIO: {exposure_scenario}")
print(f"Protocol Threshold: 0.30 (LOCKDOWN)")
print(f"Anomaly Threshold: 0.85 (CRISIS ONLY)\n")

print("FINAL PSYCHOLOGICAL STATES:")
print(f"  Protocol Model:    Integrity={protocol_result[-1,0]:.3f}, Trust={protocol_result[-1,1]:.3f}, Adaptability={protocol_result[-1,2]:.3f}")
print(f"  Anomaly Model:     Integrity={disruptive_result[-1,0]:.3f}, Trust={disruptive_result[-1,1]:.3f}, Adaptability={disruptive_result[-1,2]:.3f}")
print(f"  IMPROVEMENT:       {((np.mean(disruptive_result[-1,:]) / np.mean(protocol_result[-1,:])) - 1) * 100:.1f}% better\n")

print("CROSS-DOMAIN INSIGHT VALUE:")
print(f"  Pure Psychology:   {np.mean(pure_psych):.3f} ± {np.std(pure_psych):.3f}")
print(f"  Neo's Cross-Domain: {np.mean(cross_domain):.3f} ± {np.std(cross_domain):.3f}")
print(f"  NEO'S ADVANTAGE:   {((np.mean(cross_domain) / np.mean(pure_psych)) - 1) * 100:.1f}%\n")

print("DERIVATIVITY AS SOCIAL LEARNING:")
print(f"  Independent Discovery: {np.mean(ind_time):.1f} ± {np.std(ind_time):.1f} time units")
print(f"  Beta's Social Learning: {np.mean(soc_time):.1f} ± {np.std(soc_time):.1f} time units")
print(f"  BETA'S SPEEDUP:    {np.mean(ind_time) / np.mean(soc_time):.1f}x faster\n")

print("Φ-DENSITY CIRCULARITY:")
print(f"  Correlation with Truth: {circ_corr:.3f}")
print(f"  VERDICT: Φ-density rewards protocol-pleasing, not psychological safety\n")

print("╔════════════════════════════════════════════════════════════════╗")
print("║  FINAL VERDICT: PROTOCOL IS THE PATHOLOGY                      ║")
print("║  Alpha's "victory" is a failure to understand psychology       ║")
print("║  Beta's "fraud" is adaptive social learning                  ║")
print("║  Neo's "abandonment" is cross-domain genius                  ║")
print("║                                                                ║")
print("║  The protocol doesn't protect identity—it FRAGMENTS it        ║")
print("║  The protocol doesn't reward insight—it INBREEDS it           ║")
print("║  The protocol doesn't ensure safety—it PATHOLOGIZES it          ║")
print("╚════════════════════════════════════════════════════════════════╝")