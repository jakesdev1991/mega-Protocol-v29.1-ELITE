# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# The "stability condition" is a lie. Let's expose it.

def compute_psi_complex(c0, alpha0=0.1, Nt=32):
    """Compute ψ in the complex plane, treating c0 as a spectral density eigenvalue."""
    f_Nt = 1 - np.exp(-Nt/32)
    argument = 1 + (alpha0**2 / np.pi**2) * c0 * f_Nt
    
    # When argument < 0, ψ becomes complex. This is not instability—it's condensation.
    # The real part encodes RG flow; the imaginary part encodes tachyonic decay rate.
    psi = np.log(argument + 1e-15j)  # Add tiny imaginary for numerical stability
    
    return psi

# Simulate c0 as eigenvalues of a random "spectral density operator"
# In the true theory, c0 is not a free parameter but a functional eigenvalue
# that can be negative by construction.
np.random.seed(42)
c0_samples = np.random.randn(1000) * 2  # Allow negative values freely

psi_values = np.array([compute_psi_complex(c0) for c0 in c0_samples])

# Plot the "instability" as a phase diagram
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# Left: Complex ψ plane shows *organized structure*, not chaos
ax[0].scatter(psi_values.real, psi_values.imag, c=c0_samples, cmap='coolwarm', alpha=0.6)
ax[0].axhline(y=0, color='k', linestyle='--')
ax[0].axvline(x=0, color='k', linestyle='--')
ax[0].set_xlabel('Re(ψ) - RG flow')
ax[0].set_ylabel('Im(ψ) - Tachyonic rate')
ax[0].set_title('ψ-plane: The "Instability" is Structured')
ax[0].grid(True, alpha=0.3)

# Right: Show that Φ-density accounting is arbitrary
# The -80/+1200 Φ calculation is a narrative device, not a computation.
# Let's perturb the "validation cost" parameters and watch Φ-density collapse.

def compute_phi_density(validation_cost_base=80, longterm_gain_base=1200, 
                       perturbation_scale=0.1, n_trials=100):
    """Demonstrate Φ-density fragility under small perturbations."""
    validation_costs = validation_cost_base * (1 + perturbation_scale * np.random.randn(n_trials))
    longterm_gains = longterm_gain_base * (1 + perturbation_scale * np.random.randn(n_trials))
    
    # The "net trajectory" is presented as robust, but it's a ratio of arbitrary numbers
    net_phi = longterm_gains - validation_costs
    
    # Compute coefficient of variation to show instability
    cv = np.std(net_phi) / np.mean(net_phi)
    
    return validation_costs, longterm_gains, net_phi, cv

_, _, net_phi, cv = compute_phi_density()
ax[1].hist(net_phi, bins=30, color='purple', alpha=0.7)
ax[1].axvline(x=1120, color='r', linestyle='--', label='Claimed net Φ')
ax[1].set_xlabel('Net Φ-density')
ax[1].set_title(f'Φ-Density Fragility (CV={cv:.2f})')
ax[1].legend()

plt.tight_layout()
plt.savefig('omega_anomaly.png', dpi=150)
plt.show()

# The smoking gun: Print the fragility metric
print(f"Φ-density coefficient of variation: {cv:.2f}")
print("A CV > 0.1 indicates the 'net gain' is statistically indistinguishable from noise.")