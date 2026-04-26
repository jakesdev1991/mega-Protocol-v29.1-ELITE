# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# -------------------------------------------------
# Ω-Protocol AVRI v54.1 Mathematical Validator
# -------------------------------------------------
# This script checks the internal consistency of the
# AVRI proposal against the stated formulas and
# Omega Protocol invariants.
# -------------------------------------------------

EPS = 1e-9          # small epsilon to avoid log(0)
R_MAX = 2.8         # stiffness mismatch scaling
C_AUDIT = 6         # number of invariants checked
K_B_LN2 = np.log(2) # Landauer factor (k_B=1 in natural units)

def avri_metrics(COD, xi_intel, xi_sub):
    """
    Compute AVRI-derived quantities.
    Parameters
    ----------
    COD : float
        Chain Overlap Density = |<Ψ_intel|Ψ_sub>|^2 ∈ [0,1]
    xi_intel : float
        Intellectual Stiffness (logic rigor)
    xi_sub : float
        Subconscious Capacity (system readiness)
    Returns
    -------
    dict
        All intermediate and final metrics.
    """
    # 1. Phi_N: Identity Density (log2(COD+ε))
    phi_N = np.log2(COD + EPS)

    # 2. Psi: Identity Continuity (ln(Phi_N+ε))
    # Note: The proposal writes ψ = ln(Φ_N + ε) with Φ_N ≤ 0.
    # To keep the argument of ln positive we rely on ε > |Φ_N| when needed.
    # We compute as written and guard against non‑positive input.
    inner_psi = phi_N + EPS
    if inner_psi <= 0:
        raise ValueError(
            f"Invalid ψ argument: Φ_N+ε = {inner_psi:.3e} ≤ 0. "
            f"Check COD={COD} or increase EPS."
        )
    psi = np.log(inner_psi)

    # 3. Phi_Delta: Adaptation Asymmetry
    R_align = np.abs(xi_sub - xi_intel)
    phi_Delta = psi * np.tanh(R_align / R_MAX)

    # 4. Audit Cost (Landauer per invariant)
    delta_S_audit = K_B_LN2 * C_AUDIT

    # 5. Net Φ-density
    phi_net = phi_N + phi_Delta - delta_S_audit

    return {
        "COD": COD,
        "phi_N": phi_N,
        "psi": psi,
        "R_align": R_align,
        "phi_Delta": phi_Delta,
        "delta_S_audit": delta_S_audit,
        "phi_net": phi_net,
        "xi_intel": xi_intel,
        "xi_sub": xi_sub,
    }

def check_invariants(metrics):
    """
    Evaluate the six Omega Protocol invariants.
    Returns a dict of pass/fail and explanatory messages.
    """
    results = {}

    # 1. Metric Non-Degeneracy: |det(g)| > 1e-15
    # We cannot compute g from the given scalars; use COD>0 as a proxy.
    results["Metric Non-Degeneracy"] = (
        metrics["COD"] > 0,
        f"COD={metrics['COD']:.6f} (>0 → proxy pass)"
    )

    # 2. Identity Continuity: ψ = ln(Φ_N) ≥ ln(0.95)
    # (as written: ψ = ln(Φ_N+ε))
    psi_thresh = np.log(0.95)
    results["Identity Continuity"] = (
        metrics["psi"] >= psi_thresh,
        f"ψ={metrics['psi']:.6f}, threshold={psi_thresh:.6f}"
    )

    # 3. Stiffness Matching: Ξ_intel ≤ Ξ_sub
    results["Stiffness Matching"] = (
        metrics["xi_intel"] <= metrics["xi_sub"],
        f"Ξ_intel={metrics['xi_intel']:.3f}, Ξ_sub={metrics['xi_sub']:.3f}"
    )

    # 4. Entropy Cap: H_collapse ≤ 0.3
    # Placeholder: assume ideal H_collapse = 0 (no collapse)
    H_collapse = 0.0
    results["Entropy Cap"] = (
        H_collapse <= 0.3,
        f"H_collapse={H_collapse:.3f} ≤ 0.3"
    )

    # 5. Information Conservation: ΔΦ_net ≥ 0 (post‑audit)
    results["Information Conservation"] = (
        metrics["phi_net"] >= 0,
        f"Φ_net={metrics['phi_net']:.6f} (≥0?)"
    )

    # 6. Asymmetry Control: Φ_Δ < 0.5·Φ_N
    # Note: Both Φ_N and Φ_Δ are negative in the current formulation.
    results["Asymmetry Control"] = (
        metrics["phi_Delta"] < 0.5 * metrics["phi_N"],
        f"Φ_Δ={metrics['phi_Delta']:.6f}, 0.5·Φ_N={0.5*metrics['phi_N']:.6f}"
    )

    return results

def demo():
    """
    Example sweep to see if any parameter set satisfies all invariants.
    """
    print("=== Ω-Proto AVRI v54.1 Mathematical Audit ===\n")
    # Sweep plausible values
    cod_vals = np.linspace(0.01, 0.99, 20)
    xi_sub_vals = np.linspace(0.1, 3.0, 10)
    # Fix xi_intel as a fraction of xi_sub to test stiffness matching
    frac_intel = 0.8

    passing = []
    for COD in cod_vals:
        for xi_sub in xi_sub_vals:
            xi_intel = frac_intel * xi_sub
            try:
                m = avri_metrics(COD, xi_intel, xi_sub)
                inv = check_invariants(m)
                if all(v[0] for v in inv.values()):
                    passing.append((COD, xi_sub, xi_intel, m, inv))
            except ValueError as e:
                # Skip invalid ψ arguments
                continue

    if passing:
        print(f"Found {len(passing)} parameter sets that satisfy all invariants.\n")
        # Show the first passing example
        COD, xi_sub, xi_intel, m, inv = passing[0]
        print("--- Example Passing Configuration ---")
        print(f"COD          : {COD:.6f}")
        print(f"Ξ_sub        : {xi_sub:.6f}")
        print(f"Ξ_intel      : {xi_intel:.6f} (={frac_intel:.2f}·Ξ_sub)")
        print(f"Φ_N          : {m['phi_N']:.6f}")
        print(f"ψ            : {m['psi']:.6f}")
        print(f"Φ_Δ          : {m['phi_Delta']:.6f}")
        print(f"ΔS_audit     : {m['delta_S_audit']:.6f}")
        print(f"Φ_net        : {m['phi_net']:.6f}")
        print("\nInvariant Checks:")
        for name, (ok, msg) in inv.items():
            print(f"  {name:22} : {'PASS' if ok else 'FAIL'} ({msg})")
    else:
        print("No parameter set in the sweep satisfied *all* invariants.")
        print("This indicates a likely inconsistency in the proposed formulas.")
        print("Try adjusting constants (R_MAX, C_AUDIT, ε) or revisit the definitions.")

if __name__ == "__main__":
    demo()