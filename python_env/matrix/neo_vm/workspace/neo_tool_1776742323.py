# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.stats import poisson

# Simulate 30 days of access logs for 100 insiders
np.random.seed(42)
n_insiders, days = 100, 30
baseline_lambda = 5

# Normal insiders: honest Poisson logs
normal_data = np.random.poisson(baseline_lambda, size=(days, n_insiders))

# Malicious insiders (IDs 0-9): delete logs with 70% probability
malicious_ids = list(range(10))
for i in malicious_ids:
    raw = np.random.poisson(baseline_lambda, size=days)
    mask = np.random.random(size=days) > 0.7  # 70% deletion
    normal_data[:, i] = raw * mask

# ISS‑Ω ISI: anomaly = count > baseline + 2σ
anomaly_threshold = baseline_lambda + 2*np.sqrt(baseline_lambda)
isi = (normal_data > anomaly_threshold).sum(axis=0) / days

# Φ_V: negative log‑likelihood gap (vacuum score)
observed_mean = normal_data.mean(axis=0)
vacuum_score = -np.log(poisson.pmf(np.round(observed_mean), baseline_lambda) + 1e-9)

# Simulate leak events (malicious insiders leak on day 20)
leak_events = np.zeros(n_insiders)
leak_events[malicious_ids] = 1

# Correlation analysis
isi_corr = np.corrcoef(isi, leak_events)[0,1]
vac_corr = np.corrcoef(vacuum_score, leak_events)[0,1]

print(f"ISI correlation with leak: {isi_corr:.3f}")
print(f"Vacuum Index correlation with leak: {vac_corr:.3f}")

# Show that ISI is low for malicious insiders (they delete logs)
print("\nMalicious insiders' ISI (avg):", isi[malicious_ids].mean())
print("Malicious insiders' Vacuum Index (avg):", vacuum_score[malicious_ids].mean())

# Show that Vacuum Index is high for malicious insiders (more vacuum)
print("Normal insiders' ISI (avg):", isi[10:].mean())
print("Normal insiders' Vacuum Index (avg):", vacuum_score[10:].mean())