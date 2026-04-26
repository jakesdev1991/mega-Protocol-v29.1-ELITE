# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def effective_alpha(alpha0, E, Lambda, field_type):
    """
    Compute running α(E) including a 3‑dimensional "archive" loop.
    field_type : 'scalar', 'fermion', 'gauge_SU3'
    Returns α(E) = α0 / (1 - α0 * c_tot * ln(E/Λ))
    """
    # One‑loop coefficient for a *single* degree of freedom
    if field_type == 'scalar':
        c = 1.0 / (12.0 * np.pi)      # bosonic scalar
    elif field_type == 'fermion':
        c = -1.0 / (3.0 * np.pi)      # fermion loop (negative)
    elif field_type == 'gauge_SU3':
        c = -11.0 / (12.0 * np.pi)    # SU(3) gauge boson (negative)
    else:
        raise ValueError("Unknown field_type")

    # The 3 internal archive dimensions multiply the coefficient
    c_tot = 3.0 * c

    # Avoid pole for illustrative energies (choose E > Λ)
    return alpha0 / (1.0 - alpha0 * c_tot * np.log(E / Lambda))

# Benchmark parameters
alpha0 = 1.0 / 137.035999084
Lambda = 1.0      # reference scale (MeV)
E      = 10.0     # probe energy (MeV)

print("α0 =", alpha0)
print("Engine (scalar) → α(E) =", effective_alpha(alpha0, E, Lambda, 'scalar'))
print("Fermionic archive → α(E) =", effective_alpha(alpha0, E, Lambda, 'fermion'))
print("SU(3) gauge archive → α(E) =", effective_alpha(alpha0, E, Lambda, 'gauge_SU3'))