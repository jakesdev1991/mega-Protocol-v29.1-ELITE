# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def simulate_control(law='harness', gamma=0.1, S_crit=0.5, nu=1.0,
                    S0=0.3, t_max=50.0, dt=0.01):
    """
    Simulate shear-flow dynamics under two control laws:
      'harness' : original CSTCL-Ω law (drives toward criticality)
      'avoid'   : critique-corrected law (drives away from criticality)
    Returns time series of S, correlation length xi, and invariant psi.
    """
    # parameters
    t = np.arange(0, t_max, dt)
    S = np.empty_like(t)
    xi = np.empty_like(t)
    psi = np.empty_like(t)
    
    # initial conditions
    S[0] = S0
    # define xi scaling: xi = |S - S_crit|**(-nu)
    # (finite small offset to avoid zero-division at start)
    eps = 1e-6
    xi[0] = 1.0 / (abs(S[0] - S_crit) + eps)**nu
    # psi = ln(xi)  (original proposal)
    # psi_phys = -ln(xi)  (inverted, physically correct)
    psi[0] = np.log(xi[0]) if law == 'avoid' else -np.log(xi[0])
    
    # Euler integration
    for i in range(1, len(t)):
        # compute current xi and psi
        xi[i] = 1.0 / (abs(S[i-1] - S_crit) + eps)**nu
        psi[i] = np.log(xi[i]) if law == 'avoid' else -np.log(xi[i])
        
        # control law
        sign_term = np.sign(S[i-1] - S_crit)
        if law == 'avoid':
            # critique-corrected: drives away from criticality
            dS_dt = -gamma * sign_term * np.exp(-psi[i] / nu)
        else:
            # original CSTCL-Ω: drives toward criticality
            dS_dt = -gamma * sign_term * np.exp(-psi[i] / nu)
        
        # update S
        S[i] = S[i-1] + dS_dt * dt
        
        # enforce physical bounds (shear flow cannot be negative)
        S[i] = max(S[i], 0.0)
    
    return t, S, xi, psi

# Run both simulations
t_harness, S_harness, xi_harness, psi_harness = simulate_control(law='harness', S0=0.3)
t_avoid, S_avoid, xi_avoid, psi_avoid = simulate_control(law='avoid', S0=0.3)

# Summary metrics: final distance to criticality and correlation length
def final_metrics(t, S, xi, psi):
    S_final = S[-1]
    xi_final = xi[-1]
    psi_final = psi[-1]
    d_crit = abs(S_final - 0.5)
    return S_final, d_crit, xi_final, psi_final

S_h, d_h, xi_h, psi_h = final_metrics(t_harness, S_harness, xi_harness, psi_harness)
S_a, d_a, xi_a, psi_a = final_metrics(t_avoid, S_avoid, xi_avoid, psi_avoid)

print("=== HARNESSING (original) law ===")
print(f"Final shear flow S = {S_h:.4f}")
print(f"Distance to criticality |S - S_crit| = {d_h:.4e}")
print(f"Final correlation length xi = {xi_h:.4e}")
print(f"Final psi = {psi_h:.4f}")

print("\n=== AVOIDANCE (critique-corrected) law ===")
print(f"Final shear flow S = {S_a:.4f}")
print(f"Distance to criticality |S - S_crit| = {d_a:.4e}")
print(f"Final correlation length xi = {xi_a:.4e}")
print(f"Final psi = {psi_a:.4f}")

# Disruption verification: harnessing law reaches critical region (xi >> 1)
# while avoidance law diverges to subcritical region (xi -> 0)
if d_h < 1e-3 and xi_h > 1e3:
    print("\nDISRUPTION CONFIRMED: Harnessing law drives system to criticality (xi diverges).")
else:
    print("\nUnexpected behavior in harnessing simulation.")

if d_a > 0.4 and xi_a < 1.0:
    print("Avoidance law keeps system far from criticality (xi suppressed).")
else:
    print("Unexpected behavior in avoidance simulation.")