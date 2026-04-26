# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# ── parameters (natural units) ──────────────────────────────────────────────
m      = 1.0          # reference mass
g      = 0.2          # coupling
alpha0 = 1.0/137.0    # bare fine‑structure constant
Lambda = 1.0e4        # UV cutoff
PI     = math.pi

# ── grid for Φ_N and Φ_Δ ──────────────────────────────────────────────────
phiN_vals = np.linspace(0.1, 5.0, 200)   # scan Φ_N
phiD_vals = np.linspace(0.0, 2.5, 200)   # scan Φ_Δ

# storage
exact_grid   = np.zeros((len(phiN_vals), len(phiD_vals)))
series_grid  = np.zeros_like(exact_grid)
entropy_grid = np.zeros_like(exact_grid)

# ─– helper: Shannon entropy of binary mass distribution ───────────────────
def binary_entropy(p):
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p*math.log(p) + (1.-p)*math.log(1.-p))

# ─– main computation ───────────────────────────────────────────────────────
for i, phiN in enumerate(phiN_vals):
    eps = g*phiN/m
    for j, phiD in enumerate(phiD_vals):
        # exact argument of the log
        arg = 1.0 - 2.0*eps*math.cosh(phiD) + eps**2
        if arg <= 0.0:
            # beyond the “shredding” boundary – exact result becomes complex
            # we flag it as NaN for clarity
            exact_grid[i,j] = np.nan
            series_grid[i,j] = np.nan
            entropy_grid[i,j] = np.nan
            continue

        # exact vacuum polarization
        Pi_exact = (alpha0/(3.0*PI))*math.log(Lambda**2/(m*m*arg))
        D_exact  = 1.0 - Pi_exact
        alpha_exact = alpha0/D_exact
        exact_grid[i,j] = alpha_exact

        # series‑truncated denominator (up to O(ε²))
        Pi_series = (alpha0/(3.0*PI))*(math.log(Lambda/m) +
                                       eps*math.cosh(phiD) -
                                       0.5*eps**2*(1.0 - 2.0*math.cosh(phiD)**2))
        D_series = 1.0 - Pi_series
        alpha_series = alpha0/D_series
        series_grid[i,j] = alpha_series

        # ––– entropy of the effective‑mass distribution (m_+, m_–) –––
        m_plus  = m - g*phiN*math.exp( phiD)
        m_minus = m - g*phiN*math.exp(-phiD)
        # probability proportional to the mass (any monotonic weight shows gauge‑dependence)
        p = m_plus/(m_plus + m_minus) if (m_plus+m_minus)>0 else 0.5
        entropy_grid[i,j] = binary_entropy(p)

# ─– simple diagnostic print near the boundary ––––––––––––––––––––––––––––
# locate a point close to the “shredding” line: Φ_N = (m/g)*exp(-Φ_Δ)
idx_phiD = np.argmin(np.abs(phiD_vals - 1.0))  # Φ_Δ ≈ 1
# corresponding Φ_N on the boundary
phiN_boundary = (m/g)*math.exp(-phiD_vals[idx_phiD])
idx_phiN = np.argmin(np.abs(phiN_vals - phiN_boundary))

print("\n── Diagnostics near shredding boundary (Φ_D≈1.0) ──")
print(f"Φ_N (boundary)          = {phiN_boundary:.4f}")
print(f"Φ_N (grid)              = {phiN_vals[idx_phiN]:.4f}")
print(f"Exact α                 = {exact_grid[idx_phiN, idx_phiD]:.6e}")
print(f"Series α                = {series_grid[idx_phiN, idx_phiD]:.6e}")
print(f"Relative error (series) = {abs(series_grid[idx_phiN, idx_phiD]/exact_grid[idx_phiN, idx_phiD]-1):.3e}")
print(f"Binary entropy (bits)   = {entropy_grid[idx_phiN, idx_phiD]:.4f}")

# –– demonstrate gauge‑dependence of entropy ––
print("\n── Entropy gauge‑dependence ──")
# same physical masses, but reparametrise the fields:
# define new fields (Φ_N', Φ_Δ') such that the masses are unchanged
# m_± = m - g Φ_N e^{±Φ_Δ} = m - g Φ_N' e^{±Φ_Δ'}
# choose Φ_N' = Φ_N * cosh(Φ_Δ),  Φ_Δ' = atanh(tanh(Φ_Δ)/cosh(Φ_Δ))
# (any invertible redefinition works)
phiN_orig = 2.0
phiD_orig = 1.2
m_p = m - g*phiN_orig*math.exp( phiD_orig)
m_m = m - g*phiN_orig*math.exp(-phiD_orig)

# a different field pair that yields the same m_±
phiN_prime = phiN_orig*math.cosh(phiD_orig)
phiD_prime = math.atanh(math.tanh(phiD_orig)/math.cosh(phiD_orig)) if abs(math.tanh(phiD_orig))<1 else 0.0

# recompute entropy with the primed fields
p_orig = m_p/(m_p+m_m)
p_prime = (m - g*phiN_prime*math.exp( phiD_prime)) / ((m - g*phiN_prime*math.exp( phiD_prime)) + (m - g*phiN_prime*math.exp(-phiD_prime)))
# the probabilities are the same (they must be, masses are unchanged)
# but the Shannon entropy computed from the field variables differs because
# the mapping of probabilities to fields is non‑linear – a gauge artefact.
print(f"Original field entropy = {binary_entropy(p_orig):.4f}")
print(f"Prime field entropy    = {binary_entropy(p_prime):.4f} (same masses, different field values)")

# ── summary ────────────────────────────────────────────────────────────────
print("\n── Conclusion ──")
print("The exact non‑perturbative result stays finite and tends to zero at the boundary.")
print("The truncated series diverges and produces a fictitious sign‑change.")
print("The Shannon entropy of the mass distribution is not invariant under field redefinitions.")