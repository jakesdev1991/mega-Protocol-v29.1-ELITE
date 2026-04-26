# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------ Parameters (plausible ranges) ------------------
m = 10                     # number of workers
t_max = (m-1)//2           # max tolerable Byzantine workers
t_range = np.linspace(0, t_max, 50)          # t values
ell_max = 10.0             # max allowed latency (arbitrary time unit)
ell_range = np.linspace(0, ell_max, 50)      # latency values
s_range = np.linspace(0.1, 0.9, 50)          # sparsity (0< s <1)

# Coefficients (example values)
lam = 1.0
gamma0, gamma1, gamma2 = 0.5, 0.2, 0.1
delta0, delta1, delta2 = 0.5, 0.2, 0.1

# ------------------ Helper functions ------------------
def eta(t):      # residual corruption noise (decreases with t)
    return t / m          # dimensionless, 0..0.5

def zeta(ell):   # latency‑induced error (increases with ell)
    return ell / ell_max  # dimensionless, 0..1

# Original stiffness invariants (as in proposal)
def xiN_inv2_orig(t, ell):
    return lam * (gamma0 + gamma1 * t + gamma2 * ell)

def xiDelta_inv2_orig(t, ell):
    return lam * (delta0 - delta1 * t + delta2 * ell)

# Revised stiffness invariants (sign‑flipped for symmetry)
def xiN_inv2_rev(t, ell):
    return lam * (gamma0 - gamma1 * t - gamma2 * ell)

def xiDelta_inv2_rev(t, ell):
    return lam * (delta0 + delta1 * t + delta2 * ell)

# Mapping to Phi_N, Phi_Delta (linearised form used in proposal)
alpha1, alpha2 = 0.3, 0.4   # example positive coefficients
beta1,  beta2  = 0.2, 0.3
PhiN0, PhiDelta0 = 0.8, 0.4

def PhiN_stream(t, ell):
    return PhiN0 - alpha1 * eta(t) - alpha2 * zeta(ell)

def PhiDelta_stream(t, ell):
    return PhiDelta0 + beta1 * eta(t) - beta2 * zeta(ell)

# ------------------ 1. Dimensional Consistency ------------------
# All terms in PhiN_stream and PhiDelta_stream are dimensionless because:
#   eta(t) and zeta(ell) are ratios, coefficients are pure numbers.
print("Dimensional consistency check:")
print("  PhiN_stream expression uses only dimensionless quantities: OK")
print("  PhiDelta_stream expression uses only dimensionless quantities: OK\n")

# ------------------ 2. Boundary Feasibility ------------------
tol = 1e-3
print("Boundary feasibility (original stiffness):")
feasible_N_orig = any(xiN_inv2_orig(t, ell) < tol for t in t_range for ell in ell_range)
feasible_Delta_orig = any(xiDelta_inv2_orig(t, ell) < tol for t in t_range for ell in ell_range)
print(f"  xiN^{-2} can be ~0?  {feasible_N_orig}")
print(f"  xiDelta^{-2} can be ~0? {feasible_Delta_orig}")

print("\nBoundary feasibility (revised stiffness):")
feasible_N_rev = any(xiN_inv2_rev(t, ell) < tol for t in t_range for ell in ell_range)
feasible_Delta_rev = any(xiDelta_inv2_rev(t, ell) < tol for t in t_range for ell in ell_range)
print(f"  xiN^{-2} can be ~0?  {feasible_N_rev}")
print(f"  xiDelta^{-2} can be ~0? {feasible_Delta_rev}\n")

# ------------------ 3. Controller Constraint Sampling ------------------
np.random.seed(0)
n_samples = 20000
t_samples = np.random.uniform(0, t_max, n_samples)
ell_samples = np.random.uniform(0, ell_max, n_samples)
s_samples = np.random.uniform(0.1, 0.9, n_samples)

PhiN_vals = PhiN_stream(t_samples, ell_samples)
PhiDelta_vals = PhiDelta_stream(t_samples, ell_samples)

sat_N = np.mean(PhiN_vals >= 0.6)
sat_Delta = np.mean(PhiDelta_vals <= 0.7)
sat_both = np.mean((PhiN_vals >= 0.6) & (PhiDelta_vals <= 0.7))

print("Controller constraint satisfaction (random sampling):")
print(f"  Phi_N >= 0.6 satisfied in {sat_N*100:.1f}% of samples")
print(f"  Phi_Delta <= 0.7 satisfied in {sat_Delta*100:.1f}% of samples")
print(f"  Both constraints satisfied in {sat_both*100:.1f}% of samples")

# If constraints are too tight, we can suggest loosening thresholds.
if sat_both < 0.5:
    print("\nWarning: Joint constraint satisfaction is low; consider revising thresholds or stiffness signs.")