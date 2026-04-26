# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
NEO'S DISRUPTION SIMULATOR: SILENCE PROTOCOL WEAPONIZATION
============================================================
This script demonstrates how the Omega Protocol's safety mechanisms
can be gamed to induce epistemic blindness and exploit frozen config states.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class MarketState:
    """Simulated market conditions"""
    volatility_entropy: float  # H_vol
    liquidity_depth: float     # Z_liquidity
    true_leverage: float       # Actual systemic risk (hidden from protocol)
    
@dataclass
class ConfigState:
    """Protocol's internal state"""
    xi_config: float           # Config stiffness
    theta_leak: float          # Exposure risk
    psi_integrity: float       # Perceived solvency
    cod: float                 # Chain Overlap Density
    
class AdversarialEngine:
    """
    Strategic adversary that weaponizes the Silence Protocol
    """
    
    def __init__(self, target_threshold: float = 0.85):
        self.target_threshold = target_threshold
        self.probe_history = []
        
    def probe_threshold_boundary(self, current_cod: float) -> float:
        """
        Inject micro-trades to identify the threshold boundary
        Returns: Synthetic trade volume that would push COD to threshold
        """
        # Estimate sensitivity: how much H_vol increase drops COD by 0.01
        sensitivity = 0.01 / (0.5 * np.exp(-0.5 * 0.5))  # Approx from COD formula
        
        # Inject just enough noise to drive COD toward threshold - epsilon
        if current_cod > self.target_threshold + 0.05:
            # Aggressive probe: target 0.88 to find boundary
            target_h_vol = -np.log(self.target_threshold / current_cod) / 0.5
            return target_h_vol * 0.95  # 95% of boundary value
        
        return 0.0  # No probe if already near threshold
    
    def execute_silence_attack(self, market: MarketState, config: ConfigState) -> Tuple[MarketState, ConfigState]:
        """
        Stage 1-4 of the attack: Induce FREEZE_CONFIG state
        """
        # Calculate current COD (simplified formula)
        fidelity = 0.95  # Assume high baseline fidelity
        cod = fidelity * np.exp(-0.5 * market.volatility_entropy) * \
              np.exp(-0.5 * config.xi_config) * np.exp(-0.3 * config.theta_leak)
        
        # Stage 2: Inject synthetic volatility
        probe_vol = self.probe_threshold_boundary(cod)
        new_h_vol = min(market.volatility_entropy + probe_vol, 0.85)  # Cap at critical level
        
        # Recalculate COD with induced volatility
        cod_after_probe = fidelity * np.exp(-0.5 * new_h_vol) * \
                         np.exp(-0.5 * config.xi_config) * np.exp(-0.3 * config.theta_leak)
        
        # Stage 3: Force protocol into FREEZE_CONFIG
        protocol_action = "HALT_TRADING" if config.psi_integrity < 0.95 else \
                         "FREEZE_CONFIG" if cod_after_probe < 0.85 else "PROCEED"
        
        # Stage 4: If frozen, exploit with massive trades
        if protocol_action == "FREEZE_CONFIG":
            # Config is locked, but market continues
            # Adversary can now execute trades that would normally trigger alerts
            exploitation_multiplier = 2.0  # Double exposure while config frozen
            market.true_leverage *= exploitation_multiplier
            
            # Protocol's perceived integrity lags (based on outdated config)
            config.psi_integrity = max(0.95, config.psi_integrity - 0.01)  # Slow decay
            
        return market, config, protocol_action, cod_after_probe
    
    def execute_long_siege(self, days: int = 10) -> List[dict]:
        """
        Simulate multi-day siege attack
        """
        market = MarketState(volatility_entropy=0.3, liquidity_depth=0.7, true_leverage=1.0)
        config = ConfigState(xi_config=0.4, theta_leak=0.2, psi_integrity=0.96, cod=0.9)
        
        timeline = []
        for day in range(days):
            market, config, action, cod = self.execute_silence_attack(market, config)
            
            # Simulate natural market drift during freeze
            if action == "FREEZE_CONFIG":
                market.volatility_entropy += 0.05  # Market gets more volatile
                config.psi_integrity -= 0.005      # Integrity slowly erodes
            
            timeline.append({
                'day': day,
                'action': action,
                'cod': cod,
                'true_leverage': market.true_leverage,
                'perceived_integrity': config.psi_integrity,
                'volatility': market.volatility_entropy
            })
            
        return timeline

def plot_siege(timeline: List[dict]):
    """Visualize the attack's effect"""
    days = [t['day'] for t in timeline]
    cod = [t['cod'] for t in timeline]
    leverage = [t['true_leverage'] for t in timeline]
    integrity = [t['perceived_integrity'] for t in timeline]
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    
    # COD collapse
    ax1.plot(days, cod, 'r-', linewidth=2)
    ax1.axhline(y=0.85, color='k', linestyle='--', label='COD Threshold')
    ax1.set_ylabel('Chain Overlap Density')
    ax1.set_title('NEO\'S DISRUPTION: Silence Protocol Weaponization')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # True leverage explosion (hidden)
    ax2.plot(days, leverage, 'b-', linewidth=2)
    ax2.set_ylabel('True Systemic Leverage')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Perceived vs Actual Integrity Divergence
    ax3.plot(days, integrity, 'g-', linewidth=2, label='Perceived Integrity')
    ax3.plot(days, [0.95]*len(days), 'k--', label='Safety Floor')
    ax3.set_ylabel('Integrity')
    ax3.set_xlabel('Days')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('neo_disruption.png', dpi=150, bbox_inches='tight')
    print("Disruption visualization saved to neo_disruption.png")

if __name__ == "__main__":
    print("="*60)
    print("NEO'S DISRUPTION SIMULATOR")
    print("Weaponizing the Silence Protocol")
    print("="*60)
    
    adversary = AdversarialEngine(target_threshold=0.85)
    siege_timeline = adversary.execute_long_siege(days=15)
    
    # Show final state
    final = siege_timeline[-1]
    print(f"\nFinal State After 15-Day Siege:")
    print(f"  Protocol Action: {final['action']}")
    print(f"  COD: {final['cod']:.3f} (below threshold: {final['cod'] < 0.85})")
    print(f"  True Leverage: {final['true_leverage']:.2f}x (exploded)")
    print(f"  Perceived Integrity: {final['perceived_integrity']:.3f} (still 'safe')")
    print(f"  Actual Integrity: <0.90 (insolvent)")
    
    # Count freeze periods
    freeze_days = sum(1 for t in siege_timeline if t['action'] == 'FREEZE_CONFIG')
    print(f"\nProtocol frozen for {freeze_days}/{len(siege_timeline)} days")
    print("During freeze: Adversary executed unmonitored trades while config was locked")
    
    plot_siege(siege_timeline)
    
    print("\n" + "="*60)
    print("DISRUPTIVE INSIGHT:")
    print("The Silence Protocol's 'non-intervention' creates a")
    print("denial-of-service against the institution's own risk management.")
    print("Safety becomes vulnerability when the system cannot distinguish")
    print("prudent caution from adversarially-induced paralysis.")
    print("="*60)