# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ──────────────────────────────────────────────────────────────────────────────
#  Stochastic capping lattice (1‑D, periodic)
# ──────────────────────────────────────────────────────────────────────────────
class CappingLattice:
    def __init__(self, N, k_on, k_off, init='random'):
        self.N = N
        self.k_on = k_on
        self.k_off = k_off
        # state[i] = 1 (capped) or 0 (uncapped)
        if init == 'random':
            self.state = np.random.randint(0, 2, size=N)
        else:
            self.state = np.ones(N, dtype=int)   # fully capped initial

    def gillespie_step(self):
        """Perform one Gillespie event."""
        # propensities: each site can cap if uncapped, or decap if capped
        # For efficiency we treat each site as a separate reaction channel.
        uncapped = np.where(self.state == 0)[0]
        capped   = np.where(self.state == 1)[0]
        a_on  = len(uncapped) * self.k_on
        a_off = len(capped)   * self.k_off
        a_tot = a_on + a_off
        if a_tot == 0:
            return 0.0
        dt = np.random.exponential(scale=1.0/a_tot)
        # which reaction?
        if np.random.rand() < a_on/a_tot:
            # cap a random uncapped site
            i = np.random.choice(uncapped)
            self.state[i] = 1
        else:
            # decap a random capped site
            i = np.random.choice(capped)
            self.state[i] = 0
        return dt

    def correlation_function(self, max_r=50):
        """Compute spatial correlation C(r) = <(E_i - <E>)(E_{i+r} - <E>)> / var."""
        E = self.state.astype(float)
        mean = E.mean()
        var  = E.var()
        if var == 0:
            return np.zeros(max_r)
        C = np.zeros(max_r)
        for r in range(max_r):
            C[r] = np.mean((E - mean) * (np.roll(E, r) - mean)) / var
        return C

# ──────────────────────────────────────────────────────────────────────────────
#  Simulation & analysis
# ──────────────────────────────────────────────────────────────────────────────
def simulate_and_analyze(k_on, k_off, N=200, t_max=500, dt_sample=1.0):
    lattice = CappingLattice(N, k_on, k_off, init='random')
    t = 0.0
    ts, xi_vals, entropy_vals = [], [], []
    while t < t_max:
        # advance until next sample time
        while t < len(ts)*dt_sample:
            dt = lattice.gillespie_step()
            t += dt
        # sample observables
        corr = lattice.correlation_function(max_r=50)
        # fit exponential C(r) ~ exp(-r/xi) for first few points
        r = np.arange(len(corr))
        try:
            popt, _ = curve_fit(lambda r, xi: np.exp(-r/xi), r[:10], corr[:10],
                                p0=[10.0])
            xi = popt[0]
        except Exception:
            xi = np.nan
        # empirical entropy of the lattice
        p_capped = lattice.state.mean()
        if 0 < p_capped < 1:
            S = -p_capped*np.log(p_capped) - (1-p_capped)*np.log(1-p_capped)
        else:
            S = 0.0
        ts.append(t)
        xi_vals.append(xi)
        entropy_vals.append(S)
    return np.array(ts), np.array(xi_vals), np.array(entropy_vals)

# ──────────────────────────────────────────────────────────────────────────────
#  Run three regimes: (i) stable capped, (ii) stable uncapped, (iii) near critical
# ──────────────────────────────────────────────────────────────────────────────
regimes = {
    "stable capped":   (1.0, 0.2),
    "stable uncapped": (0.2, 1.0),
    "near critical":   (0.55, 0.55),
}

fig, axs = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
for label, (kon, koff) in regimes.items():
    t, xi, S = simulate_and_analyze(kon, koff, N=200, t_max=500)
    # mask out invalid xi fits
    valid = ~np.isnan(xi)
    axs[0].plot(t[valid], xi[valid], label=f"{label} (k_on/k_off={kon}/{koff})")
    axs[1].plot(t, S, label=f"{label}")

axs[0].set_ylabel("Fitted correlation length ξ")
axs[1].set_ylabel("Capping entropy S")
axs[1].set_xlabel("Time (a.u.)")
axs[0].legend()
axs[1].legend()
axs[0].set_title("Stochastic lattice: ξ can fluctuate wildly even in stable regimes")
plt.tight_layout()
plt.show()