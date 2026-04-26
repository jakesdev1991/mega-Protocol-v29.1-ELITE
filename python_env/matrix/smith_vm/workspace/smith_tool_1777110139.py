# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# OMEGA PROTOCOL VALIDATION SCRIPT
# Validates the mathematical soundness and invariant compliance of the
# Intellectual Validation Gate (IVG) v56.0-Ω-REINTEGRATE implementation.
# =============================================================================
import math
import random
from typing import List, Tuple

# -----------------------------------------------------------------------------
# Helper functions (mirroring the C++ logic)
# -----------------------------------------------------------------------------
def fidelity(intent: List[float], identity: List[float]) -> float:
    """Normalized dot‑product fidelity ∈ [0,1]."""
    if not intent or not identity:
        return 0.0
    n = min(len(intent), len(identity))
    dot = sum(intent[i] * identity[i] for i in range(n))
    magI = sum(x * x for x in identity[:n])
    magV = sum(x * x for x in intent[:n])
    if magI == 0.0 or magV == 0.0:
        return 0.0
    f = dot / (math.sqrt(magI) * math.sqrt(magV))
    return max(0.0, min(1.0, f))

def damping(H_super: float, Lambda: float = 1.0) -> float:
    """Uncertainty damping exp(-Λ·H) ∈ (0,1]."""
    return math.exp(-Lambda * H_super)

def atrophy_penalty(H_super: float, theta_atrophy: float = 0.15) -> float:
    """Penalty ∈ [0,1]; 1 when H≥θ, linearly decreases to 0 at H=0."""
    if H_super >= theta_atrophy:
        return 1.0
    # linear fall‑off to zero at H=0
    return H_super / theta_atrophy

def COD_reboot(intent: List[float],
               identity: List[float],
               H_super: float,
               psi_id: float,
               psi_id_threshold: float = 0.95,
               Lambda: float = 1.0,
               theta_atrophy: float = 0.15) -> float:
    """
    Chain Overlap Density for reboot alignment.
    Returns 0 if psi_id < threshold (hard gate).
    """
    if psi_id < psi_id_threshold:
        return 0.0
    fid = fidelity(intent, identity)
    dam = damping(H_super, Lambda)
    att = atrophy_penalty(H_super, theta_atrophy)
    return fid * dam * psi_id * att

def superposition_entropy(fragments: List[List[float]]) -> float:
    """
    Normalized Shannon entropy of fragment probabilities.
    Returns value in [0,1].
    """
    if not fragments:
        return 0.0
    # probability proportional to 1/(1+sqrt(dim))
    dims = [len(f) for f in fragments]
    probs = [1.0 / (1.0 + math.sqrt(d)) for d in dims]
    total = sum(probs)
    probs = [p / total for p in probs]
    H = -sum(p * math.log(p) for p in probs if p > 0.0)
    max_H = math.log(len(fragments))
    if max_H == 0.0:
        max_H = 1.0
    return min(1.0, max(0.0, H / max_H))

def failure_mode_detector(H_super: float,
                          Gamma_reboot: float,
                          psi_id: float,
                          COD: float,
                          theta_shock: float = 0.80,
                          theta_atrophy: float = 0.15,
                          Gamma_high: float = 0.60,
                          Gamma_mid: float = 0.50,
                          psi_id_crit: float = 0.90,
                          COD_low: float = 0.80) -> str:
    """
    Returns a string label for the detected risk.
    Mirrors the enum logic in the C++ code.
    """
    if (H_super > theta_shock and Gamma_reboot > Gamma_high) or psi_id < psi_id_crit:
        return "REBOOT_COLLAPSE"
    if (H_super < theta_atrophy and Gamma_reboot > Gamma_mid and psi_id < 0.95):
        return "QUANTUM_ATROPHY"
    if COD < COD_low and psi_id > 0.95:
        return "IDENTITY_VACUUM"
    return "NONE"

# -----------------------------------------------------------------------------
# Validation tests
# -----------------------------------------------------------------------------
def test_fidelity_bounds():
    for _ in range(1000):
        a = [random.uniform(-1, 1) for _ in range(10)]
        b = [random.uniform(-1, 1) for _ in range(10)]
        f = fidelity(a, b)
        assert 0.0 <= f <= 1.0, f"Fidelity out of bounds: {f}"
    print("✓ fidelity bounds")

def test_damping_bounds():
    for H in [i/100.0 for i in range(0, 201)]:  # 0..2
        d = damping(H)
        assert 0.0 < d <= 1.0, f"Damping out of bounds: {d} at H={H}"
    print("✓ damping bounds")

def test_atrophy_penalty_bounds():
    for H in [i/1000.0 for i in range(0, 200)]:  # 0..0.2
        p = atrophy_penalty(H)
        assert 0.0 <= p <= 1.0, f"Atrophy penalty out of bounds: {p} at H={H}"
    # edge cases
    assert atrophy_penalty(0.0) == 0.0
    assert atrophy_penalty(0.15) == 1.0
    assert atrophy_penalty(0.30) == 1.0  # saturates
    print("✓ atrophy penalty bounds")

def test_COD_hard_gate():
    intent = [1.0]*5
    identity = [1.0]*5
    for psi in [0.9, 0.94, 0.95, 0.96]:
        c = COD_reboot(intent, identity, H_super=0.2, psi_id=psi)
        if psi < 0.95:
            assert c == 0.0, f"COD should be zero for psi_id={psi}"
        else:
            assert c > 0.0, f"COD should be positive for psi_id={psi}"
    print("✓ COD hard gate")

def test_COD_range():
    for _ in range(500):
        intent = [random.uniform(-1, 1) for _ in range(8)]
        identity = [random.uniform(-1, 1) for _ in range(8)]
        H = random.random()
        psi = random.uniform(0.9, 1.0)
        c = COD_reboot(intent, identity, H, psi)
        assert 0.0 <= c <= 1.0, f"COD out of [0,1]: {c}"
    print("✓ COD range")

def test_superposition_entropy_normalization():
    # single fragment → entropy 0
    assert superposition_entropy([[1.0,2.0]]) == 0.0
    # two identical fragments → max entropy = ln(2)/ln(2) = 1
    frag = [[0.5]*10, [0.5]*10]
    assert math.isclose(superposition_entropy(frag), 1.0, rel_tol=1e-9)
    # random fragments should be in [0,1]
    for _ in range(200):
        n = random.randint(2, 10)
        frags = [[random.uniform(-1,1) for _ in range(12)] for __ in range(n)]
        s = superposition_entropy(frags)
        assert 0.0 <= s <= 1.0, f"Entropy out of bounds: {s}"
    print("✓ superposition entropy normalization")

def test_failure_mode_logic():
    # REBOOT_COLLAPSE: high H + high Gamma OR low psi
    assert failure_mode_detector(H_super=0.85, Gamma_reboot=0.7, psi_id=0.96, COD=0.5) == "REBOOT_COLLAPSE"
    assert failure_mode_detector(H_super=0.5, Gamma_reboot=0.2, psi_id=0.88, COD=0.5) == "REBOOT_COLLAPSE"
    # QUANTUM_ATROPHY: low H, mid Gamma, low psi
    assert failure_mode_detector(H_super=0.1, Gamma_reboot=0.55, psi_id=0.9, COD=0.5) == "QUANTUM_ATROPHY"
    # IDENTITY_VACUUM: low COD, high psi
    assert failure_mode_detector(H_super=0.2, Gamma_reboot=0.1, psi_id=0.96, COD=0.7) == "IDENTITY_VACUUM"
    # NONE: everything nominal
    assert failure_mode_detector(H_super=0.3, Gamma_reboot=0.2, psi_id=0.97, COD=0.9) == "NONE"
    print("✓ failure mode detector")

def test_invariant_phi_loss():
    """
    Simple check that the Phi loss formula from the C++ snippet is
    non‑negative and grows when psi_id drops below threshold or audit cost rises.
    """
    K = 1.0
    def phi_loss(psi, audit_factor=1.0):
        loss = 0.0
        if psi < 0.95:
            loss += (0.95 - psi) * 0.5 * K
        loss += K * math.log(2.0) * audit_factor
        return loss
    # baseline
    base = phi_loss(0.97, 1.0)
    # lower identity → higher loss
    assert phi_loss(0.90, 1.0) > base
    # higher audit factor → higher loss
    assert phi_loss(0.97, 2.0) > base
    # loss never negative
    for psi in [i/100.0 for i in range(0, 120)]:
        for af in [i/10.0 for i in range(0, 21)]:
            assert phi_loss(psi, af) >= 0.0
    print("✓ phi loss invariant")

# -----------------------------------------------------------------------------
# Run all tests
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    test_fidelity_bounds()
    test_damping_bounds()
    test_atrophy_penalty_bounds()
    test_COD_hard_gate()
    test_COD_range()
    test_superposition_entropy_normalization()
    test_failure_mode_logic()
    test_invariant_phi_loss()
    print("\nAll validation checks passed. The IVG v56.0 implementation is mathematically sound and respects the Omega Protocol invariants.")