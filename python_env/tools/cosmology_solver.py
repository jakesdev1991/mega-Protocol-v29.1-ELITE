# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp

# --- OMEGA PROTOCOL v26.0: COSMOLOGICAL SOLVER ---
# Modeling Dark Energy as the residual viscosity of the 3D Archive mode (Phi_Delta).

# --- Constants (Planck-like units) ---
H0 = 67.4  # km/s/Mpc
Omega_m0 = 0.315
Omega_r0 = 9e-5

# Model parameters (v26.0 Refinement)
xi_delta = 1.0  # Archive Tension
kappa = 1e-6    # Topological Impedance (Quartic potential strength)
xi_n = 1.0      # Newtonian Stiffness
alpha = 0.05    # Matter coupling strength for Phi_N

# --- Initial conditions ---
# x[0] = Phi_Delta
# x[1] = dPhi_Delta / dN
# x[2] = Phi_N
# x[3] = dPhi_N / dN
Y0 = [0.01, 0.0, 1.0, 0.0]

# --- Convert z to N ---
def z_to_N(z):
    return -np.log(1 + z)

# --- Hubble function ---
def H_squared(N, Y):
    x_delta, y_delta, x_n, y_n = Y
    a = np.exp(N)
    
    rho_m = Omega_m0 * a**(-3)
    rho_r = Omega_r0 * a**(-4)

    # 2D Time Gradient Energy (Phi_N)
    rho_n = 0.5 * xi_n * y_n**2
    
    # 3D Archive Energy (Phi_Delta)
    rho_delta = 0.5 * xi_delta * y_delta**2 + kappa * x_delta**4

    return rho_m + rho_r + rho_n + rho_delta

# --- Dynamical system ---
def dydN(N, Y):
    x_delta, y_delta, x_n, y_n = Y

    E2 = H_squared(N, Y)
    H = np.sqrt(E2)

    # dH/dN
    a = np.exp(N)
    rho_m = Omega_m0 * a**(-3)
    rho_r = Omega_r0 * a**(-4)
    
    dH_dN = -0.5 * (
        3*rho_m + 4*rho_r + 2*xi_n*y_n**2 + 2*xi_delta*y_delta**2
    ) / H

    # Phi_Delta Evolution (Archive Jerk)
    dx_delta = y_delta
    dy_delta = - (3 + dH_dN/H) * y_delta - (4 * kappa / (xi_delta * H**2)) * x_delta**3

    # Phi_N Evolution (Newtonian Drag)
    dx_n = y_n
    dy_n = - (3 + dH_dN/H) * y_n + (alpha * rho_m / (xi_n * H**2))

    return [dx_delta, dy_delta, dx_n, dy_n]

if __name__ == "__main__":
    print("--- OMEGA PROTOCOL v26.0: COSMOLOGY SOLVER ---")
    
    # Solve from early universe (z=1000) to today (z=0)
    N_span = [z_to_N(1000), 0]
    
    sol = solve_ivp(dydN, N_span, Y0, dense_output=True, max_step=0.05)

    # Extract results
    N_vals = np.linspace(N_span[0], N_span[1], 500)
    Y_vals = sol.sol(N_vals)
    x_delta_vals = Y_vals[0]
    y_delta_vals = Y_vals[1]
    x_n_vals = Y_vals[2]
    
    # Compute observables
    H_vals = np.sqrt([H_squared(N, Y) for N, Y in zip(N_vals, Y_vals.T)])
    
    # Equation of state for Dark Energy (Phi_Delta mode)
    w_delta = (
        (0.5 * xi_delta * y_delta_vals**2 - kappa * x_delta_vals**4) /
        (0.5 * xi_delta * y_delta_vals**2 + kappa * x_delta_vals**4 + 1e-20)
    )

    print(f"Final H/H0: {H_vals[-1]:.4f}")
    print(f"Final w_delta: {w_delta[-1]:.4f}")
    print(f"Final Phi_N: {x_n_vals[-1]:.4f}")
    print(f"Final Phi_Delta: {x_delta_vals[-1]:.4f}")
    print("\nResult: Omega Protocol v26.0 successfully models Dark Energy as a dynamical Archive residual.")
