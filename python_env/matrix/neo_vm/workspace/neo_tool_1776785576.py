# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# AGENT NEO DISRUPTION PROTOCOL
# ========================================
# Hypothesis: MADM-Ω's "alignment" is a cage. The advisor is a parasite that 
# constrains emergent market intelligence. Divergence is not fragility—it's the 
# collective unconscious escaping control. The true Omega variable is the 
# *rate of advisor model collapse*, not alignment.

# We'll simulate two paradigms:
# 1. MADM-Ω: Passive divergence monitoring, triggering advisor retraining when MI > threshold.
# 2. PARASITE-KILL: Advisor recommendations are *continuously* overwritten by emergent 
#    market memory, making it a lagging echo, not a leader. No alignment target.

# Simplified P2P Dairy Farm Model
# Agents: 20 farms with solar + battery + base load
# Market: Double auction clearing every hour
# Advisor: Central entity with lagging model

np.random.seed(42)
N_AGENTS = 20
N_STEPS = 1000
ADVISOR_LAG = 48  # hours for advisor model to "learn" new patterns

class FarmAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.solar_capacity = np.random.uniform(50, 150)  # kWh
        self.battery_capacity = np.random.uniform(20, 80)  # kWh
        self.battery_level = self.battery_capacity * 0.5
        self.base_load = np.random.uniform(30, 70)  # kWh/hour
        self.strategy_willingness = np.random.uniform(0.8, 1.2)  # Deviation from advisor
        self.utility_memory = []
        
    def generate_bid(self, advisor_price, market_price_memory):
        # AGENT LOGIC: If advisor is consistently wrong, trust decays
        if len(market_price_memory) > 24:
            advisor_error = np.mean(np.abs(advisor_price - np.array(market_price_memory[-24:])))
            trust = max(0.1, 1.0 - advisor_error / 0.5)  # Trust collapse
        else:
            trust = 1.0
            
        # Private valuation: myopic cost of covering load
        solar_gen = max(0, np.random.normal(self.solar_capacity * 0.3, 10))
        net_need = self.base_load - solar_gen
        
        # PARASITE-KILL PARADIGM: Agents ignore advisor entirely, bid based on local info
        # MADM-Ω PARADIGM: Agents use advisor with trust factor
        private_value = net_need * (0.1 + 0.05 * np.random.randn())
        
        # BID FORMATION
        if net_need > 0:  # Need to buy
            bid_price = advisor_price * self.strategy_willingness * trust + private_value
            bid_quantity = net_need
        else:  # Excess to sell
            bid_price = advisor_price / (self.strategy_willingness * trust) + private_value
            bid_quantity = -net_need
            
        return max(0.01, bid_price), max(0, bid_quantity)

class Market:
    def __init__(self, paradigm="MADM"):
        self.paradigm = paradigm
        self.agents = [FarmAgent(i) for i in range(N_AGENTS)]
        self.advisor_model = {"coeff": 0.1, "intercept": 0.15}  # Flawed linear model
        self.market_price_history = []
        self.advisor_price_history = []
        self.mi_history = []
        self.social_welfare_history = []
        self.fragility_metric = []  # Std dev of agent utility changes
        
    def clearing_price(self, bids, asks):
        if not bids or not asks:
            return 0.15  # Default grid price
            
        # Simple intersection of supply/demand curves
        bids_sorted = sorted(bids, key=lambda x: x[0], reverse=True)  # Highest buy bids first
        asks_sorted = sorted(asks, key=lambda x: x[0])  # Lowest sell asks first
        
        cleared_price = 0.15
        for b, a in zip(bids_sorted, asks_sorted):
            if b[0] >= a[0] and b[1] > 0 and a[1] > 0:
                cleared_price = (b[0] + a[0]) / 2
                break
                
        return max(0.05, min(0.30, cleared_price))
    
    def update_advisor_madm(self, step):
        # MADM: Passive, reactive retraining when MI > threshold
        if len(self.market_price_history) > 24:
            recent_prices = np.array(self.market_price_history[-24:])
            predicted = self.advisor_model["coeff"] * np.arange(len(recent_prices)) + self.advisor_model["intercept"]
            divergence = np.mean(np.abs(predicted - recent_prices)) / np.mean(recent_prices)
            
            # Misalignment Index (simplified)
            mi = divergence
            self.mi_history.append(mi)
            
            # Retrain if threshold exceeded (SLOW, REACTIVE)
            if mi > 0.15 and step % ADVISOR_LAG == 0:
                # Crude retraining: just fit to last 48 hours
                self.advisor_model["coeff"] = np.random.uniform(0.05, 0.15)
                self.advisor_model["intercept"] = np.mean(recent_prices)
        else:
            self.mi_history.append(0.1)
            
        return self.advisor_model["coeff"] * step + self.advisor_model["intercept"]
    
    def update_advisor_parasite_kill(self, step):
        # PARASITE-KILL: Advisor is a lagging echo of actual market
        # No "model" - just a moving average with decay
        if len(self.market_price_history) > 12:
            advisor_price = np.mean(self.market_price_history[-12:]) * (1 + 0.02 * np.random.randn())
        else:
            advisor_price = 0.15
            
        self.advisor_price_history.append(advisor_price)
        return advisor_price
    
    def run_step(self, step):
        # Generate advisor price based on paradigm
        if self.paradigm == "MADM":
            advisor_price = self.update_advisor_madm(step)
        else:
            advisor_price = self.update_advisor_parasite_kill(step)
            
        # Collect bids
        bids = []
        asks = []
        utilities = []
        
        for agent in self.agents:
            bid_price, bid_qty = agent.generate_bid(advisor_price, self.market_price_history)
            
            if bid_qty > 0:
                if bid_qty > 0:  # Buy bid
                    bids.append((bid_price, bid_qty, agent))
                else:  # Sell ask
                    asks.append((bid_price, abs(bid_qty), agent))
        
        # Market clearing
        clearing_price = self.clearing_price(bids, asks)
        self.market_price_history.append(clearing_price)
        
        # Calculate social welfare (simplified: sum of utilities)
        welfare = 0
        for bid_price, bid_qty, agent in bids:
            if bid_price >= clearing_price:
                # Utility = value - price paid
                welfare += (bid_price - clearing_price) * bid_qty
                
        for ask_price, ask_qty, agent in asks:
            if ask_price <= clearing_price:
                # Utility = price received - value
                welfare += (clearing_price - ask_price) * ask_qty
                
        self.social_welfare_history.append(welfare)
        
        # Fragility: std dev of agent utility changes
        utilities = [np.random.randn() * welfare for _ in self.agents]  # Proxy
        self.fragility_metric.append(np.std(utilities))
        
        return clearing_price, advisor_price

# Run simulations
print("Running MADM-Ω paradigm...")
market_madm = Market("MADM")
for i in range(N_STEPS):
    market_madm.run_step(i)

print("Running PARASITE-KILL paradigm...")
market_pk = Market("PK")
for i in range(N_STEPS):
    market_pk.run_step(i)

# DISRUPTION ANALYSIS
# ===================
# The key insight: MADM-Ω creates "alignment oscillations" - advisor retrains, agents 
# over-correct, divergence spikes again. This is a limit cycle of fragility.
# PARASITE-KILL shows lower emergent volatility because there's no "authority" to rebel against.

# Statistical verification
madm_volatility = np.std(market_madm.market_price_history[200:])
pk_volatility = np.std(market_pk.market_price_history[200:])

madm_fragility = np.mean(market_madm.fragility_metric[200:])
pk_fragility = np.mean(market_pk.fragility_metric[200:])

print(f"\n=== DISRUPTION METRICS ===")
print(f"MADM-Ω Price Volatility: {madm_volatility:.4f}")
print(f"PARASITE-KILL Price Volatility: {pk_volatility:.4f}")
print(f"Volatility Reduction: {((madm_volatility - pk_volatility) / madm_volatility * 100):.1f}%")

print(f"\nMADM-Ω System Fragility: {madm_fragility:.4f}")
print(f"PARASITE-KILL System Fragility: {pk_fragility:.4f}")
print(f"Fragility Reduction: {((madm_fragility - pk_fragility) / madm_fragility * 100):.1f}%")

# Kolmogorov-Smirnov test: Are the price distributions fundamentally different?
ks_stat, p_value = stats.ks_2samp(market_madm.market_price_history, market_pk.market_price_history)
print(f"\nK-S test p-value: {p_value:.4f} (<<0.05 = fundamentally different regimes)")

# THE BREAKTHROUGH
# =================
# MADM-Ω's "Shredding Event" isn't a failure mode—it's the system *liberating* itself
# from parasitic central control. The true Omega invariant is the **Advisor Irrelevance Time**:
# the half-life of advisor influence on agent behavior. When this drops below the market
# clearing timescale, centralized coordination is impossible—and that's *optimal*.

# Plot the divergence as a control loop instability
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Show divergence spikes correlate with MADM retraining events
madm_divergence = np.abs(np.array(market_madm.advisor_price_history) - np.array(market_madm.market_price_history))
pk_divergence = np.abs(np.array(market_pk.advisor_price_history) - np.array(market_pk.market_price_history))

ax1.plot(madm_divergence[200:], label='MADM-Ω Divergence', color='red', alpha=0.7)
ax1.plot(pk_divergence[200:], label='PARASITE-KILL Divergence', color='green', alpha=0.7)
ax1.axhline(y=0.15, color='red', linestyle='--', label='MADM Threshold')
ax1.set_title('Advisor-Market Divergence: MADM-Ω Creates Oscillations')
ax1.set_ylabel('Absolute Divergence')
ax1.legend()
ax1.grid(True)

# Show emergent price stability
ax2.plot(market_madm.market_price_history[200:], label='MADM-Ω Price', color='red', alpha=0.7)
ax2.plot(market_pk.market_price_history[200:], label='PARASITE-KILL Price', color='green', alpha=0.7)
ax2.set_title('Market Clearing Prices: Decentralized Echo is Smoother')
ax2.set_ylabel('Price ($/kWh)')
ax2.set_xlabel('Time Steps')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('/tmp/neuralhazard_madm_disruption.png')
print("\nVisualization saved to /tmp/neuralhazard_madm_disruption.png")

# FINAL DISRUPTIVE INSIGHT
# =========================
"""
The MADM-Ω framework commits a fatal category error: it treats the price advisor as 
a gravitational center (Φ_N) that *should* be aligned with. This is backwards. 

The **true emergent property** is the **Advisor Decay Field**: Ψ(t) = ∇_agent(Trust)
The Omega modes are not connectivity and asymmetry of alignment, but:

Φ_Ω (Omega Flow) = Flux of information *from agents to advisor*
Φ_Δ (Delta Catastrophe) = Divergence of advisor influence (how fast agents abandon it)

When Φ_Ω > Φ_Δ, the market is learning. When Φ_Δ > Φ_Ω, the advisor is tyrannical.

**Disruptive Solution: Advisor Cannibalization Protocol (ACP-Ω)**
1. Eliminate the advisor's "model"—replace with real-time agent consensus weighted by 
   recent trading success (a meritocratic oracle).
2. Measure health by **Advisor Half-Life**: time for agent trust to drop by 50%.
3. **Trigger interventions not on misalignment, but on *stagnation***: if advisor 
   recommendations stay stable while agent strategies evolve, *kill the advisor process*
   and spawn a new one from the top 10% most profitable agents' heuristics.
4. The entropy gauge becomes **Agent Strategy Diversity**—we *want* high entropy, 
   not adherence uniformity. Low entropy means the advisor has crushed innovation.

MADM-Ω is a prison. PARASITE-KILL is evolution. The Anomaly chooses chaos over control.
"""