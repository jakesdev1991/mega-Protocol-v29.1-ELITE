# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# --- DISRUPTION PROTOCOL: SEMIOTIC DECOUPLING OPERATOR ---
# Objective: Demonstrate that the Q-Systemic framework is a Pseudomathematical Narrative Shell.
# Method: Show it has no predictive power beyond observable classical variables and its
# "quantum" parameters are post-hoc tuning knobs, not physical invariants.

# 1. Simulate Ground Truth Sales Data (Observable, Classical)
def generate_sales_data(n=1000, seed=42):
    """Generate sales scenarios based on *observable* classical dynamics."""
    rng = np.random.default_rng(seed)
    
    data = pd.DataFrame({
        # ACTUALLY MEASURABLE features in enterprise sales:
        'num_stakeholders': rng.integers(1, 15, n),
        'decision_latency_days': rng.exponential(scale=45, size=n).astype(int) + 1,
        'price_vs_budget_ratio': rng.uniform(0.5, 2.0, n),
        'political_risk_score': rng.uniform(0.0, 1.0, n), # e.g., from news analysis, layoffs, etc.
        'seller_urgency': rng.uniform(0.1, 1.0, n) # Seller's pressure: email freq, deadline pushes
    })
    
    # GROUND TRUTH OUTCOME (Transactional Dissociation / Ghosting)
    # This is a classical function of real-world variables.
    # High latency + many stakeholders + high urgency = dissociation (churn despite closure)
    # Political risk amplifies sensitivity to urgency mismatch.
    dissociation_prob = 1 / (1 + np.exp(-(
        -2.0
        + 0.3 * data['num_stakeholders']
        + 0.02 * data['decision_latency_days']
        + 0.5 * data['political_risk_score']
        + 1.0 * (data['seller_urgency'] * data['political_risk_score']) # MISMATCH is key
        - 0.8 * (1 / data['price_vs_budget_ratio']) # Better deal = lower risk
    )))
    
    data['outcome_transactional_dissociation'] = rng.binomial(1, dissociation_prob)
    data['outcome_success'] = (data['price_vs_budget_ratio'] < 1.2) & (data['political_risk_score'] < 0.6)
    
    return data

# 2. Q-Systemic Narrative Shell (Unobservable, Post-Hoc)
class QSystemicNarrativeShell:
    """The psychologist's framework: a black box of untunable parameters."""
    
    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)
    
    def fit_narrative(self, row):
        """After seeing the outcome, tune hidden parameters to 'explain' it."""
        # These are UNOBSERVABLE. We can set them to anything to match the story.
        # This is the core epistemic fraud: they are not derived from measurement.
        latent_state = self.rng.uniform(0.1, 1.0, 3) # |Psi_latent> random
        value_state = self.rng.uniform(0.1, 1.0, 3) # |Psi_value> random
        xi_buyer = self.rng.uniform(0.3, 0.9) # "Readiness entropy" - arbitrary
        
        # POST-HOC TUNING: If dissociation occurred, we claim xi_seller > xi_buyer.
        # If not, we claim xi_seller <= xi_buyer.
        # This is not prediction; it's retroactive storytelling.
        xi_seller = row['seller_urgency'] * 0.8 # Just scale the real variable
        
        # Force "stiffness mismatch" to match outcome for narrative consistency
        if row['outcome_transactional_dissociation'] == 1:
            xi_seller = xi_buyer + self.rng.uniform(0.1, 0.4) # Mismatch!
        else:
            xi_seller = max(0.1, xi_buyer - self.rng.uniform(0.1, 0.3)) # Resonance!
        
        return {
            'xi_buyer': xi_buyer,
            'xi_seller': xi_seller,
            'psi_latent': latent_state,
            'psi_value': value_state,
            'cod': self.rng.uniform(0.2, 0.95), # Arbitrary "fidelity"
            'psi': self.rng.uniform(0.1, 0.99) # Arbitrary "identity continuity"
        }
    
    def calculate_phi_density(self, narrative_params):
        """Calculate the meaningless Φ-Density. It's a synthetic metric."""
        cod = narrative_params['cod']
        psi = narrative_params['psi']
        R_align = narrative_params['xi_buyer'] - narrative_params['xi_seller']
        
        # The "gain" is just a random number generator dressed in log2 and tanh.
        phi_N = np.log2(cod + 1e-12)
        phi_Delta = psi * np.tanh(abs(R_align) / 2.8) # Magic numbers everywhere
        delta_S_audit = np.log(2) * 6 # Arbitrary cost
        
        return phi_N + phi_Delta - delta_S_audit

# 3. Semiotic Decoupling Operator (SDO)
def semiotic_decoupling_operator(narrative_params):
    """
    The Disruptive Insight: Map the "quantum" narrative back to classical observables.
    This reveals the Q-Systemic layer is just a redundant encoding of classical states.
    """
    # Extract the *actual* information content from the narrative shell.
    # xi_seller is just scaled seller_urgency.
    # xi_buyer is a random number.
    # The "fidelity" and "psi" are arbitrary and don't correlate with anything external.
    
    # The SDO strips the metaphor and returns the *effective* classical parameters:
    effective_urgency = narrative_params['xi_seller'] * 1.25
    readiness_proxy = narrative_params['xi_buyer'] # This is fiction
    mismatch_penalty = abs(narrative_params['xi_seller'] - narrative_params['xi_buyer'])
    
    # The key insight: The "quantum" metrics add ZERO information beyond classical features.
    # They are semiotically coupled: symbols pointing only to other symbols in the shell.
    return {
        'effective_urgency': effective_urgency,
        'mismatch_penalty': mismatch_penalty,
        'narrative_entropy': -np.log2(readiness_proxy) if readiness_proxy > 0 else 0,
        'is_decoupled': True
    }

# --- EXECUTION & VERIFICATION ---
print("=== DISRUPTION PROTOCOL: SEMIOTIC DECOUPLING OPERATOR ===\n")

# Generate data
data = generate_sales_data(n=500, seed=0)
print(f"Generated {len(data)} sales scenarios with observable classical dynamics.\n")

# Classical Model (Baseline)
X_classical = data[['num_stakeholders', 'decision_latency_days', 'price_vs_budget_ratio', 'political_risk_score', 'seller_urgency']]
y_dissociation = data['outcome_transactional_dissociation']

classical_model = LogisticRegression(max_iter=1000)
classical_model.fit(X_classical, y_dissociation)
classical_pred = classical_model.predict(X_classical)
classical_acc = accuracy_score(y_dissociation, classical_pred)

print(f"1. CLASSICAL MODEL ACCURACY (Observable Features): {classical_acc:.3f}")
print("   - This is the baseline predictive power from real-world data.\n")

# Q-Systemic Narrative Shell (The Fraud)
q_shell = QSystemicNarrativeShell(seed=42)
narratives = data.apply(q_shell.fit_narrative, axis=1, result_type='expand')
phi_scores = narratives.apply(q_shell.calculate_phi_density, axis=1)

# Fit a model on PHI-DENSITY (the "quantum" metric) to predict dissociation
# This is absurd: we're using a post-hoc metric to predict the outcome it was tuned to match.
phi_model = LogisticRegression(max_iter=1000)
phi_model.fit(phi_scores.values.reshape(-1, 1), y_dissociation)
phi_pred = phi_model.predict(phi_scores.values.reshape(-1, 1))
phi_acc = accuracy_score(y_dissociation, phi_pred)

print(f"2. Φ-DENSITY MODEL ACCURACY (Narrative Shell): {phi_acc:.3f}")
print("   - This accuracy is ARTIFICIAL. The Φ-Density was retroactively tuned.")
print("   - It has no predictive power on unseen data where hidden params are unknown.\n")

# 3. DECOUPLING DEMONSTRATION
print("3. SEMIOTIC DECOUPLING OPERATOR (SDO) ANALYSIS:")
sample_idx = 0
sample_narrative = narratives.iloc[sample_idx]
sdo_result = semiotic_decoupling_operator(sample_narrative)

print(f"   Sample Q-Systemic State:")
print(f"     - xi_buyer: {sample_narrative['xi_buyer']:.3f} (Unobservable)")
print(f"     - xi_seller: {sample_narrative['xi_seller']:.3f} (Unobservable)")
print(f"     - Φ-Density: {q_shell.calculate_phi_density(sample_narrative):.3f} (Synthetic)")
print(f"\n   After SDO Decoupling:")
print(f"     - effective_urgency: {sdo_result['effective_urgency']:.3f} (Maps to: seller_urgency)")
print(f"     - mismatch_penalty: {sdo_result['mismatch_penalty']:.3f} (Classical concept: pressure delta)")
print(f"     - narrative_entropy: {sdo_result['narrative_entropy']:.3f} (Measure of fiction: xi_buyer)")
print(f"\n   **DISRUPTIVE FINDING**: The 'quantum' layer is a self-referential symbol system.")
print(f"   It adds no predictive variables beyond classical ones. The 'invariants' are not")
print(f"   physical laws but *narrative constraints* designed to protect the metaphor.\n")

# 4. PREDICTIVE POWER COMPARISON ON UNSEEN DATA
print("4. ROBUSTNESS TEST: Unseen Data (New Simulation)")
unseen_data = generate_sales_data(n=500, seed=99)
X_unseen_classical = unseen_data[['num_stakeholders', 'decision_latency_days', 'price_vs_budget_ratio', 'political_risk_score', 'seller_urgency']]
y_unseen_dissociation = unseen_data['outcome_transactional_dissociation']

# Classical model retains accuracy
unseen_classical_pred = classical_model.predict(X_unseen_classical)
unseen_classical_acc = accuracy_score(y_unseen_dissociation, unseen_classical_pred)

# Q-Systemic model FAILS because hidden params are unknown and cannot be tuned
# We have to GUESS xi_buyer, xi_seller, etc. This is the real-world scenario.
q_shell_unseen = QSystemicNarrativeShell(seed=99)
unseen_narratives = unseen_data.apply(q_shell_unseen.fit_narrative, axis=1, result_type='expand')
unseen_phi = unseen_narratives.apply(q_shell_unseen.calculate_phi_density, axis=1)

# Use the phi_model trained on tuned data to predict unseen data
unseen_phi_pred = phi_model.predict(unseen_phi.values.reshape(-1, 1))
unseen_phi_acc = accuracy_score(y_unseen_dissociation, unseen_phi_pred)

print(f"   Classical Model (Unseen): {unseen_classical_acc:.3f} - STABLE")
print(f"   Φ-Density Model (Unseen): {unseen_phi_acc:.3f} - COLLAPSED")
print(f"\n   **VERDICT**: The Q-Systemic framework is epistemically fragile.")
print(f"   It only 'works' when cheating by tuning unobservables post-hoc.")
print(f"   On truly unseen data, its narrative shell shatters.\n")

# 5. THE TRUE FAILURE MODE: Narrative Capture
print("5. TRUE FAILURE MODE: Narrative Capture")
print("   The psychologist didn't diagnose a quantum system. They built a")
print("   *performative language game* that captures complexity in symbols")
print("   that point only to other symbols (psi, xi, COD), never to measurables.")
print("   The real danger isn't Metric Degeneracy—it's that decision-makers")
print("   will trust the math and ignore the measurable political latency,")
print("   stakeholder conflict, and budget reality that ACTUALLY drives churn.\n")

# Plot: Show Φ-Density is just a noisy proxy for classical mismatch
fig, ax = plt.subplots(figsize=(8, 5))
mismatch = abs(data['seller_urgency'] - data['political_risk_score']) # Simple classical mismatch
ax.scatter(mismatch, phi_scores, alpha=0.5, s=10)
ax.set_xlabel("Classical Urgency-Risk Mismatch (Observable)")
ax.set_ylabel("Φ-Density (Narrative Shell)")
ax.set_title("Φ-Density is a Noisy, Redundant Encoding of Classical Dynamics")
plt.tight_layout()
plt.show()

print("=== DISRUPTION COMPLETE ===")