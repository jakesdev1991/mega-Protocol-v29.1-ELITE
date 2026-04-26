# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for BTS-Ω (Biological Topology Shield)
-----------------------------------------------------------------------
This script checks that a given biological system state satisfies:
  - Covariant-mode definitions from the double-well Hessian ansatz
  - BTFI definition and bounds
  - Entropy gauge (Shannon conditional entropy)
  - Boundary‑condition logic (shredding vs freeze)
  - MPC-Ω QP constraints and cost‑function direction
Replace the mock data with real extracted topology to validate a live system.
"""

import math
import numpy as np
from typing import Dict, List, Tuple

# ----------------------------------------------------------------------
# 1. Mock database‑topology extraction (replace with real parser)
# ----------------------------------------------------------------------
def extract_topology() -> Dict[str, float]:
    """
    Returns a dict with:
        V      : number of tables (vertices)
        E      : number of foreign‑key edges
        F      : number of independent query cycles (faces)
        delta  : constraint satisfaction gap (# enforced / # possible)
        d_norm : max BCNF level (normalization depth)
    """
    # Example numbers – adjust to match a real leaked backup
    return {
        "V": 12,          # tables
        "E": 18,          # foreign keys
        "F": 4,           # query cycles
        "delta": 0.55,    # 55% of possible biological constraints enforced
        "d_norm": 2.0     # max BCNF level = 2
    }

# ----------------------------------------------------------------------
# 2. Covariant-mode mapping from Hessian ansatz
# ----------------------------------------------------------------------
def compute_phi_n_phi_delta(topo: Dict[str, float],
                            kappa: Dict[str, float]) -> Tuple[float, float]:
    """
    Implements:
        ω_N^2 = κ1 * |χ|/V + κ2
        ω_Δ^2 = κ3 * Δ * (1/d_norm) + κ4
        Φ_N = sqrt(ω_N^2)
        Φ_Δ = sqrt(ω_Δ^2)
    """
    V, E, F = topo["V"], topo["E"], topo["F"]
    chi = V - E + F                     # Euler characteristic
    delta = topo["delta"]
    d_norm = topo["d_norm"]

    omega_N_sq = kappa["κ1"] * abs(chi) / V + kappa["κ2"]
    omega_D_sq = kappa["κ3"] * delta * (1.0 / d_norm) + kappa["κ4"]

    # Guard against negative (should not happen with calibrated κ)
    if omega_N_sq < 0 or omega_D_sq < 0:
        raise ValueError("Hessian‑ansatz produced negative curvature; check κ‑values.")
    phi_N = math.sqrt(omega_N_sq)
    phi_D = math.sqrt(omega_D_sq)
    return phi_N, phi_D, chi, delta, d_norm

# ----------------------------------------------------------------------
# 3. BTFI definition
# ----------------------------------------------------------------------
def compute_btfi(phi_N: float, phi_D: float, C_t: float = 1.0) -> float:
    """
    BTFI(t) = Φ_N(t) * Φ_Δ(t) * C(t)
    C(t) captures cross‑couplings; set to 1.0 for baseline.
    """
    return phi_N * phi_D * C_t

# ----------------------------------------------------------------------
# 4. Conditional entropy (Shannon) over subsystem types
# ----------------------------------------------------------------------
def conditional_entropy(subtype_probs: Dict[str, float],
                        btfi_histograms: Dict[str, List[float]]) -> float:
    """
    S = Σ_s p(s) [ - Σ_k p(k|s) log p(k|s) ]
    subtype_probs: prior probability of each biological subsystem type
    btfi_histograms: list of bin probabilities for BTFI within each type (must sum to 1)
    """
    S = 0.0
    for s, p_s in subtype_probs.items():
        hist = btfi_histograms.get(s, [])
        if not hist:
            continue
        # Normalize just in case
        hist = np.array(hist, dtype=float)
        hist /= hist.sum()
        inner = -np.sum(hist * np.log(hist + 1e-12))  # avoid log(0)
        S += p_s * inner
    return float(S)

# ----------------------------------------------------------------------
# 5. Invariant & QP constraint checks
# ----------------------------------------------------------------------
def validate_state(phi_N: float,
                   phi_D: float,
                   btfi: float,
                   psi: float,
                   S: float,
                   S_target: float,
                   bounds: Dict[str, Tuple[float, float]]) -> List[str]:
    """
    Returns a list of violated rule strings (empty if all pass).
    """
    violations = []

    # Covariant-mode positivity (implicit in sqrt)
    if phi_N <= 0 or phi_D <= 0:
        violations.append("Φ_N or Φ_Δ non‑positive (Hessian ansatz failed).")

    # BTFI bound from QP
    if btfi > bounds["BTFI"][1]:
        violations.append(f"BTFI = {btfi:.3f} exceeds upper bound {bounds['BTFI'][1]}.")

    # Φ_N lower bound (from QP: Φ_N ≥ 0.6)
    if phi_N < bounds["Phi_N"][0]:
        violations.append(f"Φ_N = {phi_N:.3f} below lower bound {bounds['Phi_N'][0]}.")

    # Entropy band
    if not (bounds["S"][0] <= S <= bounds["S"][1]):
        violations.append(f"Entropy S = {S:.3f} outside allowed range [{bounds['S'][0]}, {bounds['S'][1]}].")

    # Boundary‑condition logic (informal check)
    # Shredding: large Φ_N + high entropy → ψ should be large positive
    # Freeze:    small Φ_N + low entropy → ψ should be large negative
    if phi_N > 2.0 and S > 0.8 * bounds["S"][1] and psi < 0:
        violations.append("Shredding regime detected but ψ not positive (boundary condition mismatch).")
    if phi_N < 0.5 and S < 0.2 * bounds["S"][0] and psi > 0:
        violations.append("Freeze regime detected but ψ not negative (boundary condition mismatch).")

    return violations

# ----------------------------------------------------------------------
# 6. Main driver – plug in your calibrated constants and data
# ----------------------------------------------------------------------
def main():
    # ---- Calibration constants (to be fitted on historical leak data) ----
    kappa = {
        "κ1": 0.8,   # maps topological imbalance to curvature
        "κ2": 0.2,   # baseline stiffness
        "κ3": 0.6,   # maps constraint × inverse normalization to curvature
        "κ4": 0.1    # baseline constraint curvature
    }

    # ---- Extract topology from a leaked backup ----
    topo = extract_topology()
    print("Topology extracted:", topo)

    # ---- Compute covariant modes ----
    phi_N, phi_D, chi, delta, d_norm = compute_phi_n_phi_delta(topo, kappa)
    print(f"Φ_N = {phi_N:.4f}, Φ_Δ = {phi_D:.4f}")
    print(f"χ = {chi}, Δ = {delta:.3f}, d_norm = {d_norm:.2f}")

    # ---- BTFI (set cross‑coupling C=1 for now) ----
    btfi = compute_btfi(phi_N, phi_D, C_t=1.0)
    print(f"BTFI = {btfi:.4f}")

    # ---- Invariant ψ (needs a reference Φ_N^{(0)} for a robust network) ----
    Phi_N0 = 0.6   # reference value from the QP lower bound
    psi = math.log(phi_N / Phi_N0) if phi_N > 0 else float('-inf')
    print(f"ψ = ln(Φ_N/Φ_N0) = {psi:.4f}")

    # ---- Conditional entropy example ----
    # Suppose we have two subsystem types: genomic and proteomic
    subtype_probs = {"genomic": 0.6, "proteomic": 0.4}
    # BTFI histograms (3 bins: low, medium, high) for each type
    btfi_histograms = {
        "genomic":    [0.2, 0.5, 0.3],   # mostly medium BTFI
        "proteomic":  [0.4, 0.4, 0.2]    # split low/medium
    }
    S = conditional_entropy(subtype_probs, btfi_histograms)
    print(f"Conditional entropy S_bts = {S:.4f}")

    # ---- Define QP / invariant bounds ----
    bounds = {
        "BTFI":   (0.0, 0.7),   # BTFI ≤ 0.7
        "Phi_N":  (0.6, None),  # Φ_N ≥ 0.6
        "S":      (0.0, 1.5)    # placeholder entropy range; adjust from data
    }

    # ---- Run validation ----
    violations = validate_state(
        phi_N=phi_N,
        phi_D=phi_D,
        btfi=btfi,
        psi=psi,
        S=S,
        S_target=0.8,   # desired entropy set‑point (example)
        bounds=bounds
    )

    if violations:
        print("\n❌ VALIDATION FAILED – Violations:")
        for v in violations:
            print(" -", v)
    else:
        print("\n✅ ALL Ω‑PROTOCOL INVARIANTS AND QP CONSTRAINTS SATISFIED.")

if __name__ == "__main__":
    main()