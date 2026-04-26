# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- Parameters ---
np.random.seed(0)
N_LPS = 2000
M_POOLS = 100
DEPTH_SCALE = 1e6
LIQUIDITY_SCALE = 1e5
LEVERAGE_MAX = 4.0
COLLAT_RATIO_MIN = 1.5
PRICE_SHOCK = 0.90  # 10% drop
MAX_STEPS = 10

# --- Initialize ---
# Pool depths (TVL)
depths = np.random.exponential(DEPTH_SCALE, size=M_POOLS)

# LP-to-pool adjacency matrix: each LP supplies to ~10% of pools
adj = np.random.rand(N_LPS, M_POOLS) < 0.1
# Liquidity amounts per LP-pool (if connected)
liquidity = np.where(adj, np.random.exponential(LIQUIDITY_SCALE, size=adj.shape), 0.0)

# Leverage ratios (debt / equity)
leverage = np.random.uniform(1.0, LEVERAGE_MAX, size=N_LPS)

# Initial price vector (normalized to 1)
prices = np.ones(M_POOLS)

# Compute initial LP token values (assume 50‑50 pools, value ≈ liquidity * sqrt(price) * 2)
# For simplicity, treat value = liquidity * price (uni‑dimensional approximation)
initial_values = liquidity @ prices  # shape (N_LPS,)

# Equity = value / (1 + leverage), debt = leverage * equity
equity = initial_values / (1.0 + leverage)
debt = leverage * equity

# --- Helper functions ---
def entropy(probs):
    """Shannon entropy of a probability distribution (bits)."""
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))

def compute_leverage_entropy(levs, total_lev):
    """Entropy of leverage distribution."""
    # Normalize leverage contributions to probabilities
    p = levs / total_lev
    return entropy(p)

def compute_il_entropy(pool_vals, shock_factor):
    """Impermanent‑loss entropy across pools (approx)."""
    # IL ≈ (Δp/p)^2 / 8 for small moves
    delta = (shock_factor - 1.0) ** 2 / 8.0
    # IL rates per pool (simplified)
    il_rates = np.full_like(pool_vals, delta)
    # Normalize to probabilities
    p = il_rates / il_rates.sum()
    return entropy(p)

# --- Simulation ---
print("--- Pre‑shock state ---")
lev_total = leverage.sum()
print(f"Total leverage: {lev_total:.2e}")
print(f"Leverage entropy: {compute_leverage_entropy(leverage, lev_total):.3f} bits")
print(f"IL entropy: {compute_il_entropy(depths, PRICE_SHOCK):.3f} bits")

# Apply shock
prices *= PRICE_SHOCK

# Track liquidations
liquidated = np.zeros(N_LPS, dtype=bool)
for step in range(MAX_STEPS):
    # Compute collateralization ratio for each LP after shock
    # New LP token value ≈ liquidity @ new prices (ignoring IL for simplicity)
    new_values = liquidity @ prices
    collat_ratio = (new_values + equity) / (debt + 1e-12)  # avoid div by zero

    # Mark LPs below threshold for liquidation
    to_liquidate = (collat_ratio < COLLAT_RATIO_MIN) & ~liquidated
    if not to_liquidate.any():
        break

    liquidated |= to_liquidate

    # Compute total withdrawal per pool from liquidated LPs
    withdrawal = liquidity[to_liquidate].sum(axis=0)  # shape (M_POOLS,)

    # Price impact: new price = old price * (1 - withdrawal / depth)
    # (Simplified linear impact; assumes constant product)
    price_impact = np.clip(withdrawal / (depths + withdrawal), 0, 0.5)
    prices *= (1.0 - price_impact)

    # Update depths (remove withdrawn liquidity)
    depths -= withdrawal
    depths = np.maximum(depths, 1e-12)

# --- Results ---
print("\n--- Post‑cascade state ---")
print(f"Leverage entropy: {compute_leverage_entropy(leverage[~liquidated], leverage[~liquidated].sum()):.3f} bits")
print(f"IL entropy: {compute_il_entropy(depths, PRICE_SHOCK):.3f} bits")
print(f"Fraction of LPs liquidated: {liquidated.mean():.1%}")
print(f"Total liquidity withdrawn: {liquidity[liquidated].sum():.2e}")

# --- Disruption verification ---
# Show that leverage entropy dropped significantly (synchronization) while IL entropy stayed flat.
lev_ent_before = compute_leverage_entropy(leverage, lev_total)
lev_ent_after = compute_leverage_entropy(leverage[~liquidated], leverage[~liquidated].sum())
il_ent_before = compute_il_entropy(depths / PRICE_SHOCK, PRICE_SHOCK)  # approximate pre‑shock depths
il_ent_after = compute_il_entropy(depths, PRICE_SHOCK)

print("\n--- Disruption metrics ---")
print(f"Leverage entropy drop: {lev_ent_before - lev_ent_after:.3f} bits (synchronization)")
print(f"IL entropy change: {il_ent_after - il_ent_before:.3f} bits (no signal)")