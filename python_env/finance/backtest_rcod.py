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

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat
import torch

def run_backtest():
    print("🚀 [Backtest] Initializing RCOD Backtest for Bitcoin...")
    
    # 1. Load data
    df = pd.read_csv('finance/btc_historical_full.csv', index_col='Date', parse_dates=True)
    # Target the 90-day period that previously failed (-11.99%)
    df = df.tail(90)
    prices = df['Close'].values
    volumes = df['Volume'].values
    dates = df.index
    
    print(f"Backtesting SMART FILTER on the last {len(prices)} days...")
    
    # 2. Strategy Parameters
    window_size = 10
    threshold = 0.5 # Lower threshold but higher requirements
    sma_period = 20
    
    # 3. Simulator State
    cash = 10000.0
    position = 0.0
    trades = []
    
    monitor = RCODMonitor()
    
    # Calculate SMA for trend filtering
    df['SMA'] = df['Close'].rolling(window=sma_period).mean()
    smas = df['SMA'].values
    
    for i in range(window_size, len(prices)):
        # Skip until SMA is ready
        if i < sma_period: continue
        
        # Calculate RCOD
        scaled_input = (prices[i] - prices[i-1]) / prices[i-1] * 10.0
        _, phi_delta = monitor.step(scaled_input, layer_id="btc_smart")
        
        current_price = prices[i]
        current_sma = smas[i]
        
        # SMART LOGIC:
        # 1. Phi_Delta > 0.5 (Informational Shock)
        # 2. Price > SMA (Trend is Upward) - Prevents buying the 'top' of a crash
        # 3. Volume > Previous Volume (Confirmation)
        
        if phi_delta > threshold and current_price > current_sma and volumes[i] > volumes[i-1] and cash > 0:
            # BUY
            position = cash / current_price
            trades.append({"date": dates[i], "type": "BUY", "price": current_price})
            cash = 0
            print(f"[{dates[i].date()}] SMART BUY at ${current_price:,.2f} (Trend Confirmed)")
            
        elif (phi_delta < 0.2 or current_price < current_sma) and position > 0:
            # SELL (Exit if stability returns OR trend breaks)
            cash = position * current_price
            trades.append({"date": dates[i], "type": "SELL", "price": current_price})
            position = 0
            print(f"[{dates[i].date()}] SMART SELL at ${current_price:,.2f} (Profit/Protection Exit)")

    # Final valuation
    final_value = cash + (position * prices[-1])
    return_pct = ((final_value - 10000.0) / 10000.0) * 100
    
    print("\n" + "="*40)
    print(f"💰 BACKTEST RESULTS")
    print(f"Starting Balance: $10,000.00")
    print(f"Ending Balance:   ${final_value:,.2f}")
    print(f"Total Return:      {return_pct:.2f}%")
    print(f"Total Trades:      {len(trades)}")
    print("="*40)
    
    return final_value

if __name__ == "__main__":
    run_backtest()
