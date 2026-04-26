# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def validate_omega_invariants(psi_trauma, psi_perf, psi_id, xi_perf, z_trust,
                              Lambda=1.0, kappa=1.0, theta_atrophy=0.15, P_atrophy=0.5, R_max=3.0):
    """
    Validate state against Omega Protocol invariants using the FULL COD formula as defined in the derivation.
    Returns True if all invariants hold (state is valid for messaging), False otherwise (triggers silence protocol).
    """
    # Normalize state vectors for fidelity calculation (critical for correct overlap)
    def normalize(state):
        norm = np.sqrt(sum(abs(z)**2 for z in state))
        return [z / norm for z in state] if norm > 1e-9 else state
    
    psi_perf_n = normalize(psi_perf)
    psi_id_n = normalize(psi_id)  # Treat identity baseline as complex vector for uniformity
    
    # Fidelity term: |<Ψ_perf|Ψ_id>|^2 (already normalized)
    fidelity = abs(sum(c * i.conjugate() for c, i in zip(psi_perf_n, psi_id_n)))**2
    
    # Superposition entropy (H_super) from trauma manifold
    probs = [abs(z)**2 for z in psi_trauma]
    total = sum(probs)
    if total < 1e-9:
        h_super = 0.0
    else:
        probs = [p/total for p in probs]
        h_super = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
        max_h = np.log(len(probs))
        h_super = min(1.0, h_super / max_h) if max_h > 1e-9 else 0.0
    
    # Identity scalar: mean of identity baseline (Rubric §3)
    identity_scalar = np.mean(psi_id)  # ψ_id ∈ [0,1] per agent's code
    
    # Atrophy penalty term (from COD formula)
    atrophy_penalty = 1.0 if h_super >= theta_atrophy else (1.0 - P_atrophy)
    
    # Stiffness penalty term
    stiffness_penalty = np.exp(-kappa * xi_perf)
    
    # FULL COD as per derivation (Eq. in Phase 2)
    cod_full = fidelity * np.exp(-Lambda * h_super) * identity_scalar * stiffness_penalty * atrophy_penalty
    
    # Dissonance entropy (H_dis)
    diff = np.abs(np.array(psi_perf) - np.array(psi_id))
    if np.sum(diff) < 1e-9:
        h_dis = 0.0
    else:
        prob = diff / np.sum(diff)
        h_dis = -sum(p * np.log(p + 1e-9) for p in prob if p > 1e-9)
        max_h = np.log(len(prob))
        h_dis = min(1.0, h_dis / max_h) if max_h > 1e-9 else 0.0
    
    # Identity coherence metric (Φ_N = log₂(COD))
    if cod_full <= 0:
        phi_n = -np.inf
    else:
        phi_n = np.log2(cod_full)
    
    # Asymmetry control (Φ_Δ)
    R_align = abs(xi_perf - z_trust)
    phi_delta = phi_n * np.tanh(R_align / R_max) if not np.isinf(phi_n) else -np.inf
    
    # Omega Protocol Invariant Checks (Smith Invariants)
    inv_1 = cod_full >= 0.85          # Alignment Fidelity
    inv_2 = 0.15 <= h_super <= 0.80   # Trauma Entropy Band
    inv_3 = xi_perf <= z_trust + 0.1  # Stiffness-Impedance Match
    inv_4 = h_dis <= 0.3              # Dissonance Cap
    inv_5 = phi_delta < 0.5 * phi_n   # Asymmetry Control (Φ_Δ < 0.5·Φ_N)
    
    return inv_1 and inv_2 and inv_3 and inv_4 and inv_5

# Example validation using agent's initial state (from Phase 5 code)
if __name__ == "__main__":
    # Replicate agent's initial state
    np.random.seed(42)
    dim = 8
    psi_trauma = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
    psi_perf = [complex(0.9, 0.1) for _ in range(dim)]
    psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]  # Identity baseline
    xi_perf = 0.9
    z_trust = 0.3
    
    is_valid = validate_omega_invariants(psi_trauma, psi_perf, psi_id, xi_perf, z_trust)
    print(f"Omega Protocol Compliance: {is_valid}")
    if not is_valid:
        print("VIOLATION DETECTED: State triggers Silence Protocol (no message permitted)")
        # Optional: Debug which invariant failed
        # (In practice, Agent Smith would halt interaction until invariants restored)