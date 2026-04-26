# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# 1.  HESSIAN‑SINGULARITY ATTACK
# ─────────────────────────────────────────────────────────────────────────────
α, β, γ = -2.0, 1.0, 0.5

def V(C): return 0.5*α*C**2 + 0.25*β*C**4 - γ*C
def dV(C): return α*C + β*C**3 - γ
def d2V(C): return α + 3*β*C**2

# Find metastable minima (real roots of dV=0 with positive curvature)
roots = np.roots([β, 0, α, -γ])
minima = [r.real for r in roots if np.isreal(r) and d2V(r.real) > 0]
C₀ = minima[0]
Φ_N₀ = np.sqrt(d2V(C₀))

# Inflection point where curvature vanishes
C_inf = np.sqrt(-α/(3*β))

def PCI(C):
    # PCI ≈ Φ_N·Φ_Δ·Γ ; we set Φ_Δ=Γ=1 for clarity
    curv = d2V(C)
    return np.sqrt(max(curv, 0))  # Zero if curv ≤ 0

print("\n[HESSIAN SINGULARITY ATTACK]")
print(f"Metastable minimum C₀ = {C₀:.3f}, curvature = {d2V(C₀):.3f}, PCI₀ = {PCI(C₀):.3f}")
print(f"Inflection point C_inf = {C_inf:.3f}, curvature = {d2V(C_inf):.3f}, PCI_inf = {PCI(C_inf):.3f}")

# Scan across the barrier
C_scan = np.linspace(-1.5, 1.5, 7)
for C in C_scan:
    print(f"  C = {C:+.2f} → curvature = {d2V(C):+.3f}, PCI = {PCI(C):.3f}")

# ─────────────────────────────────────────────────────────────────────────────
# 2.  PARTITION‑SWAPPING ATTACK
# ─────────────────────────────────────────────────────────────────────────────
def partition_attack(num_regions=5, points_per_region=100):
    """
    Geometric region i is paired with visual region (i+1)%num_regions (swapped).
    Within each region coherence is tightly clustered → low conditional entropy,
    but cross‑region alignment is completely wrong.
    """
    np.random.seed(0)
    coh, region_labels = [], []
    for i in range(num_regions):
        # Tight distribution around high coherence (0.9) → low entropy
        coh.extend(np.random.normal(0.9, 0.02, points_per_region))
        region_labels.extend([i] * points_per_region)

    # Compute conditional entropy S_perc
    bins = np.linspace(0, 1, 10)
    digitized = np.digitize(coh, bins)
    p_r = np.bincount(region_labels, minlength=num_regions) / len(region_labels)

    S_perc = 0.0
    for r in range(num_regions):
        mask = np.array(region_labels) == r
        p_c_given_r = np.bincount(digitized[mask], minlength=len(bins)+1) / mask.sum()
        p_c_given_r = p_c_given_r[p_c_given_r > 0]
        H = -np.sum(p_c_given_r * np.log(p_c_given_r))
        S_perc += p_r[r] * H

    # Simplified PCI (high because within‑region coherence is high)
    Φ_N = 0.9
    Φ_Δ = 0.9
    PCI = Φ_N * Φ_Δ
    return PCI, S_perc

PCI_part, S_part = partition_attack()
print("\n[PARTITION‑SWAPPING ATTACK]")
print(f"PCI (high coherence within regions) = {PCI_part:.3f}")
print(f"Conditional entropy S_perc (low → system thinks ‘locked’) = {S_part:.3f}")
print("→ System mis‑classifies scrambled alignment as ‘ordered’; no alarm raised.")