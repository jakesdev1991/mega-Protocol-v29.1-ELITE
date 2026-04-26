# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validation for PDSD-Ω (Protected Document Semantic Drift Analysis)
# --------------------------------------------------------------
import numpy as np
import pandas as pd

# ----- Helper functions -------------------------------------------------
def sci_from_features(A, C, G, RV, w):
    """
    Compute Semantic Coherence Index.
    A, C, G, RV: arrays (same shape) of feature values in [0,1].
    w: length-4 array of non‑negative weights that sum to 1.
    """
    term = w[0] * (1 - A) + w[1] * (1 - C) + w[2] * G + w[3] * np.exp(-RV)
    return np.clip(term, 0.0, 1.0)   # safety clamp

def phi_N_sem(SCI_bar, PhiN0, alpha):
    """Map smoothed SCI to process connectivity."""
    return PhiN0 * np.tanh(alpha * SCI_bar)

def phi_Delta_sem(C_bar, PhiDelta0, beta, clip=True):
    """Map smoothed contradiction density to asymmetry."""
    val = PhiDelta0 + beta * C_bar
    if clip:
        val = np.clip(val, 0.0, 1.0)   # enforce Omega invariant ΦΔ∈[0,1]
    return val

def stl_detrend(series, period=4):
    """
    Very simple STL‑like detrend: subtract a moving‑average of length `period`.
    Returns residual and its std.
    """
    if len(series) < period:
        raise ValueError("Series too short for chosen period")
    trend = pd.Series(series).rolling(window=period, center=True).mean().bfill().ffill()
    residual = series - trend
    sigma = np.std(residual)
    return residual, sigma

def anomaly_score(residual, sigma):
    """Absolute residual normalized by std."""
    return np.abs(residual) / (sigma + 1e-12)

# ----- Synthetic data generation ----------------------------------------
np.random.seed(42)
T = 52  # weeks of observation
# Features in [0,1] with some drift to simulate stress
A = np.clip(0.2 + 0.01*np.arange(T) + 0.05*np.random.randn(T), 0, 1)
C = np.clip(0.1 + 0.015*np.arange(T) + 0.04*np.random.randn(T), 0, 1)
G = np.clip(0.8 - 0.008*np.arange(T) + 0.03*np.random.randn(T), 0, 1)
RV = np.clip(0.5 - 0.005*np.arange(T) + 0.02*np.random.randn(T), 0, 1)  # revision velocity

# Weights (must sum to 1)
w = np.array([0.25, 0.25, 0.25, 0.25])

# ----- Compute SCI -------------------------------------------------------
SCI = sci_from_features(A, C, G, RV, w)

# Smoothing for mapping (simple exponential moving average)
alpha_ema = 0.3
SCI_smooth = np.zeros_like(SCI)
C_smooth  = np.zeros_like(C)
SCI_smooth[0] = SCI[0]
C_smooth[0]   = C[0]
for t in range(1, T):
    SCI_smooth[t] = alpha_ema*SCI[t] + (1-alpha_ema)*SCI_smooth[t-1]
    C_smooth[t]   = alpha_ema*C[t]   + (1-alpha_ema)*C_smooth[t-1]

# ----- Omega variable mapping --------------------------------------------
PhiN0 = 0.8   # baseline process connectivity
PhiDelta0 = 0.2
alpha = 2.0   # SCI → ΦN sensitivity
beta  = 0.3   # contradiction → ΦΔ sensitivity

PhiN_sem   = phi_N_sem(SCI_smooth, PhiN0, alpha)
PhiDelta_sem = phi_Delta_sem(C_smooth, PhiDelta0, beta, clip=True)

# ----- Anomaly detection (STL‑like) --------------------------------------
residual, sigma = stl_detrend(SCI, period=4)
s_SCI = anomaly_score(residual, sigma)

risk_flag = (s_SCI > 2.3) & (PhiDelta_sem > 0.5)

# ----- Constraint checking -----------------------------------------------
constraints = {
    "SCI >= 0.6": np.all(SCI >= 0.6),
    "ΦN_sem >= 0.7": np.all(PhiN_sem >= 0.7),
    "ΦΔ_sem <= 0.55": np.all(PhiDelta_sem <= 0.55),
}

# ----- Cost function (for illustration) ---------------------------------
lam = 0.5
cost = -np.log(SCI + 1e-12) + lam * s_SCI
avg_cost = np.mean(cost)

# ----- Reporting ---------------------------------------------------------
print("=== Semantic Feature Statistics ===")
print(f"A mean: {A.mean():.3f}, C mean: {C.mean():.3f}, G mean: {G.mean():.3f}, RV mean: {RV.mean():.3f}")
print()
print("=== Derived Quantities (averaged) ===")
print(f"SCI mean: {SCI.mean():.3f}")
print(f"ΦN_sem mean: {PhiN_sem.mean():.3f}")
print(f"ΦΔ_sem mean: {PhiDelta_sem.mean():.3f}")
print(f"Anomaly score mean: {s_SCI.mean():.3f}, max: {s_SCI.max():.3f}")
print()
print("=== Constraint Satisfaction ===")
for name, ok in constraints.items():
    print(f"{name}: {'PASS' if ok else 'FAIL'}")
print()
print(f"Average cost (−log(SCI)+λ·s): {avg_cost:.3f}")
print()
print("=== Risk Flags (weeks where both conditions true) ===")
risk_weeks = np.where(risk_flag)[0]
if len(risk_weeks) == 0:
    print("No risk weeks detected.")
else:
    print(f"Risk weeks (0‑indexed): {risk_weeks.tolist()}")