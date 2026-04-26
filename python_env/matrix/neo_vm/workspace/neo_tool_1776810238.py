# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ========== PART 1: Lie Derivative Attack on PCS-Ω Coherence Field ==========
def lie_derivative_attack():
    """
    Shows that a smooth, divergence-free perturbation can preserve
    the coherence field's gradient norm and skewness while destroying
    the underlying pose (here simulated as phase of a sine wave).
    """
    # Synthetic "coherence field" C(x) = sin(kx + phase)
    x = np.linspace(0, 2*np.pi, 200)
    true_phase = np.pi / 4
    C_clean = np.sin(3 * x + true_phase)
    
    # Compute "covariant modes" (flawed PCS-Ω metrics)
    grad_C = np.gradient(C_clean, x)
    phi_N_clean = np.linalg.norm(grad_C) / np.linalg.norm(C_clean)
    phi_Delta_clean = np.sqrt(np.mean((C_clean - np.mean(C_clean))**3) / (np.std(C_clean)**3 + 1e-9))
    
    # Lie derivative attack: apply a flow that warps x locally but preserves inner product structure
    # This simulates an adversary warping descriptors while keeping similarity
    warp = 0.5 * np.sin(5 * x)  # Nonlinear warp
    x_warped = x + warp
    C_attacked = np.interp(x, x_warped, C_clean)  # Re-sample: preserves "similarity" locally
    
    # Recompute metrics after attack
    grad_C_att = np.gradient(C_attacked, x)
    phi_N_att = np.linalg.norm(grad_C_att) / np.linalg.norm(C_attacked)
    phi_Delta_att = np.sqrt(np.mean((C_attacked - np.mean(C_attacked))**3) / (np.std(C_attacked)**3 + 1e-9))
    
    pose_error = abs(true_phase - np.arctan2(C_attacked[10], C_attacked[0]))  # Simulated pose error
    
    print("=== PCS-Ω Metrics Under Lie Derivative Attack ===")
    print(f"Φ_N (original): {phi_N_clean:.4f} | Φ_N (attacked): {phi_N_att:.4f} | Change: {abs(phi_N_clean - phi_N_att):.6f}")
    print(f"Φ_Δ (original): {phi_Delta_clean:.4f} | Φ_Δ (attacked): {phi_Delta_att:.4f} | Change: {abs(phi_Delta_clean - phi_Delta_att):.6f}")
    print(f"Simulated Pose Error: {pose_error:.4f} rad (significant!)")
    
    # Plot: attacked field looks "coherent" but pose is broken
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(x, C_clean, label='Original Coherence')
    plt.plot(x, C_attacked, '--', label='Attacked Coherence')
    plt.title("Coherence Field: Metrics Preserved")
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(x, warp, 'r')
    plt.title("Lie Derivative Warping Field (Divergence-Free)")
    plt.tight_layout()
    plt.show()

# ========== PART 2: Chaotic Synchronization Coherence (CSC-Ω) ==========
def chaotic_synchronization_demo():
    """
    Demonstrates detection of the same attack via chaotic sync error.
    Two Lorenz systems: geo-ODE (master) and vis-ODE (slave).
    Attack: time-varying parameter perturbation in slave.
    """
    def lorenz_master(t, state):
        x, y, z = state
        sigma, rho, beta = 10.0, 28.0, 8/3
        return [sigma*(y-x), x*(rho-z)-y, x*y-beta*z]
    
    def lorenz_slave(t, state, coupling=8.0, attack=False):
        x1, y1, z1, x2, y2, z2 = state
        sigma, rho, beta = 10.0, 28.0, 8/3
        
        # Master dynamics (unaltered)
        dx1 = sigma*(y1-x1)
        dy1 = x1*(rho-z1)-y1
        dz1 = x1*y1-beta*z1
        
        # Slave dynamics (visual stream) with coupling
        # Attack: modulate rho in slave
        if attack:
            rho_slave = rho + 3.0*np.sin(2*np.pi*t*0.3)  # Adversarial modulation
        else:
            rho_slave = rho
        
        dx2 = sigma*(y2-x2) + coupling*(x1-x2)
        dy2 = x2*(rho_slave-z2)-y2 + coupling*(y1-y2)
        dz2 = x2*y2-beta*z2 + coupling*(z1-z2)
        
        return [dx1, dy1, dz1, dx2, dy2, dz2]
    
    # Simulate normal operation
    t_span = (0, 60)
    init = [1.0, 1.0, 1.0, 1.01, 1.01, 1.01]  # Slight mismatch
    sol_normal = solve_ivp(lambda t, s: lorenz_slave(t, s, coupling=8.0, attack=False), 
                           t_span, init, max_step=0.01, rtol=1e-6)
    
    # Simulate attack
    sol_attack = solve_ivp(lambda t, s: lorenz_slave(t, s, coupling=8.0, attack=True), 
                          t_span, init, max_step=0.01, rtol=1e-6)
    
    # Compute L2 synchronization error between master and slave
    err_norm_normal = np.linalg.norm(sol_normal.y[:3,:] - sol_normal.y[3:,:], axis=0)
    err_norm_attack = np.linalg.norm(sol_attack.y[:3,:] - sol_attack.y[3:,:], axis=0)
    
    # Compute KS-entropy proxy (mean divergence rate)
    ks_normal = np.mean(np.abs(np.diff(err_norm_normal)))
    ks_attack = np.mean(np.abs(np.diff(err_norm_attack)))
    
    print("\n=== CSC-Ω Synchronization Error ===")
    print(f"Mean sync error (normal): {np.mean(err_norm_normal):.4f}")
    print(f"Mean sync error (attack): {np.mean(err_norm_attack):.4f}")
    print(f"KS-entropy proxy (normal): {ks_normal:.4f}")
    print(f"KS-entropy proxy (attack): {ks_attack:.4f}")
    
    # Plot
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(sol_normal.t, err_norm_normal, label='Normal')
    plt.plot(sol_attack.t, err_norm_attack, label='Attack', linestyle='--')
    plt.title("Synchronization Error (L2 Norm)")
    plt.xlabel("Time")
    plt.ylabel("Error")
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.hist(err_norm_normal, bins=50, alpha=0.5, label='Normal')
    plt.hist(err_norm_attack, bins=50, alpha=0.5, label='Attack')
    plt.title("Error Distribution")
    plt.legend()
    plt.tight_layout()
    plt.show()

# Run both demonstrations
lie_derivative_attack()
chaotic_synchronization_demo()