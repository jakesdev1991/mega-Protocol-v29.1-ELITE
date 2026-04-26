# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import time
import json
import asyncio
import numpy as np
import gc
import subprocess

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from finance.market_monitor import MarketMonitor
from finance.execute_trade import SolanaExecutor
from finance.finance_agent import FinanceAgent

def get_current_ram_usage():
    """Queries CIM for precise system-wide RAM usage %."""
    try:
        cmd = 'powershell "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory"'
        out = subprocess.check_output(cmd, shell=True).decode()
        lines = out.strip().split('\n')
        if len(lines) >= 3:
            data = lines[2].split()
            total = int(data[0])
            free = int(data[1])
            return ((total - free) / total) * 100
    except:
        return 99.0 # Assume full if check fails
    return 99.0

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat
import torch

class SafeStealthEngine:
    """
    Omega Protocol v30.1 - Safe Stealth Engine (Dynamic Learning Mode).
    Respects 50% RAM target and dynamically adjusts weights based on PnL.
    """
    def __init__(self):
        self.market = MarketMonitor()
        self.solana = SolanaExecutor()
        self.finbrain = FinanceAgent("Safe-FinBrain")
        self.monitor = RCODMonitor()
        self.safety_ceiling = 50.0 
        self.prev_price = None
        
        # Day Trading State
        self.position_sol = 0.0
        self.starting_cash = 1000.0
        self.cash = self.starting_cash
        self.prices_history = []
        self.last_trade_round = 0
        
        # --- DYNAMIC STRATEGY WEIGHTS (The 'Ky' Weights) ---
        self.weights = {
            "sma_window": 15,
            "cooldown_rounds": 10,
            "buy_threshold": 0.6,
            "sell_threshold": 0.2,
            "vol_multiplier": 20.0
        }
        self.performance_log = [] # Track PnL history for learning
        
        print(f"🛡️  Dynamic Stealth Engine initialized. Starting Weights: {self.weights}")

    async def meta_recalibrate(self):
        """Allows the FinBrain to adjust weights based on recent performance."""
        recent_pnl = (self.cash + (self.position_sol * self.prev_price) - self.starting_cash) / self.starting_cash * 100
        
        task = f"""
        ### META-LEARNING RESET
        Current Weights: {json.dumps(self.weights)}
        Recent Performance: {recent_pnl:.2f}% return.
        
        Analyze the market regime and performance. Should we adjust our strategy?
        If we are losing money, consider increasing sma_window or buy_threshold.
        If we are missing trades, consider lowering buy_threshold or vol_multiplier.
        
        Respond ONLY with a JSON object of updated weights if changes are needed, e.g.:
        {{"sma_window": 20, "buy_threshold": 0.7, ...}}
        """
        
        print(f"🧠 [Meta-Learning] Safe-FinBrain is reflecting on performance ({recent_pnl:.2f}%)...")
        suggestion = self.finbrain.reason(task, depth="standard")
        
        try:
            # Extract JSON from agent response
            import re
            match = re.search(r'\{.*\}', suggestion, re.DOTALL)
            if match:
                new_weights = json.loads(match.group())
                self.weights.update(new_weights)
                print(f"⚙️  [Weights Updated]: {self.weights}")
        except Exception as e:
            print(f"⚠️  Meta-Recalibration failed to parse: {e}")

    async def main_loop(self):
        round_count = 1
        while True:
            ram = get_current_ram_usage()
            
            if ram > 90.0:
                print(f"⚠️ [CRITICAL] System RAM at {ram:.1f}%. Entering Emergency Throttle (60s)...")
                await asyncio.sleep(60)
                continue
            
            # 1. Market Sensory Update
            buffer = self.market.get_latest_market_state()
            current_price = buffer['price'].iloc[-1]
            self.prices_history.append(current_price)
            if len(self.prices_history) > self.weights["sma_window"]:
                self.prices_history.pop(0)
            current_sma = sum(self.prices_history) / len(self.prices_history)
            
            # 2. RCOD Computation
            phi_delta = 0.0
            if self.prev_price is not None:
                scaled_input = (current_price - self.prev_price) / self.prev_price * self.weights["vol_multiplier"]
                _, phi_delta = self.monitor.step(scaled_input, layer_id="sol_daytrade")
            
            self.prev_price = current_price
            
            # 3. Meta-Learning Trigger (Every 50 rounds)
            if round_count % 50 == 0:
                await self.meta_recalibrate()
            
            # 4. Intraday Trading Logic (Dynamic)
            in_cooldown = (round_count - self.last_trade_round) < self.weights["cooldown_rounds"]
            
            if len(self.prices_history) == self.weights["sma_window"] and not in_cooldown:
                if phi_delta > self.weights["buy_threshold"] and current_price > current_sma and self.cash > 0: 
                    task = f"[PAPER_TRADE_PROTOCOL] INTRADAY entry signal at Phi_Delta={phi_delta:.4f}."
                    decision = self.finbrain.reason(task, depth="standard")
                    if "entry" in decision.lower() or "buy" in decision.lower():
                        self.position_sol = self.cash / current_price
                        self.cash = 0.0
                        self.last_trade_round = round_count
                        print(f"🔥 [BUY] at ${current_price:,.2f}. Weights: {self.weights['buy_threshold']} thres.")
                        await self.solana.execute_mock_swap(self.position_sol)
                        
                elif (phi_delta < self.weights["sell_threshold"] or current_price < current_sma) and self.position_sol > 0:
                    task = f"[PAPER_TRADE_PROTOCOL] INTRADAY exit signal at Phi_Delta={phi_delta:.4f}."
                    decision = self.finbrain.reason(task, depth="standard")
                    if "exit" in decision.lower() or "sell" in decision.lower():
                        self.cash = self.position_sol * current_price
                        self.last_trade_round = round_count
                        print(f"❄️ [SELL] at ${current_price:,.2f}. Portfolio: ${self.cash:,.2f}")
                        await self.solana.execute_mock_swap(self.position_sol)
                        self.position_sol = 0.0
            
            total_value = self.cash + (self.position_sol * current_price)
            print(f"⏱️  Round {round_count} | Price: ${current_price:,.2f} | Phi_Delta: {phi_delta:.4f} | Portfolio: ${total_value:,.2f}")
            
            wait_time = 2 if ram < self.safety_ceiling else 5
            await asyncio.sleep(wait_time)
            round_count += 1
            if round_count % 20 == 0: gc.collect()

if __name__ == "__main__":
    engine = SafeStealthEngine()
    asyncio.run(engine.main_loop())
