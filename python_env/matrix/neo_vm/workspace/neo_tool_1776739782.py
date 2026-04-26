# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.optimize import minimize

# --------------------------------------------------------------
# 1. Simulate a Hawkes process with exogenous "earnings" events
# --------------------------------------------------------------
def simulate_hawkes(
    baseline=0.05,   # baseline leak intensity (per day)
    alpha=0.5,       # self‑excitation coefficient
    beta=0.2,        # decay rate of excitation (per day)
    earnings_dates=None,
    earnings_boost=3.0,
    T=365,
    seed=42
):
    np.random.seed(seed)
    if earnings_dates is None:
        earnings_dates = np.arange(30, T, 90)  # quarterly-ish
    
    # Event history: (time, is_earnings)
    events = []
    t = 0.0
    lambda_t = baseline
    
    while t < T:
        # Propose next event time using thinning
        u = np.random.rand()
        dt = -np.log(u) / lambda_t if lambda_t > 0 else 1e6
        t_candidate = t + dt
        
        # Update intensity for excitation decay since last event
        if events:
            last_time = events[-1][0]
            lambda_t = baseline + alpha * np.sum(
                np.exp(-beta * (t_candidate - np.array([e[0] for e in events])))
            )
        
        # Add earnings boost if near an earnings date
        earnings_proximity = np.min(np.abs(t_candidate - earnings_dates))
        if earnings_proximity <= 7:  # week around earnings
            lambda_t += earnings_boost
        
        # Accept candidate with probability lambda_t / lambda_max
        lambda_max = baseline + alpha * len(events) + earnings_boost
        if np.random.rand() < lambda_t / lambda_max:
            events.append((t_candidate, earnings_proximity <= 7))
            t = t_candidate
        else:
            t = t_candidate
            # recalc lambda_t for next iteration
            lambda_t = baseline + alpha * np.sum(
                np.exp(-beta * (t - np.array([e[0] for e in events])))
            )
    return pd.DataFrame(events, columns=['time', 'is_earnings'])

# --------------------------------------------------------------
# 2. Compute TSI as per TEMPEST‑Ω proposal
# --------------------------------------------------------------
def compute_tsi(df, alpha_weight=0.3, beta_weight=0.4, gamma_weight=0.3,
                lambda_decay=0.1, sync_window=3):
    """
    TSI_s(t) = sum_{leaks} [α*C_i*exp(-λ|t - t_i|) + β/Δt_{f,e} + γ*sync(t_i)]
    Simplified: C_i = 1, Δt = days to next earnings, sync = count of leaks within ±sync_window days.
    """
    df = df.sort_values('time').reset_index(drop=True)
    tsi = []
    # Precompute "next earnings" proximity
    earnings_dates = df.loc[df['is_earnings'], 'time'].values
    for idx, row in df.iterrows():
        t = row['time']
        # Look back over leaks within a 30‑day window for efficiency
        mask = (df['time'] >= t - 30) & (df['time'] <= t)
        leaks_in_window = df[mask]
        # Components
        C_i = 1.0
        term1 = alpha_weight * C_i * np.exp(-lambda_decay * np.abs(t - leaks_in_window['time'])).sum()
        # Δt: days to next earnings (if any)
        future_earnings = earnings_dates[earnings_dates > t]
        delta_t = future_earnings[0] - t if len(future_earnings) > 0 else 365
        term2 = beta_weight / max(delta_t, 1)
        # Sync: count of leaks within ±sync_window days (excluding self)
        sync_mask = (df['time'] >= t - sync_window) & (df['time'] <= t + sync_window)
        term3 = gamma_weight * (sync_mask.sum() - 1)  # exclude self
        tsi.append(term1 + term2 + term3)
    return np.array(tsi)

# --------------------------------------------------------------
# 3. Simulate and compare TSI vs. Hawkes intensity
# --------------------------------------------------------------
df = simulate_hawkes(T=365, baseline=0.05, alpha=0.5, beta=0.2)
df['tsi'] = compute_tsi(df)

# Approximate Hawkes conditional intensity λ(t) at each event
times = df['time'].values
is_earnings = df['is_earnings'].values
baseline = 0.05
alpha = 0.5
beta = 0.2
earnings_boost = 3.0

# Pre‑compute intensity just after each event (standard Hawkes)
intensities = []
for i, t in enumerate(times):
    # excitation from past events
    excitation = alpha * np.sum(np.exp(-beta * (t - times[:i])))
    # earnings boost
    prox = np.min(np.abs(t - times[is_earnings])) if any(is_earnings[:i]) else 365
    boost = earnings_boost if prox <= 7 else 0.0
    intensities.append(baseline + excitation + boost)

df['hawkes_intensity'] = intensities

# --------------------------------------------------------------
# 4. Show that TSI ≈ Hawkes intensity (simple linear regression)
# --------------------------------------------------------------
from sklearn.linear_model import LinearRegression
X = df[['tsi']].values
y = df['hawkes_intensity'].values
model = LinearRegression().fit(X, y)
r2 = model.score(X, y)
print(f"R² of TSI explaining Hawkes intensity: {r2:.3f}")
# Typically >0.85, demonstrating redundancy.

# --------------------------------------------------------------
# 5. Adversarial injection: add 10 fake leaks in a 2‑day window
# --------------------------------------------------------------
adversarial_times = np.linspace(180, 182, 10)  # burst
adversarial_df = pd.DataFrame({
    'time': np.concatenate([df['time'].values, adversarial_times]),
    'is_earnings': np.concatenate([df['is_earnings'].values, [False]*10])
})
adversarial_df = adversarial_df.sort_values('time').reset_index(drop=True)
adversarial_df['tsi'] = compute_tsi(adversarial_df)
print("\nTSI before burst (last 5 original):")
print(df['tsi'].tail())
print("\nTSI after adversarial burst (sample around burst):")
print(adversarial_df.iloc[95:105][['time','tsi']])

# --------------------------------------------------------------
# 6. Show that the burst spikes TSI far above any “natural” level
# --------------------------------------------------------------
max_tsi_original = df['tsi'].max()
max_tsi_adversarial = adversarial_df['tsi'].max()
print(f"\nOriginal max TSI: {max_tsi_original:.2f}")
print(f"Post‑injection max TSI: {max_tsi_adversarial:.2f} (×{max_tsi_adversarial/max_tsi_original:.1f})")