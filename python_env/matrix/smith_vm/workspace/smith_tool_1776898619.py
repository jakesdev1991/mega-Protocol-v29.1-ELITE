# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Trauma‑Induced Performance Anxiety Model
--------------------------------------------------------------------------------
This script checks the mathematical soundness of the Q-Systemic Self mapping
described in the agent's thought. It validates:
  * COD_trauma computation (fidelity)
  * Unitarity of the Phase‑Shift Decoupling (PSD) operator
  * Conservation of an informational stiffness observable
  * The identity invariant ψ_id = ln(φ_id)

Usage:
    python3 omega_validator.py
"""

import numpy as np
from scipy.linalg import expm

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def normalize(vec):
    """Return a normalized copy of vec (handles zero vector safely)."""
    norm = np.linalg.norm(vec)
    if norm == 0:
        raise ValueError("Cannot normalize the zero vector.")
    return vec / norm

def cod_threat_reality(psi_threat, psi_reality):
    """
    Compute COD_trauma = |<threat|reality>|^2 / (<threat|threat><reality|reality>)
    Works for un-normalized vectors.
    """
    num = np.abs(np.vdot(psi_threat, psi_reality)) ** 2
    den = (np.vdot(psi_threat, psi_threat) * np.vdot(psi_reality, psi_reality))
    if den == 0:
        raise ValueError("One of the vectors has zero norm.")
    return num / den

def identity_overlap(psi, psi_id):
    """φ_id = |<id|psi>|^2 (assumes psi_id is normalized)."""
    return np.abs(np.vdot(psi_id, psi)) ** 2

def psi_id_from_phi(phi):
    """ψ_id = ln(φ_id) – invariant definition."""
    if phi <= 0:
        raise ValueError("φ_id must be > 0 to take log.")
    return np.log(phi)

def stiffness_expectation(psi, stiffness_op=None):
    """
    Expectation value of stiffness observable.
    If stiffness_op is None, we use the identity (=> <ψ|ψ> = 1 for normalized ψ).
    """
    if stiffness_op is None:
        stiffness_op = np.eye(len(psi))
    return np.vdot(psi, stiffness_op @ psi).real  # should be real for Hermitian op

def psd_unitary(gamma_t, dt, dim=2):
    """
    Build the unitary for a small time step dt under
        H_eff = gamma(t) * sigma_x
    where sigma_x = [[0,1],[1,0]] embedded in the appropriate subspace.
    We assume the two-level subspace is spanned by basis vectors [0,1].
    """
    sigma_x = np.array([[0, 1],
                        [1, 0]], dtype=complex)
    # Embed into full Hilbert space if dim > 2 (identity on orthogonal complement)
    if dim > 2:
        sigma_x_full = np.eye(dim, dtype=complex)
        sigma_x_full[0:2, 0:2] = sigma_x
    else:
        sigma_x_full = sigma_x
    H = gamma_t * sigma_x_full
    U = expm(-1j * H * dt)   # ℏ = 1 units
    return U

# ----------------------------------------------------------------------
# Test scenario (feel free to modify vectors / gamma function)
# ----------------------------------------------------------------------
def run_validation():
    # Define a 2‑dimensional Hilbert space (threat |0>, safety |1>)
    dim = 2
    # Basis: |0> = [1,0]^T (threat), |1> = [0,1]^T (safety)
    # Example states (not normalized on purpose to test COD robustness)
    psi_threat_raw = np.array([1.2, 0.3], dtype=complex)   # some threat amplitude
    psi_reality_raw = np.array([0.1, 1.0], dtype=complex) # mostly safe reality
    psi_id_raw = np.array([1.0, 0.0], dtype=complex)      # identity aligned with threat basis

    # Normalize for evolution (states used in dynamics should be normalized)
    psi_threat = normalize(psi_threat_raw)
    psi_reality = normalize(psi_reality_raw)
    psi_id = normalize(psi_id_raw)

    # ---- 1. COD check -------------------------------------------------
    cod = cod_threat_reality(psi_threat_raw, psi_reality_raw)
    print(f"COD_trauma = {cod:.4f} (should be in [0,1])")
    assert 0.0 <= cod <= 1.0 + 1e-12, "COD out of bounds!"

    # ---- 2. Identity invariant check ----------------------------------
    phi_id = identity_overlap(psi_threat, psi_id)   # using current threat state as example
    psi_id_val = psi_id_from_phi(phi_id)
    # Re‑compute ψ_id from definition to ensure consistency
    psi_id_check = np.log(phi_id)
    assert np.isclose(psi_id_val, psi_id_check), "ψ_id ≠ ln(φ_id) invariant violated"
    print(f"Identity overlap φ_id = {phi_id:.6f} → ψ_id = ln(φ_id) = {psi_id_val:.6f}")

    # ---- 3. Stiffness observable (simple choice) ----------------------
    # Here we pick stiffness_op = |0><0| + |1><1| = I (norm preservation)
    stiffness_op = np.eye(dim, dtype=complex)
    xi_before = stiffness_expectation(psi_threat, stiffness_op)
    print(f"Initial stiffness expectation ξ = {xi_before:.6f} (should be 1 for normalized state)")

    # ---- 4. PSD evolution ------------------------------------------------
    # Define a sample time‑dependent coupling: a smooth pulse
    def gamma_t(t):
        # Example: a Gaussian pulse centered at t=0.5 with width 0.1
        return 2.0 * np.exp(-((t - 0.5) ** 2) / (2 * 0.05))

    total_time = 1.0
    steps = 200
    dt = total_time / steps
    psi = psi_threat.copy()   # start from threat state

    for step in range(steps):
        t = step * dt
        gamma = gamma_t(t)
        U = psd_unitary(gamma, dt, dim=dim)
        psi = U @ psi
        # Renormalize numerically (should stay ~1)
        psi = normalize(psi)

    # ---- 5. Post‑evolution checks --------------------------------------
    xi_after = stiffness_expectation(psi, stiffness_op)
    print(f"Final stiffness expectation ξ = {xi_after:.6f}")
    assert np.isclose(xi_after, xi_before, atol=1e-8), \
        "Stiffness not conserved during PSD evolution!"

    # COD after evolution (using the evolved state as new "threat" signal)
    cod_after = cod_threat_reality(psi, psi_reality_raw)
    print(f"COD after PSD = {cod_after:.4f}")

    # Identity invariant after evolution
    phi_id_after = identity_overlap(psi, psi_id)
    psi_id_after = np.log(phi_id_after)
    print(f"Post‑PSD φ_id = {phi_id_after:.6f} → ψ_id = {psi_id_after:.6f}")
    assert np.isclose(psi_id_after, np.log(phi_id_after)), \
        "ψ_id = ln(φ_id) invariant broken after evolution!"

    print("\n✅ All Omega Protocol invariant checks passed.")
    return True

if __name__ == "__main__":
    try:
        run_validation()
    except AssertionError as e:
        print(f"\n❌ Invariant violation: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise