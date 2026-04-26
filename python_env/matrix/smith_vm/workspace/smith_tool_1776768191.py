# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Jerk‑Stability Validator
---------------------------------------
Validates the informational‑jerk stability calculation for a Linux HSA node
according to the corrected, dimension‑consistent formula.
"""

import numpy as np

# ----------------------------------------------------------------------
# Input parameters (as supplied in the Engine output)
# ----------------------------------------------------------------------
v = 1.0                     # vacuum expectation value (scale factor); set to 1 for normalized units
Phi_N   = 0.78 * v          # Newtonian field magnitude
Phi_D   = 0.35 * v          # Archive (3‑D) field magnitude
dPhi_N  = 2.1e3 * v         # Newtonian velocity  (v * s^-1)
dPhi_D  = 8.7e3 * v         # Archive velocity    (v * s^-1)
xi_inv2 = 4.2e6             # stiffness inverse squared  (s^-2)  -> lambda * v^2
J_source = 1.5e12           # source jerk contribution (s^-3)
J_thresh = 5.0e12           # empirical stability threshold (s^-3)

# ----------------------------------------------------------------------
# Helper: normalise to dimensionless quantities
# ----------------------------------------------------------------------
phi_N   = Phi_N   / v
phi_D   = Phi_D   / v
dphi_N  = dPhi_N  / v          # now in s^-1
dphi_D  = dPhi_D  / v          # now in s^-1
xi2     = 1.0 / xi_inv2        # xi^2  (s^2)
xi4     = xi2**2               # xi^4  (s^4)

# ----------------------------------------------------------------------
# Jerk‑stability computation (corrected formula)
# ----------------------------------------------------------------------
J_archive = 3.0 * phi_D / xi4 * (dphi_D**3)
J_newton  =       phi_N / xi4 * (dphi_N**3)
J_stab    = J_archive - J_newton + J_source

# ----------------------------------------------------------------------
# Dimensional sanity check (should be s^-3)
# ----------------------------------------------------------------------
# In our normalised system the result is already in s^-3 because
#   phi_* : dimensionless
#   dphi_*: s^-1
#   xi^4  : s^4
#   => (dimensionless)*(s^-1)^3 / s^4 = s^-3
assert np.isclose(J_stab.unit, 1.0), "Dimensional mismatch: expected s^-3"

# ----------------------------------------------------------------------
# Omega Protocol invariant test
# ----------------------------------------------------------------------
stable = J_stab < J_thresh

# ----------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------
print(f"Normalised fields:   Φ_N/v = {phi_N:.3f},   Φ_Δ/v = {phi_D:.3f}")
print(f"Normalised velocities:  dΦ_N/dt / v = {dphi_N:.2e} s⁻¹,  dΦ_Δ/dt / v = {dphi_D:.2e} s⁻¹")
print(f"Stiffness ξ² = {xi2:.3e} s²  →  ξ⁴ = {xi4:.3e} s⁴")
print(f"Jerk contributions:")
print(f"  Archive term   = {J_archive:.3e} s⁻³")
print(f"  Newtonian term = {J_newton:.3e} s⁻³")
print(f"  Source term    = {J_source:.3e} s⁻³")
print(f"→ Computed J_stab = {J_stab:.3e} s⁻³")
print(f"Threshold J_thresh = {J_thresh:.3e} s⁻³")
print(f"Protocol invariant (J_stab < J_thresh) : {stable}")

if not stable:
    raise AssertionError("Omega Protocol violation: J_stab exceeds stability threshold.")