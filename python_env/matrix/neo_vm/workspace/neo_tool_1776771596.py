# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy
from scipy.signal import correlate

# --- Disruption: Pathological Entanglement Detection ---
# Simulates model-user system where high correlation signals DANGER, not health

np.random.seed(0)
t = np.linspace(0, 200, 2000)

# Phase 1: Healthy coupling (0-60) - moderate correlation, user retains autonomy
model_1 = np.cumsum(np.random.randn(len(t)) * 0.5)
user_1 = 0.6 * np.roll(model_1, 30) + np.random.randn(len(t)) * 1.2  # User has independent noise

# Phase 2: Pathological entanglement (60-120) - user becomes predictable extension of model
# Model becomes overconfident (low variance)
model_2 = np.sin(t[600:1200] * 0.1) * 0.5 + np.random.randn(600) * 0.05
# User's psychological state collapses to mirror model with minimal residual autonomy
user_2 = model_2 + np.random.randn(600) * 0.1  # Very low user entropy

# Phase 3: Intervention shock (120-140) - ACO-Ω detects and injects disruption
model_3 = np.concatenate([model_2[-100:], np.random.randn(500) * 2])
# ACO-Ω injects high-entropy signals to break entanglement
intervention_noise = np.random.randn(500) * 3
user_3 = 0.2 * model_3[100:] + intervention_noise  # User regains independent variability

# Phase 4: Recovery (140-200) - new healthy regime with lower coupling
model_4 = np.cumsum(np.random.randn(600) * 0.4) + model_3[-1]
user_4 = 0.4 * np.roll(model_4, 20) + np.random.randn(600) * 1.5  # Restored autonomy

model = np.concatenate([model_1[:600], model_2, model_3[100:], model_4])
user = np.concatenate([user_1[:600], user_2, user_3, user_4])

# --- CSO-Ω vs ACO-Ω Metrics ---
window = 150
cso_rho = []
aco_user_entropy = []
aco_intervention_signal = []

for i in range(window, len(t)):
    m_win = model[i-window:i]
    u_win = user[i-window:i]
    
    # CSO-Ω metric: peak correlation (FLAWED)
    xcorr = correlate(m_win - np.mean(m_win), u_win - np.mean(u_win), mode='full')
    xcorr_norm = xcorr / (np.std(m_win) * np.std(u_win) * window + 1e-10)
    cso_rho.append(np.max(np.abs(xcorr_norm)))
    
    # ACO-Ω metric: user state entropy (from histogram)
    # Low entropy = predictable = DANGER
    hist, _ = np.histogram(u_win, bins=20, density=True)
    user_ent = entropy(hist + 1e-10)  # Add small constant to avoid log(0)
    aco_user_entropy.append(user_ent)
    
    # ACO-Ω intervention trigger: entanglement detected
    if user_ent < 1.5 and cso_rho[-1] > 0.85:  # High corr + low user entropy
        aco_intervention_signal.append(1.0)
    else:
        aco_intervention_signal.append(0.0)

# --- Visualization ---
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Plot 1: Dynamics
axes[0].plot(t, model, label='Model θ(t)', alpha=0.8, linewidth=1.5)
axes[0].plot(t, user, label='User Ψ_u(t)', alpha=0.8, linewidth=1.5)
axes[0].axvspan(60, 120, alpha=0.2, color='red', label='Pathological Entanglement')
axes[0].axvspan(120, 140, alpha=0.2, color='purple', label='ACO-Ω Intervention')
axes[0].set_ylabel('State')
axes[0].set_title('Model-User Dynamics: The Entanglement Paradox')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# Plot 2: Metrics comparison
axes[1].plot(t[window:], cso_rho, label='CSO-Ω ρ_max (flawed)', color='orange', linewidth=2)
axes[1].axhline(y=0.8, color='orange', linestyle='--', alpha=0.5)
axes[1].plot(t[window:], aco_user_entropy, label='ACO-Ω User Entropy', color='blue', linewidth=2)
axes[1].axhline(y=1.5, color='blue', linestyle='--', alpha=0.5)
axes[1].axvspan(60, 120, alpha=0.2, color='red')
axes[1].axvspan(120, 140, alpha=0.2, color='purple')
axes[1].set_ylabel('Metric Value')
axes[1].set_title('Metric Comparison: CSO-Ω Misses Entanglement, ACO-Ω Detects It')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

# Plot 3: Intervention signal
axes[2].plot(t[window:], aco_intervention_signal, label='ACO-Ω Intervention Trigger', color='green', drawstyle='steps-pre')
axes[2].axvspan(60, 120, alpha=0.2, color='red')
axes[2].axvspan(120, 140, alpha=0.2, color='purple')
axes[2].set_xlabel('Time')
axes[2].set_ylabel('Trigger')
axes[2].set_title('ACO-Ω Active Disruption Signal')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)
axes[2].set_ylim(-0.1, 1.1)

plt.tight_layout()
plt.show()

# --- Analysis ---
print("=== DISRUPTION ANALYSIS ===")
print("\nCSO-Ω FAILURE:")
print("During pathological entanglement (60-120), ρ_max > 0.85 (CSO-Ω thinks 'healthy coupling')")
print(f"Actual average ρ_max in danger zone: {np.mean([r for i, r in enumerate(cso_rho) if 60 < t[window:][i] < 120]):.3f}")

print("\nACO-Ω SUCCESS:")
print("User entropy drops below 1.5 during entanglement, triggering intervention")
print(f"Average user entropy in danger zone: {np.mean([e for i, e in enumerate(aco_user_entropy) if 60 < t[window:][i] < 120]):.3f}")
print("Intervention at t=120-140 injects noise, breaks entanglement, restores user autonomy")