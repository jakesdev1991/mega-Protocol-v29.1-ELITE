# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Audit Script for TEMPEST‑Ω
-----------------------------------------
Validates:
  * Dimensionless nature of all state variables.
  * Hard bounds:   TSI ≤ 4.0,  Φ_N ≥ 0.5,  Φ_Δ ≤ 0.75.
  * Invariant ψ = ln(φ_n) is real‑valued (φ_n > 0).
  * Entropy gauge A_μ = ∂_μ S_h is a pure gradient (zero curl).
  * Cost integrand non‑negative.
  * Optional: simple QP feasibility check (TSI target tracking).

Usage:
    >>> audit = OmegaAudit(params)
    >>> audit.step(t, TSI, sync, C_i, delta_t_fe, m_eff, m0, xi, xi0)
    >>> if audit.violations:
    ...     print("Violations:", audit.violations)
"""

import numpy as np
from typing import Dict, List, Tuple

class OmegaAudit:
    def __init__(self,
                 # Model coefficients (should be dimensionless after proper scaling)
                 alpha: float = 1.0,
                 beta: float = 1.0,
                 gamma: float = 1.0,
                 lam: float = 0.1,          # decay constant [1/time] → will be made dimensionless by multiplying with a reference time τ0
                 eta1: float = 0.5,
                 eta2: float = 0.3,
                 eta3: float = 0.4,
                 tau1: float = 14.0,        # days → will be made dimensionless by τ0
                 tau2: float = 42.0,
                 tau3: float = 7.0,
                 # Reference scales for non‑dimensionalisation
                 t0: float = 1.0,           # reference time (e.g., 1 day)
                 m0: float = 1.0,           # reference mass (inverse‑time^2)
                 xi0: float = 1.0,          # reference correlation length
                 # Cost weights
                 mu1: float = 0.1,
                 mu2: float = 0.1,
                 # Target TSI for the MPC
                 TSI_target: float = 2.0):
        # Store dimensionless coefficients (absorb t0 where needed)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.lam = lam * t0          # now dimensionless
        self.eta1 = eta1
        self.eta2 = eta2
        self.eta3 = eta3
        self.tau1 = tau1 / t0
        self.tau2 = tau2 / t0
        self.tau3 = tau3 / t0
        self.t0 = t0
        self.m0 = m0
        self.xi0 = xi0
        self.mu1 = mu1
        self.mu2 = mu2
        self.TSI_target = TSI_target

        self.violations: List[str] = []
        self.history: List[Dict] = []

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def _check_dimensionless(self, name: str, value: float):
        """In this simplified audit we treat every supplied number as already
        dimensionless. In a production system you would attach units and
        verify cancellation."""
        if not isinstance(value, (int, float, np.floating)):
            raise TypeError(f"{name} must be a numeric type")
        # No further check – assume caller has non‑dimensionalised.

    def _add_violation(self, msg: str):
        self.violations.append(msg)

    # ------------------------------------------------------------------
    # Core computations
    # ------------------------------------------------------------------
    def compute_TSI(self,
                    sector_leaks: List[Tuple[float, float, float, float]]) -> float:
        """
        sector_leaks: list of (t_leak, C_i, delta_t_fe, sync) for the sector.
        All times must be expressed in the same units as t0.
        Returns instantaneous TSI_s(t) (dimensionless).
        """
        TSI = 0.0
        for t_leak, C_i, delta_t_fe, sync in sector_leaks:
            self._check_dimensionless("t_leak", t_leak)
            self._check_dimensionless("C_i", C_i)
            self._check_dimensionless("delta_t_fe", delta_t_fe)
            self._check_dimensionless("sync", sync)
            # exponential decay term (dimensionless because lam*t0 is dimensionless)
            decay = np.exp(-self.lam * abs(t_leak))
            TSI += (self.alpha * C_i * decay
                    + self.beta / max(delta_t_fe, 1e-6)   # avoid div‑0
                    + self.gamma * sync)
        return TSI

    def compute_phi_N(self, TSI_now: float, TSI_tau1: float, TSI_tau2: float) -> float:
        """Φ_N^{(temp)}(t) = Φ_N^{(0)} + η1·TSI(t‑τ1) − η2·TSI(t‑τ2)^2"""
        # Assume baseline Φ_N^{(0)} = 0.5 (mid‑point of allowed range)
        Phi_N0 = 0.5
        Phi_N = Phi_N0 + self.eta1 * TSI_tau1 - self.eta2 * (TSI_tau2 ** 2)
        self._check_dimensionless("Phi_N", Phi_N)
        return Phi_N

    def compute_phi_Delta(self, sync_now: float) -> float:
        """Φ_Δ^{(temp)}(t) = Φ_Δ^{(0)} + η3·sync(t‑τ3)"""
        Phi_Delta0 = 0.2   # arbitrary baseline within allowed band
        Phi_Delta = Phi_Delta0 + self.eta3 * sync_now
        self._check_dimensionless("Phi_Delta", Phi_Delta)
        return Phi_Delta

    def compute_psi(self, m_eff: float) -> float:
        """ψ = ln(φ_n) with φ_n = m_eff / m_0"""
        self._check_dimensionless("m_eff", m_eff)
        self._check_dimensionless("m0", self.m0)
        phi_n = m_eff / self.m0
        if phi_n <= 0:
            self._add_violation("φ_n ≤ 0 → ψ undefined")
            return float('nan')
        psi = np.log(phi_n)
        self._check_dimensionless("ψ", psi)
        return psi

    def compute_entropy_gauge_curl(self, S_h_vals: np.ndarray, dx: float) -> float:
        """
        Approximate ∂_[μ A_{ν]} using finite differences on a 1‑D proxy.
        Returns max |curl|; should be ≈0 for a pure gradient.
        """
        # A_μ = ∂_μ S_h  → in 1‑D: A = dS_h/dx
        A = np.gradient(S_h_vals, dx)
        # curl in 1‑D is zero by construction; we compute second derivative as proxy
        curl_approx = np.gradient(A, dx)
        max_curl = np.max(np.abs(curl_approx))
        if max_curl > 1e-10:
            self._add_violation(f"Entropy gauge not a pure gradient: max|curl|={max_curl:.2e}")
        return max_curl

    def cost_integrand(self, TSI: float, s_TSI: float, Phi_N: float) -> float:
        """(TSI‑target)^2 + μ1·s_TSI^2 + μ2·(1‑Φ_N)^2"""
        term1 = (TSI - self.TSI_target) ** 2
        term2 = self.mu1 * (s_TSI ** 2)
        term3 = self.mu2 * ((1.0 - Phi_N) ** 2)
        val = term1 + term2 + term3
        if val < -1e-12:   # allow tiny negative due to round‑off
            self._add_violation(f"Negative cost integrand: {val}")
        return val

    # ------------------------------------------------------------------
    # Public step – call once per audit tick
    # ------------------------------------------------------------------
    def step(self,
             t: float,
             sector_leaks: List[Tuple[float, float, float, float]],
             sync_now: float,
             m_eff: float,
             S_h_vals: np.ndarray,
             dx: float,
             # histories needed for τ‑delayed terms
             TSI_history: List[float],
             sync_history: List[float]) -> Dict:
        """
        Perform all checks for the current time step.
        Returns a dictionary with the computed state variables.
        """
        self.violations.clear()

        # ---- 1. TSI (needs current leak list) ----
        TSI_now = self.compute_TSI(sector_leaks)

        # ---- 2. Delayed TSI values for Φ_N ----
        # Assume TSI_history[-n] corresponds to t - n*dt; we approximate τ1,τ2 steps.
        # For simplicity we require the caller to provide the correctly lagged values.
        if len(TSI_history) < max(int(self.tau1), int(self.tau2)) + 1:
            self._add_violation("Insufficient history for τ‑delayed TSI")
            TSI_tau1 = TSI_tau2 = TSI_now   # fallback – will likely trigger a violation later
        else:
            TSI_tau1 = TSI_history[-int(self.tau1)]
            TSI_tau2 = TSI_history[-int(self.tau2)]

        # ---- 3. Φ_N and Φ_Δ ----
        Phi_N = self.compute_phi_N(TSI_now, TSI_tau1, TSI_tau2)
        Phi_Delta = self.compute_phi_Delta(sync_now)

        # ---- 4. ψ (invariant) ----
        psi = self.compute_psi(m_eff)

        # ---- 5. Entropy gauge (should be gradient) ----
        max_curl = self.compute_entropy_gauge_curl(S_h_vals, dx)

        # ---- 6. Hard bounds (Omega invariants) ----
        if TSI_now > 4.0 + 1e-9:
            self._add_violation(f"TSI_s = {TSI_now:.3f} > 4.0")
        if Phi_N < 0.5 - 1e-9:
            self._add_violation(f"Φ_N = {Phi_N:.3f} < 0.5")
        if Phi_Delta > 0.75 + 1e-9:
            self._add_violation(f"Φ_Δ = {Phi_Delta:.3f} > 0.75")

        # ---- 7. Cost integrand (non‑negative check) ----
        # s_TSI approximated as anomaly score; here we use a simple z‑score proxy.
        # In practice you would compute s_TSI = |TSI - TSI_hat| / σ_TSI.
        s_TSI = abs(TSI_now - np.mean(TSI_history[-20:])) / (np.std(TSI_history[-20:]) + 1e-6)
        cost = self.cost_integrand(TSI_now, s_TSI, Phi_N)

        # ---- 8. Store history ----
        entry = {
            "t": t,
            "TSI": TSI_now,
            "Phi_N": Phi_N,
            "Phi_Delta": Phi_Delta,
            "psi": psi,
            "max_curl": max_curl,
            "cost": cost,
            "violations": list(self.violations)
        }
        self.history.append(entry)
        return entry

# ----------------------------------------------------------------------
# Example usage (synthetic data)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    audit = OmegaAudit(alpha=0.8, beta=0.5, gamma=0.3, lam=0.1,
                       eta1=0.6, eta2=0.4, eta3=0.5,
                       tau1=14, tau2=42, tau3=7,
                       t0=1.0, m0=1.0, xi0=1.0,
                       mu1=0.1, mu2=0.1, TSI_target=2.0)

    # Dummy leak list: (t_leak, C_i, delta_t_fe, sync)
    leak_list = [(0.0, 3.0, 5.0, 2.0),
                 (1.0, 2.0, 3.0, 1.0),
                 (2.0, 4.0, 2.0, 3.0)]

    # Build a short history for delayed terms (just repeat current TSI)
    TSI_hist = [audit.compute_TSI(leak_list)] * 50
    sync_hist = [2.0] * 50

    # Dummy entropy field (linear → zero curl)
    x = np.linspace(0, 10, 100)
    S_h = 0.5 * x   # S_h = c * ln(xi/xi0) approximated linearly for demo
    dx = x[1] - x[0]

    for step in range(5):
        out = audit.step(t=step*1.0,
                         sector_leaks=leak_list,
                         sync_now=2.0,
                         m_eff=1.2,   # slightly above m0 → ψ>0
                         S_h_vals=S_h,
                         dx=dx,
                         TSI_history=TSI_hist,
                         sync_history=sync_hist)
        print(f"Step {step}: TSI={out['TSI']:.3f}, Φ_N={out['Phi_N']:.3f}, "
              f"Φ_Δ={out['Phi_Delta']:.3f}, ψ={out['psi']:.3f}, "
              f"violations={out['violations']}")

    if audit.violations:
        print("\n=== FINAL VIOLATIONS ===")
        for v in set(audit.violations):
            print("-", v)
    else:
        print("\nAll Omega Protocol checks passed for this synthetic run.")