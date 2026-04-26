# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
LMPC‑Ω Invariant Validator
--------------------------
Checks that a candidate LMPC‑Ω implementation respects the Omega Protocol
invariants (Φ_N, Φ_Δ, Ψ) and the associated constraints.
"""

import numpy as np

def validate_lmpc_omega(
    lambdas_raw: np.ndarray,
    lambda_max: np.ndarray,
    weights: np.ndarray,
    eta1: float = 0.5,
    eta2: float = 0.3,
    eta3: float = 0.2,
    phiN0: float = 0.9,
    phiD0: float = 0.1,
    tau: float = 0.0,          # lead‑time (seconds) – only needed for causality comment
    cai_limit: float = 0.8,
    mas_limit: float = 0.6,
    phiN_min: float = 0.6,
    phiD_max: float = 0.8,
    sigmoid_scale: float = 1.0,
) -> dict:
    """
    Parameters
    ----------
    lambdas_raw : shape (n_constraints, n_samples)
        Raw Lagrange multiplier values extracted at each control step.
    lambda_max : shape (n_constraints,)
        Historical maximum for each constraint (used for normalization).
    weights : shape (n_constraints,)
        Non‑negative weights summing to 1 for CAI calculation.
    eta1, eta2, eta3 : float > 0
        Mapping gains.
    phiN0, phiD0 : float in [0,1]
        Baseline Omega‑Protocol variables.
    tau : float
        Lead‑time (must be >=0 for causal mapping).
    cai_limit, mas_limit : float
        Hard bounds enforced by the MPC‑Ω layer.
    phiN_min, phiD_max : float
        Allowed ranges for the Omega invariants.
    sigmoid_scale : float
        Controls steepness of sigmoid (default 1).

    Returns
    -------
    dict with computed quantities if all checks pass.
    """

    # ---------- 1. Basic shape checks ----------
    assert lambdas_raw.ndim == 2, "lambdas_raw must be 2D (constraints × time)"
    n_con, n_t = lambdas_raw.shape
    assert lambda_max.shape == (n_con,), "lambda_max must match number of constraints"
    assert weights.shape == (n_con,), "weights must match number of constraints"
    assert np.all(weights >= 0), "weights must be non‑negative"
    assert np.isclose(weights.sum(), 1.0), "weights must sum to 1"
    assert eta1 > 0 and eta2 > 0 and eta3 > 0, "mapping gains must be positive"
    assert tau >= 0.0, "lead‑time τ must be non‑negative (causality)"
    assert 0 <= phiN0 <= 1 and 0 <= phiD0 <= 1, "baseline Omega vars must be in [0,1]"
    assert 0 < cai_limit <= 1 and 0 < mas_limit <= 1, "limits must lie in (0,1]"
    assert 0 <= phiN_min <= 1 and 0 <= phiD_max <= 1, "invariant bounds must be in [0,1]"
    assert phiN_min < phiN0, "phiN_min must be below baseline to allow decrease"
    assert phiD_max > phiD0, "phiD_max must be above baseline to allow increase"

    # ---------- 2. Normalization ----------
    lambdas_norm = lambdas_raw / lambda_max[:, None]          # shape (n_con, n_t)
    # Clip to [0,1] to guard against occasional overshoot due to noise
    lambdas_norm = np.clip(lambdas_norm, 0.0, 1.0)

    # ---------- 3. Constraint Activity Index (CAI) ----------
    cai = np.tensordot(weights, lambdas_norm, axes=([0], [0]))  # shape (n_t,)
    assert np.all((0.0 <= cai) & (cai <= 1.0)), "CAI out of [0,1] range"
    assert np.all(cai <= cai_limit), f"CAI exceeds MPC‑Ω limit ({cai_limit})"

    # ---------- 4. Multiplier Asymmetry Score (MAS) ----------
    # Example: assume first two constraints are top/bottom wall‑distance multipliers.
    # In practice the user should supply indices; here we just illustrate.
    if n_con >= 2:
        mas = np.abs(lambdas_norm[0] - lambdas_norm[1]) / (
            lambdas_norm[0] + lambdas_norm[1] + 1e-12
        )
    else:
        mas = np.zeros(n_t)  # degenerate case
    assert np.all((0.0 <= mas) & (mas <= 1.0)), "MAS out of [0,1] range"
    assert np.all(mas <= mas_limit), f"MAS exceeds MPC‑Ω limit ({mas_limit})"

    # ---------- 5. Covariance & Psi invariant ----------
    # Use a sliding window; here we use the whole sample for simplicity.
    # In real‑time implementation a fixed‑length window (e.g., 50 ms) is used.
    cov = np.cov(lambdas_norm)  # shape (n_con, n_con)
    # Covariance must be symmetric positive‑semidefinite; we require PD for log‑det.
    eigvals = np.linalg.eigvalsh(cov)
    assert np.all(eigvals > 0), "Covariance matrix is not positive‑definite"
    det_cov = np.linalg.det(cov)
    # Reference covariance from a quiescent baseline (could be pre‑computed)
    cov0 = np.cov(lambdas_norm[:, : max(1, n_t // 10)])  # first 10% as baseline
    det_cov0 = np.linalg.det(cov0)
    psi = np.log(det_cov / det_cov0)  # scalar
    # No explicit bound on psi, but we can note that a sharp negative drop signals loss of DOF.

    # ---------- 6. Mapping to Omega variables ----------
    # Sigmoid: 1 / (1 + exp(-scale * x))
    def sigmoid(x):
        return 1.0 / (1.0 + np.exp(-sigmoid_scale * x))

    phiN = phiN0 - eta1 * sigmoid(cai)          # shape (n_t,)
    phiD = phiD0 + eta2 * mas + eta3 * np.std(lambdas_norm, axis=0, ddof=1)  # shape (n_t,)

    # Enforce Omega‑Protocol ranges
    assert np.all((phiN_min <= phiN) & (phiN <= 1.0)), f"Phi_N out of allowed [{phiN_min},1]"
    assert np.all((0.0 <= phiD) & (phiD <= phiD_max)), f"Phi_D out of allowed [0,{phiD_max}]"

    # ---------- 7. Anomaly detection (diagnostic only) ----------
    # Simple Kalman‑like predictor: use exponential moving average as placeholder.
    alpha = 0.1
    cai_hat = np.zeros_like(cai)
    mas_hat = np.zeros_like(mas)
    cai_hat[0] = cai[0]
    mas_hat[0] = mas[0]
    for i in range(1, n_t):
        cai_hat[i] = alpha * cai[i] + (1 - alpha) * cai_hat[i-1]
        mas_hat[i] = alpha * mas[i] + (1 - alpha) * mas_hat[i-1]
    sigma_cai = np.std(cai - cai_hat) + 1e-12
    sigma_mas = np.std(mas - mas_hat) + 1e-12
    s_cai = np.abs(cai - cai_hat) / sigma_cai
    s_mas = np.abs(mas - mas_hat) / sigma_mas

    # Anomaly rule (does NOT affect invariants; just a flag)
    anomaly = (s_cai > 2.5) & (s_mas > 2.0) & (phiD > 0.7)

    # ---------- 8. Return diagnostics ----------
    return {
        "lambdas_norm": lambdas_norm,
        "CAI": cai,
        "MAS": mas,
        "Psi": psi,
        "Phi_N": phiN,
        "Phi_D": phiD,
        "anomaly_flag": anomaly.any(),
        "anomaly_indices": np.where(anomaly)[0],
    }


# ----------------------------------------------------------------------
# Example usage (random data) – will raise AssertionError if any invariant broken.
if __name__ == "__main__":
    np.random.seed(42)
    n_con = 6          # e.g., 3 coil currents + 2 wall distances + 1 shape bound
    n_t   = 500        # 500 control steps (~0.5 s at 1 kHz)
    lambdas_raw = np.abs(np.random.randn(n_con, n_t)) * 0.5  # keep small for demo
    lambda_max = np.max(lambdas_raw, axis=1) * 1.2          # give some headroom
    weights = np.array([0.2, 0.2, 0.15, 0.15, 0.15, 0.15])   # sums to 1

    result = validate_lmpc_omega(
        lambdas_raw=lambdas_raw,
        lambda_max=lambda_max,
        weights=weights,
        eta1=0.4,
        eta2=0.3,
        eta3=0.2,
        phiN0=0.85,
        phiD0=0.15,
        tau=0.02,          # 20 ms lead‑time (causal)
        cai_limit=0.8,
        mas_limit=0.6,
        phiN_min=0.6,
        phiD_max=0.8,
    )

    print("Validation PASSED")
    print(f"  Final CAI  : {result['CAI'][-1]:.3f}")
    print(f"  Final MAS  : {result['MAS'][-1]:.3f}")
    print(f"  Final Ψ    : {result['Psi']:.3f}")
    print(f"  Final Φ_N  : {result['Phi_N'][-1]:.3f}")
    print(f"  Final Φ_D  : {result['Phi_D'][-1]:.3f}")
    print(f"  Anomaly detected? {result['anomaly_flag']}")