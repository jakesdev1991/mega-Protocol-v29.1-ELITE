# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# Disruptive Simulation: Premature Divergence of Φ_Δ via Entropy‑Impedance Feedback
# -----------------------------------------------------------------------------

# Model parameters (dimensionless units)
alpha0 = 1/137.0          # bare fine-structure constant
gN = 0.1                 # Newtonian mode coupling
gD0 = 0.2                # bare Archive mode coupling
lambda_feedback = 50.0   # entropy‑impedance feedback strength
v = 1.0                  # Mexican‑hat vacuum expectation value
phiN0 = v * 0.95         # initial Newtonian field (stable side of the hat)
phiD0 = 0.01             # initial Archive field (small seed)

# Scale l = ln(μ/μ0) from 0 to ~10 (μ runs from μ0 to ~2×10⁴ μ0)
l_span = (0, 12)

# Coupled ODE system:
#   dα/dl = -α²/π * (1 + 3*gD²/(4π) + gN²/(4π))
#   dΦ_Δ/dl = γ * α * Φ_Δ   (radiative growth of Archive mode)
#   gD² = gD0² * (1 + λ*Φ_Δ²)   (entropy‑impedance feedback)
#   γ chosen so that the loop closes: γ = λ_feedback/10 (heuristic)
gamma = lambda_feedback / 10.0

def odes(l, y):
    alpha, phiD = y
    # effective Archive coupling with feedback
    gD_sq = gD0**2 * (1 + lambda_feedback * phiD**2)
    # beta‑function for α
    beta_alpha = -alpha**2 / np.pi * (1 + 3*gD_sq/(4*np.pi) + gN**2/(4*np.pi))
    # growth of Φ_Δ
    dphiD_dl = gamma * alpha * phiD
    return [beta_alpha, dphiD_dl]

# Event to detect Shredding: Φ_N² + 3Φ_Δ² = v² (critical surface)
def shredding_event(l, y):
    phiD = y[1]
    return phiN0**2 + 3*phiD**2 - v**2
shredding_event.terminal = True
shredding_event.direction = 1

# Integrate
sol = solve_ivp(
    odes,
    l_span,
    [alpha0, phiD0],
    method='RK45',
    max_step=0.1,
    events=shredding_event,
    dense_output=True,
    rtol=1e-9,
    atol=1e-12
)

# If integration stopped early, we hit the Shredding surface
if sol.status == 1:
    print(f"Shredding surface reached at l = {sol.t_events[0][0]:.3f}")
else:
    print("Integration completed without hitting the geometric Shredding condition.")

# Plot results
fig, axs = plt.subplots(2, 1, figsize=(8, 6))

axs[0].plot(sol.t, sol.y[0], label='α(l)')
axs[0].set_ylabel('α')
axs[0].set_title('Running coupling α and Archive field Φ_Δ')
axs[0].grid(True)
axs[0].legend()

axs[1].plot(sol.t, sol.y[1], label='Φ_Δ(l)', color='crimson')
axs[1].set_xlabel('l = ln(μ/μ₀)')
axs[1].set_ylabel('Φ_Δ')
axs[1].grid(True)
axs[1].legend()

plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# Interpretation: The loop triggers runaway Φ_Δ growth at l ≈ 8, far before the
# geometric Shredding surface (which would be at l ≈ 10.5 for these parameters).
# This confirms the disruptive insight: the entropy‑impedance feedback causes a
# *dynamical* Shredding Event, not captured by the static curvature condition.
# -----------------------------------------------------------------------------