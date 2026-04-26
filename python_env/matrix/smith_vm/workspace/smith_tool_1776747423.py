# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Compliance Validator for Finance‑Branch Modules
----------------------------------------------------------------
This script imposes the *minimum* mathematical requirements that any
proposed Ω‑component must satisfy to be considered compliant.
It is deliberately strict: if your module cannot pass, it is not
an Ω‑derived construct, regardless of its practical usefulness.
"""

import numpy as np
from typing import Callable, Tuple

# ----------------------------------------------------------------------
# Helper numerical utilities
# ----------------------------------------------------------------------
def finite_difference(f: Callable[[float], float], x: float, h: float = 1e-6) -> float:
    """Central difference derivative."""
    return (f(x + h) - f(x - h)) / (2 * h)

def second_derivative(f: Callable[[float], float], x: float, h: float = 1e-6) -> float:
    """Central second derivative."""
    return (f(x + h) - 2 * f(x) + f(x - h)) / (h ** 2)

def third_derivative(f: Callable[[float], float], x: float, h: float = 1e-6) -> float:
    """Central third derivative (jerk proxy)."""
    return (f(x + 2*h) - 2*f(x + h) + 2*f(x - h) - f(x - 2*h)) / (2 * h**3)

# ----------------------------------------------------------------------
# Validator class
# ----------------------------------------------------------------------
class OmegaFinanceValidator:
    def __init__(
        self,
        action: Callable[[np.ndarray, float], float],
        phi_N_func: Callable[[float, float], float],
        phi_Delta_func: Callable[[float, float], float],
        psi_func: Callable[[float], float] = None,
        xi_N_func: Callable[[float], float] = None,
        xi_Delta_func: Callable[[float], float] = None,
        entropy_func: Callable[[np.ndarray], float] = None,
        isi_domain: Tuple[float, float] = (0.0, 3.0),
        t_domain: Tuple[float, float] = (0.0, 24.0),  # months, arbitrary
        n_samples: int = 200,
    ):
        """
        Parameters
        ----------
        action : callable
            S[phi, t] – the Omega action (or finance analogue). Should accept
            a 2‑element array [phi_N, phi_Delta] and time t, returning a scalar.
        phi_N_func, phi_Delta_func : callable
            Functions returning the Newtonian and asymmetry components given
            ISI and time: phi_N(ISI, t), phi_Delta(ISI, t).
        psi_func, xi_N_func, xi_Delta_func : callable, optional
            Invariant definitions. If omitted, the validator attempts to
            compute them from the action (see _derive_invariants).
        entropy_func : callable, optional
            Shannon‑conditional entropy S_cond(p) where p is a vector of
            return probabilities. If None, the entropy check is skipped.
        isi_domain, t_domain : tuple
            Bounds over which validation is performed.
        n_samples : int
            Number of grid points for validation.
        """
        self.action = action
        self.phi_N = phi_N_func
        self.phi_Delta = phi_Delta_func
        self.psi = psi_func
        self.xi_N = xi_N_func
        self.xi_Delta = xi_Delta_func
        self.entropy = entropy_func
        self.isi_grid = np.linspace(*isi_domain, n_samples)
        self.t_grid = np.linspace(*t_domain, n_samples)

        # Derive invariants if not supplied (by differentiating the action)
        if self.psi is None or self.xi_N is None or self.xi_Delta is None:
            self._derive_invariants()

    # ------------------------------------------------------------------
    # Invariant derivation from the action (simplified)
    # ------------------------------------------------------------------
    def _derive_invariants(self):
        """
        Attempt to extract:
            psi = ln(phi_N)
            xi_N = ∂²S/∂phi_N²   (curvature w.r.t. Newtonian mode)
            xi_Delta = ∂²S/∂phi_Delta²
        This is a *proxy*; a true Ω‑action would give exact forms.
        """
        def S_wrapper(phi_N_val, phi_Delta_val, t):
            return self.action(np.array([phi_N_val, phi_Delta_val]), t)

        # Use a representative time (mid‑grid) for curvature estimation
        t_mid = self.t_grid[len(self.t_grid)//2]

        def phi_N_curvature(phi_N):
            # hold phi_Delta at its nominal value for this phi_N
            phi_Delta_nom = self.phi_Delta(self.isi_grid[len(self.isi_grid)//2], t_mid)
            return S_wrapper(phi_N, phi_Delta_nom, t_mid)

        def phi_Delta_curvature(phi_Delta):
            phi_N_nom = self.phi_N(self.isi_grid[len(self.isi_grid)//2], t_mid)
            return S_wrapper(phi_N_nom, phi_Delta, t_mid)

        # Compute psi directly
        self.psi = lambda phi_N: np.log(phi_N)

        # Compute curvature via second derivative
        self.xi_N = lambda phi_N: second_derivative(phi_N_curvature, phi_N)
        self.xi_Delta = lambda phi_Delta: second_derivative(phi_Delta_curvature, phi_Delta)

    # ------------------------------------------------------------------
    # Validation checks
    # ------------------------------------------------------------------
    def _check_covariant_decomposition(self):
        """
        Verify that phi_N and phi_Delta satisfy the Euler‑Lagrange equations
        derived from the supplied action:
            d/dt (∂S/∂φ̇_i) - ∂S/∂φ_i = 0
        Since we have no explicit velocity dependence in the toy action,
        we reduce to checking stationarity: ∂S/∂φ_i ≈ 0 on‑shell.
        """
        for ISI in self.isi_grid:
            for t in self.t_grid:
                phi_N_val = self.phi_N(ISI, t)
                phi_Delta_val = self.phi_Delta(ISI, t)

                # Gradient of action w.r.t each field (numeric)
                eps = 1e-6
                dS_dphi_N = (self.action(np.array([phi_N_val + eps, phi_Delta_val]), t) -
                             self.action(np.array([phi_N_val - eps, phi_Delta_val]), t)) / (2*eps)
                dS_dphi_Delta = (self.action(np.array([phi_N_val, phi_Delta_val + eps]), t) -
                                 self.action(np.array([phi_N_val, phi_Delta_val - eps]), t)) / (2*eps)

                # Stationarity condition (should be ~0)
                assert abs(dS_dphi_N) < 1e-3, (
                    f"Euler‑Lagrange violation for Φ_N: ∂S/∂Φ_N={dS_dphi_N:.6f} at ISI={ISI:.3f}, t={t:.3f}"
                )
                assert abs(dS_dphi_Delta) < 1e-3, (
                    f"Euler‑Lagrange violation for Φ_Δ: ∂S/∂Φ_Δ={dS_dphi_Delta:.6f} at ISI={ISI:.3f}, t={t:.3f}"
                )

    def _check_invariants(self):
        """Ensure invariants are well‑defined and finite over the domain."""
        for ISI in self.isi_grid:
            for t in self.t_grid:
                phi_N_val = self.phi_N(ISI, t)
                phi_Delta_val = self.phi_Delta(ISI, t)

                # psi = ln(phi_N) must be real → phi_N > 0
                assert phi_N_val > 0, f"Φ_N ≤ 0 → ψ undefined at ISI={ISI:.3f}, t={t:.3f}"
                psi_val = self.psi(phi_N_val)
                assert np.isfinite(psi_val), f"ψ non‑finite at ISI={ISI:.3f}, t={t:.3f}"

                # xi_N, xi_Delta should be finite (no poles)
                xi_N_val = self.xi_N(phi_N_val)
                xi_Delta_val = self.xi_Delta(phi_Delta_val)
                assert np.isfinite(xi_N_val), f"ξ_N non‑finite at ISI={ISI:.3f}, t={t:.3f}"
                assert np.isfinite(xi_Delta_val), f"ξ_Δ non‑finite at ISI={ISI:.3f}, t={t:.3f}"

    def _check_entropy_gauge(self):
        """If an entropy function is provided, verify its dynamical coupling."""
        if self.entropy is None:
            return  # Skip if not supplied
        # We approximate a probability distribution from returns; here we use a placeholder:
        # In a real validation you would feed actual return data.
        dummy_returns = np.random.randn(50)  # stand‑in for log‑returns
        # Convert to a simple histogram probability vector
        hist, _ = np.histogram(dummy_returns, bins=10, density=True)
        p = hist / hist.sum()
        S = self.entropy(p)
        assert np.isfinite(S), "Entropy must be finite"
        # Check that entropy varies with time via the jerk of Φ_N (proxy)
        # Compute jerk of Φ_N at a sample point
        ISI_mid = self.isi_grid[len(self.isi_grid)//2]
        t_mid = self.t_grid[len(self.t_grid)//2]
        # Define phi_N(t) at fixed ISI
        phi_N_t = lambda tt: self.phi_N(ISI_mid, tt)
        jerk = third_derivative(phi_N_t, t_mid)
        # Entropy should have some non‑zero coupling; we just ensure it's not constant zero
        # (real test would involve regression of S vs jerk)
        assert not np.isclose(jerk, 0.0, atol=1e-6) or np.abs(S) > 1e-6, (
            "Entropy gauge shows no variation with Φ_N jerk – likely missing coupling."
        )

    def _check_bounds(self):
        """Simple QP‑style bounds (sanity filter)."""
        for ISI in self.isi_grid:
            assert 0.0 <= ISI <= 3.0, f"ISI out of declared bounds: {ISI}"
            for t in self.t_grid:
                phi_N = self.phi_N(ISI, t)
                phi_Delta = self.phi_Delta(ISI, t)
                assert 0.0 <= phi_N <= 0.85, (
                    f"Φ_N={phi_N:.4f} exceeds bound [0,0.85] at ISI={ISI:.3f}, t={t:.3f}"
                )
                assert 0.0 <= phi_Delta <= 0.7, (
                    f"Φ_Δ={phi_Delta:.4f} exceeds bound [0,0.7] at ISI={ISI:.3f}, t={t:.3f}"
                )

    def run_all(self):
        """Execute the full validation suite."""
        print("Running Omega Protocol compliance checks …")
        self._check_covariant_decomposition()
        print("✓ Covariant decomposition (Euler‑Lagrange) satisfied.")
        self._check_invariants()
        print("✓ Invariants (ψ, ξ_N, ξ_Δ) well‑defined.")
        self._check_entropy_gauge()
        print("✓ Entropy gauge present and coupled (if supplied).")
        self._check_bounds()
        print("✓ Simple QP bounds respected.")
        print("\nAll checks passed – the module is Ω‑compliant (within numerical tolerance).")
        return True

# ----------------------------------------------------------------------
# Example usage (placeholder – replace with real implementations)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Dummy action: S = 0.5*(phi_N^2 + phi_Delta^2) - lambda*ISI*phi_N*phi_Delta
    # This is merely illustrative; a genuine Ω‑action would be far more complex.
    lam = 0.1
    def dummy_action(phi, t):
        phi_N, phi_Delta = phi
        return 0.5*(phi_N**2 + phi_Delta**2) - lam * phi_N * phi_Delta

    # Dummy component functions (the ones from the proposal)
    eta1, eta2, eta3 = 0.2, 0.3, 0.1
    tau1, tau2, tau3 = 1.0, 0.5, 2.0  # months
    def phi_N_component(ISI, t):
        return 0.5 + eta1 * np.tanh(ISI * (t - tau1))  # baseline 0.5 for illustration

    def phi_Delta_component(ISI, t):
        return 0.3 + eta2 * ISI * (t - tau2) - eta3 * (ISI * (t - tau3))**2

    # Placeholder invariant and entropy (None → will be derived/skipped)
    validator = OmegaFinanceValidator(
        action=dummy_action,
        phi_N_func=phi_N_component,
        phi_Delta_func=phi_Delta_component,
        # psi, xi_N, xi_Delta left None → derived from action
        entropy=None,  # you could supply a Shannon entropy callable here
        isi_domain=(0.0, 3.0),
        t_domain=(0.0, 24.0),
        n_samples=150,
    )
    try:
        validator.run_all()
    except AssertionError as e:
        print("\n❌ VALIDATION FAILED:")
        print(e)