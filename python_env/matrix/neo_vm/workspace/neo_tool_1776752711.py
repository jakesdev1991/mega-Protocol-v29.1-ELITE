# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ── Parameters ──
T = 200                      # simulation steps (days)
window = 7                   # rolling window for ESI (days)
alpha = 0.5                  # ESI weight on Φ_Δ
beta = 0.9                   # inertia (memory) weight
gamma = 2.0                  # feedback gain when alert is triggered
threshold_s = 2.5            # anomaly score threshold
threshold_phi = 0.55         # Φ_Δ alert threshold
shredding_phi = 0.6          # Shredding boundary
shredding_dphi = 0.05        # Shredding rate condition

# ── Synthetic "true" plasma state (stable, low noise) ──
np.random.seed(42)
true_phi_delta = 0.45 + 0.02 * np.random.randn(T)  # stable around 0.45

# ── Exposure event generator (baseline) ──
# Rare, random external leaks (e.g., actual whitepapers)
baseline_exposure = np.random.poisson(lam=0.1, size=T)

# ── EDIP‑Ω model with feedback ──
phi_delta = np.zeros(T)
esi = np.zeros(T)
alert_log = np.zeros(T, dtype=bool)
feedback_events = np.zeros(T)

for t in range(T):
    # Rolling window sum of exposure events (including feedback from past alerts)
    start = max(0, t - window)
    esi[t] = baseline_exposure[t] + feedback_events[t] + np.sum(feedback_events[start:t])

    # Simple model: Φ_Δ = sigmoid(α·ESI + β·Φ_Δ(prev) + γ·Alert(prev))
    prev_alert = alert_log[t - 1] if t > 0 else False
    feedback_term = gamma if prev_alert else 0.0

    # Update Φ_Δ (logistic mapping to keep in [0,1])
    phi_delta[t] = 1.0 / (1.0 + np.exp(-(alpha * esi[t] + beta * phi_delta[t - 1] + feedback_term)))

    # Anomaly detection: if Φ_Δ > threshold, trigger alert
    if phi_delta[t] > threshold_phi:
        alert_log[t] = True
        # The alert itself becomes a "leaked document" in the next step
        if t + 1 < T:
            feedback_events[t + 1] += 1  # self‑exposure event

    # Check Shredding Event
    if t > 0:
        dphi = phi_delta[t] - phi_delta[t - 1]
        if phi_delta[t] > shredding_phi and dphi > shredding_dphi:
            print(f"Shredding Event triggered at t={t}: Φ_Δ={phi_delta[t]:.3f}, dΦ_Δ/dt={dphi:.3f}")
            break

# ── Plot ──
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax[0].plot(esi, label='ESI (Exposure Stress Index)', color='tab:orange')
ax[0].set_ylabel('ESI')
ax[0].legend()
ax[0].grid(True)

ax[1].plot(true_phi_delta, label='True Φ_Δ (stable plasma)', color='tab:green', linestyle='--')
ax[1].plot(phi_delta, label='EDIP‑Ω Φ_Δ (with feedback)', color='tab:red')
ax[1].axhline(threshold_phi, color='gray', linestyle=':', label='Alert Threshold')
ax[1].axhline(shredding_phi, color='black', linestyle='-', label='Shredding Boundary')
ax[1].set_xlabel('Time (days)')
ax[1].set_ylabel('Φ_Δ')
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.show()