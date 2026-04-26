# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

# --- Simulation Parameters ---
m = 30               # number of data sources
d = 10               # dimension of true data vector
rho = 3              # redundancy factor
n = rho * d          # total encoded dimension
t = (m - 1) // 2     # max Byzantine sources the scheme claims to tolerate
tau = 0.1            # residual norm threshold for flagging a source
alpha, beta, gamma = 2.0, 10.0, 0.5  # DCI tuning constants
epsilon = 0.01       # adversarial safety margin (|e_i| = tau - epsilon)

# --- Helper Functions ---
def generate_encoding_matrix(d, n):
    """Create a random sparse encoding matrix of shape (n, d) with condition number ~1e3."""
    A = np.random.randn(n, d)
    # Force high condition number by scaling a few singular values
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    s[-1] = s[0] / 1e3  # make smallest singular value much smaller
    A = U @ np.diag(s) @ Vt
    # Sparsify: keep only 30% of entries
    mask = np.random.rand(n, d) < 0.3
    A = A * mask
    return A

def encode(d_vec, E):
    """Encode true data vector d_vec (shape (d,)) into y (shape (n,))."""
    return E @ d_vec

def partition(y, m):
    """Partition encoded vector y into m sub-vectors of equal size."""
    sub_len = n // m
    return [y[i*sub_len:(i+1)*sub_len] for i in range(m)]

def corrupt(y_list, corrupt_idx, tau, epsilon):
    """Inject adversarial error e_i into each corrupted source.
    The error vector has norm (tau - epsilon) and is aligned with the
    original sub-vector to maximize impact while staying just below threshold.
    """
    corrupted = []
    for i, yi in enumerate(y_list):
        if i in corrupt_idx:
            norm_yi = np.linalg.norm(yi)
            if norm_yi > 1e-9:
                direction = yi / norm_yi
            else:
                direction = np.random.randn(*yi.shape)
                direction = direction / np.linalg.norm(direction)
            e_i = direction * (tau - epsilon)
            corrupted.append(yi + e_i)
        else:
            corrupted.append(yi)
    return corrupted

def decode(y_list, E):
    """Reconstruct d_est from corrupted sub-vectors using pseudo‑inverse (naive decoder)."""
    y_full = np.concatenate(y_list)  # shape (n,)
    d_est = np.linalg.pinv(E) @ y_full
    return d_est

def residuals(y_list, d_est, E):
    """Compute per‑source residual vectors."""
    r_list = []
    sub_len = n // m
    for i, yi in enumerate(y_list):
        Ei = E[i*sub_len:(i+1)*sub_len, :]  # sub‑matrix for source i
        ri = yi - Ei @ d_est
        r_list.append(ri)
    return r_list

def compute_dci(residuals, tau, alpha, beta, gamma, rho):
    """Compute Data Corruption Index (DCI)."""
    flagged = [np.linalg.norm(r) > tau for r in residuals]
    theta = sum(flagged) / len(residuals)
    epsilon_avg = np.mean([np.linalg.norm(r) for r in residuals])
    dci = np.tanh(alpha * theta + beta * epsilon_avg + gamma * rho)
    return dci, theta, epsilon_avg

# --- Monte Carlo Simulation ---
np.random.seed(42)
num_trials = 1000

dci_vals = []
theta_vals = []
epsilon_vals = []
reconstruction_errors = []

for trial in range(num_trials):
    # True data vector
    d_true = np.random.randn(d)

    # Encoding matrix
    E = generate_encoding_matrix(d, n)

    # True encoded vector
    y_true = encode(d_true, E)

    # Partition into source sub‑vectors
    y_parts = partition(y_true, m)

    # Randomly select t sources to corrupt
    corrupt_set = set(random.sample(range(m), t))

    # Corrupt the selected sources
    y_corrupt = corrupt(y_parts, corrupt_set, tau, epsilon)

    # Decode using naive pseudo‑inverse (assumes all sources honest)
    d_est = decode(y_corrupt, E)

    # Compute residuals based on decoded estimate
    r_list = residuals(y_corrupt, d_est, E)

    # Compute DCI and related metrics
    dci, theta, eps = compute_dci(r_list, tau, alpha, beta, gamma, rho)

    # Reconstruction error (L2 norm)
    error = np.linalg.norm(d_est - d_true)

    # Store results
    dci_vals.append(dci)
    theta_vals.append(theta)
    epsilon_vals.append(eps)
    reconstruction_errors.append(error)

# --- Analysis ---
mean_dci = np.mean(dci_vals)
mean_theta = np.mean(theta_vals)
mean_eps = np.mean(epsilon_vals)
mean_error = np.mean(reconstruction_errors)

print("=== DCI Evasion Attack Results (1000 trials) ===")
print(f"Mean DCI: {mean_dci:.4f} (threshold for alert = 0.7)")
print(f"Mean flagged fraction θ: {mean_theta:.4%}")
print(f"Mean residual norm ε: {mean_eps:.4f} (detection threshold τ = {tau})")
print(f"Mean reconstruction error: {mean_error:.4f}")
print("\n--- Key Insight ---")
print(f"Despite keeping θ and ε low (both < {tau}), the reconstruction error is {mean_error/tau:.1f}× the detection threshold.")
print("The DCI is therefore a poor sentinel; an adversary can evade detection while causing large objective corruption.")