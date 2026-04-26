# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for Higher-Order Lattice Polarization
Checks for Shredding instability and Poisson‑recovery violation.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

# ----------------------------------------------------------------------
# Model parameters (can be overridden)
# ----------------------------------------------------------------------
m_N   = 1.0      # Newtonian mode mass
m_Del = 1.0      # Archive mode mass
lam   = 0.5      # coupling lambda (>0 triggers instability)
PhiN0 = 0.0      # initial Phi_N
PhiD0 = 1e-3     # small seed perturbation in Phi_Delta
vN0   = 0.0      # initial velocity Phi_N
vD0   = 0.0      # initial velocity Phi_Delta
t_span = (0, 50) # integration time
t_eval = np.linspace(*t_span, 5000)

# ----------------------------------------------------------------------
# Equations of motion (homogeneous)
# ----------------------------------------------------------------------
def rhs(t, y):
    PhiN, PhiD, vN, vD = y
    aN = - m_N**2 * PhiN - lam * PhiD**2
    aD = - (m_Del**2 + 2 * lam * PhiN) * PhiD
    return [vN, vD, aN, aD]

sol = solve_ivp(rhs, t_span, [PhiN0, PhiD0, vN0, vD0],
                t_eval=t_eval, method='RK45', rtol=1e-9, atol=1e-12)

PhiN = sol.y[0]
PhiD = sol.y[1]

# ----------------------------------------------------------------------
# Shredding detection: exponential growth of Phi_Delta
# ----------------------------------------------------------------------
shred_threshold = 1e3          # arbitrary large value
shred_event = np.any(np.abs(PhiD) > shred_threshold)
shred_time  = sol.t[np.where(np.abs(PhiD) > shred_threshold)[0][0]] if shred_event else None

# ----------------------------------------------------------------------
# Poisson recovery test (1‑D periodic domain)
# ----------------------------------------------------------------------
L = 10.0                # domain length
Nx = 256                # grid points
x = np.linspace(0, L, Nx, endpoint=False)
dx = x[1] - x[0]

# Source term: rho + lambda*PhiD^2 (take rho=0 for simplicity)
source = lam * PhiD**2   # shape (time,)

# Build Laplacian matrix (periodic BCs)
main = -2 * np.ones(Nx)
offs =  np.ones(Nx-1)
Lap = diags([offs, main, offs], [-1, 0, 1], shape=(Nx, Nx))/dx**2
Lap = Lap + diags([1/Nx**2, 1/Nx**2], [-(Nx-1), Nx-1], shape=(Nx, Nx))  # periodic wrap

# Solve Poisson for each time step and check boundedness of PhiN_Poisson
max_Poisson_phiN = 0.0
for t_idx, src in enumerate(source):
    # Solve Lap * phi = src
    phiN_poisson = spsolve(Lap, src)
    max_Poisson_phiN = max(max_Poisson_phiN, np.max(np.abs(phiN_poisson)))

poisson_bounded = max_Poisson_phiN < 1e6   # arbitrary bound; adjust as needed

# ----------------------------------------------------------------------
# Omega‑Protocol invariant summary
# ----------------------------------------------------------------------
print("\n=== Omega Protocol Audit ===")
print(f"Parameters: m_N={m_N}, m_Δ={m_Del}, λ={lam}")
print(f"Initial seed Φ_Δ(0) = {PhiD0}")
print(f"Integration time: {t_span[0]} → {t_span[1]}")
print("")
print("Shredding detection:")
print(f"  Φ_Δ exceeded {shred_threshold}? {'YES' if shred_event else 'NO'}")
if shred_event:
    print(f"  First occurrence at t ≈ {shred_time:.3f}")
print("")
print("Poisson‑recovery check:")
print(f"  Max |Φ_N| from Poisson solve: {max_Poisson_phiN:.3e}")
print(f"  Bounded? {'YES' if poisson_bounded else 'NO'}")
print("")
print("Invariant Verdict:")
if shred_event or not poisson_bounded:
    print("  ❌ INVARIANT VIOLATION – Shredding instability detected.")
    print("     The derivation must be rejected or stabilized.")
else:
    print("  ✅ INVARIANTS PRESERVED – No Shredding observed for chosen parameters.")
print("===========================\n")