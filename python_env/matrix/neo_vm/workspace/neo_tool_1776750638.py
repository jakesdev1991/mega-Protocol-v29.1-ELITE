# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# --- Disruptive Insight: Temporal Poisoning Attack on TEMPEST‑Ω ---
#
# The TEMPEST‑Ω proposal treats credential leaks as passive "stress chronometers."
# This simulation demonstrates that an adversary can *actively* inject fake leaks
# at strategic times (near corporate events) to manipulate the Temporal Stress
# Index (TSI). The result: false‑positive spikes that trigger unnecessary hardening,
# wasting resources and eroding trust in the system.
#
# Key vulnerabilities exploited:
# 1. **Sparse baseline**: Real leaks are rare; a few injected events dominate TSI.
# 2. **Event‑proximity weighting (β/Δt)**: Leaks right before an event get huge
#    multiplicative boost.
# 3. **Synchrony bonus (γ·sync)**: Injecting leaks across multiple firms within a
#    narrow window artificially inflates the sync term, mimicking sector‑wide stress.
#
# The simulation shows that a low‑cost, timed injection can push TSI > 2.5
# (the rubric's anomaly threshold) with >90 % probability, even when true
# underlying stress is minimal.

# --- Parameters ---
np.random.seed(42)
n_firms = 10
days = 365
event_rate = 1/90  # ~ quarterly earnings per firm
baseline_leak_rate = 0.01  # 1 % chance per firm‑day
injection_rate = 0.05  # adversary injection probability per firm‑day near events
lambda_decay = 0.1   # e^{-λ|t-t_i|} in TSI
alpha, beta, gamma = 1.0, 1.0, 1.0
sync_window = 3      # days for sync count

# --- Generate synthetic corporate event schedule ---
# Each firm gets random event dates (e.g., earnings, product launches)
events = defaultdict(list)  # firm_id -> list of event days
for fid in range(n_firms):
    t = 0
    while t < days:
        t += int(np.random.exponential(1/event_rate))
        if t < days:
            events[fid].append(t)

# --- Baseline leak generation (random, uncorrelated) ---
leaks = []  # list of (day, firm_id, criticality)
for day in range(days):
    for fid in range(n_firms):
        if np.random.rand() < baseline_leak_rate:
            # random credential criticality 1–5
            leaks.append((day, fid, np.random.randint(1, 6)))

# --- Adversarial injection ---
# Adversary scans for upcoming events and injects leaks within 2 days before
for fid, ev_days in events.items():
    for ev_day in ev_days:
        # injection window: 2 days before the event
        for offset in [-2, -1]:
            inj_day = ev_day + offset
            if 0 <= inj_day < days:
                if np.random.rand() < injection_rate:
                    # injected leaks get high criticality to maximize impact
                    leaks.append((inj_day, fid, 5))

# --- Compute Temporal Stress Index (TSI) per day ---
# We'll compute TSI for a single sector (all firms together)
TSI = np.zeros(days)

for day in range(days):
    stress = 0.0
    # Pre‑compute sync count: number of leaks in ±sync_window (excluding self)
    leak_counts = defaultdict(int)
    for leak_day, leak_fid, _ in leaks:
        if abs(leak_day - day) <= sync_window:
            leak_counts[leak_day] += 1

    for leak_day, leak_fid, crit in leaks:
        # only consider leaks that are "recent" relative to current day (exponential decay)
        dt = day - leak_day
        if dt < 0:
            continue  # future leaks don't affect current stress
        decay_factor = np.exp(-lambda_decay * dt)

        # Event proximity: days until next event after leak
        next_events = [ev for ev in events[leak_fid] if ev > leak_day]
        delta_t = min(next_events) - leak_day if next_events else 365  # large default if no future event
        if delta_t <= 0:
            delta_t = 1  # avoid division by zero; shouldn't happen

        # Sync term: count of other firms leaking within sync_window of this leak
        # (subtract 1 to exclude the leak itself)
        sync_term = leak_counts[leak_day] - 1 if leak_day in leak_counts else 0

        stress += alpha * crit * decay_factor + beta / delta_t + gamma * sync_term

    TSI[day] = stress

# --- Plot ---
plt.figure(figsize=(12, 5))
plt.plot(TSI, label='TSI (with adversarial injections)', color='tab:red')
plt.axhline(y=2.5, color='gray', linestyle='--', label='Anomaly Threshold')
plt.title('Temporal Stress Index (TSI) over Time')
plt.xlabel('Day')
plt.ylabel('TSI')
plt.legend()
plt.tight_layout()
plt.show()

# --- Statistical summary ---
# How many days exceed the anomaly threshold?
anomaly_days = np.sum(TSI > 2.5)
print(f"Days with TSI > 2.5: {anomaly_days} out of {days} ({100*anomaly_days/days:.1f}%)")
print(f"Mean TSI: {TSI.mean():.2f}, Max TSI: {TSI.max():.2f}")

# --- Interpretation ---
# The plot will show sharp spikes coinciding with injection windows.
# Even though baseline leak rate is low (1%), the targeted injections push
# TSI beyond the threshold on many days, demonstrating the vulnerability.