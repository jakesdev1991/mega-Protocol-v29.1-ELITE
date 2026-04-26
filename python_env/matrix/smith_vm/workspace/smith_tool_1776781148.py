# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Runtime validator for the QNA‑RTM proposal.
Ensures:
  - Entropy >= log(5)
  - Confidence >= Confidence_Threshold
  - psi_unc <= psi_max
  - Robust loss >= 0
  - Instantaneous cost integrand >= 0
If any check fails, a RuntimeError is raised – the Omega Protocol
should then invoke a safe‑fallback control action.
"""

import numpy as np
from typing import Tuple, Dict

# ----------------------------------------------------------------------
# Protocol‑level constants (these would be supplied by the Omega Framework)
# ----------------------------------------------------------------------
LOG5 = np.log(5.0)                # ≈ 1.60944
CONFIDENCE_THRESHOLD = 0.7        # example threshold; tune per domain
PSI_MAX = 10.0                    # example upper bound on uncertainty magnitude
MU1 = 1.0                         # weight for entropy deviation term
MU2 = 1.0                         # weight for confidence deviation term

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def discrete_entropy(probs: np.ndarray) -> float:
    """
    Shannon entropy for a discrete distribution.
    Returns 0 for deterministic distributions.
    """
    # Guard against log(0)
    probs = np.clip(probs, 1e-12, 1.0)
    return -np.sum(probs * np.log(probs))

def robust_loss(theta_samples: np.ndarray,
                y_true: float,
                y_pred_fn) -> float:
    """
    Approximate the robust loss:
        L = E_q[ Entropy(q) + Var(y_true - y_pred) ]
    For demonstration we treat each theta sample as defining a
    categorical distribution over a fixed set of outcomes.
    """
    # Assume theta_samples shape = (N_samples, N_outcomes)
    # Each row is a probability vector (already normalized)
    entropies = np.apply_along_axis(discrete_entropy, 1, theta_samples)
    # y_pred is a deterministic function of theta (e.g., neural net output)
    y_preds = np.apply_along_axis(y_pred_fn, 1, theta_samples)
    variances = (y_true - y_preds) ** 2
    loss = np.mean(entropies + variances)
    return loss

def instantaneous_cost(state: Dict[str, float]) -> float:
    """
    Compute the integrand of J:
        psi_unc^2 + mu1*(log5 - Entropy)^2 + mu2*(Confidence - Threshold)^2
    """
    psi_unc = state["psi_unc"]
    entropy = state["Entropy"]
    conf = state["Confidence"]
    term1 = psi_unc ** 2
    term2 = MU1 * (LOG5 - entropy) ** 2
    term3 = MU2 * (conf - CONFIDENCE_THRESHOLD) ** 2
    return term1 + term2 + term3

def validate_state(state: Dict[str, float],
                   theta_samples: np.ndarray,
                   y_true: float,
                   y_pred_fn) -> None:
    """
    Perform all Omega‑Protocol invariant checks.
    Raises RuntimeError on the first violation.
    """
    # 1. QP constraints
    if state["psi_unc"] > PSI_MAX:
        raise RuntimeError(f"psi_unc ({state['psi_unc']:.3f}) exceeds psi_max ({PSI_MAX})")
    if state["Entropy"] < LOG5:
        raise RuntimeError(f"Entropy ({state['Entropy']:.3f}) below log(5) ({LOG5:.3f})")
    if state["Confidence"] < CONFIDENCE_THRESHOLD:
        raise RuntimeError(f"Confidence ({state['Confidence']:.3f}) below threshold ({CONFIDENCE_THRESHOLD})")

    # 2. Robust loss non‑negativity (should always hold for a proper distribution)
    loss = robust_loss(theta_samples, y_true, y_pred_fn)
    if loss < -1e-12:  # allow tiny numerical noise
        raise RuntimeError(f"Robust loss negative: {loss:.6e}")

    # 3. Cost integrand non‑negativity (sum of squares)
    cost = instantaneous_cost(state)
    if cost < -1e-12:
        raise RuntimeError(f"Instantaneous cost negative: {cost:.6e}")

    # If we reach here, all invariants are satisfied for this step.
    return None

# ----------------------------------------------------------------------
# Example usage (mock data)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock neural‑network prediction function: linear in theta for simplicity
    def mock_y_pred(theta):
        # theta is a probability vector; we map it to a scalar via a fixed weight vector
        w = np.linspace(0.1, 1.0, num=theta.shape[0])
        return np.dot(theta, w)

    # Generate some random probability vectors (Dirichlet) as theta samples
    rng = np.random.default_rng(seed=42)
    N_samples = 20
    N_outcomes = 5
    theta_samples = rng.dirichlet(alpha=np.ones(N_outcomes), size=N_samples)

    # Example state vector (could come from the controller at time t)
    state_example = {
        "Phi_N_quantum": 0.42,
        "Phi_D_neural": 0.57,
        "psi_unc": 3.2,          # must be <= PSI_MAX
        "xi_N": 0.1,
        "xi_D": -0.05,
        "Entropy": 1.68,         # must be >= log(5)
        "Confidence": 0.73       # must be >= threshold
    }

    y_true_observed = 0.55

    try:
        validate_state(state_example,
                       theta_samples,
                       y_true_observed,
                       mock_y_pred)
        print("✅ State passes all Omega‑Protocol invariant checks.")
    except RuntimeError as e:
        print("❌ Invariant violation detected:")
        print(e)