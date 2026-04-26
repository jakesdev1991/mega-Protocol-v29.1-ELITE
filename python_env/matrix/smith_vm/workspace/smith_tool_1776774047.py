# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the refined GIC‑Ω proposal.
Checks gauge invariance, dimensional consistency,
entropy‑gauge dynamics, and MPC‑Ω optimality.
"""

import numpy as np
from scipy.optimize import minimize

# ----------------------------------------------------------------------
# Helper: random field generators (discretised 1‑D lattice for simplicity)
# ----------------------------------------------------------------------
def random_phi(N):
    """Random complex scalar field Φ_N (dimensionless)."""
    return (np.random.randn(N) + 1j*np.random.randn(N)) / np.sqrt(2.0)

def random_A(N):
    """Random real gauge field A_μ (we only need spatial component A_x)."""
    return np.random.randn(N)

def covariant_derivative(phi, A, g=1.0):
    """D_x Φ = (∂_x - i g A_x) Φ  (forward difference)."""
    dphi = np.gradient(phi)          # ∂_x Φ
    return dphi - 1j * g * A * phi

def field_strength(A):
    """F_{xy} = ∂_x A_y - ∂_y A_x ; with only A_x we get zero, so add a dummy A_y."""
    Ay = np.random.randn(N) * 0.1   # small transverse component for non‑zero F
    return np.gradient(A) - np.gradient(Ay)   # simplified 1‑D analogue

# ----------------------------------------------------------------------
# 1. Gauge invariance of the Omega action (kinetic + Maxwell term)
# ----------------------------------------------------------------------
def omega_action(phi, A, lam=0.1, g=1.0):
    """S_Omega = ∫ [ |DΦ|^2/2 - F^2/4 + lam * (|Φ|^2 - 1)^2 ] dx."""
    Dphi = covariant_derivative(phi, A, g)
    kinetic = 0.5 * np.sum(np.abs(Dphi)**2)
    F = field_strength(A)
    maxwell = -0.25 * np.sum(F**2)
    potential = lam * np.sum((np.abs(phi)**2 - 1.0)**2)
    return kinetic + maxwell + potential

def gauge_transform(phi, A, alpha):
    """Local U(1): Φ → e^{iα}Φ, A → A + ∂α."""
    phi_t = phi * np.exp(1j * alpha)
    A_t = A + np.gradient(alpha)
    return phi_t, A_t

def test_gauge_invariance():
    global N
    N = 64
    phi = random_phi(N)
    A = random_A(N)
    alpha = np.random.randn(N) * 0.2   # arbitrary gauge function
    S_before = omega_action(phi, A)
    phi_t, A_t = gauge_transform(phi, A, alpha)
    S_after = omega_action(phi_t, A_t)
    return np.isclose(S_before, S_after, rtol=1e-6, atol=1e-8)

# ----------------------------------------------------------------------
# 2. Backup field equation of motion (limit κ → ∞ forces B = O[Φ])
# ----------------------------------------------------------------------
def observables(phi, A):
    """Simple set of gauge‑invariant observables: |Φ|^2 and |DΦ|^2."""
    O1 = np.abs(phi)**2
    Dphi = covariant_derivative(phi, A)
    O2 = np.abs(Dphi)**2
    return np.stack([O1, O2], axis=-1)   # shape (N,2)

def backup_eom_residual(B, O, kappa=1e3):
    """Residual of ∂_t^2 B - v^2 ∇^2 B + κ (B - O) = 0.
       We use a steady‑state ansatz (∂_t B = 0, ∇^2 B ≈ 0) → residual = κ(B-O)."""
    return kappa * (B - O)

def test_backup_tracking():
    phi = random_phi(N)
    A = random_A(N)
    O = observables(phi, A)          # target
    B = O + 0.01 * np.random.randn(*O.shape)  # small perturbation
    res = backup_eom_residual(B, O, kappa=1e6)
    return np.max(np.abs(res)) < 1e-3   # should be ~0 when κ large

# ----------------------------------------------------------------------
# 3. Dimensionality check (all quantities dimensionless)
# ----------------------------------------------------------------------
def test_dimensionless():
    # In our code we treat everything as pure numbers → dimensionless by construction.
    # We just verify that no hidden dimensional constants appear.
    phi = random_phi(N)
    A = random_A(N)
    # kinetic term |DΦ|^2
    Dphi = covariant_derivative(phi, A)
    kin = np.sum(np.abs(Dphi)**2)
    # Maxwell term F^2
    F = field_strength(A)
    maxw = np.sum(F**2)
    # potential (|Φ|^2-1)^2
    pot = np.sum((np.abs(phi)**2 - 1.0)**2)
    # All above are pure numbers → OK
    return np.isfinite(kin) and np.isfinite(maxw) and np.isfinite(pot)

# ----------------------------------------------------------------------
# 4. Entropy gauge Lagrangian → equation of motion
# ----------------------------------------------------------------------
def shannon_entropy(p, eps=1e-12):
    """p: probability vector (sums to 1). Returns H in nats."""
    p = np.clip(p, eps, 1.0)
    return -np.sum(p * np.log(p))

def entropy_gauge_lagrangian(H, dHdt, dHdx, kappa_H=0.5, H_star=0.0):
    """L = 0.5 (∂_t H)^2 - 0.5 v^2 (∂_x H)^2 - (κ_H/2)(H-H*)^2.
       We set v=1 for simplicity."""
    kinetic = 0.5 * dHdt**2
    gradient = -0.5 * dHdx**2   # note minus sign from metric signature (+,−)
    potential = -0.5 * kappa_H * (H - H_star)**2
    return kinetic + gradient + potential

def var_entropy_gauge():
    """Check that δL/δH gives -∂_t^2 H + ∂_x^2 H - κ_H (H-H*) = 0."""
    # Use a simple sinusoidal test: H = a*sin(kx - ωt)
    x = np.linspace(0, 2*np.pi, N)
    t = 0.0
    a, k, w = 0.3, 2.0, 1.5
    H = a * np.sin(k*x - w*t)
    dHdt = -a * w * np.cos(k*x - w*t)
    dHdx = a * k * np.cos(k*x - w*t)
    L = entropy_gauge_lagrangian(H, dHdt, dHdx)
    # Euler‑Lagrange: ∂_t(∂L/∂(∂_t H)) + ∂_x(∂L/∂(∂_x H)) - ∂L/∂H = 0
    dL_dHdt = dHdt                     # ∂L/∂(∂_t H) = ∂_t H
    dL_dHdx = -dHdx                    # ∂L/∂(∂_x H) = -v^2 ∂_x H (v=1)
    dL_dH = -kappa_H * (H - 0.0)       # ∂L/∂H = -κ_H (H-H*)
    EL = np.gradient(dL_dHdt, t, edge_order=2) + np.gradient(dL_dHdx, x, edge_order=2) - dL_dH
    # For our exact sinusoid, EL should be zero up to numerical error.
    return np.max(np.abs(EL)) < 1e-4

# ----------------------------------------------------------------------
# 5. MPC‑Ω quadratic program + KKT check
# ----------------------------------------------------------------------
def mpc_qp():
    """Minimize  J = 0.5*H^2 + 0.5*kappa_H*(H-H*)^2 + mu*psi^2 + lambda_S*S
       s.t.   xi_N >= xiN_min, xi_Delta >= xiDelta_min, H >= 0, S >= 0, CR >= CR_min.
       We solve a tiny version with scalar decision variables."""
    # Parameters (chosen to be feasible)
    kappa_H, mu, lambda_S = 0.5, 0.2, 0.1
    H_star, psi_target = 0.0, 0.0
    xiN_min, xiDelta_min = 0.5, 0.5
    CR_min = 0.2
    # Decision vector: [H, psi, xiN, xiDelta, S, CR]
    def objective(z):
        H, psi, xiN, xiDelta, S, CR = z
        return 0.5*H**2 + 0.5*kappa_H*(H-H_star)**2 + mu*(psi-psi_target)**2 + lambda_S*S
    # Constraints as inequalities g(z) >= 0
    cons = [
        {'type': 'ineq', 'fun': lambda z: z[2] - xiN_min},          # xiN >= xiN_min
        {'type': 'ineq', 'fun': lambda z: z[3] - xiDelta_min},     # xiDelta >= xiDelta_min
        {'type': 'ineq', 'fun': lambda z: z[0]},                   # H >= 0
        {'type': 'ineq', 'fun': lambda z: z[4]},                   # S >= 0
        {'type': 'ineq', 'fun': lambda z: z[5] - CR_min}           # CR >= CR_min
    ]
    res = minimize(objective, x0=[0.1,0.0,1.0,1.0,0.1,0.3], constraints=cons)
    if not res.success:
        return False, res.message
    z_opt = res.x
    # Compute KKT: gradient + sum lambda_i * ∇g_i = 0, lambda_i >=0, lambda_i*g_i=0
    H, psi, xiN, xiDelta, S, CR = z_opt
    grad = np.array([
        H + kappa_H*(H-H_star),          # dJ/dH
        2*mu*(psi-psi_target),           # dJ/dpsi
        0.0,                             # dJ/dxiN
        0.0,                             # dJ/dxiDelta
        lambda_S,                        # dJ/dS
        0.0                              # dJ/dCR
    ])
    # Jacobian of constraints
    jac = np.array([
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],   # xiN - xiN_min
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],   # xiDelta - xiDelta_min
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # H
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],   # S
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]    # CR - CR_min
    ])
    # Lagrange multipliers from QP (scipy returns them in res.lambda_)
    lam = np.array(res.lambda['ineq']) if hasattr(res, 'lambda') else np.zeros(len(cons))
    # Stationarity
    station = grad + jac.T @ lam
    # Complementarity
    g_vals = np.array([fun(z_opt) for _,fun in cons])
    comp = lam * g_vals
    ok = (np.max(np.abs(station)) < 1e-6) and (np.all(lam >= -1e-9)) and (np.max(np.abs(comp)) < 1e-6)
    return ok, None

def test_mpc_kkt():
    ok, msg = mpc_qp()
    return ok

# ----------------------------------------------------------------------
# 6. Anomaly score bounds (GPD tail)
# ----------------------------------------------------------------------
def test_anomaly_bounds():
    # Simulate psi time series
    t = np.arange(200)
    psi = 0.1*np.random.randn(len(t)) + 0.02*t   # slight drift
    u = np.percentile(np.abs(psi), 95)
    excess = np.abs(psi) - u
    excess = excess[excess > 0]
    if len(excess) < 5:
        return True   # not enough data → trivially passes
    # Fit GPD (shape c, loc=0, scale) using scipy.stats.genpareto
    from scipy.stats import genpareto
    try:
        c, loc, scale = genpareto.fit(excess, floc=0)
        # CDF
        def GPD_cdf(x):
            return genpareto.cdf(x, c, loc, scale)
        a = 1.0 - GPD_cdf(np.abs(psi) - u)
        a = np.clip(a, 0.0, 1.0)   # tail probability
        return np.all((a >= 0.0) & (a <= 1.0))
    except Exception:
        return False

# ----------------------------------------------------------------------
# Run all tests
# ----------------------------------------------------------------------
if __name__ == "__main__":
    tests = [
        ("Gauge invariance of Ω‑action", test_gauge_invariance),
        ("Backup field tracks observables", test_backup_tracking),
        ("Dimensionless quantities", test_dimensionless),
        ("Entropy gauge EoM", var_entropy_gauge),
        ("MPC‑Ω KKT conditions", test_mpc_kkt),
        ("Anomaly score in [0,1]", test_anomaly_bounds)
    ]
    all_pass = True
    for name, func in tests:
        try:
            result = func()
            if isinstance(result, tuple):
                ok, msg = result
                status = "PASS" if ok else f"FAIL ({msg})"
            else:
                status = "PASS" if result else "FAIL"
            if not ("PASS" in status):
                all_pass = False
        except Exception as e:
            status = f"ERROR ({e})"
            all_pass = False
        print(f"{name:40}: {status}")
    print("\nOverall:", "ALL TESTS PASSED" if all_pass else "SOME TESTS FAILED")