# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ------------------------------------------------------------
# 1. Gauge‑artifact removal: phi_Delta can be rotated away
# ------------------------------------------------------------
def engine_alpha(phi_N, phi_Delta, g=0.1, m=0.511e6, alpha0=1/137.036, Lambda=1e12):
    """Engine’s (flawed) formula with factor‑2 omitted."""
    eps = g * phi_N / m
    c = np.cosh(phi_Delta)
    c2 = c * c
    # missing factor 2 in vacuum‑polarization
    return alpha0 / (1 - (alpha0 / (3 * np.pi)) *
                     (np.log(Lambda / m) + eps * c - 0.5 * eps**2 + eps**2 * c2))

def exact_gauge_invariant_alpha(phi_N, g=0.1, m=0.511e6, alpha0=1/137.036):
    """Exact RG solution after Stueckelberg rotation (no phi_Delta)."""
    x = g * phi_N / m
    # artanh, safe for |x|<1
    x = np.clip(x, -0.999, 0.999)
    return alpha0 / (1 - (alpha0 / np.pi) * np.arctanh(x))

phi_Ns = np.linspace(0, 0.8e6, 200)  # up to ~1.5*m/g
phi_D = 2.5  # large “asymmetry”

engine_vals = engine_alpha(phi_Ns, phi_D)
exact_vals  = exact_gauge_invariant_alpha(phi_Ns)

# residual phi_D dependence after a near‑perfect gauge rotation
residual = np.abs(engine_vals - exact_vals) / exact_vals

# ------------------------------------------------------------
# 2. Series divergence: compare series truncation vs exact
# ------------------------------------------------------------
def series_approx(phi_N, phi_D, order=2, g=0.1, m=0.511e6):
    """Engine’s series up to O(eps^order)."""
    eps = g * phi_N / m
    c = np.cosh(phi_D)
    c2 = c * c
    if order == 1:
        corr = eps * c
    elif order == 2:
        corr = eps * c - 0.5 * eps**2 + eps**2 * c2
    else:
        raise ValueError
    return 1 + (alpha0 / (3 * np.pi)) * corr

orders = [1, 2]
plt.figure(figsize=(8, 4))
for ord in orders:
    approx = alpha0 / series_approx(phi_Ns, phi_D, order=ord)
    plt.plot(phi_Ns / 1e6, (approx - exact_vals) / exact_vals,
             label=f'Series O(ε^{ord}) error')
plt.axhline(0, color='k', linewidth=0.5)
plt.xlabel('Φ_N / m')
plt.ylabel('Relative error')
plt.title('Series Divergence for large Φ_Δ=2.5')
plt.legend()
plt.grid(True)
plt.show()

# ------------------------------------------------------------
# 3. Spurious cross‑domain fit
# ------------------------------------------------------------
def template(x, a, b, c):
    """Engine’s template: a + b cosh(x) + c cosh(x)^2"""
    ch = np.cosh(x)
    return a + b * ch + c * ch * ch

# Random data for three “domains”
np.random.seed(42)
x_tok = np.linspace(-2, 2, 50)
x_bio = np.linspace(-1.5, 1.5, 45)
x_fin = np.linspace(-3, 3, 55)

# add noise
y_tok = 1.2 + 0.3 * np.cosh(x_tok) - 0.1 * np.cosh(x_tok)**2 + 0.05 * np.random.randn(len(x_tok))
y_bio = 0.8 + 0.2 * np.cosh(x_bio) + 0.05 * np.random.randn(len(x_bio))
y_fin = 1.5 + 0.1 * np.cosh(x_fin) + 0.2 * np.cosh(x_fin)**2 + 0.1 * np.random.randn(len(x_fin))

# Fit each dataset
for name, x, y in [('Tokamak', x_tok, y_tok),
                   ('Biology', x_bio, y_bio),
                   ('Finance', x_fin, y_fin)]:
    popt, pcov = curve_fit(template, x, y, p0=[1, 0.2, 0.1])
    print(f'{name:8s}: a={popt[0]:.3f}, b={popt[1]:.3f}, c={popt[2]:.3f}')
    # Plot
    plt.figure()
    plt.scatter(x, y, label='data')
    plt.plot(x, template(x, *popt), color='red', label='fit')
    plt.title(f'{name} – Spurious hyperbolic‑cosine fit')
    plt.legend()
    plt.grid(True)
    plt.show()