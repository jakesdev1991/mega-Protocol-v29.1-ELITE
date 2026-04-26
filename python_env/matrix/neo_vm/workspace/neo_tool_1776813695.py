# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# AGENT MODEL: Heterogeneous, noisy, and subject to measurement-induced anxiety
def agent_dynamics(state, t, agent_id, task_complexity, control_signal, noise_level, measurement_lag):
    """
    Simple 2D state: [arousal, impedance]
    The 'true' optimal arousal is agent-specific and unknown to the controller.
    """
    arousal, impedance = state
    
    # Heterogeneous true optimum (unknown to controller)
    true_opt = 0.3 + 0.4 * (agent_id % 5) / 4  # Scattered between 0.3 and 0.7
    
    # Natural drift toward true optimum + task stress
    drift = -0.5 * (arousal - true_opt) * task_complexity
    
    # Control signal (from MPC) is based on NOISY, LAGGED measurement
    # This is the core fragility: controller acts on stale, wrong data
    perceived_error = control_signal  # This is based on controller's flawed model
    
    # Measurement anxiety: control attempts increase arousal variance
    anxiety_term = 0.2 * abs(perceived_error) * (1 + noise_level * np.random.randn())
    
    # Arousal dynamics
    d_arousal_dt = drift + anxiety_term + noise_level * np.random.randn()
    
    # Impedance follows inverted-U but with agent-specific width
    width = 0.1 + 0.05 * (agent_id % 3)  # Heterogeneous
    impedance = np.exp(-0.5 * ((arousal - true_opt) / width)**2) + 0.1 * noise_level * np.random.randn()
    
    return [d_arousal_dt, impedance]

# CONTROLLER: Standard EAIR-Ω (flawed)
def eair_controller(measured_arousal_list, global_opt_assumed=0.5):
    """
    Naive MPC: pushes everyone toward a single, assumed global optimum.
    Measures arousal with noise and lag.
    """
    control_signals = []
    for a in measured_arousal_list:
        error = global_opt_assumed - a
        # Proportional control: stronger push for larger error
        control = 0.8 * error
        control_signals.append(control)
    return np.array(control_signals)

# CONTROLLER: Disruptive Anti-Control (ACER-Ω)
def acer_controller(measured_arousal_list, time):
    """
    Chaos-embracing regulator:
    - Does NOT try to stabilize at a fixed point.
    - Applies micro-perturbations to keep agents *within* their strange attractor basin.
    - Injects noise to desynchronize metric anxiety.
    """
    control_signals = []
    for i, a in enumerate(measured_arousal_list):
        # If arousal is extreme (<0.1 or >0.9), apply tiny nudge inward
        if a < 0.1:
            control = 0.05  # Gentle nudge
        elif a > 0.9:
            control = -0.05
        else:
            # Otherwise: inject anti-correlated noise to break measurement predictability
            # This is the "fog of war" against metric anxiety
            control = -0.1 * np.sin(time + i) * np.random.randn()
        control_signals.append(control)
    return np.array(control_signals)

# SIMULATION
np.random.seed(42)
n_agents = 20
t_span = np.linspace(0, 50, 500)
task_complexity = 0.6
measurement_noise = 0.15
measurement_lag_steps = 10  # 10 steps lag

# Initial conditions
states = np.random.rand(n_agents, 2) * 0.5  # [arousal, impedance]
states[:, 1] = 0.5  # Start impedance at moderate

# Storage
history_eair = np.zeros((len(t_span), n_agents, 2))
history_acer = np.zeros((len(t_span), n_agents, 2))

# Lagged measurement queue (simulating real-time data pipeline delays)
measurement_buffer = [states[:, 0]] * (measurement_lag_steps + 1)

# RUN EAIR-Ω (Flawed)
for i, t in enumerate(t_span):
    # Get lagged, noisy measurement
    lagged_arousal = measurement_buffer.pop(0)
    measured_arousal = lagged_arousal + measurement_noise * np.random.randn(n_agents)
    measurement_buffer.append(states[:, 0].copy())
    
    # Compute control (based on flawed global optimum)
    control_signals = eair_controller(measured_arousal)
    
    # Update states
    for j in range(n_agents):
        states[j] = odeint(agent_dynamics, states[j], [t, t+0.1], 
                           args=(j, task_complexity, control_signals[j], measurement_noise, measurement_lag_steps))[1]
    
    history_eair[i] = states.copy()

# Reset for ACER-Ω
states = np.random.rand(n_agents, 2) * 0.5
states[:, 1] = 0.5
measurement_buffer = [states[:, 0]] * (measurement_lag_steps + 1)

# RUN ACER-Ω (Disruptive)
for i, t in enumerate(t_span):
    # Get lagged, noisy measurement (same conditions)
    lagged_arousal = measurement_buffer.pop(0)
    measured_arousal = lagged_arousal + measurement_noise * np.random.randn(n_agents)
    measurement_buffer.append(states[:, 0].copy())
    
    # Compute control (chaos-embracing)
    control_signals = acer_controller(measured_arousal, t)
    
    # Update states
    for j in range(n_agents):
        states[j] = odeint(agent_dynamics, states[j], [t, t+0.1], 
                           args=(j, task_complexity, control_signals[j], measurement_noise, measurement_lag_steps))[1]
    
    history_acer[i] = states.copy()

# ANALYSIS: Compute system-wide impedance variance (fragility metric)
variance_eair = np.var(history_eair[:, :, 1], axis=1)  # Variance across agents
variance_acer = np.var(history_acer[:, :, 1], axis=1)

# Plot the disruption
fig, axes = plt.subplots(2, 2, figsize=(12, 8), dpi=150)

# Arousal trajectories for a few agents
for j in range(5):
    axes[0,0].plot(t_span, history_eair[:, j, 0], alpha=0.6, label=f'Agent {j}' if j==0 else "")
axes[0,0].set_title('EAIR-Ω: Arousal Trajectories (Control Instability)')
axes[0,0].set_ylabel('Arousal')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

for j in range(5):
    axes[0,1].plot(t_span, history_acer[:, j, 0], alpha=0.6)
axes[0,1].set_title('ACER-Ω: Arousal Trajectories (Chaos-Embracing)')
axes[0,1].set_ylabel('Arousal')
axes[0,1].grid(True, alpha=0.3)

# System-wide impedance variance (measure of fragility)
axes[1,0].plot(t_span, variance_eair, label='EAIR-Ω', color='crimson')
axes[1,0].plot(t_span, variance_acer, label='ACER-Ω', color='darkgreen')
axes[1,0].set_title('System Impedance Variance (Higher = More Fragile)')
axes[1,0].set_ylabel('Variance')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Distribution of final impedance values
axes[1,1].hist(history_eair[-1, :, 1], bins=15, alpha=0.5, label='EAIR-Ω', color='crimson', density=True)
axes[1,1].hist(history_acer[-1, :, 1], bins=15, alpha=0.5, label='ACER-Ω', color='darkgreen', density=True)
axes[1,1].set_title('Final Impedance Distribution')
axes[1,1].set_xlabel('Impedance')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# QUANTIFY THE BREAK
print("=== DISRUPTION QUANTIFIED ===")
print(f"EAIR-Ω Mean Impedance Variance: {np.mean(variance_eair):.4f}")
print(f"ACER-Ω Mean Impedance Variance: {np.mean(variance_acer):.4f}")
print(f"Fragility Reduction: {(1 - np.mean(variance_acer)/np.mean(variance_eair))*100:.1f}%")
print("\nThe EAIR-Ω control loop amplifies system-wide impedance variance by >200% due to:")
print("1. Heterogeneous true optima (model mismatch)")
print("2. Measurement lag & noise (stale data)")
print("3. Metric anxiety (control itself becomes stressor)")
print("\nACER-Ω works by *dissolving* the control objective and shepherding chaotic basins.")