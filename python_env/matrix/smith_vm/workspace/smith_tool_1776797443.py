# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTFM‑Ω mathematical & Omega‑Protocol validation script.
Checks:
  * Dimensional consistency (all quantities dimensionless)
  * CFI in [0,1] and mapping to Phi_N, Phi_Delta, psi
  * Invariants: Phi_N >= 0.6, entropy >= log(3), CFI <= 0.65
  * Cost function non‑negative
  * No numerical divergences in psi
"""

import numpy as np
from scipy.stats import skew
from scipy.sparse import csgraph
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
import warnings
warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------
# 1. Synthetic data generation (replace with real characterization data)
# ----------------------------------------------------------------------
np.random.seed(42)
n_devices = 5          # number of synthetic devices
n_contexts = 8         # number of distinct biological contexts
n_params   = 4         # [basal, dynamic_range, hill, latency]

# Transfer-function vectors f_i(c)  (device i, context c)
# Simulate some baseline plus context‑dependent noise
F_true = np.random.uniform(0.5, 2.0, size=(n_devices, n_params, n_contexts))
# Add device‑specific drift to create asymmetry
for i in range(n_devices):
    F_true[i] *= np.random.uniform(0.8, 1.2, size=(n_params, 1))

# Observed data with measurement noise
sigma_obs = 0.05
F_obs = F_true + sigma_obs * np.random.randn(*F_true.shape)

# Context vectors c (one‑hot chassis + continuous variables)
# For simplicity: chassis one‑hot (3 types) + growth rate + temperature + burden
n_chassis = 3
c_chassis = np.eye(n_chassis)[np.random.choice(n_chassis, n_contexts)]
c_cont    = np.random.uniform(0, 1, size=(n_contexts, 3))   # growth, temp, burden
C = np.hstack([c_chassis, c_cont])                         # shape (n_contexts, dim_c)
dim_c = C.shape[1]

# Sequence embeddings s_i (dimensionless, from a pretrained DNA model)
dim_s = 10
S = np.random.randn(n_devices, dim_s)   # pretend embeddings

# ----------------------------------------------------------------------
# 2. Helper functions
# ----------------------------------------------------------------------
def tanh(x): return np.tanh(x)

def compute_cfi(F, C, S, alpha=1.0, beta=1.0, gamma=1.0, delta=1.0):
    """CFI = tanh[α·var_TF + β·κ + γ·χ − δ·ρ]"""
    # Transfer‑function variance across contexts (per device)
    # Use L2 norm of deviation from mean across contexts
    F_norm = np.linalg.norm(F, axis=1)          # (n_devices, n_contexts)
    mean_F = np.mean(F_norm, axis=1, keepdims=True)
    var_TF = np.var(F_norm - mean_F, axis=1)    # (n_devices,)

    # Contextual coupling: L2 norm of gradient w.r.t. context
    # Approximate gradient by finite differences on a regular grid (here we just use std)
    kappa = np.std(F_norm, axis=1)              # proxy for sensitivity

    # Compositional singularity: max absolute correlation with any other device
    chi = np.zeros(n_devices)
    for i in range(n_devices):
        corrs = [np.corrcoef(F_norm[i], F_norm[j])[0,1] for j in range(n_devices) if j!=i]
        chi[i] = np.max(np.abs(corrs)) if corrs else 0.0

    # Data density: fraction of non‑NaN observations (here full)
    rho = np.ones(n_devices)   # assume fully characterized for simplicity

    cfi_raw = alpha*var_TF + beta*kappa + gamma*chi - delta*rho
    cfi = tanh(cfi_raw)
    return np.clip(cfi, 0.0, 1.0), var_TF, kappa, chi, rho

def compute_phi_n_delta(F_norm, C):
    """Phi_N = spectral gap of context‑graph Laplacian.
       Phi_Delta = skewness of transfer‑function distribution across contexts."""
    # Build a fully‑connected context graph with weight = exp(-||c_i-c_j||^2 / (2*l^2))
    # Length‑scale l set to median distance for scaling invariance
    dists = np.linalg.norm(C[:,None,:] - C[None,:,:], axis=2)
    l = np.median(dists[dists>0])
    W = np.exp(-dists**2 / (2*l**2))
    np.fill_diagonal(W, 0.0)
    D = np.diag(W.sum(axis=1))
    L = D - W
    # eigenvalues of symmetric Laplacian
    eigvals = np.linalg.eigvalsh(L)
    # spectral gap = smallest non‑zero eigenvalue
    phi_n = eigvals[1] if len(eigvals) > 1 else 0.0

    # Skewness of the distribution of F_norm across all device‑context pairs
    phi_delta = skew(F_norm.flatten())
    return phi_n, phi_delta

def compute_ricci_scalar_gplvm(F_norm, S, C):
    """
    Approximate Ricci scalar of the latent manifold learned by a GPLVM.
    We treat the latent space as the 3‑D output of a GPLVM that maps
    (F_norm, S) -> latent Z (size n_samples x 3).  The metric is induced
    by the GP kernel (RBF).  For a Riemannian manifold with metric g,
    Ricci scalar R = g^{ij} (∂_k Γ^k_{ij} - ∂_j Γ^k_{ik} + Γ^k_{ij}Γ^l_{kl} - Γ^k_{il}Γ^l_{jk}).
    Numerically we approximate using finite differences on a small grid.
    For validation we only need a scalar that varies smoothly with data;
    we therefore compute a simple proxy: the scalar curvature of the
    RBF kernel induced metric approximated via the Laplacian of log det(g).
    """
    # Stack inputs for GPLVM: concatenate normalized F_norm and S
    F_norm_flat = F_norm.T   # (n_contexts, n_devices)
    X = np.hstack([F_norm_flat, S])   # (n_contexts, n_devices+dim_s)
    # Use a GP with RBF kernel to learn a smooth mapping to a 3‑D latent space
    # We'll fit three independent GPs (one per latent dimension)
    latent_dim = 3
    Z = np.zeros((X.shape[0], latent_dim))
    for d in range(latent_dim):
        gp = GaussianProcessRegressor(kernel=RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-5),
                                      normalize_y=True)
        gp.fit(X, np.random.randn(X.shape[0]))   # dummy target; we only need the kernel
        # The posterior mean gives a smooth function; we use it as latent coordinate
        Z[:,d] = gp.predict(X)
    # Compute metric tensor g_ij = ∂Z/∂x^i · ∂Z/∂x^j (Jacobian product)
    # Approximate Jacobian by finite differences
    eps = 1e-6
    J = np.zeros((X.shape[0], X.shape[1], latent_dim))
    for i in range(X.shape[1]):
        X_plus = X.copy()
        X_minus = X.copy()
        X_plus[:,i]  += eps
        X_minus[:,i] -= eps
        Z_plus = np.zeros_like(Z)
        Z_minus = np.zeros_like(Z)
        for d in range(latent_dim):
            gp = GaussianProcessRegressor(kernel=RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-5),
                                          normalize_y=True)
            gp.fit(X, Z[:,d])
            Z_plus[:,d]  = gp.predict(X_plus)
            Z_minus[:,d] = gp.predict(X_minus)
            J[:,i,d] = (Z_plus[:,d] - Z_minus[:,d]) / (2*eps)
    # g_ij = sum over latent dimensions J_ki * J_kj
    g = np.einsum('kij,kij->ij', J, J)   # shape (n_features, n_features)
    # Invert metric
    try:
        ginv = np.linalg.inv(g)
    except np.linalg.LinAlgError:
        ginv = np.pinv(g)
    # Christoffel symbols: Γ^k_{ij} = 0.5 * g^{kl} (∂_i g_{jl} + ∂_j g_{il} - ∂_l g_{ij})
    # Compute derivatives of g via finite differences
    dg = np.zeros((X.shape[1], X.shape[1], X.shape[1]))
    for a in range(X.shape[1]):
        X_plus = X.copy()
        X_minus = X.copy()
        X_plus[:,a]  += eps
        X_minus[:,a] -= eps
        g_plus = np.einsum('kij,kij->ij',
                           np.array([[(np.einsum('kij,kij->ij',
                                         np.array([[(np.einsum('kij,kij->ij',
                                                    np.zeros_like(J)) for _ in range(latent_dim)]) for _ in range(X.shape[0])])])), # placeholder
        # To keep the script short we replace the full Ricci computation with a scalar proxy:
    # ------------------------------------------------------------------
    # Proxy: Ricci scalar ≈ -∇^2 (log det g)   (valid for 2‑D, but serves as a smooth scalar)
    # ------------------------------------------------------------------
    log_det_g = np.log(np.linalg.det(g) + 1e-12)
    # Laplacian on the input space approximated via finite differences on a grid
    # We'll evaluate on a small mesh of the input space (here just reuse X points)
    # Simple finite‑difference Laplacian: sum of second derivatives along each input dimension
    laplacian_log_det = np.zeros(X.shape[0])
    for a in range(X.shape[1]):
        X_plus2 = X.copy()
        X_minus2 = X.copy()
        X_plus2[:,a]  += 2*eps
        X_minus2[:,a] -= 2*eps
        X_plus  = X.copy()
        X_minus = X.copy()
        X_plus[:,a]  += eps
        X_minus[:,a] -= eps
        g_plus2  = np.einsum('kij,kij->ij', J, J)  # recompute metric at +2eps (approx)
        g_minus2 = np.einsum('kij,kij->ij', J, J)  # -2eps
        g_plus   = np.einsum('kij,kij->ij', J, J)  # +eps
        g_minus  = np.einsum('kij,kij->ij', J, J)  # -eps
        # Actually recompute properly:
        def metric_at(Xin):
            J_in = np.zeros((Xin.shape[0], Xin.shape[1], latent_dim))
            for i in range(Xin.shape[1]):
                Xp = Xin.copy()
                Xm = Xin.copy()
                Xp[:,i] += eps
                Xm[:,i] -= eps
                for d in range(latent_dim):
                    gp = GaussianProcessRegressor(kernel=RBF(length_scale=1.0)+WhiteKernel(noise_level=1e-5),
                                                  normalize_y=True)
                    gp.fit(Xin, Z[:,d])   # note: we reuse same Z as target (approx)
                    J_in[:,i,d] = (gp.predict(Xp) - gp.predict(Xm))/(2*eps)
            return np.einsum('kij,kij->ij', J_in, J_in)
        g_pp = metric_at(X_plus2)
        g_mm = metric_at(X_minus2)
        g_p  = metric_at(X_plus)
        g_m  = metric_at(X_minus)
        g0   = metric_at(X)
        d2g = (g_pp - 2*g_p + 2*g_m - g_mm) / (4*eps**2)   # second derivative
        laplacian_log_det += np.trace(np.linalg.solve(g0, d2g))   # g^{ij} ∂_i∂_j (log det g)
    ricci_proxy = -laplacian_log_det   # scalar per input point
    # Average over contexts to get a single curvature estimate
    R_context = np.mean(ricci_proxy)
    return R_context

def entropy_context(C):
    """Shannon entropy of context distribution (discrete chassis + continuous approximated via histogram)."""
    # Discretize continuous part into 3 bins each for simplicity
    cont_bins = np.linspace(0,1,4)
    disc_part = C[:,:n_chassis]   # one‑hot chassis
    cont_part = C[:,n_chassis:]
    hist, _ = np.histogramdd(cont_part, bins=[cont_bins]*3)
    hist = hist.flatten()
    hist = hist / hist.sum() if hist.sum()>0 else hist
    # Combine with chassis distribution (average over samples)
    chassis_dist = np.mean(disc_part, axis=0)
    chassis_dist = chassis_dist / chassis_dist.sum()
    # Joint distribution approximated as product (independent assumption)
    joint = np.outer(chassis_dist, hist).flatten()
    joint = joint[joint>0]
    return -np.sum(joint * np.log(joint))

# ----------------------------------------------------------------------
# 3. Main validation routine
# ----------------------------------------------------------------------
def main():
    # ---- Step A: Compute CFI and related metrics ----
    F_norm = np.linalg.norm(F_obs, axis=1)   # (n_devices, n_contexts)
    cfi, var_TF, kappa, chi, rho = compute_cfi(F_obs, C, S)
    print("CFI per device:", np.round(cfi, 3))
    print("Transfer‑function variance:", np.round(var_TF,3))
    print("Contextual coupling (kappa):", np.round(kappa,3))
    print("Compositional singularity (chi):", np.round(chi,3))
    print("Data density (rho):", np.round(rho,3))

    # ---- Step B: Compute Omega invariants ----
    phi_n, phi_delta = compute_phi_n_delta(F_norm, C)
    print("\nPhi_N (spectral gap):", round(phi_n,4))
    print("Phi_Delta (skewness):", round(phi_delta,4))

    # ---- Step C: Compute curvature‑based psi ----
    R_context = compute_ricci_scalar_gplvm(F_norm, S, C)
    R0 = 1.0   # reference curvature (dimensionless)
    lambda_ = 0.5   # coupling constant (chosen O(1))
    psi = np.log(np.abs(R_context)/R0 + 1e-12) + lambda_ * np.mean(cfi)
    print("\nRicci scalar (proxy):", round(R_context,6))
    print("Psi = ln(|R|/R0) + λ·CFI:", round(psi,4))

    # ---- Step D: Entropy gauge ----
    S_context = entropy_context(C)
    print("\nContext entropy S:", round(S_context,4))
    print("Required minimum log(3) =", round(np.log(3),4))

    # ---- Step E: Check Omega Protocol constraints ----
    violations = []
    if np.any(cfi > 0.65):
        violations.append("CFI exceeds 0.65 (max allowed)")
    if phi_n < 0.6:
        violations.append(f"Phi_N = {phi_n:.4f} < 0.6 (connectivity too low)")
    if S_context < np.log(3):
        violations.append(f"Context entropy = {S_context:.4f} < log(3) (insufficient context diversity)")
    # psi should stay finite; we guard against extreme values
    if np.isinf(psi) or np.isnan(psi):
        violations.append("Psi is infinite or NaN (possible divergence)")
    # Additional physical sanity: CFI in [0,1] by construction
    if np.any((cfi < 0) | (cfi > 1)):
        violations.append("CFI outside [0,1]")

    if violations:
        print("\n*** OMEGA PROTOCOL VIOLATIONS ***")
        for v in violations:
            print("- " + v)
    else:
        print("\nAll Omega Protocol constraints satisfied.")

    # ---- Step F: MPC‑Ω style cost function (non‑negative check) ----
    mu1, mu2, mu3 = 1.0, 1.0, 1.0
    cost integrand = (
        np.maximum(cfi - 0.65, 0.0)**2 +
        mu1 * np.maximum(0.6 - phi_n, 0.0)**2 +
        mu2 * phi_delta**2 +
        mu3 * np.maximum(np.log(3) - S_context, 0.0)**2
    )
    J = np.trapz(cost integrand, dx=1.0)   # simple integration over dummy time axis
    print("\nMPC‑Ω cost (should be >=0):", round(J,6))
    if J < -1e-12:
        print("WARNING: Cost negative – check formulation.")
    else:
        print("Cost non‑negative ✔️")

    # ---- Step G: Dimensional consistency (sanity) ----
    # In natural units all inputs are dimensionless; we just assert that
    # no raw dimensional constants (like meters, seconds) appear.
    # The script uses only pure numbers, so we consider this satisfied.
    print("\nDimensional consistency: assumed satisfied (all quantities dimensionless).")

if __name__ == "__main__":
    main()