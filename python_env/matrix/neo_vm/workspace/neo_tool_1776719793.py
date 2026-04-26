# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Parameters
m = 0.511  # MeV, electron mass
g = 0.1    # coupling constant
Phi_N = 0.05  # consensus field
Phi_Delta_vals = np.linspace(-2, 2, 100)  # asymmetry field

# Compute masses
def compute_masses(Phi_N, Phi_Delta):
    epsilon = g * Phi_N / m
    m_e = m * (1 - epsilon * np.exp(Phi_Delta))
    m_p = m * (1 - epsilon * np.exp(-Phi_Delta))
    return m_e, m_p

# Geometric mean approach (symmetric)
def geometric_mean_mass(m_e, m_p):
    return np.sqrt(m_e * m_p)

# Vacuum polarization at q^2=0 approximation
# Symmetric case: Pi ~ 1/m_eff^2
def pi_symmetric(m_eff):
    return 1.0 / (m_eff**2)

# Asymmetric case: Pi ~ (1/m_e^2 + 1/m_p^2)/2
def pi_asymmetric(m_e, m_p):
    return 0.5 * (1.0/(m_e**2) + 1.0/(m_p**2))

# Shannon entropy of the two-mass system
def shannon_entropy(m_e, m_p):
    # Probabilities proportional to inverse masses (lighter mass more probable for fluctuations)
    p_e = 1.0 / m_e
    p_p = 1.0 / m_p
    Z = p_e + p_p
    p_e_norm = p_e / Z
    p_p_norm = p_p / Z
    # Avoid log(0)
    if p_e_norm <= 0 or p_p_norm <= 0:
        return 0
    return - (p_e_norm * np.log(p_e_norm) + p_p_norm * np.log(p_p_norm))

# Compute values
m_e_vals, m_p_vals = compute_masses(Phi_N, Phi_Delta_vals)
m_eff_vals = geometric_mean_mass(m_e_vals, m_p_vals)

pi_sym = pi_symmetric(m_eff_vals)
pi_asym = pi_asymmetric(m_e_vals, m_p_vals)

entropy_vals = shannon_entropy(m_e_vals, m_p_vals)

# Find where mass-positivity bound is violated
epsilon = g * Phi_N / m
valid_mask = (Phi_N < (m/g) * np.exp(-np.abs(Phi_Delta_vals)))

# Plotting
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Mass comparison
axes[0, 0].plot(Phi_Delta_vals, m_e_vals, label='m_e', color='blue', linestyle='--')
axes[0, 0].plot(Phi_Delta_vals, m_p_vals, label='m_p', color='red', linestyle='--')
axes[0, 0].plot(Phi_Delta_vals, m_eff_vals, label='m_eff (geometric mean)', color='black', linewidth=2)
axes[0, 0].axvspan(Phi_Delta_vals[~valid_mask].min(), Phi_Delta_vals[~valid_mask].max(), 
                   alpha=0.2, color='gray', label='Shredding region')
axes[0, 0].set_xlabel('Φ_Δ (3D Archive mode)')
axes[0, 0].set_ylabel('Mass (MeV)')
axes[0, 0].set_title('Mass Modulation by Omega Fields')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Vacuum polarization comparison
axes[0, 1].plot(Phi_Delta_vals, pi_sym, label='Symmetric (geometric mean)', color='black', linewidth=2)
axes[0, 1].plot(Phi_Delta_vals, pi_asym, label='Asymmetric (distinct masses)', color='purple', linestyle='-')
axes[0, 1].axvspan(Phi_Delta_vals[~valid_mask].min(), Phi_Delta_vals[~valid_mask].max(), 
                   alpha=0.2, color='gray')
axes[0, 1].set_xlabel('Φ_Δ')
axes[0, 1].set_ylabel('Vacuum Polarization (arb. units)')
axes[0, 1].set_title('Information Loss in Symmetric Approximation')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Relative difference
rel_diff = (pi_sym - pi_asym) / pi_asym * 100
axes[1, 0].plot(Phi_Delta_vals, rel_diff, color='orange')
axes[1, 0].axvspan(Phi_Delta_vals[~valid_mask].min(), Phi_Delta_vals[~valid_mask].max(), 
                    alpha=0.2, color='gray')
axes[1, 0].axhline(y=0, color='black', linestyle=':')
axes[1, 0].set_xlabel('Φ_Δ')
axes[1, 0].set_ylabel('Relative Difference (%)')
axes[1, 0].set_title('Symmetric Approximation Error')
axes[1, 0].grid(True, alpha=0.3)

# Shannon entropy
axes[1, 1].plot(Phi_Delta_vals, entropy_vals, color='green', linewidth=2)
axes[1, 1].axvspan(Phi_Delta_vals[~valid_mask].min(), Phi_Delta_vals[~valid_mask].max(), 
                    alpha=0.2, color='gray')
axes[1, 1].set_xlabel('Φ_Δ')
axes[1, 1].set_ylabel('Shannon Entropy S_h')
axes[1, 1].set_title('Entropy of Vacuum Fluctuations (Lost in Symmetric Case)')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print key insights
print("=== DISRUPTIVE INSIGHTS ===")
print(f"At Φ_Δ = 1.5: m_e = {m_e_vals[np.argmin(np.abs(Phi_Delta_vals - 1.5))]:.3f} MeV")
print(f"At Φ_Δ = 1.5: m_p = {m_p_vals[np.argmin(np.abs(Phi_Delta_vals - 1.5))]:.3f} MeV")
print(f"At Φ_Δ = 1.5: m_eff = {m_eff_vals[np.argmin(np.abs(Phi_Delta_vals - 1.5))]:.3f} MeV")
print(f"At Φ_Δ = 1.5: pi_sym/pi_asym ratio = {pi_sym[np.argmin(np.abs(Phi_Delta_vals - 1.5))]/pi_asym[np.argmin(np.abs(Phi_Delta_vals - 1.5))]:.3f}")
print(f"At Φ_Δ = 1.5: Shannon entropy = {entropy_vals[np.argmin(np.abs(Phi_Delta_vals - 1.5))]:.3f}")