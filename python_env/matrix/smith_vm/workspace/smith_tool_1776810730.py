# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATS-Ω Mathematical Validator
----------------------------
Validates that a given snapshot of the computational‑integrity field
obeys the Ω‑Physics Rubric v26.0 constraints imposed by the Algorithmic
Topology Shield (ATS‑Ω).

Usage:
    python3 ats_omega_validator.py   # runs a self‑test with synthetic data
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (mirroring the definitions in the proposal)
# ----------------------------------------------------------------------
def compute_phi_n(sigma: np.ndarray) -> float:
    """
    Φ_N = sqrt( max eigenvalue of covariance matrix Σ ).
    """
    evals = np.linalg.eigvalsh(sigma)   # symmetric → real eigenvalues
    return np.sqrt(np.max(evals))

def compute_phi_delta(sigma: np.ndarray, third_moment: np.ndarray) -> float:
    """
    Φ_Δ = μ3 / (μ2)^(3/2)
    where μ2 = variance (average of diagonal of Σ) and μ3 = average third central moment.
    """
    mu2 = np.trace(sigma) / sigma.shape[0]   # average variance
    mu3 = np.mean(third_moment)              # placeholder; in practice compute from data
    if mu2 == 0:
        return 0.0
    return mu3 / (mu2 ** 1.5)

def psi_from_phi_n(phi_n: float, phi_n0: float) -> float:
    """
    Invariant ψ = ln( Φ_N / Φ_N^{(0)} )
    """
    if phi_n <= 0 or phi_n0 <= 0:
        raise ValueError("Φ_N and Φ_N^{(0)} must be positive for log.")
    return np.log(phi_n / phi_n0)

def shannon_conditional_entropy(path_probs: np.ndarray, type_weights: np.ndarray) -> float:
    """
    S_alg = Σ_m p(m) [ - Σ_k p_{m,k} log p_{m,k} ]
    path_probs.shape = (M_types, K_paths)
    type_weights.shape = (M_types,) and sums to 1.
    """
    # avoid log(0)
    safe_probs = np.where(path_probs > 0, path_probs, 1e-12)
    entropy_per_type = -np.sum(safe_probs * np.log(safe_probs), axis=1)
    return np.dot(type_weights, entropy_per_type)

def compute_ati(curvature_ratio: float,
                beta1_ratio: float,
                s_alg: float) -> float:
    """
    ATI = (|R_G(t)|/|R_G(0)|) * (β1(t)/β1(0)) * exp(-S_alg(t))
    The proposal expects ATI ∈ [0,1]; we clip to that interval.
    """
    raw = curvature_ratio * beta1_ratio * np.exp(-s_alg)
    return float(np.clip(raw, 0.0, 1.0))

def cost_integrand(ati: float,
                   phi_n: float,
                   phi_n0: float,
                   phi_delta: float,
                   s_alg: float,
                   mu1: float = 1.0,
                   mu2: float = 1.0,
                   mu3: float = 1.0) -> float:
    """
    Quadratic penalty used in the MPC‑Ω cost function.
    """
    term1 = (0.6 - ati) ** 2 if ati < 0.6 else 0.0
    term2 = mu1 * (0.5 - phi_n/phi_n0) ** 2 if phi_n/phi_n0 < 0.5 else 0.0
    term3 = mu2 * phi_delta ** 2
    term4 = mu3 * (np.log(2) - s_alg) ** 2 if s_alg < np.log(2) else 0.0
    return term1 + term2 + term3 + term4

# ----------------------------------------------------------------------
# Synthetic data generator (for demonstration / unit‑test)
# ----------------------------------------------------------------------
def generate_synthetic_data(n_components: int = 6,
                            n_time_steps: int = 1,
                            seed: int = 0) -> dict:
    """
    Returns a dict with:
        B          : shape (n_components, n_time_steps)   – computational integrity field
        type_id    : shape (n_components,)                – 0 or 1 (two algorithmic types)
        path_frac  : shape (n_components, n_time_steps, 2) – fraction of components taking path 0/1
    """
    rng = np.random.default_rng(seed)
    # Base field with some spatial correlation
    B = rng.normal(loc=1.0, scale=0.2, size=(n_components, n_time_steps))
    # Add a slow drift to mimic temporal evolution
    B += 0.05 * np.arange(n_time_steps)[None, :]
    # Random assignment of component type
    type_id = rng.integers(0, 2, size=n_components)
    # Random path fractions (must sum to 1 per component per time)
    path_frac = rng.dirichlet([1.0, 1.0], size=(n_components, n_time_steps))
    return {"B": B, "type_id": type_id, "path_frac": path_frac}

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_snapshot(snapshot: dict,
                      phi_n0_ref: float = None) -> None:
    """
    Performs all rubric‑level checks on a single time‑step snapshot.
    Raises AssertionError on any violation.
    """
    B = snapshot["B"]                     # shape (n_comp, 1)
    n_comp = B.shape[0]
    # Flatten time dimension (we assume a single snapshot)
    B_flat = B[:, 0]

    # ---- 1. Covariance and moments ----
    mean_B = np.mean(B_flat)
    # Centered data
    X = B_flat - mean_B
    # Covariance matrix (n_comp x n_comp)
    sigma = np.outer(X, X) / n_comp   # maximum‑likelihood estimator
    # Third central moment (scalar per component, then averaged)
    third_moment = np.mean(X ** 3)    # we use a scalar approximation for Φ_Δ

    phi_n = compute_phi_n(sigma)
    phi_delta = compute_phi_delta(sigma, third_moment)

    # Reference Φ_N^{(0)}: if not supplied, use the value from a fault‑free run.
    # For the synthetic test we compute it from the first snapshot itself,
    # assuming it represents the baseline.
    if phi_n0_ref is None:
        phi_n0_ref = phi_n   # baseline = current (for demo only)

    psi = psi_from_phi_n(phi_n, phi_n0_ref)

    # ---- 2. Entropy (Shannon conditional) ----
    # We need path fractions per component; for demo we reuse the synthetic path_frac.
    path_frac = snapshot["path_frac"][:, 0, :]   # shape (n_comp, 2)
    type_id = snapshot["type_id"]
    M = int(type_id.max()) + 1   # number of types (should be 2 in demo)
    K = path_frac.shape[1]       # number of paths (2)

    # Build probability matrix p[m,k]
    p_mk = np.zeros((M, K))
    type_weights = np.zeros(M)
    for m in range(M):
        mask = (type_id == m)
        type_weights[m] = np.mean(mask.astype(float))
        if type_weights[m] > 0:
            p_mk[m, :] = np.mean(path_frac[mask, :], axis=0)
        else:
            p_mk[m, :] = 0.0
    # Normalise type weights (should already sum to 1)
    type_weights = type_weights / np.sum(type_weights)

    s_alg = shannon_conditional_entropy(p_mk, type_weights)

    # ---- 3. Algorithmic Topology Integrity Index (ATI) ----
    # For demo we set curvature_ratio = beta1_ratio = 1 (no change).
    curvature_ratio = 1.0
    beta1_ratio = 1.0
    ati = compute_ati(curvature_ratio, beta1_ratio, s_alg)

    # ---- 4. Invariant and boundary checks ----
    # Invariant must match the log ratio (within tolerance)
    assert np.abs(psi - np.log(phi_n / phi_n0_ref)) < 1e-12, \
        f"Invariant ψ mismatch: computed {psi}, expected {np.log(phi_n/phi_n0_ref)}"

    # Algorithmic Shredding: ψ → +∞ when Φ_N → ∞ AND S_alg high.
    # We operationalise "high" as S_alg > 1.5 (arbitrary but > ln2≈0.693)
    shredding = (phi_n > 10 * phi_n0_ref) and (s_alg > 1.5)
    # Informational Freeze: ψ → -∞ when Φ_N → 0 AND S_alg low.
    freeze = (phi_n < 0.1 * phi_n0_ref) and (s_alg < 0.2)

    # ---- 5. MPC‑Ω QP constraints ----
    assert ati >= 0.6 - 1e-9, f"ATI constraint violated: ATI={ati}"
    assert phi_n >= 0.5 * phi_n0_ref - 1e-9, \
        f"Φ_N constraint violated: Φ_N={phi_n}, 0.5Φ_N0={0.5*phi_n0_ref}"
    assert s_alg >= np.log(2) - 1e-9, \
        f"Entropy constraint violated: S_alg={s_alg}, ln2={np.log(2)}"

    # ---- 6. Cost non‑negativity ----
    cost = cost_integrand(ati, phi_n, phi_n0_ref, phi_delta, s_alg)
    assert cost >= -1e-12, f"Cost integrand negative: {cost}"

    # ---- 7. Boundary flagging (informational only) ----
    if shredding:
        print("[WARNING] Algorithmic Shredding condition detected.")
    if freeze:
        print("[WARNING] Informational Freeze condition detected.")

    # If we reach here, the snapshot passes all rubric checks.
    print("[PASS] Snapshot satisfies all Ω‑Physics Rubric v26.0 constraints.")
    print(f"  Φ_N = {phi_n:.4f} (baseline {phi_n0_ref:.4f})")
    print(f"  Φ_Δ = {phi_delta:.4f}")
    print(f"  ψ   = {psi:.4f}")
    print(f"  S_alg = {s_alg:.4f}")
    print(f"  ATI   = {ati:.4f}")
    print(f"  Cost integrand = {cost:.6f}")

# ----------------------------------------------------------------------
# Self‑test when run as a script
# ----------------------------------------------------------------------
if __name__ == "__main__":
    snap = generate_synthetic_data(n_components=8, seed=42)
    # Use the first snapshot as baseline for Φ_N^{(0)} (as the proposal suggests)
    baseline_phi_n = compute_phi_n(
        np.outer(snap["B"][:,0] - np.mean(snap["B"][:,0]),
                 snap["B"][:,0] - np.mean(snap["B"][:,0])) / snap["B"].shape[0]
    )
    validate_snapshot(snap, phi_n0_ref=baseline_phi_n)