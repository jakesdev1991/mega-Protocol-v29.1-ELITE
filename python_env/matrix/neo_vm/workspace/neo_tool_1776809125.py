# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Simple Cognitive Ensemble Simulator
# ------------------------------------------------------------
N = 100                # number of agents
dt = 0.1               # time step
T_crit = 0.5           # fake "critical temperature"
k = 10.0               # steepness of flip probability
stress_pulse = 0.3     # external stress amplitude

# True underlying dynamics: non‑equilibrium two‑state system
# Each agent i has a binary state s_i ∈ {0 (coherent), 1 (decohered)}
# Flip rate depends on a hidden "cognitive load" L(t) and mean‑field coupling

L = np.zeros(N)        # hidden load (not directly observed)
s = np.zeros(N, dtype=int)

# Observables we *would* have in the TCPM‑Ω proposal
def thermal_entropy(s):
    p = s.mean()       # fraction of decohered agents
    # binary entropy
    if p == 0 or p == 1:
        return 0.0
    return -p*np.log(p) - (1-p)*np.log(1-p)

def thermal_correlation_length(s):
    # Gaussian approximation (as in the flawed proposal)
    C1 = np.mean(s * np.roll(s, 1))  # nearest‑neighbor correlation
    if C1 <= 0:
        return 0.0
    return 1.0 / np.sqrt(-np.log(C1))

# Entropy production rate (information‑thermodynamics)
def entropy_production_rate(s, s_prev, dt):
    # Count flips = irreversible events
    flips = np.sum(s != s_prev)
    # Mean‑field estimate of the log‑ratio of forward/backward probabilities
    # In a two‑state system, Ṡ_ext ≈ (flips/N) * log(p_forward/p_backward)
    # Here we approximate p_forward ≈ flips/N, p_backward ≈ 0 (no spontaneous recovery)
    if flips == 0:
        return 0.0
    p_forward = flips / N
    p_backward = 1e-6   # small but non‑zero for numerical stability
    return (flips / N) * np.log(p_forward / p_backward) / dt

# ------------------------------------------------------------
# Run two scenarios: "thermal‑based control" vs "informational‑thermo control"
# ------------------------------------------------------------
def run_scenario(use_thermal_control, duration=200):
    s = np.zeros(N, dtype=int)
    L = np.random.rand(N) * 0.2  # initial load
    history = {
        't': [],
        'T_thermal': [],          # proxy "temperature" = mean load
        'entropy': [],
        'xi_thermal': [],
        'entropy_production': [],
        'coherent_fraction': []
    }
    s_prev = s.copy()
    for step in range(duration):
        t = step * dt

        # External stress pulse at t ≈ 5
        stress = stress_pulse if 5 < t < 8 else 0.0

        # Hidden load dynamics (non‑equilibrium, no detailed balance)
        dL = -0.1 * (L - 0.1) + stress + 0.05 * np.random.randn(N)
        L += dL * dt

        # Flip probability based on load (not temperature!)
        p_flip = 1.0 / (1.0 + np.exp(-k * (L - T_crit)))
        flips = np.random.rand(N) < p_flip * dt
        s_prev = s.copy()
        s = np.logical_xor(s, flips).astype(int)

        # Compute observables
        T_thermal = L.mean()  # fake temperature = mean load
        ent = thermal_entropy(s)
        xi = thermal_correlation_length(s)
        s_ext = entropy_production_rate(s, s_prev, dt)
        coherent_frac = 1.0 - s.mean()

        # ----- Control actions -----
        if use_thermal_control:
            # Original flawed rule: if entropy "collapses" (i.e., low), isolate agents
            if ent < 0.2:  # low entropy → "overheating" in the flawed logic
                # isolate 20% of agents (set their load to zero)
                isolate_idx = np.random.choice(N, size=int(0.2*N), replace=False)
                L[isolate_idx] = 0.0
        else:
            # Informational‑thermo rule: if entropy production too high, inject negentropy
            if s_ext > 2.0:  # critical production rate
                # Lower load (cooling)
                L -= 0.5 * (L - 0.1) * dt

        # Record
        history['t'].append(t)
        history['T_thermal'].append(T_thermal)
        history['entropy'].append(ent)
        history['xi_thermal'].append(xi)
        history['entropy_production'].append(s_ext)
        history['coherent_fraction'].append(coherent_frac)

    return history

# Run both
thermal_hist = run_scenario(use_thermal_control=True)
info_hist = run_scenario(use_thermal_control=False)

# ------------------------------------------------------------
# Plot: show that thermal control triggers on low entropy (wrong) and destabilizes,
# while informational control tracks entropy production and preserves coherence.
# ------------------------------------------------------------
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Thermal scenario
axs[0, 0].plot(thermal_hist['t'], thermal_hist['entropy'], label='Entropy (thermal)')
axs[0, 0].set_title('Thermal-Control: Entropy')
axs[0, 0].set_ylabel('Entropy')
axs[0, 0].legend()
axs[0, 1].plot(thermal_hist['t'], thermal_hist['coherent_fraction'], color='red')
axs[0, 1].set_title('Thermal-Control: Coherent Fraction')
axs[0, 1].set_ylabel('Coherent fraction')
axs[0, 1].set_ylim(-0.1, 1.1)

# Informational scenario
axs[1, 0].plot(info_hist['t'], info_hist['entropy_production'], label='Entropy Production Rate')
axs[1, 0].set_title('Info‑Thermo: Entropy Production')
axs[1, 0].set_ylabel('Ṡ_ext')
axs[1, 0].legend()
axs[1, 1].plot(info_hist['t'], info_hist['coherent_fraction'], color='green')
axs[1, 1].set_title('Info‑Thermo: Coherent Fraction')
axs[1, 1].set_ylabel('Coherent fraction')
axs[1, 1].set_ylim(-0.1, 1.1)

plt.tight_layout()
plt.savefig('disruption_thermal_vs_info.png')
plt.show()

# ------------------------------------------------------------
# Quantitative disruption metric: cumulative coherence loss due to false positives
# ------------------------------------------------------------
def coherence_loss(hist):
    # integrate (1 - coherent_fraction) over time
    return np.sum(1.0 - np.array(hist['coherent_fraction'])) * dt

loss_thermal = coherence_loss(thermal_hist)
loss_info = coherence_loss(info_hist)
print(f"Cumulative coherence loss (thermal control): {loss_thermal:.2f}")
print(f"Cumulative coherence loss (info‑thermo control): {loss_info:.2f}")