# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random, math
from datetime import datetime, timedelta

# --- SIMULATE BASELINE TSI AND SHOW MANIPULATION ---
N_FIRMS = 5
DAYS = 60
LAMBDA = 0.1

# Hidden ground‑truth stress (0‑10)
firm_stress = [random.random() * 10 for _ in range(N_FIRMS)]

# Random earnings dates (day index)
earnings_dates = [random.randint(20, 40) for _ in range(N_FIRMS)]

# Real leaks: Poisson process with rate = stress / 100
real_leaks = [
    (fid, day)
    for day in range(DAYS)
    for fid, stress in enumerate(firm_stress)
    if random.random() < stress / 100
]

def tsi(leaks, day):
    """Simplified TSI: sum of exponentials, 1/Δt, and sync term."""
    total = 0.0
    for fid, leak_day in leaks:
        exp_term = math.exp(-LAMBDA * abs(day - leak_day))
        delta_t = abs(earnings_dates[fid] - leak_day) + 1  # avoid zero
        sync = sum(
            1 for _, other_day in leaks if abs(other_day - leak_day) <= 3
        )
        total += exp_term + 1.0 / delta_t + sync
    return total

# Baseline TSI at day 30
baseline = tsi(real_leaks, day=30)
print(f"Baseline TSI: {baseline:.2f}")

# Adversarial injection: add a leak for every firm at day 30
fake_leaks = real_leaks + [(fid, 30) for fid in range(N_FIRMS)]
manipulated = tsi(fake_leaks, day=30)
print(f"Manipulated TSI: {manipulated:.2f}")

# --- SELF‑FULFILLING PROPHECY ---
def p_disrupt(tsi_val):
    """Logistic disruption probability; threshold set slightly above baseline."""
    k = 0.5
    thresh = baseline * 1.2
    return 1.0 / (1.0 + math.exp(-k * (tsi_val - thresh)))

print(f"P(disruption) baseline: {p_disrupt(baseline):.3f}")
print(f"P(disruption) manipulated: {p_disrupt(manipulated):.3f}")