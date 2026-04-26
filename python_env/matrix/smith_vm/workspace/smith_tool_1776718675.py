# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol validation script for the Higher-Order Lattice Polarization
derivation of the fine-structure constant.

The script scans over a grid of (Phi_N, Phi_Delta) values and reports
any violation of the protocol invariants:
    - mass positivity (real m_e, m_p)
    - perturbative control (|eps * cosh| < lambda_max)
Optionally it also checks the quality of the epsilon^2 expansion.
"""

import numpy as np

# ------------------- Protocol parameters -------------------
# Bare electron mass (set to 1 in natural units)
m = 1.0
# Dimensionless coupling
g = 0.1
# UV cutoff (appears only inside a log, we fix a reasonable ratio)
Lambda_over_m = 1e3
# Safety margin for the expansion parameter (Omega Protocol)
lambda_max = 0.3   # require |eps*cosh| < 0.3
# Fine-structure constant bare value (not needed for stability checks)
alpha0 = 1.0/137.0

# ------------------- Helper functions -------------------
def effective_masses(Phi_N, Phi_Delta):
    """Return m_e, m_p."""
    Phi_plus  = Phi_N * np.exp( Phi_Delta)
    Phi_minus = Phi_N * np.exp(-Phi_Delta)
    m_e = m - g * Phi_plus
    m_p = m - g * Phi_minus
    return m_e, m_p

def Pi_exact(Phi_N, Phi_Delta):
    """Exact one-loop vacuum polarization (leading log)."""
    m_e, m_p = effective_masses(Phi_N, Phi_Delta)
    # Guard against non-positive masses (would give log of neg/zero)
    if m_e <= 0 or m_p <= 0:
        return np.nan   # signal invalid point
    m_eff = np.sqrt(m_e * m_p)
    return (alpha0/(3*np.pi)) * np.log(Lambda_over_m * m / m_eff)

def alpha_ren_exact(Phi_N, Phi_Delta):
    """Renormalized fine-structure constant from exact Pi."""
    Pi = Pi_exact(Phi_N, Phi_Delta)
    if np.isnan(Pi):
        return np.nan
    return alpha0 / (1.0 - Pi)

def expansion_check(Phi_N, Phi_Delta, order=2):
    """Compare exact log term to its epsilon^2 expansion."""
    eps = g * Phi_N / m
    # Exact log term from masses
    m_e, m_p = effective_masses(Phi_N, Phi_Delta)
    if m_e <= 0 or m_p <= 0:
        return np.nan
    log_exact = np.log(m_e * m_p / m**2)
    # Series: -2*eps*cosh + eps^2*(1-2*cosh^2)
    cosh = np.cosh(Phi_Delta)
    log_series = -2.0*eps*cosh + eps**2 * (1.0 - 2.0*cosh**2)
    return log_exact, log_series, eps*cosh   # also return expansion parameter

# ------------------- Scan over parameter space -------------------
Phi_N_vals = np.logspace(-3, 1, 40)   # from 0.001 to 10 (in units of m/g)
Phi_Delta_vals = np.linspace(-2, 2, 41)  # symmetric range

violations = []

for Phi_N in Phi_N_vals:
    for Phi_Delta in Phi_Delta_vals:
        # 1) Mass positivity
        m_e, m_p = effective_masses(Phi_N, Phi_Delta)
        if m_e <= 0 or m_p <= 0:
            violations.append(('mass_positivity', Phi_N, Phi_Delta, m_e, m_p))
            continue   # no need to check further

        # 2) Perturbative control
        eps = g * Phi_N / m
        control_param = eps * np.cosh(Phi_Delta)
        if abs(control_param) >= lambda_max:
            violations.append(('perturbative_control', Phi_N, Phi_Delta,
                               eps, control_param))
            continue

        # 3) Optional: expansion quality (should be small if control_param <<1)
        log_ex, log_series, _ = expansion_check(Phi_N, Phi_Delta)
        if not np.isnan(log_ex):
            rel_err = abs(log_ex - log_series) / (abs(log_ex) + 1e-12)
            if rel_err > 0.05:   # >5% discrepancy signals breakdown of eps^2 truncation
                violations.append(('expansion_breakdown', Phi_N, Phi_Delta,
                                   rel_err, log_ex, log_series))

# ------------------- Reporting -------------------
print(f"Scanned {len(Phi_N_vals)*len(Phi_Delta_vals)} points.")
print(f"Found {len(violations)} invariant violations.\n")

if violations:
    print("First few violations:")
    for typ, *rest in violations[:10]:
        if typ == 'mass_positivity':
            Phi_N, Phi_Delta, m_e, m_p = rest
            print(f"[mass_positivity] Phi_N={Phi_N:.3f}, Phi_Delta={Phi_Delta:.3f} -> m_e={m_e:.3e}, m_p={m_p:.3e}")
        elif typ == 'perturbative_control':
            Phi_N, Phi_Delta, eps, ctrl = rest
            print(f"[perturbative_control] Phi_N={Phi_N:.3f}, Phi_Delta={Phi_Delta:.3f} -> eps={eps:.3e}, eps*cosh={ctrl:.3f}")
        else:  # expansion_breakdown
            Phi_N, Phi_Delta, rel_err, lex, lser = rest
            print(f"[expansion_breakdown] Phi_N={Phi_N:.3f}, Phi_Delta={Phi_Delta:.3f} -> rel_err={rel_err:.3f}")
else:
    print("No violations found within the scanned region.")

# ------------------- Example of a shredding scenario -------------------
print("\n--- Example illustrating the shredding mechanism ---")
# Choose a source that gives a large Phi_N near the origin (simulated by picking a large Phi_N)
Phi_N_example = 5.0   # this is > m/g = 10 for g=0.1,m=1 => m/g =10, actually still below; increase
Phi_N_example = 12.0  # now exceeds m/g
Phi_Delta_example = 0.5
m_e, m_p = effective_masses(Phi_N_example, Phi_Delta_example)
print(f"Chosen Phi_N={Phi_N_example}, Phi_Delta={Phi_Delta_example}")
print(f"  m_e = {m_e:.3e}, m_p = {m_p:.3e}")
if m_e <= 0 or m_p <= 0:
    print("  -> Mass positivity VIOLATED (tachyonic effective mass).")
else:
    print("  -> Masses still positive (but check perturbative control).")
eps = g*Phi_N_example/m
print(f"  Expansion parameter eps*cosh = {eps*np.cosh(Phi_Delta_example):.3f}")
print(f"  Protocol limit lambda_max = {lambda_max}")
if abs(eps*np.cosh(Phi_Delta_example)) >= lambda_max:
    print("  -> Perturbative control also violated.")