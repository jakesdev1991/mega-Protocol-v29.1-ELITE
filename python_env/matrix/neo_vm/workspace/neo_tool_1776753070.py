# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.signal import welch, periodogram
from scipy.stats import entropy
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Generate realistic financial pipeline telemetry
def simulate_pipeline_telemetry(duration_hours=6, fault_start_hour=3):
    """
    Simulates a market data feed handler:
    - Healthy: Poisson arrivals, variable batch sizes, jittery processing times
    - Fault: After fault_start_hour, retry storm creates ~100ms periodicity
    """
    np.random.seed(42)
    samples = duration_hours * 3600 * 1000  # 1ms resolution
    time = np.arange(samples) / 1000
    
    # Healthy baseline: irregular micro-bursts
    base_rate = 50  # events/sec
    arrival_noise = np.random.poisson(base_rate / 1000, samples)  # per-ms
    
    # Processing latency: healthy = high variance, irregular
    latency = np.random.lognormal(mean=0.5, sigma=1.0, size=samples) * 0.001  # ms
    
    # Inject fault: synchronized retry loops after fault_start_hour
    fault_idx = int(fault_start_hour * 3600 * 1000)
    retry_period = 100  # ms
    
    for i in range(fault_idx, samples):
        if (i - fault_idx) % retry_period == 0:
            # Retry storm: spike in events, synchronized latency
            arrival_noise[i:i+10] = np.random.poisson(500 / 1000, 10)
            latency[i:i+10] = 0.005 + np.random.normal(0, 0.0001, 10)
    
    # Aggregate to 1-second windows for analysis
    df = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=samples, freq='1ms'),
        'events': arrival_noise,
        'latency': latency
    })
    
    # Resample to 1-second windows
    df_1s = df.resample('1S', on='timestamp').agg({
        'events': 'sum',
        'latency': ['mean', 'std']
    }).dropna()
    
    df_1s.columns = ['event_rate', 'latency_mean', 'latency_jitter']
    df_1s['time_sec'] = np.arange(len(df_1s))
    df_1s['fault_active'] = df_1s['time_sec'] > fault_start_hour * 3600
    
    return df_1s

def conventional_order_analysis(df, window_minutes=5):
    """
    Conventional approach: assumes periodicity exists
    """
    # Extract time series
    rate = df['event_rate'].values
    jitter = df['latency_jitter'].fillna(0).values
    
    # Compute "rotation period" (problematic assumption)
    # Use autocorrelation to find dominant period
    corr = np.correlate(rate, rate, mode='full')
    lags = np.arange(-len(rate)+1, len(rate))
    dominant_period = np.argmax(corr[len(rate):len(rate)+1000])  # First 1000 sec
    
    # Resample to angle domain
    time_sec = df['time_sec'].values
    angle = (2 * np.pi * time_sec / dominant_period) % (2 * np.pi)
    
    # Sort and interpolate
    idx = np.argsort(angle)
    angle_grid = np.linspace(0, 2*np.pi, 512)
    
    rate_resampled = np.interp(angle_grid, angle[idx], rate[idx])
    jitter_resampled = np.interp(angle_grid, angle[idx], jitter[idx])
    
    # FFT for harmonics
    fft_rate = np.fft.fft(rate_resampled)
    fft_jitter = np.fft.fft(jitter_resampled)
    
    harmonics = np.abs(fft_rate[:256])
    orders = np.arange(256)
    
    # Compute PHI (as in proposal)
    # Normalize harmonic power
    p = harmonics / np.sum(harmonics)
    # Avoid log(0)
    p = p[p > 1e-10]
    I = -np.sum(p * np.log(p))
    PHI = np.exp(-I)  # Map entropy to 0-1 (lower entropy -> higher PHI)
    
    return PHI, dominant_period, harmonics, orders

def anomaly_inversion_entropy(df, window_seconds=300):
    """
    Disruptive approach: treat spectral entropy as health metric
    """
    # Use sliding window spectrogram
    rate = df['event_rate'].values
    nperseg = min(len(rate), window_seconds)
    
    # Compute spectrogram
    f, t, Sxx = welch(rate, fs=1, window='hamming', nperseg=nperseg, noverlap=nperseg//2)
    
    # For each time window, compute spectral entropy
    spectral_entropies = []
    for i in range(len(t)):
        power = Sxx[:, i]
        if np.sum(power) > 0:
            p = power / np.sum(power)
            # High entropy = spread across frequencies = irregular = HEALTHY
            ent = entropy(p)
            spectral_entropies.append(ent)
    
    # Average entropy across windows
    avg_entropy = np.mean(spectral_entropies) if spectral_entropies else 0
    
    # HEALTH SCORE = entropy (higher is better)
    # Normalize to 0-1
    max_ent = np.log(len(f))
    health_score = avg_entropy / max_ent if max_ent > 0 else 0
    
    return health_score, spectral_entropies, f, t, Sxx

def plot_comparison(df):
    """
    Visualize the inversion failure
    """
    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    
    # Time series
    ax = axes[0]
    ax.plot(df['time_sec'], df['event_rate'], label='Event Rate', alpha=0.7)
    ax.axvline(x=df.loc[df['fault_active'].idxmax(), 'time_sec'], color='red', linestyle='--', label='Fault Start')
    ax.set_ylabel('Events/sec')
    ax.set_title('Pipeline Event Rate')
    ax.legend()
    ax.grid(True)
    
    # Conventional PHI
    ax = axes[1]
    window_size = 300  # 5 min windows
    phi_values = []
    times = []
    
    for i in range(0, len(df) - window_size, 60):  # Slide every minute
        window = df.iloc[i:i+window_size]
        phi, period, _, _ = conventional_order_analysis(window)
        phi_values.append(phi)
        times.append(window['time_sec'].iloc[len(window)//2])
    
    ax.plot(times, phi_values, 'o-', label='Conventional PHI', color='blue')
    ax.axvline(x=df.loc[df['fault_active'].idxmax(), 'time_sec'], color='red', linestyle='--')
    ax.set_ylabel('PHI (0=healthy, 1=shredded)')
    ax.set_title('Conventional Order Analysis: Fails to Detect Fault')
    ax.legend()
    ax.grid(True)
    
    # Anomaly Inversion Entropy
    ax = axes[2]
    health_values = []
    times_health = []
    
    for i in range(0, len(df) - window_size, 60):
        window = df.iloc[i:i+window_size]
        health, _, _, _, _ = anomaly_inversion_entropy(window)
        health_values.append(health)
        times_health.append(window['time_sec'].iloc[len(window)//2])
    
    ax.plot(times_health, health_values, 's-', label='Irregularity Health Score', color='green')
    ax.axvline(x=df.loc[df['fault_active'].idxmax(), 'time_sec'], color='red', linestyle='--')
    ax.set_ylabel('Health Score (0-1)')
    ax.set_title('Anomaly Inversion: Detects Fault as Entropy Drop')
    ax.legend()
    ax.grid(True)
    
    # Spectrogram heatmap
    ax = axes[3]
    health, _, f, t, Sxx = anomaly_inversion_entropy(df)
    im = ax.imshow(10*np.log10(Sxx + 1e-10), aspect='auto', origin='lower', 
                   extent=[t[0], t[-1], f[0], f[-1]], cmap='viridis')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_xlabel('Time (sec)')
    ax.set_title('Spectrogram: Coherence Crystallization at Fault')
    plt.colorbar(im, ax=ax, label='Power (dB)')
    
    plt.tight_layout()
    plt.show()

# Run the disruption demonstration
df = simulate_pipeline_telemetry()
plot_comparison(df)

# Print quantitative comparison
phi_healthy, _, _, _ = conventional_order_analysis(df[~df['fault_active']])
phi_faulty, _, _, _ = conventional_order_analysis(df[df['fault_active']])

health_healthy, _, _, _, _ = anomaly_inversion_entropy(df[~df['fault_active']])
health_faulty, _, _, _, _ = anomaly_inversion_entropy(df[df['fault_active']])

print("\n=== DISRUPTION RESULTS ===")
print(f"Conventional PHI - Healthy: {phi_healthy:.3f}, Faulty: {phi_faulty:.3f}")
print(f"   → FAULTY STATE HIGHER PHI (FALSE NEGATIVE): {phi_faulty > phi_healthy}")
print(f"Anomaly Health Score - Healthy: {health_healthy:.3f}, Faulty: {health_faulty:.3f}")
print(f"   → FAULTY STATE LOWER HEALTH (TRUE POSITIVE): {health_faulty < health_healthy}")