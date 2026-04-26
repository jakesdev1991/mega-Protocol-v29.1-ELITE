# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validation Script for the Functional‑Space Entanglement Monitor (FSEM‑Ω)

This script checks the mathematical soundness of the core equations presented in the
proposal and verifies that the derived Omega invariants (Φ_N, Φ_Δ, ψ) respect the
protocol’s basic constraints:

    • FFI ∈ [0, 1]   (by construction via tanh)
    • Φ_N ≥ 0        (connectivity cannot be negative)
    • ψ is finite    (avoid singularities unless intentionally at a boundary)
    • MPC‑Ω QP constraints:
          FFI ≤ 0.65
          Φ_N ≥ 0.60
          S_func ≥ ln(3)   (functional diversity gauge)

If any check fails, a ValidationError is raised with a descriptive message.
The script is self‑contained; it generates synthetic functional‑telemetry data
to demonstrate the validation pipeline.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def safe_log(x: float, eps: float = 1e-12) -> float:
    """Log that guards against log(0)."""
    return np.log(max(x, eps))


# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass
class FunctionalTelemetry:
    """Container for the raw functional observables needed by FSEM‑Ω."""
    # Functional coordinates (promoter strength, RBS efficiency, Vmax, Km, pathway flux …)
    func_coords: np.ndarray          # shape (n_devices, n_func_dims)
    # Context vector per device (host, media, temperature … encoded as floats)
    context: np.ndarray              # shape (n_devices, n_ctx_dims)
    # Crosstalk matrix: measured interference between devices (symmetric, zero‑diag)
    crosstalk: np.ndarray            # shape (n_devices, n_devices)
    # Failure flag (1 = failed to meet spec, 0 = success)
    failure: np.ndarray              # shape (n_devices,)
    # Functional type labels for entropy calculation (e.g., 0=metabolic,1=signaling,2=regulatory)
    func_type: np.ndarray            # shape (n_devices,)


# ----------------------------------------------------------------------
# Core FSEM‑Ω computations
# ----------------------------------------------------------------------
class FSEMOmega:
    """
    Implements the mathematical pipeline described in the proposal:
      - builds a low‑dimensional function‑space manifold (via UMAP‑like embedding,
        here replaced by a simple PCA for reproducibility),
      - computes gradient norm G, curvature scalar κ (Laplacian), entanglement E,
        context variance σ²_context,
      - derives FFI, Φ_N, Φ_Δ, ψ,
      - checks Omega‑Protocol invariants and MPC‑Ω QP constraints.
    """

    def __init__(
        self,
        alpha: float = 1.0,
        beta: float = 1.0,
        gamma: float = 1.0,
        delta: float = 1.0,
        eta1: float = 0.5,
        eta2: float = 0.3,
        eta3: float = 0.4,
        eta4: float = 0.2,
        tau1: float = 4.0,   # weeks – treated as a scalar shift in index for demo
        tau2: float = 4.0,
        R0: float = 1.0,
        lambd: float = 0.5,
    ):
        # FFI weighting
        self.alpha, self.beta, self.gamma, self.delta = alpha, beta, gamma, delta
        # Mapping to Omega variables
        self.eta1, self.eta2, self.eta3, self.eta4 = eta1, eta2, eta3, eta4
        self.tau1, self.tau2 = tau1, tau2
        # Curvature scaling
        self.R0, self.lambd = R0, lambd

    # ------------------------------------------------------------------
    # Manifold embedding (stand‑in for UMAP)
    # ------------------------------------------------------------------
    def _embed_function_space(self, X: np.ndarray) -> np.ndarray:
        """
        Very simple linear embedding: PCA to 3 components.
        In a real implementation this would be UMAP/PHATE on the functional
        telemetry (promoter strength, kinetics, flux …).
        """
        from sklearn.decomposition import PCA

        pca = PCA(n_components=3)
        return pca.fit_transform(X)

    # ------------------------------------------------------------------
    # Gradient norm G = ⟨‖∇ℱ‖⟩
    # ------------------------------------------------------------------
    def _gradient_norm(self, F_emb: np.ndarray) -> float:
        """
        Approximate ∇ℱ by finite differences across the point cloud.
        We compute the average pairwise distance gradient magnitude.
        """
        # Use k‑nearest neighbours (k=5) to estimate local gradient
        from sklearn.neighbors import NearestNeighbors

        nbrs = NearestNeighbors(n_neighbors=6, algorithm="auto").fit(F_emb)
        distances, _ = nbrs.kneighbors(F_emb)
        # Exclude self distance (0)
        grad_est = np.mean(distances[:, 1:])  # average distance to neighbours
        return float(grad_est)

    # ------------------------------------------------------------------
    # Curvature scalar κ = ⟨∇²ℱ⟩  (Laplacian approximation)
    # ------------------------------------------------------------------
    def _laplacian_curvature(self, F_emb: np.ndarray) -> float:
        """
        Approximate the Laplacian via the variance of pairwise distances.
        Negative values indicate saddle‑like (crosstalk) regions.
        """
        from sklearn.metrics import pairwise_distances

        dists = pairwise_distances(F_emb)
        # Laplacian ≈ mean of squared distances minus square of mean distance
        mean_d = np.mean(dists)
        mean_sq = np.mean(dists ** 2)
        kappa = mean_sq - mean_d ** 2
        return float(kappa)  # can be negative

    # ------------------------------------------------------------------
    # Entanglement index E = (1/n) Σ Crosstalk_ij²
    # ------------------------------------------------------------------
    def _entanglement_index(self, C: np.ndarray) -> float:
        return float(np.mean(C ** 2))

    # ------------------------------------------------------------------
    # Context‑dependence variance σ²_context
    # ------------------------------------------------------------------
    def _context_variance(self, ctx: np.ndarray) -> float:
        # Variance across devices for each context dimension, then average
        return float(np.mean(np.var(ctx, axis=0)))

    # ------------------------------------------------------------------
    # Functional diversity gauge S_func (Shannon entropy)
    # ------------------------------------------------------------------
    def _functional_entropy(self, labels: np.ndarray) -> float:
        vals, counts = np.unique(labels, return_counts=True)
        probs = counts / counts.sum()
        return float(-np.sum(probs * np.log(probs + 1e-12)))

    # ------------------------------------------------------------------
    # Ricci curvature proxy (we use the Laplacian of ℱ as a scalar curvature)
    # ------------------------------------------------------------------
    def _ricci_curvature(self, F_emb: np.ndarray) -> float:
        # In 2‑D manifolds, Ricci = Gaussian curvature ≈ Laplacian/2.
        # We keep it simple: use the Laplacian we already computed.
        return self._laplacian_curvature(F_emb)

    # ------------------------------------------------------------------
    # Main evaluation pipeline
    # ------------------------------------------------------------------
    def evaluate(self, tel: FunctionalTelemetry) -> Tuple[float, float, float, dict]:
        """
        Returns:
            FFI, Φ_N, Φ_Δ, ψ
        and a dict of intermediate metrics for debugging.
        """
        # 1. Embed functional coordinates into a 3‑D manifold
        F_emb = self._embed_function_space(tel.func_coords)  # (n,3)

        # 2. Compute primitive metrics
        G = self._gradient_norm(F_emb)                      # gradient norm
        kappa = self._laplacian_curvature(F_emb)            # curvature scalar
        E = self._entanglement_index(tel.crosstalk)         # entanglement
        sigma2_ctx = self._context_variance(tel.context)    # context variance

        # 3. Functional Fragility Index (tanh squashes to [0,1])
        raw = (
            self.alpha * np.abs(kappa)
            + self.beta * G
            + self.gamma * E
            + self.delta * sigma2_ctx
        )
        FFI = np.tanh(raw)  # ∈ [0,1]

        # 4. Mapping to Ω variables (using delayed values – we approximate delay by using same timestep)
        #    Baseline values Φ_N^(0), Φ_Δ^(0) set to 1.0 for illustration.
        Phi_N0 = 1.0
        Phi_Delta0 = 0.0
        Phi_N = Phi_N0 - self.eta1 * FFI + self.eta2 * (1.0 - E)
        Phi_Delta = Phi_Delta0 + self.eta3 * sigma2_ctx - self.eta4 * G

        # 5. Invariant ψ from Ricci curvature
        R_func = self._ricci_curvature(F_emb)  # scalar curvature proxy
        psi = safe_log(np.abs(R_func) / self.R0) + self.lambd * FFI

        # 6. Functional entropy (diversity gauge)
        S_func = self._functional_entropy(tel.func_type)

        intermediates = {
            "G": G,
            "kappa": kappa,
            "E": E,
            "sigma2_ctx": sigma2_ctx,
            "FFI_raw": raw,
            "R_func": R_func,
            "S_func": S_func,
        }

        return FFI, Phi_N, Phi_Delta, psi, intermediates

    # ------------------------------------------------------------------
    # Validation of Omega‑Protocol invariants & MPC‑Ω QP constraints
    # ------------------------------------------------------------------
    def validate(
        self,
        FFI: float,
        Phi_N: float,
        Phi_Delta: float,
        psi: float,
        S_func: float,
    ) -> None:
        """
        Raises ValueError if any invariant or constraint is violated.
        """
        # ---- Basic invariant checks ----
        if not (0.0 <= FFI <= 1.0):
            raise ValueError(f"FFI out of bounds: {FFI:.6f} ∉ [0,1]")
        if Phi_N < 0.0:
            raise ValueError(f"Φ_N negative: {Phi_N:.6f} (must be ≥ 0)")
        # ψ may be any real number; we only guard against NaN/Inf
        if not np.isfinite(psi):
            raise ValueError(f"ψ non‑finite: {psi}")

        # ---- MPC‑Ω QP constraints (as given in the proposal) ----
        if FFI > 0.65 + 1e-9:
            raise ValueError(
                f"MPC constraint violated: FFI = {FFI:.6f} > 0.65"
            )
        if Phi_N < 0.60 - 1e-9:
            raise ValueError(
                f"MPC constraint violated: Φ_N = {Phi_N:.6f} < 0.60"
            )
        if S_func < np.log(3) - 1e-9:
            raise ValueError(
                f"MPC constraint violated: S_func = {S_func:.6f} < ln(3) ≈ {np.log(3):.6f}"
            )

        # If we reach here, all checks passed.
        return True


# ----------------------------------------------------------------------
# Synthetic data generator for demonstration
# ----------------------------------------------------------------------
def generate_synthetic_telemetry(
    n_devices: int = 50,
    n_func_dims: int = 8,
    n_ctx_dims: int = 4,
    seed: int = 42,
) -> FunctionalTelemetry:
    rng = np.random.default_rng(seed)

    # Random functional coordinates (promoter strength, kinetics, flux …)
    func_coords = rng.uniform(0, 2, size=(n_devices, n_func_dims))

    # Random context vectors (host id encoded 0‑2, media composition, temperature)
    context = rng.uniform(0, 1, size=(n_devices, n_ctx_dims))

    # Synthetic crosstalk: symmetric with zero diagonal, values in [0,0.3]
    C = rng.uniform(0, 0.3, size=(n_devices, n_devices))
    C = (C + C.T) / 2
    np.fill_diagonal(C, 0.0)

    # Random failure flag (10% failures)
    failure = rng.choice([0, 1], size=n_devices, p=[0.9, 0.1])

    # Random functional type labels (3 categories)
    func_type = rng.integers(0, 3, size=n_devices)

    return FunctionalTelemetry(
        func_coords=func_coords,
        context=context,
        crosstalk=C,
        failure=failure,
        func_type=func_type,
    )


# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def main():
    # Instantiate the FSEM‑Ω engine with default weights (as in the proposal)
    fsem = FSEMOmega()

    # Generate synthetic telemetry
    tel = generate_synthetic_telemetry()

    # Run the evaluation pipeline
    FFI, Phi_N, Phi_Delta, psi, inter = fsem.evaluate(tel)

    # Print intermediate metrics for transparency
    print("=== FSEM‑Ω Evaluation ===")
    print(f"Gradient norm G          : {inter['G']:.4f}")
    print(f"Curvature scalar κ       : {inter['kappa']:.4f}")
    print(f"Entanglement index E     : {inter['E']:.4f}")
    print(f"Context variance σ²_ctx  : {inter['sigma2_ctx']:.4f}")
    print(f"FFI (tanh)               : {FFI:.4f}")
    print(f"Φ_N (connectivity)       : {Phi_N:.4f}")
    print(f"Φ_Δ (asymmetry)          : {Phi_Delta:.4f}")
    print(f"ψ (Ricci‑based invariant): {psi:.4f}")
    print(f"Functional entropy S_func: {inter['S_func']:.4f}")
    print("=========================")

    # Validate against Omega Protocol invariants and MPC‑Ω constraints
    try:
        fsem.validate(FFI, Phi_N, Phi_Delta, psi, inter["S_func"])
        print("\n✅ All Omega‑Protocol invariants and MPC‑Ω constraints satisfied.")
    except ValueError as e:
        print("\n❌ Validation failed:")
        print(e)
        # Optionally, one could trigger a redesign action here.


if __name__ == "__main__":
    main()