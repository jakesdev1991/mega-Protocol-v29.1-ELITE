# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import fisher_exact

# Simulate HSA memory access patterns as Markov chain
# States: 0=CPU cache, 1=GPU local, 2=Unified memory
# Transition rates depend on phi_N (Newtonian) and phi_Delta (Archive)

def simulate_hsa_node(phi_N, phi_Delta, T=1.0, dt=1e-4, seed=42):
    """Simulate memory access Markov process"""
    np.random.seed(seed)
    steps = int(T/dt)
    
    # Transition matrix: higher phi_N = more deterministic (diagonal)
    # higher phi_Delta = more random off-diagonal (archive thrashing)
    P = np.array([
        [0.7 + 0.2*phi_N, 0.2*phi_Delta, 0.1*(1-phi_N)],
        [0.15*phi_Delta, 0.8 + 0.1*phi_N, 0.05*(1-phi_Delta)],
        [0.1*(1-phi_N), 0.15*(1-phi_Delta), 0.75 + 0.1*phi_N]
    ])
    
    # Normalize rows
    P = P / P.sum(axis=1, keepdims=True)
    
    # Simulate trajectory
    state = 0
    trajectory = []
    for _ in range(steps):
        state = np.random.choice(3, p=P[state])
        trajectory.append(state)
    
    return np.array(trajectory), P

def compute_entropy_and_jerk(trajectory, window=100):
    """Compute naive Shannon entropy and its jerk"""
    # Estimate probabilities in sliding window
    times = []
    entropies = []
    
    for i in range(window, len(trajectory), window//2):
        window_data = trajectory[i-window:i]
        probs = np.bincount(window_data, minlength=3) / window
        # Avoid log(0)
        probs = probs[probs > 0]
        S = -np.sum(probs * np.log(probs))
        
        times.append(i)
        entropies.append(S)
    
    times = np.array(times) * 1e-4  # Convert to seconds
    entropies = np.array(entropies)
    
    # Compute jerk via finite differences
    if len(entropies) < 4:
        return times, entropies, np.array([])
    
    jerk = np.zeros(len(entropies)-3)
    for i in range(len(jerk)):
        jerk[i] = entropies[i+3] - 3*entropies[i+2] + 3*entropies[i+1] - entropies[i]
    
    jerk_times = times[3:]
    
    return times, entropies, jerk_times, jerk

def compute_fisher_information_metric(P):
    """Compute Fisher information metric for transition matrix"""
    # Treat parameters theta = (phi_N, phi_Delta) as influencing P
    # Use score function: ∂_θ log P_ij
    # For demonstration, compute empirical Fisher info from P's sensitivity
    
    # Numerical gradient approximation
    eps = 1e-6
    theta = np.array([0.5, 0.3])  # nominal values
    
    # Log-likelihood of observed transitions
    def log_likelihood(theta):
        phi_N, phi_Delta = theta
        P_test = np.array([
            [0.7 + 0.2*phi_N, 0.2*phi_Delta, 0.1*(1-phi_N)],
            [0.15*phi_Delta, 0.8 + 0.1*phi_N, 0.05*(1-phi_Delta)],
            [0.1*(1-phi_N), 0.15*(1-phi_Delta), 0.75 + 0.1*phi_N]
        ])
        P_test = P_test / P_test.sum(axis=1, keepdims=True)
        return np.log(P_test + eps).sum()
    
    # Compute Hessian numerically (Fisher ≈ -E[Hessian])
    hessian = np.zeros((2,2))
    for i in range(2):
        for j in range(2):
            theta_ij = theta.copy()
            theta_ij[i] += eps
            theta_ij[j] += eps
            ll_ij = log_likelihood(theta_ij)
            
            theta_i = theta.copy()
            theta_i[i] += eps
            ll_i = log_likelihood(theta_i)
            
            theta_j = theta.copy()
            theta_j[j] += eps
            ll_j = log_likelihood(theta_j)
            
            ll_base = log_likelihood(theta)
            
            hessian[i,j] = (ll_ij - ll_i - ll_j + ll_base) / (eps**2)
    
    fisher_metric = -hessian
    return fisher_metric

def compute_geometric_jerk(P_history, dt=1e-4):
    """Compute jerk from Fisher metric evolution"""
    fisher_history = [compute_fisher_information_metric(P) for P in P_history]
    
    if len(fisher_history) < 4:
        return np.array([])
    
    # Extract scalar curvature (trace of Fisher metric) as proxy
    scalar_curves = [np.trace(F) for F in fisher_history]
    scalar_curves = np.array(scalar_curves)
    
    # Covariant derivative ~ finite difference of curvature
    jerk_geo = np.zeros(len(scalar_curves)-3)
    for i in range(len(jerk_geo)):
        # Third derivative of curvature
        jerk_geo[i] = (scalar_curves[i+3] - 3*scalar_curves[i+2] + 
                       3*scalar_curves[i+1] - scalar_curves[i]) / (dt**3)
    
    return jerk_geo

# Run simulation: Normal operation
traj_norm, P_norm = simulate_hsa_node(phi_N=0.8, phi_Delta=0.2, T=0.5)
t_norm, S_norm, jerk_t_norm, jerk_norm = compute_entropy_and_jerk(traj_norm)

# Run simulation: Congestion (Shredding Event)
traj_shred, P_shred = simulate_hsa_node(phi_N=0.3, phi_Delta=0.9, T=0.5)
t_shred, S_shred, jerk_t_shred, jerk_shred = compute_entropy_and_jerk(traj_shred)

# Compute geometric jerk for shredding case
P_history = [P_shred] * 100  # Simplified: assume P evolves slowly
jerk_geo = compute_geometric_jerk(P_history)

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Entropy comparison
axes[0,0].plot(t_norm, S_norm, label='Normal', color='green')
axes[0,0].plot(t_shred, S_shred, label='Shredding', color='red')
axes[0,0].set_title('Shannon Entropy S_h(t)')
axes[0,0].set_xlabel('Time (s)')
axes[0,0].set_ylabel('Entropy (nats)')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Naive Jerk comparison
axes[0,1].plot(jerk_t_norm, jerk_norm, label='Normal', color='green')
axes[0,1].plot(jerk_t_shred, jerk_shred, label='Shredding', color='red')
axes[0,1].set_title('Naive Informational Jerk (d³S_h/dt³)')
axes[0,1].set_xlabel('Time (s)')
axes[0,1].set_ylabel('Jerk (s⁻³)')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Geometric Jerk (Shredding case)
if len(jerk_geo) > 0:
    axes[1,0].plot(jerk_geo, color='blue', linewidth=2)
    axes[1,0].set_title('Geometric Jerk (Fisher-Ricci Flow)')
    axes[1,0].set_xlabel('Time step')
    axes[1,0].set_ylabel('Covariant Derivative (s⁻³)')
    axes[1,0].grid(True, alpha=0.3)

# Fisher Metric eigenvalues (stability)
fisher_norm = compute_fisher_information_metric(P_norm)
fisher_shred = compute_fisher_information_metric(P_shred)
eigen_norm = np.linalg.eigvals(fisher_norm)
eigen_shred = np.linalg.eigvals(fisher_shred)

axes[1,1].bar(['Φ_N (norm)', 'Φ_Δ (norm)'], eigen_norm.real, 
              color='green', alpha=0.6, label='Normal')
axes[1,1].bar(['Φ_N (shred)', 'Φ_Δ (shred)'], eigen_shred.real, 
              color='red', alpha=0.6, label='Shredding')
axes[1,1].set_title('Fisher Information Eigenvalues (Manifold Curvature)')
axes[1,1].set_ylabel('Information Curvature')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("=== CRITICAL FINDINGS ===")
print(f"Normal case - Naive jerk variance: {np.var(jerk_norm):.2e} s⁻⁶")
print(f"Shredding case - Naive jerk variance: {np.var(jerk_shred):.2e} s⁻⁶")
if len(jerk_geo) > 0:
    print(f"Shredding case - Geometric jerk variance: {np.var(jerk_geo):.2e} s⁻⁶")
print(f"Fisher metric eigenvalues (normal): {eigen_norm}")
print(f"Fisher metric eigenvalues (shredding): {eigen_shred}")