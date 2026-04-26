# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

# Reaction rates (normalized to cap‑addition rate = 1)
k_cap = 1.0      # capping enzyme forward rate
k_decap = 0.5    # decapping enzyme rate (tunable)
k_decay = 0.1    # capped RNA decay rate

# Construct directed hypergraph Laplacian L = D_out - K where K_ij = rate i→j
# States: 0 = uncapped, 1 = capped, 2 = decayed (absorbing)
K = np.array([[0,        k_cap,     0],
              [k_decap,  0,         k_decay],
              [0,        0,         0]])   # decayed state is sink

# Out‑degree diagonal matrix
D_out = np.diag(K.sum(axis=1))

# Graph Laplacian (asymmetric for directed graph)
L = D_out - K

# Compute eigenvalues of the symmetrized Laplacian L_sym = (L + L.T)/2
# (spectral gap of the directed graph is bounded by the symmetric part)
L_sym = 0.5 * (L + L.T)
eigvals = la.eigvalsh(L_sym, eigvals_only=True)
eigvals_sorted = np.sort(eigvals)

# Spectral gap λ₂ (second smallest eigenvalue)
lambda2 = eigvals_sorted[1] if len(eigvals_sorted) > 1 else 0
mixing_time = 1.0 / lambda2 if lambda2 > 1e-12 else np.inf

# Cheeger constant (approximate via edge boundary / min volume)
# For this tiny graph we brute‑force compute the minimal cut
def cheeger_constant(K):
    n = K.shape[0]
    min_ratio = np.inf
    for mask in range(1, 2**n - 1):
        S = [i for i in range(n) if mask & (1 << i)]
        V_S = sum(K.sum(axis=1)[S])  # volume of S (out‑going weight)
        V_S_comp = sum(K.sum(axis=1)[i] for i in range(n) if i not in S)
        # edges from S to complement
        boundary = sum(K[i, j] for i in S for j in range(n) if j not in S)
        ratio = boundary / min(V_S, V_S_comp) if min(V_S, V_S_comp) > 0 else np.inf
        min_ratio = min(min_ratio, ratio)
    return min_ratio

cheeger = cheeger_constant(K)

# Print diagnostics
print(f"k_decap = {k_decap:.2f}")
print(f"Spectral gap λ₂ = {lambda2:.4f}")
print(f"Mixing time τ_mix = {mixing_time:.2e}")
print(f"Cheeger constant h = {cheeger:.4f}")

# Sweep decapping rate to show percolation transition
k_decaps = np.linspace(0.1, 2.0, 50)
gaps = []
cheegers = []
for kd in k_decaps:
    K_local = np.array([[0, k_cap, 0],
                        [kd, 0, k_decay],
                        [0, 0, 0]])
    D_local = np.diag(K_local.sum(axis=1))
    L_local = D_local - K_local
    L_sym_local = 0.5 * (L_local + L_local.T)
    ev = la.eigvalsh(L_sym_local, eigvals_only=True)
    gaps.append(ev[1] if len(ev) > 1 else 0)
    cheegers.append(cheeger_constant(K_local))

# Plot transition
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(k_decaps, gaps, marker='o')
ax[0].set_xlabel('Decapping rate k_decap')
ax[0].set_ylabel('Spectral gap λ₂')
ax[0].set_title('Spectral gap collapse')
ax[1].plot(k_decaps, cheegers, marker='s', color='orange')
ax[1].set_xlabel('Decapping rate k_decap')
ax[1].set_ylabel('Cheeger constant h')
ax[1].set_title('Network fragmentation')
plt.tight_layout()
plt.savefig('capping_percolation.png')
plt.show()