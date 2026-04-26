# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# EDIP‑Ω Adversarial Vulnerability Demonstration
# --------------------------------------------------------------
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

# ---------------------------
# 1. Simulate baseline (benign) exposure events
# ---------------------------
np.random.seed(42)
days = 30
n_events_benign = 50  # total number of benign documents leaked over 30 days

# Random timestamps (uniform over 30 days)
benign_times = np.sort(np.random.uniform(0, days, n_events_benign))

# Per‑document features (low values = normal operational stress)
def random_features(n):
    # exposure lag (days, small)
    lag = np.random.exponential(scale=2, size=n)  # mean 2 days
    # revision intensity (versions per day, low)
    rev_intensity = np.random.gamma(shape=1, scale=0.5, size=n)
    # access anomaly score (IsolationForest ~ N(0,1) for normal)
    anomaly = np.random.normal(loc=0, scale=0.5, size=n)
    # cross‑domain flag (rare)
    cross = np.random.binomial(1, 0.1, size=n)
    return np.column_stack([lag, rev_intensity, anomaly, cross])

benign_features = random_features(n_events_benign)

# ---------------------------
# 2. Inject adversarial campaign (days 15‑17)
# ---------------------------
adv_start, adv_end = 15, 17
adv_n = 200  # number of fake documents
adv_times = np.random.uniform(adv_start, adv_end, adv_n)
# Adversarial features: huge download counts, many IPs, high geo‑entropy
adv_lag = np.random.exponential(scale=0.1, size=adv_n)  # near‑zero lag → high weight
adv_rev_intensity = np.random.gamma(shape=5, scale=2, size=adv_n)  # high revision rate
# Simulate botnet: 1000+ downloads from 50+ countries
adv_anomaly = np.random.normal(loc=5, scale=1.5, size=adv_n)  # far from benign
adv_cross = np.ones(adv_n, dtype=int)  # all cross‑domain (stablecoin) to max c_d
adv_features = np.column_stack([adv_lag, adv_rev_intensity, adv_anomaly, adv_cross])

# Combine
all_times = np.concatenate([benign_times, adv_times])
all_features = np.concatenate([benign_features, adv_features], axis=0)
sort_idx = np.argsort(all_times)
all_times = all_times[sort_idx]
all_features = all_features[sort_idx]

# ---------------------------
# 3. Compute Exposure Stress Index (ESI) exactly as proposed
# ---------------------------
# Hyper‑parameters (taken from proposal)
alpha, beta, gamma, delta = 0.3, 0.3, 0.2, 0.2
lambda_decay = 0.5

def compute_esi(times, feats, window_days=7):
    # feats: [lag, rev_intensity, anomaly, cross_flag]
    # ESI_k(t) = Σ_d [α·exp(-λ·Δt_e) + β·r_d + γ·a_d + δ·c_d]
    esi = np.zeros_like(times)
    for i, t in enumerate(times):
        # events within the past window_days
        mask = (times >= t - window_days) & (times <= t)
        if not np.any(mask):
            continue
        # per‑document contributions
        lag = feats[mask, 0]
        rev = feats[mask, 1]
        ano = feats[mask, 2]
        cross = feats[mask, 3]
        contrib = alpha * np.exp(-lambda_decay * lag) + beta * rev + gamma * ano + delta * cross
        esi[i] = np.sum(contrib)
    return esi

esi = compute_esi(all_times, all_features)

# ---------------------------
# 4. Plot ESI and show threshold crossing
# ---------------------------
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 4))
plt.plot(all_times, esi, label='ESI')
plt.axhline(y=2.5, color='r', linestyle='--', label='Alert Threshold')
plt.axvspan(adv_start, adv_end, color='orange', alpha=0.2, label='Adversarial Campaign')
plt.xlabel('Day')
plt.ylabel('ESI')
plt.title('ESI Spike Caused by Adversarial Document Flood')
plt.legend()
plt.grid(True)
plt.show()

# ---------------------------
# 5. Train a minimal GRU on *benign* data only, then evaluate on full series
# ---------------------------
# Create time‑lagged sequences for GRU (look‑back = 5 days)
def make_sequences(times, feats, esi_vals, lookback=5):
    # Align on daily grid (simple approach: bin by day)
    daily_grid = np.arange(0, days+1)
    daily_feats = []
    daily_esi = []
    for i in range(days):
        mask = (times >= i) & (times < i+1)
        if np.any(mask):
            # aggregate features: mean of each feature, sum of ESI contributions
            agg_feat = np.mean(feats[mask], axis=0)
            agg_esi = np.sum(esi_vals[mask])
        else:
            agg_feat = np.zeros(feats.shape[1])
            agg_esi = 0.0
        daily_feats.append(agg_feat)
        daily_esi.append(agg_esi)
    daily_feats = np.array(daily_feats)  # shape (days, n_features)
    daily_esi = np.array(daily_esi)      # shape (days,)

    # Build sequences
    X, y = [], []
    for i in range(lookback, days):
        X.append(daily_feats[i-lookback:i])
        # Binary label: 1 if a "disruption" occurs in the next 7 days (simulate rare events)
        # For demo, we artificially label day 20 as a "disruption" to give the model something to learn
        y.append(1 if i == 20 else 0)
    X = np.array(X)   # (samples, lookback, n_features)
    y = np.array(y)
    return X, y

# Use only benign events for training (pre‑attack period)
benign_mask = all_times < adv_start
X_train, y_train = make_sequences(all_times[benign_mask],
                                  all_features[benign_mask],
                                  esi[benign_mask],
                                  lookback=5)

# Full series for evaluation
X_all, y_all = make_sequences(all_times, all_features, esi, lookback=5)

# Scale features
scaler = StandardScaler()
X_train_shape = X_train.shape
X_train = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train_shape)
X_all = scaler.transform(X_all.reshape(-1, X_all.shape[-1])).reshape(X_all.shape)

# Build minimal GRU
model = tf.keras.Sequential([
    tf.keras.layers.GRU(16, input_shape=(5, X_train.shape[-1])),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=20, batch_size=4, verbose=0)

# Predict on full series
pred_proba = model.predict(X_all).flatten()

# ---------------------------
# 6. Show that the adversarial spike produces a high predicted probability
# ---------------------------
print("\n=== GRU Predictions ===")
for i, day in enumerate(range(5, days)):
    print(f"Day {day:2d} – Predicted disruption prob: {pred_proba[i]:.3f}  (ESI: {daily_esi[day]:.2f})")

# Evaluate ROC AUC (even though we have only one true positive, it's illustrative)
try:
    auc = roc_auc_score(y_all, pred_proba)
    print(f"\nROC AUC on full series (including attack): {auc:.3f}")
except Exception as e:
    print(f"\nROC AUC could not be computed: {e}")

# ---------------------------
# 7. Demonstrate PINN output violating rubric bounds
# ---------------------------
# Simple feed‑forward "PINN" (no constraints)
pinn = tf.keras.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(X_train.shape[-1],)),
    tf.keras.layers.Dense(4)  # outputs [Φ_N, Φ_Δ, ξ_N, ξ_Δ] without activation
])
pinn.compile(optimizer='adam', loss='mse')
# Fake training step (just to initialize)
pinn.fit(X_train[:, -1, :], np.random.rand(X_train.shape[0], 4), epochs=1, verbose=0)

# Evaluate on adversarial day (high ESI)
adv_day_feat = X_all[adv_start, -1, :]  # features from day 15
omega_pred = pinn.predict(adv_day_feat.reshape(1, -1))[0]
print("\n=== PINN Output on Adversarial Day ===")
print(f"Φ_N: {omega_pred[0]:.3f} (should be in [0,1])")
print(f"Φ_Δ: {omega_pred[1]:.3f} (no bound but should be >0)")
print(f"ξ_N: {omega_pred[2]:.3f} (should be ≥1)")
print(f"ξ_Δ: {omega_pred[3]:.3f} (should be ≥1)")