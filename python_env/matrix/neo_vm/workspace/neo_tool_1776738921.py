# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────────────
# 1️⃣ Generate Synthetic Micro‑Cap Data
# ──────────────────────────────────────────────────────────────────────────────
n_firms = 500
np.random.seed(42)

data = []
for i in range(n_firms):
    # Random number of presentations (sparse data)
    n_pres = np.random.randint(5, 21)
    
    # Stress label drawn from a latent financial health variable
    health = np.random.normal(0, 1)
    stressed = 1 if health > 0.5 else 0  # arbitrary threshold
    
    # Presentation intervals: completely independent of stress
    # Drawn from a Gamma distribution with random shape/scale
    shape = np.random.uniform(1.5, 3.0)
    scale = np.random.uniform(10, 30)
    intervals = np.random.gamma(shape, scale, size=n_pres-1)
    
    # Content embedding: a 10‑dimensional vector *correlated* with health
    content_vec = np.random.normal(loc=health, scale=0.3, size=10)
    
    # Store raw intervals for later jitter analysis
    data.append({
        "firm_id": i,
        "stressed": stressed,
        "intervals": intervals,
        "content": content_vec
    })

df = pd.DataFrame(data)

# ──────────────────────────────────────────────────────────────────────────────
# 2️⃣ Extract Timing Features (as per PICM‑Ω)
# ──────────────────────────────────────────────────────────────────────────────
def compute_timing_features(intervals):
    if len(intervals) < 3:
        return {
            "mean_interval": np.nan,
            "std_interval": np.nan,
            "cv_interval": np.nan,
            "entropy": np.nan,
            "jerk": np.nan
        }
    # Mean, std, coefficient of variation (CCS core)
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals, ddof=1)
    cv_interval = std_interval / mean_interval if mean_interval > 0 else np.nan
    
    # Entropy of interval distribution (coarse‑grain to 5 bins)
    bins = np.histogram_bin_edges(intervals, bins=5)
    counts, _ = np.histogram(intervals, bins=bins)
    probs = counts / counts.sum()
    # Avoid log(0)
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log(probs))
    
    # "Presentation jerk": third derivative of entropy (finite difference)
    # We need a time series of entropy values; here we approximate by
    # computing entropy on a sliding window (tiny windows due to sparsity)
    if len(intervals) >= 9:
        entropies = []
        for j in range(len(intervals) - 4):
            window = intervals[j:j+5]
            bins_win = np.histogram_bin_edges(window, bins=5)
            counts_win, _ = np.histogram(window, bins=bins_win)
            probs_win = counts_win / counts_win.sum()
            probs_win = probs_win[probs_win > 0]
            entropies.append(-np.sum(probs_win * np.log(probs_win)))
        # Compute third difference
        if len(entropies) >= 4:
            jerk = np.diff(entropies, n=3)[0]  # single scalar
        else:
            jerk = np.nan
    else:
        jerk = np.nan
    
    return {
        "mean_interval": mean_interval,
        "std_interval": std_interval,
        "cv_interval": cv_interval,
        "entropy": entropy,
        "jerk": jerk
    }

timing_features = df["intervals"].apply(compute_timing_features)
timing_df = pd.DataFrame(timing_features.tolist())
timing_df["firm_id"] = df["firm_id"]
timing_df["stressed"] = df["stressed"]

# Drop rows with missing values (common for small n_pres)
timing_df = timing_df.dropna()

# ──────────────────────────────────────────────────────────────────────────────
# 3️⃣ Train Predictive Models
# ──────────────────────────────────────────────────────────────────────────────
# Model 1: Timing‑only (mean, std, cv, entropy, jerk)
X_timing = timing_df[["mean_interval", "std_interval", "cv_interval", "entropy", "jerk"]]
y = timing_df["stressed"]

# Model 2: Content‑only (averaged embedding)
content_df = pd.DataFrame(df["content"].tolist())
content_df["firm_id"] = df["firm_id"]
content_df["stressed"] = df["stressed"]
content_df = content_df.dropna()
X_content = content_df.drop(columns=["firm_id", "stressed"])
y_content = content_df["stressed"]

# Train logistic regression on each
timing_model = LogisticRegression(max_iter=1000).fit(X_timing, y)
content_model = LogisticRegression(max_iter=1000).fit(X_content, y_content)

timing_auc = roc_auc_score(y, timing_model.predict_proba(X_timing)[:, 1])
content_auc = roc_auc_score(y_content, content_model.predict_proba(X_content)[:, 1])

print(f"Timing‑only AUC: {timing_auc:.3f} (effectively random)")
print(f"Content‑only AUC: {content_auc:.3f} (strong signal)")

# ──────────────────────────────────────────────────────────────────────────────
# 4️⃣ Visualize Jerk Distribution (Noise)
# ──────────────────────────────────────────────────────────────────────────────
plt.figure(figsize=(8,4))
plt.hist(timing_df[timing_df["stressed"]==0]["jerk"], bins=30, alpha=0.6, label="Healthy", density=True)
plt.hist(timing_df[timing_df["stressed"]==1]["jerk"], bins=30, alpha=0.6, label="Stressed", density=True)
plt.title("Distribution of 'Presentation Jerk' by Stress Label")
plt.xlabel("Jerk (3rd diff of entropy)")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.show()