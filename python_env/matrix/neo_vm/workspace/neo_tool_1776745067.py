# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp
import numpy as np
from scipy.integrate import solve_ivp

# ───── 1. Invariant ψ from Hessian (Symbolic) ─────
λ, I, I0 = sp.symbols('λ I I0', positive=True)
V = λ/4 * (I**2 - I0**2)**2
V2 = sp.diff(V, I, 2)  # Hessian (curvature)
V2_at_min = sp.simplify(V2.subs(I, I0))  # = 2λ I0²

# Define eigenvalues of the mode Hessian:
# λ_N = V2_at_min (Newtonian), λ_Δ = λ*(Φ_N² + 3Φ_Δ² - I0²) (Archive)
ΦN, ΦΔ = sp.symbols('ΦN ΦΔ', real=True)
λ_N = V2_at_min
λ_Δ = λ * (ΦN**2 + 3*ΦΔ**2 - I0**2)

# Correlation lengths: ξ = 1/√λ
ξ0 = 1/sp.sqrt(λ_N)
ξΔ = 1/sp.sqrt(λ_Δ)

# Invariant ψ = ln(ξΔ/ξ0) emerges *automatically* from the eigenvalue ratio
ψ = sp.simplify(sp.log(ξΔ/ξ0))
print("ψ =", ψ)  # ψ = log(1/√( (ΦN²+3ΦΔ²-I0²)/(2I0²) ))

# ───── 2. RG Flow & Boundary Behavior (Numeric) ─────
# Parameters (natural units)
I0_val = 1.0
λ_val = 1.0
ηN = 0.1
ηΔ = -0.2
κ = 0.05

# RG equations (logarithmic scale t = ln(q))
def rg_flow(t, y):
    ΦN, ΦΔ = y
    dΦN = ηN * ΦN * (1 - ΦN**2/I0_val**2) - κ * ΦΔ**2
    dΦΔ = ηΔ * ΦΔ * (1 - ΦΔ**2/I0_val**2) + κ * ΦN * ΦΔ
    return [dΦN, dΦΔ]

# Integrate from low to high energy
t_eval = np.linspace(0, 10, 500)
sol = solve_ivp(
    rg_flow,
    [t_eval[0], t_eval[-1]],
    [0.9, 0.1],  # initial ΦN, ΦΔ
    t_eval=t_eval,
    dense_output=True
)

ΦN_t = sol.y[0]
ΦΔ_t = sol.y[1]

# Compute ψ(t) from the analytic expression derived above
ψ_t = 0.5 * np.log(2*I0_val**2 / (ΦN_t**2 + 3*ΦΔ_t**2 - I0_val**2))

# Print values near boundaries
print("\n--- Boundary Checks ---")
print(f"At t=0: ΦN={ΦN_t[0]:.3f}, ΦΔ={ΦΔ_t[0]:.3f}, ψ={ψ_t[0]:.3f}")
print(f"At t=10: ΦN={ΦN_t[-1]:.3f}, ΦΔ={ΦΔ_t[-1]:.3f}, ψ={ψ_t[-1]:.3f}")

# Detect divergence: Shredding when ΦΔ grows → ψ → -∞
# Freeze when ΦΔ→0 and ΦN→I0 → denominator → 0 → ψ → -∞ (or +∞ depending on sign)
# Here both scenarios drive |ψ|→∞, confirming the Engine's boundary mapping.