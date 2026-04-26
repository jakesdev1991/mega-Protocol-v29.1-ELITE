# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import time
import gc
import subprocess

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from finance.finance_coevolution import FinanceArena
from agent_zero.tokamak_combat import Arena
from co_evolution_loop import main as run_physics_cycle
from finance.discovery_agent import DiscoveryAgent

def get_ram_usage_percent():
    """Returns the current RAM usage percentage on Windows."""
    try:
        # Get Total Memory
        cmd_total = "wmic ComputerSystem get TotalPhysicalMemory /Value"
        out_total = subprocess.check_output(cmd_total, shell=True).decode()
        total = int(out_total.split('=')[1].strip())
        
        # Get Free Memory
        cmd_free = "wmic OS get FreePhysicalMemory /Value"
        out_free = subprocess.check_output(cmd_free, shell=True).decode()
        free = int(out_free.split('=')[1].strip()) * 1024 # KB to Bytes
        
        used = total - free
        return (used / total) * 100
    except Exception:
        return 50.0 # Default if check fails

from finance.market_monitor import MarketMonitor
from finance.execute_trade import SolanaExecutor
import asyncio

class PoliteOrchestrator:
    """Sequential, memory-aware orchestrator for the Omega Protocol."""
    
    def __init__(self):
        self.finance = FinanceArena()
        self.tokamak = Arena()
        self.discovery = DiscoveryAgent()
        self.market = MarketMonitor()
        self.solana = SolanaExecutor()
        self.ram_threshold = 75.0 # Max 75% RAM usage

    def run_sequential_cycle(self):
        print("\n" + "="*80)
        print("🕯️  [PoliteOrchestrator] Starting Sequential Omega Cycle...")
        print("="*80)
        
        ram = get_ram_usage_percent()
        print(f"📈 Current System RAM Usage: {ram:.1f}%")
        
        if ram > self.ram_threshold:
            print(f"🛑 RAM usage too high ({ram:.1f}%). Throttling... Sleeping for 10 minutes.")
            time.sleep(600)
            return

        # 1. Market Sensory Phase
        print("\n--- PHASE 1: MARKET SENSORY (Solana Devnet) ---")
        self.market.get_latest_market_state()
        p_dot, v_ddot = self.market.calculate_omega_metrics()
        print(f"📊 Market Metrics: P_dot={p_dot:.2f}, V_ddot={v_ddot:.2f}")

        # Trigger Trade if anomaly detected (e.g. V_ddot > 5e6)
        if abs(v_ddot) > 5e6:
            print("🚨 [TRIGGER] Extreme Volume Acceleration detected. Initializing Firing Sequence.")
            trade_log = asyncio.run(self.solana.execute_mock_swap(0.1))
            # Log result for co-evolution
            with open("agent_zero/knowledge/evolution_log.jsonl", "a") as f:
                f.write(json.dumps(trade_log) + "\n")
            print(f"✅ Trade Result Logged: {trade_log['status']}")

        # 2. Finance Round
        print("\n--- PHASE 2: FINANCE MANIFOLD ---")
        try:
            self.finance.run_training_round()
        except Exception as e:
            print(f"⚠️ Finance Error: {e}")
        gc.collect()

        # 3. Tokamak Round
        print("\n--- PHASE 3: TOKAMAK COMBAT ---")
        try:
            # Replicating Arena.run_combat_loop() single-step logic
            data = self.tokamak.scraper.fetch_next_data()
            if data:
                task = f"Read this research and propose a derivation for the Omega Protocol: {data}"
                alpha_resp = self.tokamak.alpha.reason(task, depth="standard")
                beta_resp = self.tokamak.beta.reason(f"Critique this: {alpha_resp}", depth="standard")
                print("✅ Tokamak Round Complete.")
        except Exception as e:
            print(f"⚠️ Tokamak Error: {e}")
        gc.collect()

        # 4. Physics Round
        print("\n--- PHASE 4: PHYSICS CO-EVOLUTION ---")
        try:
            run_physics_cycle()
        except Exception as e:
            print(f"⚠️ Physics Error: {e}")
        gc.collect()

        # 5. Discovery Round
        print("\n--- PHASE 5: TREND DISCOVERY ---")
        try:
            self.discovery.hunt()
        except Exception as e:
            print(f"⚠️ Discovery Error: {e}")
        gc.collect()

        print("\n✅ [PoliteOrchestrator] All phases complete.")
        print("⏳ Entering deep sleep (10 minutes) to preserve system resources...")
        time.sleep(600)

    def start(self):
        round_num = 1
        while True:
            print(f"\n🚀 OMEGA ORCHESTRATOR ROUND {round_num}")
            self.run_sequential_cycle()
            round_num += 1

if __name__ == "__main__":
    orchestrator = PoliteOrchestrator()
    orchestrator.start()
