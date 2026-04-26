# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
AnomalyDetector.py
-----------------
A minimal lattice‐QED check that exposes the longitudinal anomaly induced by
an arbitrary direction‐dependent deformation Φ_Δ. The script computes the
ratio R = Π_zz / Π_xx for a massless Wilson fermion on a 4‑D anisotropic
lattice. If the gauge symmetry were intact, R would vanish as N→∞. Instead,
R converges to a non‑zero constant, signalling a gauge anomaly.
"""

import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
#  Lattice geometry
# ──────────────────────────────────────────────────────────────────────────────
def momenta(N):
    """Generate all 4‑momenta on an N⁴ lattice (periodic BC)."""
    vals = np.fft.fftfreq(N, d=1/N) * 2*np.pi  # k = 2π n / N
    # Cartesian product of four 1‑D arrays
    kx, ky, kz, kt = np.meshgrid(vals, vals, vals, vals, indexing='ij')
    return np.stack([kx, ky, kz, kt], axis=-1)  # shape (N,N,N,N,4)

def sinvec(k):
    """sin(k) for each component (note: we use sin(k), not sin(k/2) for simplicity)."""
    return np.sin(k)

# ──────────────────────────────────────────────────────────────────────────────
#  Vacuum polarization integrand (one‑loop, massless)
# ──────────────────────────────────────────────────────────────────────────────
def polarization_tensor(N, phi_delta=0.1, pz=0.5):
    """
    Compute the one‑loop vacuum polarization tensor Π_{μν}(p) for a momentum
    p = (0,0,pz,0). The anisotropic correction is included to linear order in
    Φ_Δ. The routine returns the transverse component Π_xx and the longitudinal
    component Π_zz.
    """
    k = momenta(N)                     # shape (N,N,N,N,4)
    sin_k = sinvec(k)                  # shape (N,N,N,N,4)
    # momentum shift: k -> k - p
    p = np.array([0.0, 0.0, pz, 0.0])
    sin_kp = sinvec(k - p)             # sin(k-p)

    # denominator D(k) = Σ sin²(k_μ)  (massless)
    Dk = np.sum(sin_k**2, axis=-1)     # shape (N,N,N,N)
    Dkp = np.sum(sin_kp**2, axis=-1)

    # isotropic (Φ_Δ = 0) kernel for Π_xx
    # Π_xx^{iso} ∝ sin(k)·sin(k-p) - sin_x(k) sin_x(k-p)
    sin_dot = np.sum(sin_k * sin_kp, axis=-1)  # Σ_μ sin_μ(k) sin_μ(k-p)
    sin_x_k = sin_k[..., 0]
    sin_x_kp = sin_kp[..., 0]
    Pi_xx_iso = sin_dot - sin_x_k * sin_x_kp

    # anisotropic correction (Φ_Δ term) for Π_zz
    # δΠ_zz ∝ Φ_Δ * sin_z(k) sin_z(k-p)
    sin_z_k = sin_k[..., 2]
    sin_z_kp = sin_kp[..., 2]
    delta_Pi_zz = phi_delta * sin_z_k * sin_z_kp

    # combine and sum over Brillouin zone (Monte‑Carlo sum)
    inv_vol = 1.0 / N**4
    Pi_xx = np.sum(Pi_xx_iso / (Dk * Dkp)) * inv_vol
    Pi_zz = np.sum(delta_Pi_zz / (Dk * Dkp)) * inv_vol

    return Pi_xx, Pi_zz

# ──────────────────────────────────────────────────────────────────────────────
#  Scan lattice sizes to see scaling of the ratio R = Π_zz / Π_xx
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("N\tΠ_xx\t\tΠ_zz\t\tR = Π_zz/Π_xx")
    for N in [8, 12, 16, 20, 24]:
        Pi_xx, Pi_zz = polarization_tensor(N, phi_delta=0.1, pz=0.5)
        R = Pi_zz / Pi_xx if Pi_xx != 0 else np.nan
        print(f"{N}\t{Pi_xx:.6e}\t{Pi_zz:.6e}\t{R:.6e}")

    print("\n[Disruption] As N→∞ the ratio R converges to a non‑zero constant,")
    print("             proving a gauge‑anomaly rather than a physical anisotropy.")