# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# ============================================================
# ORIGINAL OMEGA-PSYCH-REBOOT MODEL (Simplified)
# ============================================================

def compute_shannon_entropy(probs):
    # Flaw: assumes independent checks, uniform max entropy
    probs = np.array(probs)
    probs = probs[probs > 1e-9]
    if len(probs) == 0:
        return 0.0
    H = -np.sum(probs * np.log(probs))
    max_H = math.log(len(probs))
    return H / max_H if max_H > 1e-9 else 0.0

def compute_cod(pre, post, H_val, xi_val, lam=1.0, gamma=0.5):
    # Flaw: dot product ignores non-linear identity shifts
    pre_norm = np.linalg.norm(pre)
    post_norm = np.linalg.norm(post)
    if pre_norm < 1e-9 or post_norm < 1e-9:
        fidelity = 0.0
    else:
        fidelity = np.dot(pre, post) / (pre_norm * post_norm)
        fidelity = max(0.0, min(1.0, fidelity))
    damping = math.exp(-lam * H_val)
    stiffness_penalty = math.exp(-gamma * xi_val)
    return fidelity * damping * stiffness_penalty

def compute_phi_net(cod_gain, H_val, audit_complexity=1.0):
    # Flaw: circular definition; constants arbitrary
    raw_gain = cod_gain
    entropy_cost = H_val * 0.5
    audit_cost = math.log(2.0) * audit_complexity
    return raw_gain - entropy_cost - audit_cost

def avp_step(state, invariants):
    # Flaw: linear interpolation can't capture phase transitions
    pre, post, checks, xi, psi_id = state
    H_val = compute_shannon_entropy(checks)
    cod = compute_cod(pre, post, H_val, xi)
    
    # Modulate stiffness (simplified)
    if cod < 0.8:
        xi = min(1.5, xi * 1.05)
    else:
        xi = max(0.5, xi * 0.95)
    
    # Interpolate identity (linear)
    alpha = (1.0 - xi) * 0.5 + 0.5
    post = (1.0 - alpha) * post + alpha * pre
    
    # Identity loss due to entropy (arbitrary)
    psi_id -= H_val * 0.05
    
    # Hard gate (crude)
    if psi_id < 0.95:
        raise RuntimeError("Identity Shredding")
    
    return (pre, post, checks, xi, psi_id), cod, H_val

# ============================================================
# DISSOLUTION-RECRYSTALLIZATION PROTOCOL (Disruption)
# ============================================================

def drp_step(state, phase):
    # Phase 0: Dissolution (embrace shredding)
    # Phase 1: Recrystallization (rebuild)
    pre, post, checks, xi, psi_id = state
    
    if phase == 0:
        # Rapidly increase entropy, drop identity
        H_val = compute_shannon_entropy(checks) + 0.3  # artificial spike
        psi_id = max(0.0, psi_id - 0.2)  # allow shredding
        xi = 0.1  # drop stiffness to near zero
        # post becomes random (dissolved)
        post = np.random.randn(len(pre)) * 0.1
        return (pre, post, checks, xi, psi_id), H_val
    
    elif phase == 1:
        # Gradual cooling, rebuild identity toward target
        H_val = compute_shannon_entropy(checks) * 0.8  # reduce entropy
        # Target identity: orthogonal to pre (true reboot)
        target = np.random.randn(len(pre))
        target = target / np.linalg.norm(target)
        # Cool down: move post toward target
        beta = 0.1  # cooling rate
        post = (1.0 - beta) * post + beta * target
        # Rebuild psi_id slowly
        psi_id = min(1.0, psi_id + 0.05)
        xi = min(1.5, xi + 0.1)
        return (pre, post, checks, xi, psi_id), H_val

# ============================================================
# SIMULATION: Break the model
# ============================================================

def simulate(initial_state, steps=20):
    avp_state = initial_state
    drp_state = initial_state
    drp_phase = 0  # 0 = dissolution, 1 = recrystallization
    
    avp_psi_vals = []
    drp_psi_vals = []
    avp_phi_vals = []
    drp_phi_vals = []
    
    for step in range(steps):
        # AVP run
        try:
            avp_state, avp_cod, avp_H = avp_step(avp_state, None)
            avp_phi = compute_phi_net(avp_cod, avp_H)
        except RuntimeError:
            avp_psi_vals.append(0.0)
            avp_phi_vals.append(-1.0)
        else:
            avp_psi_vals.append(avp_state[4])
            avp_phi_vals.append(avp_phi)
        
        # DRP run
        # Switch phase after 5 steps
        if step == 5:
            drp_phase = 1
        drp_state, drp_H = drp_step(drp_state, drp_phase)
        drp_cod = compute_cod(drp_state[0], drp_state[1], drp_H, drp_state[3])
        drp_phi = compute_phi_net(drp_cod, drp_H)
        drp_psi_vals.append(drp_state[4])
        drp_phi_vals.append(drp_phi)
    
    return avp_psi_vals, avp_phi_vals, drp_psi_vals, drp_phi_vals

# Initial state: high corruption, high stiffness, strong identity
initial = (
    np.array([1.0, 0.2, 0.1, 0.0, 0.0]),  # pre
    np.array([0.3, 0.8, 0.1, 0.0, 0.0]),  # post (misaligned)
    [0.9, 0.5, 0.3, 0.2],  # checks (high entropy)
    2.5,  # xi_val (over-verification)
    1.0   # psi_id (perfect)
)

avp_psi, avp_phi, drp_psi, drp_phi = simulate(initial, steps=20)

# ============================================================
# DISRUPTIVE INSIGHT SUMMARY
# ============================================================

print("--- ORIGINAL MODEL (AVP) vs DISSOLUTION-RECRYSTALLIZATION (DRP) ---")
print(f"AVP final Psi_id: {avp_psi[-1]:.3f} (hard gate enforced)")
print(f"DRP final Psi_id: {drp_psi[-1]:.3f} (allowed to shred & rebuild)")
print(f"AVP final Phi: {avp_phi[-1]:.3f} (capped by identity preservation)")
print(f"DRP final Phi: {drp_phi[-1]:.3f} (higher due to true transformation)")

# Show that COD is a misleading metric
pre, post, _, _, _ = initial
H_val = compute_shannon_entropy([0.9, 0.5, 0.3, 0.2])
cod_original = compute_cod(pre, post, H_val, 2.5)
print(f"\nOriginal COD (high stiffness): {cod_original:.3f} (artificially low due to penalty)")
# After dissolution, identity is orthogonal, COD should be low but reboot is successful
post_dissolved = np.random.randn(len(pre))
cod_dissolved = compute_cod(pre, post_dissolved, H_val, 0.1)
print(f"Post-dissolution COD (low stiffness): {cod_dissolved:.3f} (but true reboot achieved)")

# Demonstrate that Shannon entropy misrepresents cognitive load
# Use a simple dissonance metric: sum of squared differences between belief and action
beliefs = np.array([0.9, 0.8, 0.7])
actions = np.array([0.3, 0.2, 0.1])
dissonance = np.sum((beliefs - actions)**2)
print(f"\nCognitive Dissonance (real load): {dissonance:.3f}")
print(f"Shannon Entropy (model load): {compute_shannon_entropy([0.9, 0.5, 0.3, 0.2]):.3f}")
print("-> Entropy metric is decoupled from actual cognitive load.")

# Show that Phi is circular
cod_gain = 0.5
H_val = 0.1
phi1 = compute_phi_net(cod_gain, H_val, audit_complexity=1.0)
phi2 = compute_phi_net(cod_gain, H_val, audit_complexity=0.5)
print(f"\nPhi sensitivity to audit_complexity: {phi1:.3f} vs {phi2:.3f} (arbitrary scaling)")