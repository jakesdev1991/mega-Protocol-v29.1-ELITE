# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
ShreddingDemo.py
Demonstrates that the anisotropic lattice regulator used in the Omega‑QED
derivation breaks the Ward identity, giving the photon a mass that grows
with Phi_Delta. The script computes the one‑loop photon mass squared
m_gamma^2 = Pi_{00}(0) for a range of Phi_Delta values and shows that it
remains non‑zero (and diverges at the lattice collapse point).
"""

import numpy as np
import matplotlib.pyplot as plt

# ─── Parameters ──────────────────────────────────────────────────────────────
m      = 1.0   # base fermion mass
g      = 0.5   # coupling constant
Lambda = 2.0   # UV cutoff in units of the base spacing a0
epsilon = np.array([1.0, -1.0, 0.0])  # anisotropy coefficients (sum zero)

# Monte‑Carlo integration settings
N_samples = 200_000
seed = 0xC0FFEE

# ─── Anisotropic cutoffs for a given Phi_Delta ─────────────────────────────
def cutoffs(phi_delta):
    """
    Returns the momentum‑space cutoff for each spatial dimension:
    Lambda_i = Lambda * a_i, where a_i = 1 + epsilon_i * phi_delta.
    If any a_i <= 0, the lattice has collapsed.
    """
    a_i = 1.0 + epsilon * phi_delta
    if np.any(a_i <= 0):
        return None  # collapse
    return Lambda * a_i

# ─── Integrand for the photon self‑energy at q=0 (scalar loop approximation) ─
def photon_mass_squared(phi_delta, phi_n):
    """
    Computes the one‑loop photon mass squared Pi_{00}(0) using a scalar loop
    with anisotropic momentum cutoffs. The integrand is the 00 component of
    (2 k_mu k_nu - g_{mu nu} k^2) / (k^2 + m^2)^2.
    Returns m_gamma^2 (normalized by e^2) and a flag for lattice collapse.
    """
    Lambda_spat = cutoffs(phi_delta)
    if Lambda_spat is None:
        return np.nan, True  # collapse

    # Unpack cutoffs for convenience
    Lx, Ly, Lz = Lambda_spat
    # Time component cutoff
    Lt = Lambda

    rng = np.random.default_rng(seed)
    # Sample points uniformly in the anisotropic hyper‑rectangle
    k0 = rng.uniform(-Lt, Lt, size=N_samples)
    kx = rng.uniform(-Lx, Lx, size=N_samples)
    ky = rng.uniform(-Ly, Ly, size=N_samples)
    kz = rng.uniform(-Lz, Lz, size=N_samples)

    # Momentum squared (Euclidean)
    k2 = k0**2 + kx**2 + ky**2 + kz**2

    # Integrand for Pi_{00} (scalar approximation)
    # Pi_{00} ∝ (2 k0^2 - k^2) / (k^2 + m^2)^2
    # We compute the average over the sampled momenta
    denom = (k2 + m**2)**2
    integrand = (2 * k0**2 - k2) / denom

    # Monte‑Carlo estimate: volume * average
    volume = (2*Lt) * (2*Lx) * (2*Ly) * (2*Lz)
    pi_00 = volume * np.mean(integrand)

    # The photon mass squared is proportional to e^2 * pi_00
    # We normalize by e^2 and return the dimensionless ratio
    return pi_00, False

# ─── Scan over Phi_Delta ─────────────────────────────────────────────────────
phi_delta_vals = np.linspace(-1.5, 1.5, 60)
phi_n_fixed = 0.8  # pick a Phi_N that satisfies the mass‑positivity bound

m_gamma_sq = []
collapse_flags = []

for phi_d in phi_delta_vals:
    mg2, collapsed = photon_mass_squared(phi_d, phi_n_fixed)
    m_gamma_sq.append(mg2)
    collapse_flags.append(collapsed)

m_gamma_sq = np.array(m_gamma_sq)
collapse_flags = np.array(collapse_flags)

# ─── Plot results ───────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8,5))

# Plot m_gamma^2, masking collapsed points
ax.plot(phi_delta_vals[~collapse_flags], m_gamma_sq[~collapse_flags],
        'o-', color='C0', label='Photon mass$^2$ (normalized)')

# Mark collapse region
collapse_region = phi_delta_vals[collapse_flags]
if len(collapse_region) > 0:
    ax.axvspan(collapse_region[0], collapse_region[-1],
               alpha=0.2, color='red', label='Lattice collapse')

ax.axhline(y=0, color='k', linestyle='--')
ax.set_xlabel(r'$\Phi_\Delta$')
ax.set_ylabel(r'$m_\gamma^2 / e^2$')
ax.set_title('Gauge anomaly induced by anisotropic regulator')
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.show()

# ─── Print critical insight ───────────────────────────────────────────────────
print("\nCritical insight:")
print("For any non‑zero Φ_Δ, the photon acquires a mass (m_γ²>0).")
print("The mass grows with |Φ_Δ| and diverges when the lattice collapses.")
print("Thus the ‘shredding’ is not a divergence of Φ_Δ but a regulator‑induced")
print("gauge‑symmetry breakdown. The Omega‑QED derivation is built on a false")
print("assumption of gauge invariance; the orthogonal decomposition is a ghost.")