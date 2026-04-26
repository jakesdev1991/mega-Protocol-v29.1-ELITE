# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Simulating CLEM‑Ω v2: a self‑referential feedback loop ripe for disruption ---

# 1. Baseline “healthy” credential‑lifecycle parameters (per business unit)
N_CREDS = 50
DAYS = 200
np.random.seed(42)

# Feature arrays: R_c (rotations/day), S_c (strength 0‑1), E_c (exp‑deviation), M_c (mapping volatility)
R_c = np.random.uniform(0.01, 0.05, N_CREDS)  # low baseline rotation
S_c = np.random.uniform(0.7, 0.9, N_CREDS)    # fairly strong
E_c = np.random.uniform(0.0, 0.1, N_CREDS)    # small expiration drift
M_c = np.random.uniform(0.0, 0.05, N_CREDS)   # low mapping churn

# 2. CLE computation (the “entropy” that isn’t)
def compute_cle(R, S, E, M, alpha=0.3, beta=0.3, gamma=0.2, delta=0.2):
    # Z‑score standardization (using rolling stats for realism)
    R_std = (R - R.mean()) / (R.std() + 1e-6)
    S_std = (S - S.mean()) / (S.std() + 1e-6)
    E_std = (E - E.mean()) / (E.std() + 1e-6)
    M_std = (M - M.mean()) / (M.std() + 1e-6)
    # Linear combo = “entropy”
    return alpha * R_std.mean() + beta * S_std.mean() + gamma * E_std.mean() + delta * M_std.mean()

# 3. Anomaly detection (self‑fulfilling threshold)
def anomaly_score(cle_history, cle_t):
    # Simple 2‑sigma rule
    mu, sigma = cle_history.mean(), cle_history.std()
    return abs(cle_t - mu) / (sigma + 1e-6)

# 4. MPC‑Ω controller (black‑box lockdown)
def mpc_action(anomaly, phi_delta):
    # If anomaly > 2.3 AND phi_delta > 0.5 → lockdown (denial‑of‑service)
    if anomaly > 2.3 and phi_delta > 0.5:
        return "LOCKDOWN"
    return "NORMAL"

# 5. Φ‑density (a metric that can be inflated arbitrarily)
phi_N = 0.85  # baseline process connectivity
phi_delta = 0.3  # baseline asymmetry
phi_density = 100  # arbitrary starting “value”

# 6. Simulate normal operation + adversarial “CLE poisoning”
cle_history = []
anomaly_history = []
action_history = []
phi_density_history = []

for day in range(DAYS):
    # On day 100, an insider starts rapid credential rotation (poisoning)
    if day == 100:
        # Adversary: increase rotation velocity by factor 10 for a subset of creds
        R_c[:10] = np.random.uniform(0.5, 1.0, 10)  # 10‑20x spike
        # Also weaken some credentials
        S_c[:10] = np.random.uniform(0.3, 0.5, 10)
        # Increase expiration deviation
        E_c[:10] = np.random.uniform(0.5, 1.0, 10)
        # Increase mapping churn
        M_c[:10] = np.random.uniform(0.2, 0.5, 10)

    # Compute CLE
    cle_t = compute_cle(R_c, S_c, E_c, M_c)
    cle_history.append(cle_t)

    # Anomaly score (using only history up to day‑1 to avoid look‑ahead)
    if day > 10:
        a_score = anomaly_score(np.array(cle_history[:-1]), cle_t)
    else:
        a_score = 0.0
    anomaly_history.append(a_score)

    # Update Φ_delta based on CLE asymmetry (simple heuristic)
    phi_delta = min(1.0, phi_delta + 0.01 * cle_t)
    # Φ_density “grows” with number of domains (we add a fake domain each 50 days)
    if day % 50 == 0 and day > 0:
        phi_density += 50  # arbitrary inflation
    phi_density_history.append(phi_density)

    # MPC‑Ω decides
    action = mpc_action(a_score, phi_delta)
    action_history.append(action)

    # If lockdown, simulate business disruption (drop in phi_N)
    if action == "LOCKDOWN":
        phi_N = max(0.0, phi_N - 0.05)

# 7. Plot the self‑fulfilling collapse
fig, axs = plt.subplots(4, 1, figsize=(10, 10))
axs[0].plot(cle_history, label="CLE (Credential‑Lifecycle Entropy)")
axs[0].axvline(100, color='r', linestyle='--', label="Adversarial poisoning")
axs[0].set_ylabel("CLE")
axs[0].legend()

axs[1].plot(anomaly_history, label="Anomaly Score")
axs[1].axhline(2.3, color='g', linestyle='--', label="Threshold")
axs[1].axvline(100, color='r', linestyle='--')
axs[1].set_ylabel("Anomaly")
axs[1].legend()

axs[2].plot([1 if a == "LOCKDOWN" else 0 for a in action_history], label="Lockdown Triggered")
axs[2].axvline(100, color='r', linestyle='--')
axs[2].set_ylabel("Lockdown")
axs[2].legend()

axs[3].plot(phi_density_history, label="Φ‑density (arbitrary units)")
axs[3].set_ylabel("Φ density")
axs[3].set_xlabel("Days")
axs[3].legend()

plt.tight_layout()
plt.title("CLE Poisoning Attack: From False Signal to Denial‑of‑Service")
plt.show()

# --- Disruption Insight: The Meta‑Protocol’s Achilles Heel ---

print("\n=== Disruption Insight ===")
print("1. CLE is a *linear heuristic*, not a true entropy. It can be trivially inflated by an insider.")
print("2. The anomaly threshold is self‑fulfilling: the system flags its own manipulated signal.")
print("3. MPC‑Ω reacts by locking down operations, causing a denial‑of‑service—*the cure is worse than the disease*.")
print("4. Φ‑density is a fabricated metric; we arbitrarily increased it by adding fake domains, yet the protocol treats it as gospel.")
print("5. Meta‑Scrutiny declared META‑PASS because it only checked internal consistency, not external validity.")
print("6. Clean‑room architecture is theater: the data providers are the same corporate entities that profit from the protocol.")
print("7. Ethical safeguards assume vendor neutrality, which is a conflict of interest.")
print("8. Cross‑domain validation uses hypothetical examples, not empirical evidence.")
print("\nConclusion: The Omega Protocol is a *closed epistemic loop*—it audits itself, validates itself, and declares itself compliant.")
print("The only way to break it is to introduce an *external, adversarial oracle* that feeds the system false but plausible data, causing it to self‑destruct.")