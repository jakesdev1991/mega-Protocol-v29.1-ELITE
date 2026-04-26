# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation for Functional‑Space Entanglement Monitor (FSEM‑Ω)
Agent Smith – The Matrix Guardian
"""

import numpy as np
try:
    import umap
    _HAS_UMAP = True
except Exception:  # pragma: no cover
    _HAS_UMAP = False
    from sklearn.decomposition import PCA

def synthetic_telemetry(n_devices=50, n_contexts=5, seed=42):
    """Generate mock functional data: promoter strength, RBS, Vmax, Km, flux."""
    rng = np.random.default_rng(seed)
    # Base functional coordinates (4 dims)
    func = rng.uniform(0, 2, size=(n_devices, 4))
    # Context vectors (host, media, temp, etc.)
    ctx = rng.uniform(0, 1, size=(n_devices, n_contexts))
    # Crosstalk matrix: random symmetric with low baseline
    X = rng.normal(scale=0.1, size=(n_devices, n_devices))
    crosstalk = (X + X.T) / 2
    np.fill_diagonal(crosstalk, 0.0)
    # Failure flag: 1 if any crosstalk > 0.3 or flux low
    failure = (np.any(crosstalk > 0.3, axis=1) | (func[:, -1] < 0.3)).astype(int)
    return func, ctx, crosstalk, failure

def embed_function_space(func_coords):
    """Embed functional coordinates into a 3D manifold."""
    if _HAS_UMAP:
        reducer = umap.UMAP(n_components=3, random_state=0)
        emb = reducer.fit_transform(func_coords)
    else:
        pca = PCA(n_components=3)
        emb = pca.fit_transform(func_coords)
    return emb  # shape (n,3)

def compute_metrics(emb, ctx, crosstalk):
    """Gradient (norm), Laplacian (curvature scalar), entanglement, context variance."""
    # Approximate gradient via finite differences on a simple grid:
    # Use k-nearest neighbours to estimate local variation.
    from sklearn.neighbors import NearestNeighbors
    nbrs = NearestNeighbors(n_neighbors=5, algorithm='auto').fit(emb)
    distances, indices = nbrs.kneighbors(emb)
    # Gradient magnitude: average change in function value per distance
    grad_vals = []
    for i, neigh in enumerate(indices):
        diff = emb[neigh] - emb[i]
        dist = np.linalg.norm(diff, axis=1)
        # avoid zero dist
        mask = dist > 1e-8
        if np.any(mask):
            grad_vals.append(np.mean(np.linalg.norm(diff[mask], axis=1) / dist[mask]))
    G = np.mean(grad_vals) if grad_vals else 0.0

    # Laplacian (curvature scalar): average of second‑order differences
    lap_vals = []
    for i, neigh in enumerate(indices):
        diff = emb[neigh] - emb[i]
        dist2 = np.sum(diff**2, axis=1)
        mask = dist2 > 1e-8
        if np.any(mask):
            lap_vals.append(np.mean(dist2[mask]))
    kappa = np.mean(lap_vals) if lap_vals else 0.0  # positive => convex, negative => saddle

    # Entanglement index: mean squared crosstalk
    E = np.mean(crosstalk**2)

    # Context variance: variance of functional output across contexts for each device
    # Use first functional coordinate as proxy for output (e.g., promoter strength)
    func_output = emb[:, 0][:, None]  # (n,1)
    # replicate across contexts and compute variance per device
    context_var = np.var(np.tile(func_output, (1, ctx.shape[1])) * ctx, axis=1)
    sigma2_ctx = np.mean(context_var)

    return G, kappa, E, sigma2_ctx

def compute_ffi(G, kappa, E, sigma2_ctx, alpha=1.0, beta=1.0, gamma=1.0, delta=1.0):
    """Functional Fragility Index in [0,1] via tanh."""
    arg = alpha * np.abs(kappa) + beta * G + gamma * E + delta * sigma2_ctx
    return np.tanh(arg)

def update_omega_vars(FFI_prev, PhiN0, PhiDelta0, eta1=0.2, eta2=0.1,
                      eta3=0.15, eta4=0.1, tau1=3, tau2=3):
    """Simple linear update (ignoring time lag for static validation)."""
    PhiN = PhiN0 - eta1 * FFI_prev + eta2 * (1 - np.mean(EE))  # EE placeholder
    PhiDelta = PhiDelta0 + eta3 * sigma2_ctx - eta4 * G
    return PhiN, PhiDelta

def ricci_approx(emb):
    """Very rough Ricci scalar: trace of Hessian of embedding coordinates."""
    # Fit a quadratic model locally and take trace of its Hessian.
    from sklearn.linear_model import Ridge
    n = emb.shape[0]
    ricci_vals = []
    for i in range(n):
        # Use 5 nearest neighbours
        nbrs = NearestNeighbors(n_neighbors=6).fit(emb)
        dist, idx = nbrs.kneighbors(emb[i].reshape(1, -1))
        idx = idx[0][1:]  # exclude self
        A = emb[idx]
        # target: squared distance from centre (quadratic form)
        b = np.sum((A - emb[i])**2, axis=1)
        model = Ridge(alpha=1e-3, fit_intercept=False).fit(A, b)
        # Hessian of quadratic form is 2 * coeff matrix (since model predicts x^T C x)
        C = model.coef_.reshape(3, 3)
        ricci_vals.append(np.trace(C))
    return np.mean(ricci_vals)

def validate_ffsem_omega():
    func, ctx, xtalk, failure = synthetic_telemetry()
    emb = embed_function_space(func)
    G, kappa, E, sigma2_ctx = compute_metrics(emb, ctx, xtalk)
    FFI = compute_ffi(G, kappa, E, sigma2_ctx)

    # Baseline Omega variables (arbitrary but within physical range)
    PhiN0, PhiDelta0 = 0.8, 0.0
    # For static validation we ignore time lag; use current FFI
    PhiN = PhiN0 - 0.2 * FFI + 0.1 * (1 - E)
    PhiDelta = PhiDelta0 + 0.15 * sigma2_ctx - 0.1 * G

    # Ricci curvature and psi
    R_func = ricci_approx(emb)
    R0 = 1.0
    lam = 0.5
    psi = np.log(np.abs(R_func) / R0) + lam * FFI

    # Functional entropy (shannon over functional types – mock 3 types)
    # Assign each device to a type based on clustering of first coordinate
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=3, random_state=0).fit(emb[:, 0][:, None])
    _, counts = np.unique(km.labels_, return_counts=True)
    p = counts / counts.sum()
    S_func = -np.sum(p * np.log(p + 1e-12))

    # MPC‑Ω constraints
    violations = []
    if FFI > 0.65:
        violations.append(f"FFI too high: {FFI:.3f} > 0.65")
    if PhiN < 0.6:
        violations.append(f"Phi_N too low: {PhiN:.3f} < 0.6")
    if S_func < np.log(3):
        violations.append(f"Functional entropy too low: {S_func:.3f} < log(3)≈{np.log(3):.3f}")

    # Action sanity: double‑well coefficients should keep V bounded below
    alpha, beta = 1.0, 1.0  # as in proposal
    V = 0.5 * alpha * np.mean(emb**2) + 0.25 * beta * np.mean(emb**4)
    if V < 0:
        violations.append(f"Double‑well potential negative: {V:.3f} (unstable)")

    # Output
    print("=== FSEM‑Ω Validation Report ===")
    print(f"Gradient G          : {G:.4f}")
    print(f"Curvature κ         : {kappa:.4f}")
    print(f"Entanglement E      : {E:.4f}")
    print(f"Context variance    : {sigma2_ctx:.4f}")
    print(f"Functional Fragility Index (FFI) : {FFI:.4f}")
    print(f"Phi_N               : {PhiN:.4f}")
    print(f"Phi_Delta           : {PhiDelta:.4f}")
    print(f"Ricci curvature R   : {R_func:.4f}")
    print(f"Psi                 : {psi:.4f}")
    print(f"Functional entropy S_func : {S_func:.4f}")
    print(f"Double‑well V       : {V:.4f}")
    if violations:
        print("\n⚠️  PROTOCOL VIOLATIONS:")
        for v in violations:
            print(" -", v)
        return False
    else:
        print("\n✅  All Omega invariants satisfied.")
        return True

if __name__ == "__main__":
    validate_ffsem_omega()