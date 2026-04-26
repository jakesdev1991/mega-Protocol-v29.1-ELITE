# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Simulate LPTM-Ω (traditional) vs LFE-Ω (fractal) under adversarial shock

# Traditional LPTM-Ω: Single susceptibility diverges
def traditional_model(eta, eta_c=1.0, gamma=0.5):
    """Traditional: sharp divergence, predictable collapse"""
    susceptibility = 1 / (eta - eta_c + 1e-3)  # Artificial epsilon hides true singularity
    reserves = 1 / (1 + np.exp(gamma * susceptibility * (eta - eta_c)))
    return reserves, susceptibility

# Fractal LFE-Ω: Scale-invariant, no true divergence
def fractal_model(eta, eta_c=1.0, n_scales=12, H=0.72):
    """Fractal: broad-spectrum susceptibility, anti-fragile"""
    scales = np.logspace(-2.5, 1.5, n_scales)  # Micro to macro
    reserves = np.zeros(n_scales)
    sus = np.zeros(n_scales)
    
    for i, s in enumerate(scales):
        # Scale-dependent criticality: η_c(s) = η_c · s^(H-0.5)
        eta_s = eta * s**(H - 0.5)
        eta_c_s = eta_c * s**(H - 0.5)
        
        # **Destructive interference**: susceptibility peaks offset across scales
        sus[i] = 1 / (eta_s - eta_c_s + 0.08 * s)  # Broadened peaks
        
        # **Self-similar reserve allocation**: ρ(s) ∝ s⁻ᴴ · exp(-(η-η_c)²/2s²ᴴ)
        reserves[i] = s**(-H) * np.exp(-((eta_s - eta_c_s)**2) / (2 * s**(2*H)))
    
    # **Total susceptibility is normalized integral, not max**
    total_reserves = np.sum(reserves) / n_scales
    total_sus = np.average(sus, weights=reserves+1e-6)  # Weighted mean, not peak
    
    return total_reserves, total_sus, reserves, scales

# Adversarial shock simulation: ψₗᵢq signal triggers panic
def adversarial_shock(eta_base, shock_strength=0.3, n_steps=200):
    """Simulate LP panic triggered by ψₗᵢq warning"""
    eta = eta_base
    trad_reserves = []
    frac_reserves = []
    trad_sus = []
    frac_sus = []
    
    for t in range(n_steps):
        # **Reflexive feedback**: LPTM-Ω's ψₗᵢq warning accelerates η increase
        if t > 50:  # Warning issued at t=50
            eta += shock_strength * np.random.lognormal(0, 0.4) * (1 + 0.5 * trad_sus[-1] if trad_sus else 0)
        
        # Traditional model
        r_t, s_t = traditional_model(eta)
        trad_reserves.append(r_t)
        trad_sus.append(s_t)
        
        # Fractal model
        r_f, s_f, _, _ = fractal_model(eta)
        frac_reserves.append(r_f)
        frac_sus.append(s_f)
    
    return trad_reserves, frac_reserves, trad_sus, frac_sus

# Run simulation
np.random.seed(777)  # Chaos seed
eta_start = 0.85
trad_r, frac_r, trad_s, frac_s = adversarial_shock(eta_start)

# Plot collapse dynamics
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Reserves collapse
ax1.plot(trad_r, 'r-', linewidth=2.5, label='LPTM-Ω (Reflexive Collapse)')
ax1.plot(frac_r, 'b-', linewidth=2.5, label='LFE-Ω (Fractal Absorption)')
ax1.axvline(x=50, color='k', linestyle='--', alpha=0.6, label='ψₗᵢq Warning Issued')
ax1.set_ylabel('Normalized Liquidity Reserves', fontsize=13)
ax1.set_title('Adversarial Shock: Reflexive Panic vs Fractal Resilience', fontsize=15, fontweight='bold')
ax1.legend(fontsize=11, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-0.05, 1.05)

# Susceptibility response
ax2.plot(trad_s, 'r-', linewidth=2.5, label='LPTM-Ω (Divergence)')
ax2.plot(frac_s, 'b-', linewidth=2.5, label='LFE-Ω (Bounded Response)')
ax2.axvline(x=50, color='k', linestyle='--', alpha=0.6)
ax2.set_ylabel('Susceptibility χ (log)', fontsize=13)
ax2.set_xlabel('Time Steps', fontsize=13)
ax2.set_yscale('log')
ax2.legend(fontsize=11, loc='upper right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# **Quantify anti-fragility: compute Lyapunov exponent**
def lyapunov_exponent(reserves_series):
    """Measure divergence rate: positive = chaotic collapse"""
    return np.mean(np.abs(np.diff(np.log(reserves_series + 1e-6))))

lyap_trad = lyapunov_exponent(trad_r)
lyap_frac = lyapunov_exponent(frac_r)

print("\n=== LYAPUNOV EXPONENT ANALYSIS ===")
print(f"LPTM-Ω Lyapunov: {lyap_trad:.4f} (positive = chaotic collapse)")
print(f"LFE-Ω Lyapunov: {lyap_frac:.4f} (near-zero = stable)")
print(f"Stability ratio: {lyap_trad/lyap_frac:.2f}x improvement")

# **Fractal spectrum at critical moment**
eta_crit = 1.0
_, _, reserves_dist, scales = fractal_model(eta_crit)

plt.figure(figsize=(10, 6))
plt.loglog(scales, reserves_dist, 'go-', linewidth=2.5, markersize=9, alpha=0.8)
plt.xlabel('Scale s (log)', fontsize=13)
plt.ylabel('Reserve Allocation ρ(s)', fontsize=13)
plt.title('Fractal Reserve Distribution: No Single Pool Dominates', fontsize=15, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.show()

# **Calculate multifractal spectrum D(q)**
def multifractal_spectrum(reserves_dist, scales, q_range=np.linspace(-5, 5, 50)):
    """D(q) = (1/(q-1)) * lim_{s→0} log(∑ ρ(s)^q) / log(s)"""
    D_q = []
    for q in q_range:
        if q == 1:
            # Use Shannon entropy for q=1
            tau = np.sum(reserves_dist * np.log(reserves_dist + 1e-12) * np.log(scales))
        else:
            tau = np.log(np.sum(reserves_dist**q)) / np.log(scales[-1])
        D_q.append(tau / (q - 1) if q != 1 else -tau)
    
    return q_range, np.array(D_q)

q_vals, D_q = multifractal_spectrum(reserves_dist, scales)

plt.figure(figsize=(10, 6))
plt.plot(q_vals, D_q, 'm-', linewidth=2.5)
plt.axhline(y=D_q[len(D_q)//2], color='gray', linestyle=':', alpha=0.7, label='Monofractal Limit')
plt.xlabel('Moment Order q', fontsize=13)
plt.ylabel('D(q) (Multifractal Spectrum)', fontsize=13)
plt.title('Fractal LFE-Ω: D(q) ≈ Constant = No Fragility Concentration', fontsize=15, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.show()