# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- Non‑linear RG equation ---
def rg_nonlinear(lnq, alpha, beta0=2.0/(3*np.pi), gamma=0.5, alpha_crit=1.0):
    """
    dα/dln q = beta0 * α * (1 - α/alpha_crit) + gamma * α**2 * ln(q**2)
    """
    q2 = np.exp(2*lnq)          # q^2 = e^{2 ln q}
    log_term = np.log(q2)        # ln(q^2)
    dalpha_dlnq = (beta0 * alpha * (1 - alpha/alpha_crit)
                   + gamma * alpha**2 * log_term)
    return dalpha_dlnq

# --- Solve for a range of initial alphas ---
def evolve_alpha(alpha0, lnq_max=10, n_points=1000):
    lnq_span = (0, lnq_max)
    sol = solve_ivp(
        fun=lambda lnq, a: rg_nonlinear(lnq, a),
        t_span=lnq_span,
        y0=[alpha0],
        t_eval=np.linspace(*lnq_span, n_points),
        method='RK45',
        dense_output=True
    )
    return sol.t, sol.y[0]

# --- Scan gamma to find bifurcation ---
def scan_gamma(gammas, alpha0=0.01, lnq_max=10):
    results = {}
    for g in gammas:
        # patch the global gamma used in rg_nonlinear (quick & dirty)
        global _gamma
        _gamma = g
        # wrap rg_nonlinear to capture gamma
        def rg_wrapper(lnq, alpha, beta0=2.0/(3*np.pi), alpha_crit=1.0):
            return rg_nonlinear(lnq, alpha, beta0, _gamma, alpha_crit)
        lnq, alpha = evolve_alpha(alpha0, lnq_max)
        results[g] = (lnq, alpha)
    return results

# --- Plot the flow for several gammas ---
if __name__ == "__main__":
    gammas = [0.1, 0.3, 0.5, 0.7, 0.9]
    data = scan_gamma(gammas, alpha0=0.01, lnq_max=12)

    fig, ax = plt.subplots(figsize=(8,5))
    for g, (lnq, alpha) in data.items():
        ax.plot(np.exp(lnq), alpha, label=f"γ={g:.1f}")

    ax.set_xscale('log')
    ax.set_xlabel(r"$q$ (GeV)", fontsize=12)
    ax.set_ylabel(r"$\alpha_{\rm fs}(q)$", fontsize=12)
    ax.set_title("Non‑linear RG flow: emergence of chaotic regime")
    ax.legend()
    ax.grid(True, which='both', ls=':')
    plt.tight_layout()
    plt.savefig("chaotic_rg_flow.png", dpi=150)
    plt.show()