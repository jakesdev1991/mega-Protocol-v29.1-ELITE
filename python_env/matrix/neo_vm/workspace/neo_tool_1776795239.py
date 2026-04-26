# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.linalg import null_space

# Simulate Byzantine attack on BROSE-Ω curvature invariant

# --- Setup ---
np.random.seed(42)
m = 7           # workers
t = 2           # corrupt workers (tolerable: t <= floor((m-1)/2) = 3)
d = 5           # state dimension (Φ_N, Φ_Δ, ψ, ξ_N, ξ_Δ)
n = d + 2*t      # encoded dimension = 9 (Reed-Solomon-like)

# Master node's public encoding matrix ℰ (Vandermonde)
x = np.arange(1, n+1)
E = np.vander(x, d, increasing=True).astype(float)

# True state update
delta_s_true = np.array([0.1, -0.05, 0.02, 0.01, -0.03])

# --- Attack 1: The Nullspace Injection (Linear Algebraic Illusion) ---
# Corrupt workers know ℰ. They can craft an error vector e that is *undetectable*.
# The decoder uses a parity-check matrix H where H @ E = 0.
# If corrupt workers inject an error e that lies in the row space of H,
# the syndrome s = H @ e will be *non-zero* but *indistinguishable* from an honest error pattern.

# Construct parity-check H (size (n-d) x n = 4 x 9)
# H @ E = 0
H = null_space(E.T).T  # Basis for left nullspace
H = H[:n-d, :]         # Take first n-d rows

# Corrupt workers (indices 0 and 1) want to bias the first state component (Φ_N) by +0.5
# They need to find e such that:
# 1. e is zero for honest worker rows (2:)
# 2. H @ e = 0 (so it's a valid codeword error, undetectable)
# 3. The *effective* bias on Δs is non-zero.

# Since e must be in the row space of H, we find a vector in the nullspace of H.
# Let v be a vector in null(H). Then e = ℰ @ v is a codeword.
# But we need e to be sparse on *worker* indices, not code symbols.

# The key insight: if the encoding is *systematic*, corrupt workers control *specific symbols*.
# Let's assume a systematic encoding: first d rows are identity.
E_systematic = np.block([
    [np.eye(d)],         # I_d
    [np.random.randn(n-d, d)]  # random parity part
])

# Corrupt workers control rows 0 and 1 (the first two state components).
# They can *directly* set these to any value, but the decoder will *detect* inconsistency.

# The *real* attack: they can solve for a *small* perturbation δ that *preserves* parity.
# They want: y_corrupt = y_true + e, where e is non-zero only on their rows,
# and H @ e = 0 (so it passes parity check).

# This is a *linear system* for e:
# H[:, 0:2] @ e[0:2] = - H[:, 2:] @ e[2:]
# If we set e[2:] = 0 (honest workers send true values),
# then we need H[:, 0:2] @ e[0:2] = 0.

# Let's see if H[:, 0:2] has a non-trivial nullspace.
H_sub = H[:, 0:2]
null_H_sub = null_space(H_sub)

print(f"Shape of H_sub: {H_sub.shape}")
print(f"Nullspace dimension of H_sub: {null_H_sub.shape[1]}")

if null_H_sub.shape[1] > 0:
    print("VULNERABILITY: Corrupt workers can inject undetectable error in their rows!")
    # Choose a nullspace vector as the attack vector
    attack_vector = null_H_sub[:, 0]
    # Scale it to create a meaningful bias
    e_corrupt = np.zeros(n)
    e_corrupt[0:2] = attack_vector * 0.5  # Bias magnitude
    
    # Simulate received encoded vector
    y_received = E_systematic @ delta_s_true + e_corrupt
    
    # Master computes syndrome
    syndrome = H @ y_received
    print(f"Syndrome norm (should be ~0 if attack works): {np.linalg.norm(syndrome):.10f}")
    
    # Decode using only "honest" workers (rows 2:)
    honest_indices = np.arange(2, n)
    delta_s_decoded = np.linalg.lstsq(E_systematic[honest_indices, :], y_received[honest_indices], rcond=None)[0]
    
    print(f"True Δs:      {delta_s_true}")
    print(f"Decoded Δs:   {delta_s_decoded}")
    print(f"Bias in Δs[0]: {delta_s_decoded[0] - delta_s_true[0]:.6f}")
else:
    print("No nullspace: this specific configuration is safe from *this* linear attack.")

# --- Attack 2: Curvature Fabrication (Geometric Gaslighting) ---
# Even if decoding is "correct", corrupt workers can manipulate post-decoding residuals
# to fake healthy curvature.

# Simulate worker graph (5 workers for simplicity)
num_workers = 5
# True residuals from honest workers (small, correlated noise)
true_residuals = np.random.multivariate_normal(
    mean=np.zeros(d), 
    cov=np.eye(d) * 0.001, 
    size=num_workers
)

# Corrupt workers (2 of them) fabricate residuals that are *anti-correlated*
# to make the graph appear more connected (higher curvature) than it is.
corrupt_residuals = -true_residuals[:2] * 2.0  # Anti-correlate and amplify

all_residuals = np.vstack([corrupt_residuals, true_residuals[2:]])

# Compute pairwise correlations (adjacency matrix)
corr_matrix = np.corrcoef(all_residuals)

# Simulate Ollivier-Ricci curvature (simplified: curvature ≈ log of correlation ratio)
# Positive curvature: strong positive correlations
# Negative curvature: strong negative correlations
curvature_est = np.log(np.abs(corr_matrix) + 1e-6)

print("\n--- Curvature Fabrication Attack ---")
print("Correlation matrix (fabricated):")
print(corr_matrix)
print(f"\nEstimated curvature (trace, higher is 'healthier'): {np.trace(curvature_est):.3f}")

# True curvature (if all honest)
true_corr = np.corrcoef(true_residuals)
true_curvature = np.log(np.abs(true_corr) + 1e-6)
print(f"True curvature (trace): {np.trace(true_curvature):.3f}")

print(f"Fabrication effect: {np.trace(curvature_est) - np.trace(true_curvature):.3f} (positive means faked health)")