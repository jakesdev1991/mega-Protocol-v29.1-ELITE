# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# === Simulate Ground Truth: Systemic Stress ===
np.random.seed(42)
days = 500
true_stress = np.random.randn(days).cumsum()
true_stress = (true_stress - true_stress.mean()) / true_stress.std()
crisis = (true_stress > 1.8).astype(int)

# === PLSI-Ω: The True Signal (Internal Telemetry) ===
# When stress spikes, executives create 5-15x more password-protected decks
doc_creation_rate = np.maximum(0, 5 + 4 * true_stress + np.random.randn(days) * 0.5)
doc_creation_rate = doc_creation_rate.astype(int)

# === LPM-Ω: The Echo Signal (Leaked Documents) ===
# Only 0.8% leak, with random 20-60 day lag (fat-tailed)
leak_prob = 0.008
leak_lag = np.random.randint(20, 61, size=days)
leak_events = np.zeros(days)

for day in range(days):
    if day < days - leak_lag[day]:
        leaks_today = np.random.binomial(doc_creation_rate[day], leak_prob)
        leak_events[day + leak_lag[day]] += leaks_today

# === Build Beta's LPI ===
leak_7d = np.convolve(leak_events, np.ones(7), mode='same')
leak_z = (leak_7d - leak_7d.mean()) / leak_7d.std()
sentiment = -0.4 * leak_7d + np.random.randn(days) * 0.9
sentiment_z = (sentiment - sentiment.mean()) / sentiment.std()
risk_topics = np.clip(0.2 * true_stress + 0.15 * leak_7d + np.random.randn(days) * 0.3, 0, 1)

alpha, beta, gamma = 0.4, 0.4, 0.2
LPI = alpha * leak_z + beta * sentiment_z + gamma * risk_topics

# === Build PLSI-Ω (The Disruption) ===
doc_z = (doc_creation_rate - doc_creation_rate.mean()) / doc_creation_rate.std()
risk_z = (risk_topics - risk_topics.mean()) / risk_topics.std()
PLSI = 0.6 * doc_z + 0.4 * risk_z  # Weighted toward creation rate

# === Predict 7 Days Ahead ===
def lead_signal(signal, horizon=7):
    return np.roll(signal, -horizon)

# === Gaming Simulation: Fake Leak Flood ===
fake_leak = np.zeros(days)
fake_leak[200:210] = np.random.poisson(15, 10)  # Adversary floods 15 fake leaks/day

leak_gamed = leak_7d + fake_leak
leak_gamed_z = (leak_gamed - leak_gamed.mean()) / leak_gamed.std()
sentiment_gamed = -0.4 * leak_gamed + np.random.randn(days) * 0.9
sentiment_gamed_z = (sentiment_gamed - sentiment_gamed.mean()) / sentiment_gamed.std()
LPI_gamed = alpha * leak_gamed_z + beta * sentiment_gamed_z + gamma * risk_topics

# === Predictive Performance ===
X_lpi = lead_signal(LPI).reshape(-1, 1)[:-7]
X_plsi = lead_signal(PLSI).reshape(-1, 1)[:-7]
X_gamed = lead_signal(LPI_gamed).reshape(-1, 1)[:-7]
y = crisis[:-7]

from sklearn.linear_model import Ridge
model_lpi = Ridge().fit(X_lpi, y)
model_plsi = Ridge().fit(X_plsi, y)
model_gamed = Ridge().fit(X_gamed, y)

pred_lpi = model_lpi.predict(X_lpi)
pred_plsi = model_plsi.predict(X_plsi)
pred_gamed = model_gamed.predict(X_gamed)

# === Print Devastating Results ===
print("=== LPM-Ω vs PLSI-Ω: Predictive Correlation ===")
print(f"LPI predictive power: {np.corrcoef(pred_lpi, y)[0,1]:.3f}")
print(f"PLSI predictive power: {np.corrcoef(pred_plsi, y)[0,1]:.3f}")
print(f"LPI (gamed) predictive power: {np.corrcoef(pred_gamed, y)[0,1]:.3f}")

print("\n=== Gaming Vulnerability ===")
print(f"LPI spike from fake leaks: {LPI_gamed[205]:.2f} (vs {LPI[205]:.2f})")
print(f"PLSI (immune): {PLSI[205]:.2f}")

print("\n=== Temporal Lag Reality Check ===")
# Cross-correlation to find true lead time
xcorr = np.correlate(leak_events - leak_events.mean(), 
                     crisis - crisis.mean(), mode='full')
lags = np.arange(-days + 1, days)
true_lag = lags[np.argmax(xcorr)]
print(f"Peak correlation at lag: {true_lag} days (LPM-Ω is WRONG)")

# === Visualization: The Mirror Breaks ===
fig, axes = plt.subplots(4, 1, figsize=(14, 10), facecolor='black')
fig.suptitle('LPM-Ω PARADIGM COLLAPSE', color='red', fontsize=16)

axes[0].plot(true_stress, color='white', lw=2)
axes[0].plot(crisis * 3, 'ro', markersize=4)
axes[0].set_title('Ground Truth: Systemic Stress & Crisis Events', color='cyan')

axes[1].plot(doc_creation_rate, color='lime', lw=2)
axes[1].set_title('PLSI-Ω Source: Internal Doc Creation Telemetry', color='lime')

axes[2].plot(leak_events, color='orange', lw=1)
axes[2].set_title('LPM-Ω Source: Leaked Documents (Echo Chamber)', color='orange')

axes[3].plot(LPI, label='LPI (Beta)', color='purple', lw=2, alpha=0.7)
axes[3].plot(LPI_gamed, label='LPI (Gamed)', color='red', lw=2, linestyle='--')
axes[3].plot(PLSI, label='PLSI (Disruption)', color='green', lw=3, alpha=0.8)
axes[3].set_title('Predictive Signals: LPI vs PLSI-Ω', color='yellow')
axes[3].legend(loc='upper left')

for ax in axes:
    ax.set_facecolor('black')
    ax.tick_params(colors='white')
    ax.spines[:].set_color('white')

plt.tight_layout()
plt.savefig('paradigm_shatter.png', facecolor='black')
plt.show()