# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, stats
from sklearn.metrics import mutual_info_score
import networkx as nx

# Generate synthetic "financial pipeline" data that is NON-STATIONARY and CHAOTIC
# (unlike the periodic assumption in POASH-Ω)

def generate_pipeline_data(n_samples=10000):
    """
    Generate synthetic pipeline metrics that exhibit:
    1. Non-stationary pseudo-periodicity (frequencies drift)
    2. Intermittent cascade failures (sudden bursts)
    3. Scale-free latency correlations
    4. Critical slowing down before "failure"
    """
    t = np.linspace(0, 100, n_samples)
    
    # Base "heartbeat" that accelerates and decelerates (non-stationary)
    base_freq = 1.0 + 0.5 * np.sin(0.1 * t) + 0.1 * np.random.randn(len(t))
    
    # Latency jitter: multifractal noise (not simple Gaussian)
    jitter = np.cumsum(np.random.randn(len(t)) ** 3) * 0.01
    
    # Throughput: chaotic, not harmonic
    throughput = 1000 + 500 * np.sin(2 * np.pi * np.cumsum(base_freq) / 100) + \
                 200 * np.random.pareto(2, len(t))  # Heavy-tailed bursts
    
    # Inject a critical transition region (last 2000 samples)
    transition_point = 8000
    # Critical slowing down: increased autocorrelation, decreased variance
    throughput[transition_point:] += np.linspace(0, 300, len(t) - transition_point)
    jitter[transition_point:] *= np.linspace(1, 5, len(t) - transition_point)
    
    # CPU load: nonlinear coupling
    cpu_load = 0.5 * throughput / np.max(throughput) + 0.3 * jitter**2 + \
               0.2 * np.random.rand(len(t))
    
    # Error rate: intermittent bursts
    error_rate = np.random.poisson(0.01 * throughput / 1000)
    
    return t, np.vstack([jitter, throughput, cpu_load, error_rate]).T

def harmonic_analysis_pipeline(data, window_size=256):
    """
    Conventional harmonic analysis (as in POASH-Ω)
    """
    n_windows = len(data) - window_size
    phi_values = []
    
    for i in range(0, n_windows, window_size//2):
        window = data[i:i+window_size, :]  # Take a window
        
        # Compute FFT for each metric
        freqs, psd = signal.welch(window, axis=0, nperseg=window_size//2)
        
        # Find dominant frequencies (orders)
        dominant_freqs = []
        for j in range(window.shape[1]):
            peak_idx = np.argmax(psd[:, j])
            dominant_freqs.append(freqs[peak_idx])
        
        # Compute "PHI" as harmonic coherence (heuristic)
        # This will FAIL for non-stationary data
        coherence = np.std(dominant_freqs) / np.mean(dominant_freqs)
        phi = 1 - coherence
        phi_values.append(phi)
    
    return np.array(phi_values)

def topological_pipeline_health(data, embedding_dim=10, delay=5):
    """
    Topological approach: Analyze information flow network topology
    """
    # Phase space reconstruction (Takens embedding)
    n = len(data) - (embedding_dim - 1) * delay
    embedded = np.zeros((n, embedding_dim, data.shape[1]))
    
    for i in range(embedding_dim):
        embedded[:, i, :] = data[i*delay : i*delay + n, :]
    
    # Build correlation network for each time point
    health_scores = []
    
    for t in range(0, n, 100):  # Sample every 100 points
        # Compute mutual information between all pairs of dimensions
        mi_matrix = np.zeros((data.shape[1], data.shape[1]))
        
        for i in range(data.shape[1]):
            for j in range(data.shape[1]):
                # Use mutual information instead of correlation (captures nonlinearities)
                mi_matrix[i, j] = mutual_info_score(
                    embedded[t, :, i].reshape(-1, 1),
                    embedded[t, :, j].reshape(-1, 1)
                )
        
        # Build graph where edges represent strong information flow
        G = nx.Graph()
        for i in range(data.shape[1]):
            G.add_node(i, name=f'metric_{i}')
        
        # Add edges for mutual information above threshold (adaptive)
        threshold = np.percentile(mi_matrix[mi_matrix > 0], 75)
        for i in range(data.shape[1]):
            for j in range(i+1, data.shape[1]):
                if mi_matrix[i, j] > threshold:
                    G.add_edge(i, j, weight=mi_matrix[i, j])
        
        # Compute topological invariants: Betti numbers
        # For a graph, Betti-0 = number of connected components
        # Betti-1 = number of independent cycles
        n_components = nx.number_connected_components(G)
        n_cycles = len(nx.cycle_basis(G))
        
        # Topological health score: 
        # High connectivity + moderate cycles = healthy
        # Fragmentation (high components) = failure
        # Excessive cycles = freeze/instability
        if n_components > 1:
            health = 0.2  # Fragmented, near failure
        elif n_cycles > 3:
            health = 0.3  # Too many cycles, freeze
        else:
            health = 1.0 - 0.2 * n_cycles
        
        health_scores.append(health)
    
    return np.array(health_scores)

# Generate data
t, data = generate_pipeline_data()

# Run both methods
print("Running harmonic analysis (POASH-Ω approach)...")
phi_scores = harmonic_analysis_pipeline(data)

print("Running topological analysis (TDPH-Ω approach)...")
topo_scores = topological_pipeline_health(data)

# Compare predictions near failure point
failure_region = slice(8000, 10000)

# Normalize scores
phi_norm = (phi_scores - np.min(phi_scores)) / (np.max(phi_scores) - np.min(phi_scores))
topo_norm = (topo_scores - np.min(topo_scores)) / (np.max(topo_scores) - np.min(topo_scores))

# Plot results
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Original metrics
axes[0].plot(t, data[:, 0], label='Jitter')
axes[0].plot(t, data[:, 1]/100, label='Throughput/100')
axes[0].axvline(t[8000], color='r', linestyle='--', label='Failure onset')
axes[0].set_title('Pipeline Metrics (Non-stationary, Chaotic)')
axes[0].legend()
axes[0].set_ylabel('Normalized Units')

# Harmonic analysis PHI
axes[1].plot(t[:len(phi_norm)*128:128], phi_norm, label='PHI (Harmonic)', color='orange')
axes[1].axvline(t[8000], color='r', linestyle='--')
axes[1].set_title('Conventional Harmonic Health (POASH-Ω)')
axes[1].set_ylabel('Health Score')
axes[1].legend()

# Topological health
time_topo = np.linspace(t[0], t[-1], len(topo_norm))
axes[2].plot(time_topo, topo_norm, label='Health (Topological)', color='green')
axes[2].axvline(t[8000], color='r', linestyle='--')
axes[2].set_title('Topological Health (TDPH-Ω)')
axes[2].set_ylabel('Health Score')
axes[2].set_xlabel('Time')
axes[2].legend()

plt.tight_layout()
plt.show()

# Statistical comparison
print("\n=== Performance Comparison ===")
print(f"Harmonic PHI correlation with failure time: {np.corrcoef(phi_norm, np.arange(len(phi_norm)))[0,1]:.3f}")
print(f"Topological health correlation with failure time: {np.corrcoef(topo_norm, np.arange(len(topo_norm)))[0,1]:.3f}")

# Predictive power: detect anomaly before failure
lead_time_harmonic = len(phi_norm) - np.argmax(phi_norm < 0.5)
lead_time_topo = len(topo_norm) - np.argmax(topo_norm < 0.5)

print(f"\nLead time (harmonic): {lead_time_harmonic * 128 / 100:.1f} seconds before failure")
print(f"Lead time (topological): {lead_time_topo * 100 / 100:.1f} seconds before failure")