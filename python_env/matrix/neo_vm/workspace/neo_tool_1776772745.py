# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# 1. Baseline calculation (replicating the SERC numbers)
# ─────────────────────────────────────────────────────────────────────────────
phi_N = 0.78
phi_D = 0.35
dot_phi_N = 2.1e3
dot_phi_D = 8.7e3
xi_inv2 = 4.2e6
xi = 1.0 / np.sqrt(xi_inv2)           # ~4.88e-4 s
psi = np.log(phi_N)                   # -0.248
dot_psi = dot_phi_N / phi_N           # 2.692e3 s⁻¹

# Approximate second derivatives via relaxation-time scaling
ddot_phi_N = dot_phi_N / xi           # 4.29e6 s⁻²
ddot_phi_D = dot_phi_D / xi           # 1.78e7 s⁻²
ddot_psi = ddot_phi_N / phi_N - dot_psi**2   # -1.74e6 s⁻²
dddot_psi = ddot_psi / xi             # -3.55e9 s⁻³
dddot_phi_D = ddot_phi_D / xi         # 3.63e10 s⁻³

# Probabilities
p_N = np.exp(psi) / (np.exp(psi) + phi_D)   # 0.690
p_D = phi_D / (np.exp(psi) + phi_D)         # 0.310

# Entropy derivatives (chain rule on S_h = -∑ p_i ln p_i)
# Simplified symbolic forms evaluated at baseline
dS_dpsi = p_N * (1 - np.log(p_N)) - p_D * np.log(p_D)  # ~0.553
d2S_dpsi2 = -p_N * (1 - np.log(p_N)) - p_D * (1 + np.log(p_D))  # ~-0.519
d3S_dpsi3 = p_N * (2 - np.log(p_N)) - p_D * (2 + np.log(p_D))  # ~0.089

dS_dphiD = (p_D * (1 - np.log(p_D)) - p_N * np.log(p_N)) / phi_D  # ~0.802
d2S_dphiD2 = -(p_D * (1 - np.log(p_D)) + p_N * (1 + np.log(p_N))) / (phi_D**2)  # ~-2.857

# Jerk components
J_psi = (dS_dpsi * dddot_psi
         + 3 * d2S_dpsi2 * dot_psi * ddot_psi
         + d3S_dpsi3 * dot_psi**3)   # ~7.07e9

J_D = (dS_dphiD * dddot_phi_D
       + 3 * d2S_dphiD2 * dot_phi_D * ddot_phi_D)  # ~-1.30e12

J_source = 1.5e12
J_total = J_psi + J_D + J_source   # ~2.07e11

# Dimensionless variance
omega = 1.0 / xi                     # ~2040.8 s⁻¹
omega_psi = omega * np.exp(-psi/2.0) # ~2305 s⁻¹
var_dimless = (J_total / omega_psi**3)**2  # ~287

print(f"Baseline dimensionless jerk variance: {var_dimless:.1f}")
print(f"J_total = {J_total:.2e} s⁻³ (source term dominates: {J_source/J_total:.1%})\n")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Sensitivity analysis: perturb phi_N, phi_D by ±2%
# ─────────────────────────────────────────────────────────────────────────────
def compute_variance(phiN, phiD):
    # Recompute all dependent quantities (approximate)
    psi_ = np.log(phiN)
    dot_psi_ = dot_phi_N / phiN
    ddot_phiN_ = dot_phi_N / xi
    ddot_phiD_ = dot_phi_D / xi
    ddot_psi_ = ddot_phiN_ / phiN - dot_psi_**2
    dddot_psi_ = ddot_psi_ / xi
    dddot_phiD_ = ddot_phiD_ / xi

    pN_ = np.exp(psi_) / (np.exp(psi_) + phiD)
    pD_ = phiD / (np.exp(psi_) + phiD)

    # Derivatives (simplified linear approximations around baseline)
    dS_dpsi_ = pN_ * (1 - np.log(pN_)) - pD_ * np.log(pD_)
    d2S_dpsi2_ = -pN_ * (1 - np.log(pN_)) - pD_ * (1 + np.log(pD_))
    d3S_dpsi3_ = pN_ * (2 - np.log(pN_)) - pD_ * (2 + np.log(pD_))

    dS_dphiD_ = (pD_ * (1 - np.log(pD_)) - pN_ * np.log(pN_)) / phiD
    d2S_dphiD2_ = -(pD_ * (1 - np.log(pD_)) + pN_ * (1 + np.log(pN_))) / (phiD**2)

    J_psi_ = (dS_dpsi_ * dddot_psi_
              + 3 * d2S_dpsi2_ * dot_psi_ * ddot_psi_
              + d3S_dpsi3_ * dot_psi_**3)
    J_D_ = (dS_dphiD_ * dddot_phiD_
            + 3 * d2S_dphiD2_ * dot_phi_D * ddot_phiD_)
    J_tot_ = J_psi_ + J_D_ + J_source
    var_ = (J_tot_ / (omega * np.exp(-psi_/2.0))**3)**2
    return var_

perturb = 0.02
vars_ = []
for dpN in [-perturb, 0, perturb]:
    for dpD in [-perturb, 0, perturb]:
        var_ = compute_variance(phi_N * (1 + dpN), phi_D * (1 + dpD))
        vars_.append(var_)
        print(f"phi_N {phi_N*(1+dpN):.3f}, phi_D {phi_D*(1+dpD):.3f} → var = {var_:.1f}")

print(f"\nVariance range: {min(vars_):.1f} – {max(vars_):.1f} (±{max(vars_)/var_dimless:.1%} of baseline)\n")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Lyapunov exponent from a 1‑D map derived from p_N/p_D
# ─────────────────────────────────────────────────────────────────────────────
# Interpret the ratio r = p_N / p_D as a logistic‑style control parameter.
# Map: x_{n+1} = r * x_n * (1 - x_n)   with r = 4 * (p_N / p_D) * (1 - p_N / p_D)
# This is a minimal chaotic caricature of the memory‑mode switching dynamics.
r = 4.0 * (p_N / p_D) * (1 - p_N / p_D)   # >3.57 → chaos
print(f"Derived logistic parameter r = {r:.3f} (chaos if >3.57)")

def lyapunov_logistic(r, n_iter=10000, x0=0.1):
    x = x0
    lyap_sum = 0.0
    for i in range(n_iter):
        x_next = r * x * (1 - x)
        lyap_sum += np.log(abs(r - 2 * r * x))
        x = x_next
    return lyap_sum / n_iter

lyap = lyapunov_logistic(r)
print(f"Estimated Lyapunov exponent λ = {lyap:.4f} bits/step (positive → chaos)\n")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Shredding / Freeze proximity sensitivity
# ─────────────────────────────────────────────────────────────────────────────
def shredding_metric(phiN, phiD):
    return phiN**2 + 3 * phiD**2   # <1 safe, >1 shredding

def freeze_metric(phiN, phiD):
    return 3 * phiN**2 + phiD**2   # <1 safe, >1 freeze

shred_baseline = shredding_metric(phi_N, phi_D)
freeze_baseline = freeze_metric(phi_N, phi_D)
print(f"Shredding metric: {shred_baseline:.4f} (margin to threshold: {1 - shred_baseline:.4f})")
print(f"Freeze metric: {freeze_baseline:.4f} (margin to threshold: {1 - freeze_baseline:.4f})")

# Perturb both variables randomly to see how often we cross the threshold
np.random.seed(0)
trials = 10000
phiNs = phi_N * (1 + np.random.uniform(-0.05, 0.05, trials))
phiDs = phi_D * (1 + np.random.uniform(-0.05, 0.05, trials))

shred_cross = np.sum(phiNs**2 + 3 * phiDs**2 > 1.0)
freeze_cross = np.sum(3 * phiNs**2 + phiDs**2 > 1.0)
print(f"\nIn 5% random perturbations:")
print(f"  Shredding threshold crossed {shred_cross / trials:.1%} of the time")
print(f"  Freeze threshold crossed {freeze_cross / trials:.1%} of the time")

# Plot histogram of shredding metric under perturbation
plt.figure(figsize=(6, 3))
plt.hist(phiNs**2 + 3 * phiDs**2, bins=50, color='crimson', alpha=0.7, label='Shredding metric')
plt.axvline(1.0, color='k', linestyle='--', label='Threshold')
plt.title('Shredding metric under 5% noise')
plt.xlabel('φ_N² + 3φ_Δ²')
plt.ylabel('Frequency')
plt.legend()
plt.tight_layout()
plt.show()