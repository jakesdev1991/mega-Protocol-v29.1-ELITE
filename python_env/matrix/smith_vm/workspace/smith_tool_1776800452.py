# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validator – Epistemic‑AI Pipeline Fragility Monitor (EAPFM‑Ω)
# --------------------------------------------------------------
# This script checks the mathematical soundness and invariant compliance
# of the EAPFM‑Ω proposal described in the audit.
#
# Invariants to verify (per Ω‑Physics Rubric v26.0):
#   1. Φ_N  (connectivity)   – must stay ≥ 0.6 (dimensionless)
#   2. Φ_Δ  (asymmetry)      – appears in gauge current J^μ
#   3. J^μ  (gauge current)  – must be J^μ = √2·Φ_Δ·δ^μ_0
#   4. ψ_epist (epistemic invariant) – defined as
#          ψ_epist = ln(|R_epist|/R0) + λ·EFI
#      No explicit bound is given, but the proposal ties
#      ψ_epist → ±∞ to Φ_Δ → ±∞ or 0 (boundary conditions).
#   5. EFI (Epistemic Fragility Index) – must satisfy EFI ≤ 0.70
#   6. S_data (data‑choice Shannon entropy) – must satisfy S_data ≥ ln(4)
#   7. The action term 𝒜_μ J^μ must be dimensionless.
#
# The validator receives a dictionary of sampled state variables and
# returns a compliance report.
# --------------------------------------------------------------

import math
from typing import Dict, Tuple, List

def validate_eapfm_omega(state: Dict[str, float],
                         lambda_: float = 1.0,
                         R0: float = 1.0) -> Tuple[bool, List[str]]:
    """
    Validate a single snapshot of the EAPFM‑Ω state against Omega Protocol invariants.

    Parameters
    ----------
    state : dict
        Required keys (all dimensionless after normalization):
        - 'Phi_N'   : Φ_N   (connectivity)
        - 'Phi_Delta': Φ_Δ   (asymmetry)
        - 'EFI'     : EFI   ∈ [0,1]
        - 'S_data'  : S_data (Shannon entropy of data sources)
        - 'R_epist' : |R_epist| (magnitude of Ricci curvature of Knowledge Field)
        - optional: 'gauge_mu_0' : value of 𝒜_μ for μ=0 (used to check dimensionless product)
    lambda_ : float
        Stiffness coefficient in ψ_epist definition (default 1.0).
    R0 : float
        Reference curvature scale (default 1.0).

    Returns
    -------
    (is_compliant, messages)
        is_compliant : bool – True if all checked invariants hold.
        messages     : list of str – human‑readable explanations of any violations.
    """
    msgs = []
    compliant = True

    # ----- 1. Φ_N connectivity invariant -----
    Phi_N = state.get('Phi_N')
    if Phi_N is None:
        msgs.append("Missing 'Phi_N' in state.")
        compliant = False
    elif Phi_N < 0.6:
        msgs.append(f"Φ_N = {Phi_N:.3f} < 0.6 (connectivity too low).")
        compliant = False
    else:
        msgs.append(f"Φ_N = {Phi_N:.3f} ✓ (≥ 0.6)")

    # ----- 2. Φ_Δ asymmetry (used in gauge current) -----
    Phi_Delta = state.get('Phi_Delta')
    if Phi_Delta is None:
        msgs.append("Missing 'Phi_Delta' in state.")
        compliant = False
    else:
        msgs.append(f"Φ_Δ = {Phi_Delta:.3f} ✓ (present)")

    # ----- 3. Gauge current J^μ = √2·Φ_Δ·δ^μ_0 -----
    # We only need to verify the temporal component J^0 = √2·Φ_Δ,
    # and that the product 𝒜_μ J^μ is dimensionless.
    # For dimensionlessness we require 𝒜_0 to have inverse dimension of J^0.
    # Since we work in normalized units, we simply check that
    # 𝒜_0 * J^0 yields a pure number (no units).
    gauge_A0 = state.get('gauge_mu_0')  # 𝒜_0 component
    if gauge_A0 is None:
        msgs.append("Missing 'gauge_mu_0' (𝒜_0) for gauge‑current dimensionless check.")
        compliant = False
    else:
        J0 = math.sqrt(2) * Phi_Delta if Phi_Delta is not None else float('nan')
        product = gauge_A0 * J0
        # In normalized units we expect product to be O(1); we accept any real number.
        msgs.append(f"J^0 = √2·Φ_Δ = {J0:.3f}")
        msgs.append(f"𝒜_0·J^0 = {product:.3f} (dimensionless check)")

    # ----- 4. EFI bound -----
    EFI = state.get('EFI')
    if EFI is None:
        msgs.append("Missing 'EFI' in state.")
        compliant = False
    elif not (0.0 <= EFI <= 1.0):
        msgs.append(f"EFI = {EFI:.3f} outside [0,1].")
        compliant = False
    elif EFI > 0.70:
        msgs.append(f"EFI = {EFI:.3f} > 0.70 (fragility threshold exceeded).")
        compliant = False
    else:
        msgs.append(f"EFI = {EFI:.3f} ✓ (≤ 0.70)")

    # ----- 5. Data‑choice entropy bound -----
    S_data = state.get('S_data')
    if S_data is None:
        msgs.append("Missing 'S_data' in state.")
        compliant = False
    elif S_data < math.log(4):
        msgs.append(f"S_data = {S_data:.3f} < ln(4) ≈ {math.log(4):.3f} (insufficient diversity).")
        compliant = False
    else:
        msgs.append(f"S_data = {S_data:.3f} ✓ (≥ ln(4))")

    # ----- 6. ψ_epist definition (no explicit bound, but we compute it) -----
    R_epist = state.get('R_epist')
    if R_epist is None:
        msgs.append("Missing 'R_epist' (|R_epist|) for ψ_epist.")
        compliant = False
    else:
        psi_epist = math.log(R_epist / R0) + lambda_ * EFI
        msgs.append(f"ψ_epist = ln(|R_epist|/R0) + λ·EFI = {psi_epist:.3f}")
        # Boundary‑as‑singularity check: if ψ_epist → ±∞ we expect Φ_Δ → ±∞ or 0.
        # We flag extreme values as a warning.
        if abs(psi_epist) > 10:
            msgs.append(f"⚠️  ψ_epist magnitude large ({psi_epist:.2f}); "
                        "approaching boundary singularity – verify Φ_Δ behavior.")

    # ----- 7. Cross‑check boundary conditions (optional) -----
    # According to the proposal:
    #   Epistemic Collapse: ψ_epist → +∞  AND Φ_Δ → +∞
    #   AI Orthodoxy:       ψ_epist → -∞  AND Φ_Δ → 0
    # We implement a simple proximity test.
    if psi_epist is not None and Phi_Delta is not None:
        collapse_cond = (psi_epist > 5) and (Phi_Delta > 5)
        orthodoxy_cond = (psi_epist < -5) and (abs(Phi_Delta) < 0.1)
        if collapse_cond:
            msgs.append("⚠️  State near Epistemic Collapse boundary (ψ_epist↑, Φ_Δ↑).")
        if orthodoxy_cond:
            msgs.append("⚠️  State near AI Orthodoxy boundary (ψ_epist↓, Φ_Δ→0).")

    # ----- Final summary -----
    if compliant:
        msgs.insert(0, "✅ All checked Omega Protocol invariants are satisfied.")
    else:
        msgs.insert(0, "❌ One or more Omega Protocol invariants violated.")

    return compliant, msgs


# ----------------------------------------------------------------------
# Example usage – simulate a few snapshots
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example 1: nominal healthy state
    healthy = {
        'Phi_N': 0.78,
        'Phi_Delta': 0.42,
        'EFI': 0.55,
        'S_data': math.log(5),   # > ln(4)
        'R_epist': 1.2,
        'gauge_mu_0': 0.5        # arbitrary 𝒜_0 in normalized units
    }
    ok, notes = validate_eapfm_omega(healthy)
    print("\n--- Healthy snapshot ---")
    for n in notes:
        print(n)

    # Example 2: violating EFI and entropy
    risky = {
        'Phi_N': 0.5,      # too low
        'Phi_Delta': 0.9,
        'EFI': 0.78,       # >0.70
        'S_data': math.log(2),  # < ln(4)
        'R_epist': 0.8,
        'gauge_mu_0': 0.3
    }
    ok, notes = validate_eapfm_omega(risky)
    print("\n--- Risky snapshot ---")
    for n in notes:
        print(n)

    # Example 3: near boundary (large ψ_epist)
    boundary = {
        'Phi_N': 0.65,
        'Phi_Delta': 6.0,   # large Φ_Δ
        'EFI': 0.6,
        'S_data': math.log(4.5),
        'R_epist': 50.0,    # → large curvature → large ψ_epist
        'gauge_mu_0': 0.2
    }
    ok, notes = validate_eapfm_omega(boundary)
    print("\n--- Boundary‑proximity snapshot ---")
    for n in notes:
        print(n)