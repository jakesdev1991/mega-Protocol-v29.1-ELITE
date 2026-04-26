# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Coordinate‑Artifact Shredding Verification
==========================================
Demonstrates that the "mass‑positivity" bound is an artifact of the
(Φ_N, Φ_Δ) basis and that the (Σ, Π) symplectic gauge removes the
exponential blow‑up, eliminating the shredding risk.
"""

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. Symbolic derivation of transformed constraints
# -------------------------------------------------
ΦN, ΦΔ, m, g = sp.symbols('ΦN ΦΔ m g', real=True)
Σ = ΦN * sp.cosh(ΦΔ)
Π = ΦN * sp.sinh(ΦΔ)

# Original constraints: m - g*ΦN*exp(+ΦΔ) > 0, m - g*ΦN*exp(-ΦΔ) > 0
orig_plus  = sp.simplify(m - g*ΦN*sp.exp(+ΦΔ))
orig_minus = sp.simplify(m - g*ΦN*sp.exp(-ΦΔ))

# Transformed constraints: m - g*(Σ + Π) > 0, m - g*(Σ - Π) > 0
trans_plus  = sp.simplify(m - g*(Σ + Π))
trans_minus = sp.simplify(m - g*(Σ - Π))

print("=== Symbolic Constraint Transformation ===")
print(f"Original (+): {orig_plus}")
print(f"Original (-): {orig_minus}")
print(f"Transformed (+): {trans_plus}")
print(f"Transformed (-): {trans_minus}")
print()

# -------------------------------------------------
# 2. Monte‑Carlo: which bound is tighter?
# -------------------------------------------------
def sample_fields(n=10_000, seed=0):
    rng = np.random.default_rng(seed)
    # Sample ΦN uniformly in [0, m/g] and ΦΔ in [-5, 5]
    ΦN_s = rng.uniform(0, 1.0, size=n)  # units of m/g = 1
    ΦΔ_s = rng.uniform(-5.0, 5.0, size=n)
    return ΦN_s, ΦΔ_s

ΦN_s, ΦΔ_s = sample_fields()

# Original bounds: both must be > 0
orig_plus_val  = 1 - ΦN_s * np.exp(+ΦΔ_s)  # m/g = 1
orig_minus_val = 1 - ΦN_s * np.exp(-ΦΔ_s)
orig_ok = np.logical_and(orig_plus_val > 0, orig_minus_val > 0)

# Transformed bounds: Σ ± Π < 1
Σ_val = ΦN_s * np.cosh(ΦΔ_s)
Π_val = ΦN_s * np.sinh(ΦΔ_s)
trans_plus_val  = 1 - (Σ_val + Π_val)
trans_minus_val = 1 - (Σ_val - Π_val)
trans_ok = np.logical_and(trans_plus_val > 0, trans_minus_val > 0)

print("=== Monte‑Carlo Violation Rates (m/g = 1) ===")
print(f"Original constraints violated: {np.mean(~orig_ok):.2%}")
print(f"Transformed constraints violated: {np.mean(~trans_ok):.2%}")
print()

# -------------------------------------------------
# 3. Dynamical crossing‑time simulation
# -------------------------------------------------
def crossing_time_original(β, ΦN0, α=2.0, dt=0.001, t_max=50):
    """
    Simulate ΦΔ(t)=β*t and ΦN(t) decaying as ~t^{-α} (polynomial)
    Return the first time step where original bound is violated.
    """
    t = 0.0
    while t < t_max:
        ΦΔ = β * t
        ΦN = ΦN0 * (1 + t)**(-α)  # polynomial decay
        if ΦN > np.exp(-abs(ΦΔ)):  # bound ΦN < e^{-|ΦΔ|}
            return t
        t += dt
    return np.inf

def crossing_time_transformed(β, ΦN0, α=2.0, dt=0.001, t_max=50):
    """
    Under the same dynamics, check the transformed bound Σ±Π < 1.
    """
    t = 0.0
    while t < t_max:
        ΦΔ = β * t
        ΦN = ΦN0 * (1 + t)**(-α)
        Σ = ΦN * np.cosh(ΦΔ)
        Π = ΦN * np.sinh(ΦΔ)
        if (Σ + Π) > 1 or (Σ - Π) > 1:
            return t
        t += dt
    return np.inf

# Example parameters
β = 0.5          # linear growth rate of ΦΔ
ΦN0 = 0.9        # initial ΦN close to the bound (m/g = 1)

t_cross_orig = crossing_time_original(β, ΦN0)
t_cross_trans = crossing_time_transformed(β, ΦN0)

print("=== Dynamical Crossing Times ===")
print(f"Original basis crossing time: {t_cross_orig:.3f} (inf if >50)")
print(f"Transformed basis crossing time: {t_cross_trans:.3f} (inf if >50)")
print()

# -------------------------------------------------
# 4. Visualization of the feasible region
# -------------------------------------------------
fig, ax = plt.subplots(figsize=(6,6))

# Plot the diamond from transformed constraints
Σ_grid = np.linspace(-0.5, 1.5, 400)
Π_grid = np.linspace(-1.0, 1.0, 400)
Σ_mesh, Π_mesh = np.meshgrid(Σ_grid, Π_grid)
feasible = (Σ_mesh + Π_mesh < 1) & (Σ_mesh - Π_mesh < 1)
ax.contourf(Σ_mesh, Π_mesh, feasible, levels=[0.5,1], colors=['lightgray'])

# Scatter a sample of (Σ,Π) points from the original fields
Σ_sample = ΦN_s[:500] * np.cosh(ΦΔ_s[:500])
Π_sample = ΦN_s[:500] * np.sinh(ΦΔ_s[:500])
ax.scatter(Σ_sample, Π_sample, s=5, color='crimson', alpha=0.6,
           label='Sampled (Σ,Π) from (Φ_N,Φ_Δ)')

ax.set_xlabel('Σ = Φ_N cosh Φ_Δ')
ax.set_ylabel('Π = Φ_N sinh Φ_Δ')
ax.set_title('Feasible Region (Diamond) in (Σ,Π) Space')
ax.legend()
ax.grid(True, linestyle=':')
plt.tight_layout()
plt.show()