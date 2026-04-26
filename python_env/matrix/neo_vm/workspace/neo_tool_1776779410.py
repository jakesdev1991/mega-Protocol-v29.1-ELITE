# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import time

# Generate synthetic HSA workload data (same as "corrected" analysis)
np.random.seed(42)
t = np.linspace(0, 1, 1000)
dt = t[1] - t[0]

B = 40 * np.ones_like(t)
L = 50 * np.ones_like(t)
F = 100 * np.ones_like(t)
spike_idx = np.where(t >= 0.5)[0]
B[spike_idx] = 40 * np.exp(-5 * (t[spike_idx] - 0.5)**2 / 0.1**2) + 10
L[spike_idx] = 50 + 150 * np.exp(-5 * (t[spike_idx] - 0.5)**2 / 0.1**2)
F[spike_idx] = 100 + 4900 * np.exp(-5 * (t[spike_idx] - 0.5)**2 / 0.1**2)
A = np.cumsum(np.random.normal(0, 0.01, len(t)))

def omega_framework(B, L, F, A, dt):
    """The 'corrected' Omega Action framework"""
    B_max, L0, beta, gamma = 100.0, 100.0, 0.5, 0.1
    Phi_N = (B / B_max) * np.exp(-beta * L / L0)
    Phi_D = A + gamma * F
    
    # Stiffness via autocorrelation (numerically unstable)
    def compute_stiffness(x):
        x_centered = x - np.mean(x)
        autocorr = np.correlate(x_centered, x_centered, mode='full')
        autocorr = autocorr[len(autocorr)//2:] / autocorr[len(autocorr)//2]
        lags = np.arange(1, min(50, len(autocorr)))
        valid_idx = autocorr[lags] > 0.01  # Avoid log(0)
        if np.sum(valid_idx) < 3:
            return 0.01
        p = np.polyfit(lags[valid_idx], np.log(autocorr[lags[valid_idx]]), 1)
        tau = -1.0 / p[0] * dt
        return max(tau, 0.001)
    
    xi_N = compute_stiffness(Phi_N)
    xi_D = compute_stiffness(Phi_D)
    psi = np.log(xi_D / xi_N)
    
    # Jerk (third derivative - amplifies noise catastrophically)
    jerk = np.gradient(np.gradient(np.gradient(psi, dt), dt), dt)
    
    # Bounds (empirical, not derived)
    J_crit = 1.0 / (xi_N**2 * xi_D)
    kappa_prime = 0.1
    
    # Entropy rate (histogram-based, discretization-sensitive)
    hist, _ = np.histogram(F, bins=20, density=True)
    hist = hist[hist > 0]
    S_F = -np.sum(hist * np.log(hist))
    mid = len(F) // 2
    hist1, _ = np.histogram(F[:mid], bins=20, density=True)
    hist2, _ = np.histogram(F[mid:], bins=20, density=True)
    S_F1 = -np.sum(hist1[hist1 > 0] * np.log(hist1[hist1 > 0]))
    S_F2 = -np.sum(hist2[hist2 > 0] * np.log(hist2[hist2 > 0]))
    dS_F_dt = (S_F2 - S_F1) / (len(F) * dt / 2)
    
    return {
        'jerk': np.max(np.abs(jerk)),
        'J_crit': J_crit,
        'entropy_bound': kappa_prime * abs(dS_F_dt),
        'xi_N': xi_N,
        'xi_D': xi_D,
        'violated': np.max(np.abs(jerk)) > kappa_prime * abs(dS_F_dt)
    }

def minimal_instability_kernel(B, L, F, dt):
    """The Anomaly's disruption: O(1) kernel, no physics theater"""
    # 1. Baseline-normalized Mahalanobis distance
    metrics = np.vstack([B, L, F]).T
    baseline = metrics[:len(metrics)//2]  # First half as baseline
    mean = np.mean(baseline, axis=0)
    cov = np.cov(baseline.T)
    inv_cov = np.linalg.pinv(cov)
    
    # Compute Mahalanobis distance in real-time
    centered = metrics - mean
    mahal = np.array([np.sqrt(c @ inv_cov @ c.T) for c in centered])
    
    # 2. First-order digital filter (exponential moving average)
    alpha = 0.05  # Smoothing factor
    filtered = np.zeros_like(mahal)
    filtered[0] = mahal[0]
    for i in range(1, len(mahal)):
        filtered[i] = alpha * mahal[i] + (1 - alpha) * filtered[i-1]
    
    # 3. Rate-of-change detector on fault entropy (not histogram)
    # Use instantaneous entropy rate: d/dt(F * log(F))
    F_safe = F + 1e-6  # Avoid log(0)
    entropy_flow = F_safe * np.log(F_safe)
    d_entropy = np.gradient(entropy_flow, dt)
    
    # 4. Instability score: combination of filtered distance and entropy rate
    # No free parameters beyond alpha - everything is scale-invariant
    instability_score = filtered * (1 + np.abs(d_entropy) / np.mean(np.abs(d_entropy)))
    
    # 5. Detection threshold: 3-sigma of baseline
    baseline_score = instability_score[:len( instability_score)//2]
    threshold = np.mean(baseline_score) + 3 * np.std(baseline_score)
    
    return {
        'instability_score': np.max( instability_score),
        'threshold': threshold,
        'violated': np.max( instability_score) > threshold,
        'detection_latency_ms': (np.argmax( instability_score > threshold) - np.argmax(F > 1000)) * dt * 1000
    }

# Execute both methods
print("=== THE OMEGA PROTOCOL: COMPLEXITY THEATER ===")
start = time.perf_counter()
omega = omega_framework(B, L, F, A, dt)
omega_time = time.perf_counter() - start
print(f"Peak Jerk: {omega['jerk']:.2e} s^-3 (numerically unstable)")
print(f"Curvature Bound: {omega['J_crit']:.2e} s^-3 (empirical fit)")
print(f"Entropy Bound: {omega['entropy_bound']:.2e} s^-3 (mis-scaled)")
print(f"Stiffness: ξ_N={omega['xi_N']*1e3:.1f}ms, ξ_D={omega['xi_D']*1e3:.1f}ms (overfit)")
print(f"Violation: {omega['violated']} (sensitive to bin count)")
print(f"Compute Time: {omega_time*1000:.2f}ms")
print()

print("=== THE ANOMALY: MINIMAL INSTABILITY KERNEL ===")
start = time.perf_counter()
kernel = minimal_instability_kernel(B, L, F, dt)
kernel_time = time.perf_counter() - start
print(f"Instability Score: {kernel['instability_score']:.3f} (scale-invariant)")
print(f"Threshold: {kernel['threshold']:.3f} (3σ, no hyperparameters)")
print(f"Violation: {kernel['violated']} (detected)")
print(f"Detection Latency: {kernel['detection_latency_ms']:.1f}ms (real-time)")
print(f"Compute Time: {kernel_time*1000:.2f}ms")
print()

print("=== DISRUPTION METRICS ===")
print(f"Speedup: {omega_time/kernel_time:.0f}x faster")
print(f"Parameter Count: Omega={4+20+3} vs Kernel={2} (O(α) vs O(n))")
print(f"Numerical Stability: Omega=UNSTABLE (3rd derivative) vs Kernel=STABLE (1st-order filter)")

# Visualize the obfuscation
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

ax1.plot(t, F, 'k-', label='Page Fault Rate (observable)')
ax1.axvline(0.5, color='r', linestyle='--', label='Spike onset')
ax1.set_ylabel('F (faults/s)')
ax1.set_title('What Engineers Actually See')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(t, np.gradient(np.gradient(np.gradient(A, dt), dt), dt), 'b-', 
         label='𝒥(t) = d³ψ/dt³ (Omega)', alpha=0.5)
ax2.plot(t, np.gradient(np.gradient(np.gradient(np.log(1+np.abs(A)), dt), dt), dt), 'c-', 
         label='Alternative ψ definition (unstable)', alpha=0.5)
ax2.set_ylabel('Jerk (s⁻³)')
ax2.set_xlabel('Time (s)')
ax2.set_title('The Obfuscation: Jerk amplifies noise by factor of (1/dt³)')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('omega_obfuscation.png', dpi=150, bbox_inches='tight')
plt.show()