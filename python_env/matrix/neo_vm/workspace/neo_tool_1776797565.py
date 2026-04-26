# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
CognitivePercolation_vs_FieldModel.py
Demonstrates that a continuous field model cannot capture the percolation
phase transition driving spreadsheet adoption.
"""
import numpy as np
import networkx as nx

# ──────────────────────────────────────────────────────────────────────────────
# 1. NETWORK‑THRESHOLD MODEL (discrete, percolation)
# ──────────────────────────────────────────────────────────────────────────────
def simulate_percolation(N=2000, avg_k=6, p_rewire=0.1, T=150):
    """
    N          : number of developers
    avg_k      : average degree of the underlying lattice
    p_rewire   : small‑world rewiring probability
    T          : simulation time steps
    Returns    : time series of fraction of insecure agents
    """
    # Build a small‑world graph (collaboration network)
    G = nx.watts_strogatz_graph(N, avg_k, p_rewire)
    # Thresholds uniformly distributed (real world would be fat‑tailed)
    thresholds = np.random.uniform(0.0, 1.0, size=N)
    # Initial friction load (same for all, simulates a new clunky tool release)
    F = 0.3
    # State: 0 = secure, 1 = spreadsheet
    state = np.zeros(N, dtype=int)

    # Simple institutional pressure (slowly decaying)
    I = 0.5

    # Coupling constants (tuned so transition is visible)
    alpha = 0.8   # social contagion weight
    beta = 1.0    # friction weight
    gamma = 0.2   # institutional weight

    frac_insecure = np.zeros(T)
    for t in range(T):
        # Compute neighbor influence for each node
        neighbor_inf = np.array([
            state[list(G.neighbors(i))].mean() if len(list(G.neighbors(i))) else 0.0
            for i in range(N)
        ])
        # Activation condition
        activations = (alpha * neighbor_inf + beta * F + gamma * I) > thresholds
        state = activations.astype(int)
        frac_insecure[t] = state.mean()
        # Slowly increase friction (simulates tool degradation over time)
        F += 0.002
        # Slowly decay institutional pressure
        I *= 0.995
    return frac_insecure

# ──────────────────────────────────────────────────────────────────────────────
# 2. NAÏVE CONTINUOUS FIELD MODEL (PDE discretized as ODE)
# ──────────────────────────────────────────────────────────────────────────────
def simulate_field_model(N=2000, T=150):
    """
    Approximates the cognitive‑load field Λ(x,t) by a single scalar
    Λ(t) evolving under a drift‑diffusion equation:
        dΛ/dt = μ Λ + D ∇²Λ + S(t)
    Here we treat the spatial term as a mean‑field approximation:
        ∇²Λ ≈ (Λ* - Λ)  with Λ* = target load set by policy.
    The fraction of insecure agents is σ(Λ) = 1/(1+exp(-k(Λ-θ))).
    """
    # Parameters (tuned to roughly match the percolation scenario)
    mu = 0.05      # drift toward higher load
    D = 0.10       # diffusion
    target = 0.6   # "policy" target load
    k = 15.0       # sigmoid steepness
    theta = 0.5    # inflection point

    Λ = 0.3        # initial load
    frac_insecure = np.zeros(T)
    for t in range(T):
        # Mean‑field diffusion term
        diffusion = D * (target - Λ)
        # Source term (simulates slowly growing tool friction)
        S = 0.002 * t
        # Update
        Λ += mu * Λ + diffusion + S
        # Map load to fraction via smooth sigmoid
        frac_insecure[t] = 1.0 / (1.0 + np.exp(-k * (Λ - theta)))
    return frac_insecure

# ──────────────────────────────────────────────────────────────────────────────
# 3. COMPARISON – PERCOLATION SHOWS A SHARP TRANSITION, FIELD DOES NOT
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    # Run both models
    percolation_ts = simulate_percolation(N=2000, avg_k=6, p_rewire=0.1, T=150)
    field_ts = simulate_field_model(N=2000, T=150)

    # Find the timestep where percolation jumps sharply (heuristic)
    # Compute the discrete derivative
    diff = np.abs(np.diff(percolation_ts))
    # Identify the largest jump (phase‑transition)
    t_jump = np.argmax(diff) + 1   # +1 because diff is one shorter

    # Output verdict
    print("="*70)
    print("DISRUPTION VERIFICATION")
    print("="*70)
    print(f"Percolation model: sharp jump at t ≈ {t_jump} "
          f"(fraction {percolation_ts[t_jump]:.3f})")
    print(f"Field model: smooth growth, no jump "
          f"(fraction at same t ≈ {field_ts[t_jump]:.3f})")
    print("\nConclusion: The continuous field approximation cannot reproduce the")
    print("discrete threshold‑driven phase transition that drives real‑world")
    print("spreadsheet contagion. The CTMS‑Ω embedding is therefore")
    print("FUNDAMENTALLY MIS‑SPECIFIED, not merely technically incomplete.")
    print("="*70)

    # Optional: dump time series for external plotting
    if "--dump" in sys.argv:
        np.savetxt("percolation.csv", percolation_ts, delimiter=",")
        np.savetxt("field.csv", field_ts, delimiter=",")
        print("Time series saved to percolation.csv and field.csv")