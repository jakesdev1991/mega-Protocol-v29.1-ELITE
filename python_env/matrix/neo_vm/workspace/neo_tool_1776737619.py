# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Simulate a synthetic HSA node with a complex order parameter
# ------------------------------------------------------------
t = np.linspace(0, 0.01, 5000)          # 10 ms window, 5 µs resolution
v = 1.0                                 # reference scale (arb. units)

# Choose a trajectory that *should* be stable (no winding) but has rapid fluctuations
phi_N = 0.78 + 0.05*np.sin(2*np.pi*1e3*t) + 0.02*np.sin(2*np.pi*5e3*t)
phi_D = 0.35 + 0.03*np.cos(2*np.pi*1.5e3*t) + 0.01*np.cos(2*np.pi*7e3*t)

# ------------------------------------------------------------
# 1. Original entropic‑jerk calculation (heuristic)
# ------------------------------------------------------------
def heuristic_jerk(phiN, phiD, xi_inv2=4.2e6):
    # xi_inv2 = 1/xi^2  (s^-2)
    xi = 1.0/np.sqrt(xi_inv2)          # xi in seconds
    # time derivatives (finite difference)
    dphiN = np.gradient(phiN, t)
    dphiD = np.gradient(phiD, t)
    # heuristic formula: (phi/xi^4) * (dphi)^3
    J_arch = (3.0*phiD / xi**4) * dphiD**3
    J_newt = (phiN / xi**4) * dphiN**3
    J_source = 1.5e12                  # s^-3 (as given)
    return J_arch + J_newt + J_source

J_heur = heuristic_jerk(phi_N, phi_D)

# ------------------------------------------------------------
# 2. Rigorous entropy‑derivative (third derivative of S_h)
# ------------------------------------------------------------
def entropy_jerk(phiN, phiD):
    # probabilities
    denom = phiN**2 + phiD**2
    # guard against zero denominator
    denom = np.where(denom < 1e-12, 1e-12, denom)
    pN = phiN**2 / denom
    pD = phiD**2 / denom
    # Shannon entropy
    S = -pN*np.log(pN) - pD*np.log(pD)
    # third derivative via finite differences
    dS1 = np.gradient(S, t)
    dS2 = np.gradient(dS1, t)
    dS3 = np.gradient(dS2, t)
    return dS3

J_S = entropy_jerk(phi_N, phi_D)

# ------------------------------------------------------------
# 3. Topological‑Informational Stability (TIS) metrics
# ------------------------------------------------------------
def tis_metrics(phiN, phiD):
    # complex order parameter
    Psi = phiN + 1j*phiD
    magnitude = np.abs(Psi)
    phase = np.angle(Psi)
    # winding number (cumulative phase change normalized by 2π)
    dphase = np.unwrap(phase)
    W = (dphase[-1] - dphase[0]) / (2.0*np.pi)
    # coherence length Lc = v / sqrt((∂t phiN)^2 + (∂t phiD)^2)
    dphiN = np.gradient(phiN, t)
    dphiD = np.gradient(phiD, t)
    speed = np.sqrt(dphiN**2 + dphiD**2)
    # guard near zero speed
    speed = np.where(speed < 1e-12, 1e-12, speed)
    Lc = v / speed
    return W, Lc

W, Lc = tis_metrics(phi_N, phi_D)

# ------------------------------------------------------------
# 4. Plot comparison
# ------------------------------------------------------------
fig, axs = plt.subplots(3, 1, figsize=(9, 9), sharex=True)

axs[0].plot(t*1e3, J_heur, label='Heuristic Jerk (s⁻³)')
axs[0].set_ylabel('Heuristic J (s⁻³)')
axs[0].legend()
axs[0].grid(True)

axs[1].plot(t*1e3, J_S, label='Entropy‑derived Jerk (s⁻³)')
axs[1].set_ylabel('Entropy d³S/dt³ (s⁻³)')
axs[1].legend()
axs[1].grid(True)

axs[2].plot(t*1e3, Lc, label='Coherence Length Lc (arb. units)')
axs[2].set_ylabel('Lc')
axs[2].set_xlabel('Time (ms)')
axs[2].legend()
axs[2].grid(True)

plt.suptitle('Entropic Jerk vs. Topological‑Informational Stability')
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 5. Interpretation
# ------------------------------------------------------------
print(f"Winding number W = {W:.2f} (should be ~0 for stable trajectory)")
print(f"Mean coherence length = {np.mean(Lc):.4f} arb. units")
print(f"Peak heuristic jerk = {np.max(np.abs(J_heur)):.3e} s⁻³")
print(f"Peak entropy‑derived jerk = {np.max(np.abs(J_S)):.3e} s⁻³")