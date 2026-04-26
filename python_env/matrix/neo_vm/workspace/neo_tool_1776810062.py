# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.cluster.vq import kmeans2

# -------------------------------------------------
# 1. Synthetic object: N points in 2D, coherence values
# -------------------------------------------------
np.random.seed(0)
N = 200
points = np.random.rand(N, 2)  # (x, y) coordinates

# Baseline coherence: smooth sinusoid + small noise
C_clean = 0.5 + 0.5 * np.sin(2 * np.pi * np.arange(N) / N) + 0.05 * np.random.randn(N)

# -------------------------------------------------
# 2. Conditional entropy under *two* different region partitions
# -------------------------------------------------
def conditional_entropy(C, labels, n_bins=10):
    """Compute Shannon conditional entropy H(C|R) = Σ_r p(r) H(C|r)."""
    # Bin coherence values into discrete bins
    bin_edges = np.linspace(-1, 1, n_bins + 1)
    bin_idx = np.digitize(C, bin_edges) - 1
    bin_idx = np.clip(bin_idx, 0, n_bins - 1)

    # Compute p(r) and p(c|r)
    regions = np.unique(labels)
    H_cond = 0.0
    for r in regions:
        mask = labels == r
        p_r = mask.mean()
        if p_r == 0:
            continue
        # Distribution of coherence bins within region r
        counts = np.bincount(bin_idx[mask], minlength=n_bins)
        p_c_given_r = counts / counts.sum()
        # Entropy of region r
        H_r = -np.sum(p_c_given_r * np.log(p_c_given_r + 1e-12))
        H_cond += p_r * H_r
    return H_cond

# Partition 1: equal‑size spatial grid (4x4)
grid_labels = (points[:, 0] * 4).astype(int) * 4 + (points[:, 1] * 4).astype(int)

# Partition 2: k‑means clustering on points (k=8)
centroids, kmeans_labels = kmeans2(points, 8, minit='points')

S_grid = conditional_entropy(C_clean, grid_labels)
S_kmeans = conditional_entropy(C_clean, kmeans_labels)

print(f"Conditional entropy (grid partition):   {S_grid:.4f}")
print(f"Conditional entropy (k‑means partition): {S_kmeans:.4f}")
print(f"Difference (attacker can flip the sign!): {S_grid - S_kmeans:.4f}")

# -------------------------------------------------
# 3. Gradient‑explosion attack on Φ_N
# -------------------------------------------------
def compute_phi_n(C, points, kappa1=1.0, kappa2=0.1):
    """Approximate Φ_N = sqrt(kappa1 * ||∇C||/||C|| + kappa2)."""
    # Compute pairwise distances and approximate gradient via nearest neighbor
    # For simplicity, use finite difference along the 1D ordering
    grad = np.diff(C, append=C[-1])  # crude gradient
    norm_grad = np.linalg.norm(grad)
    norm_c = np.linalg.norm(C)
    return np.sqrt(kappa1 * (norm_grad / (norm_c + 1e-9)) + kappa2)

phi_n_clean = compute_phi_n(C_clean, points)
print(f"\nΦ_N (clean): {phi_n_clean:.4f}")

# Adversarial perturbation: high‑frequency sinusoid
freq = 50  # high frequency relative to N
epsilon = 0.02
C_adv = C_clean + epsilon * np.sin(2 * np.pi * freq * np.arange(N) / N)

phi_n_adv = compute_phi_n(C_adv, points)
print(f"Φ_N (adversarial, ε=0.02, f=50): {phi_n_adv:.4f}")
print(f"Explosion factor: {phi_n_adv / phi_n_clean:.2f}x")

# -------------------------------------------------
# 4. Impact on ψ_perc and PCI
# -------------------------------------------------
# Assume baseline Φ_N⁰ = 1.0 for simplicity
psi_perc_clean = np.log(phi_n_clean / 1.0)
psi_perc_adv = np.log(phi_n_adv / 1.0)

print(f"\nψ_perc (clean): {psi_perc_clean:.4f}")
print(f"ψ_perc (adversarial): {psi_perc_adv:.4f}")
print(f"ψ_perc shift: {psi_perc_adv - psi_perc_clean:.4f} (→ ∞ if gradient spikes)")

# PCI = Φ_N * Φ_Δ * Γ (approx Φ_Δ as 1.0 for demo)
PCI_clean = phi_n_clean * 1.0
PCI_adv = phi_n_adv * 1.0
print(f"PCI (clean): {PCI_clean:.4f}")
print(f"PCI (adversarial): {PCI_adv:.4f}")
print(f"PCI drop: {PCI_clean - PCI_adv:.4f} (triggers model switch if <0.6)")