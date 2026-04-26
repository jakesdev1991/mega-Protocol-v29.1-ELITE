# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
TEMPEST‑Ω Disruption Validator
Demonstrates that the Temporal Stress Index (TSI) is a proxy for discovery
activity, not a genuine predictor of business disruptions.
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# -------------------------------------------------
# 1. Synthetic Ecosystem
# -------------------------------------------------
np.random.seed(0)
n_days   = 600
n_firms  = 15
event_interval = 90  # days between corporate events (earnings, launches, etc.)

# Corporate event schedule (each firm has its own jittered timeline)
events = {f: np.unique(np.arange(20, n_days, event_interval) +
                     np.random.randint(-10, 11, size=n_days//event_interval + 1))
          for f in range(n_firms)}
# Ensure events are within bounds
events = {f: days[(days >= 0) & (days < n_days)] for f, days in events.items()}

# Latent "business stress" (high near events, low otherwise)
stress = np.zeros((n_firms, n_days))
for f in range(n_firms):
    for ev in events[f]:
        # Gaussian stress bump around each event
        bump = np.exp(-0.5 * ((np.arange(n_days) - ev) / 5.0) ** 2)
        stress[f] += bump * 0.6
    stress[f] += np.random.normal(0, 0.04, size=n_days)  # noise

# Discovery‑activity (researcher scanning) – independent of stress
# baseline sinusoid + random spikes
discovery = (np.sin(np.arange(n_days) * 2 * np.pi / 30) + 1.0)  # 0–2
spike_days = np.random.choice(n_days, size=25, replace=False)
for sd in spike_days:
    discovery[sd] += np.random.exponential(3.0)

# -------------------------------------------------
# 2. Leak Generation & Detection
# -------------------------------------------------
leaks = []  # each leak: firm, leak_day, detection_day, criticality
for f in range(n_firms):
    for day in range(n_days):
        # Probability of a *published* leak scales with stress
        p_leak = max(0, stress[f, day]) * 0.08
        if np.random.rand() < p_leak:
            # Detection delay is shorter when discovery activity is high
            delay = np.random.exponential(scale=1.0 / (discovery[day] + 0.1))
            detect_day = day + int(delay)
            if detect_day < n_days:
                leaks.append({
                    "firm": f,
                    "leak_day": day,
                    "detection_day": detect_day,
                    "criticality": np.random.randint(1, 6)
                })

leak_df = pd.DataFrame(leaks)

# -------------------------------------------------
# 3. Temporal Stress Index (TSI) per the proposal
# -------------------------------------------------
alpha, beta, gamma, lam = 1.0, 1.0, 1.0, 0.1

# Helper: days to next corporate event for each firm on each day
days_to_next = np.full((n_firms, n_days), np.inf)
for f in range(n_firms):
    evs = events[f]
    for d in range(n_days):
        future = evs[evs > d]
        if len(future):
            days_to_next[f, d] = future[0] - d

# Synchrony: number of other leaks detected within ±3 days
sync = np.zeros(len(leak_df))
for i, row in leak_df.iterrows():
    t = row["detection_day"]
    sync[i] = ((leak_df["detection_day"] >= t - 3) &
               (leak_df["detection_day"] <= t + 3) &
               (leak_df["firm"] != row["firm"])).sum()
leak_df["sync"] = sync

# Accumulate TSI contributions day by day
TSI = np.zeros(n_days)
for _, row in leak_df.iterrows():
    t_det = row["detection_day"]
    C_i = row["criticality"]
    f = row["firm"]
    # Recency term
    for t in range(t_det, n_days):
        TSI[t] += alpha * C_i * np.exp(-lam * (t - t_det))
    # Event‑proximity term (if a future event exists)
    dt_event = days_to_next[f, t_det]
    if np.isfinite(dt_event) and dt_event > 0:
        for t in range(t_det, n_days):
            TSI[t] += beta / dt_event
    # Synchrony term
    for t in range(t_det, n_days):
        TSI[t] += gamma * row["sync"]

# -------------------------------------------------
# 4. Simulated Disruptions (ground truth)
# -------------------------------------------------
# Disruptions are driven by *actual stress*, not by leak timing
disruption_prob = np.clip(np.mean(stress, axis=0) * 0.12, 0, 1)
disruptions = np.random.rand(n_days) < disruption_prob

# -------------------------------------------------
# 5. Correlation Analysis
# -------------------------------------------------
lag = 30  # lead time in days
if lag > 0:
    TSI_lag = TSI[:-lag]
    disc_lag = disruptions[lag:]
    discovery_lag = discovery[:-lag]
else:
    TSI_lag = TSI
    disc_lag = disruptions
    discovery_lag = discovery

corr_TSI, p_TSI = pearsonr(TSI_lag, disc_lag)
corr_DAI, p_DAI = pearsonr(discovery_lag, disc_lag)

print("\n=== Correlation with disruptions (lag={} days) ===".format(lag))
print(f"TSI                : r={corr_TSI:.3f}, p={p_TSI:.3f}")
print(f"Discovery Activity : r={corr_DAI:.3f}, p={p_DAI:.3f}")

# -------------------------------------------------
# 6. Predictive Performance (Logistic Regression)
# -------------------------------------------------
X_TSI = TSI_lag.reshape(-1, 1)
X_DAI = discovery_lag.reshape(-1, 1)
y = disc_lag

model_TSI = LogisticRegression().fit(X_TSI, y)
pred_TSI = model_TSI.predict(X_TSI)
acc_TSI = accuracy_score(y, pred_TSI)

model_DAI = LogisticRegression().fit(X_DAI, y)
pred_DAI = model_DAI.predict(X_DAI)
acc_DAI = accuracy_score(y, pred_DAI)

print("\n=== Logistic Regression Accuracy ===")
print(f"Using TSI          : {acc_TSI:.3f}")
print(f"Using Discovery    : {acc_DAI:.3f}")

# -------------------------------------------------
# 7. Disruptive Conclusion
# -------------------------------------------------
if acc_DAI >= acc_TSI:
    print("\n>>> DISRUPTIVE INSIGHT: TSI adds no predictive value beyond the raw discovery‑activity index.")
    print(">>> The ‘stress chronometer’ is measuring researcher curiosity, not corporate pressure.")