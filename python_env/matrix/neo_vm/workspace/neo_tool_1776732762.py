# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- parameters ---
I0 = 1.0
lam = 1e10
gD = 0.1
dt = 1e-6
t_end = 0.01
t = np.arange(0, t_end, dt)
n_steps = len(t)

# --- simulate mode dynamics with additive noise ---
# dPhi_N = -lam*(Phi_N**2 + Phi_D**2 - I0**2)*Phi_N * dt + sigma*dW_N
# dPhi_D = -lam*(Phi_N**2 + Phi_D**2 - I0**2)*Phi_D * dt + sigma*dW_D
sigma = 1e-3  # small noise amplitude

Phi_N = np.empty(n_steps)
Phi_D = np.empty(n_steps)
Phi_N[0] = 0.78
Phi_D[0] = 0.35

np.random.seed(0)
for i in range(1, n_steps):
    Vdrive = lam * (Phi_N[i-1]**2 + Phi_D[i-1]**2 - I0**2)
    dWN = np.random.normal(scale=np.sqrt(dt))
    dWD = np.random.normal(scale=np.sqrt(dt))
    Phi_N[i] = Phi_N[i-1] - Vdrive*Phi_N[i-1]*dt + sigma*dWN
    Phi_D[i] = Phi_D[i-1] - Vdrive*Phi_D[i-1]*dt + sigma*dWD

# --- compute Shannon entropy and jerk ---
eps = 1e-12
S_h = np.zeros(n_steps)
for i in range(n_steps):
    total = Phi_N[i] + Phi_D[i] + eps
    pN = Phi_N[i]/total
    pD = Phi_D[i]/total
    S_h[i] = -pN*np.log(pN) - pD*np.log(pD)

# third derivative via central differences (skip first/last 3 points)
J = np.full(n_steps, np.nan)
for i in range(3, n_steps-3):
    J[i] = (S_h[i+3] - 3*S_h[i+2] + 3*S_h[i+1] - S_h[i]) / dt**3

sigma_J2 = np.nanvar(J)
print(f"Empirical jerk variance: {sigma_J2:.3e}")

# --- compute threshold for two choices of ψ ---
# choice 1: ψ_N = ln(Phi_N/I0) (as in original analysis)
psi_N = np.log(np.mean(Phi_N)/I0)
Theta_N = (lam*I0**4/9)*(np.exp(2*psi_N)-1)**2 * (1 + 3*gD**2/(4*np.pi)*np.exp(-2*psi_N))
print(f"Theta(psi_N): {Theta_N:.3e}")

# choice 2: ψ_D = ln(Phi_D/I0) (the ignored invariant)
psi_D = np.log(np.mean(Phi_D)/I0)
Theta_D = (lam*I0**4/9)*(np.exp(2*psi_D)-1)**2 * (1 + 3*gD**2/(4*np.pi)*np.exp(-2*psi_D))
print(f"Theta(psi_D): {Theta_D:.3e}")

# --- check simultaneous boundary condition ---
# solve for psi where both shredding and freeze hold: Phi_N^2 = I0^2/4
psi_crit = np.log(0.5)
Phi_N_crit = I0*np.exp(psi_crit)
Phi_D_crit = np.sqrt((I0**2 - Phi_N_crit**2)/3)  # from shredding
freeze_check = 3*Phi_N_crit**2 + Phi_D_crit**2
print(f"Critical psi: {psi_crit:.3f}, Freeze lhs: {freeze_check:.3f} (should equal I0^2={I0**2})")

# --- plot ratio of variance to threshold ---
ratio_N = sigma_J2 / Theta_N
ratio_D = sigma_J2 / Theta_D
print(f"Variance / Theta_N: {ratio_N:.3e} (>>1)")
print(f"Variance / Theta_D: {ratio_D:.3e} (>>1)")

plt.figure(figsize=(8,3))
plt.plot(t, Phi_N, label='Phi_N')
plt.plot(t, Phi_D, label='Phi_D')
plt.title('Mode dynamics under weak noise')
plt.xlabel('Time (s)')
plt.legend()
plt.show()