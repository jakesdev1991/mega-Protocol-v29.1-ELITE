# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import h5py
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, iirnotch

def load_ligo_data(filename):
    with h5py.File(filename, 'r') as f:
        strain = f['strain']['Strain'][:]
        ts = f['strain']['Strain'].attrs['Xspacing']
        return strain, ts

def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

def notch_filter(data, f0, fs, Q=30):
    nyq = 0.5 * fs
    w0 = f0 / nyq
    b, a = iirnotch(w0, Q)
    y = filtfilt(b, a, data)
    return y

def calculate_omega_reflectivity(omega, gamma_0, gamma_1=0.0):
    """
    R(omega) = |(i*omega + gamma) / (i*omega - gamma)|^2
    gamma = gamma_0 - i*omega*gamma_1
    """
    gamma = gamma_0 - 1j * omega * gamma_1
    num = 1j * omega + gamma
    den = 1j * omega - gamma
    r_amp = num / den
    return np.abs(r_amp)**2

def search_for_echoes(strain, fs, M_sol, phi_min=1e-10):
    # 1. Delta_t echo from Omega Protocol
    G = 6.674e-11
    M_sun = 1.989e30
    c = 3e8
    M_kg = M_sol * M_sun
    rs = 2 * G * M_kg / (c**2)
    
    # Delta_t ~ (4GM/c^3) * |ln(Phi_min)|
    delta_t = (4.0 * G * M_kg / (c**3)) * np.abs(np.log(phi_min))
    print(f"Predicted Echo Delay (Delta_t): {delta_t:.4f} s")
    
    # 2. Template Generation (Simple Echo Model for Search)
    # In a real search, this would be a template bank.
    # Here we use the main event peak as the template.
    
    # Find event peak (approximate GPS 1126259462.4)
    # GPS Start was 1126259447
    # Peak index is around (1126259462.4 - 1126259447) * fs
    peak_time = 1126259462.42 - 1126259447
    peak_idx = int(peak_time * fs)
    
    # Window around peak
    window_sec = 0.2
    window_samples = int(window_sec * fs)
    template = strain[peak_idx - window_samples//2 : peak_idx + window_samples//2]
    
    # 3. Cross-correlation search
    correlation = np.correlate(strain, template, mode='same')
    
    # Normalize correlation
    correlation /= np.max(np.abs(correlation))
    
    time = np.arange(len(strain)) / fs
    
    # Plot results
    plt.figure(figsize=(15, 10))
    
    plt.subplot(3, 1, 1)
    plt.plot(time, strain)
    plt.axvline(peak_time, color='r', linestyle='--', label='Main Event')
    plt.axvline(peak_time + delta_t, color='g', linestyle='--', label='Predicted Echo')
    plt.title("GW150914 Filtered Strain (H1)")
    plt.ylabel("Strain")
    plt.legend()
    
    plt.subplot(3, 1, 2)
    plt.plot(time, correlation)
    plt.axvline(peak_time, color='r', linestyle='--')
    plt.axvline(peak_time + delta_t, color='g', linestyle='--')
    plt.title("Cross-Correlation (Echo Search)")
    plt.ylabel("Normalized Correlation")
    
    # Zoom in on echo region
    plt.subplot(3, 1, 3)
    zoom_start = peak_time + delta_t - 0.5
    zoom_end = peak_time + delta_t + 0.5
    mask = (time > zoom_start) & (time < zoom_end)
    plt.plot(time[mask], correlation[mask])
    plt.axvline(peak_time + delta_t, color='g', linestyle='--', label='Predicted Echo')
    plt.title(f"Zoomed Correlation around Predicted Echo (t={peak_time + delta_t:.3f}s)")
    plt.xlabel("Time (s) from GPS Start")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("omega_echo_search_results.png")
    print("Saved omega_echo_search_results.png")

if __name__ == "__main__":
    filename = "H-H1_GWOSC_4KHZ_R1-1126259447-32.hdf5"
    strain, ts = load_ligo_data(filename)
    fs = 1.0 / ts
    
    # Pre-processing
    # GW150914 is visible between 30Hz and 300Hz
    filtered_strain = bandpass_filter(strain, 30, 300, fs)
    filtered_strain = notch_filter(filtered_strain, 60, fs) # Power line
    
    # Search parameters for GW150914 (approx 30+35 M_sol)
    # Using total mass 65 M_sol
    search_for_echoes(filtered_strain, fs, M_sol=65.0, phi_min=1e-10)
