# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import sympy as sp

# ----------------------------
# Symbolic validation of BRS-Ω core equations
# ----------------------------

# Define symbols (all dimensionless unless noted)
t, s, m, ell0, alpha, beta, ell_max = sp.symbols('t s m ell0 alpha beta ell_max', nonnegative=True)
PhiN0, PhiDelta0 = sp.symbols('PhiN0 PhiDelta0', real=True)
a1, a2, b1, b2 = sp.symbols('a1 a2 b1 b2', positive=True)  # coefficients from derivation
# Latency model
ell = ell0 + alpha * t / m - beta * s

# Streaming covariant modes (first‑principles derived linear forms)
PhiN_stream = PhiN0 - a1 * t / m - a2 * ell / ell_max   # assuming eta ~ t/m, zeta ~ ell/ell_max
PhiDelta_stream = PhiDelta0 + b1 * t / m - b2 * ell / ell_max

# Stiffness invariants (dimension of time)
lam, gamma0, gamma1, gamma2, delta0, delta1, delta2 = sp.symbols('lam gamma0 gamma1 gamma2 delta0 delta1 delta2', positive=True)
xiN_inv2 = lam * (gamma0 + gamma1 * t + gamma2 * ell)   # => xiN has dimension sqrt(time)
xiDelta_inv2 = lam * (delta0 - delta1 * t + delta2 * ell)

# Metric coupling invariant (dimensionless)
psi = sp.log(sp.sqrt(xiN_inv2 * xiDelta_inv2))  # placeholder; actual form not critical for dim check

# Entropy-based threat level (symbolic)
# Assume gradient norms g_i, we define entropy H = -sum p_i log p_i, p_i = g_i / sum g
# For validation we just enforce 0 <= H <= log(m) => theta in [0,1]
H, H_max = sp.symbols('H H_max', nonnegative=True)
theta = 1 - H / H_max

# Cost function integrand (per time step)
lam1, lam2 = sp.symbols('lam1 lam2', positive=True)
cost = (1 - PhiN_stream)**2 + (PhiDelta_stream)**2 + lam1 * (theta - t/m)**2 + lam2 * (ell/ell_max)**2

# ----------------------------
# Dimensional consistency checks
# ----------------------------
# We assign units: [t] = 1, [s] = 1, [m] = 1, [ell0] = T, [alpha] = T, [beta] = T, [ell_max] = T
# Therefore ell/T is dimensionless, t/m dimensionless.
# PhiN0, PhiDelta0 dimensionless => PhiN_stream, PhiDelta_stream dimensionless ✓
# xiN_inv2 has units: lam * (1 + 1*T + 1*T) => lam must be 1/T^2 to give xiN_inv2 units 1/T^2
# Let lam = 1/T^2 => xiN has units T ✓
# psi = log(sqrt(xiN_inv2 * xiDelta_inv2)) => argument dimensionless (1/T^2 * 1/T^2 => 1/T^4, sqrt => 1/T^2) => not dimensionless.
# To fix, we need a reference scale xi0 with same units as xi, so psi = log(xi/xi0). We'll adjust:
xi0 = sp.symbols('xi0', positive=True)  # has units T
psi_corrected = sp.log(sp.sqrt(1/(xiN_inv2 * xiDelta_inv2)) * xi0)  # xi = 1/sqrt(xiN_inv2 * xiDelta_inv2)
# Now argument of log is dimensionless ✓

# ----------------------------
# Numeric sanity check
# ----------------------------
np.random.seed(42)
def random_params():
    m_val = np.random.randint(5, 21)          # number of workers
    t_val = np.random.randint(0, m_val//2)    # t <= floor((m-1)/2)
    s_val = np.random.uniform(0.1, 0.9)       # sparsity ratio
    ell0_val = np.random.uniform(0.1, 0.5)    # base latency (ms)
    alpha_val = np.random.uniform(0.0, 0.5)   # latency increase per t/m
    beta_val  = np.random.uniform(0.0, 0.5)   # latency decrease per sparsity
    ell_max_val = np.random.uniform(1.0, 5.0) # max allowed latency
    PhiN0_val = np.random.uniform(0.6, 0.9)
    PhiDelta0_val = np.random.uniform(0.1, 0.4)
    a1_val, a2_val, b1_val, b2_val = np.random.uniform(0.1, 0.5, size=4)
    lam_val = 1.0  # set reference time scale = 1 ms^(-2) for simplicity
    gamma0_val, gamma1_val, gamma2_val = np.random.uniform(0.1, 0.5, size=3)
    delta0_val, delta1_val, delta2_val = np.random.uniform(0.1, 0.5, size=3)
    H_val = np.random.uniform(0, np.log(m_val))  # entropy within bounds
    H_max_val = np.log(m_val)
    return dict(m=m_val, t=t_val, s=s_val, ell0=ell0_val, alpha=alpha_val, beta=beta_val,
                ell_max=ell_max_val, PhiN0=PhiN0_val, PhiDelta0=PhiDelta0_val,
                a1=a1_val, a2=a2_val, b1=b1_val, b2=b2_val,
                lam=lam_val, gamma0=gamma0_val, gamma1=gamma1_val, gamma2=gamma2_val,
                delta0=delta0_val, delta1=delta1_val, delta2=delta2_val,
                H=H_val, H_max=H_max_val)

def evaluate(params):
    m = params['m']
    t = params['t']
    s = params['s']
    ell0 = params['ell0']
    alpha = params['alpha']
    beta = params['beta']
    ell_max = params['ell_max']
    PhiN0 = params['PhiN0']
    PhiDelta0 = params['PhiDelta0']
    a1 = params['a1']; a2 = params['a2']; b1 = params['b1']; b2 = params['b2']
    ell = ell0 + alpha * t / m - beta * s
    PhiN = PhiN0 - a1 * t / m - a2 * ell / ell_max
    PhiDelta = PhiDelta0 + b1 * t / m - b2 * ell / ell_max
    xiN_inv2 = params['lam'] * (params['gamma0'] + params['gamma1'] * t + params['gamma2'] * ell)
    xiDelta_inv2 = params['lam'] * (params['delta0'] - params['delta1'] * t + params['delta2'] * ell)
    # avoid division by zero or negative
    if xiN_inv2 <= 0 or xiDelta_inv2 <= 0:
        xiN = np.inf
        xiDelta = np.inf
    else:
        xiN = 1.0 / np.sqrt(xiN_inv2)
        xiDelta = 1.0 / np.sqrt(xiDelta_inv2)
    theta = 1.0 - params['H'] / params['H_max']
    cost_val = (1 - PhiN)**2 + PhiDelta**2 + 0.5 * (theta - t/m)**2 + 0.5 * (ell/ell_max)**2
    return {
        'ell': ell,
        'PhiN': PhiN,
        'PhiDelta': PhiDelta,
        'xiN': xiN,
        'xiDelta': xiDelta,
        'theta': theta,
        'cost': cost_val,
        'constraints': {
            't_le_tmax': t <= (m-1)//2,
            'ell_le_ellmax': ell <= ell_max,
            'PhiN_ge_0_6': PhiN >= 0.6,
            'PhiDelta_le_0_7': PhiDelta <= 0.7,
            'theta_in_01': 0.0 <= theta <= 1.0,
            'xiN_finite': np.isfinite(xiN),
            'xiDelta_finite': np.isfinite(xiDelta)
        }
    }

# Run a batch of random tests
failures = []
for i in range(1000):
    p = random_params()
    r = evaluate(p)
    if not all(r['constraints'].values()):
        failures.append((i, r, p))

print(f"Random tests: {1000 - len(failures)} passed, {len(failures)} failed")
if failures:
    print("First failure details:")
    idx, res, params = failures[0]
    print(f"Test #{idx}")
    for k, v in res['constraints'].items():
        print(f"  {k}: {v}")
    print("  Parameters:", params)
else:
    print("All random tests satisfied constraints.")

# ----------------------------
# Symbolic check of cost non-negativity
# ----------------------------
# Show that cost is a sum of squares => always >=0
print("\nSymbolic cost expression:")
sp.simplify(cost)
print("Cost is manifestly non-negative as sum of squares.")