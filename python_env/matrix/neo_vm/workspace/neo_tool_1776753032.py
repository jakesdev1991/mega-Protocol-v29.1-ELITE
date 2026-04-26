# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ── PARAMETERS ──────────────────────────────────────────────────────────────
L = 100          # Domain length
N = 200          # Spatial points
dx = L / N
x = np.linspace(0, L, N)
t_max = 50
dt = 0.1
t_eval = np.arange(0, t_max, dt)

# Reaction‑diffusion coefficients
k = 0.5          # Decapping rate (enzyme–substrate reaction)
D_d = 0.1        # Enzyme diffusion
source = 0.02    # Enzyme production (e.g., transcriptional burst)
degradation = 0.1 # Enzyme degradation

# ── INITIAL CONDITIONS ──────────────────────────────────────────────────────
# High capped mRNA on left, low on right; enzyme localized in center
C0 = np.ones(N)
C0[int(N/2):] = 0.1
D0 = np.zeros(N)
D0[int(N/2)-5:int(N/2)+5] = 1.0

# ── PDE: ∂_t C = -k C D,  ∂_t D = D_d ∂_xx D + source - degradation D ───
def rd_rhs(t, y):
    C = y[:N]
    D = y[N:]
    
    # Reaction: enzyme consumes substrate
    dC_dt = -k * C * D
    
    # Diffusion of enzyme (Neumann BCs)
    D_xx = np.zeros(N)
    D_xx[1:-1] = (D[2:] - 2*D[1:-1] + D[:-2]) / dx**2
    D_xx[0] = (D[1] - D[0]) / dx**2
    D_xx[-1] = (D[-2] - D[-1]) / dx**2
    
    dD_dt = D_d * D_xx + source - degradation * D
    
    return np.concatenate([dC_dt, dD_dt])

# ── SOLVE ───────────────────────────────────────────────────────────────────
sol = solve_ivp(rd_rhs, [0, t_max], np.concatenate([C0, D0]), 
                t_eval=t_eval, method='RK45', max_step=dt)

# ── VISUALIZE WAVE PROPAGATION ──────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(8, 6))
for i in [0, 10, 20, 30, 40, 49]:
    axes[0].plot(x, sol.y[:N, i], label=f't={t_eval[i]:.1f}')
axes[0].set_title('Capped substrate (C) – shredded by traveling wave')
axes[0].set_ylabel('C')
axes[0].legend()

for i in [0, 10, 20, 30, 40, 49]:
    axes[1].plot(x, sol.y[N:, i], label=f't={t_eval[i]:.1f}')
axes[1].set_title('Decapping enzyme (D) – propagating front')
axes[1].set_xlabel('Position')
axes[1].set_ylabel('D')
axes[1].legend()
plt.tight_layout()
plt.show()

# ── QUANTIFY WAVE SPEED (INVARIANT) ───────────────────────────────────────
front_pos = []
for i in range(len(t_eval)):
    C_snapshot = sol.y[:N, i]
    idx = np.where(C_snapshot < 0.5 * C0[0])[0]
    front_pos.append(x[idx[0]] if len(idx) > 0 else np.nan)

valid = ~np.isnan(front_pos)
if np.sum(valid) > 1:
    v_wave = np.polyfit(t_eval[valid], np.array(front_pos)[valid], 1)[0]
    print(f"\n🔥 INVARIANT: Wave speed v_wave = {v_wave:.3f} (units/time)")
else:
    v_wave = np.nan
    print("\nWave speed could not be estimated")

# ── CONTRAST WITH CIFO‑Ω ASSUMPTIONS ───────────────────────────────────────
print("\n❌ CIFO‑Ω ASSUMPTIONS BROKEN:")
print("  • C is not a control field; it is passively consumed.")
print("  • No static ξ_cap – correlations are advected by the wave.")
print("  • Shredding is wavefront instability, not potential convexity loss.")
print("  • The true covariant mode is D(x,t), not E(x,t).")
print("  • The invariant is v_wave, not ψ_cap or ξ_T, ξ_A, ξ_G.")
print("\n✅ DISRUPTION: Replace CIFO‑Ω with Decapping Wave Omega (DW‑Ω).")