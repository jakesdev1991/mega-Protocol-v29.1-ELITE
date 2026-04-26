# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# Define symbols for dimensionless fields and their time derivatives
phi_N, phi_D = sp.symbols('phi_N phi_D', positive=True, real=True)
phi_N_dot, phi_D_dot = sp.symbols('phi_N_dot phi_D_dot', real=True)
phi_N_ddot, phi_D_ddot = sp.symbols('phi_N_ddot phi_D_ddot', real=True)
phi_N_dddot, phi_D_dddot = sp.symbols('phi_N_dddot phi_D_dddot', real=True)

# Define the pseudo-probabilities (as in the SERC model)
p_N = phi_N**2 / (phi_N**2 + phi_D**2)
p_D = phi_D**2 / (phi_N**2 + phi_D**2)

# Shannon entropy (dimensionless)
S = -p_N*sp.log(p_N) - p_D*sp.log(p_D)

# First time derivative: dS/dt = ∂S/∂φ_N * φ_N_dot + ∂S/∂φ_D * φ_D_dot
dS_dphi_N = sp.diff(S, phi_N)
dS_dphi_D = sp.diff(S, phi_D)
dS_dt = dS_dphi_N * phi_N_dot + dS_dphi_D * phi_D_dot

# Second derivative: differentiate dS_dt with respect to time
# We'll apply the chain rule symbolically: d/dt = φ_dot * ∂/∂φ + φ_ddot * ∂/∂φ_dot
# Since dS_dt depends on φ_N, φ_D, φ_N_dot, φ_D_dot, we need to treat φ_dot as independent and then substitute.
# A more direct approach: compute the total time derivative of S as a function of t via sympy's diff.
# Instead, we compute the symbolic expression for the second derivative directly:
d2S_dt2 = (sp.diff(dS_dt, phi_N) * phi_N_dot +
           sp.diff(dS_dt, phi_D) * phi_D_dot +
           sp.diff(dS_dt, phi_N_dot) * phi_N_ddot +
           sp.diff(dS_dt, phi_D_dot) * phi_D_ddot)

# Third derivative: differentiate d2S_dt2 similarly
d3S_dt3 = (sp.diff(d2S_dt2, phi_N) * phi_N_dot +
           sp.diff(d2S_dt2, phi_D) * phi_D_dot +
           sp.diff(d2S_dt2, phi_N_dot) * phi_N_ddot +
           sp.diff(d2S_dt2, phi_D_dot) * phi_D_ddot +
           sp.diff(d2S_dt2, phi_N_ddot) * phi_N_dddot +
           sp.diff(d2S_dt2, phi_D_ddot) * phi_D_dddot)

# Simplify the full jerk expression
J_full = sp.simplify(d3S_dt3)

# The heuristic SERC term (Archive term) for comparison
# They propose: (3*phi_D / xi_D**4) * (phi_D_dot**3)
# Let's treat xi_D as a time scale (units of seconds). We'll compute symbolic magnitude ratio.
xi = sp.symbols('xi', positive=True, real=True)  # seconds
J_heuristic = (3 * phi_D / xi**4) * phi_D_dot**3

# Now substitute the given numerical values
numeric_vals = {
    phi_N: 0.78,
    phi_D: 0.35,
    phi_N_dot: 2.1e3,  # s^-1
    phi_D_dot: 8.7e3,  # s^-1
    # We need second and third derivatives; assume harmonic motion with angular frequency ω = sqrt(ξ^-2)
    # ξ^-2 = 4.2e6 s^-2  =>  ξ = 1/sqrt(4.2e6) ≈ 0.000487 s
    # For harmonic oscillator: φ(t) = A cos(ω t) => φ_dot = -A ω sin(ω t), φ_ddot = -A ω^2 cos(ω t) = -ω^2 φ, φ_dddot = A ω^3 sin(ω t) = -ω^2 φ_dot
    # We'll approximate φ_ddot ≈ -ω^2 φ and φ_dddot ≈ -ω^2 φ_dot
}
omega_sq = 4.2e6  # s^-2
phi_N_ddot_val = -omega_sq * numeric_vals[phi_N]
phi_D_ddot_val = -omega_sq * numeric_vals[phi_D]
phi_N_dddot_val = -omega_sq * numeric_vals[phi_N_dot]
phi_D_dddot_val = -omega_sq * numeric_vals[phi_D_dot]

numeric_vals_full = {
    **numeric_vals,
    phi_N_ddot: phi_N_ddot_val,
    phi_D_ddot: phi_D_ddot_val,
    phi_N_dddot: phi_N_dddot_val,
    phi_D_dddot: phi_D_dddot_val,
    xi: 1/sp.sqrt(omega_sq)  # seconds
}

# Evaluate the correct jerk (dimensionless, but we keep units symbolic for now)
J_correct_val = float(J_full.subs(numeric_vals_full))
# Evaluate the heuristic jerk (units s^-7)
J_heuristic_val = float(J_heuristic.subs(numeric_vals_full))

# Compute the ratio of heuristic to correct term (this is the "dimensional inconsistency factor")
ratio = J_heuristic_val / J_correct_val if J_correct_val != 0 else float('inf')

# Compute the correct *dimensionless* jerk by normalizing with (dS/dt)^3
dS_dt_val = float(dS_dt.subs(numeric_vals_full))
J_dimensionless = J_correct_val / (dS_dt_val**3) if dS_dt_val != 0 else float('inf')

print("=== Disruption Verification ===")
print(f"Correct jerk (symbolic, unnormalized): {J_correct_val:.6e} (dimensionless units)")
print(f"Heuristic SERC jerk: {J_heuristic_val:.6e} s^-7")
print(f"Heuristic / Correct ratio: {ratio:.6e} (demonstrates unit mismatch)")
print(f"dS/dt magnitude: {dS_dt_val:.6e} s^-1")
print(f"Dimensionless jerk (J/(dS/dt)^3): {J_dimensionless:.6e}")
print("\n=== Boundary Condition Analysis ===")
# Compute Shredding Event condition: phi_N^2 + 3*phi_D^2
shredding_val = numeric_vals[phi_N]**2 + 3 * numeric_vals[phi_D]**2
print(f"Shredding LHS (phi_N^2 + 3*phi_D^2): {shredding_val:.6f} (threshold = 1.0)")
print(f"Distance to boundary: {1.0 - shredding_val:.6f} (close to shredding, but curvature still finite)")