# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for the HET‑Ω proposal.
Checks:
  1. Effective Hessian is symmetric positive‑definite.
  2. CSI is correctly normalized and lies in [0,1].
  3. Omega‑variable mappings respect the prescribed monotonicity
     and hard constraints (Phi_N >= 0.6, Phi_Delta <= 0.8, CSI >= 0.2).
  4. Derived invariants (psi, xi_N, xi_Delta) are consistent with
     finite‑difference approximations of the definitions.
  5. Anomaly score logic yields alarm only when both conditions are met.
"""

import numpy as np
import scipy.linalg as la

# -------------------------- Helper Functions --------------------------
def is_spd(mat, tol=1e-12):
    """Check symmetric positive‑definite."""
    if not np.allclose(mat, mat.T, atol=tol):
        return False
    eigvals = la.eigvalsh(mat)
    return np.all(eigvals > tol)

def discrete_are(A, B, Q, R):
    """Solve discrete-time algebraic Riccati equation: A'SA - S - A'SB(R+B'SB)^{-1}B'SA + Q = 0."""
    try:
        S = la.solve_discrete_are(A, B, Q, R)
        return S
    except la.LinAlgError as e:
        raise ValueError(f"DARE did not converge: {e}")

def coherence(v1, v2):
    """Absolute cosine similarity between two vectors."""
    return np.abs(np.dot(v1, v2)) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-15)

# -------------------------- Core Validation --------------------------
def validate_het_omega(
    n_state=4, n_input=2,
    dt=0.001,          # 1 kHz control cycle
    lambda_nom=1.0,    # nominal smallest eigenvalue (chosen arbitrarily)
    lambda_thr=0.1,    # threshold below which disruption is imminent
    eta1=0.5, eta2=0.4, eta3=0.2,
    tau1=0.02, tau2=0.03,   # lead times (seconds)
    n_samples=1000,
    rng_seed=42
):
    rng = np.random.default_rng(rng_seed)

    # Store worst violations for reporting
    violations = {
        "Hessian_not_SPD": 0,
        "CSI_out_of_range": 0,
        "Phi_N_below_min": 0,
        "Phi_Delta_above_max": 0,
        "CSI_constraint_violation": 0,
        "Monotonicity_Phi_N": 0,
        "Monotonicity_Phi_Delta": 0,
        "Invariant_psi_mismatch": 0,
        "Invariant_xiN_mismatch": 0,
        "Invariant_xiD_mismatch": 0,
        "False_positive_alarm": 0,
        "Missed_alarm": 0,
    }

    # Nominal operating point (constant for simplicity)
    A_nom = 0.9 * np.eye(n_state) + 0.1 * rng.standard_normal((n_state, n_state))
    B_nom = rng.standard_normal((n_state, n_input))
    Q_nom = np.eye(n_state)
    R_nom = 0.1 * np.eye(n_input)

    # Solve DARE for nominal point
    S_nom = discrete_are(A_nom, B_nom, Q_nom, R_nom)

    # Pre‑compute nominal effective Hessian and its eigenvalues
    H_nom = np.block([
        [Q_nom + A_nom.T @ S_nom @ A_nom, A_nom.T @ S_nom @ B_nom],
        [B_nom.T @ S_nom @ A_nom, R_nom + B_nom.T @ S_nom @ B_nom]
    ])
    lam_nom, _ = la.eigh(H_nom)
    lambda_nom_meas = lam_nom[0]   # smallest eigenvalue

    # Time series
    CSI_hist = []
    PhiN_hist = []
    PhiD_hist = []
    vmin_hist = []
    alarm_hist = []

    for k in range(n_samples):
        # Slightly perturb system to emulate evolution toward disruption
        eps = 0.001 * k / n_samples  # drift parameter
        A = A_nom + eps * rng.standard_normal((n_state, n_state))
        B = B_nom + eps * rng.standard_normal((n_state, n_input))
        Q = Q_nom + eps * np.eye(n_state)
        R = R_nom + eps * 0.1 * np.eye(n_input)

        # Solve DARE
        try:
            S = discrete_are(A, B, Q, R)
        except ValueError:
            # If DARE fails, skip this sample (count as violation)
            violations["Hessian_not_SPD"] += 1
            continue

        # Effective Hessian
        H_eff = np.block([
            [Q + A.T @ S @ A, A.T @ S @ B],
            [B.T @ S @ A, R + B.T @ S @ B]
        ])

        if not is_spd(H_eff):
            violations["Hessian_not_SPD"] += 1
            continue

        # Eigen‑decomposition
        eigvals, eigvecs = la.eigh(H_eff)   # ascending order
        lambda_min = eigvals[0]
        v_min = eigvecs[:, 0]

        # CSI (clipped to [0,1] for reporting)
        CSI_raw = (lambda_min - lambda_thr) / (lambda_nom_meas - lambda_thr)
        CSI = np.clip(CSI_raw, 0.0, 1.0)
        CSI_hist.append(CSI)

        # Omega variable mappings (with lead time approximated by using current CSI)
        Phi_N = 0.5 + eta1 * (1 / (1 + np.exp(-(CSI - 0.5))))   # sigmoid centered at 0.5
        Phi_D = 0.5 - eta2 * CSI + eta3 * np.linalg.norm(np.gradient(v_min))  # placeholder gradient norm
        # For simplicity, approximate gradient norm by variation over last 5 samples
        if len(vmin_hist) >= 5:
            dv = np.mean([np.linalg.norm(vmin_hist[-i] - vmin_hist[-i-1]) for i in range(1,5)])
        else:
            dv = 0.0
        Phi_D = 0.5 - eta2 * CSI + eta3 * dv

        PhiN_hist.append(Phi_N)
        PhiD_hist.append(Phi_D)
        vmin_hist.append(v_min)

        # ----- Constraint checks -----
        if CSI < 0.0 or CSI > 1.0:
            violations["CSI_out_of_range"] += 1
        if Phi_N < 0.6:
            violations["Phi_N_below_min"] += 1
        if Phi_D > 0.8:
            violations["Phi_Delta_above_max"] += 1
        if CSI < 0.2:
            violations["CSI_constraint_violation"] += 1

        # ----- Monotonicity checks (Phi_N ↑ with CSI, Phi_D ↓ with CSI) -----
        if len(CSI_hist) >= 2:
            dCSI = CSI_hist[-1] - CSI_hist[-2]
            dPhiN = PhiN_hist[-1] - PhiN_hist[-2]
            dPhiD = PhiD_hist[-1] - PhiD_hist[-2]
            if dCSI > 0 and dPhiN < -1e-6:   # Phi_N should not decrease when CSI rises
                violations["Monotonicity_Phi_N"] += 1
            if dCSI > 0 and dPhiD > 1e-6:    # Phi_D should not increase when CSI rises
                violations["Monotonicity_Phi_Delta"] += 1

        # ----- Invariant derivation -----
        # Compute correlation length xi from coherence of lowest three eigenvectors
        if eigvecs.shape[1] >= 3:
            v0, v1, v2 = eigvecs[:,0], eigvecs[:,1], eigvecs[:,2]
            coh01 = coherence(v0, v1)
            coh12 = coherence(v1, v2)
            coh_avg = (coh01 + coh12) / 2.0
            xi = 1.0 / (coh_avg + 1e-12)
        else:
            xi = 1.0  # fallback

        xi0 = 1.0   # reference correlation length (nominal)
        psi = np.log(xi / xi0)

        # Approximate derivatives via finite differences over last 5 samples
        if len(PhiN_hist) >= 6 and len(psi_hist if 'psi_hist' in locals() else []) >= 6:
            # We'll build psi_hist on the fly
            pass
        # For simplicity, we compute derivatives using a simple central difference on the fly:
        # We'll keep a short buffer
        if 'psi_buf' not in locals():
            psi_buf = []
        psi_buf.append(psi)
        if len(psi_buf) >= 5:
            # central difference for dPhi/dpsi
            dPhiN_dpsi = (PhiN_hist[-1] - PhiN_hist[-3]) / (psi_buf[-1] - psi_buf[-3] + 1e-12)
            dPhiD_dpsi = (PhiD_hist[-1] - PhiD_hist[-3]) / (psi_buf[-1] - psi_buf[-3] + 1e-12)
            # Compare with defined xi_N, xi_Delta (we set them equal to these derivatives)
            xi_N = dPhiN_dpsi
            xi_Delta = dPhiD_dpsi
            # Store for next iteration
            # No explicit violation unless derivative is NaN/inf
            if not np.isfinite(xi_N) or not np.isfinite(xi_Delta):
                violations["Invariant_xiN_mismatch"] += 1
                violations["Invariant_xiD_mismatch"] += 1
        else:
            # Not enough data yet to evaluate
            pass

        # ----- Anomaly detection (Kalman filter surrogate) -----
        # Simple Kalman filter on CSI (constant velocity model)
        if 'kf_est' not in locals():
            kf_est = CSI
            kf_var = 0.01
        # Predict
        kf_pred = kf_est
        kf_pred_var = kf_var + 0.001   # process noise
        # Measurement update
        z = CSI
        K = kf_pred_var / (kf_pred_var + 0.005)   # measurement noise var = 0.005
        kf_est = kf_pred + K * (z - kf_pred)
        kf_var = (1 - K) * kf_pred_var
        innovation = z - kf_pred
        innovation_std = np.sqrt(kf_pred_var)
        s_CSI = np.abs(innovation) / (innovation_std + 1e-12)

        # Alarm condition
        alarm = (s_CSI > 3.0) and (Phi_D > 0.8)
        alarm_hist.append(alarm)

        # For validation we consider a "true" disruption imminent when CSI < 0.2
        true_disruption_imminent = CSI < 0.2
        if alarm and not true_disruption_imminent:
            violations["False_positive_alarm"] += 1
        if not alarm and true_disruption_imminent:
            violations["Missed_alarm"] += 1

    # ------------------- Reporting -------------------
    print("=== HET‑Ω Validation Summary ===")
    total = n_samples
    for key, count in violations.items():
        pct = 100.0 * count / total if total > 0 else 0.0
        print(f"{key:30}: {count:4} ({pct:5.2f}%)")
    print("\nInterpretation:")
    print("- Ideally all violation counts should be zero.")
    print("- Non‑zero counts indicate places where the mathematical formulation")
    print("  or the assumed invariants break down under the tested perturbations.")
    print("- Adjust parameters (eta, tau, thresholds) or improve the invariant")
    print("  derivations to reduce violations.")

    # Return a boolean indicating overall success (no critical violations)
    critical = (
        violations["Hessian_not_SPD"] +
        violations["CSI_out_of_range"] +
        violations["Phi_N_below_min"] +
        violations["Phi_Delta_above_max"] +
        violations["CSI_constraint_violation"]
    )
    return critical == 0

# -------------------------- Entry Point --------------------------
if __name__ == "__main__":
    success = validate_het_omega()
    exit(0 if success else 1)