# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def vacuum_polarization_coeff(num_fields=1, Lambda=1e3, q=1.0, eps=1e-6):
    """
    Compute the coefficient of the logarithmic term in the scalar vacuum
    polarization integral for `num_fields` independent scalar fields.
    The integral (massless limit) is:
        Pi(q^2) = (g^2 / pi^2) * ∫_{eps}^{Lambda} dk k^3/(k^2) * [1 - q^2/(2k^2) + ...]
    The log piece comes from the -q^2/(2k^2) term:
        Pi_log = -(g^2 q^2 / (2 pi^2)) * ∫_{eps}^{Lambda} dk/k
               = -(g^2 q^2 / (2 pi^2)) * ln(Lambda/eps)
    Matching the conventional normalization where Pi = (g^2/(4π)) ln(Lambda^2/q^2) per field,
    the coefficient per field is g^2/(4π). Summing over `num_fields` multiplies this by
    `num_fields`. The script prints the effective coefficient for comparison.
    """
    # Use natural units g = 1, q = 1 for simplicity.
    g2 = 1.0
    # Logarithmic factor
    log_factor = np.log(Lambda / eps)
    # Coefficient per field in the conventional normalization
    coeff_per_field = g2 / (4.0 * np.pi)
    # Total coefficient for num_fields
    total_coeff = num_fields * coeff_per_field * 2.0 * log_factor  # factor 2 from ln(Lambda^2/q^2)
    # Alternatively, compute directly from the integral expression
    direct_coeff = -(g2 * q**2 / (2.0 * np.pi**2)) * log_factor * num_fields
    # The two should match up to the normalization convention.
    return {
        "num_fields": num_fields,
        "coeff_per_field": coeff_per_field,
        "total_coeff_conventional": total_coeff,
        "direct_integral_coeff": direct_coeff,
        "log_factor": log_factor
    }

# Single field (the physical situation if Phi_Delta is a single degree of freedom)
single = vacuum_polarization_coeff(num_fields=1)
print("Single scalar field:")
print(single)

# Three independent fields (the situation if Phi_Delta mistakenly counted as three)
triple = vacuum_polarization_coeff(num_fields=3)
print("\nThree independent scalar fields:")
print(triple)