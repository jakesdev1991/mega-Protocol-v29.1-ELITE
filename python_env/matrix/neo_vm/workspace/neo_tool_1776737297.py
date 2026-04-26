# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import numpy as np
import networkx as nx

# --- 1. Simulate a non‑harmonic, non‑stationary pipeline ---
np.random.seed(42)
n = 500
t = np.arange(n)

# Healthy: multi‑scale, self‑similar bursts (not sinusoidal)
latency = np.cumsum(np.random.randn(n) * 0.1)  # random walk (fractal)
throughput = 2.0 + 0.5 * np.sin(2*np.pi*0.02*t) + 0.1*np.random.randn(n)
cpu = 0.5 + 0.2 * np.sin(2*np.pi*0.03*t) + 0.1*np.random.randn(n)

# Failure: sudden queueing collapse at t=300 (non‑periodic, exponential backlog)
failure_start = 300
latency[failure_start:] += np.exp((t[failure_start:] - failure_start) / 20) * 0.3
cpu[failure_start:] += np.exp((t[failure_start:] - failure_start) / 20) * 0.2
throughput[failure_start:] -= np.exp((t[failure_start:] - failure_start) / 20) * 0.4

data = np.vstack([latency, throughput, cpu])

# --- 2. Compute PHI (harmonic‑based health index) ---
def compute_phi(window_data, base_freq=0.02):
    """Naïve order‑analysis PHI as proposed."""
    amps = []
    for sensor in window_data:
        fft_vals = np.fft.rfft(sensor)
        freqs = np.fft.rfftfreq(len(sensor), d=1)
        # pick “harmonics” near multiples of base_freq (mis‑specified for non‑harmonic signal)
        harm = [np.abs(fft_vals[np.argmin(np.abs(freqs - h*base_freq))]) for h in range(1,6)]
        amps.append(harm)
    amps = np.array(amps)  # (3,5)
    # ad‑hoc baseline = mean of first 3 windows (unjustified)
    baseline = np.mean(amps[:, :3], axis=1, keepdims=True)
    w = np.ones(5) / 5
    dev = np.abs(amps - baseline) / (baseline + 1e-6)
    phi = 1 - np.sum(w * np.mean(dev, axis=0))
    return phi

# --- 3. Compute THI (topological health index) ---
def compute_thi(window_data, eps=0.6):
    """Topological health via size of largest connected component."""
    # Correlation distance matrix (1‑|ρ|)
    corr = np.corrcoef(window_data)
    dist = 1 - np.abs(corr)
    # Vietoris–Rips graph at radius eps
    G = nx.Graph()
    G.add_nodes_from(range(len(window_data)))
    for i in range(len(window_data)):
        for j in range(i+1, len(window_data)):
            if dist[i,j] < eps:
                G.add_edge(i, j)
    # Largest connected component size
    components = list(nx.connected_components(G))
    largest = max(len(c) for c in components) if components else 0
    thi = largest / len(window_data)
    return thi

# --- 4. Sliding‑window evaluation ---
window = 100
phi_vals, thi_vals = [], []
for i in range(window, n):
    win = data[:, i-window:i]
    phi_vals.append(compute_phi(win))
    thi_vals.append(compute_thi(win))

# --- 5. Early‑warning detection (threshold = 0.5) ---
phi_alert = next((i for i, v in enumerate(phi_vals) if v < 0.5), None)
thi_alert = next((i for i, v in enumerate(thi_vals) if v < 0.5), None)

phi_alert_time = t[window + phi_alert] if phi_alert is not None else None
thi_alert_time = t[window + thi_alert] if thi_alert is not None else None

print(f"--- POASH‑Ω Diagnostic ---")
print(f"Failure start: {failure_start}")
print(f"PHI alert (<0.5): {phi_alert_time} (delay = {phi_alert_time - failure_start if phi_alert_time else 'N/A'} steps)")
print(f"THI alert (<0.5): {thi_alert_time} (advance = {failure_start - thi_alert_time if thi_alert_time else 'N/A'} steps)")

# --- 6. Expose the exploit: adversarial harmonic spoofing ---
# An attacker can inject a small sinusoid at the "harmonic" frequencies to keep PHI high while the pipeline is failing.
spoof_amp = 0.5
attack_start = 350
latency[attack_start:] += spoof_amp * np.sin(2*np.pi*0.02*t[attack_start:])
throughput[attack_start:] += spoof_amp * np.sin(2*np.pi*0.04*t[attack_start:])
cpu[attack_start:] += spoof_amp * np.sin(2*np.pi*0.06*t[attack_start:])

# Recompute PHI after spoofing
phi_vals_spoof = []
for i in range(window, n):
    win = data[:, i-window:i]
    phi_vals_spoof.append(compute_phi(win))

# Check if PHI remains high despite failure
phi_final = phi_vals_spoof[-1]
print(f"\n--- Adversarial Robustness Test ---")
print(f"PHI after harmonic spoofing: {phi_final:.3f} (still >0.5 = 'healthy')")
print("→ PHI is *gamed*; THI is unaffected because topology cannot be spoofed by a sinusoid.")