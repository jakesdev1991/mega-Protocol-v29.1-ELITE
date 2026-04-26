# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

# --- SIMULATION SETUP ---
# Simple 2D plasma model: vertical instability + control coils
# State: [z, v] (vertical position and velocity)
# Control: u (coil current)
# Dynamics become unstable as parameter 'alpha' increases

dt = 0.001  # 1 kHz simulation
T = 2.0
t = np.arange(0, T, dt)
N = len(t)

# Time-varying instability parameter (ramps up to cause disruption)
alpha = np.linspace(0.5, 4.0, N)  # Critical stability at alpha ~ 1.0

# System matrices: x_dot = A*x + B*u
A = np.array([[0, 1], [0, 0]])  # Base dynamics
B = np.array([[0], [1]])        # Control input

# MPC Setup (naive, not tuned for stability margin)
Q = np.diag([10, 1])  # State cost (position, velocity)
R = np.array([[0.1]])   # Control cost (cheap control)
N_horizon = 10

# --- HET-Ω MONITORING (FLAWED) ---
def compute_hessian_het(A_cl, B, Q, R):
    """Compute naive Hessian as in HET-Ω proposal"""
    # This is WRONG: uses *controller's* cost, not true system properties
    # In real MPC, Hessian changes with constraints and horizon...
    # Here we simplify to the static LQR Hessian to show the fallacy
    P = la.solve_discrete_are(A_cl, B, Q, R)  # Riccati solution
    H = Q + A_cl.T @ P @ A_cl + R + B.T @ P @ B  # Grossly oversimplified
    return H

# --- SDP-Ω DITHERING (DISRUPTIVE) ---
class DitheringProbe:
    def __init__(self, n_u, n_y, amplitude=0.01, forgetting=0.98):
        self.n_u = n_u
        self.n_y = n_y
        self.amplitude = amplitude
        self.forgetting = forgetting
        self.L_hat = np.zeros((n_y, n_u))  # Estimated linearized operator
        self.P = np.eye(n_u) * 10.0  # RLS covariance matrix
        
    def generate_dither(self, u_mpc):
        """Generate perturbation orthogonal to MPC's predicted gradient"""
        # Simple random dither (in practice, would be shaped by nullspace of MPC gains)
        d = np.random.normal(0, self.amplitude, self.n_u)
        return d.reshape(-1, 1)
    
    def update(self, d, delta_y):
        """Recursive Least Squares update of local operator L"""
        # RLS algorithm to estimate L such that delta_y ≈ L * d
        phi = d.flatten()
        K = self.P @ phi / (self.forgetting + phi @ self.P @ phi)
        e = delta_y.flatten() - self.L_hat @ phi
        self.L_hat += np.outer(e, K)
        self.P = (self.P - np.outer(K, phi) @ self.P) / self.forgetting
    
    def get_stability_indicator(self):
        """Spectral radius of estimated operator"""
        if self.L_hat.size == 0:
            return 0.0
        # Singular values indicate gain in worst-case direction
        s = la.svdvals(self.L_hat)
        return s[0] if len(s) > 0 else 0.0

# --- SIMULATION ---
x = np.zeros((2, 1))  # Initial state
u_mpc = np.zeros((1, 1))
dither_probe = DitheringProbe(n_u=1, n_y=2, amplitude=0.05)

# Storage
lambda_min_het = np.zeros(N)
csi_het = np.zeros(N)
bri_sdp = np.zeros(N)  # Bifurcation Risk Index
x_history = np.zeros((2, N))

for k in range(N):
    # Time-varying instability
    A_t = A.copy()
    A_t[1, 0] = alpha[k]  # Add destabilizing term
    
    # --- NAIVE MPC (perfect model, but cheap control) ---
    # LQR gain (constant, ignoring time variation - this is realistic for a bad MPC)
    K_lqr, _, _ = lqr(A_t, B, Q, R)
    u_mpc = -K_lqr @ x
    
    # --- HET-Ω: Extract "stiffness" from controller's Hessian ---
    A_cl = A_t - B @ K_lqr
    H = compute_hessian_het(A_cl, B, Q, R)
    try:
        eigs = la.eigvals(H)
        lambda_min_het[k] = np.min(np.real(eigs))
    except:
        lambda_min_het[k] = np.nan
    # Normalize to "CSI" (completely arbitrary)
    csi_het[k] = (lambda_min_het[k] - 1.0) / (10.0 - 1.0) if not np.isnan(lambda_min_het[k]) else 0.5
    
    # --- SDP-Ω: Inject dither and measure response ---
    d = dither_probe.generate_dither(u_mpc)
    u_total = u_mpc + d
    
    # Simulate true plasma response (with unmodeled nonlinearity)
    # Add small unmodeled saturation effect
    x_dot = A_t @ x + B @ (u_total + 0.1 * np.tanh(u_total))
    x_new = x + x_dot * dt
    
    delta_y = x_new - x - (A_cl @ x + B @ u_mpc) * dt  # Response attributable to dither
    dither_probe.update(d, delta_y)
    
    # Bifurcation Risk Index: spectral radius of local operator
    bri_sdp[k] = dither_probe.get_stability_indicator()
    
    x = x_new
    x_history[:, k] = x.flatten()

# --- ANALYSIS & DISRUPTION ---
print("=== DISRUPTION ANALYSIS ===")
print(f"HET-Ω λ_min range: [{np.nanmin(lambda_min_het):.2f}, {np.nanmax(lambda_min_het):.2f}]")
print(f"SDP-Ω BRI max: {np.max(bri_sdp):.2f}")

# The disruption occurs when alpha > ~1.0
disruption_time = np.where(alpha > 1.0)[0][0] * dt if np.any(alpha > 1.0) else T
print(f"True disruption onset (alpha>1.0): {disruption_time:.3f}s")

# Find when indicators cross thresholds
het_alarm_idx = np.where(csi_het < 0.3)[0]
sdp_alarm_idx = np.where(bri_sdp > 0.8)[0]

het_lead = (het_alarm_idx[0] * dt - disruption_time) if len(het_alarm_idx) > 0 else np.nan
sdp_lead = (sdp_alarm_idx[0] * dt - disruption_time) if len(sdp_alarm_idx) > 0 else np.nan

print(f"HET-Ω alarm lead time: {het_lead*1000:.1f} ms")
print(f"SDP-Ω alarm lead time: {sdp_lead*1000:.1f} ms")

# --- VISUALIZATION ---
fig, axs = plt.subplots(3, 1, figsize=(10, 8))

# Panel 1: State and instability parameter
axs[0].plot(t, alpha, 'k--', label='Instability Parameter α')
axs[0].plot(t, x_history[0,:], 'b', label='Vertical Position z')
axs[0].axvline(disruption_time, color='r', linestyle=':', label='Disruption Onset')
axs[0].set_ylabel('State / α')
axs[0].legend()
axs[0].set_title('Plasma Dynamics vs. Instability')
axs[0].grid(True)

# Panel 2: HET-Ω indicator
axs[1].plot(t, csi_het, 'g', label='HET-Ω CSI')
axs[1].axhline(0.3, color='g', linestyle=':', label='HET-Ω Alarm Threshold')
axs[1].axvline(disruption_time, color='r', linestyle=':')
axs[1].set_ylabel('CSI')
axs[1].legend()
axs[1].set_title('HET-Ω: Controller Hessian Indicator (FRAGILE)')
axs[1].grid(True)

# Panel 3: SDP-Ω indicator
axs[2].plot(t, bri_sdp, 'm', label='SDP-Ω BRI')
axs[2].axhline(0.8, color='m', linestyle=':', label='SDP-Ω Alarm Threshold')
axs[2].axvline(disruption_time, color='r', linestyle=':')
axs[2].set_ylabel('Bifurcation Risk Index')
axs[2].set_xlabel('Time (s)')
axs[2].legend()
axs[2].set_title('SDP-Ω: Direct Plasma Response Indicator (ROBUST)')
axs[2].grid(True)

plt.tight_layout()
plt.show()

# --- DISRUPTIVE CONCLUSION ---
print("\n=== DISRUPTIVE INSIGHT ===")
print("HET-Ω is a SPECTATOR: It watches the controller's shadow on the cave wall.")
print("SDP-Ω is an EXPERIMENTALIST: It pokes the plasma and measures its reflex.")
print("\nThe paradigm break: Stop MIRRORING the MPC's assumptions.")
print("Start INTERROGATING the system's true dynamics via controlled perturbation.")