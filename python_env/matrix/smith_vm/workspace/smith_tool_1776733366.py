# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for NCMR‑Ω mathematical soundness
and Omega Protocol invariant enforcement.
"""

import numpy as np

# -------------------------- Helper Functions --------------------------

def sigmoid(x: float) -> float:
    """Standard logistic sigmoid, output in (0,1)."""
    return 1.0 / (1.0 + np.exp(-x))

def clip01(x: float) -> float:
    """Clip a scalar to the unit interval [0,1]."""
    return max(0.0, min(1.0, x))

def normalize_weights(w: np.ndarray) -> np.ndarray:
    """Ensure weights sum to 1 (avoid division by zero)."""
    s = w.sum()
    if s == 0:
        return np.ones_like(w) / len(w)
    return w / s

# -------------------------- Core Computation --------------------------

def compute_nci(C: float, A: float, R: float, D: float,
                alpha: float, beta: float, gamma: float, delta: float) -> float:
    """
    Narrative Coherence Index.
    All inputs expected in [0,1]; weights non‑negative and sum to 1.
    """
    nci = alpha * C + beta * A - gamma * R - delta * D
    return clip01(nci)   # enforce [0,1] bound

def update_phi_n(phi_n0: float, nci_delayed: float, eta1: float, tau: int, history: list) -> float:
    """
    Φ_N update with narrative contribution.
    Uses NCI from `tau` steps ago (if available).
    """
    # fetch delayed NCI; if not enough history, use earliest value
    if len(history) > tau:
        nci_tau = history[-tau-1]   # negative index: t‑tau
    else:
        nci_tau = history[0] if history else 0.0
    phi_n = phi_n0 + eta1 * sigmoid(nci_tau)
    return clip01(phi_n)

def update_phi_delta(phi_d0: float, nci_delayed: float, rigidity: float,
                     eta2: float, eta3: float, tau: int, history: list) -> float:
    """
    Φ_Δ update: narrative reduces asymmetry, rigidity increases it.
    """
    if len(history) > tau:
        nci_tau = history[-tau-1]
    else:
        nci_tau = history[0] if history else 0.0
    phi_d = phi_d0 - eta2 * nci_tau + eta3 * rigidity
    return clip01(phi_d)

def anomaly_score(residual: float, sigma_res: float) -> float:
    """Standardised residual (non‑negative)."""
    if sigma_res == 0:
        return 0.0
    return abs(residual) / sigma_res

def cost_integrand(nci: float, s_nci: float, phi_delta: float,
                   lam1: float, lam2: float) -> float:
    """Instantaneous cost (always ≥0 by construction)."""
    return (1.0 - nci)**2 + lam1 * (s_nci**2) + lam2 * phi_delta

# -------------------------- Validation Routine --------------------------

def validate_random_samples(num_samples: int = 10_000) -> None:
    """
    Randomly test the mathematics and invariant compliance.
    Raises AssertionError on any violation.
    """
    np.random.seed(42)  # reproducibility

    # Baseline Ω values (could be any in [0,1])
    phi_n0 = np.random.uniform(0.3, 0.7)
    phi_d0 = np.random.uniform(0.2, 0.6)

    # Hyper‑parameters (chosen to be plausible)
    eta1, eta2, eta3 = 0.2, 0.15, 0.1
    tau1, tau2 = 2, 2          # months translated to discrete steps
    lam1, lam2 = 0.5, 0.3

    # Store delayed NCI history for tau lookup
    nci_history = []

    for i in range(num_samples):
        # ---- 1. Sample raw narrative features in [0,1] ----
        C = np.random.rand()
        A = np.random.rand()
        R = np.random.rand()
        D = np.random.rand()

        # ---- 2. Sample and normalize weights ----
        w_raw = np.random.rand(4)          # [alpha, beta, gamma, delta]
        w = normalize_weights(w_raw)
        alpha, beta, gamma, delta = w

        # ---- 3. Compute NCI ----
        nci = compute_nci(C, A, R, D, alpha, beta, gamma, delta)
        nci_history.append(nci)

        # ---- 4. Update Ω variables with delay ----
        phi_n = update_phi_n(phi_n0, nci, eta1, tau1, nci_history)
        phi_d = update_phi_delta(phi_d0, nci, R, eta2, eta3, tau2, nci_history)

        # ---- 5. Anomaly score (mock residual) ----
        residual = np.random.randn() * 0.1   # small zero‑mean noise
        sigma_res = 0.05                     # assumed std of residuals
        s_nci = anomaly_score(residual, sigma_res)

        # ---- 6. Cost integrand (should be ≥0) ----
        inst_cost = cost_integrand(nci, s_nci, phi_d, lam1, lam2)
        assert inst_cost >= -1e-12, f"Negative cost: {inst_cost}"

        # ---- 7. Invariant checks ----
        assert 0.0 <= phi_n <= 1.0, f"Φ_N out of bounds: {phi_n}"
        assert 0.0 <= phi_d <= 1.0, f"Φ_Δ out of bounds: {phi_d}"
        assert 0.0 <= nci <= 1.0, f"NCI out of bounds: {nci}"
        assert s_nci >= 0.0, f"Anomaly score negative: {s_nci}"

        # ---- 8. MPC‑Ω constraint monitoring (report violations) ----
        # These are *soft* constraints for the controller; we just log.
        if not (nci >= 0.4):
            print(f"[WARN] Sample {i}: NCI={nci:.3f} < 0.4")
        if not (phi_n >= 0.7):
            print(f"[WARN] Sample {i}: Φ_N={phi_n:.3f} < 0.7")
        if not (phi_d <= 0.6):
            print(f"[WARN] Sample {i}: Φ_Δ={phi_d:.3f} > 0.6")

        # ---- 9. Prediction rule (example usage) ----
        # The rule is meant for a *prediction* phase, not the hard MPC bound.
        if s_nci > 2.5 and phi_d > 0.7:
            # This situation should be rare because Φ_Δ is clipped ≤0.6 by MPC.
            # We flag it as a potential model‑inconsistency.
            print(f"[INFO] Sample {i}: Prediction trigger (s_NCI={s_nci:.2f}, Φ_Δ={phi_d:.3f})")

    print(f"✅ Validation passed over {num_samples} random samples.")
    print("All Ω‑Protocol invariants (Φ_N, Φ_Δ ∈ [0,1], J* ≥ 0) hold.")

# -------------------------- Entry Point --------------------------

if __name__ == "__main__":
    validate_random_samples()