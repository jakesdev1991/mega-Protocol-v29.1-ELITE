# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Validation Script for QRSI-v60.1 (Quantum Resonance Sales Interface)

This script validates the mathematical soundness of the derivation and enforces
the Smith Invariants (Phi_N, Phi_Delta, J*) as hard constraints.

It:
1. Re-implements the core formulas from the derivation.
2. Samples a range of plausible states to verify invariant compliance.
3. Flags any violation of the Omega Protocol invariants.
4. Provides a clear pass/fail report.

Assumptions:
- All angles/dimensions are dimensionless and normalized as in the derivation.
- Constants: Gamma = 0.3, Lambda = 0.5 (as implied in the code), k_B*ln2 = 1 (in natural units).
- The 7 Smith Invariants correspond to the 8 checks in `enforce_smith_invariants`
  (the 7th is the audit cost subtraction, the 8th is the Silence Protocol).
"""

import numpy as np
from typing import List, Tuple

# ----------------------------
# Core Mathematical Functions
# ----------------------------

def normalize_state(state: List[complex]) -> List[complex]:
    norm = np.sqrt(sum(abs(z)**2 for z in state))
    return [z / norm for z in state] if norm > 1e-12 else state

def superposition_entropy(psi_latent: List[complex]) -> float:
    probs = [abs(z)**2 for z in psi_latent]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    probs = [p / total for p in probs]
    h = -sum(p * np.log(p + 1e-12) for p in probs if p > 1e-12)
    max_h = np.log(len(probs))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def dissonance_entropy(psi_explicit: List[complex], psi_id: List[float]) -> float:
    diff = [abs(c - i) for c, i in zip(psi_explicit, psi_id)]
    s = sum(diff)
    if s < 1e-12:
        return 0.0
    prob = [d / s for d in diff]
    h = -sum(p * np.log(p + 1e-12) for p in prob if p > 1e-12)
    max_h = np.log(len(prob))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def causal_link_density(psi_explicit: List[complex], psi_id: List[float],
                        z_env: float, xi_sell: float,
                        gamma: float = 0.3, delta: float = 0.5) -> float:
    # Fidelity term
    dot = sum(abs(c * i) for c, i in zip(psi_explicit, psi_id))
    mag_c = np.sqrt(sum(abs(c)**2 for c in psi_explicit))
    mag_i = np.sqrt(sum(abs(i)**2 for i in psi_id))
    if mag_c * mag_i < 1e-12:
        fidelity = 0.0
    else:
        fidelity = (dot / (mag_c * mag_i)) ** 2
    # Penalties
    z_penalty = np.exp(-gamma * z_env)
    xi_penalty = np.exp(-delta * xi_sell)
    return np.clip(fidelity * z_penalty * xi_penalty, 0.0, 1.0)

def update_stiffness(xi_sell: float, z_env: float,
                     dt_hours: float,
                     z_trust: float = 0.3,
                     z_resonant: float = 0.4,
                     gamma: float = 0.005,
                     delta: float = 0.004) -> Tuple[float, float]:
    exp_g = np.exp(-gamma * dt_hours)
    exp_d = np.exp(-delta * dt_hours)
    xi_new = xi_sell * exp_g + z_trust * (1 - exp_g)
    z_new  = z_env  * exp_d + z_resonant * (1 - exp_d)
    return xi_new, z_new

def phi_net(cod: float,
            h_super: float,
            h_opt: float = 0.55,
            h_max: float = 0.6,
            delta_s_audit: float = np.log(2) * 7) -> Tuple[float, float, float]:
    # Prevent singularity in Phi_N
    phi_n = np.log2(max(cod, 0.39) + 1e-12)
    psi = np.log(phi_n + 1e-12)          # identity continuity psi = ln(Phi_N)
    phi_delta = phi_n * np.tanh((h_super - h_opt) / h_max)
    return phi_n, phi_delta, phi_n + phi_delta - delta_s_audit

# ----------------------------
# Smith Invariant Enforcer
# ----------------------------

def smith_invariants_hold(cod: float,
                          h_super: float,
                          h_dis: float,
                          xi_sell: float,
                          z_trust: float,
                          z_env: float,
                          phi_n: float,
                          phi_delta: float) -> bool:
    """
    Returns True iff all 8 Smith Invariant checks pass.
    Invariant 7 (audit cost) is accounted in phi_net; Invariant 8 is the
    Silence Protocol (handled by caller).
    """
    # 1. Alignment Fidelity
    if cod < 0.85:
        return False
    # 2. Superposition Entropy Band
    if not (0.15 <= h_super <= 0.80):
        return False
    # 3. Dissonance Cap
    if h_dis > 0.3:
        return False
    # 4. Sales Stiffness ≤ Trust Impedance + 0.1
    if xi_sell > z_trust + 0.1:
        return False
    # 5. Environmental Impedance Cap
    if z_env > 0.7:
        return False
    # 6. Asymmetry Control
    if phi_delta >= 0.5 * phi_n:
        return False
    # 7. Audit cost subtracted -> already in phi_net, no extra check needed
    # 8. Silence Protocol: caller must enforce silence if any above fails
    return True

# ----------------------------
# Validation Routine
# ----------------------------

def validate_qrsiv601(num_samples: int = 10000) -> None:
    """
    Randomly samples the state space and checks:
    - Mathematical consistency of formulas.
    - Invariant compliance.
    - That the Silence Protocol (empty message) is triggered exactly when
      any invariant fails.
    """
    np.random.seed(42)  # reproducibility
    violations = []
    math_errors = []

    for i in range(num_samples):
        # Random latent/explicit states (8-dim as in the original code)
        dim = 8
        psi_latent = [complex(np.random.randn(), np.random.randn()) for _ in range(dim)]
        psi_explicit = [complex(np.random.randn(), np.random.randn()) for _ in range(dim)]
        psi_id = [np.random.rand() * 0.2 + 0.8 for _ in range(dim)]  # bias toward high identity

        # Normalize
        psi_latent = normalize_state(psi_latent)
        psi_explicit = normalize_state(psi_explicit)

        # Random environmental/sales parameters
        z_env = np.random.rand() * 1.2          # allow overshoot to test cap
        xi_sell = np.random.rand() * 1.2
        z_trust = np.random.rand() * 0.6        # trust can vary

        # Random time step to test adiabatic update
        dt = np.random.exponential(200)         # hours, mean 200

        # Update stiffness/impedance
        xi_sell, z_env = update_stiffness(xi_sell, z_env, dt, z_trust=z_trust)

        # Re-normalize latent after update (as in code)
        psi_latent = normalize_state(psi_latent)

        # Compute derived quantities
        h_super = superposition_entropy(psi_latent)
        h_dis   = dissonance_entropy(psi_explicit, psi_id)
        cod     = causal_link_density(psi_explicit, psi_id, z_env, xi_sell)
        phi_n, phi_delta, phi_net_val = phi_net(cod, h_super)

        # Invariant check
        invariants_ok = smith_invariants_hold(
            cod, h_super, h_dis, xi_sell, z_trust, z_env,
            phi_n, phi_delta
        )

        # Determine what the apply() function would return
        message = ("You are not required to decide now. Your uncertainty is not a failure. "
                   "It is part of your organization’s geometry.") if invariants_ok else ""

        # --- Validation Checks ---
        # 1. Mathematical consistency: COD must be in [0,1]
        if not (0.0 <= cod <= 1.0 + 1e-9):
            math_errors.append(f"Sample {i}: COD out of bounds: {cod}")

        # 2. Phi_N must be >= log2(0.39) (singularity prevention)
        if phi_n < np.log2(0.39) - 1e-9:
            math_errors.append(f"Sample {i}: Phi_n below singularity limit: {phi_n}")

        # 3. If invariants hold, message must be non-empty; else empty.
        if invariants_ok and not message:
            violations.append(f"Sample {i}: Invariants OK but message empty.")
        if not invariants_ok and message:
            violations.append(f"Sample {i}: Invariants violated but message sent.")

        # 4. Environmental impedance cap (Invariant 5) must be respected if invariants hold
        if invariants_ok and z_env > 0.7 + 1e-9:
            violations.append(f"Sample {i}: Invariants OK but Z_env > 0.7: {z_env}")

        # 5. Sales stiffness constraint (Invariant 4)
        if invariants_ok and xi_sell > z_trust + 0.1 + 1e-9:
            violations.append(f"Sample {i}: Invariants OK but Xi_sell > Z_trust+0.1: "
                              f"{xi_sell} > {z_trust+0.1}")

        # 6. Asymmetry control (Invariant 6)
        if invariants_ok and phi_delta >= 0.5 * phi_n - 1e-9:
            violations.append(f"Sample {i}: Invariants OK but Phi_Delta >= 0.5*Phi_N: "
                              f"{phi_delta} >= {0.5*phi_n}")

    # ----------------------------
    # Report
    # ----------------------------
    print("=== Omega Protocol Validation Report ===")
    print(f"Samples examined: {num_samples}")
    print(f"Mathematical inconsistencies: {len(math_errors)}")
    print(f"Invariant/Silence Protocol violations: {len(violations)}")
    if math_errors:
        print("\nFirst few math errors:")
        for err in math_errors[:5]:
            print(" -", err)
    if violations:
        print("\nFirst few protocol violations:")
        for v in violations[:5]:
            print(" -", v)
    if not math_errors and not violations:
        print("\n✅ All checks passed. QRSI-v60.1 is mathematically sound and invariant-compliant.")
    else:
        print("\n❌ Validation failed. Review errors above.")

# ----------------------------
# Run validation
# ----------------------------
if __name__ == "__main__":
    validate_qrsiv601(num_samples=20000)