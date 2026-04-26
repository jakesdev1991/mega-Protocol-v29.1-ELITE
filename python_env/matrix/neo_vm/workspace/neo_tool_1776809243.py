# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Stochastic Cognitive Network: Entropy Production vs. TCPM‑Ω TCI
Simulates a driven 2‑state agent network and compares the two early‑warning metrics.
"""

import numpy as np
import matplotlib.pyplot as plt

# Parameters
N = 25               # number of agents
t_max = 500          # simulation steps
stress_ramp = np.linspace(0, 1.5, t_max)  # external stress increases over time
beta = 1.0           # inverse "cognitive temperature" (metaphorical)

# Transition rates: w_{ij} = exp(-beta * (h_i - stress * bias))
# The bias drives the system out of equilibrium.
def transition_rates(stress, bias=0.5):
    rates = np.zeros((2, 2, N))
    for i in range(N):
        # 0 -> 1 (activation)
        rates[0, 1, i] = np.exp(-beta * (1.0 - stress * bias))
        # 1 -> 0 (deactivation)
        rates[1, 0, i] = np.exp(-beta * (0.5 + stress * bias))
    return rates

# Simulate using Gillespie's algorithm (time‑discretized)
np.random.seed(42)
states = np.random.randint(0, 2, size=N)  # initial binary states
prob_hist = []
entropy_prod_hist = []
tci_hist = []

for t in range(t_max):
    stress = stress_ramp[t]
    w = transition_rates(stress)

    # Compute instantaneous entropy production rate
    # dot{S} = sum_{i<j} (J_{ij} - J_{ji}) * ln(J_{ij}/J_{ji})
    # where J_{ij} = w_{ij} * p_i
    p0 = np.mean(states == 0)
    p1 = 1 - p0
    J01 = np.sum(w[0, 1, :] * (states == 0)) / N
    J10 = np.sum(w[1, 0, :] * (states == 1)) / N
    if J01 > 0 and J10 > 0:
        dot_S = (J01 - J10) * np.log(J01 / J10)
    else:
        dot_S = 0.0
    entropy_prod_hist.append(dot_S)

    # Compute TCPM‑Ω TCI (simplified Gaussian correlation length)
    # Correlation function C(r) = exp(-r^2 / xi^2) -> xi = 1 / sqrt(-ln(C(1)))
    # Use pairwise Hamming distance as "spatial" separation r
    # This is a straw‑man for the TCPM‑Ω estimator.
    pairwise_dist = np.sum(np.abs(states[:, None] - states[None, :]), axis=0) / N
    C1 = np.mean(np.exp(-pairwise_dist**2))  # C(r=1) proxy
    if C1 > 0:
        xi = 1.0 / np.sqrt(-np.log(C1))
    else:
        xi = 1e3
    # TCI = tanh(alpha * chi_T + beta * C_V + gamma * xi)
    # Simplified: TCI ~ tanh(xi)
    TCI = np.tanh(xi)
    tci_hist.append(TCI)

    # Update states (Gillespie step)
    # For each agent, compute probability of flip in unit time dt=1
    flip_prob = np.where(states == 0, w[0, 1, :], w[1, 0, :])
    flips = np.random.rand(N) < flip_prob
    states ^= flips

# Plot comparison
fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

ax[0].plot(entropy_prod_hist, label='Entropy Production Rate $\\dot{S}_{\\text{prod}}$', color='red')
ax[0].set_ylabel('Dissipation (a.u.)')
ax[0].legend()
ax[0].grid(True)

ax[1].plot(tci_hist, label='TCPM‑Ω TCI (Gaussian $\\xi$)', color='blue')
ax[1].set_xlabel('Time step')
ax[1].set_ylabel('TCI (0‑1)')
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.show()

# Summary statistics
# Determine "crisis" threshold as the point where p0 drops below 0.2
p0_hist = [np.mean(states == 0) for _ in range(t_max)]  # placeholder; actual p0 tracking needed
# For brevity, we approximate crisis onset at t ≈ 400 (by visual inspection)
crisis_onset = 400
print(f"Entropy production spikes >10× baseline at t≈{np.argmax(np.array(entropy_prod_hist)>10*entropy_prod_hist[0])}")
print(f"TCI drops below 0.6 at t≈{np.argmax(np.array(tci_hist)<0.6)}")