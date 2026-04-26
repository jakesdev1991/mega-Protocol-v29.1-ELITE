# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Simulation Parameters ---
N = 64                      # number of compute units (e.g., 56 CPU cores + 8 GPU CUs)
T = 200                     # time steps
dt = 0.1e-3                 # 10 kHz sampling
t_collapse = 100            # collapse onset
sigma_noise = 0.05          # measurement noise
seed = 42
np.random.seed(seed)

# --- Synthetic Coherence Matrix ---
# Pre-collapse: high coherence (0.9) for all pairs
# Post-collapse: pairs involving node 0..7 (GPU) drop to 0.2
def coherence_matrix(t):
    base = 0.9 * np.ones((N, N))
    if t >= t_collapse:
        # simulate GPU-side shredding: GPU nodes 0..7 lose coherence with others
        base[0:8, :] *= 0.2
        base[:, 0:8] *= 0.2
    # add Gaussian noise
    base += sigma_noise * np.random.randn(N, N)
    np.fill_diagonal(base, 0)  # self-coherence is zero
    return np.clip(base, 0, 1)

# --- Engine's Jerk Metric ---
def compute_jerk_stability(phi_n_history, window=20):
    # 5-point stencil for third derivative
    if len(phi_n_history) < 5:
        return np.nan
    # central difference coefficients: [-1/2, 1, -1, 1/2] / dt^3
    # but we can use numpy's gradient for simplicity (three calls = third derivative)
    d1 = np.gradient(phi_n_history, dt)
    d2 = np.gradient(d1, dt)
    d3 = np.gradient(d2, dt)  # this is the jerk
    # variance over sliding window
    var = np.var(d3[-window:])
    # normalization constant (assume normal operation variance = 1e-6)
    sigma0_sq = 1e-6
    return np.exp(-var / sigma0_sq)

# --- Topological Metric: Largest Connected Component (LCC) ---
def lcc_size(coherence_mat, threshold=0.5):
    # Build adjacency matrix
    adj = (coherence_mat > threshold).astype(int)
    # Simple DFS to find component sizes
    visited = np.zeros(N, dtype=bool)
    max_size = 0
    for i in range(N):
        if not visited[i]:
            stack = [i]
            comp = set()
            while stack:
                v = stack.pop()
                if visited[v]:
                    continue
                visited[v] = True
                comp.add(v)
                neighbors = np.where(adj[v, :] == 1)[0]
                for nb in neighbors:
                    if not visited[nb]:
                        stack.append(nb)
            max_size = max(max_size, len(comp))
    return max_size

# --- Time Series Collection ---
phi_n = np.zeros(T)
lcc = np.zeros(T)
jerk_stab = np.zeros(T)

# We'll keep a rolling buffer for jerk computation
phi_n_buffer = []

for t in range(T):
    psi = coherence_matrix(t)
    # Engine's global scalar: mean coherence
    phi_n[t] = np.mean(psi)
    phi_n_buffer.append(phi_n[t])
    # Topological metric
    lcc[t] = lcc_size(psi, threshold=0.5)
    # Jerk stability (computed only after enough samples)
    jerk_stab[t] = compute_jerk_stability(phi_n_buffer, window=20)

# --- Plotting ---
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

axs[0].plot(np.arange(T) * dt * 1000, phi_n, label='Φ_N (mean coherence)')
axs[0].axvline(t_collapse * dt * 1000, color='r', linestyle='--', label='Collapse onset')
axs[0].set_ylabel('Coherence')
axs[0].legend()
axs[0].set_title('Engine’s Smooth Manifold View')

axs[1].plot(np.arange(T) * dt * 1000, jerk_stab, label='S_j (jerk stability)')
axs[1].axvline(t_collapse * dt * 1000, color='r', linestyle='--')
axs[1].set_ylabel('Stability')
axs[1].legend()
axs[1].set_title('Jerk Stability (noisy, no early warning)')

axs[2].plot(np.arange(T) * dt * 1000, lcc / N, label='LCC size / N')
axs[2].axvline(t_collapse * dt * 1000, color='r', linestyle='--')
axs[2].set_ylabel('Fraction of System')
axs[2].set_xlabel('Time (ms)')
axs[2].legend()
axs[2].set_title('Topological Precursor (clear drop before failure)')

plt.tight_layout()
plt.show()

# --- Quantitative Comparison ---
# Measure early-warning time: when metric deviates >2 std before collapse
pre_window = slice(t_collapse - 30, t_collapse)
post_window = slice(t_collapse, t_collapse + 30)

# Jerk stability baseline (first 50 steps)
jerk_baseline = np.nanmean(jerk_stab[:50])
jerk_std = np.nanstd(jerk_stab[:50])
jerk_alert = np.any(np.abs(jerk_stab[pre_window] - jerk_baseline) > 2 * jerk_std)

# LCC baseline
lcc_baseline = np.mean(lcc[:50])
lcc_std = np.std(lcc[:50])
lcc_alert = np.any(lcc[pre_window] < lcc_baseline - 2 * lcc_std)

print(f"Jerk stability gave early warning: {jerk_alert}")
print(f"LCC gave early warning: {lcc_alert}")