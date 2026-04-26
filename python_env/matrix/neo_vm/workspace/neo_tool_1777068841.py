# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

def compute_phi_density(b0, H_cond, xi_N, xi_Delta, psi, R, R_max):
    """
    Compute the claimed Φ‑density metric:
      Φ_N = log2(b0 / H_cond) * xi_N
      Φ_Δ = psi * tanh(R / R_max) * xi_Delta
      Φ = Φ_N + Φ_Δ
    """
    # Guard against log(0) or negative arguments
    if H_cond <= 0 or b0 <= 0:
        return np.nan, np.nan, np.nan
    phi_N = np.log2(b0 / H_cond) * xi_N
    # If R is extreme, tanh saturates at ±1; psi can flip sign
    phi_Delta = psi * np.tanh(R / R_max) * xi_Delta
    phi = phi_N + phi_Delta
    return phi_N, phi_Delta, phi

def simulate_random_conditions(trials=10000):
    """
    Simulate random but plausible conditions for a child's shoe:
    - b0: 0th Betti number (topological components) – small integer
    - H_cond: conditional entropy – can be large due to sensor noise
    - xi_N, xi_Delta: stiffness terms in [0,1]
    - psi = ln(phi_n) – phi_n is undefined; we treat phi_n as random >0
    - R: effective Ricci curvature (nonsensical for a shoe but we treat as random)
    - R_max: curvature bound
    """
    results = []
    for _ in range(trials):
        # Topological component count: small integer 0–5 (0 means disconnected sole)
        b0 = random.choice([0, 1, 2, 3, 4, 5])
        # Sensor noise can make conditional entropy arbitrarily large
        H_cond = 10 ** random.uniform(-3, 3)  # range 0.001 to 1000 bits
        # Stiffness terms
        xi_N = random.random()
        xi_Delta = random.random()
        # phi_n is undefined; we model it as a random factor in [0.5, 2]
        phi_n = random.uniform(0.5, 2.0)
        psi = np.log(phi_n)  # can be negative if phi_n < 1
        # Ricci curvature (nonsensical but we treat as random)
        R_max = 1.0
        R = random.uniform(-3 * R_max, 3 * R_max)  # exceed bounds
        phi_N, phi_Delta, phi = compute_phi_density(b0, H_cond, xi_N, xi_Delta, psi, R, R_max)
        results.append((b0, H_cond, phi_N, phi_Delta, phi))
    return results

def analyze_results(results):
    """
    Show how often the metric is non‑physical (negative, NaN, infinite) even if we
    pretend the invariants hold.
    """
    neg_phi_N = sum(1 for r in results if r[2] < -1e-6)
    neg_phi = sum(1 for r in results if r[4] < -1e-6)
    nan_phi = sum(1 for r in results if np.isnan(r[4]))
    # Check the "Betti-Shannon Ratio" invariant (even if we define it loosely)
    # Here we pretend Betti(L) = b0 + 1 and Shannon(L|Context) = H_cond
    invariant_violated = sum(1 for r in results if (r[0] + 1) <= r[1])
    total = len(results)
    print(f"Total simulations: {total}")
    print(f"Φ_N negative: {neg_phi_N} ({100*neg_phi_N/total:.2f}%)")
    print(f"Φ negative: {neg_phi} ({100*neg_phi/total:.2f}%)")
    print(f"Φ NaN: {nan_phi} ({100*nan_phi/total:.2f}%)")
    print(f"Betti‑Shannon invariant violated: {invariant_violated} ({100*invariant_violated/total:.2f}%)")
    print("\n--- Example of catastrophic failure ---")
    # Find a case where phi is extremely negative
    worst = min(results, key=lambda x: x[4] if not np.isnan(x[4]) else np.inf)
    b0, H_cond, phi_N, phi_Delta, phi = worst
    print(f"b0={b0}, H_cond={H_cond:.3f}, phi_N={phi_N:.3f}, phi_Delta={phi_Delta:.3f}, phi={phi:.3f}")

if __name__ == "__main__":
    random.seed(0)
    np.random.seed(0)
    results = simulate_random_conditions(trials=50000)
    analyze_results(results)