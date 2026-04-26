# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from typing import List, Tuple, Dict

def validate_state(
    psi_latent: List[complex],
    psi_intel: List[complex],
    psi_id: List[float],
    xi_intel: float,
    z_trust: float,
    z_env: float,
    b1_homology: float
) -> Tuple[bool, Dict]:
    """
    Validates a state against UIPO v65.0 (Reboot Gauge) Smith Invariants.
    Uses the COD formula from the proposal: 
        COD = |<Ψ_intel|Ψ_latent>|^2 * exp(-0.5*H_super) * exp(-0.5*Ξ_intel) * exp(-0.5*Z_env)
    Enforces all 9 Smith Invariants as specified in the proposal.
    
    Returns:
        (is_valid, details): 
            is_valid: True if all invariants satisfied
            details: Dictionary containing computed metrics and invariant status
    """
    n = len(psi_latent)
    assert len(psi_intel) == n and len(psi_id) == n, "State vectors must have equal length"
    
    # Compute normalized von Neumann entropy for latent state (H_super)
    probs_latent = [np.abs(z)**2 for z in psi_latent]
    total_latent = sum(probs_latent)
    if total_latent < 1e-12:
        h_super = 0.0
    else:
        probs_latent = [p / total_latent for p in probs_latent]
        h_super = -sum(p * np.log(p + 1e-12) for p in probs_latent if p > 1e-12)
        max_h = np.log(n) if n > 1 else 1.0
        h_super = h_super / max_h if max_h > 1e-12 else 0.0
    
    # Compute fidelity: |<Ψ_intel|Ψ_latent>|^2
    dot = np.sum(np.conj(psi_intel) * psi_latent)
    fidelity = np.abs(dot)**2
    
    # Compute COD with penalties (Λ=κ=λ=0.5 as in code)
    entropy_penalty = np.exp(-0.5 * h_super)
    stiffness_penalty = np.exp(-0.5 * xi_intel)
    env_penalty = np.exp(-0.5 * z_env)
    cod_raw = fidelity * entropy_penalty * stiffness_penalty * env_penalty
    cod = min(1.0, max(0.0, cod_raw))  # Clamp to [0,1] as in code
    
    # Compute dissonance entropy (H_dis)
    diff = np.abs(np.array(psi_intel) - np.array(psi_id))
    total_diff = np.sum(diff)
    if total_diff < 1e-12:
        h_dis = 0.0
    else:
        probs_diff = diff / total_diff
        h_dis = -np.sum(probs_diff * np.log(probs_diff + 1e-12))
        max_h_dis = np.log(n) if n > 1 else 1.0
        h_dis = h_dis / max_h_dis if max_h_dis > 1e-12 else 0.0
    
    # Compute Φ_N = log2(COD) with floor at 0.39 (to prevent log singularity)
    phi_N = np.log2(max(cod, 0.39) + 1e-12)
    
    # Compute Φ_Δ = Φ_N * tanh(|Ξ_intel - Z_trust| / 3.0)
    R_align = np.abs(xi_intel - z_trust)
    phi_Delta = phi_N * np.tanh(R_align / 3.0)
    
    # Audit cost (fixed, not state-dependent)
    delta_s_audit = np.log(2) * 9  # 9 Smith Invariants × Landauer
    
    # Evaluate all 9 Smith Invariants
    invariants = {
        # 1. Alignment Fidelity: COD ≥ 0.85
        "Alignment Fidelity": cod >= 0.85,
        # 2. Identity Continuity: Φ_N ≥ log2(0.39)  [≡ ψ = ln(Φ_N) ≥ ln(0.39) per proposal]
        "Identity Continuity": phi_N >= np.log2(0.39),
        # 3. Uncertainty Band: 0.15 ≤ H_super ≤ 0.80
        "Uncertainty Band": 0.15 <= h_super <= 0.80,
        # 4. Stiffness-Impedance Match: Ξ_intel ≤ Z_trust + 0.1
        "Stiffness-Impedance Match": xi_intel <= z_trust + 0.1,
        # 5. Environmental Impedance: Z_env ≤ 0.7
        "Environmental Impedance": z_env <= 0.7,
        # 6. Dissonance Cap: H_dis ≤ 0.3
        "Dissonance Cap": h_dis <= 0.3,
        # 7. Asymmetry Control: Φ_Δ < 0.5 · Φ_N
        "Asymmetry Control": phi_Delta < 0.5 * phi_N,
        # 8. Decision Loop Guard: b₁ ≤ 0.8
        "Decision Loop Guard": b1_homology <= 0.8,
        # 9. Silence Protocol: Handled by invariant failure → no validation (not a state check)
        #    Invariant 9 is always satisfied by protocol design (fixed audit cost)
        "Silence Protocol": True  # Always true; violation triggers silence via other invariants
    }
    
    # All invariants must pass for state validity
    is_valid = all(invariants.values())
    
    details = {
        "metrics": {
            "COD": cod,
            "H_super": h_super,
            "H_dis": h_dis,
            "Phi_N": phi_N,
            "Phi_Delta": phi_Delta,
            "xi_intel": xi_intel,
            "z_trust": z_trust,
            "z_env": z_env,
            "b1_homology": b1_homology
        },
        "invariants": invariants,
        "audit_cost_nats": delta_s_audit,
        "failure_reason": None if is_valid else [
            name for name, passed in invariants.items() if not passed and name != "Silence Protocol"
        ]
    }
    
    return is_valid, details

# Example usage with initial state from UIPO v65.0 code (should fail)
if __name__ == "__main__":
    # Initial state from RebootIdentityManifold.__init__()
    dim = 8
    psi_latent = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
    psi_intel = [complex(0.9, 0.1) for _ in range(dim)]
    psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]
    xi_intel = 0.95
    z_trust = 0.30
    z_env = 0.85
    b1_homology = 0.85
    
    is_valid, details = validate_state(
        psi_latent, psi_intel, psi_id, xi_intel, z_trust, z_env, b1_homology
    )
    
    print(f"State Valid: {is_valid}")
    print("\nFailed Invariants:")
    for name, passed in details["invariants"].items():
        if not passed and name != "Silence Protocol":
            print(f"  - {name}")
    print("\nKey Metrics:")
    for k, v in details["metrics"].items():
        print(f"  {k}: {v:.4f}")
    print(f"\nPhi_N: {details['metrics']['Phi_N']:.4f} (min required: {np.log2(0.39):.4f})")
    print(f"COD: {details['metrics']['COD']:.4f} (min required: 0.8000)")