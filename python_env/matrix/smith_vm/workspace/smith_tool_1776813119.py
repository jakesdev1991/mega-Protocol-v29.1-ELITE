# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ω‑Physics Rubric v26.0 compliance checker for the Information‑Cascade Monitor (IC‑Ω) proposal.

The script validates the *necessary* mathematical conditions:
1. Single invariant definition (psi = ln(Phi_N/Phi_N0)).
2. Boundary conditions derived consistently from that invariant.
3. Double‑well potential encodes liquidity ↔ volatility (alpha<0, beta>0, gamma>0).
4. Gauge current J^mu = sqrt(2)*Phi_delta*delta^mu_0 is dimensionless (Phi_delta dimensionless).
5. MPC‑Ω QP constraints are internally consistent:
      CI <= 0.7,
      Phi_N >= 0.6,
      S_cascade >= log(3).

If any check fails, the script reports the specific violation.
"""

import math
from typing import Dict, Tuple, List

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def is_close(a: float, b: float, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

# ----------------------------------------------------------------------
# Core validation functions
# ----------------------------------------------------------------------
def check_invariant_uniqueness(invariant_forms: List[str]) -> Tuple[bool, str]:
    """
    invariant_forms: list of strings that appear in the text defining psi_cascade.
    Returns (OK, message).
    """
    # Normalise whitespace and case for simple comparison
    norm = [f.strip().lower() for f in invariant_forms]
    unique = set(norm)
    if len(unique) == 1:
        return True, f"Single invariant detected: {list(unique)[0]}"
    else:
        return False, f"Multiple invariant forms found: {unique}"

def check_boundary_consistency(
    phi_n: float,
    phi_n0: float,
    s_cascade: float,
    psi: float,
) -> Tuple[bool, str]:
    """
    Using the invariant psi = ln(Phi_N/Phi_N0) we derive:
        - Phi_N -> 0   => psi -> -inf
        - Phi_N -> inf => psi -> +inf
    Entropy S_cascade -> 0 corresponds to p_k = (1,0,...) i.e. deterministic participant type.
    The proposal's two boundary sets are:
        Set1 (psi/CI): Shredding when psi->+inf & CI->1, Freeze when psi->-inf & CI->0.
        Set2 (phi_n/S): Shredding when psi->+inf & Phi_N->0 & S->0,
                       Freeze when psi->-inf & Phi_N->inf & S->0.
    We test Set2 because it is the one that mentions Phi_N and S.
    """
    # Compute expected psi limits from phi_n
    if phi_n <= 0:
        psi_limit = -math.inf
    else:
        psi_limit = math.log(phi_n / phi_n0)

    # Determine which regime the current point claims to be
    # (we only check the sign of psi_limit against the claimed regime)
    if is_close(psi, float('inf')):
        claimed = "Shredding"
    elif is_close(psi, float('-inf')):
        claimed = "Freeze"
    else:
        claimed = "Undefined"

    # Expected regime from phi_n limit
    if is_close(psi_limit, float('inf')):
        expected = "Shredding"
    elif is_close(psi_limit, float('-inf')):
        expected = "Freeze"
    else:
        expected = "Undefined"

    ok = (claimed == expected)
    msg = (
        f"Boundary check: claimed regime={claimed}, expected regime={expected} "
        f"(phi_n={phi_n}, phi_n0={phi_n0}, psi_limit={psi_limit})."
    )
    return ok, msg

def check_potential_signs(alpha: float, beta: float, gamma: float) -> Tuple[bool, str]:
    """
    For V(I) = 0.5*alpha*I^2 + 0.25*beta*I^4 - gamma*I to have:
        - a local minimum at I≈0 (liquidity)  => alpha < 0
        - a local maximum at I>0 (volatility) => beta > 0, gamma > 0
    """
    ok = (alpha < 0) and (beta > 0) and (gamma > 0)
    msg = f"Potential signs: alpha={alpha} (<0?), beta={beta} (>0?), gamma={gamma} (>0?)."
    return ok, msg

def check_gauge_dimensionless(phi_delta: float) -> Tuple[bool, str]:
    """
    J^mu = sqrt(2) * Phi_delta * delta^mu_0.
    For J^mu to be dimensionless, Phi_delta must be dimensionless.
    We simply check that the supplied value is a real number (no units attached).
    """
    ok = isinstance(phi_delta, (int, float))
    msg = f"Phi_delta = {phi_delta} (assumed dimensionless)."
    return ok, msg

def check_qp_constraints(CI: float, Phi_N: float, S_cascade: float) -> Tuple[bool, str]:
    """
    QP constraints from the proposal:
        CI <= 0.7
        Phi_N >= 0.6
        S_cascade >= log(3)
    """
    conds = [
        ("CI <= 0.7", CI <= 0.7 + 1e-12),
        ("Phi_N >= 0.6", Phi_N >= 0.6 - 1e-12),
        ("S_cascade >= log(3)", S_cascade >= math.log(3) - 1e-12),
    ]
    failed = [name for name, ok in conds if not ok]
    ok = len(failed) == 0
    msg = ", ".join(failed) if failed else "All QP constraints satisfied."
    return ok, msg

# ----------------------------------------------------------------------
# Example usage with a *plausible* parameter set
# ----------------------------------------------------------------------
def run_validation(params: Dict[str, float]) -> None:
    """
    params should contain:
        phi_n, phi_n0, s_cascade, psi (derived from phi_n/phi_n0),
        alpha, beta, gamma, phi_delta,
        CI, S_cascade (again), plus the invariant forms list.
    """
    print("=== Ω‑Physics Rubric v26.0 Compliance Check ===\n")

    # 1. Invariant uniqueness – we simulate the two forms appearing in the text
    invariant_forms = [
        "ln(phi_n/phi_n0)",                     # from the Field‑Theoretic Embedding section
        "ln(|r_cascade|/r0) + lambda*ci(t)"    # from the Invariant from Cascade‑Graph Curvature section
    ]
    ok, msg = check_invariant_uniqueness(invariant_forms)
    print(f"[Invariant Uniqueness] {'PASS' if ok else 'FAIL'} – {msg}")

    # 2. Boundary consistency (using Set2 logic)
    ok, msg = check_boundary_consistency(
        phi_n=params["phi_n"],
        phi_n0=params["phi_n0"],
        s_cascade=params["s_cascade"],
        psi=params["psi"],
    )
    print(f"[Boundary Consistency] {'PASS' if ok else 'FAIL'} – {msg}")

    # 3. Potential sign constraints
    ok, msg = check_potential_signs(
        alpha=params["alpha"],
        beta=params["beta"],
        gamma=params["gamma"],
    )
    print(f"[Potential Signs] {'PASS' if ok else 'FAIL'} – {msg}")

    # 4. Gauge current dimensionless
    ok, msg = check_gauge_dimensionless(phi_delta=params["phi_delta"])
    print(f"[Gauge Dimensionless] {'PASS' if ok else 'FAIL'} – {msg}")

    # 5. QP constraints
    ok, msg = check_qp_constraints(
        CI=params["CI"],
        Phi_N=params["Phi_N"],
        S_cascade=params["S_cascade"],
    )
    print(f"[QP Constraints] {'PASS' if ok else 'FAIL'} – {msg}")

    print("\n=== End of Check ===")

# ----------------------------------------------------------------------
# Example parameter set (feel free to edit)
# ----------------------------------------------------------------------
example_params = {
    # Phi_N and its reference value
    "phi_n": 0.5,          # below the reference => psi negative
    "phi_n0": 1.0,
    # Entropy (Shannon) – assume three equally likely types => S = ln(3)
    "s_cascade": math.log(3),
    # Psi computed from the invariant (should be ln(0.5/1) = -ln2)
    "psi": math.log(0.5 / 1.0),
    # Double‑well potential coefficients (must satisfy alpha<0, beta>0, gamma>0)
    "alpha": -1.0,
    "beta": 2.0,
    "gamma": 0.5,
    # Gauge field (dimensionless)
    "phi_delta": 0.3,
    # MPC‑Ω state variables
    "CI": 0.55,            # below the 0.7 threshold
    "Phi_N": 0.65,         # above the 0.6 threshold
    "S_cascade": math.log(3),  # meets entropy constraint
}

if __name__ == "__main__":
    run_validation(example_params)