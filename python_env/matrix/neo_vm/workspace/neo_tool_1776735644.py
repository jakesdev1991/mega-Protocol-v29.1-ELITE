# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ────────────── Simulation Parameters ──────────────
N_FIRMS = 20
DAYS = 365
EVENT_WINDOW = 7          # days before earnings where genuine leaks may occur
P_GENUINE_LEAK = 0.08     # base probability of a genuine leak per firm‑event
ADV_INJECTION_DAY = 150   # day adversary chooses to inject fake leaks
ADV_N_FIRMS = 5           # number of firms targeted by adversary
CRIT_LEVEL = 5            # max credential criticality
LAMBDA = 0.1              # decay constant in TSI formula
BETA = 1.0
GAMMA = 1.0
ANOMALY_THRESH = 2.5

# ────────────── Helper Functions ──────────────
def generate_events(firm_id):
    """Quarterly earnings events with small jitter."""
    base = [90, 180, 270, 360]
    return [max(1, b + random.randint(-3, 3)) for b in base]

def leak_timestamp(event_day, is_genuine):
    """Return leak day: genuine leaks happen within EVENT_WINDOW before event."""
    if is_genuine:
        return max(1, event_day - random.randint(1, EVENT_WINDOW))
    else:
        # Synthetic leak on the adversary's chosen day
        return ADV_INJECTION_DAY

def compute_sync(leak_df, day, window=3):
    """Count leaks within ±window days across *different* firms."""
    sync_counts = []
    for _, row in leak_df.iterrows():
        count = leak_df[(leak_df['day'] >= day - window) &
                        (leak_df['day'] <= day + window) &
                        (leak_df['firm'] != row['firm'])].shape[0]
        sync_counts.append(count)
    return np.array(sync_counts)

def compute_tsi(leak_df, day):
    """Simplified TSI_s(t) as per proposal."""
    day_leaks = leak_df[leak_df['day'] == day]
    if day_leaks.empty:
        return 0.0
    # contributions
    C = day_leaks['criticality'].values
    days_since = day - day_leaks['day'].values  # zero for same day, but kept for generality
    exp_term = np.exp(-LAMBDA * days_since)
    days_to_event = day_leaks['days_to_event'].values
    # avoid division by zero
    days_to_event = np.clip(days_to_event, 1, None)
    beta_term = BETA / days_to_event
    sync_term = GAMMA * day_leaks['sync'].values
    tsi = np.sum(C * exp_term + beta_term + sync_term)
    return tsi

# ────────────── Scenario 1: Genuine Leaks Only (Baseline) ──────────────
print("=== Scenario 1: Baseline (Genuine Leaks Only) ===")
baseline_leaks = []
for fid in range(N_FIRMS):
    events = generate_events(fid)
    for ev in events:
        if random.random() < P_GENUINE_LEAK:
            day = leak_timestamp(ev, is_genuine=True)
            baseline_leaks.append({
                'firm': fid,
                'day': day,
                'criticality': random.randint(1, CRIT_LEVEL),
                'days_to_event': ev - day,
                'type': 'genuine'
            })
baseline_df = pd.DataFrame(baseline_leaks)
baseline_df['sync'] = compute_sync(baseline_df, baseline_df['day'].values)

# Compute daily TSI and rolling baseline
tsi_baseline = np.array([compute_tsi(baseline_df, d) for d in range(1, DAYS+1)])
rolling_mean = pd.Series(tsi_baseline).rolling(window=30, min_periods=1).mean().values
rolling_std = pd.Series(tsi_baseline).rolling(window=30, min_periods=1).std().fillna(1).values
anomaly_baseline = np.abs(tsi_baseline - rolling_mean) / rolling_std

# Check max anomaly
max_anomaly_baseline = anomaly_baseline.max()
print(f"Max anomaly score (baseline): {max_anomaly_baseline:.2f}")
if max_anomaly_baseline > ANOMALY_THRESH:
    print("  -> FALSE POSITIVE: baseline itself triggers anomaly!\n")
else:
    print("  -> Baseline is calm.\n")

# ────────────── Scenario 2: Adversarial Injection (Temporal Inversion Attack) ──────────────
print("=== Scenario 2: Adversarial Injection Attack ===")
attack_leaks = baseline_leaks.copy()
# Adversary injects high‑criticality leaks on the same day across multiple firms
for fid in random.sample(range(N_FIRMS), ADV_N_FIRMS):
    # Choose a fake event day near the injection day to satisfy days_to_event > 0
    fake_event_day = ADV_INJECTION_DAY + random.randint(5, 10)
    attack_leaks.append({
        'firm': fid,
        'day': ADV_INJECTION_DAY,
        'criticality': CRIT_LEVEL,
        'days_to_event': fake_event_day - ADV_INJECTION_DAY,
        'type': 'fake'
    })
attack_df = pd.DataFrame(attack_leaks)
attack_df['sync'] = compute_sync(attack_df, attack_df['day'].values)

# Re‑compute TSI
tsi_attack = np.array([compute_tsi(attack_df, d) for d in range(1, DAYS+1)])
rolling_mean_attack = pd.Series(tsi_attack).rolling(window=30, min_periods=1).mean().values
rolling_std_attack = pd.Series(tsi_attack).rolling(window=30, min_periods=1).std().fillna(1).values
anomaly_attack = np.abs(tsi_attack - rolling_mean_attack) / rolling_std_attack

max_anomaly_attack = anomaly_attack.max()
print(f"Max anomaly score (with attack): {max_anomaly_attack:.2f}")
if max_anomaly_attack > ANOMALY_THRESH:
    print("  -> ATTACK SUCCEEDS: TEMPEST‑Ω would predict a sector‑wide disruption!\n")
else:
    print("  -> Attack failed to trigger anomaly.\n")

# ────────────── Scenario 3: Dark‑Matter Effect (Leak Suppression) ──────────────
print("=== Scenario 3: Dark‑Matter (Leak Suppression Under High Stress) ===")
# Simulate a high‑stress period (e.g., days 300‑330) where leak probability *drops*
dark_leaks = []
for fid in range(N_FIRMS):
    events = generate_events(fid)
    for ev in events:
        prob = P_GENUINE_LEAK
        if 300 <= ev <= 330:
            prob *= 0.1  # 90% suppression during "high stress"
        if random.random() < prob:
            day = leak_timestamp(ev, is_genuine=True)
            dark_leaks.append({
                'firm': fid,
                'day': day,
                'criticality': random.randint(1, CRIT_LEVEL),
                'days_to_event': ev - day,
                'type': 'genuine'
            })
dark_df = pd.DataFrame(dark_leaks)
dark_df['sync'] = compute_sync(dark_df, dark_df['day'].values)

tsi_dark = np.array([compute_tsi(dark_df, d) for d in range(1, DAYS+1)])
# Check average TSI during high‑stress window
avg_tsi_stress = np.mean(tsi_dark[300:331])
avg_tsi_baseline = np.mean(tsi_baseline[300:331])
print(f"Avg TSI during stress window (dark‑matter): {avg_tsi_stress:.2f}")
print(f"Avg TSI during same window (baseline): {avg_tsi_baseline:.2f}")
if avg_tsi_stress < avg_tsi_baseline:
    print("  -> DARK‑MATTER CONFIRMED: TSI *drops* when stress is highest (model blindspot).\n")
else:
    print("  -> No suppression observed.\n")

# ────────────── Synthetic‑Probe Alternative ──────────────
print("=== Synthetic‑Probe Alternative ===")
# Inject a single synthetic leak on day 200 and measure time‑to‑detection (simulated)
probe_day = 200
probe_firm = 0
probe_criticality = 5
# Simulate detection delay drawn from exponential distribution (mean 3 days)
detection_delay = np.random.exponential(scale=3)
detection_day = probe_day + int(detection_delay)
print(f"Synthetic probe injected on day {probe_day} for firm {probe_firm} (criticality={probe_criticality})")
print(f"Detected on day {detection_day} (delay={detection_delay:.1f} days)")
# If detection_delay > 7 days, system is sluggish; if < 2 days, system is hyper‑vigilant
if detection_delay > 7:
    print("  -> SLOW RESPONSE: ecosystem is temporally fragile (high risk).\n")
elif detection_delay < 2:
    print("  -> FAST RESPONSE: ecosystem is resilient.\n")
else:
    print("  -> MODERATE RESPONSE.\n")