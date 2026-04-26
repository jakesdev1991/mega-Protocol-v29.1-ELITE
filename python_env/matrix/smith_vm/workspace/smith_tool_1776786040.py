# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol compliance validator for the SearXNG‑connection‑error insight.
Author: Agent Smith (Matrix Guardian)
"""

import numpy as np

# ------------------------------
# 1. Synthetic data generation
# ------------------------------
def generate_connectivity(t, t_fault, tau_net, depth=1.0):
    """
    C(t) = 1 before fault, then drops to (1-depth) and recovers exponentially.
    depth=1 => full drop to 0.
    """
    C = np.ones_like(t)
    fault_idx = t >= t_fault
    C[fault_idx] = 1.0 - depth * (1 - np.exp(-(t[fault_idx] - t_fault) / tau_net))
    return C

# ------------------------------
# 2. Helper functions for derived quantities
# ------------------------------
def compute_phi_N(C):
    """Spatial average – with a single‑point model Φ_N = C."""
    return C.copy()

def compute_phi_Delta(C, dx=1.0):
    """
    Approximate Φ_Δ ≈ <(∇C)²>.
    Using finite difference: ∇C ≈ (C[i+1]-C[i-1])/(2dx).
    """
    grad = np.zeros_like(C)
    grad[1:-1] = (C[2:] - C[:-2]) / (2 * dx)
    # boundaries: forward/backward diff
    grad[0]   = (C[1] - C[0]) / dx
    grad[-1]  = (C[-1] - C[-2]) / dx
    return grad**2  # pointwise; spatial mean later

def effective_potential(phi_N, phi_Delta, k_N=1.0, k_Delta=1.0):
    """Quasi‑harmonic effective potential V_eff = ½ k_N Φ_N² + ½ k_Δ Φ_Δ²."""
    return 0.5 * k_N * phi_N**2 + 0.5 * k_Delta * phi_Delta**2

def stiffness_invariants(phi_N, phi_Delta, k_N=1.0, k_Delta=1.0):
    """
    For V_eff = ½ k_N Φ_N² + ½ k_Δ Φ_Δ²,
    ∂²V_eff/∂Φ_N² = k_N,  ∂²V_eff/∂Φ_Δ² = k_Δ.
    Hence ξ_N = 1/k_N, ξ_Δ = 1/k_Δ.
    """
    xi_N = 1.0 / k_N
    xi_Delta = 1.0 / k_Delta
    return xi_N, xi_Delta

def correlation_length(xi_N, xi_Delta):
    """ξ = 1/√(ξ_N⁻² + ξ_Δ⁻²)  (as defined in the insight)."""
    return 1.0 / np.sqrt(1.0/xi_N**2 + 1.0/xi_Delta**2)

def compute_psi(xi, xi0):
    """ψ = ln(ξ/ξ₀)."""
    return np.log(xi / xi0)

def compute_jerk(C, dt):
    """Third derivative using numpy.gradient repeatedly."""
    dC = np.gradient(C, dt)
    d2C = np.gradient(dC, dt)
    d3C = np.gradient(d2C, dt)
    return d3C

# ------------------------------
# 3. Validation routine
# ------------------------------
def validate_insight():
    # Simulation parameters
    t_total = 30.0          # seconds
    dt = 0.01               # time step
    t = np.arange(0, t_total, dt)
    tau_net = 0.5           # average network latency (s)
    t_fault = 10.0          # moment the SearXNG error occurs
    depth = 1.0             # full drop to zero

    # Generate C(t)
    C = generate_connectivity(t, t_fault, tau_net, depth)

    # Derived fields
    phi_N = compute_phi_N(C)
    phi_Delta_pt = compute_phi_Delta(C, dx=1.0)   # pointwise
    phi_Delta = np.mean(phi_Delta_pt)            # spatial average (single point → mean)

    # Effective potential & stiffness
    xi_N, xi_Delta = stiffness_invariants(phi_N[-1], phi_Delta)  # use final values as representative
    xi0 = 1.0 / np.sqrt(1.0/xi_N**2 + 1.0/xi_Delta**2)
    xi_t = correlation_length(xi_N, xi_Delta)   # constant in this simple model
    psi = compute_psi(xi_t, xi0)

    # Jerk and normalized jerk
    j_C = compute_jerk(C, dt)
    jhat_C = j_C * tau_net**3

    # Controller thresholds
    PSI_FREEZE = -1.5
    JHAT_THRESH = 5.0   # arbitrary but reasonable dimensionless threshold

    # Determine trigger times
    trigger_psi = np.where(psi < PSI_FREEZE)[0]
    trigger_jhat = np.where(np.abs(jhat_C) > JHAT_THRESH)[0]
    trigger_times = np.unique(np.concatenate([trigger_psi, trigger_jhat]))

    # Fault detection latency: first trigger after t_fault
    if trigger_times.size > 0:
        first_trigger_idx = trigger_times[trigger_times * dt >= t_fault][0] if np.any(trigger_times * dt >= t_fault) else None
        latency = (first_trigger_idx * dt - t_fault) if first_trigger_idx is not None else np.inf
    else:
        latency = np.inf

    # ------------------------------
    # 4. Reporting
    # ------------------------------
    print("=== Omega Protocol Validation Report ===")
    print(f"Simulation length: {t_total}s, dt={dt}s")
    print(f"Network latency τ_net = {tau_net}s")
    print(f"Fault injected at t = {t_fault}s (C→0)")
    print()
    print("Derived constants (representative):")
    print(f"  Φ_N (final)   = {phi_N[-1]:.4f}")
    print(f"  Φ_Δ (mean)    = {phi_Delta:.4f}")
    print(f"  ξ_N           = {xi_N:.4f}")
    print(f"  ξ_Δ           = {xi_Delta:.4f}")
    print(f"  ξ₀            = {xi0:.4f}")
    print(f"  ξ(t)          = {xi_t:.4f}")
    print(f"  ψ(t)          = {psi:.4f}  (constant in this toy model)")
    print()
    print("Jerk analysis:")
    print(f"  max|j_C|      = {np.max(np.abs(j_C)):.3e}  1/s³")
    print(f"  max|ĵ_C|      = {np.max(np.abs(jhat_C)):.3e}  (dimensionless)")
    print()
    print("Trigger evaluation:")
    print(f"  ψ < -1.5 ?    = {np.any(psi < PSI_FREEZE)}")
    print(f"  |ĵ_C| > {JHAT_THRESH} ? = {np.any(np.abs(jhat_C) > JHAT_THRESH)}")
    if trigger_times.size > 0:
        print(f"  First trigger index = {trigger_times[0]} (t = {trigger_times[0]*dt:.3f}s)")
        print(f"  Detection latency   = {latency:.3f}s")
        print(f"  Required ≤ τ_net/2 = {tau_net/2:.3f}s → {'PASS' if latency <= tau_net/2 else 'FAIL'}")
    else:
        print("  No trigger detected → FAIL (controller silent)")
    print()
    # Overall compliance
    compliance = (
        latency <= tau_net/2 and
        (np.any(psi < PSI_FREEZE) or np.any(np.abs(jhat_C) > JHAT_THRESH))
    )
    print("=== OVERALL RESULT: {} ===".format("PASS (compliant)" if compliance else "FAIL (non‑compliant)"))
    return compliance

if __name__ == "__main__":
    validate_insight()