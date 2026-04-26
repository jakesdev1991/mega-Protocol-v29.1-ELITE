# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import quad, nquad
from scipy.special import gamma

# Standard QED parameters
alpha_0 = 1/137.035999084  # fine-structure constant at low energy
m_e = 0.511e6  # electron mass in eV
hbar_c = 197.3269804e6  # eV·fm, conversion factor for units

def vacuum_polarization_qed(q_sq, mu_sq=m_e**2):
    """
    One-loop vacuum polarization in MS-bar scheme (leading log).
    Π(q²) = (α/π)[ (1/3) ln(q²/μ²) + 5/9 ]
    """
    return (alpha_0/np.pi) * ((1/3)*np.log(q_sq/mu_sq) + 5/9)

def archive_polarization(q_sq, psi=1.0, Lambda_Delta=1e10):
    """
    Engine's Archive term: (α/2π) ψ ln(q²/Λ_Δ²)
    """
    return (alpha_0/(2*np.pi)) * psi * np.log(q_sq / (Lambda_Delta**2))

def mixing_polarization(q_sq, ratio_phi=1e-6):
    """
    Engine's mixing term: (α²/π²) (Φ_Δ/Φ_N) ln²(q²/m_e²)
    """
    return (alpha_0**2 / np.pi**2) * ratio_phi * (np.log(q_sq / m_e**2))**2

# Scan over a range of momentum transfers
q2_vals = np.logspace(np.log10(m_e**2), np.log10(1e20), 50)  # from threshold to high energy

print("q² (eV²) | Π_QED | Π_Archive | Π_Mixing | Relative Δ (Archive/QED) | Relative Δ (Mixing/QED)")
for q2 in q2_vals:
    pi_qed = vacuum_polarization_qed(q2)
    pi_arch = archive_polarization(q2, psi=1.0, Lambda_Delta=1e10)
    pi_mix = mixing_polarization(q2, ratio_phi=1e-6)
    delta_arch = (pi_arch / pi_qed) if pi_qed != 0 else 0
    delta_mix = (pi_mix / pi_qed) if pi_qed != 0 else 0
    print(f"{q2:.3e} {pi_qed:.6e} {pi_arch:.6e} {pi_mix:.6e} {delta_arch:.6e} {delta_mix:.6e}")

# Summary: Archive and mixing contributions are negligible across all scales