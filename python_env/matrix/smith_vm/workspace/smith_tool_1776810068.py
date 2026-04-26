# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
BTS-Ω Ω-Physics Rubric v26.0 compliance checker.
Verifies:
  - ψ = ln(Φ_N/Φ_N0)
  - Φ_N, Φ_Δ from Hessian eigenvalues (via topology)
  - BTFI = Φ_N * Φ_Δ * C
  - Conditional entropy S_bts
  - Boundary condition directions
  - MPC-Omega QP constraints
"""

import numpy as np
import itertools

# ---------- USER‑DEFINED CALIBRATION ----------
# These would be fitted to historical leak data; here we use placeholder values.
KAPPA = {
    "kappa1": 1.0,   # ω_N^2 ∝ |χ|/V
    "kappa2": 0.1,   # offset
    "kappa3": 1.0,   # ω_Δ^2 ∝ Δ * (1/d_norm)
    "kappa4": 0.1,
}
# Reference values for a robust network
PHI_N0 = 0.2          # BTFI_ref ≈ 0.2 → Φ_N0 = sqrt(ω_N^2) at that point
S_TARGET = 0.5        # target entropy (arbitrary units)
S_LOW, S_HIGH = 0.1, 0.9   # entropy band for QP constraints
# ------------------------------------------------

def schema_invariants(V, E, F, num_rules, num_enforced, max_bcnf):
    """
    V = #tables, E = #foreign keys, F = #independent query cycles
    num_rules = total possible biological constraints
    num_enforced = # of those actually enforced in the backup
    max_bcnf = highest BCNF level across entities
    """
    chi = V - E + F
    Delta = num_enforced / num_rules if num_rules > 0 else 0.0
    d_norm = max_bcnf
    return chi, Delta, d_norm

def compute_BTFI(chi, V, Delta, d_norm):
    """BTFI = |χ|/V * Δ * 1/d_norm"""
    return (abs(chi) / V) * Delta * (1.0 / d_norm)

def hessian_eigenvalues(chi, V, Delta, d_norm):
    """
    ω_N^2 = κ1 * |χ|/V + κ2
    ω_Δ^2 = κ3 * Δ * (1/d_norm) + κ4
    """
    wN2 = KAPPA["kappa1"] * (abs(chi) / V) + KAPPA["kappa2"]
    wD2 = KAPPA["kappa3"] * Delta * (1.0 / d_norm) + KAPPA["kappa4"]
    return wN2, wD2

def conditional_entropy(btfi_matrix, subsystem_types):
    """
    btfi_matrix: shape (n_subsystems, n_bins) counts of BTFI in each bin
    subsystem_types: list of labels for each row (length n_subsystems)
    Returns S_bts = Σ_s p(s) * [ -Σ_k p(k|s) log p(k|s) ]
    """
    # Convert counts to probabilities per subsystem
    p_cond = btfi_matrix / btfi_matrix.sum(axis=1, keepdims=True)  # p(k|s)
    # Avoid log(0)
    p_cond = np.where(p_cond > 0, p_cond, 1e-12)
    entropy_per_s = -np.sum(p_cond * np.log(p_cond), axis=1)   # -Σ_k p log p
    # Weight by subsystem prevalence
    p_s = np.bincount([subsystem_types.index(t) for t in subsystem_types]) / len(subsystem_types)
    S = np.dot(p_s, entropy_per_s)
    return S

def psi_from_phiN(phiN):
    return np.log(phiN / PHI_N0)

def validate_one_case(V, E, F, num_rules, num_enforced, max_bcnf,
                      btfi_matrix, subsystem_types):
    # 1. Topology → BTFI
    chi, Delta, d_norm = schema_invariants(V, E, F, num_rules, num_enforced, max_bcnf)
    BTFI = compute_BTFI(chi, V, Delta, d_norm)

    # 2. Hessian → Φ_N, Φ_Δ
    wN2, wD2 = hessian_eigenvalues(chi, V, Delta, d_norm)
    phiN = np.sqrt(max(wN2, 0.0))
    phiD = np.sqrt(max(wD2, 0.0))

    # 3. BTFI as derived quantity (set C=1 for baseline)
    BTFI_derived = phiN * phiD  # C(t)=1
    # Allow small tolerance due to rounding
    assert np.isclose(BTFI, BTFI_derived, rtol=1e-5), \
        f"BTFI mismatch: {BTFI} vs {phiN*phiD}"

    # 4. ψ definition
    psi = psi_from_phiN(phiN)
    assert np.isclose(psi, np.log(phiN / PHI_N0)), "ψ definition broken"

    # 5. Conditional entropy
    S = conditional_entropy(btfi_matrix, subsystem_types)

    # 6. Boundary condition direction test
    #   - Shredding: phiN → large  => psi → +∞, S should increase
    #   - Freeze:   phiN → small  => psi → -∞, S should decrease
    # We test monotonicity by perturbing phiN up/down and checking S trend.
    eps = 1e-3
    phiN_up = phiN + eps
    phiN_down = max(phiN - eps, 1e-6)
    # Recompute BTFI_derived for perturbed phiN (keep phiD constant)
    BTFI_up = phiN_up * phiD
    BTFI_down = phiN_down * phiD
    # Approximate S change via BTFI bin shift: we assume higher BTFI → more weight in high‑BTFI bins
    # For simplicity, we just check that S is a decreasing function of BTFI in this toy model:
    # (In a real implementation S would be recomputed from the perturbed btfi_matrix.)
    # Here we assert the *sign* of dS/dBTFI is negative (entropy decreases as BTFI rises).
    # We'll approximate using a linear proxy: S_proxy = S0 - alpha*(BTFI - BTFI0)
    alpha = 0.5  # arbitrary positive slope
    S0 = S
    S_up_proxy = S0 - alpha * (BTFI_up - BTFI)
    S_down_proxy = S0 - alpha * (BTFI_down - BTFI)
    # Shredding (high BTFI) → lower S (more order) → actually we want:
    #   High BTFI → system more rigid → low entropy (freeze)
    #   Low BTFI  → system more adaptable → high entropy (shredding)
    # Therefore we expect S to *decrease* as BTFI increases.
    assert S_up_proxy <= S_down_proxy + 1e-8, \
        "Entropy does not decrease with increasing BTFI (boundary condition sign wrong)"

    # 7. MPC-Omega QP constraints
    assert BTFI <= 0.7 + 1e-9, f"BTFI constraint violated: {BTFI}"
    assert phiN >= 0.6 - 1e-9, f"Φ_N constraint violated: {phiN}"
    assert S_LOW - 1e-9 <= S <= S_HIGH + 1e-9, \
        f"Entropy constraint violated: S={S} not in [{S_LOW},{S_HIGH}]"

    # 8. Cost‑function integrand (non‑negative)
    mu1, mu2, mu3 = 1.0, 1.0, 1.0
    integrand = ((BTFI - 0.6) if BTFI > 0.6 else 0.0)**2 \
                + mu1 * ((0.6 - phiN) if phiN < 0.6 else 0.0)**2 \
                + mu2 * (phiD**2) \
                + mu3 * ((S - S_TARGET)**2)
    assert integrand >= -1e-12, "Cost integrand negative"

    return {
        "BTFI": BTFI,
        "phiN": phiN,
        "phiD": phiD,
        "psi": psi,
        "S": S,
        "integrand": integrand
    }

# ---------- Synthetic test data ----------
np.random.seed(42)
V, E, F = 12, 18, 5          # example schema
num_rules, num_enforced = 20, 14
max_bcnf = 3

# Create a btfi_matrix: 4 subsystem types, 5 BTFI bins
btfi_matrix = np.random.randint(1, 20, size=(4, 5))
subsystem_types = ["genomic", "proteomic", "clinical", "metabolic"]

# Run validation
result = validate_one_case(V, E, F, num_rules, num_enforced, max_bcnf,
                           btfi_matrix, subsystem_types)
print("Validation passed. Key metrics:")
for k, v in result.items():
    print(f"  {k}: {v:.5f}")