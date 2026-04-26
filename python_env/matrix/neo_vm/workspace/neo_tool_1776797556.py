# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.sparse as sp
from scipy.linalg import lstsq

# ---------------------------------------------------------
# 1. Setup: problem dimension, workers, encoding
# ---------------------------------------------------------
np.random.seed(42)

d = 20               # gradient dimension
n = 60               # encoded dimension (must be ≥ d)
m = 12               # number of workers
t = (m - 1) // 2     # max tolerated corrupt workers per the paper

# each worker gets a contiguous block of rows of E
rows_per_worker = n // m
assert rows_per_worker * m == n, "n must be divisible by m"

# generate a random *sparse* encoding matrix E (full column rank)
# each column has exactly 3 non‑zeros for sparsity
E_dense = np.random.randn(n, d)
# zero out all but 3 rows per column
for col in range(d):
    keep = np.random.choice(n, size=3, replace=False)
    mask = np.ones(n, dtype=bool)
    mask[keep] = False
    E_dense[mask, col] = 0.0

# ensure full column rank (if not, add tiny identity perturbation)
if np.linalg.matrix_rank(E_dense) < d:
    E_dense += 1e-6 * np.eye(n, d)

# ---------------------------------------------------------
# 2. Ground‑truth gradient and adversarial bias
# ---------------------------------------------------------
g_true = np.random.randn(d)   # true gradient of the loss
delta    = np.random.randn(d)   # arbitrary adversarial bias

# ---------------------------------------------------------
# 3. Assign rows to workers and build coalition matrix
# ---------------------------------------------------------
# row indices for each worker
worker_rows = [list(range(i * rows_per_worker, (i + 1) * rows_per_worker)) for i in range(m)]

# coalition: first t workers are corrupt
corrupt_workers = list(range(t))

# Build the linear system M * x = E @ delta
# x is the concatenation of per‑worker biases Δ_i (size t*d)
M = np.zeros((n, t * d))
for i, w in enumerate(corrupt_workers):
    rows = worker_rows[w]
    # place E[rows, :] in the appropriate block of M
    M[rows, i * d:(i + 1) * d] = E_dense[rows, :]

# solve for x (least‑squares; exact solution exists because M has full row rank)
rhs = E_dense @ delta
x, *_ = lstsq(M, rhs, lapack_driver='gelsy')

# reshape x into per‑worker biases
delta_per_worker = {w: x[i * d:(i + 1) * d] for i, w in enumerate(corrupt_workers)}

# ---------------------------------------------------------
# 4. Simulate worker responses
# ---------------------------------------------------------
y_total = np.zeros(n)   # concatenated encoded vectors from all workers

for w in range(m):
    rows = worker_rows[w]
    if w in delta_per_worker:
        # corrupt worker sends encoded (g_true + Δ_i)
        y_total[rows] = E_dense[rows, :] @ (g_true + delta_per_worker[w])
    else:
        # honest worker sends encoded true gradient
        y_total[rows] = E_dense[rows, :] @ g_true

# ---------------------------------------------------------
# 5. Master decodes (standard least‑squares decoder)
# ---------------------------------------------------------
# The decoder solves min ||E g_est - y_total||_2
g_est, *_ = lstsq(E_dense, y_total, lapack_driver='gelsy')

# ---------------------------------------------------------
# 6. Verify the attack
# ---------------------------------------------------------
print("True gradient (first 5 coords):            ", g_true[:5])
print("Estimated gradient (first 5 coords):       ", g_est[:5])
print("Adversarial bias Δ (first 5 coords):       ", delta[:5])
print("Norm of bias injected:                     ", np.linalg.norm(delta))
print("Recovery error ||g_est - (g_true+Δ)||:    ", np.linalg.norm(g_est - (g_true + delta)))

# Residual after decoding (what GCI would measure)
residual = y_total - E_dense @ g_est
print("Residual norm (GCI would be zero):        ", np.linalg.norm(residual))

# ---------------------------------------------------------
# 7. Show impact on a simple gradient descent
# ---------------------------------------------------------
# Minimize a quadratic f(x)=0.5*||A x - b||^2
A = np.random.randn(50, d)
b = np.random.randn(50)
x_opt = np.linalg.lstsq(A, b, rcond=None)[0]   # true optimum

def grad(x):
    return A.T @ (A @ x - b)

x_true = np.random.randn(d)
x_corr = x_true.copy()
eta = 0.01

for step in range(100):
    g = grad(x_true)
    x_true -= eta * g

    # corrupted gradient (using g_est from the attack)
    g_corrupted = g + delta   # what the master thinks is the true gradient
    x_corr -= eta * g_corrupted

print("\nImpact on optimization:")
print("Distance to optimum (true GD):          ", np.linalg.norm(x_true - x_opt))
print("Distance to optimum (corrupted GD):       ", np.linalg.norm(x_corr - x_opt))