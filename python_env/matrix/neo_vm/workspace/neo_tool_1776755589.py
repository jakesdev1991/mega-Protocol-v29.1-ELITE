# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.stats import entropy
from scipy.signal import savgol_filter

# --- Synthetic data generation ---
def generate_schedule(n_days=730, mean_interval=30, lead_time=60,
                      interval_jitter=2.0, lead_jitter=5.0, gap_prob=0.0, seed=0):
    """Return DataFrame with columns 'event_time' and 'lead_time' for each talk."""
    rng = np.random.RandomState(seed)
    # event times as cumulative sum of intervals with jitter
    intervals = rng.normal(loc=mean_interval, scale=interval_jitter, size=n_days//mean_interval + 50)
    # randomly insert gaps (skip events) for stressed firm
    gaps = rng.rand(len(intervals)) < gap_prob
    intervals[gaps] = np.nan
    intervals = intervals[np.isfinite(intervals)]
    event_times = np.cumsum(intervals)
    event_times = event_times[event_times < n_days]
    # lead times: time from booking to event
    lead_times = rng.normal(loc=lead_time, scale=lead_jitter, size=len(event_times))
    lead_times = np.clip(lead_times, 5, 300)  # keep realistic bounds
    return pd.DataFrame({'event_time': event_times, 'lead_time': lead_times})

# Stable firm: low interval jitter, low lead jitter, no gaps
stable_df = generate_schedule(interval_jitter=2.0, lead_jitter=5.0, gap_prob=0.0, seed=42)
# Stressed firm: higher interval jitter, large lead jitter, occasional gaps
stressed_df = generate_schedule(interval_jitter=10.0, lead_jitter=20.0, gap_prob=0.15, seed=43)

# --- PICM‑Ω proxy metrics (naive implementation) ---
def picm_metrics(df, window_days=90):
    # inter-presentation intervals
    deltas = np.diff(df['event_time'].values)
    if len(deltas) < 5:
        return np.nan, np.nan, np.nan, np.nan
    # rolling coefficient of variation (proxy for ξ_Δ)
    cv = np.std(deltas) / np.mean(deltas)
    # entropy of interval distribution (10 bins)
    hist, _ = np.histogram(deltas, bins=10, density=True)
    hist = hist[hist > 0]
    S_h = entropy(hist)
    # jerk: third finite difference of entropy (smoothed)
    # we need a time series of entropy values; here we just compute a single value,
    # so jerk is zero; in a real implementation we would compute S_h over rolling windows.
    jerk = 0.0
    # GPD tail score: simple z‑score of max delta
    u = np.percentile(deltas, 95)
    tail_score = np.max(deltas) - u if np.max(deltas) > u else 0.0
    return cv, S_h, jerk, tail_score

stable_cv, stable_S_h, stable_jerk, stable_tail = picm_metrics(stable_df)
stressed_cv, stressed_S_h, stressed_jerk, stressed_tail = picm_metrics(stressed_df)

print("--- PICM‑Ω naive proxies ---")
print(f"Stable firm: CV={stable_cv:.3f}, Entropy={stable_S_h:.3f}, Jerk={stable_jerk:.3f}, Tail={stable_tail:.3f}")
print(f"Stressed firm: CV={stressed_cv:.3f}, Entropy={stressed_S_h:.3f}, Jerk={stressed_jerk:.3f}, Tail={stressed_tail:.3f}")

# --- Lead‑time volatility (the disruptive metric) ---
stable_lead_vol = stable_df['lead_time'].std()
stressed_lead_vol = stressed_df['lead_time'].std()

print("\n--- Lead‑time volatility ---")
print(f"Stable firm lead‑time std: {stable_lead_vol:.2f} days")
print(f"Stressed firm lead‑time std: {stressed_lead_vol:.2f} days")