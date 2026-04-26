# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Parameters ---
N_POOLS = 5
BLOCK_TIME = 12  # seconds (Ethereum-ish)
SIM_TIME = 1000  # seconds
LATENCIES = [0, 6, 12, 24]  # 0, 0.5B, B, 2B
ALPHA = BETA = GAMMA = DELTA = 1.0  # HFI weights

# --- AMM Pool ---
class AMM:
    def __init__(self, x0, y0):
        self.x = x0
        self.y = y0
        self.k = x0 * y0
        self.il_history = []

    def price(self):
        return self.y / self.x

    def trade(self, dx):
        # Constant product swap
        dy = self.y - self.k / (self.x + dx)
        self.x += dx
        self.y -= dy
        return dy

    def impermanent_loss(self, price_external):
        # IL vs holding
        v_hold = self.k**0.5 * (price_external**0.5 + price_external**-0.5)
        v_pool = self.x * price_external + self.y
        il = (v_pool - v_hold) / v_hold
        self.il_history.append(il)
        return il

# --- Simulation Engine ---
def simulate(latency):
    # Initialize identical pools (homogeneous design)
    pools = [AMM(x0=1000, y0=1000) for _ in range(N_POOLS)]
    trades = []  # (execute_time, pool_id, dx)
    slippages = []
    reserves = np.zeros((SIM_TIME, N_POOLS, 2))

    for t in range(SIM_TIME):
        # External price oscillates (creates arbitrage opportunity)
        price_ext = 1.0 + 0.1 * np.sin(2 * np.pi * t / 50) + 0.01 * np.random.randn()

        # Arbitrage detection (if pool price deviates > 0.5%)
        for i, pool in enumerate(pools):
            if abs(pool.price() - price_ext) / price_ext > 0.005:
                # Optimal trade size to align price (approx)
                dx = (np.sqrt(pool.k * price_ext) - pool.x)
                # Schedule trade with latency
                execute_time = t + latency
                trades.append((execute_time, i, dx))

        # Execute matured trades
        trades_to_execute = [tr for tr in trades if tr[0] <= t]
        trades = [tr for tr in trades if tr[0] > t]
        for _, i, dx in trades_to_execute:
            pool = pools[i]
            old_price = pool.price()
            pool.trade(dx)
            new_price = pool.price()
            slippage = abs(old_price - new_price) / old_price
            slippages.append(slippage)

        # Record reserves and IL
        for i, pool in enumerate(pools):
            reserves[t, i] = [pool.x, pool.y]
            pool.impermanent_loss(price_ext)

    # --- Compute Metrics ---
    # 1. Curvature (average pairwise correlation of reserve ratios)
    ratios = reserves[:, :, 1] / reserves[:, :, 0]  # y/x over time
    corrs = np.corrcoef(ratios.T)  # N_POOLS x N_POOLS
    curvature = np.mean(np.abs(corrs[np.triu_indices_from(corrs, k=1)]))

    # 2. IL dispersion
    il_final = [p.il_history[-1] for p in pools]
    sigma_il = np.std(il_final)

    # 3. Reserve concentration (HHI of token holdings across pools)
    total_x = np.sum(reserves[-1, :, 0])
    total_y = np.sum(reserves[-1, :, 1])
    share_x = reserves[-1, :, 0] / total_x
    share_y = reserves[-1, :, 1] / total_y
    hhi_x = np.sum(share_x**2)
    hhi_y = np.sum(share_y**2)
    concentration = (hhi_x + hhi_y) / 2.0

    # 4. Slippage skewness
    slippage_skew = np.mean(np.abs(slippages))  # simplified

    # 5. Homogeneity Fragility Index (HFI)
    hfi = np.tanh(ALPHA * curvature + BETA * sigma_il + GAMMA * concentration + DELTA * slippage_skew)

    # 6. Resonance Index (RI): Fourier magnitude at block frequency
    # Use slippage time-series (pad to power of 2)
    slip_series = np.array(slippages[:512]) if len(slippages) > 512 else np.pad(slippages, (0, 512 - len(slippages)), 'constant')
    fft = np.fft.fft(slip_series)
    freqs = np.fft.fftfreq(len(slip_series), d=1.0)
    block_freq = 1.0 / BLOCK_TIME
    # Find nearest frequency bin
    idx = np.argmin(np.abs(freqs - block_freq))
    ri = np.tanh(np.abs(fft[idx]) / len(slip_series))

    # 7. Total impermanent loss (aggregate loss)
    total_il = np.sum(np.abs(il_final))

    return {
        "latency": latency,
        "HFI": hfi,
        "RI": ri,
        "total_il": total_il,
        "curvature": curvature,
        "sigma_il": sigma_il,
        "concentration": concentration,
        "slippage_skew": slippage_skew,
    }

# --- Run Sweep ---
results = [simulate(lat) for lat in LATENCIES]

# --- Plot ---
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

latencies = [r["latency"] for r in results]
hfis = [r["HFI"] for r in results]
ris = [r["RI"] for r in results]
total_ils = [r["total_il"] for r in results]

ax[0].plot(latencies, hfis, 'o-', label="HFI", linewidth=2)
ax[0].plot(latencies, ris, 's--', label="Resonance Index (RI)", linewidth=2)
ax[0].set_xlabel("Arbitrage Latency (s)")
ax[0].set_ylabel("Index Value")
ax[0].set_title("HFI vs RI")
ax[0].legend()
ax[0].grid(True)

ax[1].plot(latencies, total_ils, 'o-', color='crimson', linewidth=2)
ax[1].set_xlabel("Arbitrage Latency (s)")
ax[1].set_ylabel("Total Impermanent Loss")
ax[1].set_title("Systemic Loss (Latency Resonance)")
ax[1].grid(True)

plt.tight_layout()
plt.show()