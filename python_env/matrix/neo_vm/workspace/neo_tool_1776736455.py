# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ── 1. Hessian eigenvalues: Goldstone vs. massive mode ──
lam = 0.5
v   = 1.0

def hessian_eigs(phiN, phiD):
    H11 = lam * (3*phiN**2 + phiD**2 - v**2)
    H22 = lam * (3*phiD**2 + phiN**2 - v**2)
    H12 = 2*lam * phiN * phiD
    H = np.array([[H11, H12], [H12, H22]])
    return np.sort(np.linalg.eigvals(H))

phi = np.linspace(-1.5, 1.5, 400)
eig1, eig2 = np.zeros_like(phi), np.zeros_like(phi)
for i, p in enumerate(phi):
    e1, e2 = hessian_eigs(p, 0)
    eig1[i], eig2[i] = e1, e2

plt.figure(figsize=(8,4))
plt.plot(phi, eig1, label='Eigenvalue 1 (radial)')
plt.plot(phi, eig2, label='Eigenvalue 2 (Goldstone)')
plt.axhline(0, color='k', linestyle='--')
plt.title('Hessian eigenvalues along $\Phi_N$ ($\Phi_\Delta=0$)')
plt.xlabel('$\Phi_N$')
plt.ylabel('Eigenvalue')
plt.legend()
plt.grid(True)
plt.show()

# ── 2. Running coupling: flawed vs. corrected ──
alpha0 = 1/137.035999084
gN = 0.1
gD = 0.2
Lambda = 1e4          # 10 TeV
Lambda_N = 2e4
Lambda_D = 5e4
m_gamma = gD * np.sqrt(Lambda_D)  # photon mass from BF term

def alpha_flawed(q2):
    term = (alpha0/(3*np.pi))*np.log(Lambda**2/q2) + \
           (gN**2/(4*np.pi))*np.log(Lambda_N**2/q2) + \
           (3*gD**2/(4*np.pi))*np.log(Lambda_D**2/q2)
    return alpha0 * (1 + term)

def alpha_corrected(q2):
    # standard QED + massive vector suppression
    term_qed = (alpha0/(3*np.pi))*np.log(Lambda**2/q2)
    # massive vector: only contributes when q2 >> m_gamma^2
    supp = q2/(q2 + m_gamma**2)
    term_D = (gD**2/(4*np.pi))*supp*np.log((Lambda_D**2 + m_gamma**2)/(q2 + m_gamma**2))
    return alpha0 * (1 + term_qed + term_D)

q2s = np.logspace(np.log10(1), np.log10(1e6), 200)
alpha_f = np.array([alpha_flawed(q2) for q2 in q2s])
alpha_c = np.array([alpha_corrected(q2) for q2 in q2s])

plt.figure(figsize=(8,4))
plt.loglog(q2s, alpha_f, label='Flawed (Omega)', linestyle='--')
plt.loglog(q2s, alpha_c, label='Corrected (BF)', linewidth=2)
plt.axhline(1, color='r', linestyle=':', label='Landau pole')
plt.title(r'$\alpha_{\text{fs}}(q^2)$: flawed vs. corrected')
plt.xlabel(r'$q^2$ (GeV$^2$)')
plt.ylabel(r'$\alpha$')
plt.legend()
plt.grid(True)
plt.show()