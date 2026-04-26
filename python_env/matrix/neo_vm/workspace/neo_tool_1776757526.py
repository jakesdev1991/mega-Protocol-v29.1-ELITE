# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# 1. Original (gauge‑variant) RG equations
#    Φ_N' = η_N Φ_N (1‑Φ_N²) – κ Φ_Δ²
#    Φ_Δ' = η_Δ Φ_Δ (1‑Φ_Δ²) + κ Φ_N Φ_Δ
# ------------------------------------------------------------------
def original_rg(L, y, η_N=1.0, η_Δ=-1.0, κ=0.5):
    ΦN, ΦΔ = y
    dΦN = η_N * ΦN * (1.0 - ΦN**2) - κ * ΦΔ**2
    dΦΔ = η_Δ * ΦΔ * (1.0 - ΦΔ**2) + κ * ΦN * ΦΔ
    return [dΦN, dΦΔ]

# ------------------------------------------------------------------
# 2. Extended RG equations with a minimal entropy‑gauge regulator X
#    dΦN/dL = η_N ΦN (1‑ΦN²) – κ ΦΔ²
#    dΦΔ/dL = η_Δ ΦΔ (1‑ΦΔ²) + κ ΦN ΦΔ – α X ΦΔ
#    dX/dL   = –γ X + ν ΦΔ²          (regulator grows with ΦΔ²)
# ------------------------------------------------------------------
def extended_rg(L, y, η_N=1.0, η_Δ=-1.0, κ=0.5,
                α=1.0, γ=1.0, ν=1.0):
    ΦN, ΦΔ, X = y
    dΦN = η_N * ΦN * (1.0 - ΦN**2) - κ * ΦΔ**2
    dΦΔ = η_Δ * ΦΔ * (1.0 - ΦΔ**2) + κ * ΦN * ΦΔ - α * X * ΦΔ
    dX  = -γ * X + ν * ΦΔ**2
    return [dΦN, dΦΔ, dX]

# ------------------------------------------------------------------
# 3. Integrate the original system up to a point where ΦΔ explodes
# ------------------------------------------------------------------
L_span = (0.0, 3.0)          # integrate from L=0 to L=3
y0_original = [0.1, 0.2]     # small initial conditions

sol_original = solve_ivp(
    lambda L, y: original_rg(L, y),
    L_span, y0_original,
    method='RK45',
    max_step=0.01,
    dense_output=True
)

# ------------------------------------------------------------------
# 4. Integrate the extended system for comparison
# ------------------------------------------------------------------
y0_extended = [0.1, 0.2, 0.0]   # start with regulator X=0
sol_extended = solve_ivp(
    lambda L, y: extended_rg(L, y),
    L_span, y0_extended,
    method='RK45',
    max_step=0.01,
    dense_output=True
)

# ------------------------------------------------------------------
# 5. Post‑process: compute the gauge‑invariant combination ℐ = ΦN + (κ/(2|η_Δ|)) ΦΔ²
# ------------------------------------------------------------------
L_grid = np.linspace(0.0, 2.5, 500)
ΦN_orig = sol_original.sol(L_grid)[0]
ΦΔ_orig = sol_original.sol(L_grid)[1]
ℐ_orig = ΦN_orig + (0.5 / (2.0 * abs(-1.0))) * ΦΔ_orig**2   # κ/(2|η_Δ|) = 0.5/(2*1) = 0.25

ΦN_ext = sol_extended.sol(L_grid)[0]
ΦΔ_ext = sol_extended.sol(L_grid)[1]
ℐ_ext = ΦN_ext + (0.5 / (2.0 * abs(-1.0))) * ΦΔ_ext**2

# ------------------------------------------------------------------
# 6. Plot the results
# ------------------------------------------------------------------
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Original ΦN, ΦΔ
axs[0, 0].plot(L_grid, ΦN_orig, label='Φ_N (original)')
axs[0, 0].plot(L_grid, ΦΔ_orig, label='Φ_Δ (original)')
axs[0, 0].set_xlabel('L = ln(q/q₀)')
axs[0, 0].set_ylabel('Field amplitude')
axs[0, 0].set_title('Original gauge‑variant fields')
axs[0, 0].legend()
axs[0, 0].grid(True)

# Original invariant ℐ
axs[0, 1].plot(L_grid, ℐ_orig, label='ℐ = Φ_N + (κ/(2|η_Δ|))Φ_Δ²', color='green')
axs[0, 1].set_xlabel('L = ln(q/q₀)')
axs[0, 1].set_ylabel('Invariant amplitude')
axs[0, 1].set_title('Gauge‑invariant observable (original system)')
axs[0, 1].legend()
axs[0, 1].grid(True)

# Extended ΦN, ΦΔ, X
axs[1, 0].plot(L_grid, ΦN_ext, label='Φ_N (extended)')
axs[1, 0].plot(L_grid, ΦΔ_ext, label='Φ_Δ (extended)')
axs[1, 0].plot(L_grid, sol_extended.sol(L_grid)[2], label='X (regulator)', linestyle='--')
axs[1, 0].set_xlabel('L = ln(q/q₀)')
axs[1, 0].set_ylabel('Field amplitude')
axs[1, 0].set_title('Extended system with regulator')
axs[1, 0].legend()
axs[1, 0].grid(True)

# Extended invariant ℐ
axs[1, 1].plot(L_grid, ℐ_ext, label='ℐ (extended)', color='green')
axs[1, 1].set_xlabel('L = ln(q/q₀)')
axs[1, 1].set_ylabel('Invariant amplitude')
axs[1, 1].set_title('Gauge‑invariant observable (extended system)')
axs[1, 1].legend()
axs[1, 1].grid(True)

plt.tight_layout()
plt.show()

# ------------------------------------------------------------------
# 7. Print the approximate location of the singularity (where ΦΔ > 1e4)
# ------------------------------------------------------------------
# Find the last L where ΦΔ is still finite in the original run
mask = np.isfinite(ΦΔ_orig)
if np.any(mask):
    L_last = L_grid[mask][-1]
    print(f"Original ΦΔ diverges near L ≈ {L_last:.3f} (q/q₀ ≈ {np.exp(L_last):.2e})")
else:
    print("No finite region found – divergence already at L=0?")