# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Shredding_vs_Landau.py
Agent Neo – The Anomaly
Purpose: Expose the Landau pole as the primary instability, not the Shredding invariant.
"""

import numpy as np

# ---- Parameters (lattice units) ----
h0 = 0.1          # Archive Yukawa coupling
a  = 1.0          # lattice spacing
m0 = 0.01         # reference fermion mass
M0 = 0.0          # Archive bare mass (set to zero for maximal effect)

# ---- Momentum cutoff grid ----
Lambda_min = 0.1
Lambda_max = 20.0
Nsteps = 200
Lambdas = np.linspace(Lambda_min, Lambda_max, Nsteps)

# ---- Observables ----
Pi_Delta = h0**2 * (Lambdas**2) * a**(-2)          # quadratic divergence
m_eff    = np.sqrt(M0**2 + Pi_Delta)               # effective mass
psi      = np.log(m_eff / m0)                      # Shredding invariant
denom    = 1.0 - Pi_Delta                          # charge renormalization denominator

# ---- Critical scales ----
# Landau pole: denom -> 0
idx_landau = np.argmin(np.abs(denom))
Lambda_landau = Lambdas[idx_landau]
Pi_at_landau = Pi_Delta[idx_landau]
psi_at_landau = psi[idx_landau]

# Shredding "event": psi -> +infty (practically > 10)
idx_shred = np.argmax(psi > 10.0) if np.any(psi > 10.0) else None
Lambda_shred = Lambdas[idx_shred] if idx_shred is not None else np.inf

# ---- Print the hierarchy ----
print("="*60)
print("LANDAU POLE vs SHREDDING – RAW DATA")
print("="*60)
print(f"{'Lambda':>8} {'Pi_Delta':>12} {'denom':>12} {'psi':>12}")
print("-"*60)
for i in range(0, Nsteps, Nsteps//10):
    print(f"{Lambdas[i]:8.3f} {Pi_Delta[i]:12.3e} {denom[i]:12.3e} {psi[i]:12.3e}")

print("="*60)
print(f"Landau pole (denom≈0) at Lambda = {Lambda_landau:.3f}")
print(f"  Pi_Delta = {Pi_at_landau:.3f}, denom = {denom[idx_landau]:.3e}, psi = {psi_at_landau:.3f}")
print("-"*60)
if idx_shred is not None:
    print(f"Shredding (psi>10) at Lambda = {Lambda_shred:.3f}")
    print(f"  Pi_Delta = {Pi_Delta[idx_shred]:.3e}, denom = {denom[idx_shred]:.3e}")
else:
    print("Shredding not reached within cutoff range.")
print("="*60)

# ---- Interpretation ----
print("\nDISRUPTIVE INTERPRETATION:")
if Lambda_landau < Lambda_shred:
    print("The Landau pole occurs FIRST. The theory is already non‑unitary before any Shredding invariant blows up.")
    print("Shredding is a RED HERRING – the real instability is the charge divergence at Pi_Delta=1.")
else:
    print("Unexpected: Shredding precedes Landau pole. Check parameters.")