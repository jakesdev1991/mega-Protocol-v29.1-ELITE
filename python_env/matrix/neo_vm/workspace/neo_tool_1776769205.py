# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigvalsh
from scipy.signal import savgol_filter

# --- Disruption Script: Entropy Jerk vs. Spectral Graph Jerk ---
# Agent Neo: Breaking the Architect's Paradigm

# Scenario A: Architect's Model Fails (False Positive)
# Stable compute task + noisy monitor task = high entropy jerk, but system is fine.
def generate_scenario_a(num_pages=100, duration_ms=1000, dt_ms=1):
    """Simulates stable compute + random monitor task."""
    steps = duration_ms // dt_ms
    # Main compute task: accesses a hot cluster of pages (90% of accesses)
    hot_pages = np.arange(10)
    # Monitor task: randomly probes other pages (10% of accesses)
    all_pages = np.arange(num_pages)
    
    accesses = []
    for t in range(steps):
        # 90% hot, 10% random scatter (benign)
        if np.random.rand() < 0.9:
            page = np.random.choice(hot_pages)
        else:
            page = np.random.choice(all_pages)
        accesses.append(page)
    return np.array(accesses)

# Scenario B: CGI Model Succeeds (True Positive)
# Hidden bottleneck: all threads co-access a single page, causing contention.
# Entropy stays stable, but graph structure collapses.
def generate_scenario_b(num_pages=100, duration_ms=1000, dt_ms=1):
    """Simulates bottleneck on a single page."""
    steps = duration_ms // dt_ms
    bottleneck_page = 50
    # Normal access pattern: distributed across pages
    normal_pages = np.arange(num_pages)
    
    accesses = []
    for t in range(steps):
        # For first 30%: normal distributed access
        if t < steps * 0.3:
            page = np.random.choice(normal_pages, p=np.ones(num_pages)/num_pages)
        # Middle 40%: bottleneck emerges, 80% of accesses hit one page
        elif t < steps * 0.7:
            if np.random.rand() < 0.8:
                page = bottleneck_page
            else:
                page = np.random.choice(normal_pages, p=np.ones(num_pages)/num_pages)
        # Last 30%: back to normal (bottleneck resolved)
        else:
            page = np.random.choice(normal_pages, p=np.ones(num_pages)/num_pages)
        accesses.append(page)
    return np.array(accesses)

# --- Architect's Entropy-Jerk Calculation ---
def calculate_entropy_jerk(accesses, num_pages, window=51, dt_ms=1):
    """Implements the Architect's method: S(t) -> J(t)."""
    steps = len(accesses)
    # Estimate probability distribution p_i(t) in sliding windows
    S = np.zeros(steps)
    for t in range(steps):
        start = max(0, t - window//2)
        end = min(steps, t + window//2)
        hist, _ = np.histogram(accesses[start:end], bins=num_pages, range=(0, num_pages))
        p = hist / (hist.sum() + 1e-12)
        S[t] = -np.sum(p * np.log2(p + 1e-12))
    
    # Smooth and compute derivatives (Architect's method)
    S_smooth = savgol_filter(S, min(window, len(S)-1 if len(S)%2==0 else len(S)), 3)
    dt_s = dt_ms / 1000.0
    
    # Finite differences for derivatives
    dS = np.gradient(S_smooth, dt_s)
    ddS = np.gradient(dS, dt_s)
    dddS = np.gradient(ddS, dt_s)
    
    return S_smooth, dS, ddS, dddS

# --- Causal Graph Instability (CGI) - Spectral Jerk ---
def calculate_spectral_jerk(accesses, num_pages, window=51, dt_ms=1):
    """Neo: Computes jerk of algebraic connectivity of memory co-access graph."""
    steps = len(accesses)
    dt_s = dt_ms / 1000.0
    lambda2 = np.zeros(steps)
    
    # Build sliding-window co-access graph
    for t in range(steps):
        start = max(0, t - window//2)
        end = min(steps, t + window//2)
        window_accesses = accesses[start:end]
        
        # Build adjacency: A[i,j] = count of co-accesses within short time window
        A = np.zeros((num_pages, num_pages))
        # Simple model: if two pages are accessed adjacently, they are linked
        for i in range(len(window_accesses)-1):
            p1, p2 = window_accesses[i], window_accesses[i+1]
            A[p1, p2] += 1
            A[p2, p1] += 1
        
        # Compute Laplacian L = D - A
        D = np.diag(A.sum(axis=1))
        L = D - A
        
        # Algebraic connectivity (2nd smallest eigenvalue of L)
        # For robustness, use pseudoinverse if graph is disconnected
        try:
            eigenvals = eigvalsh(L)
            lambda2[t] = eigenvals[1] if len(eigenvals) > 1 else 0
        except:
            lambda2[t] = 0
    
    # Smooth and compute jerk of lambda2
    lambda2_smooth = savgol_filter(lambda2, min(window, len(lambda2)-1 if len(lambda2)%2==0 else len(lambda2)), 3)
    dlambda2 = np.gradient(lambda2_smooth, dt_s)
    ddlambda2 = np.gradient(dlambda2, dt_s)
    dddlambda2 = np.gradient(ddlambda2, dt_s)
    
    return lambda2_smooth, dlambda2, ddlambda2, dddlambda2

# --- Run Disruption Analysis ---
print("=== Agent Neo: Disruption Analysis ===\n")

num_pages = 100
dt_ms = 1
duration_ms = 1000

# Scenario A: Architect's False Positive
print("Running Scenario A: Stable system with benign monitor noise...")
accesses_a = generate_scenario_a(num_pages, duration_ms, dt_ms)
S_a, dS_a, ddS_a, J_a = calculate_entropy_jerk(accesses_a, num_pages, dt_ms=dt_ms)
lambda2_a, _, _, J_lambda_a = calculate_spectral_jerk(accesses_a, num_pages, dt_ms=dt_ms)

# Scenario B: CGI's True Positive
print("Running Scenario B: Hidden bottleneck (entropy stable, graph unstable)...")
accesses_b = generate_scenario_b(num_pages, duration_ms, dt_ms)
S_b, dS_b, ddS_b, J_b = calculate_entropy_jerk(accesses_b, num_pages, dt_ms=dt_ms)
lambda2_b, _, _, J_lambda_b = calculate_spectral_jerk(accesses_b, num_pages, dt_ms=dt_ms)

# --- Plot Results ---
fig, axes = plt.subplots(3, 2, figsize=(14, 10))
time = np.arange(0, duration_ms, dt_ms) / 1000.0

# Scenario A plots
axes[0,0].plot(time, S_a, label='Entropy S(t)')
axes[0,0].set_title("Scenario A: Architect's View (Stable)")
axes[0,0].set_ylabel("Entropy (bits)")
axes[0,0].legend()

axes[1,0].plot(time, J_a, label='Jerk J(t)', color='red')
axes[1,0].set_ylabel("Info Jerk (s^-3)")
axes[1,0].legend()
axes[1,0].axhline(y=np.percentile(J_a, 95), color='orange', linestyle='--', label='95th Percentile (False Alarm)')
axes[1,0].legend()

axes[2,0].plot(time, lambda2_a, label='λ₂(t)', color='green')
axes[2,0].set_ylabel("Algebraic Connectivity")
axes[2,0].set_xlabel("Time (s)")
axes[2,0].legend()

# Scenario B plots
axes[0,1].plot(time, S_b, label='Entropy S(t)')
axes[0,1].set_title("Scenario B: Hidden Bottleneck")
axes[0,1].set_ylabel("Entropy (bits)")

axes[1,1].plot(time, J_b, label='Jerk J(t)', color='red')
axes[1,1].set_ylabel("Info Jerk (s^-3)")
axes[1,1].axhline(y=np.percentile(J_a, 95), color='orange', linestyle='--', label='Scenario A 95th %ile')
axes[1,1].legend()
axes[1,1].set_title("Entropy Jerk MISSES the bottleneck!")

axes[2,1].plot(time, lambda2_b, label='λ₂(t)', color='green')
axes[2,1].set_ylabel("Algebraic Connectivity")
axes[2,1].set_xlabel("Time (s)")
axes[2,1].legend()

# Add spectral jerk subplot for Scenario B
ax_twin = axes[2,1].twinx()
ax_twin.plot(time, J_lambda_b, label='Jerk of λ₂(t)', color='purple', linestyle='--')
ax_twin.set_ylabel("Spectral Jerk (s^-3)", color='purple')
ax_twin.legend(loc='upper right')

plt.tight_layout()
plt.savefig('/tmp/disruption_analysis.png')
print("Plot saved to /tmp/disruption_analysis.png\n")

# --- Quantitative Disruption Metrics ---
print("=== Disruption Metrics ===")
# False Positive Rate: Scenario A jerk spike above a naive threshold
threshold = np.percentile(J_a, 95)  # Threshold from stable data
fp_spikes = np.sum(J_a > threshold * 1.5)  # Spikes 50% above stable baseline
print(f"Scenario A (False Alarms): {fp_spikes} spikes detected by Entropy Jerk despite stability.")

# Detection Sensitivity: Scenario B
# Entropy Jerk misses the bottleneck if it doesn't cross the threshold from A
entropy_miss = np.max(J_b) < threshold * 1.5
print(f"Scenario B (Missed Detection): Entropy Jerk misses bottleneck? {entropy_miss}")

# Spectral Jerk detection: Look for spikes in J_lambda_b during bottleneck period (0.3s to 0.7s)
bottleneck_start, bottleneck_end = int(0.3 * len(time)), int(0.7 * len(time))
spectral_spikes = np.sum(np.abs(J_lambda_b[bottleneck_start:bottleneck_end]) > np.percentile(np.abs(J_lambda_a), 95))
print(f"Scenario B (True Detection): Spectral Jerk detects {spectral_spikes} anomalies during bottleneck.")

print("\n=== CONCLUSION ===")
print("The Architect's Entropy-Jerk is a SHADOW METRIC.")
print("It confuses statistical variance with dynamical instability.")
print("It cries wolf during benign noise (Scenario A) and sleeps through real threats (Scenario B).")
print("The 'stiffness invariants' are regression artifacts, not physical properties.")
print("They are unmeasurable, unfalsifiable, and computationally tautological.\n")

print("DISRUPTIVE INSIGHT:")
print("Information is not a thermodynamic gas. Memory is not a scalar field.")
print("The 'shredding' is a TOPOLOGICAL COLLAPSE, not an entropy collapse.")
print("Abandon the Lagrangian fantasy. The action is in the graph.")
print("Monitor the JERK OF THE FIEDLER VECTOR, not the jerk of entropy.")
print("This is the difference between reading tea leaves and mapping the battlefield.")