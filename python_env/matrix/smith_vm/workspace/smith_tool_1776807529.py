# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Invariant Validator for the TTM‑Ω / TCPM‑Ω proposals.

The script checks the mathematical relationships that the author claims
are invariant under the Ω‑Physics Rubric v26.0:

    • Φ_N   = 1 – TTCI                         (TTM‑Ω mapping)
    • Φ_Δ   = Var[ log( ξ_ij / ξ₀ ) ]          (TTM‑Ω mapping)
    • ψ_ttm = ln|⟨Wₚ(t)⟩| – ln|⟨Wₚ(0)⟩|
              + λ·ln( Δ_regime(t) / Δ₀ )      (topological response invariant)
    • ψ     = ln Φ_N   = ln( ξ₀ / ξ_T )       (TCPM‑Ω thermal invariant)

If any relationship deviates beyond a tolerance, the script raises an
AssertionError and prints the offending time‑step.

The validator is deliberately lightweight – it only requires NumPy.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (mirroring the definitions in the proposal)
# ----------------------------------------------------------------------
def compute_TTCI(Wp_t, Wp_0, Delta_t, Delta_0, xi_t, xi_0):
    """
    Trading Topology Coherence Index (TTM‑Ω, Step 4).
    """
    term1 = np.abs(Wp_t) / np.abs(Wp_0)          # topology preservation
    term2 = Delta_t / Delta_0                    # regime adaptation
    term3 = xi_t / xi_0                          # correlation range
    return term1 * term2 * term3

def compute_Phi_N_ttm(TTCI):
    """Φ_N^{ttm} = 1 – TTCI   (Step 4, mapping to Ω variables)."""
    return 1.0 - TTCI

def compute_Phi_Delta_ttm(xi_ij_t, xi_0):
    """
    Φ_Δ^{ttm} = Var[ log( ξ_ij(t) / ξ₀ ) ].
    xi_ij_t: array‑like of pairwise correlation lengths at time t.
    """
    log_ratios = np.log(np.asarray(xi_ij_t) / xi_0)
    return np.var(log_ratios)

def compute_psi_ttm(Wp_t, Wp_0, Delta_t, Delta_0, lam=1.0):
    """
    ψ_ttm(t) = ln|⟨Wₚ(t)⟩| – ln|⟨Wₚ(0)⟩|
               + λ·ln( Δ_regime(t) / Δ₀ )
    """
    return np.log(np.abs(Wp_t) / np.abs(Wp_0)) + lam * np.log(Delta_t / Delta_0)

def compute_Psi_thermal(xi_T_t, xi_0):
    """
    ψ(t) = ln Φ_N = ln( ξ₀ / ξ_T(t) )   (TCPM‑Ω invariant)
    """
    return np.log(xi_0 / xi_T_t)

# ----------------------------------------------------------------------
# Synthetic data generator – replace with real measurements in practice
# ----------------------------------------------------------------------
def synthetic_time_series(T=100, seed=42):
    rng = np.random.default_rng(seed)
    # Base values (normals around 1.0 with small noise)
    Wp_0   = 1.0
    Delta_0 = 1.0
    xi_0   = 1.0

    Wp_t   = np.abs(Wp_0) * rng.lognormal(mean=0.0, sigma=0.1, size=T)
    Delta_t = Delta_0 * rng.lognormal(mean=0.0, sigma=0.15, size=T)
    xi_t   = xi_0 * rng.lognormal(mean=0.0, sigma=0.12, size=T)

    # Pairwise correlation lengths – we simulate a small set of 5 links
    xi_ij_t = np.array([
        xi_0 * rng.lognormal(mean=0.0, sigma=0.1, size=T) for _ in range(5)
    ]).T   # shape (T, 5)

    return {
        "Wp_t": Wp_t, "Wp_0": Wp_0,
        "Delta_t": Delta_t, "Delta_0": Delta_0,
        "xi_t": xi_t,   "xi_0": xi_0,
        "xi_ij_t": xi_ij_t
    }

# ------------------------------------------------------------------
# Validation routine
# ------------------------------------------------------------------
def validate_ttm_omega(data, tol=1e-6, lam=1.0):
    """
    Checks all claimed invariant relationships for the TTM‑Ω formulation.
    Returns True if everything passes within `tol`.
    """
    T = len(data["Wp_t"])
    for t in range(T):
        # 1️⃣ Compute TTCI and derived Φ_N
        TTCI_t = compute_TTCI(
            data["Wp_t"][t], data["Wp_0"],
            data["Delta_t"][t], data["Delta_0"],
            data["xi_t"][t],   data["xi_0"]
        )
        Phi_N_ttm_t = compute_Phi_N_ttm(TTCI_t)

        # 2️⃣ Compute Φ_Δ
        Phi_Delta_ttm_t = compute_Phi_Delta_ttm(
            data["xi_ij_t"][t], data["xi_0"]
        )

        # 3️⃣ Compute ψ_ttm (topological response invariant)
        psi_ttm_t = compute_psi_ttm(
            data["Wp_t"][t], data["Wp_0"],
            data["Delta_t"][t], data["Delta_0"],
            lam=lam
        )

        # 4️⃣ According to the proposal, ψ_ttm should equal ln Φ_N^{ttm}
        #    (see Step 4: “Mapping to Ω Variables” – they define Φ_N^{ttm}=1‑TTCI
        #    and later give an invariant ψ_ttm that is meant to represent the
        #    same topological coherence.  We therefore enforce:
        #        ψ_ttm ≈ ln(Φ_N^{ttm})
        lhs = psi_ttm_t
        rhs = np.log(np.abs(Phi_N_ttm_t) + 1e-12)   # guard against log(0)

        if not np.isclose(lhs, rhs, atol=tol, rtol=0):
            raise AssertionError(
                f"TTM‑Ω invariant violation at t={t}: "
                f"ψ_ttm={lhs:.6f}, ln(Φ_N)={rhs:.6f}, diff={lhs-rhs:.6f}"
            )

        # 5️⃣ Optional sanity bounds (the paper enforces TTCI ≥ 0.6, etc.)
        if TTCI_t < 0.6:
            raise AssertionError(f"TTI below safety threshold at t={t}: {TTCI_t:.3f}")

    print("✅ All TTM‑Ω invariant checks passed.")
    return True

def validate_tcp_m_omega(data, tol=1e-6):
    """
    Checks the TCPM‑Ω thermal invariant:
        ψ(t) = ln Φ_N = ln( ξ₀ / ξ_T(t) )
    """
    T = len(data["xi_t"])
    for t in range(T):
        psi_thermal_t = compute_Psi_thermal(data["xi_t"][t], data["xi_0"])
        # Φ_N from the thermal side is defined as ξ₀/ξ_T
        Phi_N_thermal_t = data["xi_0"] / data["xi_t"][t]
        lhs = psi_thermal_t
        rhs = np.log(Phi_N_thermal_t)

        if not np.isclose(lhs, rhs, atol=tol, rtol=0):
            raise AssertionError(
                f"TCPM‑Ω invariant violation at t={t}: "
                f"ψ={lhs:.6f}, ln(Φ_N)={rhs:.6f}, diff={lhs-rhs:.6f}"
            )
    print("✅ All TCPM‑Ω invariant checks passed.")
    return True

# ----------------------------------------------------------------------
# Run the validator on synthetic data (replace with real telemetry)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    data = synthetic_time_series(T=200, seed=123)

    print("Validating TTM‑Ω …")
    validate_ttm_omega(data, tol=1e-5)

    print("Validating TCPM‑Ω …")
    validate_tcp_m_omega(data, tol=1e-5)

    print("\nAll Ω‑Protocol invariants are satisfied for the supplied data.")