# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh

# ------------------------------------------------------------
# Lattice geometry: 4x4x4 periodic (torus) to allow nontrivial H^2
# ------------------------------------------------------------
L = 4
Nverts = L**3
Nedges = 3 * L**3  # each vertex has 3 edges in periodic grid
Nfaces = 3 * L**3  # each edge belongs to 2 faces, but counting unique faces
Ncubes = L**3

# ------------------------------------------------------------
# Build incidence matrices d0: V->E, d1: E->F, d2: F->C
# ------------------------------------------------------------
def build_incidence():
    # vertex index i = x + L*y + L*L*z
    def idx(x, y, z):
        return (x % L) + L * ((y % L) + L * (z % L))

    # d0: Nedges x Nverts
    d0_data, d0_row, d0_col = [], [], []
    # d1: Nfaces x Nedges
    d1_data, d1_row, d1_col = [], [], []
    # d2: Ncubes x Nfaces
    d2_data, d2_row, d2_col = [], [], []

    # Edges: oriented along x (0), y (1), z (2)
    edge_id = 0
    for z in range(L):
        for y in range(L):
            for x in range(L):
                v0 = idx(x, y, z)
                # x-edge
                v1 = idx(x+1, y, z)
                d0_data.extend([1, -1])
                d0_row.extend([edge_id, edge_id])
                d0_col.extend([v0, v1])
                edge_id += 1
                # y-edge
                v1 = idx(x, y+1, z)
                d0_data.extend([1, -1])
                d0_row.extend([edge_id, edge_id])
                d0_col.extend([v0, v1])
                edge_id += 1
                # z-edge
                v1 = idx(x, y, z+1)
                d0_data.extend([1, -1])
                d0_row.extend([edge_id, edge_id])
                d0_col.extend([v0, v1])
                edge_id += 1

    # Faces: oriented by right-hand rule (xy, yz, zx)
    face_id = 0
    for z in range(L):
        for y in range(L):
            for x in range(L):
                # xy-face: edges (x-edge at y,z), (y-edge at x+1,z), (x-edge at y+1,z), (y-edge at x,z)
                # Simplified: we just need the boundary orientation for d1
                # Each face is a 2-cell bounded by 4 edges; we store orientation +/-1
                # For brevity, we hardcode the pattern for a unit cube face
                # Edge IDs: x-edge at (x,y,z) = 3*idx(x,y,z) + 0
                #           y-edge at (x,y,z) = 3*idx(x,y,z) + 1
                ex0 = 3 * idx(x, y, z) + 0
                ey0 = 3 * idx(x, y, z) + 1
                ex1 = 3 * idx(x, y+1, z) + 0
                ey1 = 3 * idx(x+1, y, z) + 1
                # xy-face boundary: ex0 -> ey1 -> -ex1 -> -ey0
                d1_data.extend([1, 1, -1, -1])
                d1_row.extend([face_id] * 4)
                d1_col.extend([ex0, ey1, ex1, ey0])
                face_id += 1

                # yz-face: edges (y-edge at x,z), (z-edge at x,y+1,z), (y-edge at x,z+1), (z-edge at x,y,z)
                ey0 = 3 * idx(x, y, z) + 1
                ez0 = 3 * idx(x, y, z) + 2
                ey1 = 3 * idx(x, y, z+1) + 1
                ez1 = 3 * idx(x, y+1, z) + 2
                d1_data.extend([1, 1, -1, -1])
                d1_row.extend([face_id] * 4)
                d1_col.extend([ey0, ez1, ey1, ez0])
                face_id += 1

                # zx-face: edges (z-edge at x,y), (x-edge at x,y,z+1), (z-edge at x+1,y), (x-edge at x,y,z)
                ez0 = 3 * idx(x, y, z) + 2
                ex0 = 3 * idx(x, y, z) + 0
                ez1 = 3 * idx(x+1, y, z) + 2
                ex1 = 3 * idx(x, y, z+1) + 0
                d1_data.extend([1, 1, -1, -1])
                d1_row.extend([face_id] * 4)
                d1_col.extend([ez0, ex1, ez1, ex0])
                face_id += 1

    # Cubes: each cube is bounded by 6 faces (oriented outward)
    cube_id = 0
    for z in range(L):
        for y in range(L):
            for x in range(L):
                # Collect face IDs for the 6 faces of the cube at (x,y,z)
                # xy-face at (x,y,z)
                f_xy0 = 3 * idx(x, y, z) + 0
                f_xy1 = 3 * idx(x, y, z) + 0 + 1  # opposite face
                # yz-face
                f_yz0 = 3 * idx(x, y, z) + 1
                f_yz1 = 3 * idx(x, y, z) + 1 + 1
                # zx-face
                f_zx0 = 3 * idx(x, y, z) + 2
                f_zx1 = 3 * idx(x, y, z) + 2 + 1
                # Simplified: we just need orientation signs for d2
                # Outward orientation for each face
                d2_data.extend([1, -1, 1, -1, 1, -1])
                d2_row.extend([cube_id] * 6)
                d2_col.extend([f_xy0, f_xy1, f_yz0, f_yz1, f_zx0, f_zx1])
                cube_id += 1

    d0 = csr_matrix((d0_data, (d0_row, d0_col)), shape=(Nedges, Nverts))
    d1 = csr_matrix((d1_data, (d1_row, d1_col)), shape=(Nfaces, Nedges))
    d2 = csr_matrix((d2_data, (d2_row, d2_col)), shape=(Ncubes, Nfaces))

    return d0, d1, d2

d0, d1, d2 = build_incidence()

# ------------------------------------------------------------
# Compute Laplacian on 2-cochains: L2 = d1 d1^T + d2^T d2
# ------------------------------------------------------------
L2 = d1 @ d1.T + d2.T @ d2

# ------------------------------------------------------------
# Find harmonic cochains: kernel of L2 (eigenvalue ~0)
# ------------------------------------------------------------
# Use a small tolerance for zero eigenvalues
eigvals, eigvecs = eigsh(L2, k=10, sigma=0.0, which='LM')
harmonic_mask = np.isclose(eigvals, 0, atol=1e-8)
b2 = harmonic_mask.sum()
print(f"Betti number b2 (dim H^2) = {b2}")

# ------------------------------------------------------------
# Construct a representative 2-cocycle for the Archive mode
# ------------------------------------------------------------
if b2 > 0:
    # Take the first harmonic eigenvector as the Archive mode
    Phi_Delta = eigvecs[:, harmonic_mask][:, 0]
    # Normalize to integer values (cohomology classes are quantized)
    Phi_Delta_int = np.rint(Phi_Delta / np.max(np.abs(Phi_Delta)) * 3).astype(int)
    print(f"Archive mode (2-cocycle) sample values: {Phi_Delta_int[:12]}")
    # Topological theta term: sum over faces
    theta = int(np.sum(Phi_Delta_int))
    print(f"Topological theta term (quantized): {theta}")
    # Effective coupling shift: Delta(1/alpha) = theta / (2π)
    # Thus alpha_eff = alpha / (1 + alpha * theta/(2π)) ≈ alpha (1 - alpha*theta/(2π))
    # For small alpha, the shift is linear in alpha (not alpha^2) but *quantized*.
    alpha = 1/137.035999084  # fine-structure constant
    delta_alpha_top = -alpha**2 * theta / (2*np.pi)
    print(f"Quantized shift in alpha_fs: {delta_alpha_top:.3e}")
else:
    print("No nontrivial H^2; topological term vanishes.")

# ------------------------------------------------------------
# Compare with naive perturbative log term (subleading)
# ------------------------------------------------------------
# Assume lattice spacing a = 1/L and m_Delta ~ 1/a
a = 1.0 / L
m_Delta = 1.0 / a
Lambda = np.pi / a  # UV cutoff
log_term = np.log(Lambda**2 / m_Delta**2) - 5/3
delta_alpha_pert = (alpha**2 / (3*np.pi)) * log_term
print(f"Perturbative log shift (incorrect scaling): {delta_alpha_pert:.3e}")
print(f"Ratio topological/perturbative: {delta_alpha_top/delta_alpha_pert:.1e}")