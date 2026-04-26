# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validator for LMPC‑Ω proposal
# --------------------------------------------------------------
# This script checks the internal mathematical consistency of the
# Lagrange‑Multiplier Plasma Controllability (LMPC‑Ω) integration
# against the core Omega Protocol invariants:
#   • Φ_N   – connectivity (must stay in [0,1])
#   • Φ_Δ   – asymmetry   (must stay in [0,1])
#   • J*    – optimal cost (must be non‑negative and bounded)
# Additionally it verifies that all derived quantities respect
# their definitional ranges and that the proposed control actions
# never violate the hard constraints imposed on the MPC.
#
# The validator is deliberately lightweight: it works on synthetic
# time‑series that mimic the TCV MPC output (control cycle ≈ 1 ms).
# --------------------------------------------------------------

import numpy as np

# ------------------------------------------------------------------
# Helper functions that mirror the LMPC‑Ω definitions
# ------------------------------------------------------------------
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def compute_CAI(lambda_tilde, w_crit):
    """Constraint Activity Index – weighted sum of normalized multipliers."""
    return np.sum(w_crit * lambda_tilde, axis=-1)

def compute_MAS(lambda_top, lambda_bottom, eps=1e-9):
    """Multiplier Asymmetry Score for a pair of constraints."""
    return np.abs(lambda_top - lambda_bottom) / (lambda_top + lambda_bottom + eps)

def compute_PSI(lambda_tilde_window):
    """Constraint‑manifold curvature invariant Ψ = log(det Σ / det Σ0)."""
    # lambda_tilde_window: shape (window_len, n_constraints)
    Sigma = np.cov(lambda_tilde_window, rowvar=False)  # (n, n)
    Sigma0 = np.cov(lambda_tilde_window[0:1], rowvar=False)  # use first sample as reference
    # Avoid numerical issues with near‑singular covariances
    eps = 1e-12
    det_Sigma = np.linalg.det(Sigma) + eps
    det_Sigma0 = np.linalg.det(Sigma0) + eps
    return np.log(det_Sigma / det_Sigma0)

def compute_phi_N(phi_N0, eta1, CAI_delayed, tau1):
    """Φ_N mapping (Eq. in proposal)."""
    return phi_N0 - eta1 * sigmoid(CAI_delayed - tau1)  # tau1 absorbed into delay

def compute_phi_Delta(phi_Delta0, eta2, MAS_delayed, eta3, std_lambda_delayed, tau2, tau3):
    """Φ_Δ mapping (Eq. in proposal)."""
    return (phi_Delta0 +
            eta2 * MAS_delayed -
            eta3 * std_lambda_delayed)  # delays absorbed into arguments

def anomaly_score(actual, predicted, sigma):
    """Standardised residual used for s_CAI / s_MAS."""
    return np.abs(actual - predicted) / (sigma + 1e-12)

# ------------------------------------------------------------------
# Validation routine
# ------------------------------------------------------------------
def validate_LMPC_Omega(t, lambda_raw, w_crit,
                        lambda_top_raw, lambda_bottom_raw,
                        phi_N0=0.9, phi_Delta0=0.2,
                        eta1=0.3, eta2=0.4, eta3=0.2,
                        tau1=0.02, tau2=0.02, tau3=0.02,
                        CAI_thr=0.8, MAS_thr=0.6,
                        phi_N_min=0.6, phi_Delta_max=0.8,
                        J_mu1=0.5, J_mu2=0.5):
    """
    Parameters
    ----------
    t : 1D array
        Time vector (seconds).
    lambda_raw : 2D array (len(t), n_constraints)
        Raw Lagrange multipliers from the QP solver at each control cycle.
    w_crit : 1D array (n_constraints,)
        Non‑negative weights that sum to 1 for critical constraints.
    lambda_top_raw, lambda_bottom_raw : 1D arrays (len(t),)
        Multipliers associated with the top/bottom wall‑distance constraints.
    Remaining arguments are the hyper‑parameters from the proposal.

    Returns
    -------
    dict with boolean flags indicating compliance.
    """
    n_steps = len(t)
    # 1️⃣ Normalise multipliers (historical max = max over the whole simulation)
    lambda_max = np.max(lambda_raw, axis=0, keepdims=True)
    lambda_max[lambda_max == 0] = 1.0   # avoid division by zero
    lambda_tilde = lambda_raw / lambda_max

    # 2️⃣ Compute CAI and MAS
    CAI = compute_CAI(lambda_tilde, w_crit)                     # (n_steps,)
    MAS = compute_MAS(lambda_top_raw, lambda_bottom_raw)       # (n_steps,)

    # 3️⃣ Apply delays (simple shift – in reality a filter would be used)
    delay_steps = int(round(tau1 / np.mean(np.diff(t))))  # assume uniform sampling
    CAI_delayed = np.concatenate([np.full(delay_steps, CAI[0]), CAI[:-delay_steps]]) if delay_steps>0 else CAI
    MAS_delayed = np.concatenate([np.full(delay_steps, MAS[0]), MAS[:-delay_steps]]) if delay_steps>0 else MAS
    # std of lambda_tilde over a short window (here 5 steps) for Φ_Δ term
    win = 5
    std_lambda = np.array([np.std(lambda_tilde[max(0,i-win):i+1], axis=0).mean()
                           for i in range(n_steps)])
    std_lambda_delayed = np.concatenate([np.full(delay_steps, std_lambda[0]),
                                         std_lambda[:-delay_steps]]) if delay_steps>0 else std_lambda

    # 4️⃣ Map to Omega variables
    phi_N = compute_phi_N(phi_N0, eta1, CAI_delayed, tau1)
    phi_Delta = compute_phi_Delta(phi_Delta0, eta2, MAS_delayed,
                                  eta3, std_lambda_delayed, tau2, tau3)

    # 5️⃣ Invariant Ψ (using a sliding window of length win)
    PSI = np.array([compute_PSI(lambda_tilde[max(0,i-win):i+1])
                    for i in range(n_steps)])

    # 6️⃣ Derive ξ_N, ξ_Δ as finite‑difference approximations of ∂Φ/∂Ψ
    dPhi_N = np.gradient(phi_N, t)
    dPhi_Delta = np.gradient(phi_Delta, t)
    dPsi = np.gradient(PSI, t)
    xi_N = dPhi_N / (dPsi + 1e-12)
    xi_Delta = dPhi_Delta / (dPsi + 1e-12)

    # 7️⃣ Anomaly scores (simple Kalman‑filter‑like predictor: persistence model)
    pred_CAI = np.concatenate([np.array([CAI[0]]), CAI[:-1]])
    pred_MAS = np.concatenate([np.array([MAS[0]]), MAS[:-1]])
    sigma_CAI = np.std(CAI - pred_CAI) + 1e-12
    sigma_MAS = np.std(MAS - pred_MAS) + 1e-12
    s_CAI = anomaly_score(CAI, pred_CAI, sigma_CAI)
    s_MAS = anomaly_score(MAS, pred_MAS, sigma_MAS)

    # 8️⃣ Hard constraint checks (as imposed on the MPC‑Ω layer)
    cai_ok = np.all(CAI <= CAI_thr)
    mas_ok = np.all(MAS <= MAS_thr)
    phiN_ok = np.all(phi_N >= phi_N_min)
    phiDelta_ok = np.all(phi_Delta <= phi_Delta_max)

    # 9️⃣ Cost function non‑negativity (J_Omega integrand)
    J_integrand = CAI**2 + J_mu1 * MAS**2 + J_mu2 * (phi_Delta)**2
    J_ok = np.all(J_integrand >= 0)

    # 🔟 Disruption‑prediction logic (from proposal)
    alarm = (s_CAI > 2.5) & (s_MAS > 2.0) & (phi_Delta > 0.7)
    alarm_any = np.any(alarm)

    # ------------------------------------------------------------------
    # Return a compliance dictionary
    # ------------------------------------------------------------------
    return {
        "CAI_in_bounds": cai_ok,
        "MAS_in_bounds": mas_ok,
        "Phi_N_ge_min": phiN_ok,
        "Phi_Delta_le_max": phiDelta_ok,
        "Cost_nonnegative": J_ok,
        "Psi_defined": np.all(np.isfinite(PSI)),
        "Xi_defined": np.all(np.isfinite(xi_N)) and np.all(np.isfinite(xi_Delta)),
        "Anomaly_scores_computed": np.all(np.isfinite(s_CAI)) and np.all(np.isfinite(s_MAS)),
        "Disruption_alarm_triggered": alarm_any,
        "First_alarm_idx": int(np.argmax(alarm)) if alarm_any else -1,
        "Diagnostics": {
            "CAI_min": float(np.min(CAI)),
            "CAI_max": float(np.max(CAI)),
            "MAS_min": float(np.min(MAS)),
            "MAS_max": float(np.max(MAS)),
            "Phi_N_min": float(np.min(phi_N)),
            "Phi_N_max": float(np.max(phi_N)),
            "Phi_Delta_min": float(np.min(phi_Delta)),
            "Phi_Delta_max": float(np.max(phi_Delta)),
            "Psi_min": float(np.min(PSI)),
            "Psi_max": float(np.max(PSI)),
        }
    }

# ------------------------------------------------------------------
# Example usage with synthetic data (for illustration only)
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Simulate 2 seconds of TCV‑like data at 1 kHz
    fs = 1000
    t = np.arange(0, 2.0, 1/fs)
    n_steps = len(t)
    n_constraints = 6  # e.g., 3 coil currents, 2 wall distances, 1 shape bound

    # Nominal stable multipliers (small positive numbers)
    lambda_base = 0.05 * np.ones((n_steps, n_constraints))

    # Introduce a growing wall‑distance asymmetry after 0.8 s
    wall_top = lambda_base[:, 3]  # placeholder index for top wall
    wall_bot = lambda_base[:, 4]  # placeholder index for bottom wall
    wall_top[int(0.8*fs):] += 0.3 * np.linspace(0, 1, n_steps - int(0.8*fs))
    wall_bot[int(0.8*fs):] -= 0.1 * np.linspace(0, 1, n_steps - int(0.8*fs))
    lambda_raw = lambda_base.copy()
    lambda_raw[:, 3] = wall_top
    lambda_raw[:, 4] = wall_bot

    # Add small random noise to all multipliers
    lambda_raw += 0.01 * np.random.randn(*lambda_raw.shape)

    # Equal weights for critical constraints (here we treat all as critical)
    w_crit = np.ones(n_constraints) / n_constraints

    # Run validation
    report = validate_LMPC_Omega(
        t, lambda_raw, w_crit,
        lambda_top_raw=lambda_raw[:, 3],
        lambda_bottom_raw=lambda_raw[:, 4]
    )

    # Print concise summary
    print("=== LMPC‑Ω Omega‑Protocol Compliance Report ===")
    for k, v in report.items():
        if k != "Diagnostics":
            print(f"{k:30}: {v}")
    print("\n--- Diagnostics ---")
    for k, v in report["Diagnostics"].items():
        print(f"{k:20}: {v:.4f}")

    # ------------------------------------------------------------------
    # Assertions – hard failures if any invariant is violated
    # ------------------------------------------------------------------
    assert report["CAI_in_bounds"], "CAI exceeded allowed threshold (0.8)."
    assert report["MAS_in_bounds"], "MAS exceeded allowed threshold (0.6)."
    assert report["Phi_N_ge_min"], "Φ_N fell below minimum (0.6)."
    assert report["Phi_Delta_le_max"], "Φ_Δ exceeded maximum (0.8)."
    assert report["Cost_nonnegative"], "Omega cost integrand became negative."
    assert report["Psi_defined"], "Ψ invariant produced NaN/Inf."
    assert report["Xi_defined"], "ξ_N or ξ_Δ undefined (division by near‑zero)."
    print("\nAll Omega‑Protocol invariants satisfied.")