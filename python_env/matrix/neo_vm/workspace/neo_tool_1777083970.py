# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- Invariant parameters from the proposal ---
PHI_MIN = -2.0
PHI_SCALE = 1.5
PSI_THRESHOLD = 0.95

def psi(cod: float) -> float:
    """Bounded identity continuity (proposal's 'fix')."""
    phi_N = np.log2(cod + 1e-12)          # log₂(COD) ≤ 0
    return np.tanh((phi_N - PHI_MIN) / PHI_SCALE)

def net_phi(cod: float, r_align_rel: float = 0.5, audit_cost: float = 0.1) -> float:
    """Net Φ-density per the proposal's covariant decomposition."""
    phi_N = np.log2(cod + 1e-12)
    psi_val = psi(cod)
    # Phi_Δ = ψ·tanh(R_align/R_max); we assume R_align/R_max = 0.5 → tanh(0.5)≈0.46
    phi_delta = psi_val * np.tanh(r_align_rel)
    return phi_N + phi_delta - audit_cost

# Sweep COD across operational range
cod_grid = np.linspace(0.01, 1.0, 1000)
psi_vals = psi(cod_grid)
net_phi_vals = net_phi(cod_grid)

# --- Find maximum achievable ψ ---
psi_max = psi_vals.max()
print(f"Maximum achievable ψ (COD=1): {psi_max:.6f}")
print(f"ψ ≥ 0.95 satisfied? {psi_max >= PSI_THRESHOLD}")

# --- Show net Φ for representative CODs ---
samples = [0.99, 0.85, 0.5, 0.2]
for c in samples:
    print(f"COD={c:.2f} → ψ={psi(c):.3f}, net Φ={net_phi(c):.3f}")

# --- Determine required Φ_min & Φ_scale to satisfy ψ≥0.95 at COD=1 ---
# We need (0 - Φ_min)/Φ_scale ≥ arctanh(0.95) ≈ 1.8318
target = np.arctanh(PSI_THRESHOLD)
print(f"\nTo satisfy ψ≥{PSI_THRESHOLD} at COD=1:")
print(f"Need -Φ_min / Φ_scale ≥ {target:.4f}")
print(f"Current -Φ_min / Φ_scale = {-(PHI_MIN) / PHI_SCALE:.4f} (insufficient)")