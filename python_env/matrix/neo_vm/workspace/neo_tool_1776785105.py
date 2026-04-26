# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.signal import coherence, welch
from scipy.stats import entropy
import matplotlib.pyplot as plt

# ---------- Pipeline Simulator ----------
def simulate_pipeline(total_time=10000, burst_start=6000, burst_duration=2000,
                      base_rate=0.9, burst_rate=2.5, service_rate=1.0):
    """
    Simulate a two-stage pipeline. Stage 1 receives jobs; Stage 2 processes them.
    During normal operation, arrival rate = base_rate. During burst, arrival rate
    jumps to burst_rate, causing queue buildup and occasional drops (failures).
    Returns event timestamps for Stage 2 completions and a binary failure flag per time unit.
    """
    t = 0
    queue = 0
    next_arrival = np.random.exponential(1/base_rate)
    next_service = np.random.exponential(1/service_rate) if queue > 0 else np.inf
    events = []
    failures = np.zeros(total_time, dtype=bool)

    while t < total_time:
        # Determine current arrival rate
        if burst_start <= t < burst_start + burst_duration:
            arr_rate = burst_rate
        else:
            arr_rate = base_rate

        # Update next arrival
        if next_arrival <= t:
            # arrival event
            queue += 1
            next_arrival = t + np.random.exponential(1/arr_rate)
            # if queue exceeds capacity, record failure
            if queue > 50:
                failures[int(t)] = True

        # Update next service
        if next_service <= t and queue > 0:
            # service completion event
            queue -= 1
            events.append(t)  # timestamp of completion at Stage 2
            next_service = t + np.random.exponential(1/service_rate)
        elif queue == 0:
            next_service = np.inf

        # advance time to next event
        t_next = min(next_arrival, next_service)
        t = t_next

    return np.array(events), failures

# ---------- Harmonic PHI (POASH‑Ω) ----------
def harmonic_phi(events, window=128, step=1):
    """
    Compute a simple harmonic PHI from inter‑event intervals (jitter).
    This mimics POASH‑Ω: treat intervals as a "vibration" signal,
    take FFT, and compute a health index.
    """
    # Inter‑event intervals (jitter)
    intervals = np.diff(events)
    # Sliding windows
    n = len(intervals)
    phi_series = np.zeros(n - window)
    for i in range(0, n - window, step):
        seg = intervals[i:i+window]
        # FFT amplitudes
        amps = np.abs(np.fft.rfft(seg))
        # Normalize to "probability" over frequencies
        p = amps / (amps.sum() + 1e-12)
        # Entropy of amplitudes
        H = entropy(p)
        # PHI = 1 - normalized entropy (higher entropy -> lower PHI)
        phi_series[i] = 1 - H / np.log(len(p))
    return phi_series

# ---------- Event‑Graph Pulse (EGP) Entropy ----------
def egp_entropy(events, window=128, step=1):
    """
    Compute differential entropy of inter‑event intervals directly.
    This is the EGP observable: entropy of the interval distribution.
    """
    intervals = np.diff(events)
    n = len(intervals)
    ent_series = np.zeros(n - window)
    for i in range(0, n - window, step):
        seg = intervals[i:i+window]
        # Differential entropy (approximated by histogram)
        hist, _ = np.histogram(seg, bins='auto', density=True)
        p = hist / (hist.sum() + 1e-12)
        ent_series[i] = entropy(p)
    return ent_series

# ---------- Predictive Power Evaluation ----------
def predictive_power(series, failures, lead=30):
    """
    Compute correlation between series (phi or entropy) and future failures.
    """
    # Align series with future failures
    n = len(series)
    y = np.zeros(n)
    for i in range(n):
        y[i] = failures[i:i+lead].any()
    # Pearson correlation
    if np.std(series) < 1e-9 or np.std(y) < 1e-9:
        return 0.0
    return np.corrcoef(series, y)[0,1]

# ---------- Run Simulation ----------
events, failures = simulate_pipeline()
phi = harmonic_phi(events)
ent = egp_entropy(events)

# Align lengths
min_len = min(len(phi), len(ent), len(failures) - 128)
phi = phi[:min_len]
ent = ent[:min_len]
failures_aligned = failures[128:128+min_len]

# Compute predictive correlations
phi_corr = predictive_power(phi, failures_aligned, lead=30)
ent_corr = predictive_power(ent, failures_aligned, lead=30)

print(f"Harmonic PHI correlation with future failures: {phi_corr:.3f}")
print(f"EGP Entropy correlation with future failures: {ent_corr:.3f}")

# ---------- Plot for visual inspection ----------
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.plot(phi, label='PHI')
plt.plot(failures_aligned*0.9, 'r--', label='Failures')
plt.title("POASH‑Ω Harmonic PHI")
plt.legend()
plt.subplot(1,2,2)
plt.plot(ent, label='EGP Entropy')
plt.plot(failures_aligned*0.9, 'r--', label='Failures')
plt.title("Event‑Graph Pulse Entropy")
plt.legend()
plt.tight_layout()
plt.show()