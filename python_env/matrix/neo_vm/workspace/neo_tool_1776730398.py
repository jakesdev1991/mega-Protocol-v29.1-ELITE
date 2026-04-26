# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- graph utilities ---
def random_graph(n, p, seed=0):
    rng = np.random.default_rng(seed)
    A = rng.random((n, n)) < p
    A = A.astype(float)
    A = np.triu(A, 1)  # upper triangle, no diagonal
    A = A + A.T          # symmetric adjacency matrix
    return A

def laplacian(A):
    deg = A.sum(axis=1)
    D = np.diag(deg)
    L = D - A
    return L

def cod_fiedler(L, conscious_node):
    # eigenvectors of Laplacian (symmetric)
    w, v = np.linalg.eigh(L)
    # Fiedler vector (subconscious) = eigenvector of 2nd smallest eigenvalue
    fiedler = v[:, 1]
    # Conscious one‑hot vector
    conscious = np.zeros(L.shape[0])
    conscious[conscious_node] = 1.0
    # Normalized squared overlap
    overlap = np.dot(fiedler, conscious)**2 / (np.dot(fiedler, fiedler) * np.dot(conscious, conscious))
    return overlap, fiedler

# --- initial connected graph ---
n = 20
p = 0.3
A = random_graph(n, p, seed=42)
L = laplacian(A)
cod, _ = cod_fiedler(L, conscious_node=0)
print(f"Initial COD (connected): {cod:.4f}")

# --- Shredding event: isolate node 1 by removing all its edges ---
A_shred = A.copy()
A_shred[1, :] = 0
A_shred[:, 1] = 0
L_shred = laplacian(A_shred)
cod_shred, _ = cod_fiedler(L_shred, conscious_node=1)
print(f"COD after shredding node 1: {cod_shred:.4f} (Conscious Black Hole)")

# --- Informational Freeze: drop algebraic connectivity (remove random edges) ---
mask = np.random.default_rng(0).random(A_shred.shape) < 0.3
A_freeze = A_shred.copy()
A_freeze[mask] = 0
A_freeze = np.triu(A_freeze, 1)
A_freeze = A_freeze + A_freeze.T
L_freeze = laplacian(A_freeze)
cod_freeze, _ = cod_fiedler(L_freeze, conscious_node=0)
# Show algebraic connectivity (second eigenvalue)
w_freeze = np.linalg.eigvalsh(L_freeze)
print(f"Algebraic connectivity (freeze): {w_freeze[1]:.4f} (low → rigid)")
print(f"COD in freeze regime: {cod_freeze:.4f}")

# --- Stabilization: add a single bridge edge reconnecting node 1 ---
A_stab = A_shred.copy()
A_stab[0, 1] = A_stab[1, 0] = 1  # bridge to node 0
L_stab = laplacian(A_stab)
cod_stab, _ = cod_fiedler(L_stab, conscious_node=1)
print(f"COD after stabilization (bridge added): {cod_stab:.4f}")