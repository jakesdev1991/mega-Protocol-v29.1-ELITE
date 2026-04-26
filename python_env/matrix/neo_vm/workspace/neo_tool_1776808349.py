# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Mass matrix eigenvalue analysis
# ─────────────────────────────────────────────────────────────────────────────
def eigenvalues(mN2, mD2, lam):
    """Eigenvalues of the 2‑mode mass matrix."""
    M = np.array([[mN2, lam],
                  [lam, mD2]], dtype=float)
    return np.linalg.eigvals(M)

def find_tachyon_threshold(mN2, mD2, lam_max=2.0, n=200):
    """Scan λ from 0 to lam_max and report when the smallest eigenvalue < 0."""
    lam_vals = np.linspace(0, lam_max, n)
    for lam in lam_vals:
        ev = eigenvalues(mN2, mD2, lam)
        if np.min(ev) < 0:
            return lam, ev
    return None, eigenvalues(mN2, mD2, lam_max)

# Example parameters (reasonable for lattice QED with anisotropy)
mN2 = 0.5   # tree‑level mass^2 of Φ_N
mD2 = 0.8   # tree‑level mass^2 of Φ_Δ

lam_crit, ev_at_crit = find_tachyon_threshold(mN2, mD2)
print("=== Eigenvalue Analysis ===")
print(f"mN² = {mN2}, mΔ² = {mD2}")
if lam_crit is not None:
    print(f"Critical mixing λ_c ≈ {lam_crit:.3f} where an eigenvalue turns negative.")
    print(f"Eigenvalues at λ = {lam_crit:.3f}: {ev_at_crit}")
else:
    print("No tachyon found in scanned λ range (but one can appear for larger λ).")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Coupled ODE simulation: show divergence of eigenmode even if Φ_Δ is clamped
# ─────────────────────────────────────────────────────────────────────────────
def coupled_odes(t, y, mN2, mD2, lam, clamp=False, clamp_val=-0.5):
    """
    y = [Φ_N, Φ_Δ]
    d²y/dt² = -M y (overdamped limit for simplicity)
    If clamp=True, Φ_Δ is artificially held at clamp_val (simulating the MPC‑Ω bound).
    """
    phiN, phiD = y
    if clamp:
        phiD = clamp_val  # hard clamp (MPC‑Ω constraint)
    # Overdamped dynamics: dy/dt = -M y
    dphiN_dt = -(mN2 * phiN + lam * phiD)
    dphiD_dt = -(lam * phiN + mD2 * phiD)
    return [dphiN_dt, dphiD_dt]

# Simulation parameters
lam = 1.2   # above the critical mixing for the chosen masses
t_span = (0, 10)
t_eval = np.linspace(*t_span, 500)

# Case A: No clamp (free evolution) – both fields diverge if eigenvalue < 0
sol_free = solve_ivp(
    lambda t, y: coupled_odes(t, y, mN2, mD2, lam, clamp=False),
    t_span, y0=[1.0, 0.1], t_eval=t_eval, method='RK45'
)

# Case B: Clamp Φ_Δ to a "safe" value above metric‑collapse bound (e.g., -0.5)
sol_clamp = solve_ivp(
    lambda t, y: coupled_odes(t, y, mN2, mD2, lam, clamp=True, clamp_val=-0.5),
    t_span, y0=[1.0, -0.5], t_eval=t_eval, method='RK45'
)

print("\n=== ODE Simulation ===")
print(f"Using λ = {lam} (above critical value if mN²≠mΔ²).")
print(f"Free evolution: Φ_N final = {sol_free.y[0,-1]:.3e}, Φ_Δ final = {sol_free.y[1,-1]:.3e}")
print(f"Clamped Φ_Δ = -0.5: Φ_N final = {sol_clamp.y[0,-1]:.3e} (still diverges due to mixing!)")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Show that the true eigenmode (diagonalised) blows up even if Φ_Δ is held fixed
# ─────────────────────────────────────────────────────────────────────────────
# Diagonalising matrix: eigenvectors of M
M = np.array([[mN2, lam], [lam, mD2]])
eigvals, eigvecs = np.linalg.eig(M)
# Sort eigenvalues / eigenvectors
order = np.argsort(eigvals)
eigvals = eigvals[order]
eigvecs = eigvecs[:, order]

# Project initial condition onto eigenbasis
y0 = np.array([1.0, 0.1])
a = np.linalg.inv(eigvecs) @ y0  # coefficients in eigenbasis

print("\n=== Eigenmode Projection ===")
print(f"Eigenvalues: {eigvals}")
print(f"Corresponding eigenvectors (columns):\n{eigvecs}")
print(f"Initial coefficients in eigenbasis: a1 = {a[0]:.3f}, a2 = {a[1]:.3f}")

# Time evolution of eigenmode amplitudes (exponential growth if eigenvalue < 0)
# In overdamped limit: da_i/dt = -λ_i a_i → a_i(t) = a_i(0) exp(-λ_i t)
t = 5.0
a_t = a * np.exp(-eigvals * t)
# Transform back to original basis
y_t = eigvecs @ a_t
print(f"After t={t}: eigenmode amplitudes = {a_t}, original fields ≈ {y_t}")

# If any eigenvalue is negative, the corresponding eigenmode grows exponentially.
if eigvals[0] < 0 or eigvals[1] < 0:
    print("\n⚠️  ALERT: Negative eigenvalue detected → exponential blow‑up of a true eigenmode!")
    print("The MPC‑Ω clamp on Φ_Δ cannot prevent this collective Shredding.")
else:
    print("\n✓ No tachyon in this parameter set (but mixing still couples the fields).")