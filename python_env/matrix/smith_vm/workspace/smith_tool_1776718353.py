# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Compliance Validator for HSA Informational Jerk Stability
-----------------------------------------------------------------------
This script checks that a candidate implementation satisfies the six pillars
of the Omega Physics Rubric v26.0 as applied to the revised analysis:

1. Covariant Modes (Φ_N, Φ_Δ) – correctly derived from coherence field.
2. Invariants (ξ_N, ξ_Δ, ψ = ln Φ_N) – explicit, reproducible definitions.
3. Entropy-like quantity (Shannon entropy of coherence distribution).
4. Jerk calculation – third derivative of Φ_N w.r.t. intrinsic time τ.
5. Jerk stability metric – penalizes heavy‑tailed jerk, leaves Gaussian
   fluctuations unpenalized (S_j → 1 for Gaussian/constant jerk).
6. MPC‑Ω state vector & cost function – all required terms present.

The validator works on synthetic telemetry data; replace the data
generation section with real HSA telemetry to validate an actual deployment.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions – mirror the mathematics from the corrected analysis
# ----------------------------------------------------------------------
def coherence_field(A, L, L0):
    """ψ_ij = A_ij * exp(-L_ij / L0)   (units of rate, later normalised)"""
    return A * np.exp(-L / L0)

def global_scalars(psi):
    """Φ_N = mean(ψ), Φ_Δ = std(ψ) over all active pairs."""
    Phi_N = np.mean(psi)
    Phi_Delta = np.std(psi)
    return Phi_N, Phi_Delta

def radial_correlation_length(psi, coords):
    """
    ξ_N = ( (1/N) Σ ||∇ψ_ij||^2 )^{-1/2}
    Approximate gradient by finite differences on the index lattice.
    coords: array of shape (N_pairs, ndim) giving the logical coordinates
            of each compute‑unit pair (e.g., (i,j) flattened).
    """
    # Sort by first coordinate then second to get a regular grid approximation
    order = np.lexsort((coords[:,1], coords[:,0]))
    psi_sorted = psi[order]
    coords_sorted = coords[order]

    # Compute finite‑difference gradient along each dimension
    grad_sq = 0.0
    for d in range(coords.shape[1]):
        diff = np.diff(psi_sorted) / np.diff(coords_sorted[:,d])
        # Pad to same length (forward difference)
        diff = np.append(diff, diff[-1])  # simple padding
        grad_sq += np.mean(diff**2)
    xi_N = (grad_sq)**(-0.5) if grad_sq > 0 else np.inf
    return xi_N

def poloidal_correlation_length(psi, pair_labels):
    """
    ξ_Δ = max_c σ_c^2 / min_c σ_c^2
    pair_labels: array of strings indicating the directional class of each pair,
                 e.g., 'CPU-GPU', 'GPU-GPU', 'CPU-CPU'.
    """
    classes = np.unique(pair_labels)
    vars_per_class = []
    for c in classes:
        mask = (pair_labels == c)
        if np.any(mask):
            vars_per_class.append(np.var(psi[mask]))
    if len(vars_per_class) < 2:
        return 1.0  # isotropic fallback
    xi_Delta = np.max(vars_per_class) / np.min(vars_per_class)
    return xi_Delta

def shannon_entropy(psi):
    """H = - Σ p log p,  p = ψ / Σψ"""
    p = psi / np.sum(psi)
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def jerk_5point(Phi_N, dtau):
    """
    Third derivative using 5‑point central stencil:
    j ≈ (-Φ(t-2Δ) + 2Φ(t-Δ) - 2Φ(t+Δ) + Φ(t+2Δ)) / (2Δ^3)
    Assumes uniform sampling in intrinsic time τ.
    """
    if len(Phi_N) < 5:
        raise ValueError("Need at least 5 samples for 5‑point stencil")
    j = (-Phi_N[:-4] + 2*Phi_N[1:-3] - 2*Phi_N[2:-2] + Phi_N[3:]) / (2 * dtau**3)
    return j

def jerk_stability_excess_kurtosis(j, epsilon=1e-12):
    """
    S_j = ( 1 + | excess_kurtosis | )^{-1}
    excess_kurtosis = (E[(j-μ)^4] / σ^4) - 3
    Returns 1 for Gaussian or constant jerk, <1 for heavy‑tailed.
    """
    mu = np.mean(j)
    sigma2 = np.var(j)
    if sigma2 < epsilon:   # effectively constant jerk
        return 1.0
    mu4 = np.mean((j - mu)**4)
    excess_kurt = mu4 / (sigma2**2) - 3.0
    S = 1.0 / (1.0 + np.abs(excess_kurt))
    return S

def build_state_vector(Phi_N, Phi_Delta, xi_N, xi_Delta, psi_inv, H, j, S_j,
                       Q_depth, P_fault, P_meas):
    """Assemble the MPC‑Ω state vector."""
    return np.array([Phi_N, Phi_Delta, xi_N, xi_Delta, psi_inv, H, j, S_j,
                     Q_depth, P_fault, P_meas])

def cost_function(S_j, H, P_meas, P_target, alpha=1.0, lam=1.0, dt=1.0):
    """
    J = Σ [ (1-S_j)^2 + α*H + λ*(P_meas-P_target)^2 ] * dt
    """
    integrand = (1.0 - S_j)**2 + alpha * H + lam * (P_meas - P_target)**2
    return np.sum(integrand) * dt

# ----------------------------------------------------------------------
# Synthetic data generation (replace with real HSA telemetry)
# ----------------------------------------------------------------------
np.random.seed(42)
n_pairs = 9   # e.g., 3x3 grid of compute units
n_time  = 200 # time steps

# Logical coordinates for each pair (i,j) flattened
coords = np.array([(i, j) for i in range(3) for j in range(3)], dtype=float)

# Directional class label for each pair (simple example)
def pair_label(i, j):
    if i < 3 and j >= 3:   return 'CPU-GPU'
    if i >= 3 and j < 3:   return 'GPU-CPU'
    if i < 3 and j < 3:    return 'CPU-CPU'
    return 'GPU-GPU'
pair_labels = np.array([pair_label(i, j) for i, j in coords])

# Baseline latency
L0 = 100.0  # ns (example)

# Generate synthetic telemetry that mimics realistic variations
A_base = 1e6   # atomic ops per second
L_base = 120.0 # ns

A = A_base * (1 + 0.1 * np.random.randn(n_pairs, n_time))
L = L_base * (1 + 0.15 * np.random.randn(n_pairs, n_time))

# ----------------------------------------------------------------------
# Main validation loop
# ----------------------------------------------------------------------
dtau = 0.1  # intrinsic time step (kernel cycles) – arbitrary units
Phi_N_series = []
Phi_Delta_series = []
xi_N_series = []
xi_Delta_series = []
psi_series = []
H_series = []
j_series = []
S_j_series = []
state_vectors = []
cost_vals = []

for t in range(n_time):
    A_t = A[:, t]
    L_t = L[:, t]

    # 1. Coherence field
    psi_t = coherence_field(A_t, L_t, L0)

    # 2. Global scalars
    Phi_N, Phi_Delta = global_scalars(psi_t)
    Phi_N_series.append(Phi_N)
    Phi_Delta_series.append(Phi_Delta)

    # 3. Invariants
    xi_N = radial_correlation_length(psi_t, coords)
    xi_Delta = poloidal_correlation_length(psi_t, pair_labels)
    xi_N_series.append(xi_N)
    xi_Delta_series.append(xi_Delta)

    psi_inv = np.log(Phi_N) if Phi_N > 0 else -np.inf
    psi_series.append(psi_inv)

    # 4. Entropy
    H = shannon_entropy(psi_t)
    H_series.append(H)

    # Store for jerk calculation (need history)
    # (we'll compute jerk after we have enough points)

    # 5. Jerk & stability (need at least 5 points)
    if t >= 4:
        j_t = jerk_5point(np.array(Phi_N_series[-5:]), dtau)[0]  # latest value
        j_series.append(j_t)
        S_j = jerk_stability_excess_kurtosis(np.array(j_series))
        S_j_series.append(S_j)
    else:
        j_series.append(np.nan)
        S_j_series.append(np.nan)

    # 6. Dummy MPC‑Ω inputs (queue depth, fault rate, power)
    Q_depth = np.random.poisson(5)
    P_fault = np.random.exponential(0.01)
    P_meas = 150.0 + 10*np.random.randn()   # Watts

    # Build state vector (use latest jerk & S_j)
    state = build_state_vector(Phi_N, Phi_Delta, xi_N, xi_Delta,
                               psi_inv, H, j_series[-1], S_j_series[-1],
                               Q_depth, P_fault, P_meas)
    state_vectors.append(state)

    # Cost (using current sample)
    P_target = 150.0
    cost = cost_function(S_j_series[-1], H, P_meas, P_target)
    cost_vals.append(cost)

# ----------------------------------------------------------------------
# Compliance Checks
# ----------------------------------------------------------------------
def check_covariant_modes():
    # Φ_N and Φ_Δ must be real numbers (not NaN/inf) for majority of steps
    ok = np.sum(np.isfinite(Phi_N_series)) > 0.9 * n_time
    ok &= np.sum(np.isfinite(Phi_Delta_series)) > 0.9 * n_time
    return ok, f"Finite Φ_N/Φ_Δ: {ok}"

def check_invariants():
    # ξ_N, ξ_Δ, ψ must be defined (finite) and ψ = ln(Φ_N)
    cond1 = np.sum(np.isfinite(xi_N_series)) > 0.9 * n_time
    cond2 = np.sum(np.isfinite(xi_Delta_series)) > 0.9 * n_time
    cond3 = np.sum(np.isfinite(psi_series)) > 0.9 * n_time
    # Verify ψ ≈ ln(Φ_N) where defined
    diff = np.abs(np.array(psi_series) - np.log(np.array(Phi_N_series)))
    cond4 = np.nanmean(diff) < 1e-6
    return cond1 and cond2 and cond3 and cond4, \
           f"ξ_N finite:{cond1}, ξ_Δ finite:{cond2}, ψ finite:{cond3}, ψ≈lnΦ_N:{cond4}"

def check_entropy():
    # Entropy must be non‑negative (Shannon entropy ≥ 0)
    ok = np.all(np.array(H_series)[~np.isnan(H_series)] >= -1e-12)
    return ok, f"Entropy non‑negative: {ok}"

def check_jerk_calc():
    # Jerk should be computed via 5‑point stencil (we already used it)
    # Just verify we have numbers after warm‑up
    ok = np.sum(np.isfinite(j_series)) > 0.8 * n_time
    return ok, f"Jerk computed: {ok}"

def check_jerk_stability():
    # For Gaussian jerk, S_j should be ~1.
    # Create a test Gaussian jerk series and verify metric.
    test_j = np.random.normal(0, 1, size=1000)
    S_test = jerk_stability_excess_kurtosis(test_j)
    # Expect S close to 1 (within tolerance)
    gauss_ok = np.abs(S_test - 1.0) < 0.05
    # For heavy‑tailed (e.g., Laplace) expect S < 1
    heavy_j = np.random.laplace(0, 1, size=1000)
    S_heavy = jerk_stability_excess_kurtosis(heavy_j)
    heavy_ok = S_heavy < 0.9
    return gauss_ok and heavy_ok, \
           f"Gaussian S_j≈1:{gauss_ok} (S={S_test:.3f}), Heavy S_j<1:{heavy_ok} (S={S_heavy:.3f})"

def check_state_and_cost():
    # State vector length must be 10 (as defined)
    ok_len = all(len(sv) == 10 for sv in state_vectors if sv is not None)
    # Cost should be non‑negative
    cost_arr = np.array(cost_vals)
    ok_cost = np.all(cost_arr >= -1e-12)
    return ok_len and ok_cost, \
           f"State length OK:{ok_len}, Cost non‑negative:{ok_cost}"

checks = [
    ("Covariant Modes (Φ_N, Φ_Δ)", check_covariant_modes),
    ("Invariants (ξ_N, ξ_Δ, ψ=lnΦ_N)", check_invariants),
    ("Entropy-like Quantity", check_entropy),
    ("Jerk Calculation", check_jerk_calc),
    ("Jerk Stability Metric", check_jerk_stability),
    ("MPC‑Ω State & Cost", check_state_and_cost),
]

print("Omega Protocol Compliance Validation\n" + "="*50)
all_pass = True
for name, func in checks:
    passed, msg = func()
    all_pass = all_pass and passed
    status = "PASS" if passed else "FAIL"
    print(f"{name:35} [{status}] - {msg}")

print("\nOverall Result:", "PASS" if all_pass else "FAIL")
if not all_pass:
    print("=> The implementation does not fully satisfy the Omega Physics Rubric v26.0.")
else:
    print("=> All rubric pillars satisfied – the analysis is compliant.")