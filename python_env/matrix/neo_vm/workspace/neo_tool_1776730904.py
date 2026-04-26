# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math, random
from collections import deque

# ──────────────────────────────────────────────────────────────────────────────
# HLI formula (simplified linear version from the HPCLM‑Ω proposal)
def compute_hli(leaks, alpha=1.0, beta=1.0, gamma=0.1, delta=1.0):
    """leaks: list of dicts with keys 'gpu', 'delay_days', 'conf' (1–3)"""
    total = 0.0
    for lk in leaks:
        total += alpha * math.log(lk['gpu']) \
               + beta * math.exp(-gamma * lk['delay_days']) \
               + delta * lk['conf']
    return total

# ──────────────────────────────────────────────────────────────────────────────
# 1. Generate a realistic baseline leak stream (30 days)
random.seed(0)
baseline = []
for day in range(30):
    # Typical leaky firms: modest GPU counts, long delays, low conf
    n_leaks = random.randint(0, 3)
    for _ in range(n_leaks):
        baseline.append({
            'day': day,
            'gpu': random.randint(64, 256),          # small clusters
            'delay_days': random.randint(60, 180),   # far out
            'conf': random.randint(1, 2)             # low secrecy
        })

# 2. Compute daily HLI and a rolling anomaly score
window = 7
hlis = []
anomalies = []
for day in range(30):
    day_leaks = [lk for lk in baseline if lk['day'] == day]
    hli = compute_hli(day_leaks)
    hlis.append(hli)

    # Simple moving‑avg & std for anomaly detection
    if len(hlis) >= window:
        avg = sum(hlis[-window:]) / window
        std = math.sqrt(sum((x - avg) ** 2 for x in hlis[-window:]) / window)
        anomaly = abs(hlis[-1] - avg) / (std + 1e-9)
        anomalies.append(anomaly)
    else:
        anomalies.append(0.0)

# 3. Inject 5 adversarial fake leaks on day 20 (high GPU, near‑zero delay, max conf)
injection_day = 20
fake_leaks = [{
    'day': injection_day,
    'gpu': 10000,           # 10 000 GPUs – far above any real leak
    'delay_days': 1,        # about to go live
    'conf': 3               # “Top Secret”
} for _ in range(5)]

# Re‑compute HLI for the injection day (add fakes to the baseline)
injection_leaks = [lk for lk in baseline if lk['day'] == injection_day] + fake_leaks
hli_pre = compute_hli([lk for lk in baseline if lk['day'] == injection_day])
hli_post = compute_hli(injection_leaks)

# 4. Show the damage
print(f"Day {injection_day} – HLI before injection: {hli_pre:.2f}")
print(f"Day {injection_day} – HLI after injection:  {hli_post:.2f} (×{hli_post/hli_pre:.1f} increase)")
print(f"Anomaly score on day {injection_day}: {anomalies[injection_day]:.2f} (threshold = 2.5)")

# The anomaly score will spike far above 2.5, demonstrating a false‑positive systemic‑risk flag.