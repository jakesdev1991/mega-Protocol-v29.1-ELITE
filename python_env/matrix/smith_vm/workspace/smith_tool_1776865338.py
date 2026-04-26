# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Strict validation of the refined Cognitive Flow Integrity Shield (CFIS-Ω)
against Omega Protocol invariants.

Assumptions (consistent with the refined proposal):
- Spatial dimension reduced to a single point (homogeneous field) → ∇²F = 0.
- Distraction gradient ∇Φ_Δ is approximated by a scalar difference ΔΦ_Δ = Φ_Δ(t) - Φ_Δ(t-1).
- Coupling term taken as γ * F * ΔΦ_Δ (scalar‑times‑scalar, added to RHS).
- Double‑well potential V(F) = (λ/4)*(F² - F_opt²)² → restoring force -dV/dF = -λ*(F³ - F_opt²*F).
"""

import numpy as np

# ----------------------------------------------------------------------
# Parameters (chosen to reflect realistic ranges; can be tuned)
# ----------------------------------------------------------------------
D      = 0.1   # diffusion coefficient (irrelevant for homogeneous case)
lam    = 1.0   # nonlinearity strength
F_opt  = 1.0   # optimal flow field value (normalised)
gamma  = 0.05  # coupling strength to distraction gradient
eta_std= 0.02  # std. dev. of stochastic noise η(x,t)
A      = 0.0   # baseline attenuation (set to zero for simplicity)

# Omega‑Protocol invariant thresholds
CFI_MIN   = 0.85
PHIN_MIN  = 0.8
S_MIN     = np.log(2)   # ≈0.6931

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def tanh(x): return np.tanh(x)

def compute_CFI(engagement, PhiN_flow, PhiDelta_flow,
                alpha=1.0, beta=1.0, gamma_=1.0):
    """CFI(t) = tanh[α·Engagement + β·Φ_N^{(flow)} - γ·Φ_Δ^{(flow)}]"""
    return tanh(alpha*engagement + beta*PhiN_flow - gamma_*PhiDelta_flow)

def PhiN_flow_update(PhiN0, CFI_prev, S_flow, eta1=0.3, eta2=0.2, tau=1):
    """
    Φ_N^{(flow)}(t) = Φ_N^{(0)} - η₁·(1 - CFI(t-τ)) + η₂·S_flow(t-τ)
    """
    return PhiN0 - eta1*(1.0 - CFI_prev) + eta2*S_flow

def psi_flow(Persistence1, Persistence0=1.0):
    """ψ_flow(t) = ln( Persistence₁(t) / Persistence₀ )"""
    if Persistence1 <= 0:
        raise ValueError("Persistence₁ must be > 0 for log.")
    return np.log(Persistence1 / Persistence0)

def field_equation(F, F_prev, DeltaPhiDelta, dt=0.1):
    """
    ∂_t F = D∇²F - λ(F³ - F_opt²·F) + η - A + γ·F·ΔΦ_Δ
    (homogeneous → ∇²F = 0)
    """
    # stochastic term
    eta = np.random.normal(0, eta_std)
    # restoring force from double‑well potential
    restoring = -lam * (F**3 - F_opt**2 * F)
    # coupling term (scalar × scalar)
    coupling = gamma * F * DeltaPhiDelta
    dF = restoring + eta - A + coupling
    return F + dF*dt   # Euler step

def simulate(T=200, dt=0.1):
    """
    Run a time‑domain simulation and verify Omega invariants at each step.
    Returns True if no violation occurs.
    """
    steps = int(T/dt)
    # Initial conditions
    F      = F_opt          # start at optimal flow
    F_prev = F_opt
    PhiN0  = 1.0            # baseline Φ_N
    S_flow = S_MIN + 0.2    # start comfortably above threshold
    Persistence1 = 1.0
    engagement   = 0.6      # moderate baseline engagement
    PhiDelta_flow = 0.2     # baseline distraction

    for i in range(steps):
        t = i*dt

        # ---- 1. Update field F (cubic double‑well + coupling) ----
        DeltaPhiDelta = PhiDelta_flow - (PhiDelta_flow if i==0 else PhiDelta_flow_hist[-1])
        F_new = field_equation(F, F_prev, DeltaPhiDelta, dt)
        F_prev, F = F, F_new

        # ---- 2. Update Ω‑variables (using lagged CFI) ----
        if i == 0:
            CFI_lag = compute_CFI(engagement, PhiN0, PhiDelta_flow)
        else:
            CFI_lag = CFI_hist[-1]

        PhiN_flow = PhiN_flow_update(PhiN0, CFI_lag, S_flow)
        # Simple dynamics for distraction and persistence (can be refined)
        PhiDelta_flow = np.clip(PhiDelta_flow + 0.01*np.random.randn(), 0.0, 0.5)
        Persistence1  = np.clip(Persistence1 + 0.005*np.random.randn(), 0.5, 2.0)

        # ---- 3. Compute CFI (current) ----
        CFI = compute_CFI(engagement, PhiN_flow, PhiDelta_flow)

        # ---- 4. Compute ψ_flow ----
        psi = psi_flow(Persistence1)

        # ---- 5. Invariant checks (Omega Protocol) ----
        if CFI < CFI_MIN:
            raise AssertionError(f"CFI invariant violated at t={t:.2f}: CFI={CFI:.3f} < {CFI_MIN}")
        if PhiN_flow < PHIN_MIN:
            raise AssertionError(f"Φ_N^{(flow)} invariant violated at t={t:.2f}: Φ_N={PhiN_flow:.3f} < {PHIN_MIN}")
        if S_flow < S_MIN:
            raise AssertionError(f"S_flow invariant violated at t={t:.2f}: S_flow={S_flow:.3f} < {S_MIN:.3f}")
        # ψ_flow must be real – already guaranteed by psi_flow guard

        # ---- 6. Store history for next step ----
        CFI_hist.append(CFI)
        PhiDelta_flow_hist.append(PhiDelta_flow)

    return True

# ----------------------------------------------------------------------
# Run validation
# ----------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)   # reproducibility
    CFI_hist = []
    PhiDelta_flow_hist = []
    try:
        if simulate():
            print("[VALIDATION PASSED] All Omega Protocol invariants satisfied "
                  "throughout the simulation.")
    except AssertionError as e:
        print("[VALIDATION FAILED]", e)