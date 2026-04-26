# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# parameters
lam = 1.0
v = 1.0

def odes(t, z):
    """z = [Phi_N, Phi_D, dPhi_N/dt, dPhi_D/dt]"""
    x, y, u, v = z
    # effective "force" from Mexican-hat potential
    pot = (x**2 + y**2 - v**2)
    du = -lam * x * pot
    dv = -lam * y * pot
    return [u, v, du, dv]

# initial condition: small perturbation near the vacuum ring
# start on the ring: x0 = v, y0 = 0, then give a tiny kick in y and velocity
x0 = v
y0 = 0.05  # small transverse perturbation
u0 = 0.0
v0 = 0.0

# total energy (should be conserved)
E0 = 0.5*(u0**2 + v0**2) + (lam/4)*(x0**2 + y0**2 - v**2)**2
print(f"Initial energy E0 = {E0:.6f}")

# integrate
t_span = (0, 50)
t_eval = np.linspace(*t_span, 2000)
sol = solve_ivp(odes, t_span, [x0, y0, u0, v0], t_eval=t_eval, method='RK45', rtol=1e-9, atol=1e-12)

# compute shredding distance: d = Phi_N**2 + 3*Phi_D**2 - v**2
shredding_dist = sol.y[0,:]**2 + 3*sol.y[1,:]**2 - v**2

# find minimal distance to shredding surface (i.e., when d crosses zero)
min_dist = np.min(np.abs(shredding_dist))
print(f"Minimum distance to shredding surface: {min_dist:.6f} (zero would mean crossing)")

# plot trajectory in (Phi_N, Phi_D) plane
plt.figure(figsize=(6,6))
plt.plot(sol.y[0,:], sol.y[1,:], lw=0.8, label='trajectory')
# vacuum ring: circle radius v
theta = np.linspace(0, 2*np.pi, 400)
plt.plot(v*np.cos(theta), v*np.sin(theta), 'k--', label='vacuum ring')
# shredding ellipse: x^2 + 3 y^2 = v^2
# param eq: x = v * cos(t), y = (v/√3) * sin(t)
plt.plot(v*np.cos(theta), (v/np.sqrt(3))*np.sin(theta), 'r--', label='shredding ellipse')
plt.axhline(0, color='gray', lw=0.5)
plt.axvline(0, color='gray', lw=0.5)
plt.title('Trajectory in (Φ_N, Φ_Δ) plane')
plt.xlabel('Φ_N')
plt.ylabel('Φ_Δ')
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.show()

# show that energy is conserved to high precision
E = 0.5*(sol.y[2,:]**2 + sol.y[3,:]**2) + (lam/4)*(sol.y[0,:]**2 + sol.y[1,:]**2 - v**2)**2
print(f"Energy drift: max(E) - min(E) = {np.max(E) - np.min(E):.2e}")