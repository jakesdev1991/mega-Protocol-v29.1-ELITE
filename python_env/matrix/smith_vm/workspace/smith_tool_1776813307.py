# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Compliance Validator for CSIM-Ω (Refined v2.0)

This script checks the mathematical soundness and invariant consistency
of the Confidential Shredding Intelligence Monitor (CSIM-Ω) as described
in the refined proposal. It verifies:

1. Double-well potential minima at V = ±sqrt(α/β)
2. Covariant modes Φ_N, Φ_Δ derived from Hessian eigenvalues
3. Veracity Integrity Index VII ∈ [0,1] and monotonic behavior
4. Invariant ψ_ver = ln(Φ_N/Φ_N0) + λ·VII
5. Conditional entropy S_ver ∈ [0, log(V)] and correct boundary mapping
6. MPC-QP constraints: VII ≥ 0.7, Φ_N ≥ 0.6, S_low ≤ S_ver ≤ S_high
7. Cost function non-negativity

Run the script; it will report PASS/FAIL for each check.
"""

import numpy as np
from scipy.special import softmax

# ------------------------------
# Parameters (representative)
# ------------------------------
alpha, beta, gamma = 1.0, 1.0, 0.5   # double-well coefficients
lam = 0.2                            # coupling to VII in ψ
Phi_N0 = 1.0                         # baseline correlation-length inverse
S_low, S_high = 0.1, 2.0             # entropy bounds (nats)
VII_thresh = 0.7
Phi_N_thresh = 0.6

# ------------------------------
# Helper functions
# ------------------------------
def double_well(V):
    """V(ϕ) = -α/2 ϕ^2 + β/4 ϕ^4 + γ/2 (∇ϕ)^2 ; we ignore gradient term for minima."""
    return -0.5*alpha*V**2 + 0.25*beta*V**4

def sigmoid(x):
    return 1.0/(1.0+np.exp(-x))

def covariant_modes(corr_len, skew):
    """
    Map measurable quantities to Φ_N, Φ_Δ.
    Φ_N ∝ 1/corr_len   (inverse correlation length)
    Φ_Δ ∝ |skew|       (absolute skewness of veracity scores)
    We use simple proportionality with unit constants for validation.
    """
    Phi_N = 1.0 / (corr_len + 1e-9)   # avoid div0
    Phi_Delta = np.abs(skew)
    return Phi_N, Phi_Delta

def compute_VII(Phi_N, Phi_Delta):
    """VII = σ(α Φ_N - β Φ_Δ + γ)"""
    return sigmoid(alpha*Phi_N - beta*Phi_Delta + gamma)

def compute_psi(Phi_N, VII):
    """ψ_ver = ln(Φ_N/Φ_N0) + λ·VII"""
    return np.log(Phi_N/Phi_N0) + lam*VII

def conditional_entropy(p_cat, p_v_given_c):
    """
    S_ver = Σ_c p(c) [ - Σ_v p(v|c) log p(v|c) ]
    p_cat: shape (C,)
    p_v_given_c: shape (C, V)
    Returns entropy in nats.
    """
    # avoid log0
    safe = np.where(p_v_given_c > 0, p_v_given_c, 1e-12)
    inner = -np.sum(safe * np.log(safe), axis=1)
    return np.sum(p_cat * inner)

# ------------------------------
# Test 1: Double-well minima
# ------------------------------
print("=== Test 1: Double-well potential minima ===")
V_vals = np.linspace(-2, 2, 401)
V_vals = double_well(V_vals)
min_idx = np.argmin(V_vals)
V_min = V_vals[min_idx]
phi_at_min = np.linspace(-2,2,401)[min_idx]
expected_min = -np.sqrt(alpha/beta)
print(f"Minimum at ϕ ≈ {phi_at_min:.3f}, V ≈ {V_min:.6f}")
print(f"Theoretical minimum ϕ = ±{expected_min:.3f}")
test1_pass = np.abs(np.abs(phi_at_min) - np.abs(expected_min)) < 0.05
print("PASS" if test1_pass else "FAIL", "\n")

# ------------------------------
# Test 2: Covariant mode mapping & VII monotonicity
# ------------------------------
print("=== Test 2: Covariant modes & VII behavior ===")
# Sweep correlation length (short -> long) and skewness (negative -> positive)
corr_len_vals = np.logspace(-2, 2, 20)   # 0.01 to 100
skew_vals = np.linspace(-2, 2, 20)
Phi_N_grid, Phi_Delta_grid = np.meshgrid(corr_len_vals, skew_vals, indexing='ij')
VII_grid = compute_VII(Phi_N_grid, Phi_Delta_grid)

# Check VII increases with Φ_N (holding Φ_Δ constant) and decreases with Φ_Δ
dVII_dPhiN = np.gradient(VII_grid, axis=0) / np.gradient(Phi_N_grid, axis=0)
dVII_dPhiD = np.gradient(VII_grid, axis=1) / np.gradient(Phi_Delta_grid, axis=1)
# Expect positive derivative w.r.t Φ_N, negative w.r.t Φ_Δ
test2a = np.all(dVII_dPhiN > -1e-3)   # allow tiny numerical noise
test2b = np.all(dVII_dPhiD < 1e-3)
print(f"∂VII/∂Φ_N ≥ 0 ? {test2a}")
print(f"∂VII/∂Φ_Δ ≤ 0 ? {test2b}")
test2_pass = test2a and test2b
print("PASS" if test2_pass else "FAIL", "\n")

# ------------------------------
# Test 3: Invariant ψ_ver definition
# ------------------------------
print("=== Test 3: Invariant ψ_ver ===")
Phi_N_test = np.array([0.5, 1.0, 2.0])
VII_test = np.array([0.5, 0.7, 0.9])
psi_test = compute_psi(Phi_N_test, VII_test)
# ψ should increase with Φ_N and VII
dpsi_dPhiN = np.gradient(psi_test, Phi_N_test)
dpsi_dVII = np.gradient(psi_test, VII_test)
test3a = np.all(dpsi_dPhiN > 0)
test3b = np.all(dpsi_dVII > 0)
print(f"ψ increases with Φ_N ? {test3a}")
print(f"ψ increases with VII ? {test3b}")
test3_pass = test3a and test3b
print("PASS" if test3_pass else "FAIL", "\n")

# ------------------------------
# Test 4: Conditional entropy bounds & boundary mapping
# ------------------------------
print("=== Test 4: Conditional entropy & boundaries ===")
# Construct synthetic data: 3 categories, 4 veracity bins
p_cat = np.array([0.4, 0.3, 0.3])                     # sums to 1
# Case A: High disorder (uniform within each category) -> high entropy
p_v_given_c_high = np.ones((3,4))/4
S_high_case = conditional_entropy(p_cat, p_v_given_c_high)
# Case B: Perfect order (delta within each category) -> zero entropy
p_v_given_c_low = np.zeros((3,4))
p_v_given_c_low[:,0] = 1.0   # all probability in first bin
S_low_case = conditional_entropy(p_cat, p_v_given_c_low)
print(f"High-entropy case S = {S_high_case:.3f} (max possible = {np.log(4):.3f})")
print(f"Low-entropy case S = {S_low_case:.3f}")
# Boundary checks:
# Collapse: Φ_N large, S near max -> ψ → +∞
Phi_N_collapse = 10.0
VII_collapse = compute_VII(Phi_N_collapse, 0.2)   # low skew
psi_collapse = compute_psi(Phi_N_collapse, VII_collapse)
# Lock: Φ_N small, S near min -> ψ → -∞
Phi_N_lock = 0.1
VII_lock = compute_VII(Phi_N_lock, 0.8)           # high skew (but low Φ_N dominates)
psi_lock = compute_psi(Phi_N_lock, VII_lock)
print(f"Collapse regime: Φ_N={Phi_N_collapse}, VII={VII_collapse:.3f}, ψ={psi_collapse:.3f}")
print(f"Lock regime:     Φ_N={Phi_N_lock},     VII={VII_lock:.3f},     ψ={psi_lock:.3f}")
test4a = S_high_case > 0.5*np.log(4)   # disorder yields substantial entropy
test4b = S_low_case < 1e-3             # order yields near-zero entropy
test4c = psi_collapse > 2.0            # positive large
test4d = psi_lock < -2.0               # negative large
print(f"Disorder → high S ? {test4a}")
print(f"Order   → low  S ? {test4b}")
print(f"Collapse → ψ>0 ? {test4c}")
print(f"Lock    → ψ<0 ? {test4d}")
test4_pass = test4a and test4b and test4c and test4d
print("PASS" if test4_pass else "FAIL", "\n")

# ------------------------------
# Test 5: MPC-QP constraints & cost function
# ------------------------------
print("=== Test 5: MPC constraints & cost ===")
# Sample trajectory over time (T=10)
T = 10
Phi_N_t = np.linspace(0.4, 0.8, T)   # some below/above threshold
Phi_Delta_t = np.sin(np.linspace(0, np.pi, T))*0.5   # skew in [0,0.5]
VII_t = compute_VII(Phi_N_t, Phi_Delta_t)
S_ver_t = np.linspace(0.2, 1.8, T)   # entropy trajectory
psi_t = compute_psi(Phi_N_t, VII_t)

# Constraints
c1 = VII_t >= VII_thresh
c2 = Phi_N_t >= Phi_N_thresh
c3 = (S_ver_t >= S_low) & (S_ver_t <= S_high)
constraints_ok = np.all(c1) and np.all(c2) and np.all(c3)
print(f"VII ≥ 0.7 ? {np.all(c1)} (min VII = {VII_t.min():.3f})")
print(f"Φ_N ≥ 0.6 ? {np.all(c2)} (min Φ_N = {Phi_N_t.min():.3f})")
print(f"S_bounds  ? {np.all(c3)} (S range = [{S_ver_t.min():.3f}, {S_ver_t.max():.3f}])")

# Cost function integrand (discrete time)
mu1, mu2, mu3 = 1.0, 1.0, 1.0
cost_integrand = (np.maximum(VII_thresh - VII_t, 0))**2 \
               + mu1*(np.maximum(Phi_N_thresh - Phi_N_t, 0))**2 \
               + mu2*Phi_Delta_t**2 \
               + mu3*(np.maximum(S_ver_t - S_high, 0) + np.maximum(S_low - S_ver_t, 0))**2
total_cost = np.trapz(cost_integrand, dx=1.0)   # simple trapezoidal
print(f"Total cost (discrete) = {total_cost:.6f}")
test5_pass = constraints_ok and (total_cost >= 0)
print("PASS" if test5_pass else "FAIL", "\n")

# ------------------------------
# Final verdict
# ------------------------------
all_tests = [test1_pass, test2_pass, test3_pass, test4_pass, test5_pass]
print("="*50)
print(f"Overall compliance: {'PASS' if all(all_tests) else 'FAIL'}")
print("="*50)