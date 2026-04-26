# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Audit: Q-Systemic Self (Psychology Branch)
Validates:
  - Invariant embodiment (ψ_id, ξ_bound) in the Hamiltonian
  - Entropy calculation (Shannon conditional entropy)
  - COD definition and range
  - AVP gamma(t) adiabatic shape (bounded, smooth)
  - Failure mode inequality
  - Φ‑density impact sign (entropy reduction → Φ increase)
  - Closed‑loop COD → γ(t) (optional, flagged if missing)
"""

import math
import cmath
from typing import Callable

# ----------------------------------------------------------------------
# Constants (as in the C++ code)
PSI_ID_COEFF = 1.0          # ψ_id  (not used in Hamiltonian – audit will flag)
XI_BOUND_DEFAULT = 1.0
XI_CRITICAL = 0.4

# ----------------------------------------------------------------------
# Helper: safe log for entropy
def safe_log(x: float) -> float:
    if x <= 0.0:
        return 0.0
    return math.log(x)

# ----------------------------------------------------------------------
# State representation (scalar complex numbers for simplicity)
Psi_exp: complex = 0.6 + 0.3j   # example experiential potential
Psi_intel: complex = 0.5 + 0.2j # example intellectual model
Psi_identity: complex = 1.0 + 0.0j  # fixed reference for ψ_id

# ----------------------------------------------------------------------
# 1. Hamiltonian energy (as implemented)
def compute_energy(t: float) -> float:
    """H_eff = H_exp + H_stiff + Gamma(t) - H_cond"""
    H_exp = 0.0                                          # baseline
    # Stiffness term (as coded): xi_bound * |<Ψ_exp|Ψ_intel>|
    H_stiff = XI_BOUND_DEFAULT * abs(Psi_exp.conjugate() * Psi_intel)
    Gamma_t = compute_gamma(t)                           # see below
    H_cond = compute_shannon_cond_entropy(Psi_exp, Psi_intel)
    return H_exp + H_stiff + Gamma_t - H_cond

# ----------------------------------------------------------------------
# 2. Gamma(t) – adiabatic validation protocol (time‑only)
def compute_gamma(t: float) -> float:
    tau_opt = 0.5
    sigma = 0.1
    return 1.0 * math.tanh((t - tau_opt) / sigma)

# ----------------------------------------------------------------------
# 3. Chain Overlap Density (COD)
def cod(exp: complex, intel: complex) -> float:
    num = abs(exp.conjugate() * intel)
    den = abs(exp) * abs(intel)
    if den == 0.0:
        return 0.0
    return (num / den) ** 2

# ----------------------------------------------------------------------
# 4. Shannon Conditional Entropy H(X|Y)  (binary success/failure model)
def compute_shannon_cond_entropy(exp: complex, intel: complex) -> float:
    p = abs(exp.conjugate() * intel)          # |⟨exp|intel⟩|
    if p > 1.0:
        p = 1.0
    if p == 0.0:
        return 0.0
    return -1.0 * p * safe_log(p)

# ----------------------------------------------------------------------
# 5. Failure mode detector
def failure_mode_risk(xi_bound: float, entropy_rate: float) -> bool:
    """Risk if xi_bound > 2 * entropy_rate"""
    return xi_bound > 2.0 * entropy_rate

# ----------------------------------------------------------------------
# 6. AVP operator – identity check (boolean) and adiabatic step
def avp_identity_ok(xi_current: float) -> bool:
    return xi_current >= XI_CRITICAL

def avp_apply(t: float, dt: float = 0.01) -> complex:
    """Euler step: |Ψ_intel> <- |Ψ_intel> - i * H_eff(t) * dt * |Ψ_intel>"""
    H = compute_energy(t)
    # Note: the C++ code added the term directly to Psi_intel (missing -i factor)
    # We follow the literal code: Psi_intel += (-1.0j * H * dt)
    return Psi_intel + (-1.0j * H * dt)

# ----------------------------------------------------------------------
# 7. Φ‑density ledger
def phi_density_impact(H_before: float, H_after: float) -> float:
    """ΔΦ = -(H_after - H_before) = H_before - H_after"""
    return -(H_after - H_before)

# ----------------------------------------------------------------------
# Audits / Assertions
def run_audit():
    print("=== Omega Protocol Audit ===")

    # ---- Invariant Embodiment ------------------------------------------------
    # ψ_id should appear in Hamiltonian; we check that the energy would change
    # if we varied ψ_id (by scaling Psi_identity). Since the code ignores it,
    # the derivative w.r.t. ψ_id is zero → violation.
    eps = 1e-6
    H0 = compute_energy(0.2)
    # Perturb identity direction
    global Psi_identity
    Psi_identity = complex(1.0 + eps, 0.0)
    H1 = compute_energy(0.2)
    Psi_identity = complex(1.0, 0.0)   # restore
    if abs(H1 - H0) > 1e-12:
        print("✓ ψ_id influences Hamiltonian")
    else:
        print("✗ ψ_id does NOT influence Hamiltonian (Invariant Embodiment FAIL)")

    # ξ_bound should appear as stiffness *|⟨Ψ_exp|Ψ_identity⟩|^2
    # Compute the term the code actually uses:
    H_stiff_code = XI_BOUND_DEFAULT * abs(Psi_exp.conjugate() * Psi_intel)
    # Compute the correct term:
    H_stiff_correct = XI_BOUND_DEFAULT * abs(Psi_exp.conjugate() * Psi_identity) ** 2
    if math.isclose(H_stiff_code, H_stiff_correct, rel_tol=1e-3):
        print("✓ Stiffness term matches prescribed form")
    else:
        print("✗ Stiffness term deviates from ξ_bound·|⟨Ψ_exp|Ψ_identity⟩|² (Invariant Embodiment FAIL)")

    # ---- Entropy Compliance --------------------------------------------------
    H_cond = compute_shannon_cond_entropy(Psi_exp, Psi_intel)
    assert 0.0 <= H_cond <= 1.0, "Entropy out of bounds"
    print(f"✓ Shannon conditional entropy = {H_cond:.5f} (in [0,1])")

    # ---- COD range -----------------------------------------------------------
    c = cod(Psi_exp, Psi_intel)
    assert 0.0 <= c <= 1.0, "COD out of [0,1]"
    print(f"✓ COD = {c:.5f} (in [0,1])")

    # ---- Gamma(t) adiabatic shape -------------------------------------------
    ts = [i * 0.05 for i in range(0, 21)]   # 0 .. 1.0
    gammas = [compute_gamma(t) for t in ts]
    # Gamma should be monotonic increasing and bounded [-1,1] (tanh)
    monotonic = all(gammas[i] <= gammas[i+1] + 1e-12 for i in range(len(gammas)-1))
    bounded = all(-1.0 <= g <= 1.0 for g in gammas)
    if monotonic and bounded:
        print("✓ Gamma(t) is monotonic and bounded (adiabatic shape OK)")
    else:
        print("✗ Gamma(t) fails monotonic/bounded test")

    # ---- Closed‑loop COD → Gamma (missing) -----------------------------------
    # We test whether gamma changes when COD changes (keeping t fixed)
    t_fixed = 0.5
    gamma_base = compute_gamma(t_fixed)
    # Perturb COD by rotating Psi_intel
    original_intel = Psi_intel
    Psi_intel = Psi_intel * cmath.exp(1j * 0.2)   # change overlap
    gamma_pert = compute_gamma(t_fixed)          # should be identical if no COD dependence
    Psi_intel = original_intel
    if math.isclose(gamma_base, gamma_pert, rel_tol=1e-12):
        print("✗ Gamma(t) does NOT depend on COD (closed‑loop missing)")
    else:
        print("✓ Gamma(t) varies with COD (closed‑loop present)")

    # ---- Failure mode inequality ---------------------------------------------
    # Choose an entropy_rate that makes the system safe/unsafe
    entropy_rate_safe = 0.2
    entropy_rate_risk = 0.6
    assert not failure_mode_risk(XI_BOUND_DEFAULT, entropy_rate_safe), "Safe state flagged as risk"
    assert failure_mode_risk(XI_BOUND_DEFAULT, entropy_rate_risk), "Risk state not detected"
    print("✓ Failure mode detector works as specified")

    # ---- AVP identity preservation -------------------------------------------
    assert avp_identity_ok(XI_BOUND_DEFAULT), "Identity stiffness below critical"
    # Apply one step and ensure the state remains normalized (approx)
    new_intel = avp_apply(0.3)
    norm_before = abs(Psi_intel)
    norm_after = abs(new_intel)
    # Expect norm change < 5% for a small dt
    assert abs(norm_after - norm_before) / norm_before < 0.05, "AVP step destabilizes norm"
    print("✓ AVP step preserves approximate normalization (identity check)")

    # ---- Φ‑density impact sign ------------------------------------------------
    H_before = compute_shannon_cond_entropy(Psi_exp, Psi_intel)
    # Simulate a small entropy reduction by aligning the vectors
    aligned_intel = Psi_exp * (abs(Psi_intel) / abs(Psi_exp))  # make them colinear
    H_after = compute_shannon_cond_entropy(Psi_exp, aligned_intel)
    delta_phi = phi_density_impact(H_before, H_after)
    # Since H_after <= H_before, delta_phi should be >= 0
    assert delta_phi >= -1e-12, "Φ‑density impact negative when entropy reduced"
    print(f"✓ Φ‑density impact = {delta_phi:.5f} (non‑negative for entropy reduction)")

    # ---- Net Φ‑density claim (not derivable from given code) ------------------
    print("\nNOTE: The claimed '+29% Φ‑Density' cannot be derived from the supplied")
    print("      equations; it would require a simulated trajectory and work accounting.")
    print("      Audit flags this as a missing derivation (Φ‑Density Traceability FAIL).")

    print("\n=== Audit Complete ===")

if __name__ == "__main__":
    run_audit()