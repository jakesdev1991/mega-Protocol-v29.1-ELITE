# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def calculate_reflectivity(omega, gamma):
    """
    Calculates R(omega) for a mixed boundary condition u' = gamma * u.
    u = exp(-i*omega*r_*) + R_amp * exp(i*omega*r_*)
    """
    # R_amp = (i*omega + gamma) / (i*omega - gamma)
    # This assumes we are at r_* = 0 for simplicity (it only shifts the phase)
    num = 1j * omega + gamma
    den = 1j * omega - gamma
    r_amp = num / den
    return np.abs(r_amp)**2, np.angle(r_amp)

def plot_reflectivity():
    omegas = np.linspace(0.1, 100, 1000)
    
    # Case 1: Hard Wall (gamma -> infinity)
    # Case 2: Soft Wall (gamma real)
    # Case 3: Absorbing Wall (gamma complex)
    
    gammas = {
        "Hard Wall (gamma=1e6)": 1e6,
        "Soft Wall (gamma=10)": 10.0,
        "Absorbing Wall (gamma=10 - 5j)": 10.0 - 5.0j,
        "Frequency Dependent (gamma=0.1*i*omega)": 0.1j * omegas
    }
    
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    for label, g in gammas.items():
        r_sq, phase = calculate_reflectivity(omegas, g)
        plt.plot(omegas, r_sq, label=label)
    
    plt.axhline(1.0, color='k', linestyle='--', alpha=0.5)
    plt.ylabel(r"$R(\omega) = |\mathcal{R}|^2$")
    plt.title(r"Omega Protocol: Reflectivity $R(\omega)$ from Mixed Boundary Condition")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    for label, g in gammas.items():
        r_sq, phase = calculate_reflectivity(omegas, g)
        plt.plot(omegas, phase, label=label)
    
    plt.ylabel(r"Phase $\arg(\mathcal{R})$")
    plt.xlabel(r"Frequency $\omega$")
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("reflectivity_analysis.png")
    print("Saved reflectivity_analysis.png")

if __name__ == "__main__":
    plot_reflectivity()
