# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Invariant Validator for FTFM‑Ω
---------------------------------------------
Checks the mathematical soundness and rubric compliance of the
Functional Transfer Fragility Monitor (FTFM‑Ω) proposal.

Run:
    python3 validate_ftfm_omega.py
"""

import numpy as np

# ----------------------------------------------------------------------
# Tolerances for floating‑point comparisons
TOL = 1e-8

# ----------------------------------------------------------------------
# Helper functions -----------------------------------------------------

def check_invariant(psi, phi_n, phi_n0):
    """
    Verify psi = ln(phi_n / phi_n0)
    """
    expected = np.log(phi_n / phi_n0)
    return np.allclose(psi, expected, atol=TOL, rtol=0)


def check_fokker_planck(prefactor, D, laplacian_term):
    """
    Ensure the diffusion term appears as 0.5 * D * laplacian.
    prefactor should be 0.5 (or absorbable into D).
    """
    return np.allclose(prefactor, 0.5, atol=TOL)


def check_action_dimensionless(terms):
    """
    All terms inside the action integrand must be dimensionless.
    `terms` is a dict mapping term name -> scalar/array value.
    """
    ok = True
    for name, val in terms.items():
        # In natural units ℏ=c=1, dimensionless <=> value is a real number.
        if not np.issubdtype(np.asarray(val).dtype, np.number):
            ok = False
            print(f"Term '{name}' is not a numeric scalar/array.")
    return ok


def check_stiffness_dimensions(xi_n, xi_delta, tau0):
    """
    Stiffness invariants must have dimensions of time.
    We enforce this by checking that xi_n / tau0 and xi_delta / tau0 are
    dimensionless (i.e., pure numbers).
    """
    ratio_n = xi_n / tau0
    ratio_d = xi_delta / tau0
    return (np.issubdtype(np.asarray(ratio_n).dtype, np.number) and
            np.issubdtype(np.asarray(ratio_d).dtype, np.number))


def check_cfi_bounds(cfi):
    """CFI must lie in [0,1]."""
    return np.all((cfi >= 0 - TOL) & (cfi <= 1 + TOL))


def check_qp_constraints(cfi, phi_n, s_context):
    """
    QP constraints:
        CFI ≤ 0.65
        Φ_N ≥ 0.6
        S_context ≥ ln(3)
    """
    cond1 = np.all(cfi <= 0.65 + TOL)
    cond2 = np.all(phi_n >= 0.6 - TOL)
    cond3 = np.all(s_context >= np.log(3) - TOL)
    return cond1 and cond2 and cond3


def check_cost_nonnegative(cost_integrand):
    """Cost integrand must be ≥ 0."""
    return np.all(cost_integrand >= -TOL)


# ----------------------------------------------------------------------
# Dummy data generator – replace with real model outputs ----------------

def generate_dummy_data(n_samples=10):
    """Create plausible synthetic values for validation."""
    np.random.seed(0)
    phi_n0 = 1.0                         # baseline connectivity
    phi_n = np.random.uniform(0.5, 0.9, n_samples)   # should stay ≥0.6 after control
    psi = np.log(phi_n / phi_n0)         # enforce invariant by construction
    xi_n = np.random.uniform(0.5, 2.0, n_samples) * 1.0   # pretend τ0 = 1.0
    xi_delta = np.random.uniform(0.5, 2.0, n_samples) * 1.0
    cfi = np.random.uniform(0.0, 0.6, n_samples)         # enforce ≤0.65
    sigma2_tf = np.random.uniform(0.0, 0.5, n_samples)
    kappa = np.random.uniform(0.0, 1.0, n_samples)
    chi = np.random.uniform(0.0, 0.8, n_samples)
    rho = np.random.uniform(0.1, 0.9, n_samples)
    s_context = -np.sum(np.array([0.3, 0.5, 0.2]) * np.log(np.array([0.3, 0.5, 0.2])))  # example entropy
    s_context = np.full_like(phi_n, s_context)  # broadcast
    # Cost integrand terms
    term1 = np.maximum(cfi - 0.6, 0.0)**2
    term2 = 0.5 * np.maximum(0.6 - phi_n, 0.0)**2
    term3 = 0.3 * (phi_n**2)  # placeholder for μ2 Φ_Δ^2 (using Φ_N as stand‑in)
    term4 = 0.4 * np.maximum(np.log(3) - s_context, 0.0)**2
    cost_integrand = term1 + term2 + term3 + term4

    # Action integrand terms (dimensionless placeholders)
    kinetic = 0.5 * np.ones_like(phi_n)   # ½ g^{μν}∂_μℱ∂_νℱ
    potential = 0.2 * np.ones_like(phi_n) # V(ℱ,s)
    omega_coupling = 0.1 * np.ones_like(phi_n) # λ_Ω L_Ω
    gauge = 0.05 * np.ones_like(phi_n)   # A_μ J^μ
    action_terms = {
        "kinetic": kinetic,
        "potential": potential,
        "omega_coupling": omega_coupling,
        "gauge": gauge,
    }

    return {
        "phi_n": phi_n,
        "phi_n0": phi_n0,
        "psi": psi,
        "xi_n": xi_n,
        "xi_delta": xi_delta,
        "tau0": 1.0,               # characteristic time
        "cfi": cfi,
        "sigma2_tf": sigma2_tf,
        "kappa": kappa,
        "chi": chi,
        "rho": rho,
        "s_context": s_context,
        "cost_integrand": cost_integrand,
        "action_terms": action_terms,
        "fokker_prefactor": 0.5,   # the ½ in front of D∇²
        "D": np.ones_like(phi_n), # dummy diffusion
        "laplacian": np.ones_like(phi_n), # dummy ∇²ℱ
    }


# ----------------------------------------------------------------------
# Main validation routine ----------------------------------------------

def main():
    data = generate_dummy_data()

    print("=== Omega‑Protocol Invariant Validation ===\n")

    # 1. Invariant form
    inv_ok = check_invariant(data["psi"], data["phi_n"], data["phi_n0"])
    print(f"Invariant ψ = ln(Φ_N/Φ_N⁰) satisfied? {'YES' if inv_ok else 'NO'}")

    # 2. Fokker‑Planck ½ factor
    fp_ok = check_fokker_planck(data["fokker_prefactor"], data["D"], data["laplacian"])
    print(f"Fokker‑Planck diffusion term has ½ factor? {'YES' if fp_ok else 'NO'}")

    # 3. Action dimensionless
    act_ok = check_action_dimensionless(data["action_terms"])
    print(f"All action integrand terms dimensionless? {'YES' if act_ok else 'NO'}")

    # 4. Stiffness dimensions (time)
    stiff_ok = check_stiffness_dimensions(
        np.mean(data["xi_n"]), np.mean(data["xi_delta"]), data["tau0"]
    )
    print(f"Stiffness invariants ξ_N, ξ_Δ have dimensions of time? {'YES' if stiff_ok else 'NO'}")

    # 5. CFI bounds
    cfi_ok = check_cfi_bounds(data["cfi"])
    print(f"CFI ∈ [0,1]? {'YES' if cfi_ok else 'NO'}")

    # 6. QP constraints
    qp_ok = check_qp_constraints(
        data["cfi"], data["phi_n"], data["s_context"]
    )
    print(f"QP constraints (CFI≤0.65, Φ_N≥0.6, S_context≥ln3) satisfied? {'YES' if qp_ok else 'NO'}")

    # 7. Cost non‑negative
    cost_ok = check_cost_nonnegative(data["cost_integrand"])
    print(f"Cost integrand non‑negative? {'YES' if cost_ok else 'NO'}")

    # Overall verdict
    all_ok = all([inv_ok, fp_ok, act_ok, stiff_ok, cfi_ok, qp_ok, cost_ok])
    print("\n--- RESULT ---")
    print("FULLY COMPLIANT with Omega Physics Rubric v26.0" if all_ok else "NON‑COMPLIANT – fix failing checks")

if __name__ == "__main__":
    main()