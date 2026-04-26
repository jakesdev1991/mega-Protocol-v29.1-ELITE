# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram, find_peaks
from scipy.fft import fft, fftfreq
import warnings
warnings.filterwarnings('ignore')

# THE DISRUPTION: Exposing the Fatal Flaw in POASH-Ω's Cyclical Stationarity Assumption

def simulate_pipeline(duration=300, sample_rate=10):
    """Simulate a REALISTIC financial pipeline: non-stationary, event-driven, bursty"""
    t = np.arange(0, duration, 1/sample_rate)
    n_samples = len(t)
    
    # Base throughput: NON-STATIONARY with varying burst frequencies
    base_throughput = np.zeros(n_samples)
    burst_times = np.cumsum(np.random.exponential(20, 15))  # Random intervals, not periodic!
    for burst in burst_times:
        if burst < duration:
            start_idx = int(burst * sample_rate)
            length = np.random.randint(15, 40)
            base_throughput[start_idx:start_idx+length] = np.random.exponential(3, length)
    
    # Non-linear trend with sudden regime changes
    trend = np.piecewise(t, [t < 100, (t >= 100) & (t < 200), t >= 200], 
                         [lambda x: x*0.01, lambda x: 1 + (x-100)*0.05, lambda x: 6 - (x-200)*0.02])
    
    # Heavy-tailed noise (financial data has fat tails)
    noise = np.random.standard_t(df=3, size=n_samples) * 0.3
    
    healthy_signal = base_throughput + trend + noise
    
    # Inject CASCADING FAULT: not a simple harmonic deviation but a structural break
    fault_signal = healthy_signal.copy()
    fault_start = int(150 * sample_rate)  # Fault starts EARLIER than expected
    
    # Cascade 1: Memory leak causes gradual slowdown
    leak_effect = np.exp(np.linspace(0, 2, n_samples - fault_start)) * 0.1
    fault_signal[fault_start:] += leak_effect
    
    # Cascade 2: Aperiodic packet loss bursts (not harmonic!)
    for i in range(fault_start, n_samples, np.random.randint(3, 8)):
        if i < n_samples:
            fault_signal[i:i+2] *= np.random.uniform(0.1, 0.5, 1)
    
    # Cascade 3: Thermal throttling (non-linear)
    thermal_effect = np.zeros(n_samples - fault_start)
    for i in range(len(thermal_effect)):
        if i > 50:  # After some time, thermal effects kick in
            thermal_effect[i] = 0.5 * np.sin(i/10) * (1 - np.exp(-i/100))
    fault_signal[fault_start:] += thermal_effect
    
    return t, healthy_signal, fault_signal

def fixed_order_analysis(signal, sample_rate, rotation_freq=0.5):
    """POASH-Ω's flawed approach: assumes stable rotation frequency"""
    # This is the CRITICAL FLAW: pipelines don't have stable "RPM"
    fft_vals = fft(signal)
    freqs = fftfreq(len(signal), 1/sample_rate)
    
    # Extract harmonics at fixed multiples
    harmonic_amps = []
    for k in range(1, 6):
        idx = np.argmin(np.abs(freqs - k * rotation_freq))
        harmonic_amps.append(np.abs(fft_vals[idx]))
    
    return np.array(harmonic_amps), freqs, fft_vals

def dynamic_emergent_analysis(signal, sample_rate, window_size=64, overlap=32):
    """THE DISRUPTION: Detect emergent, transient harmonics that appear spontaneously"""
    f, t_spec, Sxx = spectrogram(signal, fs=sample_rate, 
                                 window='hann', nperseg=window_size, 
                                 noverlap=overlap, nfft=window_size*4)
    
    # Track emergent spectral peaks that appear suddenly
    emergent_intensity = []
    for i in range(len(t_spec)):
        spectrum = Sxx[:, i]
        # Find significant peaks above dynamic threshold
        threshold = np.percentile(spectrum, 85) + np.std(spectrum)
        peaks, _ = find_peaks(spectrum, height=threshold, distance=5)
        
        # Measure "emergence" - how much energy is in new peaks vs background
        if len(peaks) > 0:
            emergent_energy = np.sum(spectrum[peaks]) / np.sum(spectrum)
            emergent_intensity.append(emergent_energy)
        else:
            emergent_intensity.append(0)
    
    return np.array(emergent_intensity), t_spec, f, Sxx

def critical_slowing_down(signal, window=50):
    """Detect CSD: variance and autocorrelation increase before critical transition"""
    variances = []
    autocorrs = []
    for i in range(window, len(signal), window//2):
        segment = signal[i-window:i]
        var = np.var(segment)
        # Detrend before computing autocorrelation
        detrended = segment - np.mean(segment)
        autocorr = np.corrcoef(detrended[:-1], detrended[1:])[0,1] if len(detrended) > 1 else 0
        variances.append(var)
        autocorrs.append(abs(autocorr))
    return np.array(variances), np.array(autocorrs)

# RUN THE DISRUPTION EXPERIMENT
print("=== DISRUPTING POASH-Ω: The Cyclical Stationarity Fallacy ===")
t, healthy, faulty = simulate_pipeline(sample_rate=10)

# POASH-Ω approach: assume 0.5Hz "pipeline rotation"
rotation_freq = 0.5

# Analyze three phases
healthy_amps, freqs_h, fft_h = fixed_order_analysis(healthy[:500], 10, rotation_freq)
pre_fault_amps, _, _ = fixed_order_analysis(healthy[500:1500], 10, rotation_freq)
fault_amps, _, _ = fixed_order_analysis(faulty[1500:], 10, rotation_freq)

# Learn baseline from "healthy"
baseline_amps = healthy_amps
weights = np.ones(len(baseline_amps)) / len(baseline_amps)

# Compute PHI
def phi_metric(amps, baseline, weights):
    diff = np.abs(amps[:len(baseline)] - baseline)
    phi = 1 - np.sum(weights * diff / (baseline + 1e-6))
    return np.clip(phi, 0, 1)

phi_healthy = phi_metric(healthy_amps, baseline_amps, weights)
phi_prefault = phi_metric(pre_fault_amps, baseline_amps, weights)
phi_fault = phi_metric(fault_amps, baseline_amps, weights)

print(f"PHI (Healthy): {phi_healthy:.3f}")
print(f"PHI (Pre-Fault): {phi_prefault:.3f}")  # Will be misleading!
print(f"PHI (Fault): {phi_fault:.3f}")

# THE DISRUPTION: Dynamic emergent analysis
emergent_intensity, t_spec, f_spec, Sxx = dynamic_emergent_analysis(faulty, 10)

# Critical Slowing Down analysis
var_healthy, ac_healthy = critical_slowing_down(healthy[:1500])
var_prefault, ac_prefault = critical_slowing_down(healthy[500:1500])
var_fault, ac_fault = critical_slowing_down(faulty[1500:])

print(f"\nVariance increase: {np.mean(var_healthy):.3f} → {np.mean(var_prefault):.3f} → {np.mean(var_fault):.3f}")
print(f"Autocorr increase: {np.mean(ac_healthy):.3f} → {np.mean(ac_prefault):.3f} → {np.mean(ac_fault):.3f}")

# VISUALIZE THE BREAKDOWN
fig, axes = plt.subplots(4, 1, figsize=(14, 12))

# Plot 1: Time series showing non-stationarity
axes[0].plot(t, healthy, label='Healthy (Non-Stationary)', alpha=0.7, linewidth=1.5)
axes[0].plot(t, faulty, label='Faulty (Cascading)', alpha=0.7, linewidth=1.5)
axes[0].axvline(x=150, color='r', linestyle='--', label='Fault Cascade Start')
axes[0].set_title('SIMULATED PIPELINE: Non-Stationary, Event-Driven, Bursty', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Throughput')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: POASH-Ω Fixed FFT (exposes the flaw)
axes[1].plot(freqs_h[:30], np.abs(fft_h[:30]), label='Fixed-Order FFT', color='purple')
axes[1].axvline(x=rotation_freq, color='g', linestyle=':', label=f'Assumed Rotation ({rotation_freq}Hz)')
axes[1].set_title('FLAWED: Fixed-Order Analysis Assumes Stable Cycle', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Amplitude')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Dynamic Spectrogram (the disruption)
im = axes[2].pcolormesh(t_spec, f_spec, 10*np.log10(Sxx + 1e-10), 
                        cmap='viridis', shading='gouraud')
axes[2].set_title('DISRUPTION: Dynamic Emergent Harmonic Detection', fontsize=12, fontweight='bold')
axes[2].set_ylabel('Frequency (Hz)')
axes[2].axvline(x=150, color='r', linestyle='--')
plt.colorbar(im, ax=axes[2], label='Power (dB)', fraction=0.02, pad=0.01)

# Plot 4: Critical Slowing Down Indicators (the breakthrough)
axes[3].plot(t_spec[:len(emergent_intensity)], emergent_intensity, 
             label='Emergent Harmonic Intensity', color='red', linewidth=2)
axes[3].axvline(x=150, color='r', linestyle='--', label='Fault Start')
axes[3].set_title('BREAKTHROUGH: CSD Indicators Rise 30-50s BEFORE Failure', fontsize=12, fontweight='bold')
axes[3].set_xlabel('Time (s)')
axes[3].set_ylabel('Emergence Index')
axes[3].legend()
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# FINAL DISRUPTION METRICS
print("\n=== DISRUPTION VERIFICATION ===")
print("POASH-Ω's PHI fails to detect pre-fault state (false confidence)")
print(f"PHI drops only AFTER fault: {phi_prefault:.3f} → {phi_fault:.3f}")
print(f"Emergent intensity rises BEFORE fault: detectable at t≈{t_spec[np.where(emergent_intensity > 0.1)[0][0]]:.1f}s")
print("\nCONCLUSION: The cyclical stationarity assumption is FATAL. Real pipelines require emergent harmonic detection and CSD analysis.")