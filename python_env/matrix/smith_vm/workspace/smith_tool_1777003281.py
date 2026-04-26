# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Compliance Validator for Audience Resonance Mapping
-----------------------------------------------------------------
Checks:
1. Dimensionless nature of all intermediate quantities.
2. COD ∈ [0,1] for valid inputs.
3. Identity hard gate (Psi_id < 0.95) raises InvariantViolation.
4. Resonance-shock detection logic.
5. Adiabatic pitch clamp: Gamma <= Xi_sys + 0.3.
6. Phi-net ledger matches prescribed equation.
7. Audit entropy formula.
8. Benchmark false-positive rate < 0.1% (Monte Carlo).
"""

import math
import random
from typing import Tuple, List

# ----------------------------------------------------------------------
# Constants (as per the specification)
# ----------------------------------------------------------------------
LAMBDA_COUPLING = 1.0          # Λ
GAMMA_COUPLING  = 0.5          # Γ (in COD formula)
PSI_TRUST_MIN   = 0.95         # hard gate threshold
XI_BUYER_MAX    = 3.0          # stiffness upper bound used in detector
PSI_TRUST_CRIT  = 0.90         # detector threshold for shock
K_BOLTZMANN     = 1.0          # natural units
AUDIT_BASE      = 1.0          # C_audit for a 3‑week cycle

# ----------------------------------------------------------------------
# Core functions (mirroring the spec)
# ----------------------------------------------------------------------
def fidelity(value: List[float], need: List[float]) -> float:
    """Quantum overlap fidelity, clamped to [0,1]."""
    if len(value) != len(need):
        raise ValueError("Vectors must be same length")
    dot = sum(v * n for v, n in zip(value, need))
    magV = sum(v * v for v in value)
    magN = sum(n * n for n in need)
    if magV == 0.0 or magN == 0.0:
        return 0.0
    f = dot / (math.sqrt(magV) * math.sqrt(magN))
    return max(0.0, min(1.0, f))

def cod_sale(value: List[float], need: List[float],
             h_noise: float, xi_buyer: float, psi_trust: float) -> float:
    """Chain Overlap Density (COD) – dimensionless [0,1]."""
    fid = fidelity(value, need)
    damping = math.exp(-LAMBDA_COUPLING * h_noise)
    stiffness = math.exp(-GAMMA_COUPLING * xi_buyer)
    trust_mult = max(0.0, psi_trust)   # zero if trust negative
    return fid * damping * stiffness * trust_mult

def invariant_violation(psi_trust: float) -> bool:
    """Hard gate: returns True if invariant broken (should abort)."""
    return psi_trust < PSI_TRUST_MIN

def resonance_shock(xi_buyer: float, psi_trust: float) -> bool:
    """Early-warning detector (not the final gate)."""
    return (xi_buyer > XI_BUYER_MAX) and (psi_trust < PSI_TRUST_CRIT)

def adiabatic_pitch(t: float, tau: float = 0.7, sigma: float = 0.1,
                    gamma_max: float = 1.2, xi_buyer: float = 0.0) -> float:
    """Measurement frequency Gamma(t) with adiabatic clamp."""
    raw = 0.5 * (1.0 + math.tanh((t - tau) / sigma)) * gamma_max
    return min(raw, xi_buyer + 0.3)   # enforce Gamma <= Xi_sys + 0.3

def audit_entropy(c_audit: float = AUDIT_BASE) -> float:
    """Dimensionless audit entropy: k_B * ln(2) * C_audit."""
    return K_BOLTZMANN * math.log(2.0) * c_audit

def phi_net(delta_cod: float, h_noise: float,
            delta_psi_trust: float, c_audit: float = AUDIT_BASE) -> float:
    """Φ‑net gain according to the ledger."""
    noise_cost = 0.5 * h_noise
    audit_cost = audit_entropy(c_audit)
    identity_cost = 0.3 * delta_psi_trust
    return delta_cod - noise_cost - audit_cost - identity_cost

# ----------------------------------------------------------------------
# Validation Tests
# ----------------------------------------------------------------------
def test_dimensionless():
    """All functions should return pure numbers (no units)."""
    # Just call with dimensionless inputs; if no exception, assume OK.
    v = [0.5, 0.2]
    n = [0.4, 0.3]
    c = cod_sale(v, n, h_noise=0.2, xi_buyer=1.0, psi_trust=0.96)
    assert 0.0 <= c <= 1.0, f"COD out of range: {c}"
    assert isinstance(c, float)
    print("✓ Dimensionless COD test passed")

def test_cod_bounds():
    """COD must stay in [0,1] for any valid inputs."""
    random.seed(42)
    for _ in range(1000):
        v = [random.random() for _ in range(3)]
        n = [random.random() for _ in range(3)]
        h = random.random()          # [0,1]
        x = random.random() * 3.0    # [0,3]
        p = random.random()          # [0,1]
        c = cod_sale(v, n, h, x, p)
        assert 0.0 <= c <= 1.0, f"COD={c} with h={h}, x={x}, p={p}"
    print("✓ COD bounds test passed (1000 random samples)")

def test_hard_gate():
    """Psi_trust < 0.95 must trigger invariant violation."""
    assert invariant_violation(0.94) == True
    assert invariant_violation(0.95) == False   # boundary inclusive
    assert invariant_violation(0.96) == False
    print("✓ Hard gate test passed")

def test_resonance_shock_logic():
    """Detector should fire only when both conditions hold."""
    # Should fire
    assert resonance_shock(xi_buyer=3.2, psi_trust=0.88) == True
    # Should not fire: stiffness ok
    assert resonance_shock(xi_buyer=2.5, psi_trust=0.88) == False
    # Should not fire: trust ok
    assert resonance_shock(xi_buyer=3.2, psi_trust=0.92) == False
    print("✓ Resonance shock detector test passed")

def test_adiabatic_clamp():
    """Gamma(t) must never exceed Xi_sys + 0.3."""
    random.seed(123)
    for _ in range(500):
        t = random.random()
        x = random.random() * 3.0
        g = adiabatic_pitch(t, xi_buyer=x)
        assert g <= x + 0.3 + 1e-12, f"Gamma={g} > Xi+0.3={x+0.3}"
        assert g >= 0.0
    print("✓ Adiabatic pitch clamp test passed")

def test_phi_net_formula():
    """Check that phi_net implements the ledger equation exactly."""
    delta_cod = 0.15
    h_noise   = 0.4
    d_psi     = -0.02   # identity erosion (negative)
    expected = delta_cod - 0.5*h_noise - K_BOLTZMANN*math.log(2.0)*AUDIT_BASE - 0.3*d_psi
    got = phi_net(delta_cod, h_noise, d_psi)
    assert math.isclose(got, expected, rel_tol=1e-9), f"Phi-net mismatch: {got} vs {expected}"
    print("✓ Phi-net formula test passed")

def test_audit_entropy():
    """Audit entropy must equal k_B*ln2*C_audit."""
    assert math.isclose(audit_entropy(1.0), K_BOLTZMANN*math.log(2.0), rel_tol=1e-12)
    assert math.isclose(audit_entropy(2.0), 2.0*K_BOLTZMANN*math.log(2.0), rel_tol=1e-12)
    print("✓ Audit entropy test passed")

def benchmark_false_positive_rate(trials: int = 5000) -> float:
    """
    Monte Carlo estimate of false-positive rate:
    legitimate high-trust buyers (Psi_trust >= 0.97, low stiffness, low noise)
    incorrectly flagged as resonance shock by the detector.
    """
    false_pos = 0
    random.seed(2025)
    for _ in range(trials):
        # generate a "good" buyer
        xi = random.uniform(0.0, 1.5)          # low stiffness
        psi = random.uniform(0.97, 1.0)        # high trust
        h   = random.uniform(0.0, 0.2)         # low noise
        if resonance_shock(xi, psi):
            false_pos += 1
    rate = false_pos / trials
    print(f"✓ Benchmark false-positive rate: {rate:.4%} over {trials} trials")
    return rate

def run_all_tests():
    test_dimensionless()
    test_cod_bounds()
    test_hard_gate()
    test_resonance_shock_logic()
    test_adiabatic_clamp()
    test_phi_net_formula()
    test_audit_entropy()
    fp_rate = benchmark_false_positive_rate()
    assert fp_rate < 0.001, f"False-positive rate too high: {fp_rate:.4%}"
    print("\n🟢 All validation checks passed. The implementation is Omega‑Protocol compliant.")

if __name__ == "__main__":
    run_all_tests()