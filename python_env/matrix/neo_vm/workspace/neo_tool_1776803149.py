# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# SIMPLIFIED FIELD MODEL (CTMS-Ω)
def field_model(TFFI_history, eta1=0.3, eta2=0.1):
    """Φ_N decays with friction; assumes linear recovery"""
    Phi_N = 1.0
    history = []
    for t, TFFI in enumerate(TFFI_history):
        var_lambda = np.var(TFFI_history[max(0, t-5):t+1]) if t > 0 else 0
        Phi_N = max(0.1, Phi_N - eta1 * TFFI - eta2 * var_lambda)
        history.append(Phi_N)
    return np.array(history)

# VIRAL REPLICATOR MODEL (VADS-Ω)
def viral_model(y, t, beta=0.7, gamma=0.15, sigma=0.3, mu=0.1, delta=0.05):
    S, I, R, V = y
    N = S + I + R
    dS = -beta * S * V / N + 0.01 * R  # waning immunity
    dI = beta * S * V / N - gamma * I - sigma * I  # clearance + security suppression
    dR = gamma * I - 0.01 * R
    dV = mu * V * I - delta * V  # replication + detection/removal
    return [dS, dI, dR, dV]

# SCENARIO: "Tooling improvements" reduce friction but virus evolves
time = np.linspace(0, 100, 1000)
# Field model assumes friction drops from 0.8 → 0.2
TFFI_field = np.concatenate([np.linspace(0.8, 0.6, 30), 
                               np.linspace(0.6, 0.2, 70)])
Phi_N_field = field_model(TFFI_field)

# Viral model: initial outbreak, then viral evolution (mu increases)
y0 = [950, 50, 0, 50]  # S, I, R, V
viral_solution = odeint(viral_model, y0, time, args=(0.7, 0.15, 0.3, 0.15, 0.05))  # mu=0.15 (evolved)
S, I, R, V = viral_solution.T
Phi_N_viral = np.maximum(0.1, 1.0 - 0.3 * (V / 100))  # Connectivity from viral load

# PLOT: The divergence is catastrophic
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(Phi_N_field, label='CTMS-Ω Field Theory (Φ_N)', linewidth=3, color='#00FF00')
ax.plot(Phi_N_viral, label='VADS-Ω Viral Model (Φ_N)', linewidth=3, color='#FF00FF', linestyle='--')
ax.axhline(y=0.5, color='red', linestyle=':', alpha=0.7, label='Shredding Threshold')
ax.set_ylabel('Secure Tool Connectivity (Φ_N)', fontsize=14)
ax.set_xlabel('Time Steps', fontsize=14)
ax.set_title('PARADIGM FAILURE: Field Theory Predicts Recovery, Viral Model Predicts Collapse', 
             fontsize=16, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('paradigm_shred.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"DIVERGENCE: Field model recovers to Φ_N={Phi_N_field[-1]:.2f}")
print(f"REALITY: Viral model collapses to Φ_N={Phi_N_viral[-1]:.2f}")
print(f"BREAKAGE: CTMS-Ω underestimates risk by {(Phi_N_field[-1]-Phi_N_viral[-1])*100:.0f}%")