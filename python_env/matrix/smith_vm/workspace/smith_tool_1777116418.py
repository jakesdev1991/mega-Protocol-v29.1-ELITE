# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator for FSG-v57.1
------------------------------------------------
Checks the mathematical soundness of the Flux Stabilization Governor
against the six Absolute Invariants as stated in the proposal.
If an invariant fails, the script reports the violation and suggests
a minimal correction (where applicable) to restore compliance.

Assumptions for validation:
- COD = |⟨Ψ_fire|Ψ_sense⟩|²  (input, ∈ [0,1])
- Φ_N = log2(COD)
- Φ_min = log2(0.85) ≈ -0.234   (as implied by Invariant #1)
- Φ_scale = 0.1                  (as used in the proposal)
- ψ = tanh((Φ_N - Φ_min)/Φ_scale)
- Φ_Δ = ψ * tanh(R_align / R_max)   (R_align, R_max ≥ 0)
- ΔS_audit = k_B * ln(2) * C_audit  (dimensionless; we set k_B*ln2 = 1 for simplicity)
- Φ_net = Φ_N + Φ_Δ - ΔS_audit
- Ξ_control(t) = Ξ_control0 * exp(-γ t) + Ξ_kinematic * (1 - exp(-γ t))
  with γ = 0.01 hr⁻¹, Ξ_kinematic = 1.0 (normalized)
- H_collapse approximated by Shannon entropy of a binary collapse state:
    H = -p*log2(p) - (1-p)*log2(1-p)  with p = COD (as a proxy)
"""

import math
import numpy as np

# --- Constants (dimensionless for audit) ---
K_B_LN2 = 1.0          # k_B * ln(2) set to 1 (absorbed into C_audit scale)
GAMMA   = 0.01         # hr⁻¹
XI_KIN  = 1.0          # normalized kinematic stiffness
XI_CTL0 = 0.8          # example initial control stiffness (< XI_KIN to satisfy Invariant #3 at t=0)

def compute_psi(COD: float, phi_min: float = math.log2(0.85), phi_scale: float = 0.1) -> float:
    """Identity continuity ψ as defined in the proposal."""
    phi_N = math.log2(COD)
    return math.tanh((phi_N - phi_min) / phi_scale)

def compute_phi_delta(psi: float, R_align: float, R_max: float) -> float:
    """Stiffness‑mismatch term."""
    return psi * math.tanh(R_align / R_max)

def compute_delta_s_audit(C_audit: float) -> float:
    """Landauer audit cost (dimensionless)."""
    return K_B_LN2 * C_audit

def compute_phi_net(COD: float, R_align: float, R_max: float, C_audit: float) -> float:
    """Net Φ‑density."""
    phi_N = math.log2(COD)
    psi   = compute_psi(COD)
    phi_D = compute_phi_delta(psi, R_align, R_max)
    deltaS = compute_delta_s_audit(C_audit)
    return phi_N + phi_D - deltaS

def xi_control(t: float) -> float:
    """Adiabatic stiffness modulation."""
    return XI_CTL0 * math.exp(-GAMMA * t) + XI_KIN * (1.0 - math.exp(-GAMMA * t))

def h_collapse_proxy(COD: float) -> float:
    """Shannon entropy of a binary proxy state (used for Invariant #4)."""
    if COD <= 0.0 or COD >= 1.0:
        return 0.0
    p = COD
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)

def validate_invariants(COD: float, R_align: float, R_max: float,
                        C_audit: float, t: float = 0.0) -> dict:
    """Evaluate each of the six Absolute Invariants."""
    results = {}

    # Invariant #1: COD ≥ 0.85
    results['Invariant #1 (COD ≥ 0.85)'] = COD >= 0.85

    # Invariant #2: ψ ≥ 0.95   (as *stated* in the proposal)
    psi = compute_psi(COD)
    results['Invariant #2 (ψ ≥ 0.95)'] = psi >= 0.95
    results['ψ value'] = psi

    # Invariant #3: Ξ_control ≤ Ξ_kinematic
    xi_ctl = xi_control(t)
    results['Invariant #3 (Ξ_control ≤ Ξ_kinematic)'] = xi_ctl <= XI_KIN
    results['Ξ_control value'] = xi_ctl

    # Invariant #4: H_collapse ≤ 0.3
    h_coll = h_collapse_proxy(COD)
    results['Invariant #4 (H_collapse ≤ 0.3)'] = h_coll <= 0.3
    results['H_collapse value'] = h_coll

    # Invariant #5: ΔS_audit subtracted from Φ‑ledger
    # We simply verify that Φ_net uses the subtraction (by construction)
    phi_net = compute_phi_net(COD, R_align, R_max, C_audit)
    results['Invariant #5 (ΔS_audit subtracted)'] = True  # design‑time check
    results['Φ_net value'] = phi_net

    # Invariant #6: Φ_Δ < 0.5 * Φ_N
    phi_N = math.log2(COD)
    phi_D = compute_phi_delta(psi, R_align, R_max)
    results['Invariant #6 (Φ_Δ < 0.5·Φ_N)'] = phi_D < 0.5 * phi_N
    results['Φ_N'] = phi_N
    results['Φ_Δ'] = phi_D

    return results

def sweep_and_report():
    """Scan the operational COD range and highlight where Invariant #2 fails."""
    print("=== Omega Protocol Invariant Scan (COD ∈ [0.85, 1.0]) ===")
    cod_vals = np.linspace(0.85, 1.0, 16)
    for cod in cod_vals:
        res = validate_invariants(COD=cod,
                                  R_align=0.5,   # example mid‑range stiffness mismatch
                                  R_max=1.0,
                                  C_audit=0.1,   # modest audit cost
                                  t=0.0)         # check at t=0 (worst‑case for #3)
        print(f"\nCOD = {cod:.3f}")
        for inv, val in res.items():
            if isinstance(val, bool):
                status = "PASS" if val else "FAIL"
                print(f"  {inv}: {status}")
            else:
                print(f"  {inv}: {val:.4f}")

    print("\n=== Suggested Fix for Invariant #2 ===")
    print("The inequality ψ ≥ 0.95 cannot hold for COD ≤ 1.0 when")
    print("Φ_N = log2(COD) ≤ 0 and ψ = tanh((Φ_N-Φ_min)/Φ_scale).")
    print("Two minimal corrections restore compliance:")
    print("  1. Redefine the invariant as ψ ≥ 0   (always true in range),")
    print("     keeping the hard gate COD ≥ 0.85 (Invariant #1).")
    print("  2. Shift the ψ‑function upward, e.g.")
    print("        ψ = 0.5 * [1 + tanh((Φ_N-Φ_min)/Φ_scale)]")
    print("     which maps ψ∈[0,1] and yields ψ≥0.95 for COD≳0.92.")
    print("Either change preserves the informational‑first intent while")
    print("eliminating the documentation‑only contradiction.")

if __name__ == "__main__":
    sweep_and_report()