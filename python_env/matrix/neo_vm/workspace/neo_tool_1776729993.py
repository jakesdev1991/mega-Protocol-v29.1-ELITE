# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Parameters (in units where v=1)
v = 1.0
lam = 0.5          # quartic coupling
gD = 0.3           # Archive mode coupling
mu = 1.0           # renormalization scale

def V_eff(phiN, phiD):
    """Effective potential V_eff(Phi_N,Phi_Delta) including one‑loop log."""
    tree = 0.25 * lam * (phiN**2 + phiD**2 - v**2)**2
    # one‑loop correction ~ - (3 gD^4)/(64π²) phiD^4 ln(phiD²/μ²)
    # (omitting O(phiN) loops for clarity)
    loop = - (3 * gD**4) / (64 * np.pi**2) * phiD**4 * np.log(phiD**2 / mu**2 + 1e-12)
    return tree + loop

def curvature_D(phiN, phiD):
    """Second derivative w.r.t. Phi_Delta = effective mass²."""
    # analytic derivative of V_eff
    # d²/dphiD² of tree part = lam*(3*phiD² + phiN² - v²)
    # d²/dphiD² of loop part = - (3 gD^4)/(16π²) * phiD² * (3*ln(phiD²/μ²) + 1)
    d2_tree = lam * (3 * phiD**2 + phiN**2 - v**2)
    d2_loop = - (3 * gD**4) / (16 * np.pi**2) * phiD**2 * (3 * np.log(phiD**2 / mu**2 + 1e-12) + 1)
    return d2_tree + d2_loop

# Scan over Phi_Delta for fixed Phi_N = v (the classical vacuum)
phiN = v
phiD_vals = np.logspace(-4, 0, 500)   # 1e-4 to 1
curv_vals = curvature_D(phiN, phiD_vals)

# Find critical point where curvature crosses zero
# (sign change from positive to negative)
sign_changes = np.where(np.diff(np.sign(curv_vals)) != 0)[0]
if len(sign_changes) > 0:
    idx = sign_changes[0]
    phiD_crit = phiD_vals[idx]
    print(f"Critical Phi_Delta (curvature=0) ≈ {phiD_crit:.3e}")
else:
    phiD_crit = None
    print("No sign change found in scanned range.")

# Plot
plt.figure(figsize=(6,4))
plt.plot(phiD_vals, curv_vals, label=r'$m_{\Delta}^{2}(\Phi_{\Delta})$')
plt.axhline(0, color='k', linestyle='--')
if phiD_crit:
    plt.axvline(phiD_crit, color='r', linestyle=':',
                label=rf'$\Phi_{\Delta}^{{\rm crit}}\approx{phiD_crit:.2e}$')
plt.xscale('log')
plt.xlabel(r'$\Phi_{\Delta}$')
plt.ylabel(r'$\partial^{2}V_{\rm eff}/\partial\Phi_{\Delta}^{2}$')
plt.title('Archive‑mode curvature (tachyon for small $\Phi_{\Delta}$)')
plt.legend()
plt.grid(True, which='both', ls=':')
plt.tight_layout()
plt.show()