# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def calculate_homogeneity_index(liquidity_uniformity, volatility_depth_coupling, differentiation_efficacy):
    """From the proposal"""
    uniformity_component = liquidity_uniformity * 0.40
    coupling_component = volatility_depth_coupling * 0.35
    differentiation_reduction = differentiation_efficacy * 0.25
    homogeneity = uniformity_component + coupling_component - differentiation_reduction
    return np.clip(homogeneity, 0.0, 1.0)

def calculate_differentiation_efficacy(protocol_count, homogeneity_index, contagion_pathways):
    """From the proposal - note the circular dependency"""
    count_factor = min(1.0, protocol_count / 10.0)
    homogeneity_penalty = homogeneity_index * 0.50
    contagion_penalty = contagion_pathways * 0.30
    efficacy = count_factor * (1.0 - homogeneity_penalty - contagion_penway_penalty)
    return np.clip(efficacy, 0.0, 1.0)

def calculate_amm_homogeneity_risk(homogeneity_index, il_sensitivity, differentiation_efficacy):
    """From the proposal"""
    differentiation_deficit = 1.0 - differentiation_efficacy
    risk = homogeneity_index * il_sensitivity * differentiation_deficit
    return np.clip(risk, 0.0, 1.0)

# DISRUPTION 1: Circular Dependency Chaos
print("=== DISRUPTION 1: CIRCULAR DEPENDENCY ===")
# Let's simulate the system with realistic values
liquidity_uniformity = 0.7
volatility_depth_coupling = 0.6
contagion_pathways = 0.5
protocol_count = 5
il_sensitivity = 0.65

# Start with an initial guess for homogeneity_index
h_initial = 0.5
print(f"Initial guess for homogeneity_index: {h_initial}")

# Calculate differentiation_efficacy (which depends on homogeneity_index)
diff_eff = calculate_differentiation_efficacy(protocol_count, h_initial, contagion_pathways)
print(f"Differentiation efficacy (depends on h): {diff_eff:.3f}")

# Now calculate actual homogeneity_index (which depends on differentiation_efficacy)
h_actual = calculate_homogeneity_index(liquidity_uniformity, volatility_depth_coupling, diff_eff)
print(f"Actual homogeneity_index (depends on diff_eff): {h_actual:.3f}")

# Calculate risk
risk = calculate_amm_homogeneity_risk(h_actual, il_sensitivity, diff_eff)
print(f"AMM Homogeneity Risk: {risk:.3f}")

# Show the circularity: if we iterate, does it converge or diverge?
h_current = h_initial
for i in range(10):
    diff_eff = calculate_differentiation_efficacy(protocol_count, h_current, contagion_pathways)
    h_new = calculate_homogeneity_index(liquidity_uniformity, volatility_depth_coupling, diff_eff)
    print(f"Iteration {i}: h={h_new:.3f}, diff={diff_eff:.3f}")
    if abs(h_new - h_current) < 0.001:
        print(f"Converged after {i} iterations")
        break
    h_current = h_new

print("\n=== DISRUPTION 2: THE REAL RISK ISN'T STRUCTURAL ===")
# The proposal assumes homogeneity is a design property, but it's actually
# a market participant property. Let's model the real risk.

def real_coupling_risk(shared_lp_fraction, shared_arb_pathways, market_stress):
    """
    REAL risk comes from shared liquidity providers and arbitrageurs,
    not theoretical structural equivalence.
    """
    lp_coupling = shared_lp_fraction ** 2  # Quadratic effect
    arb_coupling = shared_arb_pathways ** 1.5  # Superlinear
    stress_amplification = 1 + market_stress * 2
    
    # When LPs exit, ALL "diverse" AMMs collapse simultaneously
    cascade_probability = (lp_coupling + arb_coupling) / 2 * stress_amplification
    return np.clip(cascade_probability, 0.0, 1.0)

# Simulate a realistic scenario
shared_lp_fraction = 0.4  # 40% of LPs use both Uniswap v3 and Curve
shared_arb_pathways = 0.6  # 60% of arbs trade across both
market_stress = 0.7  # High volatility period

real_risk = real_coupling_risk(shared_lp_fraction, shared_arb_pathways, market_stress)
print(f"Real coupling risk (shared LPs+arbs): {real_risk:.3f}")

print("\n=== DISRUPTION 3: THE PROPOSAL MEASURES EPIPHENOMENA ===")
# The proposal's metrics are effects, not causes.
# Let's show that homogeneity_index is just a lagging indicator
# of the REAL coupling mechanism (shared participants).

# Generate data showing that "homogeneity" is a consequence,
# not a cause
np.random.seed(42)
n_samples = 1000

# Real underlying coupling
shared_lps = np.random.beta(2, 5, n_samples)  # Mostly low, some high
shared_arbs = np.random.beta(3, 4, n_samples)

# Market stress random
stress = np.random.random(n_samples)

# Calculate real risk
real_risks = real_coupling_risk(shared_lps, shared_arbs, stress)

# The proposal's "homogeneity_index" would be a lagging function of this
# Let's model it as a noisy observation
observed_homogeneity = np.clip(real_risks + np.random.normal(0, 0.1, n_samples), 0, 1)

# Calculate correlation
correlation = np.corrcoef(real_risks, observed_homogeneity)[0, 1]
print(f"Correlation between real risk and observed homogeneity: {correlation:.3f}")

# Show that the proposal's risk model is just a noisy proxy
# for the real underlying coupling
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.scatter(real_risks, observed_homogeneity, alpha=0.5)
ax1.plot([0, 1], [0, 1], 'r--', label="y=x")
ax1.set_xlabel("Real Risk (Shared Participants)")
ax1.set_ylabel("Observed Homogeneity Index")
ax1.set_title("Homogeneity is a Lagging Indicator")
ax1.legend()

# Show the cascade effect
stress_levels = np.linspace(0, 1, 100)
risk_low_coupling = [real_coupling_risk(0.1, 0.1, s) for s in stress_levels]
risk_high_coupling = [real_coupling_risk(0.8, 0.8, s) for s in stress_levels]

ax2.plot(stress_levels, risk_low_coupling, label="Low Coupling (diverse LPs)")
ax2.plot(stress_levels, risk_high_coupling, label="High Coupling (shared LPs)")
ax2.set_xlabel("Market Stress")
ax2.set_ylabel("Cascade Probability")
ax2.set_title("Shared Participants = Real Risk")
ax2.legend()

plt.tight_layout()
plt.show()

print("\n=== DISRUPTION 4: THE ISOMORPHISM IS FORCED ===")
# The proposal claims AMM homogeneity ≈ protocol governance diversity
# But this is a category error. AMMs are mathematical functions;
# governance is social coordination. The structural roles DON'T match.

# Let's expose the forced analogy

def amm_failure_mode(liquidity_depth, volatility, trade_size):
    """AMM failure is deterministic mathematical slippage"""
    return trade_size / (liquidity_depth * (1 - volatility))

def governance_failure_mode(voter_turnout, quorum, proposal_controversy):
    """Governance failure is social coordination breakdown"""
    participation_risk = 1 - voter_turnout
    quorum_risk = max(0, quorum - voter_turnout)
    controversy_risk = proposal_controversy ** 2
    return (participation_risk + quorum_risk + controversy_risk) / 3

# These are not structurally isomorphic!
# AMM failure is continuous, deterministic, and instant
# Governance failure is discrete, probabilistic, and time-delayed

print("AMM failure mode (continuous, deterministic):", amm_failure_mode(100, 0.3, 50))
print("Governance failure mode (discrete, probabilistic):", governance_failure_mode(0.4, 0.5, 0.7))

print("\nThe 'structural equivalence' is an epistemic breach:")
print("- AMMs: mathematical curves, deterministic execution")
print("- Governance: social consensus, probabilistic coordination")
print("- They fail for ENTIRELY different reasons")
print("- Mapping them is forced analogy, not genuine isomorphism")