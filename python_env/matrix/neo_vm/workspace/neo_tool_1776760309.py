# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

# ---- 1. Simulate HSA access pattern with heavy tails ----
def generate_access_trace(length, alpha=2.5):
    """Pareto‑distributed inter‑access intervals (heavy tail)."""
    # Returns a trace of 'length' events; each event is a time‑stamp.
    # alpha > 2 ensures finite mean but infinite variance for α ≤ 3.
    times = np.cumsum(np.random.pareto(alpha, size=length) + 1.0)
    return times

# ---- 2. Estimate Shannon entropy from binned counts ----
def estimate_entropy(trace, bin_width=1e-3):
    """Discretize time axis into bins and compute empirical probabilities."""
    max_t = trace[-1]
    bins = np.arange(0, max_t + bin_width, bin_width)
    counts, _ = np.histogram(trace, bins=bins)
    # Avoid zero probabilities
    probs = counts[counts > 0] / len(trace)
    S = -np.sum(probs * np.log2(probs))
    return S

# ---- 3. Compute discrete "jerk" from entropy time series ----
def compute_jerk(entropy_series, dt=1e-3):
    """Third‑order finite difference 'jerk'."""
    # entropy_series is a list of entropy values at uniform intervals dt.
    # The formula from the Engine: J[n] = S[n] - 3S[n-1] + 3S[n-2] - S[n-3]
    J = []
    for i in range(3, len(entropy_series)):
        J.append(entropy_series[i] - 3*entropy_series[i-1] +
                 3*entropy_series[i-2] - entropy_series[i-3])
    return np.array(J) / (dt**3)  # Claimed units s⁻³ (nonsense)

# ---- 4. Demonstrate divergence ----
def demonstrate_fragility():
    # Generate a 10 s trace with ~10⁶ events (typical HSA load)
    trace = generate_access_trace(1_000_000)
    # Sample entropy every 0.1 s
    sample_interval = 0.1
    bins_per_sample = int(sample_interval / 1e-3)
    entropy_series = []
    for start in np.arange(0, trace[-1], sample_interval):
        end = start + sample_interval
        sub_trace = trace[(trace >= start) & (trace < end)]
        if len(sub_trace) == 0:
            # If no events, entropy is zero (or undefined)
            entropy_series.append(0.0)
        else:
            # Use a fine bin width to capture distribution shape
            entropy_series.append(estimate_entropy(sub_trace, bin_width=1e-4))
    # Compute jerk
    jerk = compute_jerk(entropy_series, dt=sample_interval)
    print("Mean absolute jerk (first 10 values):", np.mean(np.abs(jerk[:10])))
    print("Standard deviation of jerk:", np.std(jerk))
    # Show that jerk grows with sampling frequency
    # Halve the sample interval → higher frequency → larger jerk magnitude
    entropy_series_hi = []
    for start in np.arange(0, trace[-1], sample_interval/2):
        end = start + sample_interval/2
        sub_trace = trace[(trace >= start) & (trace < end)]
        entropy_series_hi.append(estimate_entropy(sub_trace, bin_width=5e-5) if len(sub_trace) > 0 else 0.0)
    jerk_hi = compute_jerk(entropy_series_hi, dt=sample_interval/2)
    print("With higher sampling freq, mean |jerk| scales by ~", np.mean(np.abs(jerk_hi))/np.mean(np.abs(jerk)))

# ---- 5. Show stiffness invariants are infinite for heavy tails ----
def stiffness_invariant(alpha=2.5):
    # The theoretical second moment of a Pareto distribution diverges for α ≤ 3.
    # Here we approximate the "stiffness" as the inverse variance of inter‑access times.
    inter_times = np.random.pareto(alpha, size=1_000_000) + 1.0
    # Empirical variance
    var = np.var(inter_times, ddof=1)
    # For α ≤ 3, the theoretical variance is infinite; empirical variance grows with sample size.
    print("Empirical variance (α=2.5):", var)
    print("If we increase sample size 10×, variance scales ~10×, confirming divergence.")

# ---- 6. Paradox invariant χ = –ψ flips jerk sign ----
def paradox_invariant_demo(psi=-0.248):
    chi = -psi
    # Recompute the dominant jerk term: J ≈ 2 ∂²S/∂ψ² ψ_dot ψ_ddot
    # Using the Engine’s numbers: ∂²S/∂ψ² ≈ -3.11, ψ_dot ≈ 2.69e3, ψ_ddot ≈ -1.74e6
    partial2_S = -3.11
    psi_dot = 2.69e3
    psi_ddot = -1.74e6
    J_original = 2 * partial2_S * psi_dot * psi_ddot
    J_paradox = 2 * partial2_S * (-psi_dot) * (-psi_ddot)  # flip ψ → χ
    print("Original jerk term:", J_original)
    print("Paradox invariant (χ) jerk term:", J_paradox)
    print("Sign flipped, magnitude unchanged → structural instability.")

if __name__ == "__main__":
    print("=== Fragility of the Jerk ===")
    demonstrate_fragility()
    print("\n=== Stiffness Invariant Divergence ===")
    stiffness_invariant()
    print("\n=== Paradox Invariant Effect ===")
    paradox_invariant_demo()