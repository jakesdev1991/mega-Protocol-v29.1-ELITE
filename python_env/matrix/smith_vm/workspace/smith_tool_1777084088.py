# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FSG-v57.2 Mathematical Validator
--------------------------------
Validates the core equations and Smith Audit invariants of the
Flux Stabilization Governor v57.2 proposal.

Usage:
    python fsg_validator.py   # runs a self‑test with sample data
"""

import numpy as np

# ----------------------------------------------------------------------
# Constants (taken from the proposal; modify to test different fixes)
# ----------------------------------------------------------------------
K_B = 1.380649e-23          # J/K (Boltzmann constant)
LN2 = np.log(2.0)

# Identity Continuity parameters (PROPOSED FIX)
# We use the form: psi = tanh( (Phi_N + KAPPA) / PHI_SCALE )
# Choose KAPPA / PHI_SCALE >= artanh(0.95) ≈ 1.83 to make psi>=0.95 possible.
KAPPA = 2.0          # offset added to Phi_N before scaling
PHI_SCALE = 1.0      # scaling factor
# If you want to keep the original shifted form, set KAPPA = -PHI_MIN
# and keep PHI_SCALE as given; then adjust PHI_MIN accordingly.

# Smith Audit thresholds (from proposal)
COD_MIN = 0.85
PSI_MIN = 0.95
XI_CONTROL_MAX_FACTOR = 1.0   # we will compare xi_control <= xi_kinematic
H_COLLAPSE_MAX = 0.3
PHI_DELTA_MAX_RATIO = 0.5    # Phi_Delta < 0.5 * Phi_N

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def cod_from_density_mats(rho_fire: np.ndarray, rho_sense: np.ndarray) -> float:
    """
    Classical fidelity: COD = Tr(rho_fire * rho_sense)
    Assumes both are valid density matrices (Hermitian, PSD, trace=1).
    """
    if not (np.allclose(rho_fire, rho_fire.conj().T) and
            np.allclose(rho_sense, rho_sense.conj().T)):
        raise ValueError("Input matrices must be Hermitian.")
    if not (np.isclose(np.trace(rho_fire), 1.0) and
            np.isclose(np.trace(rho_sense), 1.0)):
        raise ValueError("Input matrices must have trace 1.")
    return float(np.real(np.trace(rho_fire @ rho_sense)))

def phi_N_from_cod(cod: float) -> float:
    """Phi_N = log2(COD)."""
    if cod <= 0.0:
        return -np.inf
    return np.log2(cod)

def psi_from_phi_N(phi_N: float) -> float:
    """
    Identity Continuity with the proposed fix:
        psi = tanh( (phi_N + KAPPA) / PHI_SCALE )
    """
    return np.tanh((phi_N + KAPPA) / PHI_SCALE)

def phi_delta_from_psi_and_align(psi: float, R_align: float, R_max: float) -> float:
    """Phi_Delta = psi * tanh(R_align / R_max)."""
    return psi * np.tanh(R_align / R_max)

def audit_cost(C_audit: int) -> float:
    """Landauer cost per invariant check."""
    return K_B * LN2 * C_audit

def phi_net(cod: float, psi: float, R_align: float, R_max: float,
            C_audit: int) -> float:
    """Full Phi‑net expression."""
    phi_N = phi_N_from_cod(cod)
    phi_D = phi_delta_from_psi_and_align(psi, R_align, R_max)
    delta_S = audit_cost(C_audit)
    return phi_N + phi_D - delta_S

def enforce_smith_invariants(cod: float, psi: float,
                             xi_control: float, xi_kinematic: float,
                             h_collapse: float,
                             phi_N: float, phi_Delta: float,
                             C_audit: int) -> None:
    """
    Asserts all Smith Audit invariants. Raises AssertionError on violation.
    """
    # 1. COD ≥ 0.85
    assert cod >= COD_MIN, f"Invariant 1 failed: COD={cod:.4f} < {COD_MIN}"
    # 2. ψ ≥ 0.95
    assert psi >= PSI_MIN, f"Invariant 2 failed: ψ={psi:.4f} < {PSI_MIN}"
    # 3. Ξ_control ≤ Ξ_kinematic
    assert xi_control <= xi_kinematic, (
        f"Invariant 3 failed: Ξ_control={xi_control:.4f} > Ξ_kinematic={xi_kinematic:.4f}"
    )
    # 4. H_collapse ≤ 0.3
    assert h_collapse <= H_COLLAPSE_MAX, (
        f"Invariant 4 failed: H_collapse={h_collapse:.4f} > {H_COLLAPSE_MAX}"
    )
    # 5. ΔS_audit subtracted from Φ‑ledger (checked externally via phi_net)
    #    We just record the cost for transparency.
    delta_S = audit_cost(C_audit)
    # 6. Φ_Δ < 0.5 · Φ_N
    assert phi_Delta < PHI_DELTA_MAX_RATIO * phi_N, (
        f"Invariant 6 failed: Φ_Δ={phi_Delta:.4f} ≥ 0.5·Φ_N={0.5*phi_N:.4f}"
    )
    # If we reach here, all invariants hold.
    # Optional: print audit cost for the caller.
    return delta_S

# ----------------------------------------------------------------------
# Self‑test / demo
# ----------------------------------------------------------------------
def _demo():
    print("=== FSG‑v57.2 Validator Demo ===")
    # Example density matrices (simple mixed states)
    rho_fire = np.array([[0.7, 0.1+0.05j],
                         [0.1-0.05j, 0.3]])
    rho_sense = np.array([[0.6, 0.08-0.02j],
                          [0.08+0.02j, 0.4]])

    cod = cod_from_density_mats(rho_fire, rho_sense)
    print(f"COD = {cod:.5f}")

    phi_N = phi_N_from_cod(cod)
    print(f"Φ_N = log2(COD) = {phi_N:.5f}")

    psi = psi_from_phi_N(phi_N)
    print(f"ψ = tanh((Φ_N+KAPPA)/PHI_SCALE) = {psi:.5f}")

    # Example stiffness values
    xi_kinematic = 1.2   # arbitrary units
    xi_control = 0.9     # should be ≤ xi_kinematic
    R_align = xi_kinematic - xi_control   # positive gap
    R_max = 2.0          # chosen scaling for tanh

    phi_Delta = phi_delta_from_psi_and_align(psi, R_align, R_max)
    print(f"Φ_Δ = ψ * tanh(R_align/R_max) = {phi_Delta:.5f}")

    C_audit = 6   # number of invariant checks per cycle
    delta_S = audit_cost(C_audit)
    print(f"ΔS_audit = k_B·ln2·C_audit = {delta_S:.3e} J")

    net_phi = phi_net(cod, psi, R_align, R_max, C_audit)
    print(f"Φ_net = Φ_N + Φ_Δ - ΔS_audit = {net_phi:.5f}")

    # Enforce Smith Audit invariants
    try:
        enforce_smith_invariants(
            cod=cod,
            psi=psi,
            xi_control=xi_control,
            xi_kinematic=xi_kinematic,
            h_collapse=0.15,   # example value <0.3
            phi_N=phi_N,
            phi_Delta=phi_Delta,
            C_audit=C_audit
        )
        print("\n✅ All Smith Audit invariants satisfied.")
    except AssertionError as e:
        print(f"\n❌ Invariant violation: {e}")

    # Check whether ψ can ever reach the required threshold
    # Scan COD from 0 to 1 and see max ψ.
    cod_vals = np.linspace(1e-6, 1.0, 10000)
    psi_vals = psi_from_phi_N(np.log2(cod_vals))
    max_psi = np.max(psi_vals)
    print(f"\nMaximum achievable ψ over COD∈(0,1] = {max_psi:.5f}")
    if max_psi >= PSI_MIN:
        print("✅ ψ can reach the required invariant threshold.")
    else:
        print("❌ ψ CANNOT reach the required threshold – adjust KAPPA/PHI_SCALE.")

if __name__ == "__main__":
    _demo()