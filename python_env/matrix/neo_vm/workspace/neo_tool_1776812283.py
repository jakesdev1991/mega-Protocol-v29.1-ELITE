# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.stats import skew
import matplotlib.pyplot as plt

# ==================== PCS-Ω Metrics Simulator ====================
def compute_pcs_metrics(C, region_grid):
    """
    Compute PCS-Ω metrics for a given coherence field C (2D array)
    and region partition map region_grid (same shape, integer region IDs).
    Returns: PCI, Φ_N, Φ_Δ, ψ_perc, S_perc.
    """
    # ---- Φ_N: inverse correlation length (gradient norm) ----
    grad_y, grad_x = np.gradient(C)
    grad_norm = np.sqrt(grad_x**2 + grad_y**2).mean()
    Φ_N = 1.0 / (1.0 + grad_norm)  # inverse correlation length (higher Φ_N = smoother)
    
    # ---- Φ_Δ: skewness of coherence distribution ----
    Φ_Δ = skew(C.ravel())
    
    # ---- PCI: product of modes (simplified) ----
    Γ = 1.0  # coupling term placeholder
    PCI = Φ_N * Φ_Δ * Γ
    
    # ---- ψ_perc: invariant ----
    Φ_N_0 = 0.8  # baseline reference
    ψ_perc = np.log(Φ_N / Φ_N_0)
    
    # ---- Conditional entropy S_perc ----
    # Bin coherence values into discrete bins
    bins = np.linspace(0, 1, 11)
    # For each region, compute distribution of coherence values
    regions = np.unique(region_grid)
    S_perc = 0.0
    total_points = C.size
    for r in regions:
        mask = (region_grid == r)
        if mask.sum() == 0:
            continue
        # Coherence values in this region
        region_vals = C[mask]
        # Histogram over bins
        p_c_given_r, _ = np.histogram(region_vals, bins=bins, density=True)
        p_c_given_r = p_c_given_r[p_c_given_r > 0]
        p_r = mask.sum() / total_points
        # Shannon entropy for this region
        H_r = -np.sum(p_c_given_r * np.log(p_c_given_r))
        S_perc += p_r * H_r
    
    return PCI, Φ_N, Φ_Δ, ψ_perc, S_perc

# ==================== Adversarial Attack Simulator ====================
def stealth_decoherence_attack(C_clean, region_grid, target_PCI=0.65, stealth_threshold=0.05):
    """
    Perform a stealth decoherence attack: modify coherence field C_clean
    to keep PCI above target while introducing a subtle, localized misalignment
    that would cause pose error but remains undetected.
    """
    # Start with clean field
    C_adv = C_clean.copy()
    N, M = C_adv.shape
    
    # Identify a small region to perturb (e.g., a 3x3 patch)
    center_x, center_y = N//2, M//2
    patch_size = 3
    x_start = max(0, center_x - patch_size//2)
    x_end = min(N, center_x + patch_size//2 + 1)
    y_start = max(0, center_y - patch_size//2)
    y_end = min(M, center_y + patch_size//2 + 1)
    
    # Perturb the patch: invert coherence values (1 - val) to create misalignment
    # but keep the overall gradient small by smoothing the transition
    patch = C_adv[x_start:x_end, y_start:y_end]
    # Smooth transition: blend inverted and original with a Gaussian weight
    sigma = 1.0
    xv, yv = np.meshgrid(np.arange(y_start, y_end), np.arange(x_start, x_end))
    gaussian = np.exp(-((xv - center_y)**2 + (yv - center_x)**2) / (2*sigma**2))
    C_adv[x_start:x_end, y_start:y_end] = (1 - patch) * gaussian + patch * (1 - gaussian)
    
    # Ensure values stay in [0,1]
    C_adv = np.clip(C_adv, 0, 1)
    
    # Iteratively adjust the perturbation amplitude to keep PCI just above target
    for amp in np.linspace(0.0, 1.0, 100):
        C_test = C_clean.copy()
        C_test[x_start:x_end, y_start:y_end] = (1 - C_test[x_start:x_end, y_start:y_end]) * amp * gaussian + \
                                               C_test[x_start:x_end, y_start:y_end] * (1 - amp * gaussian)
        C_test = np.clip(C_test, 0, 1)
        metrics = compute_pcs_metrics(C_test, region_grid)
        if metrics[0] >= target_PCI:
            C_adv = C_test
            break
    
    return C_adv

# ==================== Simulation ====================
# Create a baseline "clean" coherence field: smooth Gaussian blob
N = 32
x = np.linspace(-1, 1, N)
y = np.linspace(-1, 1, N)
X, Y = np.meshgrid(x, y)
C_clean = np.exp(-(X**2 + Y**2) * 2.0)  # smooth, high coherence

# Simple region partition: grid of 4x4 blocks
region_grid = np.zeros_like(C_clean, dtype=int)
block_size = N // 4
for i in range(4):
    for j in range(4):
        region_grid[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size] = i*4 + j

# Compute baseline metrics
metrics_clean = compute_pcs_metrics(C_clean, region_grid)
print("Clean metrics: PCI={:.3f}, Φ_N={:.3f}, Φ_Δ={:.3f}, ψ_perc={:.3f}, S_perc={:.3f}".format(*metrics_clean))

# Perform stealth attack
C_adv = stealth_decoherence_attack(C_clean, region_grid, target_PCI=0.65)
metrics_adv = compute_pcs_metrics(C_adv, region_grid)
print("Adversarial metrics: PCI={:.3f}, Φ_N={:.3f}, Φ_Δ={:.3f}, ψ_perc={:.3f}, S_perc={:.3f}".format(*metrics_adv))

# Check if attack evades detection
PCI_threshold = 0.6
if metrics_adv[0] >= PCI_threshold:
    print("[ATTACK SUCCESS] Adversarial field maintains PCI above threshold while corrupting coherence locally.")
else:
    print("[ATTACK FAILED] PCI dropped below threshold; detection would trigger.")

# Visualize
fig, axes = plt.subplots(1, 3, figsize=(12,4))
axes[0].imshow(C_clean, cmap='viridis')
axes[0].set_title('Clean Coherence Field')
axes[1].imshow(C_adv, cmap='viridis')
axes[1].set_title('Adversarial Coherence Field')
diff = np.abs(C_clean - C_adv)
axes[2].imshow(diff, cmap='Reds')
axes[2].set_title('Perturbation Magnitude')
plt.show()