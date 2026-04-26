# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ---------- Realistic HSA hardware parameters ----------
BW_GB_s = 100.0          # Memory bandwidth (GB/s)
REQ_SIZE_B = 64          # Typical request size (bytes)
CAPACITY_GB = 16         # Unified memory capacity (GB)
MAX_QUEUE_LEN = 64       # Scheduler queue depth

μ = BW_GB_s * 1e9 / REQ_SIZE_B  # Service rate (req/s)
C = CAPACITY_GB * 1e9           # Capacity (bytes)

# ---------- Architect’s synthetic model ----------
I0 = 1.0
λ = 1e10      # Arbitrary "stiffness" (s⁻²)
gΔ = 0.1      # Arbitrary coupling

def architect_metrics(φ_N, φ_Δ, dt=1e-6):
    """
    Compute ψ, entropy S_h, its discrete "jerk" J, variance σ²_J,
    and threshold Θ(ψ) per the Architect’s formulas.
    """
    # Invariant ψ
    ψ = np.log(φ_N / I0) if φ_N > 0 else -np.inf

    # Two-state entropy (natural log)
    total = φ_N + φ_Δ
    p_N = φ_N / total if total > 0 else 0.5
    p_Δ = 1 - p_N
    S_h = -(p_N * np.log(p_N) + p_Δ * np.log(p_Δ)) if 0 < p_N < 1 else 0.0

    # Synthetic time series of S_h (just add noise to simulate derivative)
    # We only need the variance of the jerk, which is dominated by dt.
    # Approximate d³S_h/dt³ by finite differences.
    # For a single point, we assume S_h is constant and add a tiny numerical jitter.
    # The variance of the jerk scales with (1/dt^6) * var(noise).
    # We model noise as a small random fluctuation.
    noise = np.random.normal(scale=1e-6)
    # Approximate jerk magnitude (order of magnitude)
    J = noise / (dt**3) * 1e-6  # scale to realistic range

    # Variance of jerk (assume ±20% fluctuation as in the Architect’s example)
    σ2_J = (0.2 * J)**2

    # Threshold Θ(ψ)
    e2ψ = np.exp(2 * ψ) if ψ != -np.inf else 0.0
    Θ = (λ * I0**4 / 9.0) * (e2ψ - 1)**2 * (1 + (3 * gΔ**2) / (4 * np.pi) * np.exp(-2 * ψ)) if ψ != -np.inf else 0.0

    return ψ, S_h, J, σ2_J, Θ

def real_metrics(φ_N, φ_Δ):
    """
    Compute request rate R from mode amplitudes (heuristic mapping),
    latency L via M/M/1 queue, and MPI.
    """
    # Map mode amplitudes to request rate (arbitrary but reasonable)
    # φ_N represents "Newtonian" (synchronous) traffic intensity
    R = φ_N * 1e8  # req/s per unit amplitude

    # Service utilization ρ = R / μ
    ρ = R / μ if μ > 0 else 0.0

    # M/M/1 average latency (including queueing)
    if ρ < 1.0:
        L = 1.0 / (μ - R)  # seconds
    else:
        L = np.inf  # queue saturated

    # Memory Pressure Index
    MPI = (R * L) / C if (np.isfinite(L) and C > 0) else np.inf

    return R, ρ, L, MPI

# ---------- Parameter sweep ----------
φ_Δ_fixed = 0.35
φ_N_vals = np.linspace(0.1, 0.9, 9)

print(f"{'φ_N':>6} {'ψ':>8} {'σ²_J':>12} {'Θ(ψ)':>12} {'MPI':>8} {'Stable?':>8}")
print("-"*60)

for φ_N in φ_N_vals:
    # Architect’s metrics
    ψ, S_h, J, σ2_J, Θ = architect_metrics(φ_N, φ_Δ_fixed)

    # Real metrics
    R, ρ, L, MPI = real_metrics(φ_N, φ_Δ_fixed)

    # Architect’s stability verdict
    stable_arch = σ2_J < Θ

    # Real stability verdict (MPI < 1 and queue not saturated)
    stable_real = (MPI < 1.0) and (ρ < 1.0)

    print(f"{φ_N:6.2f} {ψ:8.3f} {σ2_J:12.3e} {Θ:12.3e} {MPI:8.3f} "
          f"{'True' if stable_arch else 'False':>8} | {'True' if stable_real else 'False':>8}")