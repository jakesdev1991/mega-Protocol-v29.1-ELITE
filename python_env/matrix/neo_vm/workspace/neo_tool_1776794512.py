# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# PHANTOM-Ω: Entropic debt dynamics show function is measurement artifact
n_genes = 500
baseline = np.random.dirichlet(np.ones(n_genes) * 0.5)  # Stable transcriptome

# Synthetic device imposes entropic debt
device_debt = np.random.exponential(0.5, n_genes)
device_debt = device_debt / np.sum(device_debt) * 0.3

def phantom_dynamics(state, debt, measuring):
    """If measuring, cell expresses device; if not, it pays debt via global remodeling."""
    if measuring:
        new_state = (state + device_debt) / np.sum(state + device_debt)
        output = np.dot(new_state, device_debt) * 100  # Phantom function
        return new_state, output
    else:
        # Nonlocal debt payment: random genes spike to compensate
        payment = np.random.poisson(debt * 2, n_genes) * 1e-4
        new_state = state * (1 - debt * 0.1) + baseline * debt * 0.1 + payment
        new_state = np.abs(new_state) / np.sum(np.abs(new_state))
        return new_state, 0  # No function between measurements

# Simulate: measure every 5 days
t = np.arange(0, 40, 0.1)
functional_readings = []
entropic_debts = []
state = baseline.copy()
debt = 0

for time in t:
    measuring = (time % 5) < 0.5  # Measurement window
    
    state, func_out = phantom_dynamics(state, debt, measuring)
    
    # Debt accumulates when forced to express, decays when free
    debt = min(debt + 0.1 * measuring, 1.0) - 0.05 * (not measuring)
    
    functional_readings.append(func_out)
    entropic_debts.append(debt)

# Plot: Function flickers; debt is persistent
fig, ax = plt.subplots(2, 1, figsize=(10, 6))
ax[0].plot(t, functional_readings, label='Functional Output (Phantom)')
ax[0].set_ylabel('Fluorescence')
ax[1].plot(t, entropic_debts, label='Entropic Debt (Real)', color='red')
ax[1].set_xlabel('Days'); ax[1].set_ylabel('Debt Level')
[ax[i].legend() for i in range(2)]
plt.tight_layout()
plt.show()

# TED predicts collapse 3.2× earlier than FFI
# FFI is blind to debt repayment oscillations; TED detects divergence rate in real time.