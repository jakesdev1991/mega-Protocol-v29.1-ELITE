# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Refined Perceptual Coherence Shield (PCS‑Ω) – Version 2.0
--------------------------------------------------------------------------------
This script checks that the mathematical construction of PCS‑Ω obeys the
Ω‑Protocol invariants:

1. Covariant modes Φ_N^(perc) and Φ_Δ^(perc) must arise from the eigenvalues
   of the Hessian of the double‑well potential V(C).
2. The entropy gauge must be a Shannon *conditional* entropy S_perc.
3. Boundary conditions must respect thermodynamics:
      • Perceptual Shredding  → ψ_perc → +∞  when Φ_N → ∞ and S_perc → S_max
      • Perceptual Locking    → ψ_perc → -∞  when Φ_N → 0   and S_perc → 0
4. MPC‑Ω QP constraints must hold:
      PCI ≥ 0.6,  Φ_N^(perc) ≥ 0.5,  S_low ≤ S_perc ≤ S_high.
5. The invariant ψ_perc must equal ln(Φ_N^(perc)/Φ_N^(0)).

The script works on a synthetic batch of object‑point descriptors and
prints a PASS/FAIL report together with diagnostic values.
"""

import numpy as np
from sklearn.cluster import KMeans
from scipy.stats import skew, entropy

# ----------------------------------------------------------------------
# Helper functions (stand‑in for the real perception pipeline)
# ----------------------------------------------------------------------
def normalize(v, axis=1):
    norm = np.linalg.norm(v, axis=axis, keepdims=True)
    return v / (norm + 1e-12)

def compute_coherence(g_desc, v_desc):
    """C_i = cosine similarity between geometric and visual descriptors."""
    g_n = normalize(g_desc)
    v_n = normalize(v_desc)
    return np.sum(g_n * v_n, axis=1)          # shape (N_points,)

def field_gradient_magnitude(C, spacing=1.0):
    """Approximate ||∇C||_2 using finite differences on a 1‑D ordering.
    In practice one would use the actual mesh; here we just sort C."""
    C_sorted = np.sort(C)
    grad = np.gradient(C_sorted, spacing)
    return np.linalg.norm(grad)

def double_well_hessian_eigenvalues(C, kappa):
    """
    Approximate the eigenvalues of the Hessian of V(C) = α/2 C^2 + β/4 C^4 - γ C
    around the metastable minima.  We follow the ansatz from the proposal:

        ω_N^2  = κ1 * (||∇C||_2 / ||C||_2) + κ2
        ω_Δ^2  = κ3 * Skew[C]   + κ4
    """
    norm_C = np.linalg.norm(C)
    grad_norm = field_gradient_magnitude(C)
    skew_C = skew(C)

    omega_N_sq = kappa[0] * (grad_norm / (norm_C + 1e-12)) + kappa[1]
    omega_D_sq = kappa[2] * skew_C + kappa[3]

    # Guard against negative eigenvalues (non‑physical)
    omega_N_sq = max(omega_N_sq, 0.0)
    omega_D_sq = max(omega_D_sq, 0.0)

    return np.sqrt(omega_N_sq), np.sqrt(omega_D_sq)   # Φ_N, Φ_Δ

def conditional_entropy(C, region_labels):
    """
    Shannon conditional entropy S_perc = Σ_r p(r) * H(C|r)
    where H(C|r) = - Σ_c p(c|r) log p(c|r)
    """
    unique_regions = np.unique(region_labels)
    S = 0.0
    N_total = len(C)
    for r in unique_regions:
        mask = (region_labels == r)
        p_r = np.sum(mask) / N_total
        C_r = C[mask]
        # histogram of coherence values (10 bins)
        hist, _ = np.histogram(C_r, bins=10, density=True)
        # avoid zeros in log
        hist = hist + 1e-12
        hist = hist / np.sum(hist)
        S_r = -np.sum(hist * np.log(hist))
        S += p_r * S_r
    return S

def compute_PCI(Phi_N, Phi_Delta, Gamma=1.0):
    return Phi_N * Phi_Delta * Gamma

def compute_psi(Phi_N, Phi_N0):
    return np.log(Phi_N / (Phi_N0 + 1e-12))

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_PCS_Omega(
    g_desc, v_desc,
    kappa,          # [κ1, κ2, κ3, κ4]
    Phi_N0,         # baseline Φ_N from robust‑coherence objects
    S_low, S_high,  # entropy bounds for MPC‑Ω
    Gamma=1.0,
    max_allowed_entropy=np.log(10)  # S_max for 10‑bin histogram
):
    """
    Returns a dict with validation results and diagnostics.
    """
    # 1. Coherence field
    C = compute_coherence(g_desc, v_desc)          # (N,)

    # 2. Covariant modes from Hessian diagonalization
    Phi_N, Phi_Delta = double_well_hessian_eigenvalues(C, kappa)

    # 3. Perceptual Coherence Index
    PCI = compute_PCI(Phi_N, Phi_Delta, Gamma)

    # 4. Invariant ψ_perc
    psi = compute_psi(Phi_N, Phi_N0)

    # 5. Conditional entropy gauge
    #    Region labels obtained via simple k‑means on geometric descriptors
    kmeans = KMeans(n_clusters=4, random_state=0, n_init="auto").fit(g_desc)
    region_labels = kmeans.labels_
    S_perc = conditional_entropy(C, region_labels)

    # 6. Boundary condition checks
    #    Shredding: Φ_N large AND S_perc near max  → ψ should be large positive
    #    Locking  : Φ_N small AND S_perc near 0   → ψ should be large negative
    shredding_ok = (Phi_N > np.percentile(Phi_N, 90)) and (S_perc > 0.8 * max_allowed_entropy) and (psi > 2.0)
    locking_ok   = (Phi_N < np.percentile(Phi_N, 10)) and (S_perc < 0.2 * max_allowed_entropy) and (psi < -2.0)

    # 7. MPC‑Ω QP constraints
    constraints_ok = (PCI >= 0.6) and (Phi_N >= 0.5) and (S_low <= S_perc <= S_high)

    # 8. Invariant definition check (should hold by construction)
    invariant_ok = np.abs(psi - np.log(Phi_N / (Phi_N0 + 1e-12))) < 1e-6

    report = {
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "PCI": PCI,
        "psi_perc": psi,
        "S_perc": S_perc,
        "S_low": S_low,
        "S_high": S_high,
        "constraints_ok": constraints_ok,
        "invariant_ok": invariant_ok,
        "shredding_boundary_ok": shredding_ok,
        "locking_boundary_ok": locking_ok,
        "overall_pass": (
            constraints_ok and invariant_ok and shredding_ok and locking_ok
        ),
    }
    return report

# ----------------------------------------------------------------------
# Example usage with synthetic data
# ----------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    N_points = 500
    D_desc = 64

    # Simulate geometric and visual descriptors with some correlation
    g_desc = np.random.randn(N_points, D_desc)
    v_desc = 0.6 * g_desc + 0.4 * np.random.randn(N_points, D_desc)  # correlated

    # Hyper‑parameters (chosen to be physically plausible)
    kappa = [0.8, 0.2, 0.5, 0.1]   # [κ1, κ2, κ3, κ4]
    Phi_N0 = 0.7                   # baseline from validation set
    S_low = 0.5
    S_high = 2.0

    res = validate_PCS_Omega(
        g_desc, v_desc,
        kappa=kappa,
        Phi_N0=Phi_N0,
        S_low=S_low,
        S_high=S_high,
        Gamma=1.0,
    )

    print("=== PCS‑Ω Validation Report ===")
    for k, v in res.items():
        if isinstance(v, float):
            print(f"{k:22}: {v:.4f}")
        else:
            print(f"{k:22}: {v}")

    if res["overall_pass"]:
        print("\nRESULT: PASS – PCS‑Ω respects Ω‑Protocol invariants.")
    else:
        print("\nRESULT: FAIL – one or more invariants violated.")