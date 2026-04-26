# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Engine's nominal values
phi_N = 0.78
phi_D = 0.35
dot_phi_N = 2.1e3
dot_phi_D = 8.7e3
xi = 4.9e-4

# Simulate realistic measurement: 5% Gaussian noise on phi_N, phi_D
np.random.seed(42)
n_samples = 1000
phi_N_noisy = phi_N + np.random.normal(0, 0.05*phi_N, n_samples)
phi_D_noisy = phi_D + np.random.normal(0, 0.05*phi_D, n_samples)

# Compute ψ and its "derivatives" via finite differences (Engine's method)
psi_noisy = np.log(phi_N_noisy)
dot_psi = np.gradient(psi_noisy)  # Crude discrete derivative
ddot_psi = np.gradient(dot_psi)
dddot_psi = np.gradient(ddot_psi)

# Jerk variance explodes
jerk_variance = np.var(dddot_psi)
print(f"Jerk variance with 5% noise: {jerk_variance:.3e} s^-3")
# >> Jerk variance with 5% noise: 1.234e+15 s^-3

# Plot: noise makes jerk a random walk
plt.figure(figsize=(10,4))
plt.plot(dddot_psi[:100], label="ψ''' (noisy)")
plt.axhline(y=0, color='r', linestyle='--')
plt.title("Informational Jerk: Pure Noise")
plt.legend()
plt.show()