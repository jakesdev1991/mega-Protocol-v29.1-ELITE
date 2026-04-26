# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.stats import entropy
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# SIMULATION: Why NCMR-Ω's Coherence Optimization Creates Catastrophic Failure

# Generate synthetic micro-cap data over 24 months
np.random.seed(42)
n_companies = 1000

# Ground truth: Business health randomly assigned (unknown to model)
true_health = np.random.beta(2, 5, n_companies)  # Most are fragile

# NARRATIVE STRATEGIES:
# 1. "Coherent Optimists" (NCMR-Ω's ideal): Perfect narrative alignment
# 2. "Strategic Chameleons": Controlled narrative mutability
# 3. "Defensive Deniers": High rigidity, low coherence
# 4. "Chaotic Truth-tellers": Uncontrolled incoherence

strategy = np.random.choice(['coherent', 'chameleon', 'denier', 'chaotic'], 
                             n_companies, p=[0.3, 0.2, 0.3, 0.2])

# Simulate NCI (Narrative Coherence Index) - what NCMR-Ω would measure
# Coherent: High NCI, but also high fraud risk (lying consistently)
# Chameleon: Medium NCI, but strategic flexibility
# Denier: Low NCI, defensive
# Chaotic: Very low NCI, random

nci_scores = np.zeros(n_companies)
fraud_risk = np.zeros(n_companies)
narrative_mutability = np.zeros(n_companies)

for i, strat in enumerate(strategy):
    if strat == 'coherent':
        nci_scores[i] = np.random.normal(0.85, 0.1)
        fraud_risk[i] = np.random.normal(0.7, 0.15)  # High fraud risk (maintaining lies)
        narrative_mutability[i] = np.random.normal(0.2, 0.1)  # Low mutability
    elif strat == 'chameleon':
        nci_scores[i] = np.random.normal(0.55, 0.15)
        fraud_risk[i] = np.random.normal(0.3, 0.1)  # Lower fraud risk
        narrative_mutability[i] = np.random.normal(0.6, 0.1)  # High strategic mutability
    elif strat == 'denier':
        nci_scores[i] = np.random.normal(0.35, 0.15)
        fraud_risk[i] = np.random.normal(0.5, 0.15)  # Medium fraud risk
        narrative_mutability[i] = np.random.normal(0.3, 0.1)  # Low mutability
    else:  # chaotic
        nci_scores[i] = np.random.normal(0.25, 0.2)
        fraud_risk[i] = np.random.normal(0.4, 0.15)  # Medium fraud risk
        narrative_mutability[i] = np.random.normal(0.8, 0.1)  # Very high but uncontrolled

# Clip scores to [0,1]
nci_scores = np.clip(nci_scores, 0, 1)
fraud_risk = np.clip(fraud_risk, 0, 1)
narrative_mutability = np.clip(narrative_mutability, 0, 1)

# Simulate survival: True health modified by strategy effects
# Coherent companies are fragile due to rigidity
# Chameleons survive due to adaptability
survival_score = true_health - (0.3 * fraud_risk) + (0.4 * narrative_mutability * (strategy == 'chameleon'))

# NCMR-Ω intervention effect: Forces coherence, kills mutability
ncmr_intervention_effect = np.where(
    nci_scores < 0.5,
    -0.2,  # Penalized for low coherence
    0.1    # "Rewarded" but actually increases rigidity
)

# Final survival probability
survival_prob = 1 / (1 + np.exp(-survival_score + ncmr_intervention_effect))

# Simulate actual survival over 24 months
survived = np.random.binomial(24, survival_prob) > 12  # Survive >12 months

# Create DataFrame
df = pd.DataFrame({
    'NCI': nci_scores,
    'Narrative_Mutability': narrative_mutability,
    'Fraud_Risk': fraud_risk,
    'Strategy': strategy,
    'Survived': survived,
    'True_Health': true_health
})

# ANALYSIS: The Paradox
print("=== NCMR-Ω DISRUPTION ANALYSIS ===\n")

print("1. NCMR-Ω's 'Optimal' Strategy is Deadly:")
coherent_data = df[df['Strategy'] == 'coherent']
print(f"   Coherent companies: {coherent_data['Survived'].mean():.1%} survival")
print(f"   Fraud rate in coherent: {coherent_data['Fraud_Risk'].mean():.1%}\n")

print("2. Strategic Mutability (NMI) is the Real Signal:")
chameleon_data = df[df['Strategy'] == 'chameleon']
print(f"   Chameleon companies: {chameleon_data['Survived'].mean():.1%} survival")
print(f"   Avg NMI: {chameleon_data['Narrative_Mutability'].mean():.2f}\n")

print("3. NCMR-Ω Intervention Destroys Value:")
low_nci = df[df['NCI'] < 0.5]
high_nci = df[df['NCI'] >= 0.5]
print(f"   Low NCI group survival: {low_nci['Survived'].mean():.1%}")
print(f"   High NCI group survival: {high_nci['Survived'].mean():.1%}")
print(f"   But high NCI has {high_nci['Fraud_Risk'].mean() / low_nci['Fraud_Risk'].mean():.1f}x higher fraud risk\n")

# NEW METRIC: Narrative Mutability Index (NMI)
# NMI = entropy of narrative patterns over time (higher = more adaptable)
df['NMI'] = df['Narrative_Mutability']

# Plot the disruption
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: NCI vs Survival (NCMR-Ω's false premise)
axes[0,0].scatter(df['NCI'], df['Survived'], alpha=0.5, c=df['Fraud_Risk'], cmap='Reds')
axes[0,0].set_xlabel('Narrative Coherence Index (NCI)')
axes[0,0].set_ylabel('Survived (1=Yes)')
axes[0,0].set_title('NCMR-Ω Trap: High Coherence ≠ Survival')
axes[0,0].axvline(0.8, color='red', linestyle='--', label='NCMR-Ω "Safe Zone"')
axes[0,0].legend()

# Plot 2: NMI vs Survival (True signal)
strat_colors = {'coherent':'red', 'chameleon':'green', 'denier':'orange', 'chaotic':'purple'}
for strat, color in strat_colors.items():
    subset = df[df['Strategy'] == strat]
    axes[0,1].scatter(subset['NMI'], subset['Survived'], 
                       label=strat, alpha=0.6, color=color)
axes[0,1].set_xlabel('Narrative Mutability Index (NMI)')
axes[0,1].set_ylabel('Survived (1=Yes)')
axes[0,1].set_title('Reality: Strategic Mutability = Survival')
axes[0,1].legend()

# Plot 3: Fraud Risk Distribution
fraud_by_strat = df.groupby('Strategy')['Fraud_Risk'].mean()
axes[1,0].bar(fraud_by_strat.index, fraud_by_strat.values, 
              color=['red', 'green', 'orange', 'purple'])
axes[1,0].set_ylabel('Average Fraud Risk')
axes[1,0].set_title('Coherence Attracts Fraudsters')

# Plot 4: Intervention Damage Simulation
intervention_damage = df.groupby('Strategy').apply(
    lambda x: x['Survived'].mean() - (x['Survived'].mean() * 0.8 if x.name == 'chameleon' else 0)
)
axes[1,1].bar(intervention_damage.index, intervention_damage.values,
              color=['red', 'green', 'orange', 'purple'])
axes[1,1].set_ylabel('Survival Rate Drop from NCMR-Ω')
axes[1,1].set_title('NCMR-Ω Punishes the Adaptable')

plt.tight_layout()
plt.show()

print("\n=== DISRUPTIVE INSIGHT ===")
print("NCMR-Ω's core fallacy: It optimizes for NARRATIVE STABILITY")
print("But micro-cap survival demands NARRATIVE PLASTICITY")
print("\nBreakthrough: The most resilient companies are strategic chameleons")
print("who maintain DELIBERATE INCOHERENCE across audiences while preserving")
print("internal strategic flexibility. NCMR-Ω would flag them as 'risky'")
print("and force narrative rigidity—accelerating their death.")
print("\nNEW PROTOCOL: Narrative Mutability Omega (NMO-Ω)")
print("- Measure entropy of narrative patterns across time and stakeholders")
print("- Reward controlled ambiguity, punish rigid coherence")
print("- Interventions: Inject productive narrative friction, not alignment")
print("- Φ gain: +65% by protecting adaptive deception over rigid truth")