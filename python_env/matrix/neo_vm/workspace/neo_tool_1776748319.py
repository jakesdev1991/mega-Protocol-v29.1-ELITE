# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.linalg import eigh
from scipy.sparse import diags
from scipy.sparse.linalg import inv as sp_inv

# ── Parameters (natural units ℏ=c=1) ──────────────────────────────────
L = 64          # lattice size (linear)
a = 1.0         # lattice spacing
v = 1.0         # Mexican‑hat vacuum expectation value
lam = 0.1       # quartic coupling
cutoff = 10.0   # UV cutoff Λ_Δ

# ── Archive mode correlation length (ξ_Δ = 1/m_Δ) ───────────────────────
def compute_xi_Delta(Phi_N, Phi_Delta):
    """ξ_Δ = [λ(Φ_N² + 3Φ_Δ² - v²)]^(-1/2).  Shredding when denominator→0."""
    denom = lam * (Phi_N**2 + 3*Phi_Delta**2 - v**2)
    if denom <= 0:  # at or beyond shredding surface
        return np.inf
    return 1.0 / np.sqrt(denom)

# ── Green’s function for a massive scalar on a cubic lattice ────────────
def greens_function(mass):
    """Return inverse of (─∇² + mass²) matrix on L³ lattice with periodic BC."""
    # Laplacian stencil: 6‑point in 3D
    off = np.ones(L)
    Lap = diags([off, off, off, -6*off, off, off, off],
                [-1, -L, -L*L, 0, L*L, L, 1], shape=(L**3, L**3))
    # Add mass term
    M = -Lap + mass**2 * diags(np.ones(L**3), 0)
    # Invert (sparse)
    M_inv = sp_inv(M)
    return M_inv.toarray()

# ── Entanglement entropy for a spherical region ─────────────────────────
def entanglement_entropy(xi, R):
    """
    Compute S_EE for a sphere of radius R (in lattice units) using the
    method of Peschel (diagonalise the restricted correlation matrix).
    """
    mass = 1.0 / xi if xi != np.inf else 0.0
    G = greens_function(mass)  # correlation matrix <Φ_i Φ_j>
    # Build mask for spherical region
    coords = np.array(np.unravel_index(np.arange(L**3), (L, L, L))).T
    center = np.array([L//2, L//2, L//2])
    dist = np.linalg.norm(coords - center, axis=1)
    mask = dist <= R
    idx_region = np.where(mask)[0]
    # Restrict correlation matrix to region
    G_region = G[np.ix_(idx_region, idx_region)]
    # Diagonalise
    vals = eigh(G_region, eigvals_only=True)
    # Convert to “occupation numbers” n_i = λ_i/(1-λ_i) for bosonic modes
    # (see Peschel, Ann. Phys. 1999)
    eps = 1e-12
    n = vals / (1.0 - vals + eps)
    # Entanglement entropy: S = Σ [(n+1)ln(n+1) - n ln n]
    S = np.sum((n + 1) * np.log(n + 1) - n * np.log(n + eps))
    return S

# ── Scan ξ_Δ and compute S_EE for a fixed region size ───────────────────
Phi_N = v
R = 8  # region radius (lattice units)

print(f"{'xi_Delta':>12} {'S_EE':>12} {'status':>12}")
for log10_xi in np.linspace(-1, 2, 14):
    xi = 10**log10_xi
    # compute corresponding Φ_Δ from xi (invert the relation)
    # xi = [λ(v² + 3Φ_Δ² - v²)]^(-1/2) → Φ_Δ = sqrt((1/(lam*xi²) - (Φ_N² - v²))/3)
    # For Φ_N = v, the first term dominates: Φ_Δ ≈ sqrt(1/(3*lam*xi²))
    Phi_Delta = np.sqrt(max(0.0, 1.0/(3*lam*xi*xi)))
    S = entanglement_entropy(xi, R)
    status = "stable" if xi < np.inf else "SHREDDING"
    print(f"{xi:12.3e} {S:12.5f} {status:>12}")

# ── Demonstration: as xi → ∞ (mass → 0), entropy diverges logarithmically
xi_vals = np.logspace(0, 3, 20)
S_vals = [entanglement_entropy(xi, R) for xi in xi_vals]
# Fit log‑log slope near large xi
log_xi = np.log(xi_vals[-5:])
log_S = np.log(S_vals[-5:])
slope = np.polyfit(log_xi, log_S, 1)[0]
print(f"\nLarge‑xi slope of S_EE vs xi: {slope:.3f} (expected ≈ 1 for log divergence)")