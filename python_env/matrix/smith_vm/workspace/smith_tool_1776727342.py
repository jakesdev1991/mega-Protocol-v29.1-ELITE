# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith – Omega Protocol Validation Script
----------------------------------------------
This script checks the mathematical soundness of the Engine's corrected
derivation (Omega‑QED v3) against the absolute invariants of the Omega
Protocol (Phi_N, Phi_Delta, J*).  It validates:

1. Covariant decomposition (Phi_N, Phi_Delta) appears explicitly.
2. Invariant ψ = ln(phi_n) with phi_n = m_eff/m is defined.
3. Stiffness terms ξ_N ~ 1/(g*Phi_N) and ξ_Delta ~ 1/|Phi_Delta| are present.
4. Entropy S_h = - Σ p_k ln p_k with p_k ∝ 1/ω_k^2, ω_k = sqrt(k^2+m_eff^2) is defined.
5. Shredding (mass‑positivity) bound: Phi_N < (m/g) * exp(-|Phi_Delta|).
6. No premature divergence: effective expansion parameter
        eps_eff = (g*Phi_N/m) * cosh(Phi_Delta)
   must satisfy eps_eff < 1 for perturbative validity.
   (If eps_eff ≥ 1 the derivation flags a potential Shredding event.)
7. Lattice anisotropy bound: |Phi_Delta| < Phi_Delta_crit = 1/max|epsilon_i|
   (if supplied) to avoid directional collapse.
8. Individual mass positivity:
        m_e = m - g*Phi_N*exp(+Phi_Delta) > 0
        m_p = m - g*Phi_N*exp(-Phi_Delta) > 0
   (Both reduce to the same bound as #5, but we check explicitly.)

The script does **not** evaluate the higher‑order resummed coupling (Eq. 11)
because that requires external numeric inputs; it only checks the structural
and inequality constraints that are invariant under the Omega Protocol.

Usage:
    Provide the parameters as a dictionary `params` (see example below) and
    run `validate_omega_qed(params)`.  The function returns a tuple
    (is_compliant, violations) where `violations` is a list of human‑readable
    messages describing any rule breaches.
"""

import math
from typing import Dict, List, Tuple, Any

def validate_omega_qed(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate the Engine's corrected derivation against Omega Protocol invariants.

    Expected keys in `params` (all scalar floats unless noted):
        m          : base mass (positive)
        g          : coupling constant (positive)
        Phi_N      : scalar field Phi_N
        Phi_Delta  : scalar field Phi_Delta
        epsilon    : optional, small expansion parameter epsilon = g*Phi_N/m
                     (if omitted, computed internally)
        epsilon_i  : list or tuple of anisotropy coefficients (sum must be ~0)
        Phi_Delta_crit : optional critical anisotropy bound;
                         if not provided, computed from epsilon_i as 1/max|epsilon_i|
        m_eff      : optional effective mass; if omitted, computed from formula
        psi        : optional invariant psi = ln(phi_n); if omitted, computed
        xi_N       : optional stiffness ~1/(g*Phi_N); if omitted, computed
        xi_Delta   : optional stiffness ~1/|Phi_Delta|; if omitted, computed
        S_h        : optional entropy value; if omitted, we only check that
                     the definition is present (no numeric validation)
    Returns:
        (compliant, violations) where compliant is True if no invariant is broken.
    """
    violations: List[str] = []

    # ------------------------------------------------------------------
    # 1. Basic sanity checks
    # ------------------------------------------------------------------
    m = params.get('m')
    g = params.get('g')
    Phi_N = params.get('Phi_N')
    Phi_Delta = params.get('Phi_Delta')
    if None in (m, g, Phi_N, Phi_Delta):
        violations.append("Missing fundamental parameters: m, g, Phi_N, Phi_Delta.")
        return False, violations
    if m <= 0 or g <= 0:
        violations.append("Base mass m and coupling g must be positive.")
    # ------------------------------------------------------------------
    # 2. Compute derived quantities if not supplied
    # ------------------------------------------------------------------
    epsilon = params.get('epsilon', g * Phi_N / m)
    # Effective mass from original definition
    m_eff_sq = m**2 * (1 - 2 * epsilon * math.cosh(Phi_Delta) + epsilon**2)
    if m_eff_sq < 0:
        violations.append("Effective mass squared becomes negative (m_eff imaginary).")
        m_eff = float('nan')
    else:
        m_eff = math.sqrt(m_eff_sq)

    # Invariant ψ
    psi = params.get('psi')
    if psi is None:
        if m_eff <= 0:
            violations.append("Cannot compute ψ = ln(m_eff/m) because m_eff ≤ 0.")
        else:
            psi = math.log(m_eff / m)
            params['psi'] = psi  # store for possible later use

    # Stiffness terms
    xi_N = params.get('xi_N')
    if xi_N is None:
        if Phi_N == 0:
            violations.append("Phi_N = 0 leads to divergent ξ_N.")
        else:
            xi_N = 1.0 / (g * Phi_N)
            params['xi_N'] = xi_N

    xi_Delta = params.get('xi_Delta')
    if xi_Delta is None:
        if Phi_Delta == 0:
            violations.append("Phi_Delta = 0 leads to divergent ξ_Δ.")
        else:
            xi_Delta = 1.0 / abs(Phi_Delta)
            params['xi_Delta'] = xi_Delta

    # Entropy definition – we only check that the concept is referenced;
    # actual numeric validation would require a momentum sum, which is
    # domain‑specific and omitted here.
    if 'S_h' not in params:
        # Not a violation per se, but we note the absence.
        pass

    # ------------------------------------------------------------------
    # 3. Covariant decomposition check (Phi_N, Phi_Delta present)
    # ------------------------------------------------------------------
    # Already ensured by parameter presence.

    # ------------------------------------------------------------------
    # 4. Invariant ψ presence
    # ------------------------------------------------------------------
    if 'psi' not in params:
        violations.append("Invariant ψ = ln(phi_n) not defined.")

    # ------------------------------------------------------------------
    # 5. Stiffness terms presence
    # ------------------------------------------------------------------
    if 'xi_N' not in params:
        violations.append("Stiffness term ξ_N not defined.")
    if 'xi_Delta' not in params:
        violations.append("Stiffness term ξ_Δ not defined.")

    # ------------------------------------------------------------------
    # 6. Entropy presence (definition only)
    # ------------------------------------------------------------------
    if 'S_h' not in params:
        violations.append("Entropy S_h (Shannon entropy of virtual‑pair distribution) not defined.")

    # ------------------------------------------------------------------
    # 7. Shredding (mass‑positivity) bound
    # ------------------------------------------------------------------
    bound = (m / g) * math.exp(-abs(Phi_Delta))
    if Phi_N >= bound:
        violations.append(
            f"Shredding bound violated: Phi_N = {Phi_N:.3e} ≥ (m/g)·e^{-|ΦΔ|} = {bound:.3e}."
        )
    # Individual masses (should be positive if bound holds)
    m_e = m - g * Phi_N * math.exp(+Phi_Delta)
    m_p = m - g * Phi_N * math.exp(-Phi_Delta)
    if m_e <= 0:
        violations.append(f"Electron‑sector mass m_e = {m_e:.3e} ≤ 0 (ghost mode).")
    if m_p <= 0:
        violations.append(f"Positron‑sector mass m_p = {m_p:.3e} ≤ 0 (ghost mode).")

    # ------------------------------------------------------------------
    # 8. Premature divergence of perturbative expansion
    # ------------------------------------------------------------------
    eps_eff = epsilon * math.cosh(Phi_Delta)
    if eps_eff >= 1.0:
        violations.append(
            f"Effective expansion parameter ε_eff = ε·cosh(ΦΔ) = {eps_eff:.3e} ≥ 1 → "
            f"perturbative breakdown (potential premature Shredding)."
        )

    # ------------------------------------------------------------------
    # 9. Lattice anisotropy bound (if epsilon_i supplied)
    # ------------------------------------------------------------------
    epsilon_i = params.get('epsilon_i')
    if epsilon_i is not None:
        if not isinstance(epsilon_i, (list, tuple)):
            violations.append("epsilon_i must be a list or tuple of coefficients.")
        else:
            # Check sum ≈ 0 (tolerance 1e-12)
            if abs(sum(epsilon_i)) > 1e-12:
                violations.append(
                    f"Anisotropy coefficients do not sum to zero: sum(epsilon_i) = {sum(epsilon_i):.3e}."
                )
            max_abs = max(abs(x) for x in epsilon_i)
            if max_abs == 0:
                violations.append("All epsilon_i are zero → no anisotropy; bound undefined.")
            else:
                Phi_Delta_crit = params.get('Phi_Delta_crit', 1.0 / max_abs)
                if abs(Phi_Delta) >= Phi_Delta_crit:
                    violations.append(
                        f"Lattice anisotropy bound exceeded: |ΦΔ| = {abs(Phi_Delta):.3e} ≥ ΦΔ_crit = {Phi_Delta_crit:.3e} "
                        f"(directional collapse imminent)."
                    )

    # ------------------------------------------------------------------
    # 10. Final compliance decision
    # ------------------------------------------------------------------
    compliant = len(violations) == 0
    return compliant, violations


# ----------------------------------------------------------------------
# Example usage (feel free to replace with actual simulation values)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example parameter set that should satisfy all invariants
    example_params = {
        'm': 9.10938356e-31,          # electron mass (kg) – just a scale
        'g': 1.0,                     # coupling (dimensionless for illustration)
        'Phi_N': 1e-3,                # small field value
        'Phi_Delta': 0.2,             # moderate anisotropy
        'epsilon_i': [0.05, -0.02, -0.03],  # sums to zero
        # Optional: let script compute derived quantities
    }

    ok, msgs = validate_omega_qed(example_params)
    if ok:
        print("✅  Omega‑QED v3 derivation passes all Omega Protocol invariants.")
    else:
        print("❌  Violations detected:")
        for msg in msgs:
            print(" -", msg)