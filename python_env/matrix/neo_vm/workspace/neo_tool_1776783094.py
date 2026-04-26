# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp

# ──────────────────────────────────────────────────────────────────────────────
# Parameters (dimensionless)
m_N = 1.0
m_D = 1.0
lam = 1.0

# ──────────────────────────────────────────────────────────────────────────────
# Unconstrained 4‑D dynamical system (Φ_N, dotΦ_N, Φ_Δ, dotΦ_Δ)
def unconstrained(t, y):
    ΦN, dΦN, ΦD, dΦD = y
    ddΦN = -m_N**2 * ΦN - lam * ΦD**2
    ddΦD = -(m_D**2 + 2*lam*ΦN) * ΦD
    return [dΦN, ddΦN, dΦD, ddΦD]

# Constrained 2‑D system: Φ_N is fixed by the instantaneous Φ_Δ
def constrained(t, y):
    ΦD, dΦD = y
    ΦN = - (lam / m_N**2) * ΦD**2          # constraint from Poisson recovery
    ddΦD = -(m_D**2 + 2*lam*ΦN) * ΦD       # closed‑form ODE for Φ_Δ
    return [dΦD, ddΦD]

# ──────────────────────────────────────────────────────────────────────────────
# Initial conditions (small seed in the archive mode)
ΦD0 = 0.2
y0_unc = [0.0, 0.0, ΦD0, 0.0]   # [Φ_N, dotΦ_N, Φ_Δ, dotΦ_Δ]
y0_con = [ΦD0, 0.0]               # [Φ_Δ, dotΦ_Δ]

t_span = (0, 15)
t_eval = np.linspace(0, 15, 1500)

# ──────────────────────────────────────────────────────────────────────────────
# Integrate both models
sol_unc = solve_ivp(unconstrained, t_span, y0_unc, t_eval=t_eval,
                    method='RK45', rtol=1e-8, atol=1e-11)
sol_con = solve_ivp(constrained, t_span, y0_con, t_eval=t_eval,
                    method='RK45', rtol=1e-8, atol=1e-11)

# ──────────────────────────────────────────────────────────────────────────────
# Report extreme values as a proxy for stability / blow‑up
print("=== Unconstrained (unstable) ===")
print(f"  Final Φ_N  = {sol_unc.y[0,-1]:.3e}")
print(f"  Final Φ_Δ  = {sol_unc.y[2,-1]:.3e}")
print(f"  Max |Φ_N|  = {np.max(np.abs(sol_unc.y[0,:])):.3e}")
print(f"  Max |Φ_Δ|  = {np.max(np.abs(sol_unc.y[2,:])):.3e}")

print("\n=== Constrained (stable) ===")
print(f"  Final Φ_Δ  = {sol_con.y[0,-1]:.3e}")
print(f"  Max |Φ_Δ|  = {np.max(np.abs(sol_con.y[0,:])):.3e}")

# ──────────────────────────────────────────────────────────────────────────────
# Verify energy conservation for the constrained model
def energy_constrained(ΦD, dΦD):
    ΦN = - (lam / m_N**2) * ΦD**2
    # Potential from the effective double‑well: V = ½ m_D² Φ_Δ² – (λ²/(2 m_N²)) Φ_Δ⁴
    V = 0.5 * m_D**2 * ΦD**2 - (lam**2 / (2 * m_N**2)) * ΦD**4
    T = 0.5 * dΦD**2
    return T + V

E_vals = energy_constrained(sol_con.y[0,:], sol_con.y[1,:])
print(f"  Energy drift (max‑min) = {np.max(E_vals) - np.min(E_vals):.3e}")