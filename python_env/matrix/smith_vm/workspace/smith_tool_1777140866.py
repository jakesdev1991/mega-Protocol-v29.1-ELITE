# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from typing import List, Tuple

def compute_superposition_entropy(psi_latent: List[complex]) -> float:
    """H_super = normalized Shannon entropy of latent amplitudes."""
    probs = [np.abs(z) ** 2 for z in psi_latent]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    probs = [p / total for p in probs]
    h = -sum(p * np.log(p + 1e-12) for p in probs if p > 1e-12)
    max_h = np.log(len(probs))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def compute_dissonance_entropy(psi_exp: List[complex], psi_id: List[float]) -> float:
    """H_dis = normalized Shannon entropy of |psi_exp - psi_id|."""
    diffs = [np.abs(c - i) for c, i in zip(psi_exp, psi_id)]
    s = sum(diffs)
    if s < 1e-12:
        return 0.0
    probs = [d / s for d in diffs]
    h = -sum(p * np.log(p + 1e-12) for p in probs if p > 1e-12)
    max_h = np.log(len(probs))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def compute_cod(
    psi_exp: List[complex],
    psi_latent: List[complex],
    psi_id: List[float],
    xi_valid: float,
    z_env: float,
    h_super: float,
    kappa: float = 0.5,
    lambd: float = 0.3,
    Lambda: float = 0.4,
) -> float:
    """
    COD_val = |<psi_exp|psi_latent>|^2 *
              exp(-kappa * xi_valid) *
              exp(-lambda * z_env) *
              exp(-Lambda * h_super)
    """
    # fidelity term
    dot = sum(np.conj(c) * l for c, l in zip(psi_exp, psi_latent))
    fidelity = np.abs(dot) ** 2

    # penalties
    stiffness_penalty = np.exp(-kappa * xi_valid)
    env_penalty = np.exp(-lambd * z_env)
    entropy_penalty = np.exp(-Lambda * h_super)

    cod_raw = fidelity * stiffness_penalty * env_penalty * entropy_penalty
    # enforce hard floor to avoid singularity in Phi_N
    return max(cod_raw, 0.39)

def compute_phi_N(cod: float) -> float:
    """Phi_N = log2(COD) with COD already floored at 0.39."""
    return np.log2(cod)

def compute_phi_Delta(phi_N: float, xi_valid: float, z_trust: float) -> float:
    """Phi_Delta = Phi_N * tanh((xi_valid - z_trust) / 3)."""
    return phi_N * np.tanh((xi_valid - z_trust) / 3.0)

def enforce_smith_invariants(
    cod: float,
    h_super: float,
    h_dis: float,
    xi_valid: float,
    z_trust: float,
    z_env: float,
    b1: float,
) -> Tuple[bool, List[str]]:
    """Return (pass, list_of_failed_invariants)."""
    failed = []
    # 1. Alignment Fidelity (actionable threshold)
    if cod < 0.85:
        failed.append("Invariant 1: COD < 0.85")
    # 2. Uncertainty Band
    if not (0.15 <= h_super <= 0.80):
        failed.append(f"Invariant 2: H_super = {h_super:.3f} outside [0.15,0.80]")
    # 3. Stiffness-Impedance Match
    if xi_valid > z_trust + 0.1:
        failed.append(f"Invariant 3: xi_valid ({xi_valid:.3f}) > z_trust+0.1 ({z_trust+0.1:.3f})")
    # 4. Environmental Impedance
    if z_env > 0.7:
        failed.append(f"Invariant 4: Z_env = {z_env:.3f} > 0.7")
    # 5. Dissonance Cap
    if h_dis > 0.3:
        failed.append(f"Invariant 5: H_dis = {h_dis:.3f} > 0.3")
    # 6. Silence Protocol / Rationalization Loop Guard
    if b1 > 0.8:
        failed.append(f"Invariant 6: b1 = {b1:.3f} > 0.8 (Rationalization Loop)")
    return (len(failed) == 0, failed)

def validate_state(
    psi_latent: List[complex],
    psi_exp: List[complex],
    psi_id: List[float],
    xi_valid: float,
    z_trust: float,
    z_env: float,
    b1: float,
) -> dict:
    """
    Full validation of a given agent state.
    Returns a dict with all computed quantities and validation outcome.
    """
    h_super = compute_superposition_entropy(psi_latent)
    h_dis = compute_dissonance_entropy(psi_exp, psi_id)
    cod = compute_cod(psi_exp, psi_latent, psi_id, xi_valid, z_env, h_super)
    phi_N = compute_phi_N(cod)
    phi_Delta = compute_phi_Delta(phi_N, xi_valid, z_trust)
    passed, failed_invariants = enforce_smith_invariants(
        cod, h_super, h_dis, xi_valid, z_trust, z_env, b1
    )

    return {
        "h_super": h_super,
        "h_dis": h_dis,
        "COD": cod,
        "Phi_N": phi_N,
        "Phi_Delta": phi_Delta,
        "smith_passed": passed,
        "failed_invariants": failed_invariants,
        "silence_protocol_triggered": not passed,  # True -> no message
    }

# ----------------------------------------------------------------------
# Example usage (you can replace these with any test case)
if __name__ == "__main__":
    # Example latent state (Truth, Belonging, Shame) – amplitudes arbitrary but normalized later inside functions
    psi_latent = [0.6+0.2j, 0.5-0.1j, 0.4+0.3j]
    # Explicit state (Logic, Evidence, Consistency) – start aligned with identity
    psi_exp = [0.7+0j, 0.6+0j, 0.5+0j]
    # Identity baseline (should be close to psi_exp for high COD)
    psi_id = [0.72, 0.58, 0.52]

    # Parameters taken from the proposal (typical values)
    xi_valid = 0.95   # initial validation stiffness
    z_trust = 0.40    # baseline self-trust
    z_env = 0.80      # high external pressure (will be modulated down)
    b1 = 0.85         # initial topological defect (rationalization loop)

    result = validate_state(
        psi_latent, psi_exp, psi_id, xi_valid, z_trust, z_env, b1
    )

    print("=== Validation Result ===")
    for k, v in result.items():
        if k != "failed_invariants":
            print(f"{k}: {v}")
    print("\nFailed Invariants:", result["failed_invariants"])
    print("\nSilence Protocol (no message) triggered?",
          result["silence_protocol_triggered"])