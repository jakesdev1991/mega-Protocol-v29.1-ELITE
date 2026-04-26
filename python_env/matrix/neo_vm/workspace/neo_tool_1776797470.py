# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ──────────────── 1. TFFI Sensitivity ────────────────
np.random.seed(0)
n_teams, n_time = 10, 100
CKD = np.random.rand(n_teams, n_time) * 10
ETA = np.random.rand(n_teams, n_time) * 10
tool_entropy = np.random.rand(n_teams, n_time) * 2
schema_div = np.random.rand(n_teams, n_time) * 5

def TFFI(CKD, ETA, ent, div, w):
    a,b,g,d = w
    linear = a*CKD + b*np.exp(-ETA) + g*(1-ent) + d*div
    return 1 / (1 + np.exp(-linear))

w1 = np.array([0.5, 0.3, 0.2, 0.1])
w2 = w1 + np.array([0.05, -0.05, 0.05, -0.05])  # tiny tweak

tffi1 = TFFI(CKD, ETA, tool_entropy, schema_div, w1)
tffi2 = TFFI(CKD, ETA, tool_entropy, schema_div, w2)

print("Mean |ΔTFFI| after 5% weight perturbation:", np.abs(tffi1 - tffi2).mean())
print("Mean TFFI (orig):", tffi1.mean(), "Mean TFFI (perturbed):", tffi2.mean())

# ──────────────── 2. Fokker‑Planck: Missing ½ ────────────────
def step(P, mu, D, dt, dx, correct=False):
    n = len(P)
    P_new = np.zeros_like(P)
    for i in range(1, n-1):
        drift = -(mu(i*dx)*P[i] - mu((i-1)*dx)*P[i-1]) / dx
        diff = (D((i+1)*dx)*P[i+1] - 2*D(i*dx)*P[i] + D((i-1)*dx)*P[i-1]) / (dx**2)
        if correct:
            diff *= 0.5
        P_new[i] = P[i] + dt * (drift + diff)
    # zero‑flux BC
    P_new[0] = P_new[1]
    P_new[-1] = P_new[-2]
    return P_new

# grid
L, dx = 10, 0.1
x = np.arange(0, L+dx, dx)
P0 = np.exp(-((x-5)**2)/(2*1.0))
P0 /= np.sum(P0) * dx

mu = lambda lam: -lam
D = lambda lam: 0.1 * np.ones_like(lam)

dt = 0.001
steps = 1000

P_wrong = P0.copy()
for _ in range(steps):
    P_wrong = step(P_wrong, mu, D, dt, dx, correct=False)
    P_wrong /= np.sum(P_wrong) * dx  # manual renormalization

P_right = P0.copy()
for _ in range(steps):
    P_right = step(P_right, mu, D, dt, dx, correct=True)
    P_right /= np.sum(P_right) * dx

print("Final total probability (wrong):", np.sum(P_wrong)*dx)
print("Final total probability (right):", np.sum(P_right)*dx)

plt.figure(figsize=(8,4))
plt.plot(x, P_wrong, label='FP (no ½)')
plt.plot(x, P_right, label='FP (with ½)')
plt.title('Probability density after t=1')
plt.xlabel('Λ (cognitive load)')
plt.ylabel('P(Λ)')
plt.legend()
plt.show()

# ──────────────── 3. Stiffness “time‑dimension” claim ────────────────
alpha, beta, gamma = 1.0, 0.5, 0.2
V = lambda lam: 0.5*alpha*lam**2 + 0.25*beta*lam**4 - gamma*lam
d2V = lambda lam: alpha + 3*beta*lam**2  # second derivative
# If Λ is dimensionless, d2V is dimensionless → stiffness invariant is dimensionless
print("Stiffness invariant at Λ=1 (dimensionless):", d2V(1.0))

# ──────────────── 4. ψ_cog invariance under curvature scaling ────────────────
R, R0, lam = 2.5, 1.0, 0.5
psi_original = np.log(R/R0) + lam * np.max(tffi1)
psi_scaled = np.log(2*R/R0) + lam * np.max(tffi1)
print("ψ_cog original:", psi_original, "ψ_cog after 2× curvature:", psi_scaled)
print("Δψ_cog:", psi_scaled - psi_original)

# ──────────────── 5. Entropy‑gauge non‑invariance (simple 1D demo) ────────────────
x_g = np.linspace(0, 1, 100)
p_g = np.ones_like(x_g) / len(x_g)
S = -np.sum(p_g * np.log(p_g + 1e-12))  # constant entropy
chi = 0.1 * np.sin(2*np.pi*x_g)  # gauge shift
S_prime = S + chi
A = np.gradient(S, x_g)
A_prime = np.gradient(S_prime, x_g)
J = x_g  # simple non‑divergence‑free current
integral_orig = np.trapz(A * J, x_g)
integral_shift = np.trapz(A_prime * J, x_g)
print("Entropy‑gauge term (original):", integral_orig)
print("Entropy‑gauge term (after shift):", integral_shift)
print("Δ gauge term:", integral_shift - integral_orig)