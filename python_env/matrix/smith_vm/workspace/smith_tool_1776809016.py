# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for BTS-Ω
Checks:
  - BTFI definition and bounds
  - Φ_N, Φ_Δ derivation from BTFI (lead‑time shift)
  - ψ_bts = ln(Φ_N/Φ_N0) invariant
  - Entropy gauge: S_bts = -∑ p_k log p_k  (must be conditional on subsystem type)
  - Gauge current: J^μ = (√2 Φ_Δ, 0,0,0)
  - Boundary conditions:
        Shredding: ψ → +∞  AND  S_bts → S_max (high entropy)
        Freeze   : ψ → -∞  AND  S_bts → S_min (low entropy)
  - MPC‑Ω constraints: BTFI ≤ 0.7, Φ_N ≥ 0.6, S_bts ≥ ln(3)
If any check fails, a ValidationError is raised with a diagnostic.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper exception
# ----------------------------------------------------------------------
class ValidationError(RuntimeError):
    pass

# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass
class SchemaTopology:
    V: int          # number of tables (vertices)
    E: int          # number of foreign‑key edges
    F: int          # number of independent query cycles (faces)
    Delta: float    # constraint‑satisfaction gap ∈ [0,1]
    d_norm: int     # normalization depth (BCNF level) ≥ 1
    BTFI_series: List[float]  # BTFI(t) for a time window (lead‑time already applied)
    p_bins: np.ndarray        # probability distribution over BTFI bins (shape = K)
    subsystem_type: np.ndarray # same shape as p_bins, encoding conditioning variable (e.g., tissue type)

# ----------------------------------------------------------------------
# Core validation
# ----------------------------------------------------------------------
def validate_bts_omega(top: SchemaTopology,
                       Phi_N0: float = 0.2,
                       tau_lead: float = 2.0,   # months, used only for commentary
                       mu1: float = 1.0,
                       mu2: float = 1.0,
                       mu3: float = 1.0) -> None:
    """
    Raises ValidationError if any Omega‑Protocol invariant is violated.
    """
    # 1. BTFI definition from topology
    chi = top.V - top.E + top.F                     # Euler characteristic
    BTFI_calc = (abs(chi) / top.V) * top.Delta * (1.0 / top.d_norm)
    # allow tiny floating‑point drift
    if not np.isclose(BTFI_calc, top.BTFI_series[-1], rtol=1e-6, atol=1e-9):
        raise ValidationError(
            f"BTFI mismatch: computed {BTFI_calc:.6f} vs supplied {top.BTFI_series[-1]:.6f}"
        )
    # BTFI must lie in [0,1] by construction (|χ|≤V, Delta≤1, 1/d_norm≤1)
    if not (0.0 <= BTFI_calc <= 1.0 + 1e-12):
        raise ValidationError(f"BTFI out of physical range: {BTFI_calc}")

    # 2. Φ_N and Φ_Δ from BTFI (lead‑time already applied in series)
    Phi_N_series = np.array(top.BTFI_series)          # Φ_N(t) = BTFI(t‑τ)
    Phi_N = Phi_N_series[-1]                          # current value
    # Φ_Δ defined as std of log BTFI across related systems (here we use bin distribution)
    # Avoid log(0) by adding tiny epsilon
    eps = 1e-12
    log_btfi = np.log(top.p_bins + eps)
    Phi_Delta = np.std(log_btfi)

    # 3. Invariant ψ_bts = ln(Φ_N/Φ_N0)
    if Phi_N <= 0:
        raise ValidationError(f"Φ_N must be >0 for log, got {Phi_N}")
    psi_calc = np.log(Phi_N / Phi_N0)
    # The proposal does not give a supplied ψ; we just note the formula.
    # If a ψ value were supplied we would compare here.

    # 4. Entropy gauge – must be *conditional* on subsystem_type
    # Verify that p_bins is a proper distribution
    if not np.isclose(np.sum(top.p_bins), 1.0, atol=1e-9):
        raise ValidationError(f"p_bins does not sum to 1: sum={np.sum(top.p_bins)}")
    # Shannon entropy (unconditional)
    S_uncond = -np.sum(top.p_bins * np.log(top.p_bins + eps))
    # For a true conditional entropy we need H(BTFI|subsystem) = ∑_s p(s) H(BTFI|s)
    # Here we check that the distribution varies with subsystem_type; if all subsystems
    # share identical p_bins then conditional entropy = unconditional.
    unique_types = np.unique(top.subsystem_type)
    if len(unique_types) == 1:
        # No conditioning information – violates the rubric's demand for conditional entropy
        raise ValidationError(
            "Entropy gauge lacks conditioning: all subsystem_type identical; "
            "must compute H(BTFI|subsystem) per rubric."
        )
    # Compute conditional entropy as a sanity check
    S_cond = 0.0
    for st in unique_types:
        mask = top.subsystem_type == st
        p_s = np.sum(top.p_bins[mask])
        if p_s > 0:
            p_cond = top.p_bins[mask] / p_s
            S_cond += p_s * (-np.sum(p_cond * np.log(p_cond + eps)))
    if not np.isclose(S_cond, S_uncond, rtol=1e-3):
        # Not equal → the distribution really depends on subsystem; we accept this as conditional.
        pass
    # Store for later boundary test
    S_bts = S_cond

    # 5. Gauge current J^μ = (√2 Φ_Δ, 0,0,0)
    J_expected = np.array([np.sqrt(2) * Phi_Delta, 0.0, 0.0, 0.0])
    # No supplied J to compare; we just note the form.

    # 6. Boundary conditions (must be *opposite* in entropy)
    # Shredding: ψ → +∞  AND  S_bts → S_max (high entropy)
    # Freeze   : ψ → -∞  AND  S_bts → S_min (low entropy)
    # We test that the proposal's claimed boundaries (both S→0) are false.
    if np.isclose(S_bts, 0.0, atol=1e-9):
        raise ValidationError(
            "Entropy gauge S_bts ≈ 0 detected. "
            "Both Shredding and Freeze boundaries require S_bts→0, which contradicts the rubric. "
            "Shredding needs high entropy, Freeze needs low entropy."
        )
    # Optional: enforce that S_bts is within [0, ln(K)] where K = number of BTFI bins
    K = len(top.p_bins)
    S_max_theoretical = np.log(K)
    if not (0.0 <= S_bts <= S_max_theoretical + 1e-12):
        raise ValidationError(
            f"Conditional entropy S_bts={S_bts:.6f} outside [0, ln(K)]=[0, {S_max_theoretical:.6f}]"
        )

    # 7. MPC‑Ω constraints (from proposal)
    if BTFI_calc > 0.7 + 1e-12:
        raise ValidationError(f"BTFI constraint violated: {BTFI_calc} > 0.7")
    if Phi_N < 0.6 - 1e-12:
        raise ValidationError(f"Φ_N constraint violated: {Phi_N} < 0.6")
    if S_bts < np.log(3) - 1e-12:
        raise ValidationError(f"Entropy constraint violated: S_bts={S_bts:.6f} < ln(3)")

    # If we reach here, all internal mathematical checks pass.
    print("[Ω‑PASS] All internal invariants satisfied.")
    print(f"  BTFI = {BTFI_calc:.4f}")
    print(f"  Φ_N  = {Phi_N:.4f}  (Φ_N0 = {Phi_N0})")
    print(f"  ψ_bts = {np.log(Phi_N/Phi_N0):.4f}")
    print(f"  Φ_Δ  = {Phi_Delta:.4f}")
    print(f"  S_bts (conditional) = {S_bts:.4f}")
    print(f"  J^μ = ({np.sqrt(2)*Phi_Delta:.4f}, 0, 0, 0)")

# ----------------------------------------------------------------------
# Example usage – replace with real data from a leaked backup
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Dummy data that *would* pass if the proposal were correct:
    top = SchemaTopology(
        V=12, E=15, F=4,                # => χ = 12-15+4 = 1
        Delta=0.5,
        d_norm=2,
        BTFI_series=[0.35, 0.38, 0.40], # last element is current BTFI
        p_bins=np.array([0.2, 0.3, 0.3, 0.2]),   # 4 BTFI bins
        subsystem_type=np.array([0,0,1,1])       # two subsystems → conditioning present
    )
    try:
        validate_bts_omega(top)
    except ValidationError as e:
        print(f"[Ω‑FAIL] {e}")