# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script for the Q-Systemic Self derivation.
Checks mathematical soundness and invariant compliance.
"""

import numpy as np
from typing import Callable, Tuple

# ----------------------------------------------------------------------
# 1. Declared invariants (as they appear in the source)
# ----------------------------------------------------------------------
PSI_ID_COEFF = 1.0          # should appear in Hamiltonian
XI_BOUND_DEFAULT = 1.0      # stiffness coefficient
XI_CRITICAL = 0.4

# ----------------------------------------------------------------------
# 2. Helper functions that mimic the intended mathematics
# ----------------------------------------------------------------------
def inner_product(a: np.complex128, b: np.complex128) -> np.complex128:
    """⟨a|b⟩ = a*·b (complex conjugate of a times b)."""
    return np.conj(a) * b

def norm_sq(z: np.complex128) -> float:
    return np.real(z * np.conj(z))

def cod(exp: np.complex128, intel: np.complex128) -> float:
    """Chain Overlap Density = |⟨exp|intel⟩|^2 / (||exp||^2 ||intel||^2)."""
    num = np.abs(inner_product(exp, intel)) ** 2
    den = norm_sq(exp) * norm_sq(intel)
    return 0.0 if den == 0.0 else num / den

def conditional_entropy(exp: np.complex128, intel: np.complex128) -> float:
    """Shannon conditional entropy H(X|Y) with X=exp, Y=intel.
    For a two‑outcome model we use p = |⟨exp|intel⟩|^2."""
    p = np.abs(inner_product(exp, intel)) ** 2
    # Clamp to avoid log(0)
    p = min(max(p, 0.0), 1.0)
    if p == 0.0:
        return 0.0
    return -p * np.log(p)

def gamma(t: float, tau_opt: float = 0.5, sigma: float = 0.1) -> float:
    """Adiabatic coupling Gamma(t) = tanh((t‑tau)/sigma)."""
    return np.tanh((t - tau_opt) / sigma)

def dgamma_dt(t: float, tau_opt: float = 0.5, sigma: float = 0.1) -> float:
    """Derivative of Gamma(t)."""
    x = (t - tau_opt) / sigma
    return (1.0 / sigma) * (1.0 - np.tanh(x) ** 2)   # sech^2 = 1 - tanh^2

def hamiltonian_energy(exp: np.complex128,
                       intel: np.complex128,
                       t: float,
                       psi_id_coeff: float = PSI_ID_COEFF,
                       xi_bound: float = XI_BOUND_DEFAULT) -> float:
    """
    Intended effective Hamiltonian (real-valued):
        H_eff = H_exp + xi_bound * |⟨exp|intel⟩|^2 + Gamma(t) * Re[⟨exp|intel⟩]
                - H_cond   (entropy reduction contributes negative energy)
    For validation we set H_exp = 0 and the coupling term to the real part
    of the inner product (a common choice for a Hermitian interaction).
    """
    overlap = inner_product(exp, intel)
    overlap_sq = np.abs(overlap) ** 2
    H_stiff = xi_bound * overlap_sq
    H_couple = np.real(overlap) * gamma(t)   # Hermitian coupling
    H_cond = conditional_entropy(exp, intel)
    # H_exp set to zero for simplicity
    return H_stiff + H_couple - H_cond   # psi_id_coeff not used yet

# ----------------------------------------------------------------------
# 3. Validation Tests
# ----------------------------------------------------------------------
def test_invariant_embodiment():
    """Check that PSI_ID_COEFF and XI_BOUND_DEFAULT actually influence energy."""
    exp = np.complex128(0.6 + 0.8j)
    intel = np.complex128(0.9 + 0.2j)

    # Baseline with default invariants
    E0 = hamiltonian_energy(exp, intel, t=0.0)

    # Perturb PSI_ID_COEFF – should change energy if used
    E_psi = hamiltonian_energy(exp, intel, t=0.0,
                               psi_id_coeff=PSI_ID_COEFF * 2.0,
                               xi_bound=XI_BOUND_DEFAULT)
    # Perturb XI_BOUND_DEFAULT – should change energy
    E_xi = hamiltonian_energy(exp, intel, t=0.0,
                               psi_id_coeff=PSI_ID_COEFF,
                               xi_bound=XI_BOUND_DEFAULT * 2.0)

    # If the invariants are *not* used, the energies will be identical.
    assert not np.isclose(E0, E_psi, rtol=1e-12), \
        "PSI_ID_COEFF does not affect Hamiltonian energy."
    assert not np.isclose(E0, E_xi, rtol=1e-12), \
        "XI_BOUND_DEFAULT does not affect Hamiltonian energy."

def test_adiabatic_condition():
    """Enforce max|dΓ/dt| << ξ_bound."""
    t_vals = np.linspace(0.0, 1.0, 1000)
    deriv_vals = np.abs([dgamma_dt(t) for t in t_vals])
    max_deriv = np.max(deriv_vals)
    # "Much less than" – we adopt a factor of 0.1 as a strict bound
    assert max_deriv < 0.1 * XI_BOUND_DEFAULT, \
        f"Adiabatic condition violated: max|dΓ/dt|={max_deriv:.3f} >= 0.1*ξ_bound={0.1*XI_BOUND_DEFAULT:.3f}"

def test_cod_formula():
    """COD must be bounded [0,1] and use squared magnitudes."""
    exp = np.complex128(0.3 + 0.4j)
    intel = np.complex128(0.6 + 0.2j)
    c = cod(exp, intel)
    assert 0.0 <= c <= 1.0 + 1e-12, f"COD out of bounds: {c}"
    # Spot‑check against manual definition
    manual = np.abs(inner_product(exp, intel)) ** 2 / (norm_sq(exp) * norm_sq(intel))
    assert np.isclose(c, manual, rtol=1e-12), "COD implementation mismatch"

def test_conditional_entropy():
    """Entropy must use probability = |⟨exp|intel⟩|^2 and be non‑negative."""
    exp = np.complex128(1.0 + 0.0j)
    intel = np.complex128(0.0 + 1.0j)   # orthogonal → p=0 → H=0
    assert np.isclose(conditional_entropy(exp, intel), 0.0, atol=1e-12)

    intel = np.complex128(1.0 + 0.0j)   # identical → p=1 → H=0 (by -1*log(1)=0)
    assert np.isclose(conditional_entropy(exp, intel), 0.0, atol=1e-12)

    intel = np.complex128(0.7 + 0.7j)   # non‑trivial overlap
    p = np.abs(inner_product(exp, intel)) ** 2
    expected = -p * np.log(p) if p > 0 else 0.0
    assert np.isclose(conditional_entropy(exp, intel), expected, rtol=1e-12)

def test_failure_mode_entropy_rate():
    """Failure mode needs a well‑defined entropy rate; we approximate via finite difference."""
    def entropy_at(t):
        exp = np.complex128(np.cos(t), np.sin(t))
        intel = np.complex128(1.0, 0.0)
        return conditional_entropy(exp, intel)

    t0, t1 = 0.0, 0.01
    S0 = entropy_at(t0)
    S1 = entropy_at(t1)
    entropy_rate = np.abs((S1 - S0) / (t1 - t0))
    # Use the condition from the source: xi_bound > 2 * entropy_rate => HIGH risk
    risk = XI_BOUND_DEFAULT > 2.0 * entropy_rate
    # Just check that the expression can be evaluated without error
    assert isinstance(risk, bool)

def test_hamiltonian_hermitian():
    """The effective Hamiltonian should be real (Hermitian) for any state."""
    for _ in range(10):
        exp = np.complex128(np.random.randn() + 1j*np.random.randn())
        intel = np.complex128(np.random.randn() + 1j*np.random.randn())
        E = hamiltonian_energy(exp, intel, t=np.random.rand())
        # Imaginary part should be (near) zero
        assert np.abs(np.imag(E)) < 1e-12, f"Non‑Hermitian Hamiltonian: {E}"

def test_constant_immutability():
    """Ensure the validation does not silently mutate the declared invariants."""
    original_psi = PSI_ID_COEFF
    original_xi = XI_BOUND_DEFAULT
    # Run a dummy calculation that *could* try to modify them
    _ = hamiltonian_energy(1+0j, 1+0j, t=0.0)
    assert PSI_ID_COEFF == original_psi, "PSI_ID_COEFF was mutated!"
    assert XI_BOUND_DEFAULT == original_xi, "XI_BOUND_DEFAULT was mutated!"

def run_all_tests():
    test_invariant_embodiment()
    test_adiabatic_condition()
    test_cod_formula()
    test_conditional_entropy()
    test_failure_mode_entropy_rate()
    test_hamiltonian_hermitian()
    test_constant_immutability()
    print("All Omega‑Protocol validation checks passed.")

if __name__ == "__main__":
    run_all_tests()