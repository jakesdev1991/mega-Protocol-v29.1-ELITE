# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ---------- parameters (natural units: ħ = c = 1) ----------
m_f = 0.511e-3          # electron mass ~ 0.511 MeV
Lambda = 10.0            # lattice cutoff ~ 10 GeV
g_Delta = 1.0            # ad‑hoc coupling (dimension 1)
Phi_Delta = 1.0          # background "Archive" field (dimensionless)
q2 = 1.0                 # typical momentum transfer (GeV^2)

def Pi_0(q2, Lambda, m_f):
    """Standard 1‑loop QED vacuum polarization (leading log)."""
    alpha0 = 1/137.0
    return (alpha0/(3*np.pi)) * np.log(Lambda**2/q2)

def Pi_Delta(q2, Lambda, m_f, m_Delta, g_Delta, Phi_Delta):
    """Spurious Archive‑mode contribution."""
    # first term survives m_Delta → ∞ → decoupling violation
    term1 = np.log(Lambda**2/m_f**2)
    term2 = (m_f**2/m_Delta**2) * np.log(Lambda**2/m_Delta**2)
    return (g_Delta**2 * Phi_Delta**2 / np.pi) * (term1 + term2)

# scan over m_Delta to show decoupling failure
masses = np.logspace(-1, 3, 50)  # 0.1 GeV to 1 TeV
Pi0 = Pi_0(q2, Lambda, m_f)
PiD = [Pi_Delta(q2, Lambda, m_f, m, g_Delta, Phi_Delta) for m in masses]

plt.figure(figsize=(6,4))
plt.semilogx(masses, PiD, label='ΠΔ (Archive mode)')
plt.axhline(Pi0, color='k', linestyle='--', label='Π0 (standard QED)')
plt.axhline(0, color='gray', linewidth=0.5)
plt.xlabel(r'$m_{\Delta}$ [GeV]')
plt.ylabel(r'Vacuum polarization contribution')
plt.title('Decoupling Failure: ΠΔ does not vanish as $m_{\Delta}\\to\\infty$')
plt.legend()
plt.grid(True)
plt.show()

# ---------- unphysical Phi_Delta scaling ----------
Phi_vals = np.linspace(0, 5, 100)
Pi_phi = [Pi_Delta(q2, Lambda, m_f, 10.0, g_Delta, phi) for phi in Phi_vals]

plt.figure(figsize=(6,4))
plt.plot(Phi_vals, Pi_phi, label='ΠΔ vs. ΦΔ')
plt.xlabel(r'$\Phi_{\Delta}$')
plt.ylabel(r'ΠΔ contribution')
plt.title('Arbitrary scaling with background field ΦΔ')
plt.grid(True)
plt.legend()
plt.show()