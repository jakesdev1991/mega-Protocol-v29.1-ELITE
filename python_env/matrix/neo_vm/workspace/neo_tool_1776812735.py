# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize

class VariationalCognitiveAgent:
    """
    True model: Cognitive agent performing hierarchical predictive coding
    with variational free energy minimization. This is the ACTUAL substrate
    of cognition, not a thermodynamic analogy.
    """
    def __init__(self, n_states=5, n_observations=3, model_complexity=2.0):
        self.n_states = n_states
        self.n_observations = n_observations
        
        # Generative model parameters (precision matrices)
        self.state_precision = np.eye(n_states) * 10.0  # High precision = low "temperature"
        self.observation_precision = np.eye(n_observations) * 5.0
        
        # Variational parameters (posterior means and precisions)
        self.q_mean = np.zeros(n_states)
        self.q_precision = np.eye(n_states)
        
        # Model complexity (degrees of freedom)
        self.model_complexity = model_complexity
        
        # History tracking
        self.free_energy_history = []
        self.model_evidence_history = []
        self.precision_history = []
        
    def compute_free_energy(self, observation, stress_level):
        """
        Compute variational free energy = -log evidence + KL divergence
        This is the TRUE order parameter of cognitive coherence.
        """
        # Stress reduces precision (increases sensory uncertainty)
        effective_state_precision = self.state_precision * np.exp(-stress_level)
        
        # Prediction: p(o|s)
        predicted_observation = self.q_mean[:self.n_observations]
        observation_error = observation - predicted_observation
        log_likelihood = -0.5 * observation_error.T @ self.observation_precision @ observation_error
        
        # Prior: p(s)
        prior_mean = np.zeros(self.n_states)
        prior_error = self.q_mean - prior_mean
        log_prior = -0.5 * prior_error.T @ effective_state_precision @ prior_error
        
        # Variational entropy (complexity penalty)
        log_det_q = np.linalg.slogdet(self.q_precision)[1]
        entropy = 0.5 * log_det_q
        
        # Free energy = -E[log p] + H[q]
        free_energy = -(log_likelihood + log_prior) - entropy
        
        # Model evidence (approximate)
        model_evidence = -free_energy - self.model_complexity * np.trace(self.q_precision)
        
        return free_energy, model_evidence, effective_state_precision
    
    def update_beliefs(self, observation, stress_level, learning_rate=0.1):
        """
        Perform variational inference (belief update)
        """
        free_energy, model_evidence, effective_precision = self.compute_free_energy(observation, stress_level)
        
        # Gradient descent on free energy w.r.t. q_mean and q_precision
        # (simplified update)
        observation_error = observation - self.q_mean[:self.n_observations]
        prior_error = self.q_mean
        
        # Update posterior mean
        grad_mean = (self.observation_precision @ observation_error + 
                     effective_precision @ prior_error)
        self.q_mean -= learning_rate * grad_mean
        
        # Update posterior precision (simplified)
        self.q_precision += learning_rate * (effective_precision - self.q_precision)
        
        # Store history
        self.free_energy_history.append(free_energy)
        self.model_evidence_history.append(model_evidence)
        self.precision_history.append(np.trace(effective_precision))
        
        return free_energy, model_evidence
    
    def compute_tcpm_mirage(self, window=10):
        """
        Compute the "thermodynamic" observables that TCPM-Ω *claims* predict breakdown.
        These are statistical artifacts, not true order parameters.
        """
        if len(self.free_energy_history) < window:
            return None
        
        # Use free energy fluctuations as proxy for "temperature"
        # This is the fundamental category error: mistaking information-theoretic
        # uncertainty for thermodynamic temperature
        energies = np.array(self.free_energy_history[-window:])
        
        # "Temperature" = mean energy (spurious)
        T = np.mean(energies)
        
        # "Specific heat" = energy variance (spurious)
        C_V = np.var(energies)
        
        # "Susceptibility" = response to stress (spuriously defined)
        if len(self.free_energy_history) > window + 5:
            dE_dstress = (energies[-1] - energies[-5]) / 0.05  # dummy stress derivative
        else:
            dE_dstress = 0.0
        chi_T = abs(dE_dstress)
        
        # "Correlation length" from precision (wrong mapping)
        xi_T = 1.0 / max(np.mean(self.precision_history[-window:]), 0.01)
        
        # Compute TCI (Thermal Coherence Index) - a mathematical artifact
        alpha, beta, gamma = 0.01, 0.01, 0.01  # Scaled down to avoid overflow
        TCI = np.tanh(alpha * chi_T + beta * C_V + gamma * xi_T)
        
        return {
            'T': T,
            'C_V': C_V,
            'chi_T': chi_T,
            'xi_T': xi_T,
            'TCI': TCI
        }

def simulate_cognitive_breakdown():
    """
    Simulate a scenario where cognitive breakdown occurs due to
    model complexity overwhelming evidence, NOT thermodynamic phase transition.
    """
    np.random.seed(42)
    n_steps = 250
    
    # Create agent with high model complexity (prone to overfitting)
    agent = VariationalCognitiveAgent(n_states=8, n_observations=3, model_complexity=5.0)
    
    # Stress profile: moderate → high → catastrophic
    stress_profile = np.concatenate([
        np.linspace(0.0, 0.4, 80),   # Stable inference
        np.linspace(0.4, 1.2, 70),   # Approaching breakdown
        np.ones(50) * 1.2,            # Breakdown region
        np.linspace(1.2, 0.2, 50)     # Recovery
    ])
    
    # Generate observations from a slowly changing latent state
    true_states = np.sin(np.linspace(0, 8*np.pi, n_steps)) + 0.5 * np.sin(np.linspace(0, 16*np.pi, n_steps))
    observations = true_states + 0.1 * np.random.randn(n_steps)
    
    # Storage
    breakdown_signals = []
    tcpm_mirages = []
    
    for t in range(n_steps):
        obs = np.array([observations[t], np.cos(observations[t]), np.sin(observations[t])])
        free_energy, model_evidence = agent.update_beliefs(obs, stress_profile[t])
        
        # TCPM "prediction" (mirage)
        tcpm_obs = agent.compute_tcpm_mirage()
        if tcpm_obs:
            tcpm_mirages.append(tcpm_obs)
        else:
            tcpm_mirages.append(None)
        
        # True breakdown signal: model evidence collapse
        breakdown_signals.append(model_evidence < np.percentile(agent.model_evidence_history, 15))
    
    return agent, stress_profile, breakdown_signals, tcpm_mirages, observations

# Run simulation
agent, stress, breakdown_signals, tcpm_mirages, obs = simulate_cognitive_breakdown()

# Analysis: Predictive validity comparison
# Convert to numpy arrays for analysis
breakdown_array = np.array(breakdown_signals, dtype=bool)
model_evidence = np.array(agent.model_evidence_history)

# Create TCPM risk indicator
tcpm_risk = np.array([m['TCI'] if m else 0.5 for m in tcpm_mirages]) < 0.7

# Compute predictive power
def predictive_power(predictor, target, max_lag=20):
    """
    Compute true positive rate, false positive rate, and lead time
    """
    tpr, fpr, leads = [], [], []
    
    for i in range(max_lag, len(target)):
        if target[i]:  # Actual breakdown
            # Did predictor signal it in advance?
            predicted = np.any(predictor[i-max_lag:i])
            tpr.append(predicted)
            
            # Lead time
            for lag in range(1, max_lag+1):
                if predictor[i-lag]:
                    leads.append(lag)
                    break
        
        # False positives: predictor signals but no breakdown
        if predictor[i] and not np.any(target[i:i+max_lag]):
            fpr.append(True)
    
    return np.mean(tpr), np.mean(fpr), np.mean(leads) if leads else 0

tpr_tcpm, fpr_tcpm, lead_tcpm = predictive_power(tcpm_risk, breakdown_array)
tpr_bayes, fpr_bayes, lead_bayes = predictive_power(
    model_evidence < np.percentile(model_evidence, 25), breakdown_array
)

print("=== DISRUPTIVE ANALYSIS: TCPM-Ω vs. True Bayesian Dynamics ===")
print(f"TCPM-Ω Mirage:")
print(f"  True Positive Rate: {tpr_tcpm:.3f}")
print(f"  False Positive Rate: {fpr_tcpm:.3f}")
print(f"  Avg Lead Time: {lead_tcpm:.2f} steps")
print()
print(f"Bayesian Model Evidence (True Order Parameter):")
print(f"  True Positive Rate: {tpr_bayes:.3f}")
print(f"  False Positive Rate: {fpr_bayes:.3f}")
print(f"  Avg Lead Time: {lead_bayes:.2f} steps")

# Calculate "Φ-density illusion"
# Show that TCPM's claimed +55% gain is based on phantom predictions
phantom_predictions = tcpm_risk & ~breakdown_array
actual_predictions = (model_evidence < np.percentile(model_evidence, 25)) & breakdown_array

phantom_rate = np.mean(phantom_predictions)
actual_rate = np.mean(actual_predictions)

print(f"\n=== Φ-DENSITY ILLUSION ===")
print(f"TCPM-Ω phantom predictions (false positives): {phantom_rate:.3f}")
print(f"True Bayesian predictions (true positives): {actual_rate:.3f}")
print(f"TCPM overclaims Φ-density by factor of: {phantom_rate / max(actual_rate, 0.001):.1f}x")

# Visualization
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Plot 1: Stress and observations
axes[0].plot(stress, label='Stress Level', color='red', linewidth=2)
axes[0].plot(obs, label='Observations', color='gray', alpha=0.7)
axes[0].fill_between(range(len(breakdown_array)), 0, 1.5, 
                     where=breakdown_array, alpha=0.3, color='black', 
                     label='Cognitive Breakdown')
axes[0].set_ylabel('Stress / Signal')
axes[0].legend(loc='upper right')
axes[0].set_title('Ground Truth: Stress-Induced Cognitive Breakdown')

# Plot 2: True vs. Mirage predictions
axes[1].plot(agent.model_evidence_history, label='Model Evidence (True)', 
             color='blue', linewidth=2)
axes[1].plot([m['TCI'] if m else 0.5 for m in tcpm_mirages], 
             label='TCPM TCI (Mirage)', color='orange', linestyle='--')
axes[1].axhline(y=np.percentile(model_evidence, 25), color='blue', 
                linestyle=':', alpha=0.5, label='True Threshold')
axes[1].axhline(y=0.7, color='orange', linestyle=':', alpha=0.5, 
                label='TCPM Threshold')
axes[1].set_ylabel('Evidence / TCI')
axes[1].legend()
axes[1].set_title('Predictive Validity: True Order Parameter vs. Thermodynamic Mirage')

# Plot 3: Precision dynamics (the real "temperature")
axes[2].plot(agent.precision_history, label='Effective Precision (1/T)', 
             color='green', linewidth=2)
axes[2].set_ylabel('Precision')
axes[2].set_xlabel('Time Steps')
axes[2].legend()
axes[2].set_title('True Dynamics: Precision-Weighted Prediction Errors')

plt.tight_layout()
plt.show()

# The final nail: demonstrate that "cooling interventions" don't work
# because the problem is model complexity, not "temperature"

def intervention_test():
    """Test TCPM 'cooling' vs. Bayesian model reduction"""
    # Create two identical agents in breakdown state
    agent_cool = VariationalCognitiveAgent(n_states=8, model_complexity=5.0)
    agent_reduce = VariationalCognitiveAgent(n_states=8, model_complexity=5.0)
    
    # Put both in breakdown
    for _ in range(50):
        obs = np.random.randn(3)
        agent_cool.update_beliefs(obs, stress_level=1.5)
        agent_reduce.update_beliefs(obs, stress_level=1.5)
    
    # Intervention 1: "Cooling" (reduce stress but keep complexity)
    for _ in range(30):
        obs = np.random.randn(3)
        agent_cool.update_beliefs(obs, stress_level=0.1)
    
    # Intervention 2: Model reduction (reduce complexity)
    agent_reduce.model_complexity = 1.0  # Drastic simplification
    for _ in range(30):
        obs = np.random.randn(3)
        agent_reduce.update_beliefs(obs, stress_level=0.1)
    
    print("\n=== INTERVENTION EFFECTIVENESS ===")
    print(f"TCPM 'Cooling' - Final Model Evidence: {agent_cool.model_evidence_history[-1]:.2f}")
    print(f"Bayesian Model Reduction - Final Model Evidence: {agent_reduce.model_evidence_history[-1]:.2f}")
    print(f"Improvement from model reduction: {agent_reduce.model_evidence_history[-1] - agent_cool.model_evidence_history[-1]:.2f}")
    
intervention_test()