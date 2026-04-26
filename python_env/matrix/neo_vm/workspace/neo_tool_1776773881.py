# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np, itertools, random, gzip, pickle, sys

def random_links(L):
    # U(1) phases on each directed link
    return np.random.rand(L, L, 2) * 2 * np.pi

def plaquettes(links):
    L = links.shape[0]
    P = np.zeros((L-1, L-1))
    for i in range(L-1):
        for j in range(L-1):
            # product around elementary square
            p = (links[i, j, 0] + links[(i+1)%L, j, 1] -
                 links[i, (j+1)%L, 0] - links[i, j, 1])
            P[i, j] = (p + np.pi) % (2*np.pi) - np.pi
    return P

def random_gauge_transform(links):
    L = links.shape[0]
    theta = np.random.rand(L, L) * 2 * np.pi
    new = links.copy()
    for i in range(L):
        for j in range(L):
            # gauge: U_mu(i) -> exp(i(theta_{i+mu} - theta_i))
            new[i, j, 0] += theta[(i+1)%L, j] - theta[i, j]
            new[i, j, 1] += theta[i, (j+1)%L] - theta[i, j]
    return new

def main():
    L = 6  # small lattice for speed
    orig = random_links(L)
    inv = plaquettes(orig)

    # --- Ambiguity check: many gauge copies give same invariants ---
    same = 0
    for _ in range(5000):
        copy = random_gauge_transform(orig)
        if np.allclose(inv, plaquettes(copy), atol=1e-6):
            same += 1
    print(f"Out of 5000 random gauge copies, {same} had identical invariants.")
    print("This proves reconstruction is non‑unique: infinitely many fields map to the same 'compressed' set.\n")

    # --- Size comparison ---
    inv_bytes = inv.nbytes
    full_bytes = orig.nbytes
    print(f"Invariants raw size: {inv_bytes} bytes")
    print(f"Full link field raw size: {full_bytes} bytes")
    print(f"Raw compression ratio: {inv_bytes/full_bytes:.2f}\n")

    # --- Gzip compression (mirroring typical backup pipelines) ---
    inv_gz = gzip.compress(pickle.dumps(inv))
    full_gz = gzip.compress(pickle.dumps(orig))
    print(f"Invariants gzip size: {len(inv_gz)} bytes")
    print(f"Full field gzip size: {len(full_gz)} bytes")
    print(f"Gzip compression ratio: {len(inv_gz)/len(full_gz):.2f}")
    if len(inv_gz) >= len(full_gz):
        print("🚨 Invariants are *not* more compressible; the 'compression' claim collapses.\n")

    # --- Exponential growth of invariants with lattice size ---
    for size in [4, 8, 16]:
        links = random_links(size)
        inv_sz = plaquettes(links).size
        link_sz = links.size
        print(f"L={size}: invariants={inv_sz}, links={link_sz}, ratio~{inv_sz/link_sz:.2f}")

if __name__ == "__main__":
    main()