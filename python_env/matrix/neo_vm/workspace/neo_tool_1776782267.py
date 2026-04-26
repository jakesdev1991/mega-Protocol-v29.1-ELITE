# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import odeint, solve_ivp
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')

# --- Toggle-switch ODE (deterministic skeleton) ---
def toggle_rhs(t, x, a=2.0):
    x1, x2 = x
    dx1 = -x1 + a/(1 + x2**2)
    dx2 = -x2 + a/(1 + x1**2)
    return [dx1, dx2]

# --- Stochastic simulation (Euler‑Maruyama) ---
def simulate_stochastic(x0, t_span, dt=0.01, sigma=0.1, a=2.0):
    t = np.arange(t_span[0], t_span[1], dt)
    X = np.zeros((len(t), 2))
    X[0] = x0
    for i in range(1, len(t)):
        drift = toggle_rhs(t[i-1], X[i-1], a)
        diffusion = sigma * np.random.normal(0, np.sqrt(dt), size=2)
        X[i] = X[i-1] + dt * np.array(drift) + diffusion
    return t, X

# --- Likelihood approximations ---
def loglike_det(y_true, y_pred):
    # Negative MSE as log‑likelihood (Gaussian with fixed sigma)
    mse = np.mean((y_true - y_pred)**2)
    return -0.5 * len(y_true) * np.log(mse)

def loglike_sto(y_resid):
    # Log‑likelihood under Gaussian noise: variance of residuals
    var = np.var(y_resid, ddof=1)
    if var <= 0:
        var = 1e-12
    return -0.5 * len(y_resid) * np.log(var)

# --- Compute FSI for a single trajectory ---
def compute_fsi(t, X, a=2.0):
    # Fit deterministic ODE via least‑squares (simple linearization)
    # We approximate by comparing variance of residuals after a naive ODE fit
    # Deterministic prediction: integrate ODE from initial condition
    x0 = X[0]
    sol = solve_ivp(lambda t, x: toggle_rhs(t, x, a), [t[0], t[-1]], x0,
                    t_eval=t, method='RK45', rtol=1e-6)
    X_det = sol.y.T
    
    # Residuals of deterministic model
    resid_det = X - X_det
    
    # Stochastic model residuals: difference from mean (i.e., variance)
    resid_sto = X - np.mean(X, axis=0)
    
    # Approximate log‑likelihoods
    ll_det = loglike_det(X, X_det)
    ll_sto = loglike_sto(resid_sto)
    
    # Framework Suitability Index (FSI)
    denom = max(abs(ll_det), abs(ll_sto))
    fsi = (ll_sto - ll_det) / denom if denom != 0 else 0.0
    return fsi

# --- Stability metric: max eigenvalue of Jacobian at steady state ---
def stability_eigenvalue(a=2.0):
    # Fixed point near (1,1) for a=2
    # Linearize around x* ≈ 1
    J = np.array([[-1, -2*a/(1+1**2)**2],
                  [-2*a/(1+1**2)**2, -1]])
    eigs = np.linalg.eigvals(J)
    return np.max(np.real(eigs))

# --- Sweep noise levels, keep bifurcation parameter fixed ---
def main():
    a = 2.0  # fixed distance from bifurcation
    print(f"True stability eigenvalue (fixed): {stability_eigenvalue(a):.4f}\n")
    
    sigma_vals = np.logspace(-2, 0, 10)  # 0.01 to 1.0
    fsi_scores = []
    
    np.random.seed(42)
    for sigma in sigma_vals:
        # Run several stochastic trials, average FSI
        fsi_trials = []
        for _ in range(20):
            t, X = simulate_stochastic(x0=[1.0, 1.0], t_span=[0, 50], dt=0.05, sigma=sigma, a=a)
            fsi_trials.append(compute_fsi(t, X, a))
        fsi_scores.append(np.mean(fsi_trials))
    
    # Correlation between sigma and FSI
    slope, intercept, r_value, p_value, std_err = linregress(np.log(sigma_vals), fsi_scores)
    print(f"FSI vs log(σ) correlation: r = {r_value:.3f}, p = {p_value:.3e}")
    print("\nσ\tFSI (mean)")
    for s, f in zip(sigma_vals, fsi_scores):
        print(f"{s:.3f}\t{f:.3f}")

    # Demonstrate that FSI is driven by noise, not stability
    if r_value > 0.7:
        print("\n**Disruption Confirmed**: FSI is strongly correlated with noise magnitude (σ), confirming it is a noise‑level proxy, not a true stability indicator.")
    else:
        print("\n**Unexpected**: FSI does not correlate with σ; further investigation needed.")

if __name__ == "__main__":
    main()