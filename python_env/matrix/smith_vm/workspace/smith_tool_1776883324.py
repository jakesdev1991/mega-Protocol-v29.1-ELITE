# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol validation of the Engine's Higher‑Order Lattice Polarization
correction for the fine‑structure constant.

The script reproduces the integral:
    Δα/α = (Φ_Delta/Φ_N) * (1/Λ²) * ∫_{k<Λ} e^{-k²/(2Λ²)} / (1+(k·v)²) d³k
with Λ = 0.82, v = 1.28 (dimensionless in the Engine's notation).

It also estimates the entropy H = -∑ n_k ln n_k for the IR modes
using the occupation n_k = 1/(exp(k²/(2Λ²))-1).

If the script is run in the isolated VM, it will print the numerical
results and flag any violations of the Omega Protocol invariants that
can be checked quantitatively.
"""

import numpy as np

# ----------------------------------------------------------------------
# Parameters from the Engine (treated as dimensionless)
Lambda = 0.82          # Shredding Event horizon (inverse length units)
v      = 1.28          # VAA alignment from diagonal basis symmetry

# ----------------------------------------------------------------------
# 1. Dimensionless integral I = ∫_{0}^{Λ} 4π k² e^{-k²/(2Λ²)} / (1+(k·v)²) dk
#    Change variable q = k/Λ  => k = Λ q, dk = Λ dq, limits q∈[0,1]
def integrand(q):
    """Integrand after change of variables."""
    # 4π k² = 4π (Λ q)² = 4π Λ² q²
    # Jacobian dk = Λ dq  => overall factor Λ³
    num = 4.0 * np.pi * (Lambda**2) * (q**2) * np.exp(-q**2 / 2.0)
    den = 1.0 + (Lambda * q * v)**2   # (k·v)² = (Λ q v)²
    return num / den

# Perform the integral using Simpson's rule for high accuracy
N = 20000                     # even number of intervals
q_vals = np.linspace(0.0, 1.0, N+1)
f_vals = integrand(q_vals)
# Simpson's rule
dx = 1.0 / N
I_simpson = (dx/3.0) * (f_vals[0] + f_vals[-1] +
                        4.0*np.sum(f_vals[1:-1:2]) +
                        2.0*np.sum(f_vals[2:-2:2]))
# The integral in k‑space is I_k = Λ³ * I_simpson (because we factored Λ³ out)
I_k = (Lambda**3) * I_simpson

print(f"Dimensionless integral I_k = {I_k:.6e}")

# ----------------------------------------------------------------------
# 2. Compute the prefactor that multiplies Φ_Delta/Φ_N
prefactor = I_k / (Lambda**2)   # because formula has 1/Λ² * I_k
print(f"Prefactor (Δα/α) / (Φ_Delta/Φ_N) = {prefactor:.6e}")

# ----------------------------------------------------------------------
# 3. Infer the required ratio Φ_Delta/Φ_N to match Engine's claimed Δα/α
claimed_delta_alpha_over_alpha = 3.21e-5
required_ratio = claimed_delta_alpha_over_alpha / prefactor
print(f"Required Φ_Delta/Φ_N to obtain Δα/α = {claimed_delta_alpha_over_alpha:.2e}")
print(f"  => Φ_Delta/Φ_N = {required_ratio:.6e}")

# ----------------------------------------------------------------------
# 4. Entropy estimate for IR modes (q < 1)
#    Occupation number: n(q) = 1/(exp(q²/2) - 1)
#    Entropy density:   s = -∫ n ln n  d³k / (2π)³  (we ignore (2π)³ for a relative check)
def occupation(q):
    return 1.0 / (np.exp(q**2 / 2.0) - 1.0)

def entropy_integrand(q):
    n = occupation(q)
    # Avoid log(0) at q=0 where n→∞; we start from a small cutoff
    if q == 0.0:
        return 0.0
    return - n * np.log(n) * 4.0 * np.pi * q**2   # d³k = 4π q² dq (Λ³ factor omitted)

# Integrate from a small epsilon to 1 to see the behaviour
eps = 1e-4
q_ent = np.linspace(eps, 1.0, 20000)
s_vals = entropy_integrand(q_ent)
H_est = np.trapz(s_vals, q_ent)   # missing Λ³ factor; we report the dimensionless part
print(f"Entropy contribution (dimensionless, missing Λ³ factor) from q∈[{eps},1]: {H_est:.6f}")
print("Note: As eps → 0 the integrand ~ 2·ln(1/q²) → divergent, so H → ∞.")
print("Thus the claimed bound H ≥ 0.85 cannot be satisfied without an explicit IR cutoff.")

# ----------------------------------------------------------------------
# 5. Quick dimensional check (in natural units ℏ=c=1)
#    The Engine treats Λ and v as dimensionless; if they carry dimensions,
#    an additional hidden length scale ℓ must appear such that:
#        Λ_physical = Λ / ℓ,   v_physical = v (dimensionless)
#    The script cannot infer ℓ; any missing ℓ would show up as a mismatch
#    between the computed prefactor and the expected magnitude of Δα/α.
print("\nDimensional note:")
print("  If Λ has dimensions of [length]⁻¹, the factor Λ³ in I_k provides [L]⁻³.")
print("  The 1/Λ² prefactor adds [L]², leaving an overall [L]⁻¹.")
print("  To obtain a dimensionless Δα/α, a hidden length scale (e.g., lattice spacing a)")
print("  must appear squared in the numerator – this is not shown in the Engine's comment.")
print("  Hence the dimensional analysis is incomplete.")

# ----------------------------------------------------------------------
# Final compliance flag (based on quantitative checks only)
compliant = True
if required_ratio < 1e-6 or required_ratio > 1e-2:
    print("\n[QUANTITATIVE WARNING] Inferred Φ_Delta/Φ_N is outside a plausible range.")
    compliant = False
if H_est > 10.0:   # arbitrary large value indicating divergence
    print("[ENTROPY WARNING] Entropy integral shows IR divergence; H ≥ 0.85 claim unsupported.")
    compliant = False

if compliant:
    print("\n[QUANTITATIVE PASS] All automatically checkable numeric conditions are satisfied.")
else:
    print("\n[QUANTITATIVE FAIL] One or more numeric checks indicate inconsistency.")