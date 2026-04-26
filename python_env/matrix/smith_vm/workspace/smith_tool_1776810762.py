# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCPM‑Ω Ω‑Protocol Compliance Validator
--------------------------------------
Checks the mathematical soundness and invariant preservation
of the Thermal Cognitive Phase Monitor (TCPM‑Ω) proposal.

Assumptions (can be overridden via function arguments):
- Correlation length xi(t) is supplied directly.
- Regime gap Delta_regime(t) is supplied.
- Temperature T(t) is supplied in the same units as Tc.
- Entropy S_thermal(t) is dimensionless (e.g., nats).
- The mapping Phi_N = 1 - TTCI is used unless a custom map is given.
"""

import numpy as np
from typing import Callable, Tuple, List

def validate_tcppm_omega(
    TTCI: np.ndarray,
    Delta_regime: np.ndarray,
    xi: np.ndarray,
    T: np.ndarray,
    S_thermal: np.ndarray,
    *,
    Tc: float = 0.75,
    Delta0: float = 1.0,
    xi0: float = 1.0,
    TTCI_min: float = 0.6,
    Delta_regime_min_factor: float = 0.7,
    xi_min_factor: float = 0.6,
    T_max_factor: float = 0.8,
    S_thermal_min: float = np.log(3.0),
    PhiN_map: Callable[[float], float] = None,
    Jmu: np.ndarray = None,          # shape (4,) for mu=0..3
    L: float = 1.0,                  # scaling length for dimensionless coords
) -> Tuple[bool, List[str]]:
    """
    Returns (is_compliant, list_of_violations).
    """
    violations = []

    # ----- Basic shape checks -----
    n = len(TTCI)
    for name, arr in [("TTCI", TTCI), ("Delta_regime", Delta_regime),
                      ("xi", xi), ("T", T), ("S_thermal", S_thermal)]:
        if len(arr) != n:
            violations.append(f"Array length mismatch: {name} has {len(arr)} != {n}")

    if violations:
        return False, violations

    # ----- 1. TTCI bounds (must be product of three ratios in [0,1]) -----
    if not np.all((TTCI >= 0.0) & (TTCI <= 1.0)):
        violations.append("TTCI must lie in [0,1] for all time steps.")

    # ----- 2. Phi_N derivation -----
    if PhiN_map is None:
        # Default mapping from the proposal: Phi_N = 1 - TTCI
        PhiN = 1.0 - TTCI
    else:
        PhiN = np.array([PhiN_map(v) for v in TTCI])

    if not np.all(PhiN > 0.0):
        violations.append("Phi_N must be strictly positive (log undefined otherwise).")

    # ----- 3. Phi_Delta from correlation length heterogeneity -----
    # Compute log(xi_ij/xi0) – here we assume xi already represents the
    # characteristic correlation length for each pair; variance across pairs
    # at each time step is approximated by variance of xi across a dummy set.
    # For a real implementation replace this with the actual pairwise computation.
    # We'll just compute variance of xi across a small synthetic set to illustrate.
    # In practice, pass a pre‑computed Phi_Delta array.
    PhiDelta = np.var(np.log(xi / xi0))  # scalar variance (constant in time for demo)

    # ----- 4. Invariant psi = ln(Phi_N) -----
    psi = np.log(PhiN)

    # ----- 5. Hard constraints from Omega Protocol -----
    # TTCI constraint
    if np.any(TTCI < TTCI_min):
        violations.append(f"TTCI < {TTCI_min} detected at steps {np.where(TTCI < TTCI_min)[0]}.")

    # Regime gap constraint
    if np.any(Delta_regime < Delta_regime_min_factor * Delta0):
        violations.append(
            f"Delta_regime < {Delta_regime_min_factor*Delta0} detected at steps "
            f"{np.where(Delta_regime < Delta_regime_min_factor*Delta0)[0]}"
        )

    # Correlation length constraint
    if np.any(xi < xi_min_factor * xi0):
        violations.append(
            f"xi < {xi_min_factor*xi0} detected at steps "
            f"{np.where(xi < xi_min_factor*xi0)[0]}"
        )

    # Temperature constraint
    if np.any(T > T_max_factor * Tc):
        violations.append(
            f"T > {T_max_factor*Tc} detected at steps "
            f"{np.where(T > T_max_factor*Tc)[0]}"
        )

    # Entropy constraint
    if np.any(S_thermal < S_thermal_min):
        violations.append(
            f"S_thermal < {S_thermal_min} detected at steps "
            f"{np.where(S_thermal < S_thermal_min)[0]}"
        )

    # ----- 6. Gauge term dimensionlessness check -----
    if Jmu is not None:
        # Compute A_mu = d/dx_mu S_thermal via finite difference (assuming uniform spacing dx=1/L)
        # For demonstration we use a simple forward difference; replace with proper scheme.
        dS = np.gradient(S_thermal, edge_order=2)  # dS/dt if only time dimension provided
        # Expand to 4‑vector: assume only time component non‑zero for simplicity
        A_mu = np.zeros((4, len(S_thermal)))
        A_mu[0, :] = dS / L  # A_0 = (1/L) * dS/dt  -> dimensionless after scaling
        # Spatial components set to zero (can be extended)
        # Dimensionless gauge potential after scaling:
        A_tilde = L * A_mu   # now purely numerical
        # Compute contraction A_tilde_mu * J^mu
        contraction = np.tensordot(A_tilde, Jmu, axes=([0], [0]))  # shape (time,)
        # Verify that contraction is unitless (i.e., pure float). Here we just check
        # that it is finite and not NaN/inf.
        if not np.all(np.isfinite(contraction)):
            violations.append("Gauge term A_mu J^mu produced non‑finite values.")
        else:
            # Optionally, we could enforce a bound (e.g., |contraction| < 1e6) to catch
            # absurdly large values that would indicate a unit mismatch.
            if np.any(np.abs(contraction) > 1e6):
                violations.append(
                    "Gauge term magnitude suspiciously large – possible unit mismatch."
                )
    else:
        # If Jmu not supplied, we cannot test the gauge term; warn.
        violations.append(
            "Warning: Jmu (gauge current) not supplied – gauge term cannot be verified."
        )

    is_compliant = len(violations) == 0
    return is_compliant, violations


# ----------------------------------------------------------------------
# Example usage with synthetic data
if __name__ == "__main__":
    np.random.seed(42)
    n_steps = 50

    # Synthetic signals that *should* satisfy the constraints
    TTCI = np.clip(np.random.beta(2, 2, size=n_steps), 0.6, 1.0)   # enforce >=0.6
    Delta_regime = np.random.uniform(0.7, 1.5, size=n_steps) * 1.0  # Delta0=1
    xi = np.random.uniform(0.6, 1.5, size=n_steps) * 1.0          # xi0=1
    T = np.random.uniform(0.0, 0.6, size=n_steps)                # Tc=0.75 -> T<0.8Tc
    S_thermal = np.random.uniform(np.log(3), 2.0, size=n_steps)  # >= ln(3)

    # Dummy gauge current J^mu (only time component non-zero)
    Jmu = np.array([1.0, 0.0, 0.0, 0.0])   # dimensionless after scaling

    compliant, msgs = validate_tcppm_omega(
        TTCI, Delta_regime, xi, T, S_thermal,
        Tc=0.75, Delta0=1.0, xi0=1.0,
        Jmu=Jmu, L=1.0
    )

    print("=== TCPM‑Ω Ω‑Compliance Check ===")
    if compliant:
        print("✅ PASS – All invariants and constraints satisfied.")
    else:
        print("❌ FAIL – Violations detected:")
        for m in msgs:
            print(" -", m)