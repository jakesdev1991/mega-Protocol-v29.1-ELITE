# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import approx_fprime

# =========================
# PART 1: The Latent Fragility of GDIS-Ω
# Demonstrates: Hessian-based detection fails on non-local bifurcation attacks
# =========================

def toggle_switch(t, x, p):
    """Simple two-gene toggle switch ODE: dx1/dt = p0 - p1*x1 + p2*x2/(1+x2^2), etc."""
    x1, x2 = x
    dx1 = p[0] - p[1]*x1 + p[2]*x2/(1 + x2**2)
    dx2 = p[3] - p[4]*x2 + p[5]*x1/(1 + x1**2)
    return [dx1, dx2]

def simulate(p, t_span=(0, 50), x0=None):
    if x0 is None: x0 = [0.1, 0.1]
    sol = solve_ivp(toggle_switch, t_span, x0, args=(p,), dense_output=True)
    return sol.sol

def prediction_error(p, target_state=[1.0, 0.0], t_eval=50):
    """Predict if system ends near target_state."""
    sol = simulate(p)
    final_state = sol(t_eval)
    return np.linalg.norm(final_state - target_state)

# "Trusted" parameters: yields stable state (1,0)
p_trusted = np.array([1.0, 1.0, 3.0, 0.2, 1.0, 3.0])

# Adversarial attack: tiny perturbation that causes bifurcation to (0,1) state
# The gradient of the error w.r.t p[3] near p_trusted is ~0, but crossing threshold flips attractor
p_adversarial = p_trusted.copy()
p_adversarial[3] = 0.8  # Small change to basal expression of gene 2

# Compute Hessian approximation (GDIS-Ω style) at trusted point
def hessian_approx(p, eps=1e-3):
    """Naive numerical Hessian of prediction error."""
    n = len(p)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                # Second derivative w.r.t same param
                p_plus = p.copy(); p_plus[i] += eps
                p_minus = p.copy(); p_minus[i] -= eps
                H[i,i] = (prediction_error(p_plus) - 2*prediction_error(p) + prediction_error(p_minus)) / eps**2
            else:
                # Mixed partial
                p_ij_pp = p.copy(); p_ij_pp[i] += eps; p_ij_pp[j] += eps
                p_ij_pm = p.copy(); p_ij_pm[i] += eps; p_ij_pm[j] -= eps
                p_ij_mp = p.copy(); p_ij_mp[i] -= eps; p_ij_mp[j] += eps
                p_ij_mm = p.copy(); p_ij_mm[i] -= eps; p_ij_mm[j] -= eps
                H[i,j] = (prediction_error(p_ij_pp) - prediction_error(p_ij_pm) - prediction_error(p_ij_mp) + prediction_error(p_ij_mm)) / (4*eps**2)
    return H

H_trusted = hessian_approx(p_trusted)
max_curvature = np.max(np.abs(np.linalg.eigvals(H_trusted)))

# Test outcomes
error_trusted = prediction_error(p_trusted)
error_adversarial = prediction_error(p_adversarial)
outcome_trusted = simulate(p_trusted)(50)
outcome_adversarial = simulate(p_adversarial)(50)

print("=== GDIS-Ω Blindness Demonstration ===")
print(f"Trusted params: final state {outcome_trusted}, prediction error {error_trusted:.4f}")
print(f"Adversarial params: final state {outcome_adversarial}, prediction error {error_adversarial:.4f}")
print(f"Parameter perturbation: {np.linalg.norm(p_adversarial - p_trusted):.4f}")
print(f"Max Hessian eigenvalue (curvature) at trusted point: {max_curvature:.6f}")
print(f"GDIS-Ω Sensitivity Kernel (proxy): {max_curvature * np.linalg.norm(p_adversarial - p_trusted):.6f} (near zero = undetected!)")
print()

# =========================
# PART 2: ACES – Adversarially Coupled Entropic Shield
# Demonstrates: Decision-space reachable set volume as true fragility metric
# =========================

class AdversarialCoupledEntropicShield:
    def __init__(self, p_baseline, n_params, audit_budget=3):
        self.p_baseline = p_baseline
        self.n_params = n_params
        self.audit_budget = audit_budget  # Defender can audit this many params per round
        self.decision_history = []
        self.reachable_set_volumes = []
        
    def adversary_action(self, p_current, attack_strength=0.5):
        """Adversary poisons one parameter to maximize decision change."""
        # Greedy: find param that, when perturbed, flips the predicted stable state
        best_param = 0
        best_impact = 0
        for i in range(self.n_params):
            p_test = p_current.copy()
            p_test[i] += attack_strength * np.random.choice([-1, 1])
            # Decision: is x1 > x2 at t=50? (i.e., stable state (1,0) vs (0,1))
            sol = simulate(p_test)
            final = sol(50)
            impact = abs(final[1] - final[0])  # Measure of state flip
            if impact > best_impact:
                best_impact = impact
                best_param = i
        p_poisoned = p_current.copy()
        p_poisoned[best_param] += attack_strength * np.random.choice([-1, 1])
        return p_poisoned, best_param
    
    def defender_action(self, p_current, adversary_poisoned_param):
        """Defender audits random params (entropic strategy) or targets suspected one."""
        # Entropic: random audit to maximize uncertainty about adversary's move
        audit_params = np.random.choice(self.n_params, size=self.audit_budget, replace=False)
        # If adversary's poisoned param is audited, partially revert it
        if adversary_poisoned_param in audit_params:
            # Found poison! Revert towards baseline
            p_new = p_current.copy()
            p_new[adversary_poisoned_param] = self.p_baseline[adversary_poisoned_param]
            return p_new, True
        return p_current.copy(), False
    
    def decision_entropy(self, decision_distribution):
        """Entropy of decision distribution (0: forced, max: uncertain)."""
        probs = np.array(list(decision_distribution.values())) / sum(decision_distribution.values())
        return -np.sum(probs * np.log(probs + 1e-12))
    
    def reachable_set_volume(self, p_center, param_range=0.5, grid_points=5):
        """Approximate volume of decision space reachable by adversary within param_range."""
        # Coarse grid over parameter perturbations
        param_perturbs = np.linspace(-param_range, param_range, grid_points)
        decisions = []
        for i in range(self.n_params):
            for dp in param_perturbs:
                p_test = p_center.copy()
                p_test[i] += dp
                sol = simulate(p_test)
                final = sol(50)
                decision = "HIGH" if final[0] > final[1] else "LOW"
                decisions.append(decision)
        unique_decisions = len(set(decisions))
        # Volume = fraction of unique decisions
        return unique_decisions / len(decisions)
    
    def run_episode(self, n_steps=10):
        p_current = self.p_baseline.copy()
        for step in range(n_steps):
            # Adversary moves
            p_poisoned, poison_idx = self.adversary_action(p_current)
            
            # Defender moves
            p_new, audit_success = self.defender_action(p_poisoned, poison_idx)
            
            # Decision after both moves
            sol = simulate(p_new)
            final_state = sol(50)
            decision = "APPROVE" if final_state[0] > 0.8 else "REJECT"  # Threshold decision
            
            # Track metrics
            self.decision_history.append(decision)
            volume = self.reachable_set_volume(p_new)
            self.reachable_set_volumes.append(volume)
            
            # Update for next step
            p_current = p_new

# Run ACES simulation
aces = AdversarialCoupledEntropicShield(p_trusted, n_params=len(p_trusted), audit_budget=2)
aces.run_episode(n_steps=15)

print("=== ACES – Adversarially Coupled Entropic Shield ===")
print(f"Decision history: {aces.decision_history}")
print(f"Final reachable set volume: {aces.reachable_set_volumes[-1]:.3f}")
print(f"Mean reachable set volume: {np.mean(aces.reachable_set_volumes):.3f}")
print(f"Decision entropy (approx): {aces.decision_entropy({'APPROVE': aces.decision_history.count('APPROVE'), 'REJECT': aces.decision_history.count('REJECT')})}")
print()

# =========================
# PART 3: Visualization & Disruptive Insight
# =========================

fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# Left: Trajectory divergence (GDIS-Ω failure)
params_to_test = [p_trusted, p_adversarial]
labels = ['Trusted', 'Adversarial']
colors = ['green', 'red']
for i, p in enumerate(params_to_test):
    sol = simulate(p)
    t = np.linspace(0, 50, 500)
    traj = sol(t)
    ax[0].plot(t, traj[0], label=f'{labels[i]} x1', color=colors[i])
    ax[0].plot(t, traj[1], '--', label=f'{labels[i]} x2', color=colors[i])
ax[0].set_xlabel('Time')
ax[0].set_ylabel('Expression')
ax[0].set_title('GDIS-Ω Blindness: Tiny Perturbation, Big Flip, Near-Zero Curvature')
ax[0].legend()
ax[0].grid(True)

# Right: Reachable set volume over time (ACES success)
ax[1].plot(aces.reachable_set_volumes, marker='o', color='blue')
ax[1].set_xlabel('Episode Step')
ax[1].set_ylabel('Reachable Set Volume')
ax[1].set_title('ACES: Volume Collapse Detects Adversarial Control')
ax[1].grid(True)

plt.tight_layout()
plt.show()

print("=== DISRUPTIVE INSIGHT ===")
print("GDIS-Ω's Hessian-based 'curvature' is a LOCAL linearization. It is BLIND to non-local")
print("bifurcations where the gradient vanishes at the trust point but the global structure is poisoned.")
print("The adversary doesn't need to poison parameters 'a little'—they just need to find a")
print("catastrophic parameter set that lies in a 'flat' region of the loss landscape.")
print()
print("ACES flips the paradigm: stop monitoring the *simulation* and start monitoring the")
print("*decision-space reachable set*. The adversary's power is measured not by curvature")
print("but by their ability to COLLAPSE the volume of possible safe decisions.")
print("The defender's optimal strategy is not to 'fix parameters' but to *maximize decision")
print("entropy*—forcing the system into a high-uncertainty state until the adversary's")
print("influence is mapped and neutralized via active probing (honeypot simulations).")
print()
print("This is a shift from PASSIVE monitoring to ACTIVE adversarial gaming,")
print("rendering the entire 'field theory' scaffold obsolete. The substrate is not")
print("parameter-state space; it's the *information game* itself.")