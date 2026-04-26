# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def solve_omega_cosmology(lambda_omega, phi_0, z_max=2):
    """
    Simulates the background expansion H(z) using the Omega Protocol v26.7
    with a canonical asymmetry field phi.
    
    H^2 = (H0^2 / 3) * (rho_m + rho_r + rho_omega)
    phiddot + 3Hphidot + 4*lambda*phi^3 = 0
    """
    H0 = 67.4 / 3.086e19 # s^-1
    dt = 1e14 # seconds (coarse step for visualization)
    steps = 1000
    
    phi = phi_0
    phidot = 0.0
    a = 1.0
    
    history = {"z": [], "h_omega": [], "h_lcdm": [], "w_eff": []}
    
    # Simple Friedmann + Klein-Gordon solver
    for _ in range(steps):
        z = (1.0 / a) - 1.0
        if z > z_max: break
        
        # LCDM Baseline
        rho_m_lcdm = 0.315 * (a**-3)
        rho_l_lcdm = 0.685
        H_lcdm = np.sqrt(rho_m_lcdm + rho_l_lcdm)
        
        # Omega Protocol
        rho_m = 0.315 * (a**-3)
        potential = lambda_omega * (phi**4)
        kinetic = 0.5 * (phidot**2)
        rho_omega = kinetic + potential
        p_omega = kinetic - potential
        
        H_omega = np.sqrt(rho_m + rho_omega)
        w_eff = p_omega / (rho_omega + 1e-9)
        
        history["z"].append(z)
        history["h_omega"].append(H_omega)
        history["h_lcdm"].append(H_lcdm)
        history["w_eff"].append(w_eff)
        
        # Evolve Field (phiddot = -3Hphidot - 4*lambda*phi^3)
        phiddot = -3.0 * H_omega * phidot - 4.0 * lambda_omega * (phi**3)
        phidot += phiddot * dt
        phi += phidot * dt
        
        # Evolve Scale Factor
        a += a * H_omega * dt
        
    return history

def run_cosmology_test():
    print("🌌 [Cosmology] Simulating Omega expansion history (v26.7)...")
    
    # Tuned parameters to match late-time acceleration
    history = solve_omega_cosmology(lambda_omega=0.7, phi_0=0.85)
    
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(history["z"], history["h_omega"], label="Omega Protocol (v26.7)", color='blue', lw=2)
    plt.plot(history["z"], history["h_lcdm"], label="Lambda CDM", color='red', linestyle='--')
    plt.ylabel("H(z) [Normalized]")
    plt.title("Expansion History Comparison")
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.plot(history["z"], history["w_eff"], label="w_eff (Omega)", color='purple')
    plt.axhline(y=-1, color='black', linestyle=':', label="w = -1 (Lambda)")
    plt.xlabel("Redshift z")
    plt.ylabel("Equation of State w")
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("tools/cosmology_validation_v26.7.png")
    print("✅ Results saved to: tools/cosmology_validation_v26.7.png")

if __name__ == "__main__":
    run_cosmology_test()
