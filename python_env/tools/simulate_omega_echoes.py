# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_omega_echoes(M_solar=10.0, phi_min=1e-6, R0=0.8, omega_c=100.0, num_echoes=3):
    """
    Physics-grade simulation of gravitational wave echoes in the Omega Protocol.
    
    Parameters:
    - M_solar: Mass of the black hole in solar masses.
    - phi_min: The freeze boundary floor for the Phi field (from Governor.hpp).
    - R0: Peak reflectivity at the low-frequency (hard-wall) limit.
    - omega_c: Characteristic frequency scale for reflectivity decay.
    - num_echoes: Number of echoes to simulate.
    """
    # --- Physical Constants ---
    G = 6.67430e-11        # Gravitational constant (m^3 kg^-1 s^-2)
    c = 299792458          # Speed of light (m/s)
    M_sun_kg = 1.989e30    # Mass of the sun (kg)
    
    # --- Calculated Parameters ---
    M_kg = M_solar * M_sun_kg
    r_s = (2.0 * G * M_kg) / (c**2)
    t_light_rs = r_s / c   # Time for light to cross r_s
    
    # Delta_t derivation from Omega Protocol: delta_t ~ (4GM/c^3) * |ln(Phi_min)|
    # This accounts for the proper time delay to the physical freeze boundary.
    delta_t = (4.0 * G * M_kg / (c**3)) * np.abs(np.log(phi_min))
    
    print(f"--- Omega Protocol Physics Parameters ---")
    print(f"Mass: {M_solar} M_sol")
    print(f"Schwarzschild Radius (r_s): {r_s:.2f} meters")
    print(f"Freeze Boundary Floor (phi_min): {phi_min}")
    print(f"Calculated Echo Delay (delta_t): {delta_t:.4f} seconds")
    
    # --- Time Setup ---
    fs = 4000              # Sampling frequency (Hz) - higher for better resolution
    duration = max(0.5, (num_echoes + 1) * delta_t)
    t = np.linspace(0, duration, int(fs * duration))
    
    # --- 1. Primary Signal (Gaussian Ringdown Pulse) ---
    f_gw = 100.0            # Core GW frequency (Hz)
    pulse_width = 0.005     # Standard ringdown width
    t0 = 0.05               # Initial merger time
    primary = np.exp(-((t - t0)**2) / (pulse_width**2)) * np.sin(2 * np.pi * f_gw * t)
    
    # --- 2. Reflectivity R(omega) ---
    # Derived from the impedance mismatch at the kinetic divergence K(Phi)=1/Phi^2.
    def get_reflectivity(freq):
        # Physical model: R approaches R0 at low frequencies and decays at high frequencies
        # due to penetration into the 'viscous' informational substrate.
        return R0 * np.exp(-freq / omega_c)

    # --- 3. Generate Echoes ---
    signal = primary.copy()
    
    for i in range(1, num_echoes + 1):
        echo_delay = i * delta_t
        
        # Calculate frequency-dependent attenuation
        R = get_reflectivity(f_gw)
        amplitude = R**i  # Compounding reflection losses
        
        # Shift and add echo (with dispersion/broadening)
        # Dispersion increases with each reflection due to non-trivial scalar potential
        dispersion_factor = 1.0 + (i * 0.15)
        shifted_t = t - echo_delay
        echo_val = amplitude * np.exp(-((shifted_t - t0)**2) / ((pulse_width * dispersion_factor)**2)) * \
                   np.sin(2 * np.pi * (f_gw * (0.98**i)) * shifted_t)
        
        # Mask negative time shifts
        echo_val[t < echo_delay] = 0
        signal += echo_val

    # --- Plotting ---
    plt.figure(figsize=(14, 7))
    plt.plot(t, primary, label="Primary GW Ringdown (GR Baseline)", alpha=0.3, linestyle='--')
    plt.plot(t, signal, label="Omega Protocol Echo Signal", color='blue', linewidth=1.5)
    
    # Annotate Echoes
    for i in range(1, num_echoes + 1):
        x_pos = t0 + i*delta_t
        plt.axvline(x=x_pos, color='red', alpha=0.3, linestyle=':')
        plt.text(x_pos, 0.4, f"Echo {i}\n(R={get_reflectivity(f_gw)**i:.2f})", color='red', rotation=90, ha='right')

    plt.title(f"Gravitational Wave Echoes: Omega Protocol Derivation\n(M={M_solar} M_sol, $\\Phi_{{min}}$={phi_min}, $\\Delta t$={delta_t:.3f}s)")
    plt.xlabel("Time (s)")
    plt.ylabel("Strain (h)")
    plt.grid(True, which='both', alpha=0.3)
    plt.legend()
    
    output_path = "omega_echo_physics_grade.png"
    plt.savefig(output_path)
    print(f"Simulation complete. Physics-grade plot saved to {output_path}")
    
    return signal

if __name__ == "__main__":
    simulate_omega_echoes()
