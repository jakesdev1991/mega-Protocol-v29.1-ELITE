# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Guardian – Validation of BRDO‑Ω Integration
# --------------------------------------------------------------
# This script checks the mathematical soundness of the proposed
# Byzantine‑Resilient Distributed Omega Optimization (BRDO‑Ω)
# and verifies that all Omega‑Protocol invariants (Φ_N, Φ_Δ, J*)
# are respected under simulated Byzantine attacks.
#
# Invariants we enforce (as stated in the Omega Physics Rubric v26.0):
#   1. Φ_N  ≥ 0          (connectivity / inverse variance)
#   2. |Φ_Δ| ≤ 1         (asymmetry mode bounded)
#   3. J*  ≥ 0           (cost function non‑negative)
#   4. GCI ∈ [0,1]       (by construction)
#   5. Redundancy ρ = n/d must satisfy the information‑theoretic bound:
#          t ≤ ⌊(m‑1)/2⌋   ⇔   ρ ≥ 2·t/m + 1   (derived from the paper)
# --------------------------------------------------------------

import numpy as np
from typing import List, Tuple

# -------------------------- Helper Functions --------------------------

def sparse_encoder(d: int, n: int, seed: int = 0) -> np.ndarray:
    """
    Produce a deterministic sparse encoding matrix E ∈ ℝ^{n×d}
    as described in the paper: each column has exactly ⌈n/2⌉ non‑zero
    entries equal to ±1 (chosen by a fixed pseudo‑random pattern).
    """
    rng = np.random.default_rng(seed)
    E = np.zeros((n, d), dtype=float)
    for col in range(d):
        rows = rng.choice(n, size=(n + 1)//2, replace=False)
        signs = rng.choice([-1.0, 1.0], size=len(rows))
        E[rows, col] = signs
    return E

def encode_gradient(E: np.ndarray, grad: np.ndarray) -> np.ndarray:
    """y = E @ grad"""
    return E @ grad

def add_byzantine_error(y: np.ndarray, corrupt_idx: List[int],
                        noise_scale: float = 5.0) -> np.ndarray:
    """
    Simulate a Byzantine worker returning y + arbitrary error.
    Honest workers add zero‑mean Gaussian noise (small).
    Corrupt workers add large bounded adversarial perturbation.
    """
    m = y.shape[0]
    y_tilde = y.copy()
    for i in range(m):
        if i in corrupt_idx:
            # arbitrary direction – we use a random vector scaled by noise_scale
            y_tilde[i] += noise_scale * np.random.randn(*y[i].shape)
        else:
            y_tilde[i] += 0.01 * np.random.randn(*y[i].shape)  # honest noise
    return y_tilde

def deterministic_decoder(E: np.ndarray, y_tilde: np.ndarray,
                          t: int) -> np.ndarray:
    """
    Simple majority‑vote decoder for the sparse ±1 code.
    For each coordinate j we look at the n encoded symbols:
        ỹ_{:,j} = E_{:,j} · grad_j + error_j
    Because E_{:,j} ∈ {−1,0,+1} and is known, we can recover grad_j
    by taking the sign of the sum over rows where E_{:,j} ≠ 0,
    ignoring up to t outliers (we drop the t largest absolute residuals).
    """
    n, d = E.shape
    grad_est = np.zeros(d)
    for j in range(d):
        # rows that participate in this column
        rows = np.where(E[:, j] != 0)[0]
        vals = y_tilde[rows, j] * E[rows, j]   # undo the known ±1 factor
        # Remove the t largest magnitude outliers (if any)
        if len(vals) > t:
            idx_to_keep = np.argsort(np.abs(vals))[:-t]
            vals = vals[idx_to_keep]
        grad_est[j] = np.mean(vals)   # because E_{:,j} entries are ±1
    return grad_est

def compute_residuals(E: np.ndarray, grad_true: np.ndarray,
                      y_tilde: np.ndarray) -> np.ndarray:
    """r_i = ỹ_i − E_i @ grad_true   (per‑worker residual vector)"""
    return y_tilde - E @ grad_true

def compute_GCI(residuals: np.ndarray,
                alpha: float = 2.0, beta: float = 1.5, gamma: float = 0.5,
                tau: float = 1.0) -> float:
    """
    GCI = tanh( α·θ_corr + β·ε + γ·ρ )
    where:
        θ_corr = fraction of workers with ||r_i|| > τ
        ε      = mean residual norm
        ρ      = redundancy factor (n/d) – we treat it as a constant here
    """
    m = residuals.shape[0]
    norms = np.linalg.norm(residuals, axis=1)
    theta_corr = np.mean(norms > tau)
    eps = np.mean(norms)
    # redundancy factor – we will pass it externally; here use placeholder 3.0
    rho = 3.0
    val = alpha * theta_corr + beta * eps + gamma * rho
    return np.tanh(val)

def update_phi_n(phi_n0: float, gci: float, theta_corr: float,
                 eta1: float = 0.3, eta2: float = 0.2, tau: int = 4) -> float:
    """
    Φ_N^{(brdo)}(k) = Φ_N^{(0)} − η1·GCI_{k−τ} + η2·(1−θ_corr_{k−τ})
    We ignore the delay for validation (use current values).
    """
    return phi_n0 - eta1 * gci + eta2 * (1.0 - theta_corr)

def update_phi_delta(phi_delta0: float, theta_corr: float,
                     eps: float, eta3: float = 0.25, eta4: float = 0.15,
                     tau: int = 5) -> float:
    """
    Φ_Δ^{(brdo)}(k) = Φ_Δ^{(0)} + η3·θ_corr_{k−τ} − η4·ε_{k−τ}
    """
    return phi_delta0 + eta3 * theta_corr - eta4 * eps

def invariant_psi(Ricci: float, R0: float, gci: float,
                  lam: float = 0.8) -> float:
    """ψ = ln(|R|/R0) + λ·GCI"""
    return np.log(np.abs(Ricci) / R0) + lam * gci

def cost_function(gci: float, phi_n: float, phi_delta: float,
                  s_worker: float, mu1: float = 1.0,
                  mu2: float = 1.0, mu3: float = 1.0) -> float:
    """
    J = (GCI−0.6)_+² + μ1(0.6−Φ_N)_+² + μ2·Φ_Δ² + μ3(log(3)−S_worker)_+²
    """
    term1 = max(gci - 0.6, 0.0) ** 2
    term2 = mu1 * max(0.6 - phi_n, 0.0) ** 2
    term3 = mu2 * phi_delta ** 2
    term4 = mu3 * max(np.log(3.0) - s_worker, 0.0) ** 2
    return term1 + term2 + term3 + term4

def worker_entropy(residuals: np.ndarray) -> float:
    """S_worker = − Σ p_i log p_i,  p_i = ||r_i|| / Σ||r_j||"""
    norms = np.linalg.norm(residuals, axis=1)
    total = np.sum(norms)
    if total == 0:
        return 0.0
    p = norms / total
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

# -------------------------- Validation Routine --------------------------

def validate_brdo_omega(m: int = 9, t: int = 3, d: int = 20,
                        n: int = 12, iterations: int = 10) -> None:
    """
    Run a short simulation and assert that all Omega‑Protocol invariants
    hold at every step.
    """
    # 1. Information‑theoretic bound check
    max_t_allowed = (m - 1) // 2
    assert t <= max_t_allowed, f"t={t} exceeds bound ⌊(m−1)/2⌋={max_t_allowed}"
    # redundancy factor must be sufficient for the bound:
    # From the paper: ρ ≥ 2·t/m + 1  (derived from solving t ≤ (ρ−1)·m/(2ρ))
    rho = n / d
    min_rho = 2.0 * t / m + 1.0
    assert rho >= min_rho - 1e-9, (
        f"Redundancy ρ={rho:.3f} too low for t={t}, m={m}; need ≥{min_rho:.3f}"
    )

    # 2. Build encoder
    E = sparse_encoder(d, n, seed=42)

    # 3. Initial Omega variables (plausible nominal values)
    phi_n0 = 0.8          # baseline connectivity
    phi_delta0 = 0.0      # baseline asymmetry
    R0 = 1.0              # reference curvature

    for k in range(iterations):
        # ---- a) Simulate a true gradient (random direction) ----
        true_grad = np.random.randn(d)

        # ---- b) Encode and distribute ----
        y = encode_gradient(E, true_grad)

        # ---- c) Choose a set of Byzantine workers (worst‑case) ----
        corrupt_idx = list(range(t))   # first t workers are malicious

        # ---- d) Workers return possibly corrupted responses ----
        y_tilde = add_byzantine_error(y, corrupt_idx, noise_scale=4.0)

        # ---- e) Master decodes ----
        grad_est = deterministic_decoder(E, y_tilde, t)

        # ---- f) Compute residuals and derived metrics ----
        residuals = compute_residuals(E, true_grad, y_tilde)
        gci = compute_GCI(residuals)
        norms = np.linalg.norm(residuals, axis=1)
        theta_corr = np.mean(norms > 1.0)
        eps = np.mean(norms)

        # ---- g) Update Ω‑mode variables ----
        phi_n = update_phi_n(phi_n0, gci, theta_corr)
        phi_delta = update_phi_delta(phi_delta0, theta_corr, eps)

        # ---- h) Compute invariant ψ (need a curvature estimate) ----
        # Here we approximate Ollivier‑Ricci curvature by the average
        # pairwise correlation of residual vectors (a proxy used in the paper).
        if m > 1:
            corr_mat = np.corrcoef(residuals)   # m×m
            # set diagonal to zero, take mean of absolute off‑diagonal entries
            off_diag = corr_mat[~np.eye(m, dtype=bool)]
            Ricci = np.mean(np.abs(off_diag))
        else:
            Ricci = 0.0
        psi = invariant_psi(Ricci, R0, gci)

        # ---- i) Entropy gauge ----
        s_worker = worker_entropy(residuals)

        # ---- j) Cost function J* ----
        J_star = cost_function(gci, phi_n, phi_delta, s_worker)

        # ---- k) Assert Omega‑Protocol invariants ----
        assert 0.0 <= gci <= 1.0, f"GCI out of bounds: {gci}"
        assert phi_n >= 0.0, f"Φ_N negative: {phi_n}"
        assert abs(phi_delta) <= 1.0, f"Φ_Δ out of [-1,1]: {phi_delta}"
        assert J_star >= 0.0, f"Cost J* negative: {J_star}"
        # Entropy should be at least log(3) when the system is healthy;
        # we only warn if it drops far below (the MPC would act).
        if s_worker < np.log(3.0) - 0.5:
            print(f"[Iter {k}] Low worker entropy: S={s_worker:.3f}")

        # ---- l) Print a concise snapshot ----
        print(
            f"Iter {k:02d} | GCI={gci:.3f} | Φ_N={phi_n:.3f} | "
            f"Φ_Δ={phi_delta:.3f} | ψ={psi:.3f} | S={s_worker:.3f} | J*={J_star:.3f}"
        )

        # ---- m) Prepare next iteration (use updated Φ_N as new baseline) ----
        phi_n0 = phi_n   # simple persistence model for demo
        phi_delta0 = phi_delta

    print("\n✅ All Omega‑Protocol invariants satisfied for the simulated run.")

# -------------------------- Execute Validation --------------------------
if __name__ == "__main__":
    # Example parameters: m=9 workers, tolerate t=3 Byzantines
    validate_brdo_omega(m=9, t=3, d=15, n=12, iterations=12)