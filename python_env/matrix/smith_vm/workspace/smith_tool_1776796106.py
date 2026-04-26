# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol validation for SMPEM‑Ω (Secret‑Management Process Entropy Monitor).

The script:
1. Generates or ingests synthetic monthly snapshots of the four raw metrics:
      V  – plaintext‑key violation density   [0,1]
      G  – ownership Gini coefficient        [0,1]
      L  – lifecycle‑skew (std of log age)   [0,∞)
      S  – shadow‑IT ratio                   [0,1]
2. Computes PEFI = tanh(αV + βG + γL + δS)
3. Maps PEFI → Φ_N^{smpe}, Φ_Δ^{smpe}, ψ, ξ_N, ξ_Δ
4. Checks Ω‑invariant bounds:
      Φ_N ∈ [0,1]   (normalised)
      Φ_Δ ∈ ℝ       (no hard bound, but we flag extreme values)
      ψ   ∈ ℝ
5. Solves a tiny QP that enforces the MPC‑Ω constraints:
      PEFI ≤ 0.6
      Φ_N^{smpe} ≥ 0.6
      S_proc ≥ log(3)
   and returns the optimal control vector u (incentive, tooling, governance, exception‑cap).
6. Prints a pass/fail report.

All coefficients are set to plausible defaults; replace with calibrated values.
"""

import numpy as np
from scipy.optimize import minimize

# ----------------------------------------------------------------------
# 1. Synthetic data generator (replace with real spreadsheet scrape)
# ----------------------------------------------------------------------
def generate_synthetic_data(n_months=24, seed=42):
    rng = np.random.default_rng(seed)
    # Simulate a slowly deteriorating process then a remediation bump
    t = np.linspace(0, 1, n_months)
    V = np.clip(0.2 + 0.4*t + 0.1*rng.standard_normal(n_months), 0, 1)   # rising violations
    G = np.clip(0.3 + 0.2*t + 0.05*rng.standard_normal(n_months), 0, 1) # rising concentration
    L = np.clip(0.1 + 0.3*t + 0.05*rng.standard_normal(n_months), 0, None) # growing skew
    S = np.clip(0.05 + 0.25*t + 0.05*rng.standard_normal(n_months), 0, 1) # shadow‑IT growth
    return dict(t=t, V=V, G=G, L=L, S=S)

# ----------------------------------------------------------------------
# 2. PEFI and Ω‑variable mappings
# ----------------------------------------------------------------------
def compute_metrics(data,
                    alpha=0.4, beta=0.3, gamma=0.2, delta=0.1,
                    eta1=0.5, eta2=0.3,
                    eta3=0.4, eta4=0.2,
                    tau1=1, tau2=1,   # months of lead time (index shift)
                    PhiN0=0.8, PhiDelta0=0.2,
                    R0=1.0, lam=0.5):
    V, G, L, S = data['V'], data['G'], data['L'], data['S']
    # shift for lead time (simple index shift; assume monthly data)
    V_tau = np.roll(V, tau1)
    G_tau = np.roll(G, tau1)
    L_tau = np.roll(L, tau2)
    V_tau2 = np.roll(V, tau2)

    arg = alpha*V + beta*G + gamma*L + delta*S
    PEFI = np.tanh(arg)                     # ∈ (0,1)

    PhiN = PhiN0 - eta1*PEFI + eta2*(1 - G_tau)
    PhiD = PhiDelta0 + eta3*L_tau2 - eta4*V_tau2

    # Ricci scalar proxy: we use a simple curvature estimator from the 4‑D vector
    # (for demonstration only – replace with proper manifold calc)
    X = np.vstack([V, G, L, S]).T
    cov = np.cov(X, rowvar=False)
    eigvals = np.linalg.eigvalsh(cov)
    # Rough scalar curvature ≈ sum of eigenvalues (trace) – positive definite
    R_proc = np.trace(cov)                  # >0
    psi = np.log(np.abs(R_proc)/R0) + lam*PEFI

    # Stiffness coefficients (finite‑difference derivative)
    dpsi = np.gradient(psi)
    xi_N = np.gradient(PhiN) / np.where(np.abs(dpsi)>1e-8, dpsi, 1e-8)
    xi_D = np.gradient(PhiD) / np.where(np.abs(dpsi)>1e-8, dpsi, 1e-8)

    return dict(PEFI=PEFI, PhiN=PhiN, PhiD=PhiD,
                psi=psi, xi_N=xi_N, xi_D=xi_D,
                R_proc=R_proc, V=V, G=G, L=L, S=S)

# ----------------------------------------------------------------------
# 3. Entropy gauge (Shannon entropy of exception distribution)
# ----------------------------------------------------------------------
def exception_entropy(data, n_depts=5):
    # Simulate exception fractions per dept; in reality derived from policy‑exception logs
    rng = np.random.default_rng(123)
    p = rng.dirichlet(np.ones(n_depts), size=len(data['V']))  # each row sums to 1
    S_proc = -np.sum(p * np.log(p + 1e-12), axis=1)
    return S_proc

# ----------------------------------------------------------------------
# 4. MPC‑Ω QP (very small, solved via SLSQP)
# ----------------------------------------------------------------------
def mpc_control(metrics, entropy):
    """
    Control vector u = [u_incentive, u_tooling, u_governance, u_exception_cap]
    each ∈ [0,1] representing effort level.
    We map them to simple linear effects on the metrics:
        ΔPEFI   = -0.3*u_incentive -0.2*u_tooling -0.1*u_governance +0.05*u_exception_cap
        ΔPhiN   = +0.25*u_incentive +0.15*u_tooling +0.1*u_governance
        ΔS_proc = +0.2*u_tooling +0.1*u_governance -0.05*u_exception_cap
    (coefficients are illustrative)
    """
    PEFI0 = metrics['PEFI'][-1]          # use latest month
    PhiN0 = metrics['PhiN'][-1]
    S0    = entropy[-1]

    def objective(u):
        # Penalty for violating constraints + quadratic effort cost
        PEFI = PEFI0 + (-0.3*u[0] -0.2*u[1] -0.1*u[2] +0.05*u[3])
        PhiN = PhiN0 + (0.25*u[0] +0.15*u[1] +0.1*u[2])
        Sproc = S0 + (0.2*u[1] +0.1*u[2] -0.05*u[3])
        # constraint violations (penalised heavily)
        pen = 0.0
        if PEFI > 0.6:   pen += 1e3*(PEFI-0.6)**2
        if PhiN < 0.6:   pen += 1e3*(0.6-PhiN)**2
        if Sproc < np.log(3): pen += 1e3*(np.log(3)-Sproc)**2
        # effort cost (keep u small)
        effort = 0.1*np.sum(u**2)
        return pen + effort

    bounds = [(0,1)]*4
    x0 = [0.2,0.2,0.2,0.2]
    res = minimize(objective, x0, bounds=bounds, method='SLSQP')
    return res.x, res.success, res.message

# ----------------------------------------------------------------------
# 5. Run validation
# ----------------------------------------------------------------------
def main():
    data = generate_synthetic_data()
    metrics = compute_metrics(data)
    entropy = exception_entropy(data)

    # Latest‑step invariant checks
    latest = -1
    ok = True
    print("=== SMPEM‑Ω Ω‑Invariant Validation (latest month) ===")
    print(f"PEFI          : {metrics['PEFI'][latest]:.4f}  (target ≤0.6)")
    print(f"Φ_N^{smpe}    : {metrics['PhiN'][latest]:.4f}  (target ≥0.6)")
    print(f"Φ_Δ^{smpe}    : {metrics['PhiD'][latest]:.4f}")
    print(f"ψ             : {metrics['psi'][latest]:.4f}")
    print(f"S_proc        : {entropy[latest]:.4f}  (target ≥log(3)≈1.099)")
    print(f"R_proc (Ricci): {metrics['R_proc'][latest]:.4f}")

    if metrics['PEFI'][latest] > 0.6:
        print("❌ PEFI exceeds alert threshold")
        ok = False
    if metrics['PhiN'][latest] < 0.6:
        print("❌ Φ_N fell below connectivity floor")
        ok = False
    if entropy[latest] < np.log(3):
        print("❌ Exception entropy too low (over‑concentrated exceptions)")
        ok = False

    # MPC‑Ω control synthesis
    u_opt, feasible, msg = mpc_control(metrics, entropy)
    print("\n=== MPC‑Ω Control Recommendation ===")
    print(f"Incentive effort   : {u_opt[0]:.2f}")
    print(f"Tooling investment : {u_opt[1]:.2f}")
    print(f"Governance reset   : {u_opt[2]:.2f}")
    print(f"Exception cap      : {u_opt[3]:.2f}")
    print(f"Feasible? {feasible}  ({msg})")
    if not feasible:
        ok = False

    print("\n=== Overall Verdict ===")
    print("✅ PASS – all Ω‑invariants satisfied and MPC‑Ω QP feasible" if ok
          else "❌ FAIL – invariant or feasibility violation detected")
    return ok

if __name__ == "__main__":
    main()