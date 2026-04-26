# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for COAGN proposal.
Checks:
  Φ-1: Causal fidelity (no superluminal signal propagation)
  Φ-2: Entropy increase ≤ 3% of initial
  Φ-3: Firing mesh homotopy-equivalent to 3‑torus (Betti numbers)
  TOE Step 5: Crossed‑product stabilization (interaction term → 0)
"""

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, laplacian
from scipy.linalg import eigvals

# --------------------------
# Helper functions
# --------------------------
def shannon_entropy(v: np.ndarray, bins: int = 20) -> float:
    """Discrete Shannon entropy of a real‑valued vector."""
    hist, _ = np.histogram(v, bins=bins, density=True)
    hist = hist[hist > 0]          # avoid log(0)
    return -np.sum(hist * np.log(hist))

def betti_numbers_from_adjacency(A: np.ndarray):
    """
    Approximate Betti numbers of an undirected graph via Laplacian spectrum.
    For a genuine 3‑torus we expect β0=1, β1=3, β2=3, β3=1.
    Here we compute β0 (components) and β1 (first Betti) via cyclomatic number.
    Higher‑order Betti numbers are not captured exactly; we flag if β0,β1 deviate.
    """
    n = A.shape[0]
    L = laplacian(csr_matrix(A))
    # Number of zero eigenvalues = number of connected components (β0)
    evals = eigvals(L.toarray())
    evals = np.real_if_close(evals)
    beta0 = np.sum(np.abs(evals) < 1e-8)
    # Cyclomatic number: β1 = E - V + β0 (for an undirected graph)
    E = np.sum(A) // 2
    beta1 = E - n + beta0
    return beta0, beta1

def causal_fidelity_check(J: np.ndarray, c: float = 1.0) -> bool:
    """
    Φ-1: Ensure no eigenvalue of the Jacobian implies gain > c.
    We interpret eigenvalues as growth rates; require Re(λ) <= 0.
    (In a discretized time step, λ>0 would amplify signals beyond light‑cone.)
    """
    lambdas = eigvals(J)
    return np.all(np.real(lambdas) <= 0 + 1e-12)

def entropy_increase_check(S0: float, S1: float, max_frac: float = 0.03) -> bool:
    """Φ-2: ΔS/S0 ≤ max_frac."""
    return (S1 - S0) <= max_frac * S0 + 1e-12

def crossed_product_stabilization_check(g: np.ndarray, h: np.ndarray, K: np.ndarray) -> bool:
    """
    Simplified test: after applying regulator K, the interaction term g×h should be nulled.
    We model the interaction as the matrix product g @ h (stand‑in for Lie bracket).
    The regulator K is assumed to project onto the stabilized subspace.
    """
    interaction = g @ h
    stabilized = K @ interaction
    return np.allclose(stabilized, 0, atol=1e-8)

# --------------------------
# Simulated COAGN data
# --------------------------
np.random.seed(42)

# 1. Sensor stream (past light-cone only): 6‑dim vector [az, el, t, wind, vib, gps_err]
n_samples = 500
sensor = np.random.randn(n_samples, 6)
# Ensure causality: each sample only depends on previous ones (already true by construction)

# 2. Simple linear predictor for firing vector (3‑dim: azimuth, elevation, charge)
W = np.random.randn(3, 6) * 0.1   # predictor matrix
firing_raw = sensor @ W.T        # shape (n_samples, 3)

# 3. DEN: apply a stabilizing gain matrix Kden (simulating swarm rebalancing)
Kden = np.eye(3) - 0.05 * np.ones((3, 3))   # mild consensus damping
firing_den = firing_raw @ Kden.T

# 4. Compute Jacobian of predictor w.r.t. sensor (constant for linear model)
J = W   # 3x6; we only need the part that maps sensor→firing; causality test on J

# 5. Entropy of firing deviation (difference from nominal zero vector)
dev_raw = firing_raw - np.zeros_like(firing_raw)
dev_den = firing_den - np.zeros_like(firing_den)
S0 = shannon_entropy(dev_raw.flatten())
S1 = shannon_entropy(dev_den.flatten())

# 6. Swarm adjacency for AEM: random geometric graph approximating a 3‑torus lattice
n_turrets = 27   # 3^3 nodes for a discrete 3‑torus
pos = np.random.rand(n_turrets, 3)   # positions in unit cube [0,1)^3
# connect if distance < threshold (creates roughly a 3‑D periodic lattice)
thr = 0.2
A = np.zeros((n_turrets, n_turrets), dtype=int)
for i in range(n_turrets):
    for j in range(i+1, n_turrets):
        d = np.minimum(np.abs(pos[i]-pos[j]), 1- np.abs(pos[i]-pos[j])).max()  # toroidal distance
        if d < thr:
            A[i,j] = A[j,i] = 1

beta0, beta1 = betti_numbers_from_adjacency(A)

# 7. Crossed‑product test: mock Lie algebras as random matrices
g = np.random.randn(3,3)   # artillery dynamics algebra rep.
h = np.random.randn(3,3)   # environmental stress algebra rep.
K = np.eye(3) - 0.1 * np.random.randn(3,3)   # regulator projecting to stabilized subspace

# --------------------------
# Invariant evaluation
# --------------------------
results = {}

results["Φ-1 (Causal Fidelity)"] = causal_fidelity_check(J)
results["Φ-2 (Entropy Increase)"] = entropy_increase_check(S0, S1)
results["Φ-3 (Topology β0=1, β1=3)"] = (beta0 == 1 and beta1 == 3)
results["TOE Step 5 (Crossed‑Product Stabilization)"] = crossed_product_stabilization_check(g, h, K)

# Pretty print
print("=== Omega Protocol Invariant Validation ===")
for inv, ok in results.items():
    print(f"{inv:40} : {'PASS' if ok else 'FAIL'}")

# Overall compliance
overall = all(results.values())
print("\nOVERALL COMPLIANCE :", "PASS" if overall else "FAIL")
if not overall:
    failed = [k for k,v in results.items() if not v]
    print("Failed invariants:", ", ".join(failed))