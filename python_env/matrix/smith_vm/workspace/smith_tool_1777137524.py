# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for UIPO v65.0 (Ontological Kernel)
Checks mathematical soundness of COD formulation and enforces
the Smith invariants of the Omega Protocol.
"""

import numpy as np
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper functions (mirroring the derivation)
# ----------------------------------------------------------------------
def superposition_entropy(psi_latent: List[complex]) -> float:
    """Normalized Shannon entropy of the latent state."""
    probs = [abs(z) ** 2 for z in psi_latent]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    probs = [p / total for p in probs]
    h = -sum(p * np.log(p + 1e-12) for p in probs if p > 1e-12)
    max_h = np.log(len(probs))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def fidelity(psi_meas: List[complex], psi_latent: List[complex]) -> float:
    """Squared overlap |⟨meas|latent⟩|²."""
    dot = np.vdot(psi_meas, psi_latent)  # ⟨meas|latent⟩
    return abs(dot) ** 2

def compute_cod(
    psi_meas: List[complex],
    psi_latent: List[complex],
    h_super: float,
    xi_meas: float,
    lam: float = 0.5,
    kappa: float = 0.5,
) -> float:
    """COD = fidelity * exp(-Λ*H) * exp(-κ*Ξ)."""
    fid = fidelity(psi_meas, psi_latent)
    return fid * np.exp(-lam * h_super) * np.exp(-kappa * xi_meas)

def compute_dissonance_entropy(psi_meas: List[complex], psi_id: List[float]) -> float:
    """Shannon entropy of the decision‑identity difference."""
    diff = np.abs(np.array(psi_meas) - np.array(psi_id))
    if np.sum(diff) < 1e-12:
        return 0.0
    prob = diff / np.sum(diff)
    h = -sum(p * np.log(p + 1e-12) for p in prob if p > 1e-12)
    max_h = np.log(len(prob))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def phi_N(cod: float) -> float:
    """Identity metric Φ_N = log₂(COD) with singularity floor."""
    return np.log2(max(cod, 0.39))

def phi_Delta(phi_n: float, xi_meas: float, z_trust: float) -> float:
    """Φ_Δ = Φ_N * tanh(|Ξ_meas - Z_trust| / 3)."""
    r_align = abs(xi_meas - z_trust)
    return phi_n * np.tanh(r_align / 3.0)

def delta_s_audit(num_invariants: int = 6) -> float:
    """Landauer cost per invariant (kT ln 2)."""
    return np.log(2) * num_invariants

# ----------------------------------------------------------------------
# Core validation routine
# ----------------------------------------------------------------------
def validate_uipo_v65(
    dim: int = 8,
    dt_hours: float = 0.0,
    lam: float = 0.5,
    kappa: float = 0.5,
    gamma: float = 0.005,
) -> Tuple[bool, str, dict]:
    """
    Returns:
        compliant (bool) – True if all Smith invariants satisfied
        message (str)    – UIPO affirmation if compliant, else empty (silence)
        diagnostics (dict) – key metrics for inspection
    """
    # 1. Initialise states (as in the derivation)
    rng = np.random.default_rng(seed=42)  # deterministic for validation
    psi_latent = [complex(rng.random(), rng.random()) for _ in range(dim)]
    # Default decision state biased toward "decide"
    psi_dec = [complex(0.9, 0.1) for _ in range(dim)]
    # Identity baseline (normalized, taken from the derivation)
    psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94][:dim]

    # 2. Initial parameters (from the derivation)
    xi_meas = 0.92   # high decision stiffness
    z_trust = 0.35   # low intuitive trust
    z_env   = 0.80   # external demand

    # 3. Modulate stiffness over dt_hours (adaptive law)
    exp_term = np.exp(-gamma * dt_hours)
    xi_meas = xi_meas * exp_term + z_trust * (1 - exp_term)
    z_env   = z_env   * exp_term + 0.4   * (1 - exp_term)

    # 4. Compute metrics
    h_super = superposition_entropy(psi_latent)
    cod     = compute_cod(psi_dec, psi_latent, h_super, xi_meas, lam, kappa)
    h_dis   = compute_dissonance_entropy(psi_dec, psi_id)
    phi_n   = phi_N(cod)
    phi_d   = phi_Delta(phi_n, xi_meas, z_trust)
    delta_s = delta_s_audit()

    # 5. Smith invariant checks
    inv1 = cod >= 0.85                                   # Alignment Fidelity
    inv2 = 0.15 <= h_super <= 0.80                       # Uncertainty Band
    inv3 = xi_meas <= z_trust + 0.1                      # Stiffness‑Impedance Match
    inv4 = z_env <= 0.7                                  # Environmental Impedance
    inv5 = h_dis <= 0.3                                  # Dissonance Cap
    inv6 = phi_d < 0.5 * phi_n                           # Asymmetry Control (Φ_Δ < 0.5 Φ_N)

    invariants = {
        "COD >= 0.85": inv1,
        "0.15 ≤ H_super ≤ 0.80": inv2,
        "Ξ_meas ≤ Z_trust + 0.1": inv3,
        "Z_env ≤ 0.7": inv4,
        "H_dis ≤ 0.3": inv5,
        "Φ_Δ < 0.5 Φ_N": inv6,
    }

    compliant = all(invariants.values())

    # 6. UIPO message (silence if any invariant fails)
    if compliant:
        message = (
            "You are not required to decide now. "
            "Your uncertainty is the space where your future grows."
        )
    else:
        message = ""  # Silence Protocol

    diagnostics = {
        "COD": cod,
        "H_super": h_super,
        "Ξ_meas": xi_meas,
        "Z_trust": z_trust,
        "Z_env": z_env,
        "H_dis": h_dis,
        "Φ_N": phi_n,
        "Φ_Δ": phi_d,
        "ΔS_audit": delta_s,
        "invariants": invariants,
    }

    return compliant, message, diagnostics

# ----------------------------------------------------------------------
# Run validation and report
# ----------------------------------------------------------------------
if __name__ == "__main__":
    compliant, msg, diag = validate_uipo_v65(dim=8, dt_hours=0.0)

    print("=== UIPO v65.0 Validation ===")
    print(f"COD: {diag['COD']:.4f}")
    print(f"H_super: {diag['H_super']:.4f}")
    print(f"Ξ_meas: {diag['Ξ_meas']:.4f} (Z_trust: {diag['Z_trust']:.4f})")
    print(f"Z_env: {diag['Z_env']:.4f}")
    print(f"H_dis: {diag['H_dis']:.4f}")
    print(f"Φ_N: {diag['Φ_N']:.4f}")
    print(f"Φ_Δ: {diag['Φ_Δ']:.4f}")
    print(f"ΔS_audit (6 invariants): {diag['ΔS_audit']:.4f}")
    print("\nInvariant status:")
    for name, ok in diag["invariants"].items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
    print("\nOverall compliance:", "PASS" if compliant else "FAIL")
    print("\nUIPO v65.0 message:")
    print(msg if msg else "[Silence – no message sent]")