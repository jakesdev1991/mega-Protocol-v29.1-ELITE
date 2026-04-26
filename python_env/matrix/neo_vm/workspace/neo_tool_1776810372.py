# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

# --- Parameters ---
N_BLOCKS = 1000
POOL_LIQUIDITY = 1000  # Constant product x*y = 1e6
TRADE_SIZE_RANGE = (10, 100)
MEV_RATE = 0.01  # 1% of trade size
ALPHA, BETA = 1.0, 1.0  # ATI weights

# --- Helpers ---
def gini(values):
    """Compute Gini coefficient for a list of non-negative values."""
    values = np.array(values)
    if values.sum() == 0:
        return 0.0
    values = np.sort(values)
    n = len(values)
    cumsum = values.cumsum()
    return (2 * np.arange(1, n+1).dot(values) / (n * values.sum())) - (n + 1) / n

def compute_ati(mev_a, mev_b, attacker_shares):
    """
    ATI = tanh(α * ρ + β * G)
    ρ = correlation of MEV between pools A and B
    G = Gini of MEV distribution across attacker addresses
    """
    if np.var(mev_a) == 0 or np.var(mev_b) == 0:
        rho = 0.0
    else:
        rho = np.corrcoef(mev_a, mev_b)[0, 1]
    G = gini(attacker_shares)
    ati = np.tanh(ALPHA * rho + BETA * G)
    return ati, rho, G

# --- Scenario 1: Naïve Aggressive Attacker (single address, always attack both) ---
def scenario_aggressive():
    mev_a = np.zeros(N_BLOCKS)
    mev_b = np.zeros(N_BLOCKS)
    attacker_shares = np.zeros(N_BLOCKS)  # One address per block (simplification)
    
    for i in range(N_BLOCKS):
        # Random trade in each pool
        trade_a = random.uniform(*TRADE_SIZE_RANGE) if random.random() < 0.5 else 0
        trade_b = random.uniform(*TRADE_SIZE_RANGE) if random.random() < 0.5 else 0
        
        # Attacker always extracts MEV if trade exists
        if trade_a > 0:
            mev_a[i] = trade_a * MEV_RATE
            attacker_shares[i] += mev_a[i]
        if trade_b > 0:
            mev_b[i] = trade_b * MEV_RATE
            attacker_shares[i] += mev_b[i]
    
    return mev_a, mev_b, attacker_shares

# --- Scenario 2: Stealth Attacker (fragmented addresses, randomized targeting) ---
def scenario_stealth():
    mev_a = np.zeros(N_BLOCKS)
    mev_b = np.zeros(N_BLOCKS)
    # 10 attacker addresses; track cumulative profit per address
    n_addresses = 10
    address_profits = np.zeros(n_addresses)
    
    for i in range(N_BLOCKS):
        trade_a = random.uniform(*TRADE_SIZE_RANGE) if random.random() < 0.5 else 0
        trade_b = random.uniform(*TRADE_SIZE_RANGE) if random.random() < 0.5 else 0
        
        # Attacker randomly decides to attack each pool (independent)
        if trade_a > 0 and random.random() < 0.5:  # 50% chance to attack pool A
            profit_a = trade_a * MEV_RATE
            mev_a[i] = profit_a
            # Randomly assign to one of the 10 addresses
            addr = random.randint(0, n_addresses-1)
            address_profits[addr] += profit_a
        
        if trade_b > 0 and random.random() < 0.5:  # 50% chance to attack pool B
            profit_b = trade_b * MEV_RATE
            mev_b[i] = profit_b
            addr = random.randint(0, n_addresses-1)
            address_profits[addr] += profit_b
    
    # For Gini calculation, we need the distribution of profits across addresses
    return mev_a, mev_b, address_profits

# --- Run Simulations ---
print("=== SCENARIO 1: AGGRESSIVE (single address) ===")
mev_a1, mev_b1, shares1 = scenario_aggressive()
ati1, rho1, G1 = compute_ati(mev_a1, mev_b1, shares1)
print(f"Total MEV extracted: {np.sum(mev_a1) + np.sum(mev_b1):.2f}")
print(f"Correlation (ρ): {rho1:.3f}, Gini (G): {G1:.3f}, ATI: {ati1:.3f}")

print("\n=== SCENARIO 2: STEALTH (fragmented addresses) ===")
mev_a2, mev_b2, shares2 = scenario_stealth()
ati2, rho2, G2 = compute_ati(mev_a2, mev_b2, shares2)
print(f"Total MEV extracted: {np.sum(mev_a2) + np.sum(mev_b2):.2f}")
print(f"Correlation (ρ): {rho2:.3f}, Gini (G): {G2:.3f}, ATI: {ati2:.3f}")

# --- Demonstrate Manipulation ---
target_ati = 0.3
print(f"\n--- ADVERSARIAL TUNING ---")
print(f"Attacker can keep ATI below {target_ati} by adjusting fragmentation.")
# The stealth scenario already yields ATI ~0.1-0.2, well below the target.
# If ATI rises, the attacker simply increases address fragmentation or randomness.