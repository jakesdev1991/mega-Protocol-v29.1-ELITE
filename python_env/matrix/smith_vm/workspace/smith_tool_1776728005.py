# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
CDST-Ω mathematical‑soundness validator.
Checks Omega Protocol invariants Φ_N, Φ_Δ, J* for the proposed
Cross‑Domain Stability Transfer pipeline.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# ----------------------------------------------------------------------
# Configuration (tweak to match your environment)
# ----------------------------------------------------------------------
FINANCE_DIM = 5          # number of extracted stable‑coin risk features
PLASMA_DIM  = 5          # number of mapped tokamak features (same size for simplicity)
KAPPA       = 1.5        # max allowed operator norm of the mapping M
EPS_P       = 0.1        # max allowed disruption probability (MPC constraint)
PHI_N_MAX   = 10.0       # nominal stability‑norm bound
PHI_DELTA_MAX = 2.0      # max allowed jump in Φ_N per step
J_TOL       = 0.2        # allowed excess over baseline cost
N_SAMPLES   = 500        # synthetic dataset size
SEED        = 42

rng = np.random.default_rng(SEED)

# ----------------------------------------------------------------------
# Helper: generate a random linear mapping M with bounded spectral norm
# ----------------------------------------------------------------------
def generate_mapping(in_dim, out_dim, max_norm):
    """Return a matrix M with ||M||_2 <= max_norm."""
    # Random Gaussian matrix
    M = rng.standard_normal((out_dim, in_dim))
    # Scale to desired spectral norm
    _, s, _ = np.linalg.svd(M, full_matrices=False)
    scale = max_norm / s[0] if s[0] > 0 else 1.0
    return M * scale

M = generate_mapping(FINANCE_DIM, PLASMA_DIM, KAPPA)
assert np.linalg.norm(M, 2) <= KAPPA + 1e-9, "Mapping violates Φ_N bound"

# ----------------------------------------------------------------------
# Synthetic finance feature generator (stand‑in for white‑paper NLP output)
# ----------------------------------------------------------------------
def gen_finance_features(n):
    """Generate plausible stable‑coin risk features."""
    # Features: peg deviation, liquidity depth, arb volume, oracle latency, whale conc.
    X = rng.uniform(low=[-5, 0, 0, 0, 0],
                    high=[ 5, 10, 10, 5, 1],
                    size=(n, FINANCE_DIM))
    return X

# ----------------------------------------------------------------------
# Synthetic plasma label generator (disruption = 1 if a hidden plasma variable exceeds threshold)
# ----------------------------------------------------------------------
def plasma_label_from_finance(X_f):
    """Map finance features to plasma state via M, then compute a disruption label."""
    X_p = X_f @ M.T                     # apply mapping (finance -> plasma)
    # Hidden plasma variable: weighted sum of first two mapped features
    hidden = 0.6 * X_p[:, 0] + 0.4 * X_p[:, 1]
    # Disruption if hidden > 0 (threshold chosen arbitrarily)
    y = (hidden > 0).astype(int)
    return X_p, y

# ----------------------------------------------------------------------
# Build dataset
# ----------------------------------------------------------------------
X_f = gen_finance_features(N_SAMPLES)
X_p, y = plasma_label_from_finance(X_f)

# Standardize plasma features (as would be done before ML)
scaler = StandardScaler()
X_p_std = scaler.fit_transform(X_p)

# ----------------------------------------------------------------------
# Step 1: Train a base model on finance data (proxy for white‑paper model)
# ----------------------------------------------------------------------
# We train a logistic regression on finance features to predict the *same* label
# (this mimics using finance‑derived patterns to anticipate plasma disruption).
base_model = LogisticRegression(max_iter=1000)
base_model.fit(X_f, y)

# ----------------------------------------------------------------------
# Step 2: Transfer learning – freeze early layers, fine‑tune last layer.
# For a linear model this reduces to keeping the coefficients except the intercept.
# ----------------------------------------------------------------------
# Extract coefficients (weights) and intercept
W_base = base_model.coef_.copy()          # shape (1, FINANCE_DIM)
b_base = base_model.intercept_.copy()     # shape (1,)

# We will keep W_base fixed and only relearn an intercept on plasma data.
# Map plasma features back to finance space via pseudo‑inverse of M to use same W.
M_pinv = np.linalg.pinv(M)                # (FINANCE_DIM x PLASMA_DIM)
# Transform plasma features to finance-equivalent space
X_f_eq = X_p_std @ M_pinv.T               # (N, FINANCE_DIM)

# Fit a new intercept using logistic regression with fixed weights
# We solve for b that maximizes likelihood given fixed W.
def neg_log_likelihood(b):
    z = X_f_eq @ W_base.T + b
    # logistic loss
    return np.sum(np.log1p(np.exp(-y * z.ravel())))

from scipy.optimize import minimize
res = minimize(neg_log_likelihood, x0=np.array([0.0]), method='BFGS')
b_transfer = res.x

# Final transfer model
def predict_disruption_prob(X_plasma):
    """Return P(disrupt) for plasma feature vectors (already standardized)."""
    X_eq = X_plasma @ M_pinv.T
    logits = X_eq @ W_base.T + b_transfer
    probs = 1.0 / (1.0 + np.exp(-logits.ravel()))
    return probs

# ----------------------------------------------------------------------
# Step 3: MPC‑Ω augmentation and invariant checking
# ----------------------------------------------------------------------
def phi_n(state_vec):
    """Nominal stability norm – Euclidean norm of the state."""
    return np.linalg.norm(state_vec, 2)

def phi_delta(state_prev, state_curr):
    """Change in Φ_N between two successive steps."""
    return abs(phi_n(state_curr) - phi_n(state_prev))

def j_cost(state_vec, ctrl_effort):
    """Quadratic control‑effort cost (state weighting omitted for simplicity)."""
    return 0.5 * np.dot(ctrl_effort, ctrl_effort)   # placeholder

# Simulate a few control steps
state_prev = np.zeros(PLASMA_DIM)   # dummy initial state (e.g., normalized diagnostics)
violations = []

for step in range(5):
    # Get a random plasma sample as the "measurement"
    idx = rng.integers(0, X_p_std.shape[0])
    plasma_meas = X_p_std[idx]                     # standardized plasma features
    p_disrupt = predict_disruption_prob(plasma_meas.reshape(1, -1))[0]

    # Build augmented MPC state: [plasma_features, P_disrupt]
    mpc_state = np.concatenate([plasma_meas, [p_disrupt]])

    # Dummy control effort: try to reduce P_disrupt via a simple proportional law
    ctrl_effort = -0.5 * np.array([0.0]*PLASMA_DIM + [p_disrupt])  # only act on probability channel
    ctrl_effort = ctrl_effort[:PLASMA_DIM]   # apply to plasma actuators only

    # Invariants
    phi_n_val = phi_n(mpc_state)
    phi_delta_val = phi_delta(state_prev, mpc_state)
    j_val = j_cost(mpc_state, ctrl_effort)

    # Baseline cost (no control) for comparison
    j_baseline = j_cost(mpc_state, np.zeros_like(ctrl_effort))

    # Check
    if not (p_disrupt <= EPS_P + 1e-9):
        violations.append(f"Step {step}: P_disrupt={p_disrupt:.3f} > ε={EPS_P}")
    if not (phi_n_val <= PHI_N_MAX + 1e-9):
        violations.append(f"Step {step}: Φ_N={phi_n_val:.3f} > Φ_N^max={PHI_N_MAX}")
    if not (phi_delta_val <= PHI_DELTA_MAX + 1e-9):
        violations.append(f"Step {step}: |ΔΦ_N|={phi_delta_val:.3f} > Φ_Δ^max={PHI_DELTA_MAX}")
    if not (j_val <= j_baseline * (1.0 + J_TOL) + 1e-9):
        violations.append(f"Step {step}: J={j_val:.3f} > J_baseline*(1+τ)={j_baseline*(1.0+J_TOL):.3f}")

    state_prev = mpc_state

# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
if violations:
    print("INVARIANT VIOLATIONS DETECTED:")
    for v in violations:
        print(" -", v)
    raise AssertionError("CDST-Ω proposal breaches Omega Protocol invariants.")
else:
    print("All Omega Protocol invariants satisfied for the simulated run.")
    print(f"Final Φ_N: {phi_n(state_prev):.3f} (limit {PHI_N_MAX})")
    print(f"Final |ΔΦ_N|: {phi_delta(state_prev*0, state_prev):.3f} (limit {PHI_DELTA_MAX})")
    print(f"Final disruption probability: {predict_disruption_prob(state_prev[:PLASMA_DIM].reshape(1,-1))[0]:.3f} (limit {EPS_P})")