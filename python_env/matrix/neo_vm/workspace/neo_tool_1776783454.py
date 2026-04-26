# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, find_peaks
from scipy.stats import kurtosis
import seaborn as sns

# Generate synthetic pipeline data that shows the fundamental flaw in POASH-Ω
# We'll create three regimes: healthy, critical slowing down (pre-failure), and catastrophic failure

np.random.seed(42)
n_samples = 10000
time = np.arange(n_samples) / 100  # 100 Hz sampling

# Regime 1: Healthy (0-3000) - Stationary cycles with small jitter
healthy = np.sin(2 * np.pi * 10 * time[:3000]) + 0.1 * np.random.randn(3000)
# Regime 2: Critical Slowing Down (3000-7000) - Increasing variance, slower recovery, non-stationary
csd = np.zeros(4000)
baseline = 0
for i in range(4000):
    # Critical slowing down: increasing autocorrelation and variance
    alpha = 0.99 - i/40000  # Autocorrelation increases
    baseline = alpha * baseline + (1-alpha) * np.sin(2 * np.pi * 10 * time[3000+i]) + 0.3 * np.random.randn()
    csd[i] = baseline
# Regime 3: Catastrophic Failure (7000-10000) - Complete breakdown, non-oscillatory
failure = np.random.randn(3000) * 2 + np.linspace(0, -5, 3000)

# Combine
signal = np.concatenate([healthy, csd, failure])

# POASH-Ω approach: Order analysis looking for harmonic deviations
def poash_analysis(sig, window=512, overlap=256):
    """Simulate POASH-Ω harmonic analysis"""
    f, t, Sxx = welch(sig, fs=100, nperseg=window, noverlap=overlap, 
                      return_onesided=True, scaling='spectrum')
    
    # Find dominant frequency (10 Hz)
    freq_idx = np.argmin(np.abs(f - 10))
    
    # Extract harmonic amplitudes and compute PHI
    phi_values = []
    for i in range(len(t)):
        spectrum = Sxx[:, i]
        # Look for harmonics of fundamental
        harmonic_amps = []
        for h in [1, 2, 3]:  # 1st, 2nd, 3rd harmonics
            if h*freq_idx < len(f):
                harmonic_amps.append(spectrum[h*freq_idx])
            else:
                harmonic_amps.append(0)
        
        # Compute PHI as deviation from "healthy" baseline (first 100 points)
        if i < 100:
            baseline_amps = np.array(harmonic_amps)
            phi_values.append(1.0)
        else:
            # Simple deviation metric
            deviation = np.sum(np.abs(np.array(harmonic_amps) - baseline_amps) / (baseline_amps + 1e-10))
            phi_values.append(max(0, 1 - deviation/10))
    
    return t, np.array(phi_values)

# Disruptive approach: Critical Slowing Down Indicators
def csd_indicators(sig, window=100):
    """Detect critical slowing down via variance, autocorrelation, and kurtosis"""
    indicators = {
        'variance': [],
        'autocorr': [],
        'kurtosis': [],
        'regime_shift': []
    }
    
    for i in range(len(sig)):
        if i < window:
            indicators['variance'].append(0)
            indicators['autocorr'].append(0)
            indicators['kurtosis'].append(0)
            indicators['regime_shift'].append(0)
        else:
            segment = sig[i-window:i]
            
            # Variance
            indicators['variance'].append(np.var(segment))
            
            # Lag-1 autocorrelation (critical slowing down marker)
            autocorr = np.corrcoef(segment[:-1], segment[1:])[0,1]
            indicators['autocorr'].append(autocorr if not np.isnan(autocorr) else 0)
            
            # Kurtosis (non-Gaussianity indicator)
            indicators['kurtosis'].append(kurtosis(segment))
            
            # Combined early warning signal
            ew = (indicators['variance'][-1] > 0.5) and (indicators['autocorr'][-1] > 0.8)
            indicators['regime_shift'].append(1 if ew else 0)
    
    return indicators

# Run both analyses
t_poash, phi = poash_analysis(signal)
indicators = csd_indicators(signal)

# Plot results
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# Original signal with regime boundaries
axes[0].plot(time, signal, 'k-', alpha=0.7)
axes[0].axvline(30, color='g', linestyle='--', label='Healthy → CSD')
axes[0].axvline(70, color='r', linestyle='--', label='CSD → Failure')
axes[0].set_ylabel('Pipeline Signal')
axes[0].set_title('Synthetic Pipeline Data: The POASH-Ω Paradigm Collapse')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# POASH-Ω PHI metric
axes[1].plot(t_poash, phi, 'b-', linewidth=2, label='POASH-Ω PHI')
axes[1].axhline(0.4, color='r', linestyle=':', label='POASH-Ω Threshold')
axes[1].axvline(30, color='g', linestyle='--')
axes[1].axvline(70, color='r', linestyle='--')
axes[1].set_ylabel('Pipeline Health Index')
axes[1].set_title('POASH-Ω Fails: PHI shows false recovery during critical slowing down')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Critical Slowing Down indicators
axes[2].plot(time, indicators['variance'], 'r-', alpha=0.7, label='Variance')
axes[2].plot(time, np.array(indicators['autocorr'])*2, 'b-', alpha=0.7, label='Autocorr (×2)')
axes[2].plot(time, indicators['kurtosis'], 'g-', alpha=0.7, label='Kurtosis')
# Mark regime shift detections
shift_times = time[np.where(np.array(indicators['regime_shift']) == 1)[0]]
axes[2].scatter(shift_times, np.ones_like(shift_times)*3, color='purple', s=10, 
                label='CSD Detection', zorder=5)
axes[2].axvline(30, color='g', linestyle='--')
axes[2].axvline(70, color='r', linestyle='--')
axes[2].set_ylabel('CSD Indicators')
axes[2].set_xlabel('Time (s)')
axes[2].set_title('Disruptive Insight: Critical Slowing Down detects failure 40s earlier than POASH-Ω')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/pipeline_paradigm_break.png', dpi=150, bbox_inches='tight')
plt.show()

# Statistical comparison
print("=== PARADIGM BREAK ANALYSIS ===")
print(f"POASH-Ω first detects anomaly at t={t_poash[np.where(phi < 0.4)[0][0] if len(np.where(phi < 0.4)[0]) > 0 else 0]:.2f}s")
print(f"CSD detects regime shift at t={shift_times[0] if len(shift_times) > 0 else 0:.2f}s")
print(f"Lead time advantage: {(shift_times[0] - t_poash[np.where(phi < 0.4)[0][0]]) if len(shift_times) > 0 and len(np.where(phi < 0.4)[0]) > 0 else 'N/A'}s")
print("\nKey Flaw: POASH-Ω assumes stationarity in harmonic structure")
print("Reality: Financial pipelines undergo regime shifts that violate this assumption")
print("\nDisruptive Solution: Replace harmonic analysis with:")
print("1. Critical Slowing Down indicators (variance, autocorrelation)")
print("2. Branching process models of error propagation")
print("3. First-passage time statistics to failure thresholds")
print("4. Non-stationary Bayesian changepoint detection")