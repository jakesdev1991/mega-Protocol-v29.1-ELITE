# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for COULN‑style proposal.

The script validates:
  - Φ-1 (Causal Fidelity): decision latency <= causal horizon.
  - Φ-2 (Entropy): ΔS <= +5% (Shannon entropy change).
  - Φ-3 (Topological Integrity): mesh homotopy-equivalent to S^3.
  - Internal consistency: COD definition, Ψ_id gate, Φ-net accounting.
"""

import math
from typing import Tuple

# ----------------------------------------------------------------------
# Constants (canonically set by the Omega Protocol)
# ----------------------------------------------------------------------
C = 1.0                     # causal speed (set to 1 in normalized units)
CAUSAL_HORIZON = 1.0        # maximal allowed decision time = C * Δt_spatial
# For a city-scale Δt_spatial ~ 1s, the horizon is ~1s. We'll use 1s as a safe bound.
MAX_PROCESSING_TIME = 0.2   # 200 ms as claimed in the proposal

ENTROPY_INCREASE_LIMIT = 0.05   # Φ-2: ΔS <= +5%
MIN_COD_INTUITIVE = 0.85        # COD > 0.85 => "intuitive, frictionless"
MIN_PSI_ID = 0.95               # Ψ_id hard gate

# Placeholder for Boltzmann constant (k) in natural units; we keep it symbolic.
K_LN2 = 1.0   # we treat k*ln2 as 1 for simplicity; scale audit_complexity accordingly.

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def check_phi1(processing_time: float) -> bool:
    """Φ-1: decision must not exceed causal horizon."""
    return processing_time <= MAX_PROCESSING_TIME

def check_phi2(H0: float, H_net: float) -> bool:
    """Φ-2: entropy increase must be <= +5%."""
    delta_S = H_net - H0
    return delta_S <= ENTROPY_INCREASE_LIMIT

def check_phi3(betti: Tuple[int, int, int, int]) -> bool:
    """
    Φ-3: Betti numbers must match S^3: (β0,β1,β2,β3) = (1,0,1,0).
    """
    expected = (1, 0, 1, 0)
    return betti == expected

def compute_cod(overlap_sq: float, H_sub: float, Xi_con: float,
                Lambda: float = 0.5, Gamma: float = 0.5) -> float:
    """
    COD = |⟨Ψ_sub|Ψ_con⟩|² * exp(-Λ*H_sub) * exp(-Γ*Ξ_con)
    overlap_sq should be |⟨Ψ_sub|Ψ_con⟩|² ∈ [0,1].
    """
    if not (0.0 <= overlap_sq <= 1.0):
        raise ValueError("overlap_sq must be in [0,1]")
    return overlap_sq * math.exp(-Lambda * H_sub) * math.exp(-Gamma * Xi_con)

def compute_phi_net(Phi_gain: float, H_sub: float, H_validation: float,
                    audit_complexity: float) -> float:
    """
    Φ_net = Φ_gain - 0.5*H_sub - 0.5*H_validation - (k ln2)*audit_complexity
    """
    return Phi_gain - 0.5 * H_sub - 0.5 * H_validation - K_LN2 * audit_complexity

def validate(
    processing_time: float,
    H0: float,
    H_net: float,
    betti: Tuple[int, int, int, int],
    overlap_sq: float,
    H_sub: float,
    Xi_con: float,
    Psi_id: float,
    Phi_gain: float,
    H_validation: float,
    audit_complexity: float,
    Lambda: float = 0.5,
    Gamma: float = 0.5
) -> None:
    """
    Run all checks; raise ValueError on first failure.
    """
    # Φ-1
    if not check_phi1(processing_time):
        raise ValueError(
            f"Φ-1 violation: processing_time={processing_time:.3f}s > {MAX_PROCESSING_TIME}s"
        )

    # Φ-2
    if not check_phi2(H0, H_net):
        raise ValueError(
            f"Φ-2 violation: H0={H0:.3f}, H_net={H_net:.3f}, ΔS={H_net-H0:.3f} > {ENTROPY_INCREASE_LIMIT}"
        )

    # Φ-3
    if not check_phi3(betti):
        raise ValueError(
            f"Φ-3 violation: Betti numbers {betti} != (1,0,1,0)"
        )

    # COD threshold (internal consistency, not an Omega invariant but part of the proposal)
    cod = compute_cod(overlap_sq, H_sub, Xi_con, Lambda, Gamma)
    if cod < MIN_COD_INTUITIVE:
        raise ValueError(
            f"COD too low for intuitive routing: COD={cod:.3f} < {MIN_COD_INTUITIVE}"
        )

    # Ψ_id gate (Q-Systemic Self invariant)
    if Psi_id < MIN_PSI_ID:
        raise ValueError(
            f"Ψ_id gate failed: Ψ_id={Psi_id:.3f} < {MIN_PSI_ID}"
        )

    # Φ-net accounting (just report; no invariant demands a specific sign)
    Phi_net = compute_phi_net(Phi_gain, H_sub, H_validation, audit_complexity)
    print(f"✓ All Omega Protocol invariants satisfied.")
    print(f"  COD = {cod:.3f} (>{MIN_COD_INTUITIVE} => intuitive routing)")
    print(f"  Ψ_id = {Psi_id:.3f} (>{MIN_PSI_ID} => identity preserved)")
    print(f"  Φ_gain = {Phi_gain:.3f}")
    print(f"  Φ_net  = {Phi_net:.3f}  (after entropy & audit penalties)")
    print(f"  Processing time = {processing_time*1000:.0f} ms (<={MAX_PROCESSING_TIME*1000:.0f} ms)")

# ----------------------------------------------------------------------
# Example usage with numbers taken from the proposal (or plausible values)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example inputs (feel free to adjust)
    processing_time = 0.15   # 150 ms < 200 ms
    H0 = 0.62                # baseline entropy
    H_net = 0.59             # after adaptive routing (decrease)
    betti = (1, 0, 1, 0)     # perfect S^3 topology
    overlap_sq = 0.90        # high quantum overlap
    H_sub = 0.45             # subconscious entropy (moderate)
    Xi_con = 0.30            # stiffness modulation (low when H_sub modest)
    Psi_id = 0.97            # identity preserved
    Phi_gain = 6.0           # raw gain before penalties
    H_validation = 0.10      # entropy from validation/audit
    audit_complexity = 1.2   # as stated in the proposal
    Lambda = 0.5
    Gamma = 0.5

    try:
        validate(
            processing_time=processing_time,
            H0=H0,
            H_net=H_net,
            betti=betti,
            overlap_sq=overlap_sq,
            H_sub=H_sub,
            Xi_con=Xi_con,
            Psi_id=Psi_id,
            Phi_gain=Phi_gain,
            H_validation=H_validation,
            audit_complexity=audit_complexity,
            Lambda=Lambda,
            Gamma=Gamma
        )
    except ValueError as e:
        print("❌ Validation failed:", e)