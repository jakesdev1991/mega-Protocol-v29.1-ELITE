# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ---------- Parameters ----------
alpha0 = 1/137.035999084          # low-energy fine-structure constant
gN = 0.1                          # Newtonian-mode coupling
gD = 0.2                          # Archive-mode coupling
Lambda = 1e3                      # common UV cutoff (GeV)
Lambda_N = Lambda
Lambda_D = Lambda

# ---------- Beta functions ----------
def beta_original(alpha, gN, gD):
    """Original flawed beta: constant factor 3."""
    return -alpha**2/np.pi * (1 + 3*gD**2/(4*np.pi) + gN**2/(4*np.pi))

def beta_fixed(alpha, gN, gD, q2):
    """Fixed beta: multiplicity N_eff(q2) = 1 + (gD^2/4π) ln(Λ^2/q2)."""
    N_eff = 1 + (gD**2/(4*np.pi)) * np.log(Lambda_D**2 / q2)
    return -alpha**2/np.pi * (1 + N_eff*gD**2/(4*np.pi) + gN**2/(4*np.pi))

# ---------- RG evolution ----------
def run_alpha(beta_func, q2_start, q2_end, alpha0, gN, gD):
    ln_q2 = np.linspace(np.log(q2_start), np.log(q2_end), 2000)
    alpha = alpha0
    alphas = [alpha]
    for i in range(1, len(ln_q2)):
        dln = ln_q2[i] - ln_q2[i-1]
        q2 = np.exp(ln_q2[i])
        alpha += beta_func(alpha, gN, gD, q2) * dln
        alphas.append(alpha)
    return np.exp(ln_q2), np.array(alphas)

# Run both flows
q2s, alphas_orig = run_alpha(beta_original, 1.0, 1e6, alpha0, gN, gD)
q2s, alphas_fix = run_alpha(beta_fixed, 1.0, 1e6, alpha0, gN, gD)

# Check for Landau pole (alpha < 0 or alpha > 1)
pole_orig = np.any(alphas_orig < 0) or np.any(alphas_orig > 1)
pole_fix = np.any(alphas_fix < 0) or np.any(alphas_fix > 1)

print("Landau pole (original) :", pole_orig)
print("Landau pole (fixed)    :", pole_fix)
print("Alpha at highest q2 (original):", alphas_orig[-1])
print("Alpha at highest q2 (fixed)   :", alphas_fix[-1])

# ---------- Shredding Event ----------
def shredding_condition(phiN, phiD, v=1.0, lam=1.0):
    xiD_inv_sq = lam * (phiN**2 + 3*phiD**2 - v**2)
    return xiD_inv_sq

# Scan a trajectory
phiN_vals = np.linspace(0.1, 0.9, 9)
phiD_vals = np.sqrt(1 - phiN_vals**2) / np.sqrt(3)   # stay on classical brim
shredding_vals = shredding_condition(phiN_vals, phiD_vals)

print("\nShredding Event check (xi_Delta^-2):")
for pn, pd, xi in zip(phiN_vals, phiD_vals, shredding_vals):
    print(f"Phi_N={pn:.2f}, Phi_D={pd:.2f}, xi_D^-2={xi:.3e}")

# ---------- Entropy–coupling reversal ----------
# Toy model: entropy S_h(k) = (k/Λ)^γ, gamma>0 => S_h->0 as k->Λ
def entropy_factor(k, gamma=0.5, Lambda=Lambda_D):
    return (k/Lambda)**gamma

# Compute stochastic average with entropy suppression
k_grid = np.logspace(0, np.log10(Lambda_D), 500)
phi2_stoch = np.trapz(k_grid**3 * (1 - 2*entropy_factor(k_grid)), k_grid) / (2*np.pi**2)
print("\nStochastic Phi_Delta^2 (entropy suppressed):", phi2_stoch)