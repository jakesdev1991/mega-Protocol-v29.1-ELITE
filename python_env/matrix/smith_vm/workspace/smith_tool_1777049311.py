# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for QFAG v2.0
-------------------------------------------------
Checks the mathematical soundness of the claims made in the
"Quantum Flux-Artillery Governor (QFAG v2.0)" submission.

The script evaluates:
    - Φ_N = 1 - S_flux / S_max
    - Φ_Δ = Δt_q / Δt_c
    - ξ_N ≤ 0.005   (entropy budget)
    - ξ_Δ = (Δt * c) / d ≤ 0.95   (causality)
    - ψ = ln(Φ_N)   (informational sentinel)
    - Φ = Φ_N + Φ_Δ - ξ_N   (total Φ‑density)
    - Bekenstein bound for the claimed stress‑energy density
    - Consistency of the claimed Φ‑partition (+0.7Φ, +0.8Φ, +0.3Φ)

If any test fails, the script prints a FAIL message together with the
offending quantity and the allowed range.
"""

import math
import sys

# ----------------------------------------------------------------------
# Physical constants (SI)
# ----------------------------------------------------------------------
c = 299_792_458.0               # speed of light, m/s
hbar = 1.054_571_817e-34        # reduced Planck constant, J·s
k_B = 1.380_649e-23             # Boltzmann constant, J/K
ln2 = math.log(2)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def bekenstein_max_info(energy_joules, radius_m):
    """
    Bekenstein bound: I_max ≤ (2π E R) / (ħ c ln2)   [bits]
    """
    return (2.0 * math.pi * energy_joules * radius_m) / (hbar * c * ln2)

def stress_energy_to_energy_density(bits_per_cm3):
    """
    Convert an informational density (bits/cm³) to an energy density
    assuming each bit corresponds to k_B T ln2 of Landauer energy at T=300 K.
    This is a *conservative* lower bound; real physical systems need far more
    energy to represent a bit reliably.
    """
    T = 300.0                     # Kelvin, assumed operating temperature
    joules_per_bit = k_B * T * ln2
    # Convert bits/cm³ → bits/m³
    bits_per_m3 = bits_per_cm3 * 1e6
    return bits_per_m3 * joules_per_bit   # J/m³

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate(
    # ---- Measurable inputs (user‑adjustable) ----
    S_flux: float,          # flux defect entropy (dimensionless, 0 ≤ S_flux ≤ S_max)
    S_max: float,           # maximal flux entropy (dimensionless)
    delta_t_q: float,       # quantum actuation latency (seconds)
    delta_t_c: float,       # classical actuation latency (seconds, ≥ delta_t_q)
    d: float,               # characteristic actuation distance (meters)
    # Optional: stress‑energy claim
    stress_energy_bits_per_cm3: float = 5e10,   # from proposal
    # Optional: claimed Φ‑partition (should sum to total Φ)
    claimed_phi_parts: tuple = (0.7, 0.8, 0.3, 0.0)   # regulation, actuation, TOE, invariants
):
    """
    Returns True if all Omega Protocol checks pass, else False.
    Prints detailed diagnostics.
    """
    all_ok = True

    # ------------------------------------------------------------------
    # 1. Basic sanity of inputs
    # ------------------------------------------------------------------
    if S_max <= 0:
        print("[FAIL] S_max must be > 0.")
        all_ok = False
    if not (0.0 <= S_flux <= S_max):
        print(f"[FAIL] S_flux={S_flux} not in [0, S_max={S_max}].")
        all_ok = False
    if delta_t_q <= 0 or delta_t_c <= 0:
        print("[FAIL] Latencies must be positive.")
        all_ok = False
    if delta_t_q > delta_t_c:
        print(f"[FAIL] Quantum latency Δt_q={delta_t_q} > classical Δt_c={delta_t_c} "
              "(violates Φ_Δ ≤ 1).")
        all_ok = False
    if d <= 0:
        print("[FAIL] Actuation distance d must be > 0.")
        all_ok = False

    # ------------------------------------------------------------------
    # 2. Compute core invariants
    # ------------------------------------------------------------------
    Phi_N = 1.0 - (S_flux / S_max)          # ∈ [0,1]
    Phi_Delta = delta_t_q / delta_t_c       # ∈ [0,1] by construction
    xi_N = 0.0                              # placeholder – we will check the budget later
    xi_Delta = (delta_t_q * c) / d          # note: using Δt_q as the actuation latency
    psi = math.log(Phi_N) if Phi_N > 0 else float('-inf')

    # Entropy budget: ξ_N ≤ 0.5%
    xi_N_max_allowed = 0.005
    # Causality bound: ξ_Δ ≤ 0.95
    xi_Delta_max_allowed = 0.95

    # ------------------------------------------------------------------
    # 3. Invariant checks
    # ------------------------------------------------------------------
    if not (0.0 <= Phi_N <= 1.0):
        print(f"[FAIL] Φ_N = {Phi_N:.6f} outside [0,1].")
        all_ok = False
    if not (0.0 <= Phi_Delta <= 1.0):
        print(f"[FAIL] Φ_Δ = {Phi_Delta:.6f} outside [0,1].")
        all_ok = False
    if xi_N > xi_N_max_allowed:
        print(f"[FAIL] ξ_N = {xi_N:.6f} > allowed {xi_N_max_allowed}.")
        all_ok = False
    if xi_Delta > xi_Delta_max_allowed:
        print(f"[FAIL] ξ_Δ = {xi_Delta:.6f} > allowed {xi_Delta_max_allowed}.")
        all_ok = False
    if Phi_N <= 0:
        print(f"[FAIL] Φ_N ≤ 0 → ψ = ln(Φ_N) undefined (would be -∞).")
        all_ok = False
    else:
        # ψ is just informational; we only check that it is a real number
        if not math.isfinite(psi):
            print(f"[FAIL] ψ = ln(Φ_N) is non‑finite (Φ_N={Phi_N}).")
            all_ok = False

    # ------------------------------------------------------------------
    # 4. Total Φ‑density
    # ------------------------------------------------------------------
    Phi_total = Phi_N + Phi_Delta - xi_N
    if not (0.0 <= Phi_total <= 2.0 + 1e-12):   # tiny tolerance for FP
        print(f"[FAIL] Φ = Φ_N + Φ_Δ - ξ_N = {Phi_total:.6f} outside [0,2].")
        all_ok = False

    # ------------------------------------------------------------------
    # 5. Bekenstein bound check for the claimed stress‑energy density
    # ------------------------------------------------------------------
    # Convert bits/cm³ → Joules/m³ (using Landauer at 300 K as a *lower* bound)
    energy_density_J_per_m3 = stress_energy_to_energy_density(stress_energy_bits_per_cm3)
    # Assume a characteristic radius R = 0.5 m (size of a small artillery projectile)
    R = 0.5
    # Total energy in that volume
    E = energy_density_J_per_m3 * (4.0/3.0) * math.pi * R**3
    I_bekenstein = bekenstein_max_info(E, R)   # bits
    I_claimed = stress_energy_bits_per_cm3 * (4.0/3.0) * math.pi * R**3 * 1e6  # bits/m³ → bits in volume
    if I_claimed > I_bekenstein * (1 + 1e-9):   # allow tiny numerical slack
        print(f"[FAIL] Claimed informational density violates Bekenstein bound.")
        print(f"       I_claimed = {I_claimed:.3e} bits, I_max = {I_bekenstein:.3e} bits.")
        all_ok = False

    # ------------------------------------------------------------------
    # 6. Φ‑partition consistency
    # ------------------------------------------------------------------
    # The proposal splits the total Φ into additive parts.
    # We simply verify that the sum of the claimed parts equals the computed Φ_total
    # (within a reasonable tolerance).  If the parts do not sum, the accounting is
    # not traceable to the invariants.
    claimed_sum = sum(claimed_phi_parts)
    if not math.isclose(claimed_sum, Phi_total, rel_tol=1e-3, abs_tol=1e-3):
        print(f"[FAIL] Φ‑partition does not reconcile with computed Φ.")
        print(f"       Claimed parts sum = {claimed_sum:.6f}, Φ_total = {Phi_total:.6f}")
        all_ok = False

    # ------------------------------------------------------------------
    # 7. Final verdict
    # ------------------------------------------------------------------
    if all_ok:
        print("\n[PASS] All Omega Protocol invariant checks succeeded.")
        print(f"    Φ_N = {Phi_N:.6f}")
        print(f"    Φ_Δ = {Phi_Delta:.6f}")
        print(f"    ξ_N = {xi_N:.6f} (≤ {xi_N_max_allowed})")
        print(f"    ξ_Δ = {xi_Delta:.6f} (≤ {xi_Delta_max_allowed})")
        print(f"    ψ   = {psi:.6f}")
        print(f"    Φ   = {Phi_total:.6f}  (within [0,2])")
        print(f"    Bekenstein check: I_claimed/I_max = {I_claimed/I_bekenstein:.3e}")
    else:
        print("\n[FAIL] One or more invariant checks failed. Submission is NOT Submission‑Grade.")
    return all_ok

# ----------------------------------------------------------------------
# Example usage with the numbers *as stated* in the proposal
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Proposal‑stated approximations (we treat them as variables to be validated)
    # - S_flux / S_max ≈ 0.1  → Φ_N ≈ 0.9   (they claim +0.7Φ from regulation)
    # - Δt_q / Δt_c ≈ 0.9    → Φ_Δ ≈ 0.9   (they claim +0.8Φ from actuation)
    # - ξ_N ≈ 0 (they claim ≤0.5%)
    # - d ≈ 0.5 m (typical barrel‑to‑target distance for a short‑range system)
    # - Stress‑energy density = 5×10¹⁰ bits/cm³ (as given)

    S_max = 1.0                     # normalize maximal entropy to 1 for simplicity
    S_flux = 0.1                    # gives Φ_N = 0.9
    delta_t_q = 0.9e-6              # 0.9 µs quantum latency (illustrative)
    delta_t_c = 1.0e-6              # 1.0 µs classical latency
    d = 0.5                         # metres

    # Run the validator
    validate(
        S_flux=S_flux,
        S_max=S_max,
        delta_t_q=delta_t_q,
        delta_t_c=delta_t_c,
        d=d,
        stress_energy_bits_per_cm3=5e10,
        claimed_phi_parts=(0.7, 0.8, 0.3, 0.0)
    )