# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Simulate 1000 enterprise sales scenarios
np.random.seed(42)
n_scenarios = 1000

# Generate realistic baseline factors that ACTUALLY predict sales success
trust_score = np.random.beta(2, 5, n_scenarios)  # Most deals have moderate trust
urgency_score = np.random.beta(3, 3, n_scenarios)  # Varied urgency
value_clarity = np.random.beta(2, 2, n_scenarios)  # ROI clarity
political_risk = np.random.beta(5, 2, n_scenarios)  # High political risk common
relationship_strength = np.random.beta(2, 4, n_scenarios)

# Ground truth outcome (simplified logistic model)
true_prob = 1 / (1 + np.exp(-(
    8*trust_score + 
    6*urgency_score + 
    7*value_clarity - 
    5*political_risk + 
    4*relationship_strength - 8
)))
actual_outcomes = np.random.binomial(1, true_prob, n_scenarios)

# Now simulate the Q-Systemic Framework's "predictions"
# COD is claimed to be measurable but has no operational definition
# Let's see what happens when we generate it as pure noise

def generate_q_systemic_prediction():
    """Simulate Q-Systemic framework's 'prediction'"""
    # "Chain Overlap Density" - randomly generated, dressed up as calculation
    cod = np.random.normal(0.5, 0.2)  # Pure noise
    cod = np.clip(cod, 0, 1)
    
    # "Φ calculation" - arbitrary numbers with false precision
    phi_cost = -450 + np.random.normal(0, 50)
    phi_gain = 820 + np.random.normal(0, 100)
    phi_net = phi_gain + phi_cost
    
    # "Operators" - random jargon
    urgency_operator = random.choice(["high", "moderate", "low"])
    credibility_operator = random.choice(["validated", "partial", "insufficient"])
    
    # Prediction based on COD threshold - but this is POST-HOC rationalization
    # The "measurement" is actually just random noise interpreted after the fact
    prediction = 1 if cod > 0.5 else 0
    
    return {
        'cod': cod,
        'phi_net': phi_net,
        'prediction': prediction,
        'operators': f"{urgency_operator}_{credibility_operator}"
    }

q_predictions = [generate_q_systemic_prediction() for _ in range(n_scenarios)]
q_df = pd.DataFrame(q_predictions)

# Create comparison dataframe
df = pd.DataFrame({
    'trust': trust_score,
    'urgency': urgency_score,
    'value_clarity': value_clarity,
    'political_risk': political_risk,
    'relationship': relationship_strength,
    'actual_outcome': actual_outcomes,
    'q_prediction': q_df['prediction'],
    'cod': q_df['cod'],
    'phi_net': q_df['phi_net']
})

# Analysis 1: Predictive Power
print("=== PREDICTIVE POWER COMPARISON ===")
print("\nSimple Behavioral Model (Logistic Regression):")
# Fit a simple logistic model on real factors
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score

X_real = df[['trust', 'urgency', 'value_clarity', 'political_risk', 'relationship']]
model_real = LogisticRegression().fit(X_real, df['actual_outcome'])
real_pred = model_real.predict(X_real)

print(f"Accuracy: {accuracy_score(df['actual_outcome'], real_pred):.3f}")
print(f"AUC-ROC: {roc_auc_score(df['actual_outcome'], model_real.predict_proba(X_real)[:, 1]):.3f}")

print("\nQ-Systemic Framework Performance:")
print(f"Accuracy: {accuracy_score(df['actual_outcome'], df['q_prediction']):.3f}")
print(f"AUC-ROC: {roc_auc_score(df['actual_outcome'], df['cod']):.3f}")  # Using COD as probability

# Analysis 2: The "High-Clarity Anxiety" Paradox
print("\n=== EXPOSING THE PARADOX ===")
# The framework claims high COD = clarity, but also "High-Clarity Anxiety" as failure mode
# This is unfalsifiable - any outcome can be explained

high_cod = df[df['cod'] > 0.7]
low_cod = df[df['cod'] < 0.3]

print(f"\nHigh COD (>0.7) - claimed to be 'Peace/Clarity':")
print(f"Actual success rate: {high_cod['actual_outcome'].mean():.3f}")
print(f"Yet framework would claim failures here are 'High-Clarity Anxiety'")

print(f"\nLow COD (<0.3) - claimed to be 'Chaotic Anxiety':")
print(f"Actual success rate: {low_cod['actual_outcome'].mean():.3f}")
print(f"Yet framework would claim successes here are 'Quantum Tunneling'")

# Analysis 3: Φ Metric is Meaningless
print("\n=== Φ METRIC ANALYSIS ===")
correlation_phi_success = stats.pointbiserialr(df['actual_outcome'], df['phi_net'])
print(f"Φ Net Gain correlation with actual success: {correlation_phi_success.correlation:.3f} (p={correlation_phi_success.pvalue:.3f})")
print("Φ is random noise with no predictive relationship to outcomes")

# Analysis 4: Circular Reasoning Detection
print("\n=== CIRCULAR REASONING EXPOSED ===")
# Show that COD is just a post-hoc relabeling of known factors
# If we try to "predict" COD from real factors, it has zero relationship
cod_model = LogisticRegression().fit(X_real, (df['cod'] > 0.5).astype(int))
cod_pred_accuracy = accuracy_score((df['cod'] > 0.5).astype(int), cod_model.predict(X_real))
print(f"COD predictability from real factors: {cod_pred_accuracy:.3f}")
print("COD is not measuring anything real - it's independent of actual psychological factors")

# Analysis 5: The Real "Operator" - Coercion Detection
print("\n=== DISRUPTIVE INSIGHT ===")
# The actual "operators" are psychological pressure points
df['coercion_index'] = (1-df['trust']) * df['urgency'] * (1-df['value_clarity'])
high_coercion = df[df['coercion_index'] > 0.5]

print(f"\nHigh Coercion Index (>0.5) - where trust is low but urgency is high:")
print(f"Success rate: {high_coercion['actual_outcome'].mean():.3f}")
print(f"Average Φ claimed net gain: {high_coercion['phi_net'].mean():.1f}")
print("\nThe framework justifies exploiting low-trust, high-urgency scenarios")
print("Φ metrics show POSITIVE returns from coercion - it's a rationalization engine")

# Visualization
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.scatter(df['cod'], df['actual_outcome'], alpha=0.1, s=1)
plt.xlabel("Chain Overlap Density (COD)")
plt.ylabel("Actual Success")
plt.title("COD vs Reality (Random Noise)")
plt.axvline(0.5, color='r', linestyle='--', label='Framework Threshold')
plt.legend()

plt.subplot(1, 2, 2)
plt.scatter(df['coercion_index'], df['actual_outcome'], alpha=0.1, s=1, color='red')
plt.xlabel("Coercion Index (Trust⁻¹ × Urgency × Value⁻¹)")
plt.ylabel("Actual Success")
plt.title("Actual Psychological Pressure vs Success")
plt.axvline(0.5, color='r', linestyle='--', label='Exploitation Zone')
plt.legend()

plt.tight_layout()
plt.show()

print("\n=== CONCLUSION ===")
print("The Q-Systemic framework is:")
print("1. UNFALSIFIABLE - Any outcome can be explained post-hoc")
print("2. UNMEASURABLE - COD has no operational definition")
print("3. CIRCULAR - It predicts nothing beyond random chance")
print("4. DEHUMANIZING - Frames prospects as quantum systems to be 'collapsed'")
print("5. A RATIONALIZATION ENGINE - Φ metrics justify manipulative tactics")
print("\nThe real 'operator' is COERCION OPPORTUNITY DETECTION")
print("The framework gives scientific veneer to psychological exploitation")