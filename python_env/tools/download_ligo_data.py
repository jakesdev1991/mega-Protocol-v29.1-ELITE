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
import os

def download_gw150914_data():
    # GW150914 Hanford 4KHz HDF5 URL from GWOSC
    url = "https://gwosc.org/eventapi/html/GWTC-1-confident/GW150914/v3/H-H1_GWOSC_4KHZ_R1-1126259447-32.hdf5"
    local_filename = "H-H1_GWOSC_4KHZ_R1-1126259447-32.hdf5"
    
    if not os.path.exists(local_filename):
        print(f"Downloading {url}...")
        r = requests.get(url, allow_redirects=True)
        with open(local_filename, 'wb') as f:
            f.write(r.content)
        print("Download complete.")
    else:
        print("File already exists.")
    return local_filename

def process_ligo_data(filename):
    with h5py.File(filename, 'r') as f:
        # Explore structure
        strain = f['strain']['Strain'][:]
        ts = f['strain']['Strain'].attrs['Xspacing']
        meta = f['meta']
        gps_start = f['meta']['GPSstart'][()]
        
        duration = len(strain) * ts
        time = np.arange(0, duration, ts)
        
        print(f"GPS Start: {gps_start}")
        print(f"Sampling Rate: {1/ts} Hz")
        print(f"Number of samples: {len(strain)}")
        
        # Plot raw data
        plt.figure(figsize=(12, 6))
        plt.plot(time, strain)
        plt.title("GW150914 Raw Strain (H1)")
        plt.xlabel("Time (s) from GPS Start")
        plt.ylabel("Strain")
        plt.grid(True)
        plt.savefig("gw150914_raw.png")
        print("Saved gw150914_raw.png")
        
        return strain, ts

if __name__ == "__main__":
    fname = download_gw150914_data()
    process_ligo_data(fname)
