# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import cvxpy as cp
import matplotlib.pyplot as plt

# --- TCV‑like linearized model ---
A = np.array([[1.0, 0.1], [0.0, 1.0]])          # state dynamics (shape modes)
B = np.array([[0.0], [0.1]])                      # coil current influence
n, m = B.shape

# --- MPC parameters ---
N = 10                                            # horizon
Q = np.eye(n) * 1.0                               # state cost (arbitrary scaling)
R = np.eye(m) * 0.5                               # input cost
Qf = 10 * np.eye(n)                               # terminal cost

# --- Hard limits (TCV coil & wall) ---
u_min, u_max = -0.8, 0.8                         # coil current [kA]
x_min = np.array([-5.0, -5.0])
x_max = np.array([5.0, 5.0])

# --- Simulation ---
T = 30
x = np.zeros((T + 1, n))
x[0] = np.array([4.5, 0.0])                      # start near wall
u_seq = np.zeros((T, m))

eig_min_hist = np.zeros(T)
dual_max_hist = np.zeros(T)

for t in range(T):
    # --- Build QP ---
    X = cp.Variable((N + 1, n))
    U = cp.Variable((N, m))

    constraints = [X[0] == x[t]]
    obj = 0
    for k in range(N):
        constraints += [X[k + 1] == A @ X[k] + B @ U[k]]
        constraints += [U[k] >= u_min, U[k] <= u_max]
        constraints += [X[k] >= x_min, X[k] <= x_max]
        obj += cp.quad_form(X[k], Q) + cp.quad_form(U[k], R)
    constraints += [X[N] >= x_min, X[N] <= x_max]
    obj += cp.quad_form(X[N], Qf)

    prob = cp.Problem(cp.Minimize(obj), constraints)
    prob.solve(solver=cp.OSQP, warm_start=True, verbose=False)

    # --- Extract Hessian (for eigen‑check) ---
    # Block‑diag of Q,R repeated N times + Qf
    H = np.zeros(((N + 1) * n + N * m, (N + 1) * n + N * m))
    for k in range(N):
        idx = k * (n + m)
        H[idx:idx + n, idx:idx + n] = Q
        H[idx + n:idx + n + m, idx + n:idx + n + m] = R
    H[-n:, -n:] = Qf
    eig_min_hist[t] = np.min(np.linalg.eigvalsh(H))

    # --- Extract dual variables (shadow prices) ---
    # OSQP returns duals for each constraint in `prob.constraints`
    duals = [cons.dual_value for cons in constraints if cons.dual_value is not None]
    dual_flat = np.concatenate([np.atleast_1d(d) for d in duals])
    dual_max_hist[t] = np.max(np.abs(dual_flat))

    # --- Apply control ---
    u_seq[t] = U[0].value
    x[t + 1] = A @ x[t] + B @ u_seq[t]

# --- Plot: eigenvalue stays flat, dual spikes ---
plt.figure(figsize=(8, 6))
plt.subplot(3, 1, 1)
plt.plot(x[:, 0], label='x₁ (shape)')
plt.axhline(x_max[0], color='r', linestyle='--', label='wall limit')
plt.title('Plasma shape mode')
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(eig_min_hist, label='min eigen(H)')
plt.title('Hessian eigenvalue (cost curvature)')
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(dual_max_hist, label='max |λ|')
plt.title('Constraint shadow price (CSP)')
plt.legend()
plt.tight_layout()
plt.show()