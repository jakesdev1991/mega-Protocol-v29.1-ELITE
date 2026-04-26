# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import torch

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

def run_finance_validation():
    print("📈 [Finance Branch] Initializing RCOD Bitcoin Market Analysis...")
    
    # Raw data extracted from the docx table (Dec 2023 - Jan 2026)
    # We'll use the 'Close' prices provided in the prompt output
    # Format: Date|Open|High|Low|Close|Adj Close|Volume
    raw_data = """
Jan 12, 2026|91,765.92
Jan 11, 2026|90,827.46
Jan 10, 2026|90,386.65
Jan 9, 2026|90,513.10
Jan 8, 2026|91,027.13
Jan 7, 2026|91,308.05
Jan 6, 2026|93,729.03
Jan 5, 2026|93,882.55
Jan 4, 2026|91,413.49
Jan 3, 2026|90,603.19
Jan 2, 2026|89,944.70
Jan 1, 2026|88,731.98
Dec 31, 2025|87,508.83
Dec 30, 2025|88,430.13
Dec 29, 2025|87,138.14
Dec 28, 2025|87,835.84
Dec 27, 2025|87,802.16
Dec 26, 2025|87,301.43
Dec 25, 2025|87,234.74
Dec 24, 2025|87,611.96
Dec 23, 2025|87,414.00
Dec 22, 2025|88,490.02
Dec 21, 2025|88,621.75
Dec 20, 2025|88,344.00
Dec 19, 2025|88,103.38
Dec 18, 2025|85,462.51
Dec 17, 2025|86,143.76
Dec 16, 2025|87,843.98
Dec 15, 2025|86,419.78
Dec 14, 2025|88,175.18
Dec 13, 2025|90,298.71
Dec 12, 2025|90,270.41
Dec 11, 2025|92,511.34
Dec 10, 2025|92,020.95
Dec 9, 2025|92,691.71
Dec 8, 2025|90,640.20
Dec 7, 2025|90,405.64
Dec 6, 2025|89,272.38
Dec 5, 2025|89,387.76
Dec 4, 2025|92,141.63
Dec 3, 2025|93,527.80
Dec 2, 2025|91,350.20
Dec 1, 2025|86,321.57
Nov 30, 2025|90,394.31
Nov 29, 2025|90,851.76
Nov 28, 2025|90,919.27
Nov 27, 2025|91,285.38
Nov 26, 2025|90,518.37
Nov 25, 2025|87,341.89
Nov 24, 2025|88,270.56
Nov 23, 2025|86,805.01
Nov 22, 2025|84,648.36
Nov 21, 2025|85,090.69
Nov 20, 2025|86,631.90
Nov 19, 2025|91,465.99
Nov 18, 2025|92,948.88
Nov 17, 2025|92,093.88
Nov 16, 2025|94,177.08
Nov 15, 2025|95,549.15
Nov 14, 2025|94,397.79
Nov 13, 2025|99,697.49
Nov 12, 2025|101,663.19
Nov 11, 2025|102,997.47
Nov 10, 2025|105,996.59
Nov 9, 2025|104,719.64
Nov 8, 2025|102,282.12
Nov 7, 2025|103,372.41
Nov 6, 2025|101,301.29
Nov 5, 2025|103,891.84
Nov 4, 2025|101,590.52
Nov 3, 2025|106,547.52
Nov 2, 2025|110,639.63
Nov 1, 2025|110,064.02
Oct 31, 2025|109,556.16
Oct 30, 2025|108,305.55
Oct 29, 2025|110,055.30
Oct 28, 2025|112,956.16
Oct 27, 2025|114,119.33
Oct 26, 2025|114,472.45
Oct 25, 2025|111,641.73
Oct 24, 2025|111,033.92
Oct 23, 2025|110,069.73
Oct 22, 2025|107,688.59
Oct 21, 2025|108,476.89
Oct 20, 2025|110,588.93
Oct 19, 2025|108,666.71
Oct 18, 2025|107,198.27
Oct 17, 2025|106,467.79
Oct 16, 2025|108,186.04
Oct 15, 2025|110,783.16
Oct 14, 2025|113,118.66
Oct 13, 2025|115,271.08
Oct 12, 2025|115,169.77
Oct 11, 2025|110,807.88
Oct 10, 2025|113,214.37
Oct 9, 2025|121,705.59
Oct 8, 2025|123,354.87
Oct 7, 2025|121,451.38
Oct 6, 2025|124,752.53
Oct 5, 2025|123,513.48
    """
    
    # Parse lines (reversed to keep chronological order)
    lines = [l for l in raw_data.strip().split("\n") if l][::-1]
    prices = [float(l.split("|")[1].replace(",", "")) for l in lines]
    dates = [l.split("|")[0] for l in lines]
    
    print(f"Loaded {len(prices)} data points.")
    
    # 2. RCOD Market Monitoring
    monitor = RCODMonitor()
    phi_n_values = []
    phi_delta_values = []
    
    # We use a 10-day window for local market geometry
    window_size = 10
    
    for i in range(len(prices)):
        if i < window_size:
            phi_n_values.append(1.0) # Equilibrium
            phi_delta_values.append(0.0)
            continue
            
        # Extract window and normalize (relative price movement)
        window = np.array(prices[i-window_size:i])
        norm_window = (window - np.mean(window)) / (np.std(window) + 1e-6)
        
        # Monitor Step
        window_tensor = torch.from_numpy(norm_window).float().unsqueeze(0)
        v = layer_stat(window_tensor)
        phi_n, phi_delta = monitor.step(v, layer_id="btc_market")
        
        phi_n_values.append(phi_n)
        phi_delta_values.append(phi_delta)
        
        if phi_delta > 0.6:
            print(f"⚠️ [MARKET SHOCK] Potential Volatility Spike detected on {dates[i]} (Phi_Delta: {phi_delta:.4f})")

    # 3. Visualization
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(prices, label="BTC Price (USD)", color='gold', lw=2)
    plt.title("Bitcoin Price History (v29.1 Market Analysis)")
    plt.ylabel("Price")
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(phi_delta_values, label="Phi_Delta (Archive Mode / Shock)", color='red')
    plt.axhline(y=0.6, color='orange', linestyle='--', label="Market Instability Threshold")
    plt.ylabel("Asymmetry Score")
    plt.xlabel("Days")
    plt.title("Omega Protocol: Informational Market Fracture Detection")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_plot = "finance/btc_rcod_analysis.png"
    plt.savefig(output_plot)
    print(f"\n✅ Analysis complete. Results saved to: {output_plot}")

if __name__ == "__main__":
    run_finance_validation()
