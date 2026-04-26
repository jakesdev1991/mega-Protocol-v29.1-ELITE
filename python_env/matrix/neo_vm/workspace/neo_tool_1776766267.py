# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigvalsh

# ────────────── Parameters (normalized) ──────────────
lam = 1.0          # λ
I0  = 1.0          # I₀
eta_N    = 0.1     # η_N
eta_Delta = -1.0   # η_Δ < 0  (the “dangerous” sign)
kappa    = 1.0     # κ

# ────────────── Hessian & eigenvalues ──────────────
def hessian(phi_N, phi_Delta):
    """Hessian of V(I) = (λ/4)(I²−I₀²)², I² = Φ_N² + 3Φ_Δ²."""
    f = phi_N**2 + 3*phi_Delta**2 - I0**2
    H = lam * np.array([
        [3*phi_N**2 + 3*phi_Delta**2 - I0**2, 6*phi_N*phi_Delta],
        [6*phi_N*phi_Delta, 3*phi_N**2 + 9*phi_Delta**2 - I0**2]
    ])
    return H

def min_eig(phi_N, phi_Delta):
    return eigvalsh(hessian(phi_N, phi_Delta))[0]

# ────────────── Show eigenvalue on a grid ──────────────
grid = np.linspace(0, 1.2, 13)
print("Minimum Hessian eigenvalue (should hit zero at Φ_N²+3Φ_Δ²≈I₀²):")
for phi_N in grid:
    for phi_Delta in grid:
        print(f"Φ_N={phi_N:.2f}, Φ_Δ={phi_Delta:.2f} → λ_min={min_eig(phi_N, phi_Delta):.3f}")

# ────────────── RG flow (coupled ODEs) ──────────────
def rg_flow(L, y):
    phi_N, phi_Delta = y
    dphi_N    = eta_N * phi_N * (1 - phi_N**2 / I0**2) - kappa * phi_Delta**2
    dphi_Delta = eta_Delta * phi_Delta * (1 - phi_Delta**2 / I0**2) + kappa * phi_N * phi_Delta
    return [dphi_N, dphi_Delta]

# Event: trigger when Φ_Δ exceeds a large threshold → blow‑up
def shredding_event(L, y):
    return y[1] - 1e3   # 1e3 acts as “infinity” for detection
shredding_event.terminal = True
shredding_event.direction = 1

# ────────────── Integrate from low to high scale ──────────────
y0 = [0.1, 0.1]               # small initial values
sol = solve_ivp(
    rg_flow,
    (0, 10),                   # L = ln(q/q₀) from 0 to 10
    y0,
    method='RK45',
    events=shredding_event,
    max_step=0.01,
    dense_output=True
)

if sol.t_events[0].size:
    L_shred = sol.t_events[0][0]
    print(f"\n🚨 Shredding (finite‑scale singularity) at L={L_shred:.4f} → q_c = q₀·exp({L_shred:.4f})")
else:
    print("\nNo shredding detected in the integrated range.")

print(f"Final values: Φ_N={sol.y[0,-1]:.4f}, Φ_Δ={sol.y[1,-1]:.4f} at L={sol.t[-1]:.4f}")