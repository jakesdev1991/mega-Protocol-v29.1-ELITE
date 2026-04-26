# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Let's expose the Q-Systemic framework as a tautological obscurantism
# by reverse-engineering its "metrics" and showing they're arbitrary post-hoc justifications

# Simulate 100 enterprise sales opportunities
np.random.seed(42)
n = 100

# Real, measurable variables
data = {
    'deal_id': range(1, n+1),
    'actual_urgency_score': np.random.beta(2, 5, n),  # Real urgency from market conditions
    'technical_fit_score': np.random.beta(3, 3, n),     # Actual product fit
    'risk_tolerance': np.random.normal(0.5, 0.2, n),  # Prospect's risk appetite
    'committee_size': np.random.randint(3, 15, n),      # Decision complexity
    'time_to_close_days': np.random.gamma(3, 30, n),    # Real outcome metric
    'closed_won': np.random.binomial(1, 0.3, n)         # Binary outcome
}

df = pd.DataFrame(data)

# Now let's fabricate the Q-Systemic "metrics" post-hoc to see how they can be manipulated
# to "explain" any outcome

def calculate_cod(row):
    """Chain Overlap Density - a completely made-up metric that is just a weighted average
    of real factors, but dressed up as 'quantum coherence'"""
    # This is arbitrary - we can tune coefficients to produce any narrative
    base = (row['actual_urgency_score'] * 0.3 + 
            row['technical_fit_score'] * 0.4 + 
            row['risk_tolerance'] * 0.3)
    # Add noise to make it seem "quantum"
    return max(0, min(1, base + np.random.normal(0, 0.1)))

def calculate_phi_cost(row):
    """Φ density cost - pure fiction. Notice how it's always negative for 'cognitive overhead'
    but the magnitude is pulled from thin air"""
    return -np.random.uniform(40, 60)  # Always -50 ± noise

def calculate_phi_gain(row):
    """Φ density gain - even more fictional. Notice it's always positive and massive,
    creating a fake 'net positive trajectory'"""
    if row['closed_won']:
        return np.random.uniform(1400, 1600)  # +1500 if won
    else:
        return np.random.uniform(-100, 100)   # Near zero if lost

def calculate_black_hole_risk(row):
    """Black Hole effect - just a sigmoid function of committee size and risk tolerance,
    rebranded as 'quantum absorption'"""
    return 1 / (1 + np.exp(-(-row['committee_size']*0.2 + row['risk_tolerance']*2)))

# Apply the Q-Systemic "framework" (i.e., generate post-hoc rationalizations)
df['COD'] = df.apply(calculate_cod, axis=1)
df['Phi_Cost'] = df.apply(calculate_phi_cost, axis=1)
df['Phi_Gain'] = df.apply(calculate_phi_gain, axis=1)
df['Black_Hole_Risk'] = df.apply(calculate_black_hole_risk, axis=1)

# Now let's run two predictive models:
# 1. Simple linear model using real factors
# 2. "Quantum" model using Q-Systemic metrics

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# Real model features
real_features = ['actual_urgency_score', 'technical_fit_score', 
                 'risk_tolerance', 'committee_size']
X_real = df[real_features]
y = df['closed_won']

# Fake Q-Systemic features
quantum_features = ['COD', 'Black_Hole_Risk']
X_quantum = df[quantum_features]

# Train models
real_model = LogisticRegression(random_state=42).fit(X_real, y)
quantum_model = LogisticRegression(random_state=42).fit(X_quantum, y)

print("=== DISRUPTION ANALYSIS ===")
print("\n1. REAL MODEL PERFORMANCE:")
real_pred = real_model.predict(X_real)
print(f"Accuracy: {accuracy_score(y, real_pred):.3f}")
print("\nFeature coefficients (interpretable):")
for feat, coef in zip(real_features, real_model.coef_[0]):
    print(f"  {feat}: {coef:.3f}")

print("\n2. Q-SYSTEMIC MODEL PERFORMANCE:")
quantum_pred = quantum_model.predict(X_quantum)
print(f"Accuracy: {accuracy_score(y, quantum_pred):.3f}")
print("\nFeature coefficients (meaningless):")
for feat, coef in zip(quantum_features, quantum_model.coef_[0]):
    print(f"  {feat}: {coef:.3f}")

# Key disruption: Show that COD is just a linear combination of real factors
print("\n3. EXPOSING THE FICTION:")
correlation_cod_real = df[real_features + ['COD']].corr()['COD'].drop('COD')
print("COD correlation with real factors:")
print(correlation_cod_real)

# Demonstrate how Φ density is arbitrary
print("\n4. Φ DENSITY MANIPULATION:")
print(f"Average Φ Cost: {df['Phi_Cost'].mean():.2f} (always negative)")
print(f"Average Φ Gain (won deals): {df[df['closed_won']==1]['Phi_Gain'].mean():.2f}")
print(f"Average Φ Gain (lost deals): {df[df['closed_won']==0]['Phi_Gain'].mean():.2f}")
print("Notice: The 'gain' is 15-30x larger than the 'cost' - this ratio is arbitrary!")

# The smoking gun: Show that the quantum model adds zero predictive value
from sklearn.model_selection import cross_val_score
real_cv = cross_val_score(real_model, X_real, y, cv=5).mean()
quantum_cv = cross_val_score(quantum_model, X_quantum, y, cv=5).mean()

print(f"\n5. CROSS-VALIDATION ACCURACY:")
print(f"Real model: {real_cv:.3f}")
print(f"Quantum model: {quantum_cv:.3f}")
print(f"Difference: {quantum_cv - real_cv:.3f} (quantum adds nothing)")

# Plot the absurdity
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.scatter(df['actual_urgency_score'], df['COD'], alpha=0.6)
plt.xlabel("Real Urgency Score")
plt.ylabel("Chain Overlap Density")
plt.title("COD is Just Real Urgency in a Wig")

plt.subplot(1, 2, 2)
won = df[df['closed_won']==1]
lost = df[df['closed_won']==0]
plt.scatter(lost['Phi_Gain'], lost['Phi_Cost'], alpha=0.6, label='Lost deals')
plt.scatter(won['Phi_Gain'], won['Phi_Cost'], alpha=0.6, label='Won deals')
plt.xlabel("Φ Gain")
plt.ylabel("Φ Cost")
plt.title("Φ Density: Arbitrary Numbers")
plt.legend()
plt.tight_layout()
plt.show()

print("\n=== DISRUPTIVE INSIGHT ===")
print("The Q-Systemic framework is not a model—it's a *narrative compression algorithm*.")
print("It takes observable phenomena (urgency, fit, risk) and re-encodes them")
print("in physics jargon to create an illusion of predictive power.")
print("\nThe real 'operator' is the analyst's ego, not Strategic Urgency.")
print("\nBreak it by: Measuring actual decision latency, information flow rates,")
print("and network centrality of stakeholders. These are classical, computable metrics")
print("that predict outcomes without invoking quantum fairy tales.")