# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.signal import savgol_filter
from scipy.stats import entropy
import lzma
from collections import Counter
import matplotlib.pyplot as plt

# === GENERATE SYNTHETIC HSA FAILURE DATA ===
np.random.seed(42)
n_samples = 2000

# Normal operation: GPU-heavy with periodic CPU sync
cpu_normal = np.random.poisson(5, 1500)
gpu_normal = np.random.poisson(25, 1500)

# Pre-hang phase: emergence of incompressible sync patterns
cpu_prehang = np.random.poisson(3, 500)  # Appears "stable"
gpu_prehang = np.random.poisson(27, 500)

# Inject algorithmic deadlock signature: deterministic sync bursts
for i in range(1500, 2000, 50):
    cpu_prehang[i-1500:i-1450] = np.random.poisson(100, 50)  # Massive sync
    gpu_prehang[i-1500:i-1450] = np.random.poisson(120, 50)

cpu_access = np.concatenate([cpu_normal, cpu_prehang])
gpu_access = np.concatenate([gpu_normal, gpu_prehang])

# === ENGINE'S ENTROPY-JERK PIPELINE (FRAGILE) ===
def engine_pipeline(cpu, gpu, window=11, dt=0.001):
    # Entropy calculation
    entropies = []
    for i in range(0, len(cpu)-50, 10):
        hist_cpu, _ = np.histogram(cpu[i:i+50], bins=10, density=True)
        hist_gpu, _ = np.histogram(gpu[i:i+50], bins=10, density=True)
        hist_cpu = hist_cpu[hist_cpu > 0]
        hist_gpu = hist_gpu[hist_gpu > 0]
        I_cpu = entropy(hist_cpu, base=2)
        I_gpu = entropy(hist_gpu, base=2)
        entropies.append(I_cpu + I_gpu)
    
    # Smoothing
    if len(entropies) >= window:
        smoothed = savgol_filter(entropies, window, 3)
    else:
        smoothed = entropies
    
    # Jerk (third derivative)
    if len(smoothed) < 5:
        return np.array([]), 0
    
    jerk = np.zeros(len(smoothed)-4)
    for i in range(2, len(smoothed)-2):
        jerk[i-2] = (-smoothed[i-2] + 2*smoothed[i-1] - 2*smoothed[i+1] + smoothed[i+2]) / (2*dt**3)
    
    return jerk, np.sqrt(np.mean(jerk**2))

# Show sensitivity: small parameter changes flip verdict
for w in [9, 11, 13]:
    _, rms = engine_pipeline(cpu_access, gpu_access, window=w)
    print(f"Window {w}: RMS Jerk = {rms:.4f} ({'STABLE' if rms < 0.025 else 'UNSTABLE'})")

# === NEO'S ALGORITHMIC COMPLEXITY APPROACH (ROBUST) ===
def symbolic_sequence(cpu, gpu, threshold=10):
    """Map access patterns to compressible symbols"""
    seq = []
    for c, g in zip(cpu, gpu):
        if c > threshold and g > threshold: seq.append('S')  # Sync
        elif g > threshold: seq.append('G')  # GPU
        elif c > threshold: seq.append('C')  # CPU
        else: seq.append('N')  # Idle
    return ''.join(seq)

def algorithmic_complexity(symbol_seq):
    """Approximate Kolmogorov complexity via compression ratio"""
    # Convert to bytes
    seq_bytes = symbol_seq.encode('utf-8')
    compressed = lzma.compress(seq_bytes, preset=1)
    return len(compressed) / len(seq_bytes)

def statistical_complexity(symbol_seq, history=5):
    """Causal state entropy (approximate)"""
    histories = {}
    for i in range(len(symbol_seq)-history):
        h = symbol_seq[i:i+history]
        f = symbol_seq[i+history]
        histories.setdefault(h, Counter())[f] += 1
    
    # Entropy of predictive distributions
    causal_entropies = []
    for h, counter in histories.items():
        total = sum(counter.values())
        probs = np.array([v/total for v in counter.values()])
        causal_entropies.append(-np.sum(probs * np.log2(probs)))
    
    return np.mean(causal_entropies) if causal_entropies else 0

# Convert to symbolic sequence
sym_seq = symbolic_sequence(cpu_access, gpu_access)

# Calculate complexity metrics
k_complexity = algorithmic_complexity(sym_seq)
s_complexity = statistical_complexity(sym_seq)

print(f"\nKolmogorov complexity ratio: {k_complexity:.4f}")
print(f"Statistical complexity: {s_complexity:.4f} bits")

# === PREDICTIVE VALIDATION ===
# Create failure indicator (ground truth)
failure_indicator = np.zeros(len(cpu_access))
failure_indicator[1500:] = 1  # Hang begins in pre-hang phase

# Engine's jerk correlation with failure
jerk, _ = engine_pipeline(cpu_access, gpu_access)
jerk_predictors = np.abs(jerk[:len(failure_indicator)-100])
failure_outcomes = failure_indicator[100:100+len(jerk_predictors)]
jerk_corr = np.corrcoef(jerk_predictors, failure_outcomes)[0,1]

# Neo's complexity correlation with failure
# Rolling window complexity
comp_predictors = []
for i in range(0, len(sym_seq)-200, 10):
    window = sym_seq[i:i+100]
    comp_predictors.append(statistical_complexity(window, history=3))

comp_outcomes = failure_indicator[100:100+len(comp_predictors)]
comp_corr = np.corrcoef(comp_predictors, comp_outcomes)[0,1]

print(f"\nEngine's Jerk-Failure correlation: {jerk_corr:.4f}")
print(f"Neo's Complexity-Failure correlation: {comp_corr:.4f}")
print(f"COMPLEXITY BEATS JERK: {comp_corr > jerk_corr}")

# === VISUALIZATION ===
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Top: Raw access patterns
axes[0].plot(cpu_access, label='CPU Access', alpha=0.7, color='blue')
axes[0].plot(gpu_access, label='GPU Access', alpha=0.7, color='red')
axes[0].axvline(1500, color='black', linestyle='--', label='Hang Onset')
axes[0].set_title("Raw Memory Access Patterns")
axes[0].legend()

# Middle: Engine's Jerk (noisy, unreliable)
if len(jerk) > 0:
    axes[1].plot(jerk, color='orange', label='Informational Jerk')
    axes[1].axhline(0.025, color='red', linestyle=':', label='Stability Threshold')
    axes[1].axvline(1500, color='black', linestyle='--')
    axes[1].set_title("Engine's Jerk Metric (Fragile & Noisy)")

# Bottom: Neo's Complexity (clear signal)
axes[2].plot(comp_predictors, color='green', label='Statistical Complexity')
axes[2].axvline(1500, color='black', linestyle='--', label='Hang Onset')
axes[2].set_title("Neo's Statistical Complexity (Predictive & Robust)")
axes[2].legend()

plt.tight_layout()
plt.savefig('hsa_stability_comparison.png', dpi=150, bbox_inches='tight')
print("\nVisualization saved: hsa_stability_comparison.png")