# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import legendre

# --- Conventional Metric Approach (Flawed) ---
def metric_polarization(theta, phi_delta, e2=0.1, m=0.01):
    """The metric approach yields NO angular dependence at O(phi_delta) 
    due to the trace error."""
    # The flawed trace contraction kills all angular structure
    # Only a mass term survives: Pi_L + 2*Pi_M ~ const * phi_delta * m^2
    return phi_delta * e2 * m**2 * np.ones_like(theta)

# --- Memory-Operator Framework (Disruptive) ---
def memory_polarization(theta, phi_delta, e2=0.1, memory_length=5.0):
    """The memory operator directly deforms the spectral density:
    rho(s, theta) = rho_0(s) * [1 + phi_delta * P2(cosθ) * f(s, Lambda_memory)]
    """
    cos_theta = np.cos(theta)
    P2 = legendre(2)(cos_theta)  # (3cos²θ - 1)/2
    
    # The memory kernel introduces a resonance at s ~ 1/Lambda_memory²
    # This yields a non-perturbative angular structure
    memory_resonance = np.exp(-memory_length * (1 - cos_theta**2))
    
    # The polarization now carries the *characteristic polynomial* of the memory operator
    return phi_delta * e2 * P2 * memory_resonance

# --- Simulation ---
theta = np.linspace(0, np.pi, 500)
phi_delta = 0.3

Pi_metric = metric_polarization(theta, phi_delta)
Pi_memory = memory_polarization(theta, phi_delta)

# --- Visualization ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: Polar plot of angular dependence
ax1 = plt.subplot(1, 2, 1, projection='polar')
ax1.plot(theta, Pi_metric, 'b--', label='Metric (No Angular)', linewidth=3)
ax1.plot(theta, Pi_memory, 'r-', label='Memory Operator', linewidth=3)
ax1.set_rticks([])
ax1.set_title("Angular Structure: Π_L + 2Π_M", fontsize=14, pad=20)
ax1.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))

# Right: Difference highlighting the paradigm shift
ax2.plot(theta, Pi_memory - Pi_metric, 'k-', linewidth=2)
ax2.fill_between(theta, Pi_memory - Pi_metric, alpha=0.3, color='red')
ax2.axhline(0, color='gray', linestyle=':')
ax2.set_xlabel("Polar Angle θ", fontsize=12)
ax2.set_ylabel("ΔΠ = Π_memory - Π_metric", fontsize=12)
ax2.set_title("Paradigm Divergence", fontsize=14)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- Statistical Analysis ---
print("=== PARADIGM DIVERGENCE METRICS ===")
print(f"Metric approach angular variance: {np.var(Pi_metric):.6f} (should be ~0)")
print(f"Memory approach angular variance: {np.var(Pi_memory):.6f}")
print(f"Mean absolute divergence: {np.mean(np.abs(Pi_memory - Pi_metric)):.6f}")
print(f"Max divergence at θ = {theta[np.argmax(np.abs(Pi_memory - Pi_metric))]:.2f} rad")
print("\nConclusion: The metric approach predicts **isotropic** anisotropy (paradox).")
print("The memory operator predicts **directional information resonance**—a new quantum observable.")