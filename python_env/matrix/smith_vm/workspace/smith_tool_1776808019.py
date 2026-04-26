# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def phi_n_phi_delta(l1, l2):
    """
    Compute Phi_N and Phi_Delta from two eigenvalues l1, l2 > 0.
    Returns (Phi_N, Phi_Delta, psi)
    """
    if l1 <= 0 or l2 <= 0:
        raise ValueError("Eigenvalues must be positive for a stable action.")
    trace = l1 + l2
    Phi_N = l1 / trace                     # normalized spectral gap
    # Skewness of two numbers:
    mean = (l1 + l2) / 2.0
    d1 = l1 - mean
    d2 = l2 - mean
    # population skewness (N=2) -> denominator zero if variance=0, otherwise zero numerator
    var = (d1*d1 + d2*d2) / 2.0
    if var == 0.0:
        Phi_Delta = 0.0   # degenerate case
    else:
        skew = (d1*d1*d1 + d2*d2*d2) / (2.0 * var**1.5)
        Phi_Delta = skew
    psi = np.log(Phi_N)   # invariant as defined in proposal
    return Phi_N, Phi_Delta, psi

def check_bounds():
    """Scan eigenvalue space and report violations of rubric bounds."""
    violations = []
    # log‑scan over a wide range
    for log_l1 in np.linspace(-3, 3, 25):
        for log_l2 in np.linspace(-3, 3, 25):
            l1 = 10**log_l1
            l2 = 10**log_l2
            Phi_N, Phi_Delta, psi = phi_n_phi_delta(l1, l2)
            # Rubric expects:
            #   Shredding Event: psi -> +inf, Phi_Delta -> +inf
            #   Informational Freeze: psi -> -inf, Phi_Delta -> 0
            # Since psi is bounded above by 0, any claim of psi>0 is a violation.
            if psi > 0.0:
                violations.append((l1, l2, psi, "psi > 0 (shredding impossible)"))
            # Phi_Delta should be able to reach large values; with 2 eigenvalues it's limited.
            # We'll flag if |Phi_Delta| > 5 as "unrealistically large for 2‑mode system"
            if abs(Phi_Delta) > 5.0:
                violations.append((l1, l2, Phi_Delta, "Phi_Delta magnitude implausibly large"))
    return violations

if __name__ == "__main__":
    viol = check_bounds()
    print(f"Found {len(viol)} violations of the Omega rubric:")
    for v in viol[:10]:  # show first 10
        print(f"  λ1={v[0]:.3e}, λ2={v[1]:.3e} → ψ={v[2]:.3f}, ΦΔ={v[3]:.3f}  ({v[4]})")
    if len(viol) > 10:
        print(f"  ... and {len(viol)-10} more.")