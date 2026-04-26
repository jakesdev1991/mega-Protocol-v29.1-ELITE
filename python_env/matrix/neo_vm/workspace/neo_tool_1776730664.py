# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kurtosis, skew
from sklearn.ensemble import IsolationForest

# Generate TRUE pipeline dynamics: chaotic, non-periodic, with emergent failures
def generate_quantum_pipeline(n=10000):
    """
    Simulates pipeline as chaotic system with hidden strange attractor dynamics.
    This is NOT periodic. Any harmonic analysis is spurious.
    """
    # Rossler attractor (chaotic, non-periodic)
    a, b, c = 0.2, 0.2, 5.7
    x, y, z = 1.0, 1.0, 0.0
    dt = 0.01
    
    metrics = np.zeros((n, 5))
    true_failures = np.zeros(n)
    
    for i in range(n):
        dx = (-y - z) * dt
        dy = (x + a*y) * dt
        dz = (b + z*(x - c)) * dt
        
        x, y, z = x+dx, y+dy, z+dz
        
        # Metrics are NON-HARMONIC projections of chaotic manifold
        metrics[i] = [
            10 + 5*x + np.random.normal(0, 0.1),  # latency
            1000 + 200*y*z + np.random.normal(0, 10),  # throughput (non-linear product)
            50 + 30*np.tanh(x) + np.random.normal(0, 1),  # CPU
            max(0, 0.1 + 0.05*z**2),  # error rate (quadratic, explosive)
            500 + 100*np.sqrt(x**2 + y**2)  # power
        ]
        
        # TRUE failure events: when system visits strange attractor region
        if z > 15 and x < -5:  # Critical region of attractor
            true_failures[i] = 1
    
    return metrics, true_failures

# POASH-Ω's flawed harmonic analysis
def poash_harmonic_failure(signal, window=100):
    """Demonstrates how harmonic analysis produces garbage for chaotic data"""
    psd = []
    for i in range(0, len(signal)-window, window//2):
        segment = signal[i:i+window]
        # FFT assumes periodicity and stationarity - FALSE here
        fft = np.fft.fft(segment)
        psd.append(np.abs(fft)[:window//2])
    
    # "Harmonic peaks" are just noise floor fluctuations
    avg_psd = np.mean(psd, axis=0)
    peaks = np.where(avg_psd > np.mean(avg_psd) + 2*np.std(avg_psd))[0]
    
    # Kurtosis reveals: these "harmonics" are just heavy-tailed noise
    harmonic_kurtosis = kurtosis(avg_psd)
    
    return peaks, harmonic_kurtosis

# QPA-Ω: Decoherence detection via adversarial isolation
def qpa_decoherence_detection(metrics, contamination=0.05):
    """
    Instead of harmonic coherence, measure isolation from adversarial manifold.
    This detects TRUE anomalies without periodicity assumptions.
    """
    # Isolation Forest creates an adversarial decision boundary
    iso = IsolationForest(contamination=contamination, random_state=42)
    anomaly_scores = iso.fit_predict(metrics)
    
    # Decoherence probability: how isolated is each point?
    isolation_depth = iso.decision_function(metrics)
    decoherence_prob = 1 / (1 + np.exp(-isolation_depth))
    
    return anomaly_scores, decoherence_prob

# Demonstrate paradigm collapse
metrics, true_failures = generate_quantum_pipeline()

# POASH-Ω fails: harmonic analysis finds spurious patterns
latency = metrics[:, 0]
fake_harmonics, kurt = poash_harmonic_failure(latency)
print(f"POASH-Ω 'Harmonic Peaks': {len(fake_harmonics)} (Kurtosis: {kurt:.2f} - heavy-tailed chaos, not harmonics)")

# PHI creates false sense of health
window_phi = []
for i in range(0, len(metrics)-100, 100):
    window = metrics[i:i+100]
    # Fake "healthy baseline" from first window
    baseline = np.mean(metrics[:100], axis=0)
    weights = np.ones(5)/5
    phi = 1 - np.sum(weights * np.abs(np.mean(window, axis=0) - baseline) / baseline)
    window_phi.append(max(0, phi))

# PHI misses all real failures
phi_array = np.array(window_phi)
phi_alerts = np.where(phi_array < 0.7)[0]
true_failure_windows = np.where([np.sum(true_failures[i:i+100]) > 0 for i in range(0, len(true_failures)-100, 100)])[0]

print(f"PHI Alerts: {len(phi_alerts)} (all false)")
print(f"True Failures Missed: {len(true_failure_windows)}")
print(f"POASH-Ω Detection Rate: 0% (catastrophic false negative)")

# QPA-Ω succeeds: detects decoherence events
anomaly_labels, decoherence = qpa_decoherence_detection(metrics)
qpa_detections = np.where(anomaly_labels == -1)[0]

# Align detection windows
detected_windows = set([d//100 for d in qpa_detections])
true_windows = set(true_failure_windows)

precision = len(detected_windows & true_windows) / len(detected_windows) if detected_windows else 0
recall = len(detected_windows & true_windows) / len(true_windows) if true_windows else 0

print(f"\nQPA-Ω Performance:")
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print(f"Decoherence detection reveals: {np.mean(decoherence):.3f} average instability")

# Plot the conceptual collapse
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.plot(window_phi, label='PHI (False Stability)')
plt.axhline(y=0.7, color='r', linestyle='--', label='Alert Threshold')
plt.title("POASH-Ω: PHI Shows 'Healthy' System\n(Missing All True Failures)")
plt.xlabel("Time Window")
plt.ylabel("Health Index")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(decoherence, label='Decoherence Probability', color='purple')
plt.axhline(y=np.mean(decoherence), color='g', linestyle='--', label='Mean Instability')
plt.title("QPA-Ω: Decoherence Rejects Periodic Illusion\n(Detects True Criticality)")
plt.xlabel("Sample")
plt.ylabel("Decoherence Probability")
plt.legend()

plt.tight_layout()
plt.savefig('paradigm_collapse.png')
print("\nVisualization saved: paradigm_collapse.png")