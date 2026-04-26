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
import json

# ==========================================
# SEARCH PROTOCOL v1.0 (FROZEN)
# ==========================================
PROTOCOL = {
    "bandpass": [30, 1500],
    "tukey_alpha": 0.1,
    "window_ms": 20,
    "n_slides": 200,
    "phi_min_scaling": "lp/rs",
    "injection_amplitudes": [0.1, 0.3, 0.5]
}

EVENTS = [
    # GWTC-1
    {"name": "GW150914", "gps": 1126259462.4, "mass": 62.0},
    {"name": "GW151012", "gps": 1128678900.4, "mass": 35.0},
    {"name": "GW170608", "gps": 1180922494.5, "mass": 18.0},
    {"name": "GW170814", "gps": 1186741861.5, "mass": 53.0},
    {"name": "GW170823", "gps": 1187529256.5, "mass": 78.0},
    # GWTC-2.1 (Representative)
    {"name": "GW190521", "gps": 1242442967.4, "mass": 142.0},
    {"name": "GW190412", "gps": 1239082262.2, "mass": 37.0},
    {"name": "GW190814", "gps": 1249852257.0, "mass": 25.0}
]

def get_gwosc_urls_robust(event_name):
    # Try different catalog endpoints
    catalogs = ["GWTC-1-confident", "GWTC-2.1-confident", "GWTC-3-confident"]
    for cat in catalogs:
        api_url = f"https://gwosc.org/eventapi/json/{cat}/{event_name}/"
        try:
            r = requests.get(api_url, timeout=10)
            if r.status_code != 200: continue
            data = r.json()
            event_key = list(data['events'].keys())[0]
            strain_data = data['events'][event_key]['strain']
            h1_url, l1_url = None, None
            for entry in strain_data:
                if entry['format'] == 'hdf5' and entry['sampling_rate'] == 4096:
                    if entry['detector'] == 'H1': h1_url = entry['url']
                    elif entry['detector'] == 'L1': l1_url = entry['url']
            if h1_url and l1_url: return h1_url, l1_url
        except: continue
    return None, None

def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        print(f"  Downloading {url}...")
        try:
            r = requests.get(url, allow_redirects=True, timeout=60)
            if r.status_code == 200:
                with open(local_filename, 'wb') as f: f.write(r.content)
            else: return None
        except: return None
    return local_filename

def whiten_data(strain, fs):
    data = strain * tukey(len(strain), alpha=PROTOCOL["tukey_alpha"])
    f, psd = welch(data, fs=fs, nperseg=int(fs))
    psd_floor = max(np.percentile(psd, 5), 1e-30)
    psd = np.maximum(psd, psd_floor)
    psd_interp = np.interp(np.fft.rfftfreq(len(data), 1/fs), f, psd)
    hf = np.fft.rfft(data)
    white_hf = hf / (np.sqrt(psd_interp) + 1e-20)
    freqs = np.fft.rfftfreq(len(data), 1/fs)
    white_hf[(freqs < PROTOCOL["bandpass"][0]) | (freqs > PROTOCOL["bandpass"][1])] = 0
    white_strain = np.fft.irfft(white_hf, n=len(data))
    std = np.std(white_strain)
    if std > 0: white_strain /= std
    return white_strain

def find_h1_l1_lag(h1, l1, fs, peak_idx):
    win = int(0.05 * fs)
    h1_seg = h1[peak_idx - win : peak_idx + win]
    l1_seg = l1[peak_idx - win : peak_idx + win]
    corr = np.correlate(h1_seg, l1_seg, mode='same')
    lags = np.arange(-win, win)
    max_lag_samples = int(0.010 * fs)
    mask = (lags >= -max_lag_samples) & (lags <= max_lag_samples)
    return lags[mask][np.argmax(np.abs(corr[mask]))]

def get_windowed_stat(h1, l1, lag_samples, fs, target_idx):
    win_samples = int((PROTOCOL["window_ms"] / 1000.0) * fs)
    half_win = win_samples // 2
    h1_slice = h1[target_idx - half_win : target_idx + half_win]
    l1_slice = l1[target_idx + lag_samples - half_win : target_idx + lag_samples + half_win]
    if len(h1_slice) == 0 or len(l1_slice) == 0: return 0
    return np.max(np.abs(h1_slice) * np.abs(l1_slice))

def run_production_sweep():
    results = []
    lp, G, M_sun, c = 1.616e-35, 6.674e-11, 1.989e30, 299792458.0
    
    print(f"=== OMEGA GLOBAL SWEEP v1.0 ===")
    
    for event in EVENTS:
        name = event["name"]
        gps, mass = event["gps"], event["mass"]
        print(f"\n[Processing {name}]")
        
        h1_url, l1_url = get_gwosc_urls_robust(name)
        if not h1_url:
            print("  URLs not resolved.")
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

        h1_white = whiten_data(h1_raw, fs)
        l1_white = whiten_data(l1_raw, fs)
        peak_idx = int((gps - start_gps) * fs)
        lag_samples = find_h1_l1_lag(h1_white, l1_white, fs, peak_idx)

        # Delta_t Prediction
        M_kg = mass * M_sun
        rs = 2 * G * M_kg / (c**2)
        phi_min = lp / rs
        delta_t = (4.0 * G * M_kg / (c**3)) * np.abs(np.log(phi_min))
        echo_idx = peak_idx + int(delta_t * fs)
        
        if echo_idx >= len(h1_white) - int(0.1*fs):
            print("  Echo out of bounds.")
            continue

        # 1. On-source
        on_source = get_windowed_stat(h1_white, l1_white, lag_samples, fs, echo_idx)

        # 2. Background
        bg_scores = []
        for i in range(PROTOCOL["n_slides"]):
            shift = int((2.0 + (8.0 * i / PROTOCOL["n_slides"])) * fs)
            bg_score = get_windowed_stat(h1_white, np.roll(l1_white, shift), lag_samples, fs, echo_idx)
            bg_scores.append(bg_score)
        p_val = (np.sum(np.array(bg_scores) >= on_source) + 1) / (len(bg_scores) + 1)

        # 3. Injection Sensitivity (0.3 Amplitude)
        # Template is 0.1s around peak
        t_len = int(0.1 * fs)
        template = h1_white[peak_idx - t_len//2 : peak_idx + t_len//2]
        h1_inj = h1_white.copy()
        # Inject at echo_idx
        h1_inj[echo_idx - t_len//2 : echo_idx + t_len//2] += 0.3 * template
        inj_score = get_windowed_stat(h1_inj, l1_white, lag_samples, fs, echo_idx)
        recovered = inj_score > np.percentile(bg_scores, 95)

        print(f"  dt={delta_t:.3f}s | p={p_val:.4f} | Recov(0.3)={recovered}")
        
        results.append({
            "event": name, "mass": mass, "delta_t": delta_t,
            "p_value": p_val, "recovered_0.3": recovered
        })

    df = pd.DataFrame(results)
    df['p_corr'] = np.minimum(df['p_value'] * len(df), 1.0)
    df.to_csv("omega_global_sweep_results.csv", index=False)
    
    # Hierarchical P-value (Fisher's Method)
    valid_p = df['p_value'].values
    fisher_stat = -2 * np.sum(np.log(valid_p))
    from scipy.stats import chi2
    global_p = 1 - chi2.cdf(fisher_stat, df=2*len(valid_p))
    
    print(f"\nGLOBAL P-VALUE (Fisher): {global_p:.4e}")
    with open("omega_sweep_summary.json", "w") as f:
        json.dump({"global_p": global_p, "n_events": len(df)}, f)

if __name__ == "__main__":
    run_production_sweep()
