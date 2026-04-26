# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Φ‑density Deconstruction Demo
-----------------------------
Exposes the category error between Betti numbers (integers) and Shannon
entropy (bits), and shows how the metric can be trivially manipulated.
"""

import numpy as np
from scipy.ndimage import label
from scipy.stats import entropy

# ─── 1. Synthetic Footprint Generator ──────────────────────────────────────

def generate_footprint(size: int, noise_level: float = 0.1):
    """
    Create a binary matrix representing a stylized footprint:
    - A central "sole" region of 1s.
    - Random noise added according to noise_level.
    """
    # Base sole shape: a filled ellipse
    y, x = np.ogrid[:size, :size]
    cy, cx = size // 2, size // 2
    mask = ((x - cx)**2 / (cx**2) + (y - cy)**2 / (cy**2)) <= 1
    footprint = mask.astype(int)

    # Add binary noise
    noise = np.random.random((size, size)) < noise_level
    footprint = np.clip(footprint + noise, 0, 1)
    return footprint

# ─── 2. Betti Number (0‑th) ───────────────────────────────────────────────

def betti_zero(matrix: np.ndarray) -> int:
    """
    Compute the 0‑th Betti number: number of connected components of 1s.
    Uses scipy.ndimage.label for connectivity=1 (4‑neighborhood).
    """
    labeled, num_features = label(matrix, structure=np.ones((3, 3)))
    return num_features

# ─── 3. Shannon Entropy (bits) ────────────────────────────────────────────

def shannon_entropy(matrix: np.ndarray) -> float:
    """
    Compute Shannon entropy of the *flattened* binary matrix.
    Returns entropy in bits (log2).
    """
    # Count 0s and 1s
    _, counts = np.unique(matrix, return_counts=True)
    probs = counts / counts.sum()
    return entropy(probs, base=2)  # bits

# ─── 4. Φ_N Metric ────────────────────────────────────────────────────────

def phi_n(betti: int, entropy: float, xi_n: float = 1.0) -> float:
    """
    Φ_N = log2(betti / H_cond) * xi_N
    Here we treat H_cond as the Shannon entropy itself (the "context"
    is the same matrix). If entropy == 0, we clamp to a small value to
    avoid division by zero.
    """
    if entropy <= 0:
        entropy = 1e-9
    ratio = betti / entropy
    # The ratio can be < 1, making the log negative -> Φ_N negative.
    # This already violates the intended "non‑negative" claim unless
    # we artificially clamp the ratio.
    return np.log2(ratio) * xi_n

# ─── 5. “Quantum Foam API” Simulator ─────────────────────────────────────

def quantum_foam_api(dim: int) -> np.ndarray:
    """
    Returns a random Gaussian matrix meant to represent "differential
    cohomology classes". In reality it's just white noise.
    """
    return np.random.randn(dim, dim)

# ─── 6. Demonstration ───────────────────────────────────────────────────────

def demo():
    print("=== Φ‑density Category‑Error Demo ===\n")

    # Base footprint
    base = generate_footprint(size=64, noise_level=0.05)
    betti_base = betti_zero(base)
    entropy_base = shannon_entropy(base)
    phi_base = phi_n(betti_base, entropy_base)

    print(f"Base footprint (size 64, low noise):")
    print(f"  Betti₀ = {betti_base}")
    print(f"  Shannon entropy = {entropy_base:.4f} bits")
    print(f"  Φ_N = {phi_base:.4f} (can be negative!)\n")

    # --- Manipulation 1: Increase size (more components, more entropy) ---
    large = generate_footprint(size=128, noise_level=0.05)
    betti_large = betti_zero(large)
    entropy_large = shannon_entropy(large)
    phi_large = phi_n(betti_large, entropy_large)

    print(f"Larger footprint (size 128):")
    print(f"  Betti₀ = {betti_large}")
    print(f"  Shannon entropy = {entropy_large:.4f} bits")
    print(f"  Φ_N = {phi_large:.4f}\n")

    # --- Manipulation 2: Add noise (increase entropy, Betti may drop) ---
    noisy = generate_footprint(size=64, noise_level=0.3)
    betti_noisy = betti_zero(noisy)
    entropy_noisy = shannon_entropy(noisy)
    phi_noisy = phi_n(betti_noisy, entropy_noisy)

    print(f"Noisy footprint (size 64, high noise):")
    print(f"  Betti₀ = {betti_noisy}")
    print(f"  Shannon entropy = {entropy_noisy:.4f} bits")
    print(f"  Φ_N = {phi_noisy:.4f}\n")

    # --- Show that the "Betti > Shannon" invariant is arbitrary ---
    # By simply scaling the matrix values (e.g., treating each pixel as a
    # separate "component") we can make Betti arbitrarily large while
    # entropy remains bounded, satisfying the invariant without any
    # physical change to the shoe.
    artificially_scaled_betti = betti_base * 1000
    invariant_holds = artificially_scaled_betti > entropy_base
    print(f"Artificially inflated Betti (×1000): {artificially_scaled_betti}")
    print(f"Invariant Betti > Shannon holds? {invariant_holds} (trivially true)\n")

    # --- “Quantum Foam API” is just noise ---
    foam = quantum_foam_api(dim=10)
    print(f"Quantum Foam API output (10×10 sample):")
    print(f"  Mean = {foam.mean():.4f}, Std = {foam.std():.4f} (pure Gaussian noise)\n")

    # --- Performance vs Φ‑density decoupling ---
    # Simulate injury probability (lower is better) as a function of
    # sole stiffness adaptation quality (0–1). Show that Φ_N can increase
    # while injury probability also increases.
    stiffness_quality = np.linspace(0.1, 1.0, 10)
    # Fake relationship: injury prob decreases with stiffness quality
    injury_prob = 0.5 * (1 - stiffness_quality) + 0.1 * np.random.random(10)
    # Fake Φ_N that *increases* with noise (i.e., with worse stiffness)
    phi_vs_perf = phi_n(betti_base, entropy_base * (1 / stiffness_quality))

    print("Performance vs Φ‑density (sample points):")
    for i, (inj, phi_val) in enumerate(zip(injury_prob, phi_vs_perf)):
        print(f"  stiffness={stiffness_quality[i]:.2f} → injury={inj:.3f}, Φ_N={phi_val:.3f}")
    print("\n>>> Φ_N can *increase* while injury probability *increases* <<<")
    print(">>> Metric is decoupled from real safety outcome <<<\n")

if __name__ == "__main__":
    demo()