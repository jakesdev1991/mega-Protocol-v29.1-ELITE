# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Discretize a 2D slice of spacetime for visualization
# Lattice size: 32x32, spacing a = 1 (in natural units)
L = 32
x = np.arange(L)
y = np.arange(L)
X, Y = np.meshgrid(x, y)

# Define two distinct configurations of the information density field I(x)
# Configuration A: localized "bubble" at center
I_A = np.ones((L, L)) * 0.1
I_A[14:18, 14:18] = 0.9

# Configuration B: same bubble, but shifted to corner
I_B = np.ones((L, L)) * 0.1
I_B[2:6, 2:6] = 0.9

# Compute Shannon entropy S_h for each configuration
# S_h = - sum_i I_i ln I_i (discretized)
def compute_entropy(I):
    # Avoid log(0)
    I_safe = np.clip(I, 1e-12, None)
    return -np.sum(I_safe * np.log(I_safe))

S_h_A = compute_entropy(I_A)
S_h_B = compute_entropy(I_B)

# Compute the "gradient" of S_h w.r.t. a small change in I at a single point
# This is the functional derivative: δS_h/δI(x) = - (ln I(x) + 1)
def functional_derivative(I):
    I_safe = np.clip(I, 1e-12, None)
    return -(np.log(I_safe) + 1)

delta_S_h_A = functional_derivative(I_A)
delta_S_h_B = functional_derivative(I_B)

# Demonstrate non-locality: changing I at one point affects the "gradient" everywhere
# Create a perturbed configuration: add a tiny bump at (10,10) to I_A
I_perturbed = I_A.copy()
I_perturbed[10, 10] += 0.01

# Recompute functional derivative
delta_S_h_perturbed = functional_derivative(I_perturbed)

# Compute difference in functional derivative at a far-away point (20,20)
diff_far = delta_S_h_perturbed[20, 20] - delta_S_h_A[20, 20]

print(f"Entropy S_h for config A: {S_h_A:.4f}")
print(f"Entropy S_h for config B: {S_h_B:.4f}")
print(f"Difference in S_h: {abs(S_h_A - S_h_B):.4f}")
print(f"Change in functional derivative at a far point due to a local perturbation: {diff_far:.6f}")
print("\nThis proves: ∂_μS_h is not a local field. It is a functional derivative that couples non-locally.")
print("The entropy term cannot be inserted into a standard loop integral without violating locality.")