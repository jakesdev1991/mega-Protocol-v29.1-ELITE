# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import requests
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, iirnotch, welch
import os

def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        print(f"Downloading {url}...")
        r = requests.get(url, allow_redirects=True)
        with open(local_filename, 'wb') as f:
            f.write(r.content)
        print(f"Downloaded {local_filename}")
    return local_filename

def whiten_data(strain, fs):
    """
    Whitens the strain data by dividing by the ASD (Amplitude Spectral Density).
    """
    f, psd = welch(strain, fs=fs, nperseg=fs) # 1s segments
    psd_interp = np.interp(np.fft.rfftfreq(len(strain), 1/fs), f, psd)
    
    # FFT, whiten, and IFFT
    hf = np.fft.rfft(strain)
    white_hf = hf / np.sqrt(psd_interp)
    white_strain = np.fft.irfft(white_hf, n=len(strain))
    return white_strain

def calculate_omega_reflectivity(omega, gamma_0, gamma_abs=0.1):
    """
    FIXED: Amplitude reflection coefficient r(omega) = (i*omega - Gamma) / (i*omega + Gamma)
    Gamma = gamma_0 + i * gamma_abs * omega (Dissipative Robin parameter)
    """
    Gamma = gamma_0 + 1j * gamma_abs * omega
    r = (1j * omega - Gamma) / (1j * omega + Gamma)
    return np.abs(r)**2, np.angle(r)

def run_upgraded_search(M_sol=65.0, mode='physical'):
    # 1. Constants
    G = 6.674e-11
    M_sun = 1.989e30
    c = 299792458.0
    lp = 1.616e-35
    M_kg = M_sol * M_sun
    rs = 2 * G * M_kg / (c**2)
    
    # 2. Modes for Phi_min
    if mode == 'physical':
        # Planck/Kretschmann scaling: Phi_min ~ lp / rs
        phi_min = lp / rs
        label = "Physical (Planck/Kretschmann)"
    else:
        # Phenomenological mode (user specified or scan)
        phi_min = 1e-10
        label = "Phenomenological"
        
    delta_t = (4.0 * G * M_kg / (c**3)) * np.abs(np.log(phi_min))
    print(f"--- Mode: {label} ---")
    print(f"Phi_min: {phi_min:.2e}")
    print(f"Predicted Delay Delta_t: {delta_t:.4f} s")

    # 3. Download and Load H1 + L1
    h1_url = "https://gwosc.org/eventapi/html/GWTC-1-confident/GW150914/v3/H-H1_GWOSC_4KHZ_R1-1126259447-32.hdf5"
    l1_url = "https://gwosc.org/eventapi/html/GWTC-1-confident/GW150914/v3/L-L1_GWOSC_4KHZ_R1-1126259447-32.hdf5"
    
    h1_file = download_file(h1_url, "H1_data.hdf5")
    l1_file = download_file(l1_url, "L1_data.hdf5")
    
    with h5py.File(h1_file, 'r') as f:
        h1_strain = f['strain']['Strain'][:]
        fs = 1.0 / f['strain']['Strain'].attrs['Xspacing']
    with h5py.File(l1_file, 'r') as f:
        l1_strain = f['strain']['Strain'][:]

    # 4. Processing (Bandpass + Whitening)
    def process_strain(data):
        # Initial bandpass 30-300Hz
        nyq = 0.5 * fs
        b, a = butter(4, [30/nyq, 300/nyq], btype='band')
        y = filtfilt(b, a, data)
        # Whiten
        y = whiten_data(y, fs)
        return y

    h1_proc = process_strain(h1_strain)
    l1_proc = process_strain(l1_strain)

    # 5. Coincidence Matched Filter
    # Template: 0.1s around peak for GW150914
    peak_gps = 1126259462.42
    start_gps = 1126259447
    peak_idx = int((peak_gps - start_gps) * fs)
    
    tmpl_len = int(0.1 * fs)
    template = h1_proc[peak_idx - tmpl_len//2 : peak_idx + tmpl_len//2]
    
    h1_corr = np.correlate(h1_proc, template, mode='same')
    l1_corr = np.correlate(l1_proc, template, mode='same')
    
    # Combined SNR-like statistic (H1 * L1)
    combined = np.abs(h1_corr) * np.abs(l1_corr)
    combined /= np.max(combined)
    
    time = np.arange(len(h1_strain)) / fs
    peak_time = peak_gps - start_gps

    # 6. Plotting
    plt.figure(figsize=(15, 12))
    
    # SNR plot
    plt.subplot(3, 1, 1)
    plt.plot(time, combined, color='purple', label='Coincidence Power (H1*L1)')
    plt.axvline(peak_time, color='r', linestyle='--', alpha=0.5, label='Merger')
    plt.axvline(peak_time + delta_t, color='g', linestyle='--', label=f'Echo @ {delta_t:.3f}s')
    plt.title(f"Omega Protocol Echo Search (GW150914) - {label} Mode")
    plt.ylabel("Normalized Power")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Zoomed SNR
    plt.subplot(3, 1, 2)
    zoom_window = 0.5
    mask = (time > peak_time + delta_t - zoom_window) & (time < peak_time + delta_t + zoom_window)
    plt.plot(time[mask], combined[mask], color='purple')
    plt.axvline(peak_time + delta_t, color='g', linestyle='--')
    plt.title(f"Zoomed Region around Predicted Echo Delay ({delta_t:.4f}s)")
    plt.ylabel("Power")
    plt.grid(True, alpha=0.3)

    # R(omega) visualization
    plt.subplot(3, 1, 3)
    f_scan = np.linspace(10, 1000, 500)
    omega_scan = 2 * np.pi * f_scan
    # Use Gamma parameters from whitepaper (gamma_0=10, gamma_abs=0.1)
    R_vals = [calculate_omega_reflectivity(w, 10.0, 0.1)[0] for w in omega_scan]
    plt.plot(f_scan, R_vals, label="Reflectivity $R(\omega)$")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Reflectivity")
    plt.title("Omega Substrate Informational Impedance ($R(\omega)$)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("omega_physics_grade_results.png")
    print("Saved omega_physics_grade_results.png")

if __name__ == "__main__":
    # Execute Mode A: Physical Planck Scaling
    run_upgraded_search(mode='physical')
