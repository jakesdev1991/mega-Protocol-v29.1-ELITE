# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ----------------------------------------------------------------------
# Configuration (can be tuned per domain)
# ----------------------------------------------------------------------
EPS = 1e-12          # to avoid log2(0)
GAMMA = 1.0          # stiffness coupling in the metric
PHI_MIN = -3.0       # as used in the thought
PHI_SCALE = 0.5
R_MAX = 2.8
C_AUDIT = 6          # six invariant checks
K_B_LOG2 = np.log(2) # Landauer factor (k_B * ln 2)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def normalize(v):
    """Return unit-norm vector; if norm is zero, return zeros."""
    n = np.linalg.norm(v)
    if n == 0:
        return np.zeros_like(v)
    return v / n

def compute_cod(latent, value):
    """Fidelity COD = |<latent|value>|^2 (vectors assumed normalized)."""
    latent_u = normalize(latent)
    value_u = normalize(value)
    return np.abs(np.vdot(latent_u, value_u)) ** 2

def phi_N_from_cod(cod):
    return np.log2(cod + EPS)

def psi_from_phi_N(phi_N):
    return np.tanh((phi_N - PHI_MIN) / PHI_SCALE)

def phi_Delta_from_psi_and_stiffness(psi, xi_buyer, xi_seller):
    R_align = xi_buyer - xi_seller
    return psi * np.tanh(np.abs(R_align) / R_MAX)

def delta_S_audit():
    return K_B_LOG2 * C_AUDIT

def approx_det_g(cod, xi_buyer, xi_seller):
    """
    Approximate determinant of the metric:
        det(g) ≈ COD * exp(-GAMMA * |Xi_seller - Xi_buyer|)
    This follows from the discussion that the overlap of partial derivatives
    scales with state overlap (COD) and the exponential penalty for stiffness mismatch.
    """
    return cod * np.exp(-GAMMA * np.abs(xi_seller - xi_buyer))

def shannon_entropy(p):
    """Shannon entropy (in bits) for a probability vector p."""
    p = np.asarray(p)
    p = p[p > 0]          # remove zeros to avoid log(0)
    return -np.sum(p * np.log2(p))

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_omega_invariants(psi_latent, psi_value,
                              xi_seller, xi_buyer):
    """
    Returns:
        pass_all (bool): True if all invariants satisfied.
        diagnostics (dict): Detailed values and per‑invariant results.
    """
    # 1. COD and derived quantities
    cod = compute_cod(psi_latent, psi_value)
    phi_N = phi_N_from_cod(cod)
    psi = psi_from_phi_N(phi_N)
    phi_Delta = phi_Delta_from_psi_and_stiffness(psi, xi_buyer, xi_seller)
    delta_S = delta_S_audit()
    phi_net = phi_N + phi_Delta - delta_S

    # 2. Approximate metric determinant
    det_g = approx_det_g(cod, xi_buyer, xi_seller)

    # 3. Entropy of latent state (interpreted as a probability distribution)
    #    We treat the latent vector as unnormalized probabilities.
    latent_prob = np.abs(psi_latent)  # ensure non‑negative
    latent_prob = latent_prob / np.sum(latent_prob) if np.sum(latent_prob) > 0 else latent_prob
    H_collapse = shannon_entropy(latent_prob)

    # 4. Invariant checks
    inv_metric_nondeg = det_g > np.exp(-psi)                     # ||det(g)|| > exp(-psi)
    inv_identity_cont = psi >= 0.95                              # psi >= 0.95
    inv_stiffness_match = xi_seller <= xi_buyer                  # Xi_seller <= Xi_buyer
    inv_entropy_cap = H_collapse <= 0.3                          # H_collapse <= 0.3
    inv_info_conserv = phi_net >= 0.0                            # Delta Phi_net >= 0
    inv_asymmetry = phi_Delta < 0.5 * phi_N                      # Phi_Delta < 0.5 * Phi_N

    diagnostics = {
        "COD": cod,
        "Phi_N": phi_N,
        "Psi": psi,
        "Phi_Delta": phi_Delta,
        "Delta_S_audit": delta_S,
        "Phi_net": phi_net,
        "det_g_approx": det_g,
        "H_collapse": H_collapse,
        "Invariant_MetricNonDegeneracy": inv_metric_nondeg,
        "Invariant_IdentityContinuity": inv_identity_cont,
        "Invariant_StiffnessMatching": inv_stiffness_match,
        "Invariant_EntropyCap": inv_entropy_cap,
        "Invariant_InformationConservation": inv_info_conserv,
        "Invariant_AsymmetryControl": inv_asymmetry,
    }

    pass_all = all([
        inv_metric_nondeg,
        inv_identity_cont,
        inv_stiffness_match,
        inv_entropy_cap,
        inv_info_conserv,
        inv_asymmetry,
    ])

    return pass_all, diagnostics

# ----------------------------------------------------------------------
# Example usage (reproducing the numbers from the thought)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example vectors from the code snippet in the thought
    psi_latent = np.array([0.7, 0.2, 0.1])   # [Safety, Innovation, Political Risk]
    psi_value  = np.array([0.8, 0.15, 0.05]) # [Value, Risk, Compliance]
    xi_seller  = 0.3
    xi_buyer   = 0.6

    passed, diag = validate_omega_invariants(psi_latent, psi_value,
                                             xi_seller, xi_buyer)

    print("=== OMEGA PROTOCOL INVARIANT VALIDATION ===")
    for k, v in diag.items():
        if isinstance(v, float):
            print(f"{k:30}: {v:.6f}")
        else:
            print(f"{k:30}: {v}")
    print("-" * 50)
    print(f"OVERALL PASS: {passed}")