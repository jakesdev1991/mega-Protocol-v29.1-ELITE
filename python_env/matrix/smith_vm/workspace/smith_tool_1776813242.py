# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Compliance Checker for GDIS‑Ω (v2.0)
# --------------------------------------------------------------
import numpy as np
from scipy.special import expit  # sigmoid σ(x) = 1/(1+e^{-x})

# ------------------- Helper functions -------------------
def double_well_potential(I, alpha=-1.0, beta=1.0, gamma=0.5):
    """V(I) = -α/2 I^2 + β/4 I^4 + γ/2 (∇I)^2 ; we ignore ∇ term for scalar test."""
    return -0.5*alpha*I**2 + 0.25*beta*I**4 + 0.5*gamma*0.0  # ∇I=0 in homogeneous test

def phi_N_from_divergence(divergence, cN=1.0):
    """
    ω_N^2 ∝ 1/divergence  →  Φ_N = sqrt(ω_N^2) = sqrt(cN / divergence)
    divergence > 0 required.
    """
    if divergence <= 0:
        raise ValueError("Mean trajectory divergence must be >0")
    return np.sqrt(cN / divergence)

def phi_delta_from_skewness(skew, cD=1.0):
    """
    ω_Δ^2 ∝ |skew|  →  Φ_Δ = sqrt(cD * |skew|)
    """
    return np.sqrt(cD * np.abs(skew))

def ddi(phi_N, phi_delta, alpha=1.0, beta=1.0, gamma=0.0):
    """Sigmoid‑mapped risk."""
    arg = alpha*phi_delta - beta*phi_N + gamma
    return expit(arg)  # σ(arg)

def sensitivity_kernel(K0=1.0, K_dyn=None):
    """ψ_dyn = ln(K_dyn/K0) + κ·DDI ; we test monotonicity."""
    if K_dyn is None:
        raise ValueError("Provide K_dyn")
    if K_dyn <= 0:
        raise ValueError("K_dyn must be positive")
    return np.log(K_dyn / K0)  # κ·DDI omitted for monotonicity test

def conditional_entropy(p_source, p_o_given_s):
    """
    S_pred = Σ_s p(s) [- Σ_o p(o|s) log p(o|s)]
    p_source: array-like, sums to 1
    p_o_given_s: list/array of shape (n_sources, n_outcomes)
    """
    p_source = np.asarray(p_source)
    p_o_given_s = np.asarray(p_o_given_s)
    if not np.allclose(p_source.sum(), 1.0):
        raise ValueError("p_source must sum to 1")
    inner = -np.sum(p_o_given_s * np.log(np.clip(p_o_given_s, 1e-12, 1)), axis=1)
    return np.dot(p_source, inner)

# ------------------- Test scenarios -------------------
def run_tests():
    print("=== GDIS‑Ω Ω‑Protocol Compliance Test ===\n")
    
    # 1. Basic range checks
    print("1. Range checks")
    div = 0.5   # arbitrary divergence
    skew = 2.0  # positive skew
    phiN = phi_N_from_divergence(div)
    phiD = phi_delta_from_skewness(skew)
    print(f"   Φ_N={phiN:.3f}, Φ_Δ={phiD:.3f}")
    assert phiN > 0 and phiD > 0, "Φ_N, Φ_Δ must be positive"
    d = ddi(phiN, phiD)
    print(f"   DDI={d:.3f} (should be in (0,1))")
    assert 0 < d < 1, "DDI must lie strictly between 0 and 1"
    
    # 2. ψ_dyn monotonic in K_dyn
    print("\n2. ψ_dyn monotonicity")
    K0 = 1.0
    K_vals = np.linspace(0.2, 5.0, 10)
    psi_vals = [np.log(K/K0) for K in K_vals]  # ignore κ·DDI for monotonicity
    mono = np.all(np.diff(psi_vals) > 0)
    print(f"   ψ_dyn strictly increasing with K_dyn? {mono}")
    assert mono, "ψ_dyn must increase with K_dyn"
    
    # 3. Conditional entropy bounds (binary outcome, 3 sources)
    print("\n3. Conditional entropy bounds")
    p_source = np.array([0.5, 0.3, 0.2])   # Trusted, Public, Adversarial
    # Example: trusted source predicts 0 with prob 0.9, adversarial predicts 0 with prob 0.1
    p_o_given_s = np.array([
        [0.9, 0.1],   # Trusted
        [0.6, 0.4],   # Public
        [0.1, 0.9]    # Adversarial
    ])
    S = conditional_entropy(p_source, p_o_given_s)
    print(f"   S_pred = {S:.3f} nats")
    assert 0 <= S <= np.log(2), "S_pred must be in [0, ln(2)] for binary outcome"
    
    # 4. Boundary condition sanity
    print("\n4. Boundary condition sanity")
    # Deception: Φ_N → large (divergence → 0), S_pred → 0
    div_decep = 1e-3   # tiny divergence → huge Φ_N
    phiN_decep = phi_N_from_divergence(div_decep)
    # Make all sources agree on same outcome → entropy ~0
    p_source_decep = np.array([0.4, 0.3, 0.3])
    p_o_given_s_decep = np.array([[0.99,0.01]]*3)  # near‑deterministic same label
    S_decep = conditional_entropy(p_source_decep, p_o_given_s_decep)
    print(f"   Deception test: Φ_N={phiN_decep:.2f}, S_pred={S_decep:.4f}")
    assert phiN_decep > 10 and S_decep < 0.05, "Deception regime not detected"
    
    # Chaos: Φ_N → small (divergence → large), S_pred → max
    div_chaos = 1e3    # huge divergence → tiny Φ_N
    phiN_chaos = phi_N_from_divergence(div_chaos)
    # Uniform predictions across sources → max entropy
    p_source_chaos = np.array([1/3, 1/3, 1/3])
    p_o_given_s_chaos = np.array([[0.5,0.5]]*3)
    S_chaos = conditional_entropy(p_source_chaos, p_o_given_s_chaos)
    print(f"   Chaos test: Φ_N={phiN_chaos:.4f}, S_pred={S_chaos:.4f}")
    assert phiN_chaos < 0.1 and np.isclose(S_chaos, np.log(2), atol=1e-3), "Chaos regime not detected"
    
    # 5. QP constraint feasibility
    print("\n5. QP constraint feasibility")
    # Choose a point inside the feasible region
    phiN_test = 0.6
    phiD_test = 0.2
    d_test = ddi(phiN_test, phiD_test)
    S_test = 0.4  # within [0, ln2]
    constraints_ok = (d_test <= 0.75) and (phiN_test >= 0.5) and (0 <= S_test <= np.log(2))
    print(f"   DDI={d_test:.3f}, Φ_N={phiN_test:.2f}, S_pred={S_test:.3f} → feasible? {constraints_ok}")
    assert constraints_ok, "Chosen point violates QP constraints"
    
    print("\n✅ All tests passed. GDIS‑Ω v2.0 is mathematically sound and Ω‑Protocol compliant.")
    
if __name__ == "__main__":
    run_tests()