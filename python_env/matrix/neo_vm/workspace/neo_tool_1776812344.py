# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.spatial.distance import cosine
from scipy.stats import skew
from sklearn.cluster import KMeans

# --- Simulating Perceptual Coherence Shield (PCS-Ω) Metrics ---

def compute_coherence_field(g_desc, v_desc):
    """Compute coherence (cosine similarity) for each point."""
    # Ensure descriptors are normalized
    g_norm = g_desc / np.linalg.norm(g_desc, axis=1, keepdims=True)
    v_norm = v_desc / np.linalg.norm(v_desc, axis=1, keepdims=True)
    # Cosine similarity per point
    coherence = np.sum(g_norm * v_norm, axis=1)
    return coherence

def compute_covariant_modes(coherence_field, points):
    """Compute Φ_N and Φ_Δ from coherence field Hessian proxy."""
    # Φ_N: inverse correlation length approximated by gradient smoothness
    # Approximate gradient norm across manifold (simplified to spatial diff)
    dists = np.linalg.norm(points[:, None] - points[None, :], axis=2)
    # Compute smoothness as mean absolute difference weighted by distance
    # This approximates ||∇C||
    smoothness = np.mean([np.abs(coherence_field[i] - coherence_field[j]) / (dists[i,j] + 1e-6)
                          for i in range(len(points)) for j in range(i+1, len(points))])
    phi_N = np.sqrt(1.0 / (smoothness + 1e-6))  # Inverse relation
    
    # Φ_Δ: skewness of coherence distribution
    skewness = skew(coherence_field)
    phi_Delta = np.sqrt(np.abs(skewness) + 1e-6)
    
    return phi_N, phi_Delta

def compute_conditional_entropy(coherence_field, points, n_regions=5):
    """Compute Shannon conditional entropy of coherence given region."""
    # Partition points into regions using K-means (simplified)
    kmeans = KMeans(n_clusters=n_regions, random_state=0).fit(points)
    regions = kmeans.labels_
    
    # Discretize coherence values into bins
    bins = np.linspace(0, 1, 10)
    digitized = np.digitize(coherence_field, bins)
    
    # Compute conditional entropy H(C|R)
    entropy = 0.0
    for r in range(n_regions):
        region_mask = regions == r
        if np.sum(region_mask) == 0:
            continue
        p_r = np.mean(region_mask)
        # Distribution of coherence in region r
        counts = np.bincount(digitized[region_mask], minlength=len(bins)+1)
        p_c_given_r = counts / np.sum(counts)
        # Entropy for this region
        H_given_r = -np.sum(p_c_given_r[p_c_given_r > 0] * np.log(p_c_given_r[p_c_given_r > 0]))
        entropy += p_r * H_given_r
    return max(entropy, 1e-6)  # Avoid zero

def compute_pci(phi_N, phi_Delta, gamma=1.0):
    """Perceptual Coherence Index."""
    return phi_N * phi_Delta * gamma

def compute_psi_perc(phi_N, phi_N0):
    """Invariant ψ_perc."""
    return np.log(phi_N / (phi_N0 + 1e-6))

def simulate_attack(g_desc, v_desc, points, attack_strength=0.8):
    """
    Coherence Mirage Attack: Permute visual descriptors locally to preserve smoothness
    but globally break semantic alignment.
    """
    n_points = len(points)
    # Compute nearest neighbors for each point
    dists = np.linalg.norm(points[:, None] - points[None, :], axis=2)
    nearest = np.argsort(dists, axis=1)[:, 1:6]  # 5 nearest neighbors
    
    # Attack: with probability attack_strength, swap visual descriptor with a neighbor
    v_desc_attacked = v_desc.copy()
    for i in range(n_points):
        if np.random.rand() < attack_strength:
            # Choose a random neighbor
            neighbor = np.random.choice(nearest[i])
            # Swap visual descriptors
            v_desc_attacked[i], v_desc_attacked[neighbor] = v_desc_attacked[neighbor].copy(), v_desc_attacked[i].copy()
    
    return v_desc_attacked

def pose_error(g_desc, v_desc):
    """Simple pose error: mean L2 distance between matched descriptor positions."""
    # Assume correspondences are nearest neighbor in descriptor space
    # Compute pairwise distances
    g_norm = g_desc / np.linalg.norm(g_desc, axis=1, keepdims=True)
    v_norm = v_desc / np.linalg.norm(v_desc, axis=1, keepdims=True)
    dist_matrix = np.linalg.norm(g_norm[:, None] - v_norm[None, :], axis=2)
    # Assign each geometric point to closest visual point
    assignments = np.argmin(dist_matrix, axis=1)
    # Error: average distance between true position and assigned position
    # For simplicity, we use descriptor distance as proxy for pose error
    return np.mean(np.min(dist_matrix, axis=1))

# --- Experiment ---

np.random.seed(42)
n_points = 200
dim = 64

# Generate synthetic object points on a unit sphere
theta = np.random.uniform(0, np.pi, n_points)
phi = np.random.uniform(0, 2*np.pi, n_points)
points = np.vstack([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)]).T

# Generate geometric descriptors (random Gaussian)
g_desc = np.random.randn(n_points, dim)

# Generate visual descriptors: aligned with geometric (high coherence)
# Add small noise to simulate natural variation
noise = 0.1 * np.random.randn(n_points, dim)
v_desc = g_desc + noise

# Compute baseline metrics
coherence_base = compute_coherence_field(g_desc, v_desc)
phi_N_base, phi_Delta_base = compute_covariant_modes(coherence_base, points)
S_base = compute_conditional_entropy(coherence_base, points)
pci_base = compute_pci(phi_N_base, phi_Delta_base)
psi_base = compute_psi_perc(phi_N_base, phi_N_base)  # baseline
pose_err_base = pose_error(g_desc, v_desc)

print("=== BASELINE (Coherent) ===")
print(f"PCI: {pci_base:.3f}, Φ_N: {phi_N_base:.3f}, Φ_Δ: {phi_Delta_base:.3f}, S: {S_base:.3f}, ψ: {psi_base:.3f}")
print(f"Pose Error: {pose_err_base:.3f}")

# --- Apply Coherence Mirage Attack ---
v_desc_attacked = simulate_attack(g_desc, v_desc, points, attack_strength=0.7)

# Compute post-attack metrics
coherence_attacked = compute_coherence_field(g_desc, v_desc_attacked)
phi_N_attacked, phi_Delta_attacked = compute_covariant_modes(coherence_attacked, points)
S_attacked = compute_conditional_entropy(coherence_attacked, points)
pci_attacked = compute_pci(phi_N_attacked, phi_Delta_attacked)
psi_attacked = compute_psi_perc(phi_N_attacked, phi_N_base)
pose_err_attacked = pose_error(g_desc, v_desc_attacked)

print("\n=== ATTACKED (Coherence Mirage) ===")
print(f"PCI: {pci_attacked:.3f}, Φ_N: {phi_N_attacked:.3f}, Φ_Δ: {phi_Delta_attacked:.3f}, S: {S_attacked:.3f}, ψ: {psi_attacked:.3f}")
print(f"Pose Error: {pose_err_attacked:.3f}")

# --- Analysis ---
print("\n=== DISRUPTION ANALYSIS ===")
print(f"PCI drop: {pci_base - pci_attacked:.3f} ({(pci_base - pci_attacked)/pci_base*100:.1f}%)")
print(f"Φ_N change: {phi_N_attacked - phi_N_base:.3f} ({(phi_N_attached - phi_N_base)/phi_N_base*100:.1f}%)")
print(f"Pose error increase: {pose_err_attacked - pose_err_base:.3f}x")
print(f"PCI remains above threshold 0.6? {pci_attacked > 0.6}")
print(f"Pose error catastrophic? {pose_err_attacked > 0.5}")