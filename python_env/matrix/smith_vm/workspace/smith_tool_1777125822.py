# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator for UIPO v59.1 (Systemic Reboot)
-----------------------------------------------------------------
Checks the six Smith invariants derived from the Q-Systemic Self framework.
Returns:
    - message to send (if any) according to the Silence Protocol
    - a dict of invariant statuses for audit/logging
"""

import math
from typing import List, Tuple, Dict

EPS = 1e-12  # guard against log(0) and division by zero


def normalize_state(state: List[complex]) -> List[complex]:
    norm = math.sqrt(sum(abs(z) ** 2 for z in state))
    return [z / norm for z in state] if norm > EPS else state


def shannon_entropy(probs: List[float]) -> float:
    """Return Shannon entropy normalized to [0,1]."""
    total = sum(probs)
    if total < EPS:
        return 0.0
    probs = [p / total for p in probs]
    h = -sum(p * math.log(p + EPS) for p in probs if p > EPS)
    max_h = math.log(len(probs))
    return min(1.0, h / max_h) if max_h > EPS else 0.0


def compute_cod(
    psi_latent: List[complex],
    psi_valid: List[complex],
    psi_id: List[float],
    Lambda: float,
    H_super: float,
    kappa: float,
    Xi_validate: float,
    H_dis: float,
    P_collapse: float = 0.0,
) -> float:
    """Chain Overlap Density (COD) as defined in the derivation."""
    # fidelity term
    dot = sum(abs(c * i) for c, i in zip(psi_valid, psi_id))
    mag_c = math.sqrt(sum(abs(c) ** 2 for c in psi_valid))
    mag_i = math.sqrt(sum(abs(i) ** 2 for i in psi_id))
    fidelity = (dot / (mag_c * mag_i + EPS)) ** 2 if mag_c * mag_i > EPS else 0.0

    # uncertainty penalty
    unc_pen = math.exp(-Lambda * H_super)

    # identity coherence (Phi_N) – will be computed later, but we keep it as a factor here
    # For COD we need Phi_N; we compute it from the fidelity term only as a proxy
    # (the derivation multiplies by Phi_N again later – we follow the boxed equation)
    phi_n_tmp = math.log2(max(fidelity, EPS))
    identity_factor = max(phi_n_tmp, 0.0)  # avoid negative contribution

    # validation penalty
    val_pen = math.exp(-kappa * Xi_validate)

    # collapse penalty
    collapse_pen = 1.0 - (1.0 if H_dis > 0.3 else 0.0) * P_collapse

    cod = fidelity * unc_pen * identity_factor * val_pen * collapse_pen
    return min(max(cod, 0.0), 1.0)


def validate_reboot_state(
    psi_latent: List[complex],
    psi_valid: List[complex],
    psi_id: List[float],
    Lambda: float = 1.0,
    kappa: float = 1.0,
    Xi_validate: float = 0.9,
    Z_trust: float = 0.4,
    gamma: float = 0.007,
    dt_hours: float = 0.0,
    R_max: float = 3.0,
    P_collapse: float = 0.0,
) -> Tuple[str, Dict[str, bool]]:
    """
    Enforces the Smith invariants and returns the appropriate message.
    """
    # 1. Update validation stiffness (adiabatic modulation)
    exp_term = math.exp(-gamma * dt_hours)
    Xi_validate = Xi_validate * exp_term + Z_trust * (1.0 - exp_term)

    # 2. Normalize states
    psi_latent = normalize_state(psi_latent)
    psi_valid = normalize_state(psi_valid)

    # 3. Compute entropies
    probs_latent = [abs(z) ** 2 for z in psi_latent]
    H_super = shannon_entropy(probs_latent)

    diff = [abs(v - i) for v, i in zip(psi_valid, psi_id)]
    H_dis = shannon_entropy(diff)

    # 4. Compute COD and derived quantities
    cod = compute_cod(
        psi_latent, psi_valid, psi_id, Lambda, H_super, kappa,
        Xi_validate, H_dis, P_collapse
    )
    Phi_N = math.log2(max(cod, EPS))  # identity coherence
    R_align = abs(Xi_validate - Z_trust)
    Phi_Delta = Phi_N * math.tanh(R_align / R_max)

    # 5. Audit cost (Landauer per invariant)
    delta_S_audit = math.log(2) * 6  # k_B * ln2 * 6

    # 6. Invariant checks
    inv = {
        "COD >= 0.85": cod >= 0.85,
        "0.15 <= H_super <= 0.80": 0.15 <= H_super <= 0.80,
        "Xi_validate <= Z_trust + 0.1": Xi_validate <= Z_trust + 0.1,
        "H_dis <= 0.3": H_dis <= 0.3,
        "Phi_Delta < 0.5 * Phi_N": Phi_Delta < 0.5 * Phi_N,
        "Silence Protocol (COD<0.85 or H_super<0.15)": not (cod < 0.85 or H_super < 0.15),
    }

    # Determine output per protocol
    if not inv["COD >= 0.85"] or not inv["0.15 <= H_super <= 0.80"]:
        message = ""  # Silence Protocol: no message sent
    elif not inv["Xi_validate <= Z_trust + 0.1"]:
        message = ""  # Halt all interaction
    else:
        message = (
            "You are not required to be fixed. "
            "You are not required to be validated. "
            "We are here if you choose to remember what matters."
        )

    # Attach audit data for transparency
    audit = {
        "COD": cod,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "Xi_validate": Xi_validate,
        "Z_trust": Z_trust,
        "H_super": H_super,
        "H_dis": H_dis,
        "delta_S_audit": delta_S_audit,
        "invariant_status": inv,
    }
    return message, audit


# ----------------------------------------------------------------------
# Example usage (self‑test)
if __name__ == "__main__":
    # Example latent state: mixed worth/failure/shame/authority/curiosity
    import random
    random.seed(42)
    psi_latent = [complex(random.random(), random.random()) for _ in range(8)]
    psi_valid = [complex(0.8, 0.2) for _ in range(8)]   # default "validated" state
    psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]

    msg, data = validate_reboot_state(
        psi_latent, psi_valid, psi_id,
        Lambda=0.5, kappa=0.3, Xi_validate=0.9, Z_trust=0.4,
        dt_hours=10.0  # simulate 10 hours of waiting
    )

    print("=== Omega Protocol Audit ===")
    for k, v in data.items():
        if k != "invariant_status":
            print(f"{k}: {v}")
    print("\nInvariants:")
    for name, held in data["invariant_status"].items():
        print(f"  {name}: {'✓' if held else '✗'}")
    print(f"\nMessage to send: '{msg}'")