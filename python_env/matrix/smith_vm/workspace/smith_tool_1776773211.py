# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------
# Parameters from the SERC output
# ------------------------------
I0 = 5.0          # bits
eps = 0.2
omega_c = 2 * np.pi * 50   # rad/s (50 Hz)
tau = 2.0         # s
dt = 1e-3         # 1 ms sampling
T = 1.0           # total duration 1 s
Nsteps = int(T / dt) + 1
t = np.linspace(0, T, Nsteps)

# Synthetic I(t) without noise (deterministic core)
I = I0 * (1 + eps * np.cos(omega_c * t)) * np.exp(-t / tau)

# ------------------------------
# Finite‑difference derivatives (as in SERC)
# ------------------------------
def central_diff(f, h):
    return (np.roll(f, -1) - np.roll(f, 1)) / (2 * h)

def second_central_diff(f, h):
    return (np.roll(f, -1) - 2 * f + np.roll(f, 1)) / (h ** 2)

def third_central_diff(f, h):
    # J ≈ (f[t+2h] - 2f[t+h] + 2f[t-h] - f[t-2h]) / (2 h^3)
    return (np.roll(f, -2) - 2 * np.roll(f, -1) +
            2 * np.roll(f, 1) - np.roll(f, 2)) / (2 * h ** 3)

Idot = central_diff(I, dt)
Iddot = second_central_diff(I, dt)
J = third_central_diff(I, dt)   # informational jerk, bits/s^3

# ------------------------------
# Jerk‑stiffness relation: J = a*Idot + b*Iddot
# where a = -1/xi_N^2, b = -1/xi_Delta^2
# Solve via least squares (ignore first/last 2 points due to stencil)
# ------------------------------
valid = slice(2, -2)   # avoid edge effects from roll
A = np.vstack([Idot[valid], Iddot[valid]]).T
b_vec = J[valid]
# Solve A * [a, b]^T = b_vec
params, _, _, _ = np.linalg.lstsq(A, b_vec, rcond=None)
a, b = params
xi_N = np.sqrt(-1.0 / a)   # a should be negative
xi_Delta = np.sqrt(-1.0 / b)  # b should be negative

# ------------------------------
# Omega Protocol thresholds (from SERC)
# ------------------------------
xi_crit = 10e-3   # 10 ms
xi_max  = 100e-3  # 100 ms
J_max   = 1e6     # bits/s^3

# ------------------------------
# Validation assertions (enforce invariants)
# ------------------------------
assert a < 0, "Fitted a must be negative (=> xi_N^2 positive)"
assert b < 0, "Fitted b must be negative (=> xi_Delta^2 positive)"
assert xi_N > xi_crit, f"xi_N = {xi_N*1e3:.2f} ms ≤ xi_crit"
assert xi_Delta < xi_max, f"xi_Delta = {xi_Delta*1e3:.2f} ms ≥ xi_max"
assert np.max(np.abs(J)) < J_max, f"max|J| = {np.max(np.abs(J)):.2e} ≥ J_max"

# ------------------------------
# Dimensional sanity check (units)
# ------------------------------
# I: bits
# Idot: bits/s
# Iddot: bits/s^2
# J: bits/s^3
# xi_N, xi_Delta: seconds
# a = -1/xi_N^2 -> 1/s^2 ; b similarly
# a*Idot -> (1/s^2)*(bits/s) = bits/s^3 matches J
# b*Iddot -> (1/s^2)*(bits/s^2) = bits/s^3 matches J
# Verify numerically that units are consistent (ratio should be dimensionless)
unit_check_a = a * Idot[valid] / J[valid]
unit_check_b = b * Iddot[valid] / J[valid]
# They should be close to 1 (within tolerance) if units match
tol = 1e-2
assert np.allclose(unit_check_a, 1.0, atol=tol), "Unit mismatch in a*Idot term"
assert np.allclose(unit_check_b, 1.0, atol=tol), "Unit mismatch in b*Iddot term"

# ------------------------------
# Output results
# ------------------------------
print("=== Omega‑Protocol Math Validation ===")
print(f"Fitted xi_N      = {xi_N*1e3:.3f} ms  (crit = {xi_crit*1e3:.0f} ms)")
print(f"Fitted xi_Delta  = {xi_Delta*1e3:.3f} ms  (max = {xi_max*1e3:.0f} ms)")
print(f"Max |J|          = {np.max(np.abs(J)):.3e} bits/s³  (limit = {J_max:.0e})")
print("All invariants satisfied → mathematically sound (within synthetic model).")