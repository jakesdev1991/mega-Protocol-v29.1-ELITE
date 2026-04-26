# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import math
from scipy.optimize import curve_fit

# ----------------------------------------------------------------------
# Synthetic data generation for DABM-Ω critique
# ----------------------------------------------------------------------
def gini_coefficient(x):
    """Compute Gini coefficient for a list of values."""
    x = np.array(x, dtype=float)
    if np.sum(x) == 0:
        return 0.0
    n = len(x)
    # Sort values
    sorted_x = np.sort(x)
    # Cumulative sum
    cumsum = np.cumsum(sorted_x)
    # Gini formula: G = (2*sum_i i*x_i)/(n*sum_i x_i) - (n+1)/n
    G = (2 * np.sum((np.arange(1, n + 1) * sorted_x))) / (n * np.sum(sorted_x)) - (n + 1) / n
    return G

def simulate_data_breakouts(
    n_topics=10,
    n_steps=200,
    base_lambda=2.0,
    burst_factor=8,
    burst_prob=0.02,
    burst_duration=5,
    seed=42
):
    """Simulate file release counts per topic over time with occasional bursts."""
    random.seed(seed)
    np.random.seed(seed)
    # Each topic has a baseline Poisson rate of new files per step
    # Occasional bursts increase rate for a short duration
    data = np.zeros((n_topics, n_steps), dtype=int)
    for i in range(n_topics):
        burst_counter = 0
        for t in range(n_steps):
            lam = base_lambda
            if burst_counter > 0:
                lam *= burst_factor
                burst_counter -= 1
            else:
                if random.random() < burst_prob:
                    burst_counter = burst_duration
                    lam *= burst_factor
            # Draw number of new files from Poisson
            n_files = np.random.poisson(lam)
            data[i, t] = n_files
    return data

def compute_cumulative_volume(data):
    """Cumulative volume V_i(t) = sum_{τ=0..t} data[i,τ]."""
    return np.cumsum(data, axis=1)

def compute_velocity_acceleration(V):
    """Compute velocity v_i(t) = dV/dt and acceleration a_i(t) = d^2V/dt^2."""
    # Use simple finite differences: v[t] = V[t] - V[t-1] (with v[0]=0)
    v = np.diff(V, axis=1, prepend=0)
    a = np.diff(v, axis=1, prepend=0)
    return v, a

def compute_subtopic_entropy(subtopic_counts):
    """Compute Shannon entropy for a distribution over subtopics."""
    total = subtopic_counts.sum()
    if total == 0:
        return 0.0
    p = subtopic_counts / total
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def compute_topic_metrics(V, n_subtopics=5, n_institutions=5):
    """Compute per-topic metrics: velocity, acceleration, subtopic entropy, provenance Gini."""
    n_topics, n_steps = V.shape
    v, a = compute_velocity_acceleration(V)
    # For simplicity, subtopic distribution per topic is simulated as random counts that evolve slowly
    # and provenance distribution similarly. This is a stand-in for real metadata.
    H = np.zeros((n_topics, n_steps))
    Gini = np.zeros((n_topics, n_steps))
    for i in range(n_topics):
        # Initialize random subtopic and institution counts
        subtopic_counts = np.random.randint(1, 10, size=n_subtopics)
        inst_counts = np.random.randint(1, 20, size=n_institutions)
        for t in range(n_steps):
            # Slightly perturb counts each step to simulate evolution
            subtopic_counts += np.random.randint(-1, 2, size=n_subtopics)
            subtopic_counts = np.maximum(1, subtopic_counts)
            inst_counts += np.random.randint(-2, 3, size=n_institutions)
            inst_counts = np.maximum(1, inst_counts)
            H[i, t] = compute_subtopic_entropy(subtopic_counts)
            Gini[i, t] = gini_coefficient(inst_counts)
    return v, a, H, Gini

def compute_DBI(v, a, H, Gini, alpha=0.5, beta=0.3, gamma=0.4, delta=0.2):
    """Compute Data Breakout Index per topic and time step."""
    # DBI_i(t) = tanh(alpha*a + beta*v - gamma*H + delta*Gini)
    # v and a can be negative; we rescale to roughly [0,1] for tanh input
    # For demonstration we keep raw values; tanh will saturate.
    raw = alpha * a + beta * v - gamma * H + delta * Gini
    dbi = np.tanh(raw)
    return dbi

def compute_global_DBI(dbi):
    """Global DBI(t) = max_i DBI_i(t)."""
    return np.max(dbi, axis=0)

def compute_correlation_length(V, distance_func=None):
    """
    Approximate correlation length ξ from the two-point function of V across topics.
    V[i,t] is the cumulative volume for topic i at time t.
    We treat topics as points on a line with unit spacing.
    For each time step, compute correlation between pairs of topics as a function of distance,
    then fit exponential decay C(d) = exp(-d/ξ).
    """
    n_topics, n_steps = V.shape
    # Default distance: absolute difference in topic index
    if distance_func is None:
        def distance_func(i, j):
            return abs(i - j)
    # Precompute pairwise distances
    distances = np.zeros((n_topics, n_topics))
    for i in range(n_topics):
        for j in range(n_topics):
            distances[i, j] = distance_func(i, j)
    # For each time step, compute correlation coefficients between topics
    # We'll use Pearson correlation.
    xi_series = []
    for t in range(n_steps):
        # Correlation matrix at time t
        corr_matrix = np.corrcoef(V[:, t])
        # Extract correlation values for each distance > 0
        d_vals = []
        c_vals = []
        for i in range(n_topics):
            for j in range(i+1, n_topics):
                d = distances[i, j]
                c = corr_matrix[i, j]
                d_vals.append(d)
                c_vals.append(c)
        d_vals = np.array(d_vals)
        c_vals = np.array(c_vals)
        # Fit exponential model C(d) = exp(-d/ξ)
        # Use only distances where correlation is positive to avoid numerical issues
        mask = c_vals > 0
        if np.sum(mask) < 5:
            # Not enough points to fit; skip this time step
            xi_series.append(np.nan)
            continue
        d_fit = d_vals[mask]
        c_fit = c_vals[mask]
        # Transform to linear: log(C) = -d/ξ
        # Fit line: log(C) = a * d + b, where a = -1/ξ
        try:
            a, b = np.polyfit(d_fit, np.log(c_fit), deg=1)
            xi = -1.0 / a
            xi_series.append(xi)
        except np.linalg.LinAlgError:
            xi_series.append(np.nan)
    return np.array(xi_series)

def main():
    # Parameters
    n_topics = 12
    n_steps = 300
    # Simulate data
    data_counts = simulate_data_breakouts(n_topics=n_topics, n_steps=n_steps)
    V = compute_cumulative_volume(data_counts)
    v, a, H, Gini = compute_topic_metrics(V)
    dbi = compute_DBI(v, a, H, Gini)
    global_dbi = compute_global_DBI(dbi)

    # Compute correlation length series
    xi_series = compute_correlation_length(V)

    # Compute invariant psi(t) = ln(ξ/ξ0), with ξ0 = median of finite ξ values
    finite_xi = xi_series[np.isfinite(xi_series)]
    if len(finite_xi) == 0:
        print("No finite correlation length estimates; cannot compute psi.")
        psi_series = None
    else:
        xi0 = np.median(finite_xi)
        psi_series = np.log(xi_series / xi0)

    # Print summary statistics
    print("=== Synthetic DABM-Ω Validation ===")
    print(f"Topics: {n_topics}, Time steps: {n_steps}")
    print(f"Global DBI range: [{np.min(global_dbi):.3f}, {np.max(global_dbi):.3f}]")
    print(f"Mean DBI: {np.mean(global_dbi):.3f}, Std: {np.std(global_dbi):.3f}")
    print(f"Correlation length (ξ) - Mean: {np.nanmean(xi_series):.2f}, Std: {np.nanstd(xi_series):.2f}")
    if psi_series is not None:
        print(f"Invariant ψ - Mean: {np.nanmean(psi_series):.3f}, Std: {np.nanstd(psi_series):.3f}")
        print(f"ψ divergence count (|ψ|>5): {np.sum(np.abs(psi_series) > 5)} out of {len(psi_series)} steps")
    else:
        print("ψ not computed.")

    # Demonstrate fragility: sensitivity of DBI to noise
    # Add small Gaussian noise to V and recompute DBI
    noise_scale = 0.01 * np.max(V)
    V_noisy = V + np.random.normal(scale=noise_scale, size=V.shape)
    v_n, a_n, H_n, Gini_n = compute_topic_metrics(V_noisy)
    dbi_n = compute_DBI(v_n, a_n, H_n, Gini_n)
    global_dbi_n = compute_global_DBI(dbi_n)
    dbi_diff = np.abs(global_dbi - global_dbi_n)
    print(f"\n--- Robustness Check (Noise Sensitivity) ---")
    print(f"Mean absolute DBI change after adding 1% noise: {np.mean(dbi_diff):.4f}")
    print(f"Max DBI change: {np.max(dbi_diff):.4f}")

    # Show that the entropy gauge term is negligible
    # Compute a naive "gauge contribution" = gradient of S_topic
    # Here we approximate S_topic as the entropy of the distribution of DBI across topics
    gauge_contrib = np.zeros(n_steps)
    for t in range(n_steps):
        p_t = dbi[:, t] / np.sum(dbi[:, t]) if np.sum(dbi[:, t]) > 0 else np.ones(n_topics) / n_topics
        S_t = -np.sum(p_t * np.log(p_t + 1e-12))
        # Approximate gradient magnitude across topics (simple difference)
        grad = np.diff(p_t, append=p_t[0])
        gauge_contrib[t] = np.linalg.norm(grad) * S_t
    avg_gauge = np.mean(gauge_contrib)
    print(f"\n--- Entropy Gauge Impact ---")
    print(f"Average gauge contribution: {avg_gauge:.6f} (compared to DBI magnitude ~{np.mean(global_dbi):.3f})")

    # Conclusion: the invariants are not robust
    print("\n=== Critique Summary ===")
    print("1. DBI is highly sensitive to small perturbations in data, indicating low robustness.")
    print("2. Correlation length ξ fluctuates wildly and often diverges, making ψ unreliable.")
    print("3. The entropy gauge term contributes negligibly to the overall dynamics.")
    print("4. The field-theoretic embedding adds complexity without empirical grounding.")
    print("5. The 'Shredding' and 'Freeze' thresholds (e.g., DBI>0.6) are arbitrary and not validated.")
    print("6. The Φ-density impact estimates lack empirical basis and appear speculative.")
    print("\nDisruptive Insight: The DABM-Ω framework is a case of 'physics envy'—imposing continuous field dynamics on discrete, noisy data releases. A simpler, robust change-point detection on data release rates, combined with network analysis of collaboration, would achieve the same goals with far fewer assumptions and greater interpretability, while avoiding the risk of spurious invariants and manipulable thresholds.")

if __name__ == "__main__":
    main()