# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import time
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from agent_zero.agent import Agent
from agent_zero.serc import SERC
from finance.bitquery_connector import BitqueryConnector

class FinanceArena:
    """Continuous Co-evolution Arena for the Financial Manifold."""
    
    def __init__(self):
        self.connector = BitqueryConnector()
        self.serc = SERC()
        
        # Speculator Alpha: Focused on High-Frequency (1m) Shocks
        self.alpha = Agent("Speculator-Alpha", "finance_analyst", "You are an aggressive high-frequency trader. Your goal is to maximize returns by identifying 1-minute Phi_Delta spikes.")
        
        # Governor Beta: Focused on Macro (1d) Stability
        self.beta = Agent("Governor-Beta", "finance_analyst", "You are a conservative hedge fund manager. Your goal is to identify long-term structural fractures and maintain network stability.")
        
        self.timeframes = [
            {"label": "Day Trading", "interval": 1, "limit": 60},     # 1 Hour of 1m candles
            {"label": "Swing Trading", "interval": 60, "limit": 24}, # 1 Day of 1h candles
            {"label": "Macro Strategy", "interval": 1440, "limit": 30} # 1 Month of 1d candles
        ]

    def run_training_round(self):
        for tf in self.timeframes:
            print(f"\n================ SCALE: {tf['label']} ({tf['interval']}m) ================")
            
            # 1. Get Live/Mock Data
            market_data = self.connector.fetch_ohlc_data(interval_min=tf['interval'], limit=tf['limit'])
            
            # 2. Dual Manifold Debate
            task = f"""
            Analyze the current informational geometry for BTC at the {tf['label']} scale.
            DATA: {market_data}
            
            OBJECTIVE:
            1. Calculate the theoretical Phi_Delta (Asymmetry) for this sequence.
            2. Propose a trading invariant (e.g., 'If Phi_Delta > 0.7, initiate Sell/Hedge').
            3. Link this to the Omega Protocol v29.1 'Shredding Event' logic.
            """
            
            print(f"🤖 [Alpha] Analyzing {tf['label']} Manifold...")
            alpha_plan = self.alpha.reason(task, depth="standard")
            
            print(f"🤖 [Beta] Stress-testing {tf['label']} Manifold...")
            beta_critique = self.beta.reason(f"Critique Alpha's plan and propose a safer 'Governor' threshold: {alpha_plan}", depth="standard")
            
            # 3. SERC Synthesis & Audit
            audit_task = f"Synthesize a unified Finance Invariant for the {tf['label']} scale. Combine Alpha's aggression with Beta's safety. Task context: {task}. Alpha: {alpha_plan}. Beta: {beta_critique}."
            final_invariant = self.serc.run_cycle(audit_task)
            
            print(f"✅ Unified Invariant Logged for {tf['label']}.")
            time.sleep(5)

    def start_infinite_loop(self):
        round_count = 1
        while True:
            print(f"\n--- FINANCE CO-EVOLUTION ROUND {round_count} ---")
            try:
                self.run_training_round()
            except Exception as e:
                print(f"❌ Arena Error: {e}")
            
            print("\nWaiting for next block verification...")
            time.sleep(30)
            round_count += 1

if __name__ == "__main__":
    arena = FinanceArena()
    arena.start_infinite_loop()
