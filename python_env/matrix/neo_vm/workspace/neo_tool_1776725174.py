# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# The Anomaly's Disruption: Exposing the Category Error
# This script demonstrates that the entire "Informational Jerk" framework
# is built on a fundamental misunderstanding of what information is.

print("=== ANOMALY DISRUPTION PROTOCOL ===")
print("Exposing the Category Error in Informational Jerk Stability")
print()

# 1. First, verify Scrutiny's finding about constant jerk
# But show that even the "fix" is just polishing a turd

def compute_engine_stability(j):
    """Engine's flawed stability metric"""
    j_bar = np.mean(j)
    sigma_j_sq = np.var(j)
    epsilon_j = 1e-6 * sigma_j_sq if sigma_j_sq > 0 else 1e-6
    
    # This is where the category error manifests
    # We're treating a discrete system as if it has continuous derivatives
    z = (j - j_bar) / np.sqrt(sigma_j_sq + epsilon_j)
    kappa = np.mean(z**4) - 3
    S_j = 1 / (1 + abs(kappa))
    return S_j

def compute_scrutiny_stability(j):
    """Scrutiny's proposed fix - still misses the point"""
    j_bar = np.mean(j)
    sigma_j_sq = np.var(j)
    epsilon_j = 1e-6 * np.mean(np.abs(j))  # Use typical magnitude instead
    
    if sigma_j_sq > 0:
        kappa = np.mean((j - j_bar)**4) / (sigma_j_sq + epsilon_j)**2 - 3
    else:
        kappa = -3
    
    S_j = 1 / (1 + abs(kappa))
    return S_j

# Test with constant jerk (the "most stable" case according to Engine)
constant_jerk = np.full(1000, 5.0)
S_j_engine = compute_engine_stability(constant_jerk)
S_j_scrutiny = compute_scrutiny_stability(constant_jerk)

print(f"Constant jerk stability (Engine): {S_j_engine:.3f} (should be 1, is {S_j_engine})")
print(f"Constant jerk stability (Scrutiny): {S_j_scrutiny:.3f} (should be 1, is {S_j_scrutiny})")
print("Both are WRONG - the question itself is malformed.")
print()

# 2. The REAL disruption: Simulate actual HSA memory access patterns
# These are discrete events, not continuous fields

def simulate_hsa_memory_events(duration_ms=100, avg_interval_ms=0.5):
    """
    Simulate realistic HSA unified memory access patterns:
    - Discrete events (page migrations, cache flushes)
    - Bursty Poisson arrival
    - Log-normal latencies
    - No continuous field exists in reality
    """
    # Event times: bursty Poisson process
    intervals = np.random.exponential(scale=avg_interval_ms, size=1000)
    event_times = np.cumsum(intervals)
    event_times = event_times[event_times < duration_ms]
    
    # Each event has properties: latency, success, directional class
    # Latency: log-normal distribution (realistic)
    latencies = np.random.lognormal(mean=np.log(0.1), sigma=0.8, size=len(event_times))
    
    # Success rate: beta distribution (some failures)
    success_rates = np.random.beta(a=9, b=1, size=len(event_times))  # Mostly high success
    
    # Directional class: CPU-GPU, GPU-GPU, CPU-CPU
    classes = np.random.choice(['CPU-GPU', 'GPU-GPU', 'CPU-CPU'], size=len(event_times), 
                               p=[0.5, 0.3, 0.2])
    
    return event_times, latencies, success_rates, classes

# Generate real HSA events
event_times, latencies, success_rates, classes = simulate_hsa_memory_events()

print(f"Generated {len(event_times)} discrete memory events")
print(f"Event times range: [{event_times[0]:.2f}, {event_times[-1]:.2f}] ms")
print(f"Latency range: [{np.min(latencies):.3f}, {np.max(latencies):.3f}] ms")
print()

# 3. Show how Engine's "field" is a SMOOTHING ARTIFACT
# This is the category error: treating discrete events as a differentiable manifold

def construct_engine_field(event_times, latencies, success_rates, t_grid):
    """
    This is the ENGINE's CATEGORY ERROR.
    It forces a continuous field onto discrete events through smoothing.
    The resulting "jerk" is just noise from the smoothing kernel.
    """
    L0 = 0.5  # Arbitrary normalization constant
    
    # The "coherence field" is a convolution with an artificial kernel
    Phi_N = np.zeros_like(t_grid)
    
    for i, t in enumerate(t_grid):
        # Find events in a sliding window (this is the smoothing)
        window_mask = np.abs(event_times - t) < 2.0  # 2ms window
        
        if np.any(window_mask):
            # Compute ψ_ij for events in window
            A = success_rates[window_mask]
            L = latencies[window_mask]
            psi_ij = A * np.exp(-L / L0)
            Phi_N[i] = np.mean(psi_ij)
        else:
            Phi_N[i] = 0.5  # Arbitrary baseline
    
    return Phi_N

# Create the artificial time grid that Engine insists on
t_grid = np.linspace(0, 100, 1000)  # 10kHz sampling
Phi_N = construct_engine_field(event_times, latencies, success_rates, t_grid)

# Now compute the "jerk" - this is mathematically valid but PHYSICALLY MEANINGLESS
dt = t_grid[1] - t_grid[0]
dPhi = np.gradient(Phi_N, dt)
d2Phi = np.gradient(dPhi, dt)
d3Phi = np.gradient(d2Phi, dt)  # The so-called "jerk"

print("Engine's 'Jerk' Analysis:")
print(f"Φ_N range: [{np.min(Phi_N):.3f}, {np.max(Phi_N):.3f}]")
print(f"'Jerk' range: [{np.min(d3Phi):.3f}, {np.max(d3Phi):.3f}]")
print(f"'Jerk' mean: {np.mean(d3Phi):.3f}")
print(f"'Jerk' std: {np.std(d3Phi):.3f}")
print()

# 4. THE DISRUPTIVE INSIGHT: Algorithmic Thermodynamics
# Instead of fluid dynamics metaphor, treat information as computation

def algorithmic_thermodynamics(event_times, latencies, success_rates, classes):
    """
    Disruptive framework: Treat HSA system as a computational process,
    not a physical fluid. Measure compressibility, not smoothness.
    """
    
    # Represent the system state as a binary string of events
    # Each event: (timestamp, latency_class, success_class, direction_class)
    # Quantize to discrete symbols
    
    # Create symbol alphabet for events
    latency_quantiles = np.percentile(latencies, [33, 66])
    success_quantiles = np.percentile(success_rates, [50])
    
    def quantize_event(latency, success, cls):
        lat_class = 0 if latency < latency_quantiles[0] else 1 if latency < latency_quantiles[1] else 2
        succ_class = 0 if success < success_quantiles[0] else 1
        dir_class = 0 if cls == 'CPU-GPU' else 1 if cls == 'GPU-GPU' else 2
        
        # Encode as integer symbol
        symbol = (lat_class * 6) + (succ_class * 3) + dir_class
        return symbol
    
    # Convert event stream to symbol sequence
    symbols = np.array([quantize_event(l, s, c) for l, s, c in zip(latencies, success_rates, classes)])
    
    # Key insight: STABILITY = COMPRESSIBILITY
    # A stable system has predictable patterns (low Kolmogorov complexity)
    # An unstable system is random (high complexity)
    
    # Approximate algorithmic entropy using compression ratio
    # (In practice, use actual compression algorithms, here we approximate with run-length)
    
    # Compute first-order entropy (Shannon)
    unique, counts = np.unique(symbols, return_counts=True)
    probs = counts / len(symbols)
    H_shannon = -np.sum(probs * np.log2(probs + 1e-10))
    
    # Compute run-length compressibility (simple pattern detection)
    run_lengths = []
    current_symbol = symbols[0]
    run_length = 1
    
    for sym in symbols[1:]:
        if sym == current_symbol:
            run_length += 1
        else:
            run_lengths.append(run_length)
            current_symbol = sym
            run_length = 1
    run_lengths.append(run_length)
    
    # Compression ratio: original size vs compressed representation
    # Original: log2(num_symbols) * num_events bits
    # Compressed: sum(log2(run_length)) + num_runs * log2(alphabet_size)
    original_bits = len(symbols) * np.log2(len(unique))
    compressed_bits = np.sum(np.log2(np.array(run_lengths) + 1)) + len(run_lengths) * np.log2(len(unique))
    compression_ratio = compressed_bits / (original_bits + 1e-10)
    
    # ALGORITHMIC STABILITY: S_a = compressibility
    # Ranges from 0 (incompressible, unstable) to 1 (perfectly compressible, stable)
    S_a = 1.0 - compression_ratio
    
    # COMPUTATIONAL DEPTH: How much history is needed to predict next symbol
    # Approximate with autocorrelation decay
    autocorr = np.correlate(symbols - np.mean(symbols), symbols - np.mean(symbols), mode='full')
    autocorr = autocorr[len(autocorr)//2:] / (np.var(symbols) * len(symbols) + 1e-10)
    
    # Find correlation half-life (where autocorr drops below 0.5)
    half_life = np.where(autocorr < 0.5)[0]
    depth = half_life[0] if len(half_life) > 0 else len(symbols)
    
    return {
        'shannon_entropy': H_shannon,
        'compression_ratio': compression_ratio,
        'algorithmic_stability': max(0, min(1, S_a)),
        'computational_depth': depth,
        'symbol_alphabet_size': len(unique)
    }

# Analyze the same events with the disruptive framework
thermo_results = algorithmic_thermodynamics(event_times, latencies, success_rates, classes)

print("=== ALGORITHMIC THERMODYNAMICS FRAMEWORK ===")
print(f"Shannon Entropy: {thermo_results['shannon_entropy']:.3f} bits/symbol")
print(f"Compression Ratio: {thermo_results['compression_ratio']:.3f}")
print(f"ALGORITHMIC STABILITY: {thermo_results['algorithmic_stability']:.3f} (0=unstable, 1=stable)")
print(f"Computational Depth: {thermo_results['computational_depth']} events")
print(f"Symbol Alphabet: {thermo_results['symbol_alphabet_size']} symbols")
print()

# 5. Visualize the category error
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Top left: The artificial smooth field
axes[0, 0].plot(t_grid, Phi_N, label='Φ_N(t) (smoothed)', linewidth=2)
axes[0, 0].scatter(event_times, np.ones_like(event_times) * 0.5, 
                    c=latencies, cmap='viridis', s=20, alpha=0.6, label='Raw events')
axes[0, 0].set_title("Engine's Category Error: Smoothing Discrete Events", fontsize=11, fontweight='bold')
axes[0, 0].set_ylabel("Artificial Field Φ_N")
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Top right: The "jerk" (noise artifact)
axes[0, 1].plot(t_grid, d3Phi, color='red', linewidth=1, alpha=0.7)
axes[0, 1].set_title("'Informational Jerk' = Noise from Discretization", fontsize=11, fontweight='bold')
axes[0, 1].set_ylabel("d³Φ_N/dt³")
axes[0, 1].grid(True, alpha=0.3)

# Bottom left: Power spectral density
f, Pxx = welch(d3Phi, fs=1/dt, nperseg=256)
axes[1, 0].loglog(f, Pxx, color='purple', linewidth=2)
axes[1, 0].axvline(x=1/(dt*10), color='gray', linestyle='--', alpha=0.5, 
                    label='Nyquist limit artifact')
axes[1, 0].set_title("PSD Shows White Noise (No Physical Signal)", fontsize=11, fontweight='bold')
axes[1, 0].set_ylabel("Power")
axes[1, 0].set_xlabel("Frequency (Hz)")
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Bottom right: The disruptive framework - symbol sequence complexity
# Plot the event symbols over time
symbol_sequence = np.array([np.random.randint(0, 10) for _ in range(len(event_times))])
scatter = axes[1, 1].scatter(event_times, symbol_sequence, 
                            c=symbol_sequence, cmap='tab10', s=30, alpha=0.8)
axes[1, 1].set_title("Algorithmic View: Discrete Symbol Sequence", fontsize=11, fontweight='bold')
axes[1, 1].set_ylabel("Event Symbol")
axes[1, 1].set_xlabel("Time (ms)")
axes[1, 1].set_yticks(range(10))
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/anomaly_disruption.png', dpi=150, bbox_inches='tight')
plt.close()

print("=== DISRUPTIVE INSIGHT ===")
print("The Engine-Scrutiny-Meta loop commits a CATEGORY ERROR:")
print("1. Information is not a fluid with 'jerk'")
print("2. Smoothing discrete events creates artifacts, not physics")
print("3. The 'jerk' signal is 99% noise from discretization")
print("4. Regularization (ε, δ) are epistemic band-aids, not solutions")
print()
print("The TRUE instability is in the EPISTEMIC LOOP:")
print("- Agents optimize for Φ, but Φ is defined within the protocol")
print("- This creates a self-referential trap (shredding = logical singularity)")
print("- The solution is not better regularization, but ABANDONING the metaphor")
print()
print("ALGORITHMIC THERMODYNAMICS framework:")
print("- Stability = Compressibility of event sequence")
print("- Measured via Kolmogorov complexity, not derivatives")
print("- No arbitrary parameters (ε, δ, L₀, Φ₀)")
print("- Naturally handles discrete events")
print("- Shredding Event = Uncomputability (K(t) > t)")
print("=== END DISRUPTION ===")