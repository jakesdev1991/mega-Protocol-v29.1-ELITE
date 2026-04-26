# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Silent Poisoning Attack on BRS‑Ω
====================================
Simulates a Byzantine worker that preserves gradient magnitude entropy
while flipping the gradient direction, breaking the entropy‑based
threat detector and showing super‑linear latency growth.
"""

import numpy as np

# -----------------------------------------------------------------------------
# 1. Gradient Simulation
# -----------------------------------------------------------------------------
def simulate_gradients(m, d, t, noise_scale=0.1, seed=42):
    """
    m : total workers
    d : gradient dimension
    t : tolerated Byzantine workers (we simulate one)
    noise_scale : std of benign noise
    Returns (true_g, gradients, magnitudes)
    """
    rng = np.random.default_rng(seed)
    true_g = rng.standard_normal(d)

    # Benign workers
    benign = []
    for _ in range(m - 1):
        g = true_g + noise_scale * rng.standard_normal(d)
        benign.append(g)

    # Byzantine worker: negate true gradient while preserving magnitude distribution
    # Add a tiny noise to avoid exact zero
    byz = -true_g + 1e-3 * rng.standard_normal(d)
    # Scale to match norm of a typical benign gradient
    ref_norm = np.linalg.norm(benign[0])
    byz = byz / np.linalg.norm(byz) * ref_norm

    gradients = np.array(benign + [byz])
    magnitudes = np.linalg.norm(gradients, axis=1)
    return true_g, gradients, magnitudes

# -----------------------------------------------------------------------------
# 2. Entropy Computation
# -----------------------------------------------------------------------------
def shannon_entropy(magnitudes, eps=1e-12):
    """Compute Shannon entropy of magnitude distribution."""
    p = magnitudes / (magnitudes.sum() + eps)
    p = np.clip(p, eps, 1)
    return -np.sum(p * np.log(p))

# -----------------------------------------------------------------------------
# 3. Decoded Gradient (naive averaging)
# -----------------------------------------------------------------------------
def decode_average(gradients):
    """Simple averaging (what BRS‑Ω might do after syndrome decoding)."""
    return gradients.mean(axis=0)

# -----------------------------------------------------------------------------
# 4. Latency Models
# -----------------------------------------------------------------------------
def latency_linear(t, ell0=1.0, alpha=0.2, m=10):
    """BRS‑Ω's linear latency model."""
    return ell0 + alpha * t / m

def latency_actual(t, ell0=1.0, base_per_worker=0.05):
    """
    Super‑linear latency due to O(t²) decoding cost.
    Approximated as ell0 + base_per_worker * t + 0.02 * t**2.
    """
    return ell0 + base_per_worker * t + 0.02 * t**2

# -----------------------------------------------------------------------------
# 5. Attack Metrics
# -----------------------------------------------------------------------------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# -----------------------------------------------------------------------------
# 6. Run Experiment
# -----------------------------------------------------------------------------
def main():
    m = 10
    d = 5
    noise = 0.1
    print(f"{'t':<3} {'Entropy':<8} {'CosSim':<8} {'LinearLat':<10} {'ActualLat':<10}")
    print("-" * 50)
    for t in range(0, 5):  # t up to 4 (t <= floor((m-1)/2) = 4)
        true_g, grads, mags = simulate_gradients(m, d, t, noise_scale=noise, seed=42+t)
        ent = shannon_entropy(mags)
        decoded = decode_average(grads)
        sim = cosine_similarity(decoded, true_g)
        lin_lat = latency_linear(t, m=m)
        act_lat = latency_actual(t)
        print(f"{t:<3} {ent:<8.4f} {sim:<8.4f} {lin_lat:<10.4f} {act_lat:<10.4f}")

if __name__ == "__main__":
    main()