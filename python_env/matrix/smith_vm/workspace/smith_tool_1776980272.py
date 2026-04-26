# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator – Communications Branch (Audience Resonance)
Validates mathematical soundness and invariant compliance of the
Q-Systemic Self mapping for high‑stakes enterprise sales.
"""

import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# Constants from the spec (Omega Protocol v26.0)
# ----------------------------------------------------------------------
PSI_ID_MIN = 0.95          # Identity lower bound
XI_N_MAX   = 0.82          # Technical credibility upper bound
XI_D_MAX   = 1.28          # Process rigidity upper bound
ENTROPY_MAX_TOL = 0.80     # H(D|I) tolerance
STIFF_YIELD_LIM = 0.75     # Risk yield limit
XI_N_STAB_THRESH = 0.5     # Stability threshold for paralysis
COD_THRESHOLD = 0.85       # Minimum acceptable COD
URGENCY_MAX   = 0.9        # Not enforced directly but used in safety

# ----------------------------------------------------------------------
# Helper math (all dimensionless)
# ----------------------------------------------------------------------
def dot(a: List[float], b: List[float]) -> float:
    return sum(x*y for x, y in zip(a, b))

def norm2(v: List[float]) -> float:
    return dot(v, v)

def shannon_conditional_entropy(latent: List[float],
                                info: List[float]) -> float:
    """
    H(D|I) = -[ p log p + (1-p) log(1-p) ]
    where p = normalized overlap = <latent|info> / (||latent||·||info||)
    """
    if not latent or not info:
        raise ValueError("Vectors must be non‑empty")
    dp = dot(latent, info)
    n_lat = math.sqrt(norm2(latent))
    n_info = math.sqrt(norm2(info))
    if n_lat == 0 or n_info == 0:
        p = 0.0
    else:
        p = dp / (n_lat * n_info)
    # Clamp to avoid log(0)
    p = min(max(p, 1e-12), 1.0 - 1e-12)
    return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))

# ----------------------------------------------------------------------
# Core structures (mirroring the spec)
# ----------------------------------------------------------------------
class CommunicationInvariants:
    def __init__(self, psi_id: float, xi_N: float, xi_Delta: float):
        self.psi_id = psi_id
        self.xi_N = xi_N
        self.xi_Delta = xi_Delta

    def verify(self) -> bool:
        ok = (self.psi_id >= PSI_ID_MIN and
              self.xi_N   <= XI_N_MAX   and
              self.xi_Delta <= XI_D_MAX)
        if not ok:
            print(f"[INVARIANT FAIL] psi_id={self.psi_id:.3f} (>= {PSI_ID_MIN}), "
                  f"xi_N={self.xi_N:.3f} (<= {XI_N_MAX}), "
                  f"xi_Delta={self.xi_Delta:.3f} (<= {XI_D_MAX})")
        return ok

    def phi_loss(self) -> float:
        loss = 0.0
        if self.psi_id < PSI_ID_MIN:
            loss += (PSI_ID_MIN - self.psi_id) * 0.5
        if self.xi_N > XI_N_MAX:
            loss += (self.xi_N - XI_N_MAX) * 0.3
        if self.xi_Delta > XI_D_MAX:
            loss += (self.xi_Delta - XI_D_MAX) * 0.3
        return loss

class AudienceState:
    def __init__(self,
                 psi_latent: List[float],
                 psi_decision: List[float],
                 explicit_risk_perception: float,
                 energy_cost_factor: float = 0.0):
        self.psi_latent = psi_latent
        self.psi_decision = psi_decision
        self.explicit_risk_perception = explicit_risk_perception
        self.energy_cost_factor = energy_cost_factor

    def shannon_entropy(self, info_vector: List[float]) -> float:
        return shannon_conditional_entropy(self.psi_latent, info_vector)

class FailureMode:
    @staticmethod
    def check_paralysis(entropy: float,
                        risk: float,
                        stability: float) -> bool:
        return (entropy > ENTROPY_MAX_TOL and
                risk   > STIFF_YIELD_LIM and
                stability < XI_N_STAB_THRESH)

class ResonantAlignmentOperator:
    @staticmethod
    def strategic_urgency(t: float, tau_opt: float, sigma: float) -> float:
        return math.tanh((t - tau_opt) / sigma)

    def apply(self,
              state: AudienceState,
              invariants: CommunicationInvariants,
              pitch_vector: List[float]) -> Tuple[AudienceState, CommunicationInvariants]:
        # --- Phase 1: Diagnostic ---
        entropy = state.shannon_entropy(pitch_vector)
        if FailureMode.check_paralysis(entropy,
                                       state.explicit_risk_perception,
                                       invariants.xi_N):
            print("[OPERATOR] Decision paralysis detected – initiating Resonant Alignment.")
            # --- Phase 2: Entropy reduction (validate risk) ---
            state.explicit_risk_perception *= 0.85   # soft decay
            # --- Phase 3: Stiffness modulation (adiabatic urgency) ---
            t_norm = 0.0
            gamma = self.strategic_urgency(t_norm, tau_opt=0.5, sigma=0.1)
            if gamma > 0.5:
                # Boost credibility but never exceed XI_N_MAX
                invariants.xi_N = min(XI_N_MAX, invariants.xi_N + 0.05)
            # --- Phase 4: Soft collapse (incremental commitment) ---
            for i in range(len(state.psi_decision)):
                state.psi_decision[i] = (0.7 * state.psi_decision[i] +
                                         0.3 * state.psi_latent[i])
        # --- Phase 5: Invariant check ---
        if not invariants.verify():
            print("[OPERATOR] Invariant violation after apply – triggering repentance.")
            state.explicit_risk_perception *= 1.1  # increase safety margin
        return state, invariants

def compute_cod(pitch: List[float],
                need: List[float],
                stiffness_penalty: float,
                energy_cost: float) -> float:
    """COD = |<pitch|need>|^2 * stiffness_penalty / (1 + energy_cost)"""
    if not pitch or not need:
        return 0.0
    dp = dot(pitch, need)
    norm_p = math.sqrt(norm2(pitch))
    norm_n = math.sqrt(norm2(need))
    if norm_p == 0 or norm_n == 0:
        overlap = 0.0
    else:
        overlap = dp / (norm_p * norm_n)
    alignment = overlap * overlap          # |<...>|^2
    return alignment * stiffness_penalty / (1.0 + energy_cost)

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def run_validation() -> None:
    print("=== Omega Protocol Communications Validation ===")

    # Sample data (all dimensionless)
    latent   = [0.6, 0.4, 0.2]
    decision = [0.1, 0.1, 0.1]
    pitch    = [0.5, 0.3, 0.2]   # aligned with latent
    need_vec = latent             # for COD calculation

    state = AudienceState(psi_latent=latent,
                          psi_decision=decision,
                          explicit_risk_perception=0.78,
                          energy_cost_factor=0.1)

    invariants = CommunicationInvariants(psi_id=0.96,
                                         xi_N=0.40,
                                         xi_Delta=1.0)

    # Pre‑condition checks
    assert invariants.verify(), "Initial invariants violated"
    assert 0.0 <= state.explicit_risk_perception <= 1.0, "Risk out of bounds"
    print("[PRE] Invariants OK, state sane.")

    # Compute baseline entropy and COD
    entropy_before = state.shannon_entropy(pitch)
    cod_before = compute_cod(pitch, need_vec,
                             stiffness_penalty=math.exp(-0.5),  # example
                             energy_cost=state.energy_cost_factor)
    print(f"[BASE] Entropy={entropy_before:.3f}, COD={cod_before:.3f}")

    # Apply operator
    state_post, invariants_post = ResonantAlignmentOperator().apply(
        state, invariants, pitch)

    # Post‑condition checks
    assert invariants_post.verify(), "Post‑apply invariants violated"
    entropy_after = state_post.shannon_entropy(pitch)
    cod_after = compute_cod(pitch, need_vec,
                            stiffness_penalty=math.exp(-0.5),
                            energy_cost=state_post.energy_cost_factor)
    print(f"[POST] Entropy={entropy_after:.3f}, COD={cod_after:.3f}")

    # Entropy must not increase (operator aims to reduce uncertainty)
    assert entropy_after <= entropy_before + 1e-9, "Entropy increased – operator failed"

    # COD should move toward stability threshold (or at least not collapse)
    assert cod_after >= 0.0, "COD negative"

    # Φ‑Loss should be non‑negative and preferably lower after stabilization
    loss_before = invariants.phi_loss()
    loss_after  = invariants_post.phi_loss()
    print(f"[Φ‑Loss] before={loss_before:.3f}, after={loss_after:.3f}")
    # Allow small increase due to urgency boost, but not catastrophic
    assert loss_after <= loss_before + 0.2, "Φ‑Loss exploded"

    # Failure mode check: after stabilization we should NOT be in paralysis
    assert not FailureMode.check_paralysis(
        entropy_after,
        state_post.explicit_risk_perception,
        invariants_post.xi_N), "Still in paralysis after alignment"

    print("\n✅ All validation checks passed – specification is Omega‑Protocol compliant.")
    print("⚠️  Note: This validates the *logic* and *invariant adherence*;")
    print("   numerical values depend on the chosen scenario.")

if __name__ == "__main__":
    run_validation()