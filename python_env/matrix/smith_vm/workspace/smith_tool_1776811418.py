# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Epistemic Attack Surface Shield (EASS-Ω) Validator
----------------------------------------------------------------
Validates the mathematical soundness of the EASS-Ω proposal and enforces
the Omega Protocol invariants (Phi_N, Phi_Delta, J*) via the MPC-Ω
constraints:
    EASI <= 0.7
    Phi_N_epist >= 0.4
    S_epist >= ln(3)
"""

import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, x))

def compute_easi(
    leak_severity: float,      # [0,10] -> map to [0,1]
    audience_soph: float,      # [0,10] -> map to [0,1]
    time_to_exploit: float,    # days
    response_time: float,      # hours -> convert to days
    coordination: float,       # [0,1]
) -> float:
    """
    EASI = (leak_severity/10) * (audience_soph/10) *
           (time_to_exploit / response_time) * (1 + coordination)
    All inputs are expected in their raw ranges; the function normalizes
    the first two factors to [0,1] and the time ratio is left as‑is.
    """
    leak_norm = clamp(leak_severity / 10.0, 0.0, 1.0)
    aud_norm  = clamp(audience_soph / 10.0, 0.0, 1.0)
    # Avoid division by zero; if response_time is 0, treat as infinite threat
    if response_time <= 0:
        time_ratio = float('inf')
    else:
        time_ratio = time_to_exploit / (response_time / 24.0)  # convert hrs→days
    return leak_norm * aud_norm * time_ratio * (1.0 + coordination)

def entropy_from_flow(flow_matrix: List[List[float]]) -> float:
    """
    Compute Shannon entropy S = - Σ p_ij log(p_ij)
    flow_matrix[i][j] = info_flow(i -> j)
    """
    total = sum(sum(row) for row in flow_matrix)
    if total == 0:
        return 0.0
    entropy = 0.0
    for row in flow_matrix:
        for f in row:
            if f > 0:
                p = f / total
                entropy -= p * math.log(p)
    return entropy

def update_phi(
    Phi_N0: float,
    Phi_Delta0: float,
    EASI_prev: float,
    entropy_barrier: float,
    info_asymmetry: float,
    eta: Tuple[float, float, float, float],
    tau: float = 1.0,
) -> Tuple[float, float]:
    """
    Linear update (with delay tau) as per the proposal:
        Phi_N(t)   = Phi_N0 - eta1 * EASI(t-tau) + eta2 * entropy_barrier(t-tau)
        Phi_Delta(t)= Phi_Delta0 + eta3 * info_asymmetry(t-tau) - eta4 * Phi_N(t-tau)
    For simplicity we use the *previous* timestep values as the delayed ones.
    """
    eta1, eta2, eta3, eta4 = eta
    Phi_N = Phi_N0 - eta1 * EASI_prev + eta2 * entropy_barrier
    Phi_Delta = Phi_Delta0 + eta3 * info_asymmetry - eta4 * Phi_N
    return Phi_N, Phi_Delta

def invariant_psi(Phi_N: float, Phi_N0: float) -> float:
    """ψ_epist = ln(Phi_N / Phi_N0) ; guard against non‑positive Phi_N."""
    if Phi_N <= 0:
        raise ValueError(f"Phi_N must be > 0 for log (got {Phi_N})")
    return math.log(Phi_N / Phi_N0)

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_eass_step(
    # Raw inputs (as would be supplied by monitoring)
    leak_severity: float,
    audience_soph: float,
    time_to_exploit: float,
    response_time: float,
    coordination: float,
    # Entropy flow matrix (agents x concepts)
    flow_matrix: List[List[float]],
    # Asymmetry measure (scalar, already normalized [0,1])
    info_asymmetry: float,
    # Entropy barrier from knowledge‑moat term (scalar, [0,1])
    entropy_barrier: float,
    # Baseline Omega parameters
    Phi_N0: float = 1.0,
    Phi_Delta0: float = 0.0,
    # Eta coefficients (tunable)
    eta: Tuple[float, float, float, float] = (0.2, 0.1, 0.15, 0.05),
    # Delay (hours) -> convert to same unit as EASI timestep; we assume 1‑step = 1 hour
    tau_hours: float = 4.0,
) -> None:
    """
    Perform one validation step. Raises AssertionError if any Omega invariant
    or MPC‑Ω constraint is violated.
    """
    # 1. Compute EASI (note: response_time in hours, time_to_exploit in days)
    easi = compute_easi(
        leak_severity, audience_soph,
        time_to_exploit, response_time,
        coordination,
    )
    # 2. Compute epistemic entropy
    S_epist = entropy_from_flow(flow_matrix)
    # 3. Update Phi_N, Phi_Delta using previous EASI (here we approximate
    #    previous EASI by the current one; in a real system you would keep a buffer.)
    Phi_N, Phi_Delta = update_phi(
        Phi_N0, Phi_Delta0,
        EASI_prev=easi,          # using current as proxy for t‑tau
        entropy_barrier=entropy_barrier,
        info_asymmetry=info_asymmetry,
        eta=eta,
        tau=tau_hours / 24.0,    # convert hours to days for consistency with EASI's time ratio
    )
    # 4. Compute invariant ψ
    psi = invariant_psi(Phi_N, Phi_N0)
    # 5. MPC‑Ω constraints
    assert easi <= 0.7 + 1e-9, f"EASI too high: {easi:.4f} > 0.7"
    assert Phi_N >= 0.4 - 1e-9, f"Phi_N too low: {Phi_N:.4f} < 0.4"
    assert S_epist >= math.log(3) - 1e-9, f"S_epist too low: {S_epist:.4f} < ln(3)"
    # 6. Optional: check that Phi_Delta remains non‑negative (physical meaning)
    assert Phi_Delta >= -1e-9, f"Phi_Delta negative: {Phi_Delta:.6f}"
    # If we reach here, all checks passed
    print(
        f"✓ Step passed | EASI={easi:.4f}, Φ_N={Phi_N:.4f}, Φ_Δ={Phi_Delta:.4f}, "
        f"S={S_epist:.4f}, ψ={psi:.4f}"
    )

# ----------------------------------------------------------------------
# Example usage (self‑test)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock data representing a mild leak scenario
    flow = [
        [0.1, 0.2, 0.0],
        [0.0, 0.1, 0.3],
        [0.2, 0.0, 0.1],
    ]
    try:
        validate_eass_step(
            leak_severity=3.0,        # moderate leak
            audience_soph=4.0,        # semi‑sophisticated audience
            time_to_exploit=2.0,      # 2 days to weaponize
            response_time=12.0,       # Omega can react in 12 hrs
            coordination=0.2,         # low coordination
            flow_matrix=flow,
            info_asymmetry=0.25,
            entropy_barrier=0.15,
            Phi_N0=1.0,
            Phi_Delta0=0.0,
            eta=(0.18, 0.12, 0.1, 0.04),
            tau_hours=6.0,
        )
    except AssertionError as ae:
        print("✗ Constraint violation:", ae)
    except ValueError as ve:
        print("✗ Mathematical error:", ve)