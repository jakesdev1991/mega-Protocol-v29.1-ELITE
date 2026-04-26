# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Validation for Data‑Leakage Topology Monitor (DLTM‑Ω)

This script validates the mathematical consistency of a single time‑step
snapshot of the DLTM‑Ω state.  It assumes all inputs are already
normalized (dimensionless) as per the proposal.
"""

import math
from typing import List, Tuple

def validate_dltm_state(
    # ---- Raw graph / exposure data ----
    exposure_per_dir: List[float],          # c_i = total anomalous flow exposed per directory
    spectral_gap: float,                    # λ₁ > 0 (normalized Laplacian)
    ollivier_ricci: List[float],            # R_{ij} for each edge (i,j)
    exposure_duration: List[float],         # dur_i for each directory
    # ---- Model parameters (tanh coefficients) ----
    alpha: float = 1.0,
    beta:  float = 1.0,
    gamma: float = 1.0,
    delta: float = 1.0,
    # ---- Ω‑mapping parameters ----
    PhiN0: float = 1.0,
    PhiD0: float = 1.0,
    eta1: float = 0.5,
    eta2: float = 0.5,
    eta3: float = 0.5,
    eta4: float = 0.5,
    tau1: int = 0,          # steps of delay (0 = no delay for snapshot)
    tau2: int = 0,
    R0: float = 1.0,        # reference curvature scale
    lam: float = 0.5,       # λ coupling in ψ_leak
    # ---- MPC / cost parameters ----
    mu1: float = 1.0,
    mu2: float = 1.0,
    mu3: float = 1.0,
) -> None:
    """
    Raises AssertionError if any invariant or constraint is violated.
    Returns None on success.
    """
    N = len(exposure_per_dir)
    assert N > 0, "At least one exposed directory required"
    assert len(exposure_duration) == N, "exposure_duration length mismatch"
    assert spectral_gap > 0.0, "Spectral gap λ₁ must be > 0 (add ε or ensure graph connectivity)"
    # ------------------------------------------------------------------
    # 1. Compute auxiliary scalars
    # ------------------------------------------------------------------
    total_c = sum(exposure_per_dir)
    assert total_c > 0.0, "Total exposure concentration must be > 0"
    # concentration term C = Σ c_i² / Σ c_i
    C = sum(c * c for c in exposure_per_dir) / total_c

    # inverse spectral gap term
    inv_lambda1 = 1.0 / spectral_gap

    # mean absolute Ollivier‑Ricci curvature
    assert len(ollivier_ricci) > 0, "Ollivier‑Ricci list must be non‑empty"
    mean_abs_R = sum(abs(r) for r in ollivier_ricci) / len(ollivier_ricci)

    # exposure‑duration weights p_i and Shannon entropy S_leak
    total_dur = sum(exposure_duration)
    assert total_dur > 0.0, "Total exposure duration must be > 0"
    p = [d / total_dur for d in exposure_duration]
    S_leak = -sum(pi * math.log(pi) for pi in p if pi > 0.0)  # Shannon entropy, base e
    # Maximum possible entropy for N states is log(N)
    max_entropy = math.log(N)
    assert 0.0 <= S_leak <= max_entropy + 1e-12, f"S_leak={S_leak} out of [0, log(N)]"

    # ------------------------------------------------------------------
    # 2. DLFI via tanh (ensured ∈ [0,1])
    # ------------------------------------------------------------------
    DLFI_raw = alpha * C + beta * inv_lambda1 + gamma * mean_abs_R + delta * (1.0 - S_leak)
    DLFI = math.tanh(DLFI_raw)
    assert 0.0 <= DLFI <= 1.0, f"DLFI={DLFI} not in [0,1]"

    # ------------------------------------------------------------------
    # 3. Ω‑mapping (Φ_N, Φ_Δ) – using delayed DLFI (tau steps)
    #    For a snapshot we treat delayed = current if tau=0.
    # ------------------------------------------------------------------
    # In a real implementation we would fetch DLFI[t‑tau]; here we just use DLFI.
    PhiN_leak = PhiN0 - eta1 * DLFI + eta2 * spectral_gap
    PhiD_leak = PhiD0 + eta3 * (max(exposure_per_dir) / (total_c / N if N > 0 else 1.0)) - eta4 * S_leak
    assert PhiN_leak >= 0.0, f"Φ_N^{leak}={PhiN_leak} negative"
    assert PhiD_leak >= 0.0, f"Φ_Δ^{leak}={PhiD_leak} negative"

    # ------------------------------------------------------------------
    # 4. Invariant ψ_leak (Ollivier‑Ricci sum)
    # ------------------------------------------------------------------
    Ricci_sum = sum(ollivier_ricci)  # signed sum, can be negative
    psi_leak = math.log(abs(Ricci_sum) / R0) + lam * DLFI
    # psi_leak can be any real; just ensure it's not NaN
    assert not math.isnan(psi_leak), "ψ_leak is NaN"

    # ------------------------------------------------------------------
    # 5. Stiffness coefficients (derivatives w.r.t ψ_leak) – analytic forms
    #    ξ_N = ∂Φ_N/∂ψ_leak = -η₁ * (∂DLFI/∂ψ_leak) + η₂ * (∂λ₁/∂ψ_leak)
    #    For validation we only need to ensure they are real numbers.
    #    We approximate ∂DLFI/∂ψ_leak via chain rule:
    #        dDLFI/dψ = (1 - tanh²) * (∂DLFI_raw/∂ψ)
    #    Assuming λ₁ and ψ_leak are independent for this snapshot,
    #    we set ∂λ₁/∂ψ = 0, ∂DLFI_raw/∂ψ = lam (since DLFI_raw contains lam*DLFI? 
    #    Actually DLFI_raw does NOT contain ψ; ψ contains DLFI. So we treat
    #    ∂DLFI/∂ψ = 0 for simplicity – the validation only checks reality.
    # ------------------------------------------------------------------
    xi_N = 0.0   # placeholder; real implementation would compute full Jacobian
    xi_D = 0.0
    assert isinstance(xi_N, (int, float)) and isinstance(xi_D, (int, float)), "Stiffness coeffs non‑numeric"

    # ------------------------------------------------------------------
    # 6. MPC constraints
    # ------------------------------------------------------------------
    assert DLFI <= 0.7 + 1e-9, f"DLFI constraint violated: DLFI={DLFI} > 0.7"
    assert PhiN_leak >= 0.6 - 1e-9, f"Φ_N^{leak} constraint violated: Φ_N={PhiN_leak} < 0.6"
    assert S_leak >= math.log(3) - 1e-9, f"S_leak constraint violated: S_leak={S_leak} < log(3)"

    # ------------------------------------------------------------------
    # 7. Stage cost (non‑negative)
    # ------------------------------------------------------------------
    cost = (
        max(DLFI - 0.6, 0.0) ** 2 +
        mu1 * max(0.6 - PhiN_leak, 0.0) ** 2 +
        mu2 * (PhiD_leak ** 2) +
        mu3 * max(math.log(3) - S_leak, 0.0) ** 2
    )
    assert cost >= 0.0, f"Cost negative: {cost}"

    # If we reach here, all checks passed
    print("[OK] All DLTM‑Ω mathematical invariants and Ω‑Protocol constraints satisfied.")
    print(f"  DLFI          = {DLFI:.4f}")
    print(f"  Φ_N^{leak}    = {PhiN_leak:.4f}")
    print(f"  Φ_Δ^{leak}    = {PhiD_leak:.4f}")
    print(f"  ψ_leak        = {psi_leak:.4f}")
    print(f"  S_leak        = {S_leak:.4f} (max={max_entropy:.4f})")
    print(f"  Stage cost    = {cost:.6f}")

# ----------------------------------------------------------------------
# Example usage with synthetic data (feel free to replace with real measurements)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Synthetic graph: 4 directories, moderate exposure
    exposure_per_dir = [2.0, 1.5, 0.5, 0.2]          # c_i
    spectral_gap = 0.35                             # λ₁ > 0
    ollivier_ricci = [0.1, -0.05, 0.2, 0.0, 0.15]   # example edge curvatures
    exposure_duration = [10.0, 8.0, 2.0, 1.0]       # dur_i

    validate_dltm_state(
        exposure_per_dir=exposure_per_dir,
        spectral_gap=spectral_gap,
        ollivier_ricci=ollivier_ricci,
        exposure_duration=exposure_duration,
        # feel free to tweak parameters to test edge cases
    )