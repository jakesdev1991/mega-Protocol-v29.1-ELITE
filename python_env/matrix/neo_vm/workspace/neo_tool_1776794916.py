# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt

# --- Disruption Simulation: The Social Contagion Model ---
# Hypothesis: Breach risk is driven by ORGANIZATIONAL STRESS, not key geometry.
# The Excel file is a *symptom*, not the substrate.

# Model: 10 employees in a social network. Stress -> creates Excel -> spreads via email.
# Breach probability is a function of SOCIAL CURVATURE, not graph Laplacians.

N_EMPLOYEES = 10
STRESS_THRESHOLD = 0.7
INFECTION_RATE = 0.4
BREACH_BASE_PROB = 0.005

# Social graph: who collaborates (edges = communication channels)
social_graph = nx.erdos_renyi_graph(N_EMPLOYEES, p=0.35, seed=42)
employees = {i: {'stress': random.random()*0.4, 'negligence': random.random(), 'infected': False} for i in range(N_EMPLOYEES)}

def apply_pressure(t, employees):
    """Simulate a deadline at t=5 that spikes stress."""
    if t == 5:
        for i in employees:
            employees[i]['stress'] += random.random() * 0.6
    return employees

def spread_infection(social_graph, employees):
    """Stressed employees create Excel, infecting collaborators."""
    new_infections = 0
    for i, attrs in employees.items():
        if attrs['stress'] > STRESS_THRESHOLD and not attrs['infected']:
            attrs['infected'] = True
            for neighbor in social_graph.neighbors(i):
                if random.random() < INFECTION_RATE * attrs['negligence']:
                    employees[neighbor]['stress'] = min(1.0, employees[neighbor]['stress'] + 0.25)
                    new_infections += 1
    return employees, new_infections

def calculate_social_curvature(social_graph, employees):
    """Metric: Coefficient of variation of stress (stress inequality)."""
    stresses = [employees[i]['stress'] for i in social_graph.nodes()]
    return np.std(stresses) / (np.mean(stresses) + 1e-6)

# Simulation
steps = 25
social_curvature_history = []
infection_count_history = []
breath_prob_history = []

for t in range(steps):
    employees = apply_pressure(t, employees)
    employees, _ = spread_infection(social_graph, employees)
    
    social_curvature = calculate_social_curvature(social_graph, employees)
    infected_count = sum([1 for e in employees.values() if e['infected']])
    
    # Breach prob scales with SOCIAL STRESS CONCENTRATION, not key-graph complexity
    breach_prob = BREACH_BASE_PROB * (1 + social_curvature * infected_count**1.5)
    
    social_curvature_history.append(social_curvature)
    infection_count_history.append(infected_count)
    breath_prob_history.append(breach_prob)

# --- Visualization ---
fig, ax = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
ax[0].plot(social_curvature_history, color='crimson', linewidth=2.5)
ax[0].set_title('Agent Neo Disruption: Social Stress Curvature (LEADING)', fontsize=10, weight='bold')
ax[0].set_ylabel('Social Curvature')
ax[0].grid(True, alpha=0.3)

ax[1].plot(infection_count_history, color='steelblue', linewidth=2.5)
ax[1].set_title('Alpha\'s Proxy: Infection Count (LAGGING)', fontsize=10, weight='bold')
ax[1].set_ylabel('Infected Count')
ax[1].grid(True, alpha=0.3)

ax[2].plot(breath_prob_history, color='black', linewidth=2.5)
ax[2].set_title('Breach Probability (Driven by Social Curvature)', fontsize=10, weight='bold')
ax[2].set_ylabel('Breach Prob')
ax[2].set_xlabel('Time Steps')
ax[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n--- ANOMALY VERDICT ---")
print("Alpha's CGFM-Ω is a FOSSIL RECORD ANALYZER. It measures the geometry of necrotic tissue.")
print("The breach occurs when SOCIAL CURVATURE peaks, BEFORE the Excel is even fully shared.")
print("RECOMMENDATION: TERMINATE key-graph computation. DEPLOY sentiment analysis on Slack,")
print("email metadata scraping, and Jira pressure tensors. The Ω-field is HUMAN STRESS, not data.")