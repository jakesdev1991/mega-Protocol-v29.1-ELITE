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
from scipy.signal.windows import tukey
import os
import pandas as pd
import time as time_mod

# 1. Gold Standard GWTC-1 BBH Events (Simplified parameters for sweep)
# Total masses are approximate remnant masses from GWTC-1
EVENTS = [
    {"name": "GW150914", "gps": 1126259462.4, "mass": 62.0},
    {"name": "GW151012", "gps": 1128678900.4, "mass": 35.0},
    {"name": "GW151226", "gps": 1135136350.6, "mass": 21.0},
    {"name": "GW170104", "gps": 1167559936.6, "mass": 49.0},
    {"name": "GW170608", "gps": 1180922494.5, "mass": 18.0},
    {"name": "GW170814", "gps": 1186741861.5, "mass": 53.0},
    {"name": "GW170823", "gps": 1187529256.5, "mass": 78.0},
]

def get_gwosc_urls_robust(event_name):
    """
    Robustly resolve GWOSC HDF5 URLs using the event API.
    """
    api_url = f"https://gwosc.org/eventapi/json/GWTC-1-confident/{event_name}/"
    try:
        r = requests.get(api_url, timeout=10)
        data = r.json()
        event_key = list(data['events'].keys())[0]
        strain_data = data['events'][event_key]['strain']
        
        h1_url = None
        l1_url = None
        
        for entry in strain_data:
            if entry['format'] == 'hdf5' and entry['sampling_rate'] == 4096:
                if entry['detector'] == 'H1':
                    h1_url = entry['url']
                elif entry['detector'] == 'L1':
                    l1_url = entry['url']
                    
        return h1_url, l1_url
    except Exception as e:
        print(f"Error querying GWOSC for {event_name}: {e}")
        return None, None

def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        print(f"Downloading {url}...")
        try:
            r = requests.get(url, allow_redirects=True, timeout=60)
            if r.status_code == 200:
                with open(local_filename, 'wb') as f:
                    f.write(r.content)
            else:
                print(f"Failed: Status {r.status_code}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    return local_filename

def whiten_data(strain, fs):
    # Apply Tukey window to reduce spectral leakage
    data = strain * tukey(len(strain), alpha=0.1)
    
    # ASD estimate using Welch
    f, psd = welch(data, fs=fs, nperseg=int(fs)) # 1s segments
    
    # Robust PSD floor: Max of (percentile-5, 1e-30) to avoid zero-division
    psd_floor = max(np.percentile(psd, 5), 1e-30)
    psd = np.maximum(psd, psd_floor)
    
    # Interpolate to FFT frequencies
    psd_interp = np.interp(np.fft.rfftfreq(len(data), 1/fs), f, psd)
    
    # FFT and Divide by ASD (sqrt(PSD)) with epsilon
    hf = np.fft.rfft(data)
    white_hf = hf / (np.sqrt(psd_interp) + 1e-20)
    
    # Bandpass within whitening (30Hz to 1500Hz)
    freqs = np.fft.rfftfreq(len(data), 1/fs)
    white_hf[(freqs < 30) | (freqs > 1500)] = 0
    
    white_strain = np.fft.irfft(white_hf, n=len(data))
    
    # Standardize to unit variance (if not zero)
    std = np.std(white_strain)
    if std > 0:
        white_strain /= std
    return white_strain

def find_h1_l1_lag(h1, l1, fs, peak_idx):
    """
    Finds the H1-L1 time lag by maximizing cross-correlation around the merger.
    Limit lag to +/- 10ms (light travel time).
    """
    win = int(0.05 * fs) # 50ms window
    h1_seg = h1[peak_idx - win : peak_idx + win]
    l1_seg = l1[peak_idx - win : peak_idx + win]
    
    corr = np.correlate(h1_seg, l1_seg, mode='same')
    lags = np.arange(-win, win)
    
    # Restrict to +/- 10ms
    max_lag_samples = int(0.010 * fs)
    mask = (lags >= -max_lag_samples) & (lags <= max_lag_samples)
    
    best_lag_samples = lags[mask][np.argmax(np.abs(corr[mask]))]
    return best_lag_samples

def get_windowed_stat(h1, l1, lag_samples, fs, target_idx, window_ms=20):
    """
    Computes coincidence power maximized over a small window around the target.
    """
    win_samples = int((window_ms / 1000.0) * fs)
    half_win = win_samples // 2
    
    # H1 index is target_idx
    # L1 index is target_idx + lag_samples
    h1_slice = h1[target_idx - half_win : target_idx + half_win]
    l1_slice = l1[target_idx + lag_samples - half_win : target_idx + lag_samples + half_win]
    
    # We use the product of envelopes (Hilbert transform magnitude) or just local max
    return np.max(np.abs(h1_slice) * np.abs(l1_slice))

def run_physics_grade_sweep():
    results = []
    lp = 1.616e-35
    G = 6.674e-11
    M_sun = 1.989e30
    c = 299792458.0
    N_SLIDES = 200 # Number of time slides for background

    print(f"Starting Physics-Grade Sweep for {len(EVENTS)} events...")

    for event in EVENTS:
        name = event["name"]
        gps = event["gps"]
        mass = event["mass"]
        print(f"\n--- Event: {name} (M={mass} M_sol) ---")
        
        h1_url, l1_url = get_gwosc_urls_robust(name)
        if not h1_url or not l1_url:
            print("  Skipping: URLs not resolved.")
            continue
            
        h1_file = download_file(h1_url, f"{name}_H1.hdf5")
        l1_file = download_file(l1_url, f"{name}_L1.hdf5")
        if not h1_file or not l1_file: continue

        with h5py.File(h1_file, 'r') as f:
            h1_raw = f['strain']['Strain'][:]
            fs = 1.0 / f['strain']['Strain'].attrs['Xspacing']
            start_gps = f['meta']['GPSstart'][()]
        with h5py.File(l1_file, 'r') as f:
            l1_raw = f['strain']['Strain'][:]

        # Preprocessing
        h1_white = whiten_data(h1_raw, fs)
        l1_white = whiten_data(l1_raw, fs)
        
        peak_idx = int((gps - start_gps) * fs)
        lag_samples = find_h1_l1_lag(h1_white, l1_white, fs, peak_idx)
        print(f"  H1-L1 Lag: {lag_samples / fs * 1000:.2f} ms")

        # Predicted Delay
        M_kg = mass * M_sun
        rs = 2 * G * M_kg / (c**2)
        phi_min = lp / rs
        delta_t = (4.0 * G * M_kg / (c**3)) * np.abs(np.log(phi_min))
        echo_idx = peak_idx + int(delta_t * fs)
        
        if echo_idx >= len(h1_white) - int(0.1*fs):
            print("  Echo out of bounds.")
            continue

        # On-source score
        on_source_score = get_windowed_stat(h1_white, l1_white, lag_samples, fs, echo_idx)

        # Background via Time Slides
        # Shift L1 relative to H1 by multiple seconds
        bg_scores = []
        for i in range(N_SLIDES):
            # Shift by [2s, 10s]
            shift_samples = int((2.0 + (8.0 * i / N_SLIDES)) * fs)
            # Circular shift L1
            l1_shifted = np.roll(l1_white, shift_samples)
            bg_score = get_windowed_stat(h1_white, l1_shifted, lag_samples, fs, echo_idx)
            bg_scores.append(bg_score)
            
        p_value = (np.sum(np.array(bg_scores) >= on_source_score) + 1) / (N_SLIDES + 1)
        
        print(f"  Delay: {delta_t:.4f} s | Score: {on_source_score:.4f} | P-value: {p_value:.4f}")
        
        results.append({
            "event": name, "mass": mass, "delta_t": delta_t,
            "score": on_source_score, "p_value": p_value
        })

    # Save and Plot
    df = pd.DataFrame(results)
    # Bonferroni Correction
    df['p_corr'] = np.minimum(df['p_value'] * len(df), 1.0)
    df.to_csv("omega_physics_sweep_v2.csv", index=False)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(df["mass"], -np.log10(df["p_value"]), color='blue', label='Uncorrected p')
    plt.scatter(df["mass"], -np.log10(df["p_corr"]), color='orange', marker='x', label='Bonferroni p')
    plt.axhline(-np.log10(0.05), color='r', linestyle='--', label='p=0.05')
    plt.xlabel("Remnant Mass ($M_{sol}$)")
    plt.ylabel("-log10(p-value)")
    plt.title("Omega Protocol Echo Sweep v2 (Physics Grade)")
    plt.legend()
    plt.savefig("omega_sweep_v2_significance.png")
    print("\nSweep Complete. Significance plot saved.")

if __name__ == "__main__":
    run_physics_grade_sweep()
