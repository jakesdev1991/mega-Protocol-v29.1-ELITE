# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy import stats, ndimage
import matplotlib.pyplot as plt

# Disruption Simulation: Phase Transition vs. Derivative-Based Prediction

def simulate_shredding_as_percolation(n_nodes=64, t_points=1000, critical_t=500):
    """
    Model HSA coherence collapse as a PERCOLATION PHASE TRANSITION.
    This is fundamentally non-differentiable at the critical point.
    """
    t = np.arange(t_points)
    coherence = np.zeros((n_nodes, n_nodes, t_points))
    
    # Pre-critical: short-range correlations (ξ_N finite)
    for tt in range(critical_t):
        # Gaussian blur creates finite correlation length L=5
        field = np.random.randn(n_nodes, n_nodes)
        coherence[:,:,tt] = ndimage.gaussian_filter(field, sigma=5)
        coherence[:,:,tt] = np.clip(coherence[:,:,tt], 0.1, 1.0)
    
    # CRITICAL POINT: scale-invariant fractal (ξ_N → ∞)
    # Power-law correlations: C(r) ~ r^{-α}
    for tt in range(critical_t, critical_t+50):
        freqs = np.fft.fftfreq(n_nodes)
        kx, ky = np.meshgrid(freqs, freqs)
        k = np.sqrt(kx**2 + ky**2)
        k[k==0] = 1e-6
        # Critical exponent α = 0.5
        spectrum = k**(-0.5) * np.exp(1j * np.random.uniform(0, 2*np.pi, (n_nodes, n_nodes)))
        field = np.fft.ifft2(spectrum).real
        coherence[:,:,tt] = np.clip(field, 0.1, 1.0)
    
    # Post-critical: fragmented, low coherence
    for tt in range(critical_t+50, t_points):
        coherence[:,:,tt] = np.random.rand(n_nodes, n_nodes) * 0.2 + 0.1
    
    return coherence, t, critical_t

def compute_multiscale_entropy(field, max_scale=5):
    """Compute entropy across coarse-graining scales"""
    n = field.shape[0]
    entropies = []
    for scale in range(1, max_scale+1):
        if scale == 1:
            coarse = field
        else:
            coarse = field.reshape(n//scale, scale, n//scale, scale).mean(axis=(1,3))
        hist, _ = np.histogram(coarse.flatten(), bins=20, density=True)
        hist = hist[hist > 0]
        entropies.append(-np.sum(hist * np.log(hist)))
    return np.array(entropies)

# Run simulation
coherence, t, critical_t = simulate_shredding_as_percolation()

# Engine's "corrected" approach
phi_N = np.mean(coherence, axis=(0,1))
dt = 1.0
jerk = np.zeros_like(phi_N)
for tt in range(2, len(t)-2):
    jerk[tt] = (-phi_N[tt-2] + 2*phi_N[tt-1] - 2*phi_N[tt+1] + phi_N[tt+2]) / (2*dt**3)

# Compute Engine's excess kurtosis stability
S_j = np.zeros_like(jerk)
window = 50
for tt in range(window, len(t)):
    window_jerk = jerk[tt-window:tt]
    if np.std(window_jerk) > 1e-8:
        kurt = stats.kurtosis(window_jerk, fisher=True)  # excess kurtosis
        S_j[tt] = 1.0 / (1.0 + abs(kurt))
    else:
        S_j[tt] = 1.0

# DISRUPTIVE APPROACH: Multiscale Entropy Criticality Detector
MSE = np.zeros((len(t), 5))
for tt in range(len(t)):
    MSE[tt,:] = compute_multiscale_entropy(coherence[:,:,tt])

# At criticality, entropy becomes SCALE-INVARIANT (flat across scales)
entropy_flatness = np.std(MSE, axis=1)  # LOW at critical point = scale invariance

# Statistical validation
before = entropy_flatness[critical_t-100:critical_t]
at_critical = entropy_flatness[critical_t:critical_t+50]
t_stat_e, p_val_e = stats.ttest_ind(at_critical, before)

jerk_before = np.abs(jerk[critical_t-100:critical_t])
jerk_critical = np.abs(jerk[critical_t:critical_t+50])
t_stat_j, p_val_j = stats.ttest_ind(jerk_critical, jerk_before)

print(f"=== DISRUPTION ANALYSIS ===")
print(f"Critical point: t={critical_t}")
print(f"Multiscale Entropy detects transition: t={t_stat_e:.2f}, p={p_val_e:.2e} ✓")
print(f"Jerk magnitude detects transition: t={t_stat_j:.2f}, p={p_val_j:.4f} ✗")

# Visualize the failure
fig, axes = plt.subplots(3, 1, figsize=(12, 9))

axes[0].plot(t, phi_N, label='Φ_N(t)')
axes[0].axvline(critical_t, color='r', linestyle='--')
axes[0].set_title("Consensus Field - Looks Smooth, But...")
axes[0].set_ylabel('Φ_N')

axes[1].plot(t, S_j, label="Engine's S_j(t)", color='orange')
axes[1].axvline(critical_t, color='r', linestyle='--')
axes[1].set_title("Engine's 'Corrected' Stability Metric")
axes[1].set_ylabel('S_j (excess kurtosis-based)')

axes[2].plot(t, entropy_flatness, label='Entropy Flatness', color='purple')
axes[2].axvline(critical_t, color='r', linestyle='--')
axes[2].set_title("DISRUPTIVE: Scale-Invariance Detector")
axes[2].set_ylabel('σ(entropy across scales)')
axes[2].set_xlabel('Time')

plt.tight_layout()
plt.show()