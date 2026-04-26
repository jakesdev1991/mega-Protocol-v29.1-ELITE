# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Engine's data (normalized)
psi = np.log(0.78)  # -0.248
phi_delta = 0.35
dpsi_dt = 2.69e3
ddpsi_dt2 = -1.74e6  # corrected sign
xi = 4.9e-4
dt = xi

# Entropy function
def S_h(psi, phi_delta):
    e_psi = np.exp(psi)
    total = e_psi + phi_delta
    p_N = e_psi / total
    p_D = phi_delta / total
    return -(p_N * np.log(p_N) + p_D * np.log(p_D))

# Finite difference for nth derivative
def info_derivative(n, psi_series, phi_series, dt):
    """Compute nth time derivative of entropy"""
    S_series = [S_h(p, d) for p, d in zip(psi_series, phi_series)]
    if n == 1:
        return (S_series[-1] - S_series[-2]) / dt
    elif n == 2:
        return (S_series[-1] - 2*S_series[-2] + S_series[-3]) / dt**2
    elif n == 3:
        return (S_series[-1] - 3*S_series[-2] + 3*S_series[-3] - S_series[-4]) / dt**3
    elif n == 4:
        return (S_series[-1] - 4*S_series[-2] + 6*S_series[-3] - 4*S_series[-4] + S_series[-5]) / dt**4

# Simulate time series (small perturbations around operating point)
t_points = 5
psi_series = [psi + 0.01*np.sin(i*0.1) for i in range(t_points)]
phi_series = [phi_delta + 0.005*np.cos(i*0.1) for i in range(t_points)]

# Compute different derivative orders
acc = info_derivative(2, psi_series, phi_series, dt)
jerk = info_derivative(3, psi_series, phi_series, dt)
jounce = info_derivative(4, psi_series, phi_series, dt)

print(f"Informational Acceleration: {acc:.3e} s⁻²")
print(f"Informational Jerk: {jerk:.3e} s⁻³")
print(f"Informational Jounce: {jounce:.3e} s⁻⁴")

# Show arbitrary stability verdicts
# Using Engine's "threshold" logic but with different derivative orders
def stability_verdict(quantity, threshold):
    return "UNSTABLE" if abs(quantity) > threshold else "STABLE"

# Arbitrary thresholds for demonstration
print(f"\nStability by Acceleration: {stability_verdict(acc, 1e3)}")
print(f"Stability by Jerk: {stability_verdict(jerk, 1e12)}")
print(f"Stability by Jounce: {stability_verdict(jounce, 1e21)}")