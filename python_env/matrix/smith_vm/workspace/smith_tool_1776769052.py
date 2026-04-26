# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation of the Shredding‑flaw scaling analysis for the Omega Protocol.

Approximate RG equations (with I0 = 1, ηΔ < 0, κ > 0):
    dΦΔ/dL = |ηΔ| * ΦΔ**3 + κ * ΦN * ΦΔ
    dΦN/dL = - κ * ΦΔ**2

We integrate backwards in L (i.e. forward in x = Lc - L) to observe the
finite‑scale singularity and verify the scaling:
    ΦΔ ~ A * x^{-1/2},   ΦN ~ -B * ln(x)
with A^2 = 1/(2|ηΔ|),   B = κ/(2|ηΔ|).
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Model parameters (choose values that satisfy the Shredding conditions)
# ----------------------------------------------------------------------
eta_N = 0.1          # not used in the approximation, but kept for completeness
eta_Delta = -0.5     # ηΔ < 0  => |ηΔ| = 0.5
kappa = 0.3          # κ > 0
I0 = 1.0             # normalization (set to 1 for the scaling analysis)

abs_eta_D = -eta_Delta   # |ηΔ|

# ----------------------------------------------------------------------
# Approximate RG system (neglecting sub‑dominant terms)
# ----------------------------------------------------------------------
def approx_rg(L, y):
    """dy/dL = [dΦΔ/dL, dΦN/dL]"""
    Phi_D, Phi_N = y
    dPhi_D = abs_eta_D * Phi_D**3 + kappa * Phi_N * Phi_D
    dPhi_N = -kappa * Phi_D**2
    return [dPhi_D, dPhi_N]

# ----------------------------------------------------------------------
# Integration settings
# ----------------------------------------------------------------------
L_start = -10.0          # start far left of the would-be singularity
L_end   = -1e-3          # stop very close to Lc (we set Lc = 0 for convenience)
# Initial conditions: small perturbations around the vacuum (Phi_N ~ 0, Phi_D ~ 0)
# We seed a tiny ΦΔ to trigger the runaway.
y0 = [1e-6, 0.0]

sol = solve_ivp(approx_rg, [L_start, L_end], y0,
                method='RK45', rtol=1e-9, atol=1e-12,
                dense_output=True)

L_vals = sol.t
Phi_D_vals = sol.y[0]
Phi_N_vals = sol.y[1]

# ----------------------------------------------------------------------
# Compute the distance to the putative singularity: x = Lc - L (Lc = 0)
# ----------------------------------------------------------------------
x_vals = -L_vals   # since Lc = 0, x = -L > 0

# ----------------------------------------------------------------------
# Fit ΦΔ to A * x^{-p}
# ----------------------------------------------------------------------
# Take log: ln ΦΔ = ln A - p * ln x
mask = x_vals > 1e-4   # avoid numerical noise near the endpoint
log_x = np.log(x_vals[mask])
log_PhiD = np.log(np.abs(Phi_D_vals[mask]))
coeffs = np.polyfit(log_x, log_PhiD, 1)
p_fit = -coeffs[0]
A_fit = np.exp(coeffs[1])

# ----------------------------------------------------------------------
# Fit ΦN to C + B * ln(x)  (note the minus sign in the theory)
# ----------------------------------------------------------------------
# ΦN = C + B * ln(x)   =>   B = dΦN/d(ln x)
log_x_fit = np.log(x_vals[mask])
# Use finite difference to estimate derivative
dPhiN_dL = np.gradient(Phi_N_vals, L_vals)
dPhiN_dlnx = dPhiN_dL[mask] / (-x_vals[mask])   # d/d ln x = -x * d/dL
B_fit = np.mean(dPhiN_dlnx)   # should be roughly constant
C_fit = np.mean(Phi_N_vals[mask] - B_fit * log_x_fit)

# ----------------------------------------------------------------------
# Theoretical values from the analysis
# ----------------------------------------------------------------------
A_theory = 1.0 / np.sqrt(2.0 * abs_eta_D)
B_theory = kappa / (2.0 * abs_eta_D)

# ----------------------------------------------------------------------
# Output results
# ----------------------------------------------------------------------
print("=== Shredding‑flaw validation ===")
print(f"Integration range: L ∈ [{L_start:.3f}, {L_end:.3f}]  (Lc = 0)")
print(f"Number of points: {len(L_vals)}")
print()
print("Fitted scaling for Φ_Δ ~ A * x^{-p}:")
print(f"  p_fit   = {p_fit:.6f}   (theory p = 0.5)")
print(f"  A_fit   = {A_fit:.6f}   (theory A = {A_theory:.6f})")
print()
print("Fitted scaling for Φ_N ~ C + B * ln(x):")
print(f"  B_fit   = {B_fit:.6f}   (theory B = {B_theory:.6f})")
print(f"  C_fit   = {C_fit:.6f}   (integration constant)")
print()
print("Theory values:")
print(f"  |ηΔ|    = {abs_eta_D:.6f}")
print(f"  A_theory= {A_theory:.6f}")
print(f"  B_theory= {B_theory:.6f}")
print()
# Check positivity invariant for Φ_N (should be ≥0 for a Newtonian mode)
min_PhiN = np.min(Phi_N_vals)
print(f"Minimum Φ_N encountered: {min_PhiN:.6e}")
if min_PhiN < 0:
    print("⚠️  Φ_N becomes negative → violates the Newtonian‑mode positivity invariant.")
else:
    print("✓  Φ_N remains non‑negative (within numerical tolerance).")
# ----------------------------------------------------------------------
# Optional: plot the results
# ----------------------------------------------------------------------
try:
    plt.figure(figsize=(10,4))
    plt.subplot(1,2,1)
    plt.loglog(x_vals, np.abs(Phi_D_vals), label='Φ_Δ (num)')
    plt.loglog(x_vals, A_fit * x_vals**(-p_fit), '--', label=f'fit: A*x^{{-p}}')
    plt.loglog(x_vals, A_theory * x_vals**(-0.5), ':', label='theory: A*x^{{-1/2}}')
    plt.xlabel('x = Lc - L')
    plt.ylabel('|Φ_Δ|')
    plt.legend()
    plt.title('Φ_Δ scaling')

    plt.subplot(1,2,2)
    plt.semilogx(x_vals, Phi_N_vals, label='Φ_N (num)')
    plt.semilogx(x_vals, C_fit + B_fit * np.log(x_vals), '--',
                 label=f'fit: C + B*ln(x)')
    plt.semilogx(x_vals, C_fit + B_theory * np.log(x_vals), ':',
                 label='theory: C + B*ln(x)')
    plt.xlabel('x = Lc - L')
    plt.ylabel('Φ_N')
    plt.legend()
    plt.title('Φ_N scaling')
    plt.tight_layout()
    plt.show()
except Exception:
    pass  # plotting optional in headless environments