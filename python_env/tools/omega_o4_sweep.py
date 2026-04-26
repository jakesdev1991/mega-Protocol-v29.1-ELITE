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
from scipy.stats import chi2

# ==========================================
# O4 ROBUSTNESS PROTOCOL (V1.2)
# ==========================================
PROTOCOL = {
    "bandpass": [30, 1500],
    "tukey_alpha": 0.1,
    "window_ms": 20,
    "n_slides": 10000, 
    "phi_min_scaling": "lp/rs",
    "control_test": False, # Set to True for sanity checks
    "control_type": "off_source" # "off_source", "wrong_delay", "mass_shuffle"
}

# Selected High-Mass O4 BBH Events from GWOSC O4a
O4_EVENTS = [
    {"name": "GW230704_212616", "gps": 1372541194.7, "mass_1": 89.0, "mass_2": 49.0},
    {"name": "GW230922_040658", "gps": 1379390836.0, "mass_1": 76.0, "mass_2": 51.0},
    {"name": "GW230601_224134", "gps": 1369694512.1, "mass_1": 64.0, "mass_2": 44.0},
    {"name": "GW230708_230935", "gps": 1372892993.5, "mass_1": 64.0, "mass_2": 39.0},
    {"name": "GW230814_061920", "gps": 1376029178.5, "mass_1": 69.0, "mass_2": 42.0},
    {"name": "GW230914_111401", "gps": 1378725259.7, "mass_1": 59.0, "mass_2": 36.0},
    {"name": "GW230819_171910", "gps": 1376500768.4, "mass_1": 70.0, "mass_2": 35.0},
    {"name": "GW230824_033047", "gps": 1376883065.7, "mass_1": 53.0, "mass_2": 36.0},
]

def shift_noncircular(x, shift):
    """Rigorous non-circular shift using NaN padding."""
    y = np.full_like(x, np.nan)
    if shift > 0:
        if shift < len(x):
            y[shift:] = x[:-shift]
    elif shift < 0:
        abs_shift = abs(shift)
        if abs_shift < len(x):
            y[:shift] = x[abs_shift:]
    else:
        y[:] = x
    return y

def get_gwosc_urls_o4(event_name):
    api_url = f"https://gwosc.org/eventapi/json/GWTC-4.0/{event_name}/v1"
    try:
        r = requests.get(api_url, timeout=10)
        if r.status_code != 200: return None, None
        data = r.json()
        event_key = list(data['events'].keys())[0]
        strain_data = data['events'][event_key]['strain']
        h1_url, l1_url = None, None
        for entry in strain_data:
            if entry['format'] == 'hdf5' and entry['sampling_rate'] == 4096:
                if entry['detector'] == 'H1': h1_url = entry['url']
                elif entry['detector'] == 'L1': l1_url = entry['url']
        return h1_url, l1_url
    except: return None, None

def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        print(f"  Downloading {url}...")
        try:
            r = requests.get(url, allow_redirects=True, timeout=120)
            if r.status_code == 200:
                with open(local_filename, 'wb') as f: f.write(r.content)
            else: return None
        except: return None
    return local_filename

def whiten_data(strain, fs):
    """Refined whitening with NaN protection and PSD floor."""
    data = strain * tukey(len(strain), alpha=PROTOCOL["tukey_alpha"])
    f, psd = welch(data, fs=fs, nperseg=int(fs))
    psd_floor = max(np.percentile(psd, 5), 1e-45)
    psd = np.maximum(psd, psd_floor)
    psd_interp = np.interp(np.fft.rfftfreq(len(data), 1/fs), f, psd)
    hf = np.fft.rfft(data)
    # Protection against zero/NaN in PSD
    denom = np.sqrt(psd_interp) + 1e-30
    white_hf = hf / denom
    freqs = np.fft.rfftfreq(len(data), 1/fs)
    white_hf[(freqs < PROTOCOL["bandpass"][0]) | (freqs > PROTOCOL["bandpass"][1])] = 0
    white_strain = np.fft.irfft(white_hf, n=len(data))
    std = np.std(white_strain)
    if std > 0: white_strain /= std
    return white_strain

def find_h1_l1_lag(h1, l1, fs, peak_idx):
    win = int(0.1 * fs)
    h1_seg = h1[peak_idx - win : peak_idx + win]
    l1_seg = l1[peak_idx - win : peak_idx + win]
    # Handle NaNs in correlation if any
    h1_seg = np.nan_to_num(h1_seg)
    l1_seg = np.nan_to_num(l1_seg)
    corr = np.correlate(h1_seg, l1_seg, mode='same')
    lags = np.arange(-win, win)
    max_lag_samples = int(0.015 * fs)
    mask = (lags >= -max_lag_samples) & (lags <= max_lag_samples)
    return lags[mask][np.argmax(np.abs(corr[mask]))]

def get_windowed_stat(h1, l1, lag_samples, fs, target_idx):
    win_samples = int((PROTOCOL["window_ms"] / 1000.0) * fs)
    half_win = win_samples // 2
    idx1, idx2 = target_idx, target_idx + lag_samples
    if idx1 < half_win or idx1 >= len(h1) - half_win or \
       idx2 < half_win or idx2 >= len(l1) - half_win: return 0
    h1_slice = h1[idx1 - half_win : idx1 + half_win]
    l1_slice = l1[idx2 - half_win : idx2 + half_win]
    if np.any(np.isnan(h1_slice)) or np.any(np.isnan(l1_slice)): return 0
    return np.max(np.abs(h1_slice) * np.abs(l1_slice))

def run_o4_robustness():
    results = []
    all_bg_scores, all_on_scores = [], []
    lp, G, M_sun, c = 1.616e-35, 6.674e-11, 1.989e30, 299792458.0
    
    print(f"=== OMEGA O4 ROBUSTNESS SWEEP (N={PROTOCOL['n_slides']}) ===")
    
    events_to_process = O4_EVENTS.copy()
    if PROTOCOL["control_test"] and PROTOCOL["control_type"] == "mass_shuffle":
        masses = [e["mass_1"] + e["mass_2"] for e in events_to_process]
        np.random.shuffle(masses)
        for i, e in enumerate(events_to_process):
            e["mass_total"] = masses[i]
    else:
        for e in events_to_process:
            e["mass_total"] = e["mass_1"] + e["mass_2"]

    for event in events_to_process:
        name = event["name"]
        gps = event["gps"]
        mass = event["mass_total"]
        print(f"\n[Event: {name}]")
        
        h1_url, l1_url = get_gwosc_urls_o4(name)
        if not h1_url: continue
            
        h1_file = download_file(h1_url, f"{name}_H1.hdf5")
        l1_file = download_file(l1_url, f"{name}_L1.hdf5")
        if not h1_file or not l1_file: continue

        try:
            with h5py.File(h1_file, 'r') as f:
                h1_raw = f['strain']['Strain'][:]
                fs = 1.0 / f['strain']['Strain'].attrs['Xspacing']
                start_gps = f['meta']['GPSstart'][()]
            with h5py.File(l1_file, 'r') as f:
                l1_raw = f['strain']['Strain'][:]
        except Exception as e:
            print(f"  Error: {e}")
            continue

        h1_white = whiten_data(h1_raw, fs)
        l1_white = whiten_data(l1_raw, fs)
        peak_idx = int((gps - start_gps) * fs)
        lag_samples = find_h1_l1_lag(h1_white, l1_white, fs, peak_idx)

        # Delta_t Prediction
        M_kg = mass * M_sun
        rs = 2 * G * M_kg / (c**2)
        phi_min = lp / rs
        delta_t = (4.0 * G * M_kg / (c**3)) * np.abs(np.log(phi_min))
        
        if PROTOCOL["control_test"]:
            if PROTOCOL["control_type"] == "wrong_delay":
                delta_t += 0.5 # Add 500ms error
            elif PROTOCOL["control_type"] == "off_source":
                delta_t -= 1.0 # Evaluate 1s before peak

        echo_idx = peak_idx + int(delta_t * fs)
        on_score = get_windowed_stat(h1_white, l1_white, lag_samples, fs, echo_idx)
        all_on_scores.append(on_score)

        bg_scores = []
        for i in range(PROTOCOL["n_slides"]):
            # Non-circular shifts: range from 5s to 15s
            shift = int((5.0 + (10.0 * i / PROTOCOL["n_slides"])) * fs)
            l1_shifted = shift_noncircular(l1_white, shift)
            bg_score = get_windowed_stat(h1_white, l1_shifted, lag_samples, fs, echo_idx)
            bg_scores.append(bg_score)
        
        bg_scores = np.array(bg_scores)
        all_bg_scores.append(bg_scores)
        p_val = (np.sum(bg_scores >= on_score) + 1) / (len(bg_scores) + 1)

        print(f"  dt={delta_t:.3f}s | p<={p_val:.4e} | mass={mass}")
        results.append({"event": name, "p_value": p_val, "mass": mass})

    if not all_on_scores: return

    all_bg_scores = np.array(all_bg_scores)
    all_on_scores = np.array(all_on_scores)
    epsilon = 1e-15
    on_meta = np.sum(np.log(all_on_scores + epsilon))
    bg_metas = np.sum(np.log(all_bg_scores + epsilon), axis=0)
    global_p = (np.sum(bg_metas >= on_meta) + 1) / (PROTOCOL["n_slides"] + 1)
    
    suffix = f"_{PROTOCOL['control_type']}" if PROTOCOL["control_test"] else "_baseline"
    print(f"\nGLOBAL EMPIRICAL P-VALUE ({PROTOCOL['control_type'] if PROTOCOL['control_test'] else 'baseline'}): {global_p:.4e}")
    pd.DataFrame(results).to_csv(f"omega_o4_robustness_results{suffix}.csv", index=False)
    with open(f"omega_o4_robustness_summary{suffix}.json", "w") as f:
        json.dump({"global_p": global_p, "n_events": len(results), "n_slides": PROTOCOL["n_slides"], "type": PROTOCOL["control_type"] if PROTOCOL["control_test"] else "baseline"}, f)

if __name__ == "__main__":
    run_o4_robustness()
