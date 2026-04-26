# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------
# Parameters from the thought
# ------------------------------
ALPHA_FS_CORRECTION_GIVEN = 0.000318   # Δα/α from 3D Archive mode interactions
LAMBDA = 0.82                          # Shredding Event threshold (IR cutoff)
V = 1.28                               # VAA sensitivity alignment
ENTROPY_MIN = 0.85                     # H ≥ 0.85 constraint

# ------------------------------
# Helper functions
# ------------------------------
def weight(k_vec):
    """Weight for a mode k: exp(-k^2/(2Λ^2)) / (1 + (k·v)^2)"""
    k_sq = np.dot(k_vec, k_vec)
    kv = np.dot(k_vec, V_vec)   # V_vec defined below
    return np.exp(-k_sq / (2.0 * LAMBDA**2)) / (1.0 + kv**2)

def entropy_from_weights(weights):
    """Shannon entropy H = - Σ p_i ln p_i, with p_i = w_i / Σ w_i"""
    total = np.sum(weights)
    if total == 0:
        return 0.0
    p = weights / total
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

# ------------------------------
# Set up orthogonal Φ_N and Φ_Delta
# ------------------------------
# Choose simple orthogonal basis vectors (can be any, invariants only require dot=0)
Phi_N = np.array([1.0, 0.0, 0.0])
Phi_Delta = np.array([0.0, 1.0, 0.0])
assert np.abs(np.dot(Phi_N, Phi_Delta)) < 1e-12, "Orthogonality violation: Φ_N·Φ_Delta ≠ 0"

# Ratio Φ_Delta/Φ_N – since they are vectors we use magnitude ratio for the scalar factor
ratio = np.linalg.norm(Phi_Delta) / np.linalg.norm(Phi_N)   # =1.0 here

# V as a vector aligned with some direction; we choose x-axis for simplicity
V_vec = np.array([V, 0.0, 0.0])

# ------------------------------
# Sum over k modes (discrete approximation)
# ------------------------------
# Choose a symmetric grid covering a few Λ to capture IR contributions (k < Λ) and some UV tail
k_max = 3.0   # enough to see convergence
k_step = 0.5
k_vals = np.arange(-k_max, k_max + k_step, k_step)
# Build 3D grid
Kx, Ky, Kz = np.meshgrid(k_vals, k_vals, k_vals, indexing='ij')
k_grid = np.stack([Kx.ravel(), Ky.ravel(), Kz.ravel()], axis=-1)  # shape (N,3)

weights = np.apply_along_axis(weight, 1, k_grid)
S = np.sum(weights)

# Predicted correction
pred_correction = ratio * S

# Entropy check
H = entropy_from_weights(weights)

# ------------------------------
# Validation & Reporting
# ------------------------------
tolerance = 1e-6
math_sound = np.abs(pred_correction - ALPHA_FS_CORRECTION_GIVEN) < tolerance
orthogonal_ok = np.abs(np.dot(Phi_N, Phi_Delta)) < 1e-12
entropy_ok = H >= ENTROPY_MIN - 1e-12

print("=== Omega Protocol Validation ===")
print(f"Given Δα/α                : {ALPHA_FS_CORRECTION_GIVEN:.6e}")
print(f"Predicted Δα/α (sum)      : {pred_correction:.6e}")
print(f"Match within {tolerance:.1e}? : {math_sound}")
print(f"Orthogonality Φ_N·Φ_Delta : {np.dot(Phi_N, Phi_Delta):.3e} (should be ~0) -> {orthogonal_ok}")
print(f"Entropy H                 : {H:.4f} (required ≥ {ENTROPY_MIN}) -> {entropy_ok}")
print(f"Number of k-modes sampled : {len(k_grid)}")
print("\nResult:")
if math_sound and orthogonal_ok and entropy_ok:
    print("PASS: All Omega Protocol invariants satisfied.")
else:
    print("FAIL: One or more invariants violated.")
    if not math_sound:
        print("  - Mathematical correction mismatch.")
    if not orthogonal_ok:
        print("  - Orthogonality (Φ_N·Φ_Delta = 0) violated.")
    if not entropy_ok:
        print("  - Entropy constraint H ≥ 0.85 violated.")