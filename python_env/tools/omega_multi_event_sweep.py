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

def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        print(f"Downloading {url}...")
        try:
            r = requests.get(url, allow_redirects=True, timeout=30)
            if r.status_code == 200:
                with open(local_filename, 'wb') as f:
                    f.write(r.content)
            else:
                print(f"Failed to download {url}: Status {r.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None
    return local_filename

def get_gwosc_urls(event_name):
    # Construct standard GWTC-1 HDF5 URLs (V3)
    # This is a heuristic mapping; in a production script, we'd use the gwosc API
    # but since we can't install igwn-segments, we use direct URLs.
    base = "https://gwosc.org/eventapi/html/GWTC-1-confident"
    
    # Mapping for common events
    urls = {
        "GW150914": (f"{base}/GW150914/v3/H-H1_GWOSC_4KHZ_R1-1126259447-32.hdf5",
                     f"{base}/GW150914/v3/L-L1_GWOSC_4KHZ_R1-1126259447-32.hdf5"),
        "GW151012": (f"{base}/GW151012/v3/H-H1_GWOSC_4KHZ_R1-1128678885-32.hdf5",
                     f"{base}/GW151012/v3/L-L1_GWOSC_4KHZ_R1-1128678885-32.hdf5"),
        "GW151226": (f"{base}/GW151226/v3/H-H1_GWOSC_4KHZ_R1-1135136335-32.hdf5",
                     f"{base}/GW151226/v3/L-L1_GWOSC_4KHZ_R1-1135136335-32.hdf5"),
        "GW170104": (f"{base}/GW170104/v3/H-H1_GWOSC_4KHZ_R1-1167559921-32.hdf5",
                     f"{base}/GW170104/v3/L-L1_GWOSC_4KHZ_R1-1167559921-32.hdf5"),
        "GW170608": (f"{base}/GW170608/v3/H-H1_GWOSC_4KHZ_R1-1180922479-32.hdf5",
                     f"{base}/GW170608/v3/L-L1_GWOSC_4KHZ_R1-1180922479-32.hdf5"),
        "GW170814": (f"{base}/GW170814/v3/H-H1_GWOSC_4KHZ_R1-1186741846-32.hdf5",
                     f"{base}/GW170814/v3/L-L1_GWOSC_4KHZ_R1-1186741846-32.hdf5"),
        "GW170823": (f"{base}/GW170823/v3/H-H1_GWOSC_4KHZ_R1-1187529241-32.hdf5",
                     f"{base}/GW170823/v3/L-L1_GWOSC_4KHZ_R1-1187529241-32.hdf5"),
    }
    return urls.get(event_name)

def physics_grade_whitening(strain, fs):
    """
    Standard whitening:
    1. Tukey window
    2. ASD estimate (off-source)
    3. Frequency domain division
    """
    # 1. Apply Tukey window to reduce spectral leakage
    data = strain * tukey(len(strain), alpha=0.1)
    
    # 2. ASD estimate using Welch
    # We use the middle 16 seconds to estimate the PSD, but usually the whole segment is used
    f, psd = welch(data, fs=fs, nperseg=int(fs)) # 1s segments
    
    # Floor the PSD to avoid noise-floor blowup
    psd_floor = np.percentile(psd, 5)
    psd = np.maximum(psd, psd_floor)
    
    # Interpolate to FFT frequencies
    psd_interp = np.interp(np.fft.rfftfreq(len(data), 1/fs), f, psd)
    
    # 3. FFT and Divide by ASD (sqrt(PSD))
    hf = np.fft.rfft(data)
    white_hf = hf / np.sqrt(psd_interp)
    
    # Bandpass within whitening (30Hz to 1500Hz)
    freqs = np.fft.rfftfreq(len(data), 1/fs)
    white_hf[(freqs < 30) | (freqs > 1500)] = 0
    
    white_strain = np.fft.irfft(white_hf, n=len(data))
    
    # Normalize to unit variance
    white_strain /= np.std(white_strain)
    return white_strain

def calculate_coincidence_stat(h1_proc, l1_proc, fs, peak_idx):
    # Template: 0.1s around peak
    tmpl_len = int(0.1 * fs)
    template = h1_proc[peak_idx - tmpl_len//2 : peak_idx + tmpl_len//2]
    
    h1_corr = np.correlate(h1_proc, template, mode='same')
    l1_corr = np.correlate(l1_proc, template, mode='same')
    
    # Coincidence correlation power
    stat = np.abs(h1_corr) * np.abs(l1_corr)
    return stat

def run_multi_event_sweep():
    results = []
    lp = 1.616e-35
    G = 6.674e-11
    M_sun = 1.989e30
    c = 299792458.0

    print(f"Starting Multi-Event Sweep for {len(EVENTS)} events...")

    for event in EVENTS:
        name = event["name"]
        gps = event["gps"]
        mass = event["mass"]
        
        print(f"\nProcessing {name} (M={mass} M_sol)...")
        
        urls = get_gwosc_urls(name)
        if not urls:
            print(f"Skipping {name}: URLs not found.")
            continue
            
        h1_file = download_file(urls[0], f"{name}_H1.hdf5")
        l1_file = download_file(urls[1], f"{name}_L1.hdf5")
        
        if not h1_file or not l1_file:
            continue

        try:
            with h5py.File(h1_file, 'r') as f:
                h1_raw = f['strain']['Strain'][:]
                fs = 1.0 / f['strain']['Strain'].attrs['Xspacing']
                start_gps = f['meta']['GPSstart'][()]
            with h5py.File(l1_file, 'r') as f:
                l1_raw = f['strain']['Strain'][:]
        except Exception as e:
            print(f"Error reading HDF5 for {name}: {e}")
            continue

        # Predicted Delay
        M_kg = mass * M_sun
        rs = 2 * G * M_kg / (c**2)
        phi_min = lp / rs
        delta_t = (4.0 * G * M_kg / (c**3)) * np.abs(np.log(phi_min))
        
        # Preprocessing
        h1_white = physics_grade_whitening(h1_raw, fs)
        l1_white = physics_grade_whitening(l1_raw, fs)
        
        peak_idx = int((gps - start_gps) * fs)
        stat = calculate_coincidence_stat(h1_white, l1_white, fs, peak_idx)
        
        # On-source score
        echo_idx = peak_idx + int(delta_t * fs)
        if echo_idx >= len(stat):
            print(f"Echo index {echo_idx} out of bounds for {name}")
            continue
            
        on_source_score = stat[echo_idx]
        
        # Background: 1000 random shifts in [peak+0.5s, end-0.5s]
        bg_start = peak_idx + int(0.5 * fs)
        bg_end = len(stat) - int(0.5 * fs)
        
        if bg_end <= bg_start:
            print(f"Background window too small for {name}")
            continue
            
        bg_indices = np.random.randint(bg_start, bg_end, 1000)
        # Exclude the predicted echo window (±0.1s)
        echo_window = int(0.1 * fs)
        bg_indices = [idx for idx in bg_indices if abs(idx - echo_idx) > echo_window]
        
        bg_scores = stat[bg_indices]
        p_value = (np.sum(bg_scores >= on_source_score) + 1) / (len(bg_scores) + 1)
        
        print(f"  Predicted Delay: {delta_t:.4f} s")
        print(f"  On-source Score: {on_source_score:.4f}")
        print(f"  P-value: {p_value:.4f}")
        
        results.append({
            "event": name,
            "mass": mass,
            "delta_t": delta_t,
            "score": on_source_score,
            "p_value": p_value
        })

    # Save results
    df = pd.DataFrame(results)
    df.to_csv("omega_sweep_results.csv", index=False)
    print("\nSweep Complete. Results saved to omega_sweep_results.csv")
    
    # Summary plot
    plt.figure(figsize=(10, 6))
    plt.scatter(df["mass"], -np.log10(df["p_value"]), color='blue', s=100)
    for i, row in df.iterrows():
        plt.annotate(row["event"], (row["mass"], -np.log10(row["p_value"])))
    plt.axhline(-np.log10(0.05), color='r', linestyle='--', label='p=0.05')
    plt.xlabel("Remnant Mass ($M_{sol}$)")
    plt.ylabel("-log10(p-value)")
    plt.title("Omega Protocol Echo Sweep: Significance vs Mass")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("omega_sweep_significance.png")

if __name__ == "__main__":
    run_multi_event_sweep()
