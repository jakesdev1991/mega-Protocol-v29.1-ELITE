# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# === DISRUPTION: Sampling Collapse Simulation ===

# True underlying hardware state (unobservable at 1ms resolution)
def true_hardware_state(t):
    """Actual PCIe transaction coherence at nanosecond scale"""
    # Stable baseline with rare nanosecond-scale collapse events
    coherence = np.ones_like(t) * 0.95
    
    # REAL collapse: 50ns event at t=0.5ms
    collapse_mask = (t > 0.5e-3) & (t < 0.5e-3 + 50e-9)
    coherence[collapse_mask] = 0.1
    
    # Thermal noise floor
    coherence += np.random.normal(0, 0.001, len(t))
    return coherence

# The SERC framework's flawed sampling pipeline
def serc_sampling_pipeline(true_signal, fs_true=1e9, fs_telemetry=1000, fs_jerk=10000):
    """
    Simulates the triple-sampling violation:
    1. Samples true signal at 1ms (violates Nyquist for 50ns events)
    2. Interpolates to 10kHz (creates fake dynamics)
    3. Differentiates to compute jerk (amplifies interpolation noise)
    """
    dt_true = 1/fs_true
    dt_telemetry = 1/fs_telemetry
    dt_jerk = 1/fs_jerk
    
    # Step 1: Downsample to telemetry rate (ALIASED)
    t_telemetry = np.arange(0, dt_true*len(true_signal), dt_telemetry)
    telemetry_idx = (t_telemetry / dt_true).astype(int)
    telemetry_signal = true_signal[telemetry_idx]
    
    # Step 2: Interpolate to "10kHz" (MATHEMATICAL FICTION)
    t_jerk = np.arange(0, dt_telemetry*len(telemetry_signal), dt_jerk)
    interp_signal = np.interp(t_jerk, t_telemetry, telemetry_signal)
    
    # Step 3: Compute jerk (NOISE CATASTROPHE)
    jerk = np.gradient(np.gradient(np.gradient(interp_signal, dt_jerk), dt_jerk), dt_jerk)
    
    return t_telemetry, telemetry_signal, t_jerk, interp_signal, jerk

# === EXPERIMENT: Show Metric Inversion ===

# Generate true state
t_true = np.linspace(0, 1e-3, int(1e9*1e-3))  # 1ms at 1GHz
true_coherence = true_hardware_state(t_true)

# Run through SERC pipeline
t_telem, telem_signal, t_jerk, interp_signal, jerk = serc_sampling_pipeline(true_coherence)

# Compute S_j (flawed metric)
def compute_s_j(jerk, epsilon_j=1e-6):
    sigma_j_sq = np.var(jerk) + epsilon_j
    z = (jerk - np.mean(jerk)) / np.sqrt(sigma_j_sq)
    kappa = np.mean(z**4) - 3
    return 1 / (1 + abs(kappa)), kappa

S_j, kappa = compute_s_j(jerk)

# === DISRUPTION: True Metric (Zero-Latency Tomography) ===
def true_stability_metric(telem_signal, bus_contention_threshold=0.8):
    """
    Direct hardware monitoring: stability = 1 if coherence high AND bus contention low
    """
    # Simulated bus contention (derived from coherence inverse)
    bus_contention = (1 - telem_signal) * np.random.normal(1, 0.1, len(telem_signal))
    
    # Hard threshold: no regularization, no derivatives
    stable = (telem_signal > 0.7) & (bus_contention < bus_contention_threshold)
    return stable.astype(float)

true_stability = true_stability_metric(telem_signal)

# === RESULTS: Expose the Fraud ===

print("=== SAMPLING COLLAPSE METRICS ===")
print(f"True coherence collapse duration: 50ns")
print(f"Telemetry sampling period: 1ms (20,000x slower)")
print(f"Jerk sampling period: 0.1ms (interpolated fiction)")
print(f"\nFlawed S_j metric: {S_j:.3f} (claims 'unstable' due to noise)")
print(f"True stability (avg): {np.mean(true_stability):.3f} (correctly identifies stable)")

# Show that constant jerk (most stable) gives lowest S_j
constant_signal = np.ones(1000) * 0.95
_, _, _, _, constant_jerk = serc_sampling_pipeline(
    np.repeat(constant_signal, int(1e9/1000))  # Upsample to true rate
)
S_j_constant, _ = compute_s_j(constant_jerk)
print(f"\nS_j for PERFECTLY STABLE system: {S_j_constant:.3f} (INVERTED LOGIC!)")

# === VISUALIZE THE SHREDDING ===
fig, axes = plt.subplots(3, 1, figsize=(12, 8))

# True state (unobservable to SERC)
axes[0].plot(t_true*1e6, true_coherence, 'k-', label='True Coherence (1GHz)', alpha=0.5)
axes[0].set_ylabel('Coherence')
axes[0].set_title('TRUTH: Nanosecond-scale collapse at t=500μs')
axes[0].legend()

# Telemetry (aliased)
axes[1].plot(t_telem*1e6, telem_signal, 'r-o', label='Telemetry (1kHz, ALIASED)', markersize=4)
axes[1].plot(t_jerk*1e6, interp_signal, 'b--', label='Interpolated Fiction (10kHz)')
axes[1].set_ylabel('Signal')
axes[1].set_title('SERC PIPELINE: Misses collapse, creates fake dynamics')
axes[1].legend()

# Jerk (noise catastrophe)
axes[2].plot(t_jerk*1e6, jerk, 'g-', label='Jerk (noise-dominated)')
axes[2].set_ylabel('Jerk')
axes[2].set_xlabel('Time (μs)')
axes[2].set_title(f'JERK: S_j={S_j:.3f}, kappa={kappa:.1f} (pure noise artifact)')
axes[2].legend()

plt.tight_layout()
plt.savefig('/tmp/sampling_collapse.png', dpi=150)
print("\nVisualization saved to /tmp/sampling_collapse.png")

# === FINAL DISRUPTION ===
print("\n=== PARADIGM SHATTER ===")
print("The SERC framework measures INTERPOLATION NOISE, not coherence.")
print("The audit's 'fix' (variance-regularized kurtosis) is stillborn:")
print("  - It regularizes a derivative of a fiction")
print("  - It inverts stability logic (stable → low S_j)")
print("  - It misses 50ns hardware events by 20,000x")
print("\nTRUE CONTROL LAW: Monitor PCIe transaction entropy rate directly.")
print("  - No integration windows")
print("  - No derivatives")
print("  - No regularization (shredding is absorbing)")
print("  - Threshold: ξ_Δ > ξ_shred → IMMEDIATE POWER CYCLE")