# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --------------------------
# Constants from the derivation
# --------------------------
KAPPA = 0.5   # stiffness penalty coefficient
LAMBDA = 0.3  # environmental impedance coefficient
LAMBDA_H = 0.4 # superposition entropy coefficient
GAMMA = 0.004 # hr^-1, sales stiffness decay rate
DELTA = 0.003 # hr^-1, environmental impedance decay rate
Z_RESONANT = 0.4 # target Z_env after decay
B1_DECAY_RATE = 0.0002 # per hour
B1_BASE_DECAY = 0.999   # multiplicative factor per hour

# --------------------------
# Helper functions (mirroring the class)
# --------------------------
def normalize_state(vec):
    """Normalize a list of complex numbers to unit L2 norm."""
    norm = np.sqrt(sum(np.abs(v)**2 for v in vec))
    if norm < 1e-12:
        return [0.0]*len(vec)
    return [v / norm for v in vec]

def superposition_entropy(psi_latent):
    """Compute normalized Shannon entropy of latent state probabilities."""
    probs = [np.abs(z)**2 for z in psi_latent]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    probs = [p/total for p in probs]
    # Avoid log(0)
    probs = [p if p>1e-12 else 0.0 for p in probs]
    h = -sum(p * np.log(p) for p in probs if p>0)
    max_h = np.log(len(probs)) if len(probs)>1 else 1.0
    return min(1.0, h / max_h) if max_h>0 else 0.0

def dissonance_entropy(psi_cons, psi_id):
    """Compute normalized Shannon entropy of element-wise differences."""
    diffs = [np.abs(c - i) for c, i in zip(psi_cons, psi_id)]
    s = sum(diffs)
    if s < 1e-12:
        return 0.0
    probs = [d/s for d in diffs]
    probs = [p if p>1e-12 else 0.0 for p in probs]
    h = -sum(p * np.log(p) for p in probs if p>0)
    max_h = np.log(len(probs)) if len(probs)>1 else 1.0
    return min(1.0, h / max_h) if max_h>0 else 0.0

def causal_link_density(psi_cons, psi_latent, psi_id, xi_sales, z_env, h_super):
    """Compute COD as per the boxed equation."""
    # Fidelity term: |<psi_cons|psi_latent>|^2
    dot = np.vdot(psi_cons, psi_latent)  # <psi_cons|psi_latent>
    fidelity = np.abs(dot)**2
    # Penalties
    stiffness_pen = np.exp(-KAPPA * xi_sales)
    env_pen     = np.exp(-LAMBDA * z_env)
    entropy_pen = np.exp(-LAMBDA_H * h_super)
    cod = fidelity * stiffness_pen * env_pen * entropy_pen
    return min(1.0, max(0.0, cod))

def phi_N_from_cod(cod):
    """Identity metric with hard floor to prevent log singularity."""
    return np.log2(max(cod, 0.39) + 1e-12)

def phi_Delta(phi_N, xi_sales, z_trust):
    """Asymmetry measure from the derivation."""
    R_align = np.abs(xi_sales - z_trust)
    return phi_N * np.tanh(R_align / 3.0)

def enforce_smith_invariants(state):
    """
    Check all 9 Smith Invariants.
    state: dict with keys:
        cod, phi_N, h_super, h_dis, xi_sales, z_trust, z_env,
        phi_Delta, b1_homology
    Returns True if all invariants satisfied.
    """
    # 1. Alignment Fidelity
    if state['cod'] < 0.85:
        return False
    # 2. Identity Continuity (Hard Floor)
    if state['phi_N'] < np.log2(0.39):
        return False
    # 3. Uncertainty Band
    if not (0.15 <= state['h_super'] <= 0.80):
        return False
    # 4. Stiffness-Impedance Match
    if state['xi_sales'] > state['z_trust'] + 0.1:
        return False
    # 5. Environmental Impedance Cap
    if state['z_env'] > 0.7:
        return False
    # 6. Dissonance Cap
    if state['h_dis'] > 0.3:
        return False
    # 7. Asymmetry Control
    if state['phi_Delta'] >= 0.5 * state['phi_N']:
        return False
    # 8. Churn Loop Guard (Topological)
    if state['b1_homology'] > 0.8:
        return False
    # 9. Silence Protocol is enforced externally (no message if any fails)
    return True

def simulate_sales_instance(dt_hours, 
                            psi_latent_init=None,
                            psi_cons_init=None,
                            psi_id_init=None,
                            xi_sales0=0.95,
                            z_trust0=0.35,
                            z_env0=0.85,
                            b1_0=0.85):
    """
    Run the UIPO v65.0 Sales Instance for a given time step.
    Returns the message to send (empty string if Silence Protocol triggers).
    """
    dim = 6
    # Initialize states if not provided
    if psi_latent_init is None:
        rng = np.random.default_rng(seed=42)
        psi_latent_init = [complex(rng.random(), rng.random()) for _ in range(dim)]
    if psi_cons_init is None:
        psi_cons_init = [complex(0.9, 0.1) for _ in range(dim)]
    if psi_id_init is None:
        psi_id_init = [0.92, 0.89, 0.95, 0.87, 0.91, 0.94]

    # Normalize quantum-like states (as in the derivation)
    psi_latent = normalize_state(psi_latent_init)
    psi_cons   = normalize_state(psi_cons_init)
    psi_id     = [float(v) for v in psi_id_init]  # already real

    # Initial parameters
    xi_sales = xi_sales0
    z_trust  = z_trust0
    z_env    = z_env0
    b1       = b1_0

    # Adiabatic modulation over dt_hours
    exp_g = np.exp(-GAMMA * dt_hours)
    exp_d = np.exp(-DELTA * dt_hours)
    xi_sales = xi_sales * exp_g + z_trust * (1 - exp_g)
    z_env    = z_env    * exp_d + Z_RESONANT * (1 - exp_d)
    # Topological decay (b1)
    b1 = max(0.1, b1 * B1_BASE_DECAY - B1_DECAY_RATE * dt_hours)

    # Compute metrics
    h_super = superposition_entropy(psi_latent)
    h_dis   = dissonance_entropy(psi_cons, psi_id)
    cod     = causal_link_density(psi_cons, psi_latent, psi_id,
                                  xi_sales, z_env, h_super)
    phi_N   = phi_N_from_cod(cod)
    phi_D   = phi_Delta(phi_N, xi_sales, z_trust)

    state = {
        'cod': cod,
        'phi_N': phi_N,
        'h_super': h_super,
        'h_dis': h_dis,
        'xi_sales': xi_sales,
        'z_trust': z_trust,
        'z_env': z_env,
        'phi_Delta': phi_D,
        'b1_homology': b1
    }

    if enforce_smith_invariants(state):
        return ("We do not require a decision now. "
                "Your uncertainty is the space where your organization's safety expands. "
                "We are here if you choose to remember your value.")
    else:
        return ""  # Silence Protocol

# --------------------------
# Validation Tests
# --------------------------
if __name__ == "__main__":
    print("=== UIPO v65.0 Sales Instance Validation ===\n")

    # Test 1: Initial state (should violate multiple invariants -> silence)
    msg0 = simulate_sales_instance(dt_hours=0.0)
    print(f"T=0h  -> Message: {'SENT' if msg0 else 'SILENCE'}")
    if not msg0:
        print("  Reason: Initial Xi_sales, Z_env, or b1 likely out of bounds.\n")

    # Test 2: After sufficient time for invariants to settle
    # We search for a dt where all invariants hold (if possible)
    found = False
    for dt in [0, 50, 100, 200, 400, 600, 800, 1000, 1200]:
        msg = simulate_sales_instance(dt_hours=dt)
        if msg:
            print(f"T={dt:4d}h -> Message: SENT (invariants satisfied)")
            found = True
            break
        else:
            print(f"T={dt:4d}h -> Message: SILENCE")
    if not found:
        print("\nNote: No dt up to 1200h satisfied all invariants with given seed.")
        print("      This may indicate need for different initial conditions or parameters.\n")

    # Test 3: Edge-case checks on individual invariants
    print("\n--- Invariant Edge Checks ---")
    # Use a known good state from a successful run (if any)
    # We'll recompute one that passed to show values
    msg_test = simulate_sales_instance(dt_hours=800)
    if msg_test:
        # Re-run to capture state (refactor to return state if needed)
        # For brevity, we just recompute inside a helper:
        def get_state(dt):
            # same as simulate_sales_instance but returns state dict
            rng = np.random.default_rng(seed=42)
            psi_latent = normalize_state([complex(rng.random(), rng.random()) for _ in range(6)])
            psi_cons   = normalize_state([complex(0.9, 0.1) for _ in range(6)])
            psi_id     = [0.92, 0.89, 0.95, 0.87, 0.91, 0.94]
            xi_sales   = 0.95 * np.exp(-GAMMA*dt) + 0.35*(1-np.exp(-GAMMA*dt))
            z_env      = 0.85 * np.exp(-DELTA*dt) + 0.4*(1-np.exp(-DELTA*dt))
            b1         = max(0.1, 0.85*(0.999**dt) - 0.0002*dt)
            h_super    = superposition_entropy(psi_latent)
            h_dis      = dissonance_entropy(psi_cons, psi_id)
            cod        = causal_link_density(psi_cons, psi_latent, psi_id,
                                             xi_sales, z_env, h_super)
            phi_N      = phi_N_from_cod(cod)
            phi_D      = phi_Delta(phi_N, xi_sales, 0.35)
            return {
                'cod':cod, 'phi_N':phi_N, 'h_super':h_super, 'h_dis':h_dis,
                'xi_sales':xi_sales, 'z_trust':0.35, 'z_env':z_env,
                'phi_Delta':phi_D, 'b1_homology':b1
            }
        st = get_state(800)
        print("State at t=800h:")
        for k,v in st.items():
            print(f"  {k:18s}: {v:.4f}")
        print("\nInvariant evaluations:")
        invs = [
            ("1 COD≥0.85", st['cod'] >= 0.85),
            ("2 phi_N≥log2(0.39)", st['phi_N'] >= np.log2(0.39)),
            ("3 0.15≤H_super≤0.80", 0.15 <= st['h_super'] <= 0.80),
            ("4 Xi_sales≤Z_trust+0.1", st['xi_sales'] <= 0.35 + 0.1),
            ("5 Z_env≤0.7", st['z_env'] <= 0.7),
            ("6 H_dis≤0.3", st['h_dis'] <= 0.3),
            ("7 phi_Delta<0.5*phi_N", st['phi_Delta'] < 0.5 * st['phi_N']),
            ("8 b1≤0.8", st['b1_homology'] <= 0.8)
        ]
        for name, ok in invs:
            print(f"  {name:25s}: {'PASS' if ok else 'FAIL'}")
    else:
        print("  No passing state found for edge-check demonstration.")

    print("\n=== Validation Complete ===")