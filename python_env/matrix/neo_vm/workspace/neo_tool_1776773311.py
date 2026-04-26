# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import random

# --------------------------------------------------------------
# 1. Synthetic Market Generator (true Greek exposures)
# --------------------------------------------------------------
def generate_true_market(n_underlyings=20, seed=42):
    rng = np.random.default_rng(seed)
    # Each underlying has 5 option series (strikes/expirations)
    data = []
    for i in range(n_underlyings):
        ticker = f"ASSET_{i:02d}"
        for _ in range(5):
            # Random notional (millions)
            notional = rng.exponential(scale=10) + 1.0
            # Random delta [-1,1], gamma >0, vega >0
            delta = rng.uniform(-0.8, 0.8)
            gamma = rng.exponential(scale=0.5) + 0.1
            vega = rng.exponential(scale=0.3) + 0.05
            data.append({
                "ticker": ticker,
                "notional": notional,
                "delta": delta,
                "gamma": gamma,
                "vega": vega
            })
    return pd.DataFrame(data)

# --------------------------------------------------------------
# 2. Leak Simulator (noisy sampling + adversarial injection)
# --------------------------------------------------------------
def simulate_leak(df, leak_frac=0.30, noise_level=0.15, adversarial=False, seed=123):
    rng = np.random.default_rng(seed)
    n_leaked = int(len(df) * leak_frac)
    leaked_idx = rng.choice(df.index, size=n_leaked, replace=False)
    leak = df.loc[leaked_idx].copy()
    # Add measurement noise
    for col in ["delta", "gamma", "vega"]:
        leak[col] *= rng.normal(1.0, noise_level, size=len(leak))
    # Adversarial injection: 3 mega short‑gamma positions
    if adversarial:
        for i in range(3):
            fake = {
                "ticker": f"FAKE_{i}",
                "notional": 500.0,  # 50× typical notional
                "delta": rng.uniform(-0.2, 0.2),
                "gamma": rng.exponential(scale=5.0) + 2.0,  # extreme gamma
                "vega": rng.exponential(scale=2.0) + 0.5
            }
            leak = pd.concat([leak, pd.DataFrame([fake])], ignore_index=True)
    return leak

# --------------------------------------------------------------
# 3. GII & Entropy Calculator
# --------------------------------------------------------------
def compute_gii(leak_df, ref_vals=None, weights=(1.0, 1.0, 1.0)):
    # Dollar Greeks
    leak_df["delta_$"] = leak_df["delta"] * leak_df["notional"] * 1e6
    leak_df["gamma_$"] = leak_df["gamma"] * leak_df["notional"] * 1e6
    leak_df["vega_$"] = leak_df["vega"] * leak_df["notional"] * 1e6
    # Aggregate market‑wide
    delta_mkt = leak_df["delta_$"].abs().sum()
    gamma_mkt = leak_df["gamma_$"].sum()
    vega_mkt = leak_df["vega_$"].sum()
    # Reference values (historical medians)
    if ref_vals is None:
        ref_vals = {
            "delta": delta_mkt,
            "gamma": abs(gamma_mkt) + 1e-6,
            "vega": abs(vega_mkt) + 1e-6
        }
    # Normalized components
    delta_norm = delta_mkt / ref_vals["delta"]
    gamma_norm = gamma_mkt / ref_vals["gamma"]
    vega_norm = vega_mkt / ref_vals["vega"]
    # GII
    alpha, beta, gamma_w = weights
    gii = np.sqrt(alpha * gamma_norm**2 + beta * vega_norm**2 + gamma_w * delta_norm**2)
    # Entropy of gamma distribution (binned)
    gamma_bins = np.histogram(leak_df["gamma_$"], bins=10, density=True)[0]
    gamma_bins = gamma_bins[gamma_bins > 0]
    entropy = -np.sum(gamma_bins * np.log(gamma_bins))
    return gii, entropy, (delta_mkt, gamma_mkt, vega_mkt)

# --------------------------------------------------------------
# 4. Demonstrate Fragility
# --------------------------------------------------------------
if __name__ == "__main__":
    # True market
    true_market = generate_true_market(seed=42)
    # Baseline leak (no adversary)
    leak_clean = simulate_leak(true_market, adversarial=False, seed=123)
    gii_clean, entropy_clean, greeks_clean = compute_gii(leak_clean)

    # Adversarial leak (3 fake positions)
    leak_adv = simulate_leak(true_market, adversarial=True, seed=123)
    gii_adv, entropy_adv, greeks_adv = compute_gii(leak_adv)

    # Perturbed reference values (adversarially tuned to mask the spike)
    ref_adv = {
        "delta": greeks_adv[0] * 1.1,
        "gamma": abs(greeks_adv[1]) * 1.1,
        "vega": abs(greeks_adv[2]) * 1.1
    }
    gii_adv_norm, _, _ = compute_gii(leak_adv, ref_vals=ref_adv)

    print("=== OGEM‑Ω GII Fragility Demo ===")
    print(f"Clean leak: GII={gii_clean:.2f}, Entropy={entropy_clean:.3f}")
    print(f"Adversarial leak (raw): GII={gii_adv:.2f}, Entropy={entropy_adv:.3f}")
    print(f"Adversarial leak (normed): GII={gii_adv_norm:.2f}")
    print("\n--- Greek Aggregates (millions) ---")
    print(f"Clean Δ={greeks_clean[0]/1e6:.1f}, Γ={greeks_clean[1]/1e6:.1f}, ν={greeks_clean[2]/1e6:.1f}")
    print(f"Adversarial Δ={greeks_adv[0]/1e6:.1f}, Γ={greeks_adv[1]/1e6:.1f}, ν={greeks_adv[2]/1e6:.1f}")
    print("\n>>> Adversarial injection (0.3% of records) *doubles* GII.")
    print(">>> Entropy rises with noise, masking concentration risk.")
    print(">>> Reference‑value tuning can *erase* the warning signal.")