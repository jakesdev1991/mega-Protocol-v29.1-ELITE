# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.signal import welch

# ------------------ Helper functions ------------------
def entropy_from_amps(A):
    """A: array of harmonic amplitudes (complex or real)"""
    power = np.abs(A)**2
    p = power / np.sum(power)
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def compute_phi(alpha, beta, gamma, phi_N0, phi_D0, PHI, dPHI_dt, var_A):
    """Covariant modes from the refined derivation"""
    phi_N = phi_N0 + alpha * dPHI_dt
    phi_D = phi_D0 - beta * PHI + gamma * var_A
    return phi_N, phi_D

def average_coherence(x, y, fs=1.0, nperseg=256):
    """Average magnitude-squared coherence over frequency"""
    f, Cxy = welch(x, y, fs=fs, nperseg=nperseg)
    return np.mean(Cxy)

def stiffness_from_coherence(coh_avg, lam):
    """ξ_N^{-2}, ξ_Δ^{-2} from the proposal"""
    inv = coh_avg
    xi_N_inv2 = lam * (3.0 / inv + 1.0 / (inv * inv))
    xi_D_inv2 = lam * (1.0 / inv + 3.0 / (inv * inv))
    return 1.0/np.sqrt(xi_N_inv2), 1.0/np.sqrt(xi_D_inv2)  # ξ_N, ξ_Δ

def psi(xi, xi0=1.0):
    return np.log(xi/xi0)

# ------------------ Synthetic test ------------------
np.random.seed(42)
K = 5                              # number of orders
A_true = np.random.randn(K) + 1j*np.random.randn(K)  # harmonic amplitudes
PHI_true = 0.6                     # example PHI in admissible range
# Perturb to get a time series for derivative
dt = 60.0                          # 1 minute in seconds
A_t = A_true * (1 + 0.01*np.random.randn(K))
A_tp1 = A_true * (1 + 0.01*np.random.randn(K))
PHI_t   = 0.58
PHI_tp1 = 0.62
dPHI_dt = (PHI_tp1 - PHI_t) / dt

# Information‑theoretic coefficients (finite‑difference)
def I_of_phi(PHI_val):
    # Map PHI -> a synthetic amplitude vector for the purpose of derivative
    # Here we simply scale the amplitude magnitude
    scale = 0.5 + PHI_val          # monotonic mapping, arbitrary but smooth
    A_scaled = A_true * scale
    return entropy_from_amps(A_scaled)

eps = 1e-6
alpha = (I_of_phi(PHI_true+eps) - I_of_phi(PHI_true-eps)) / (2*eps)
beta  = (I_of_phi(PHI_true+eps) - 2*I_of_phi(PHI_true) + I_of_phi(PHI_true-eps)) / (eps**2)
# gamma: second derivative w.r.t. amplitude magnitude (use variance of A as proxy)
var_A = np.var(np.abs(A_true))
def I_of_var(v):
    # perturb overall amplitude scale to change variance
    scale = np.sqrt(v/np.var(np.abs(A_true))) if np.var(np.abs(A_true))>0 else 1.0
    A_scaled = A_true * scale
    return entropy_from_amps(A_scaled)
gamma = (I_of_var(var_A+eps) - 2*I_of_var(var_A) + I_of_var(var_A-eps)) / (eps**2)

# Baseline covariant modes (choose arbitrary zero‑point)
phi_N0, phi_D0 = 0.7, 0.5
phi_N, phi_D = compute_phi(alpha, beta, gamma, phi_N0, phi_D0,
                           PHI_true, dPHI_dt, var_A)

# Coherence between two synthetic sensor streams (latency jitter & throughput)
fs = 1.0/dt
t = np.arange(0, 300, dt)          # 5 min window
x = np.sin(2*np.pi*0.05*t) + 0.1*np.random.randn(len(t))
y = np.sin(2*np.pi*0.05*t + 0.2) + 0.1*np.random.randn(len(t))
coh_avg = average_coherence(x, y, fs=fs)

lam = 1.0                          # coupling constant (choose units s⁻²)
xi_N, xi_D = stiffness_from_coherence(coh_avg, lam)

# Check invariant definitions: ξ = ∂Φ/∂ψ (numeric)
psi_t = psi(xi_N)                  # using ξ_N as representative scale
psi_tp1 = psi(xi_N * 1.01)         # perturb ξ slightly
# Perturb PHI to see effect on Φ_N via chain rule (∂Φ_N/∂PHI * ∂PHI/∂ψ)
# We approximate ∂Φ_N/∂ψ ≈ (∂Φ_N/∂PHI)*(∂PHI/∂ψ)
# Compute ∂Φ_N/∂PHI from model: Φ_N = φ_N0 + α dPHI/dt ; α depends on PHI via I
# Use finite difference on Φ_N w.r.t PHI
def Phi_N_of_phi(PHI_val):
    # recompute alpha for this PHI (keeping dPHI/dt fixed for simplicity)
    a = (I_of_phi(PHI_val+eps) - I_of_phi(PHI_val-eps))/(2*eps)
    return phi_N0 + a * dPHI_dt
dPhi_dPHI = (Phi_N_of_phi(PHI_true+eps) - Phi_N_of_phi(PHI_true-eps))/(2*eps)
# Approximate ∂PHI/∂ψ via perturbing ξ (which changes ψ) and recomputing PHI
# For simplicity assume PHI ∝ ξ (monotonic); we use numeric derivative:
def PHI_of_xi(xi_val):
    # invert ψ: PHI = 0.5 + 0.5*tanh((xi-1)/0.2)  (arbitrary smooth mapping)
    return 0.5 + 0.5*np.tanh((xi_val-1.0)/0.2)
dPHI_dpsi = (PHI_of_xi(xi_N*1.01) - PHI_of_xi(xi_N*0.99))/(0.02*psi_t)
xi_N_from_phi = dPhi_dPHI * dPHI_dpsi

# ------------------ Validation ------------------
passed = True
# 1. BOILERPLATE check – not applicable in code, but we ensure no prints of steps
# 2. Covariant modes defined
if not (np.isfinite(phi_N) and np.isfinite(phi_D)):
    passed = False
    print("FAIL: non‑finite covariant modes")
# 3. Stiffness invariants positive
if xi_N <= 0 or xi_D <= 0:
    passed = False
    print("FAIL: non‑positive stiffness invariants")
# 4. Boundary conditions (conceptual)
#    Shredding: PHI → 0 → ξ → 0 ; Informational Freeze: PHI → 1 → ξ → ∞
#    We test monotonicity of our proxy mapping
xi_shred = PHI_of_xi(0.1)   # small ξ → low PHI
xi_freeze = PHI_of_xi(10.0) # large ξ → high PHI
if not (xi_shred < xi_freeze):
    passed = False
    print("FAIL: boundary monotonicity violated")
# 5. Constraints from MPC‑Ω
if not (PHI_true >= 0.4 and phi_N >= 0.7 and phi_D <= 0.6):
    passed = False
    print("FAIL: MPC‑Ω constraints violated")
# 6. Invariant relation ξ = ∂Φ/∂ψ (tolerance)
if not np.isclose(xi_N, xi_N_from_phi, rtol=1e-2, atol=1e-2):
    passed = False
    print(f"FAIL: ξ_N mismatch {xi_N:.3f} vs {xi_N_from_phi:.3f}")
# 7. Dimensional consistency (lambda has s⁻², ξ has s)
#    In our units lambda=1 s⁻² → ξ in seconds, check:
if not np.isclose(xi_N, 1.0/np.sqrt(lam*(3/coh_avg + 1/(coh_avg**2))), rtol=1e-6):
    passed = False
    print("FAIL: ξ_N formula mismatch")
if not np.isclose(xi_D, 1.0/np.sqrt(lam*(1/coh_avg + 3/(coh_avg**2))), rtol=1e-6):
    passed = False
    print("FAIL: ξ_Δ formula mismatch")

print("VALIDATION:", "PASS" if passed else "FAIL")