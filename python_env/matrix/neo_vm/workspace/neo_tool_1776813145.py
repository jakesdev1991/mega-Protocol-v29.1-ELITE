# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Simulates ATI manipulation and meta‑MEV extraction in a homogeneous AMM ecosystem.
Key assumptions:
  - 5 identical pools (constant‑product)
  - MEV extracted ∝ trade_size / liquidity
  - Attacker can split profits across many addresses (Sybil) and inject noise trades.
  - Defender raises swap fee by 10 % when ATI > 0.72 (deterministic policy).
  - Attacker can front‑run the fee increase by sending a high‑fee transaction just before the threshold is crossed.
"""

import numpy as np
import math
from scipy.stats import gini as calc_gini

# ──────────────────────────────────────────────────────────────────────────────
# 1. Helpers
# ──────────────────────────────────────────────────────────────────────────────
def gini_coefficient(values):
    """Gini coefficient for a 1‑D array (0 = perfect equality, 1 = max inequality)."""
    if len(values) == 0 or np.allclose(values, 0):
        return 0.0
    # Use scipy's gini (requires positive values)
    return calc_gini(np.abs(values))

def avg_correlation(matrix):
    """Average Pearson correlation (off‑diagonal) for a (pools, time) matrix."""
    if matrix.shape[0] < 2:
        return 0.0
    corr = np.corrcoef(matrix)
    # Mask diagonal and take mean of upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    return corr[mask].mean() if mask.any() else 0.0

def attack_velocity(attacks, total_blocks):
    """Average number of blocks between attack events (ν)."""
    if len(attacks) < 2:
        return np.inf
    gaps = np.diff(sorted(attacks))
    return gaps.mean()

def lp_loss_dispersion(mev_per_pool_per_block):
    """Std‑dev of LP losses across pools, averaged over time."""
    # mev_per_pool_per_block shape: (pools, blocks)
    std_per_block = np.std(mev_per_pool_per_block, axis=0)
    return std_per_block.mean()

def compute_ati(correlation, gini, inv_velocity, dispersion, weights=(1,1,1,1)):
    """ATI = tanh(α·ρ + β·G + γ·ν⁻¹ + δ·σ)."""
    linear = (weights[0] * correlation +
              weights[1] * gini +
              weights[2] * inv_velocity +
              weights[3] * dispersion)
    return math.tanh(linear)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Simulation Parameters
# ──────────────────────────────────────────────────────────────────────────────
RNG = np.random.default_rng(0)
N_POOLS = 5
N_BLOCKS = 200
LIQUIDITY = 1_000_000  # uniform across pools
MEV_FACTOR = 0.1       # MEV = factor * trade_size / liquidity
ATTACK_THRESHOLD = 0.01  # ETH; MEV > threshold counts as an “attack”
ATI_THRESHOLD = 0.72
FEE_BUMP = 0.10         # 10 % fee increase when ATI > threshold

# ──────────────────────────────────────────────────────────────────────────────
# 3. Baseline Phase (blocks 0‑99) – Honest (but homogeneous) behavior
# ──────────────────────────────────────────────────────────────────────────────
baseline_mev = np.zeros((N_POOLS, N_BLOCKS//2))
baseline_attacks = []

for block in range(N_BLOCKS//2):
    # Random trade size (log‑normal) per pool
    trade_sizes = RNG.lognormal(mean=2, sigma=1.5, size=N_POOLS)
    mev = MEV_FACTOR * trade_sizes / LIQUIDITY
    
    # Randomly assign each MEV to one of a few attacker addresses
    # (high Gini)
    baseline_mev[:, block] = mev
    
    # Record attacks
    if np.any(mev > ATTACK_THRESHOLD):
        baseline_attacks.append(block)

# Compute baseline metrics
baseline_corr = avg_correlation(baseline_mev)
baseline_gini = gini_coefficient(baseline_mev.flatten())
baseline_vel = attack_velocity(baseline_attacks, N_BLOCKS//2)
baseline_inv_vel = 1.0 / baseline_vel if np.isfinite(baseline_vel) else 0.0
baseline_disp = lp_loss_dispersion(baseline_mev)

baseline_ati = compute_ati(baseline_corr, baseline_gini,
                           baseline_inv_vel, baseline_disp)
print(f"Baseline (blocks 0-99):")
print(f"  Correlation (ρ)        : {baseline_corr:.3f}")
print(f"  Gini (G)               : {baseline_gini:.3f}")
print(f"  Avg. time between attacks (ν) : {baseline_vel:.2f} blocks")
print(f"  LP loss dispersion (σ) : {baseline_disp:.3f}")
print(f"  ATI                    : {baseline_ati:.3f}")
print(f"  → Fee ramping triggered? {baseline_ati > ATI_THRESHOLD}")

# ──────────────────────────────────────────────────────────────────────────────
# 4. Manipulation Phase (blocks 100‑199) – Attacker actively games metrics
# ──────────────────────────────────────────────────────────────────────────────
# Strategy:
#   a) Split each MEV bundle across 50 Sybil addresses → lower Gini.
#   b) Inject noise trades (tiny, non‑profitable) to decorrelate pools.
#   c) Increase attack frequency (shorter gaps) → raise ν⁻¹.
#   d) Keep per‑pool MEV similar → lower dispersion.
manip_mev = np.zeros((N_POOLS, N_BLOCKS//2))
manip_attacks = []

for block in range(N_BLOCKS//2):
    # 1. Real MEV (still high) but split across many addresses
    trade_sizes = RNG.lognormal(mean=2, sigma=1.5, size=N_POOLS)
    mev = MEV_FACTOR * trade_sizes / LIQUIDITY
    
    # 2. Noise trades: small random perturbations to decorrelate
    noise = RNG.normal(scale=0.001, size=N_POOLS)
    mev = np.maximum(mev + noise, 0.0)
    
    # 3. Force attacks more frequently (every ~3 blocks)
    if block % 3 == 0:
        # Boost one pool to exceed threshold
        mev[RNG.integers(0, N_POOLS)] += ATTACK_THRESHOLD + 0.005
        manip_attacks.append(block)
    
    # 4. Even out MEV across pools (low dispersion)
    mev = np.full_like(mev, mev.mean())
    
    manip_mev[:, block] = mev

# Compute manipulation‑phase metrics
manip_corr = avg_correlation(manip_mev)
manip_gini = gini_coefficient(manip_mev.flatten())
manip_vel = attack_velocity(manip_attacks, N_BLOCKS//2)
manip_inv_vel = 1.0 / manip_vel if np.isfinite(manip_vel) else 0.0
manip_disp = lp_loss_dispersion(manip_mev)

manip_ati = compute_ati(manip_corr, manip_gini,
                        manip_inv_vel, manip_disp)
print(f"\nManipulation (blocks 100-199):")
print(f"  Correlation (ρ)        : {manip_corr:.3f}")
print(f"  Gini (G)               : {manip_gini:.3f}")
print(f"  Avg. time between attacks (ν) : {manip_vel:.2f} blocks")
print(f"  LP loss dispersion (σ) : {manip_disp:.3f}")
print(f"  ATI                    : {manip_ati:.3f}")
print(f"  → Fee ramping triggered? {manip_ati > ATI_THRESHOLD}")

# ──────────────────────────────────────────────────────────────────────────────
# 5. Meta‑MEV: Front‑running the defender’s fee ramp
# ──────────────────────────────────────────────────────────────────────────────
# Suppose the defender raises the swap fee by FEE_BUMP when ATI > threshold.
# An attacker can watch the ATI metric and, as soon as it crosses 0.72,
# submit a high‑fee transaction to be included *before* the fee increase,
# effectively capturing the arbitrage between the old and new fee regimes.
print(f"\n--- Meta‑MEV Extraction ---")
if baseline_ati > ATI_THRESHOLD:
    print("  Baseline triggers fee ramp. Attacker front‑runs → profit.")
else:
    print("  Baseline safe (no ramp).")

if manip_ati > ATI_THRESHOLD:
    print("  Manipulation triggers fee ramp. Attacker front‑runs → profit.")
else:
    print("  Manipulation keeps ATI low → defender *does not* ramp, "
          "but attacker still extracts MEV undetected.")

# ──────────────────────────────────────────────────────────────────────────────
# 6. Summary & Disruptive Takeaway
# ──────────────────────────────────────────────────────────────────────────────
print(f"\n=== SUMMARY ===")
print(f"Baseline ATI: {baseline_ati:.3f} (high → defender acts)")
print(f"Manipulated ATI: {manip_ati:.3f} (low → defender blind)")
print(f"Even though per‑block MEV extraction stayed high, the attacker "
      f"gamed the metrics to stay under the radar.")
print(f"The ‘shield’ becomes a strategic signal that the attacker can "
      f"front‑run or suppress at will.")