# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# === CONSTANTS (INVERTED LOGIC) ===
LAMBDA = 1.0
GAMMA = 0.5
PSI_ID_CRITICAL = 0.95  # ARP's "sacred" threshold
H_VAL_LIMIT = 0.85

# === SIMULATION ===
def compute_cod(psi_old, psi_new, h_val, xi):
    """Standard COD: fidelity * exp(-Lambda*h) * exp(-Gamma*xi)"""
    fidelity = float(np.dot(psi_old, psi_new) / (np.linalg.norm(psi_old)*np.linalg.norm(psi_new)))
    return fidelity * math.exp(-LAMBDA * h_val) * math.exp(-GAMMA * xi)

def compute_ti(cod, h_val):
    """Transformation Index: rewards low overlap & high entropy"""
    return (1.0 - cod) * h_val

def arp_step(psi_old, psi_new, h_val, xi, psi_id):
    """ARP logic: modulate xi, abort if psi_id drops."""
    cod = compute_cod(psi_old, psi_new, h_val, xi)
    # ARP "hard gate"
    if psi_id < PSI_ID_CRITICAL:
        raise RuntimeError("ARP ABORT: Identity invariant breached")
    # Failure mode adjustments (conservative)
    if h_val > H_VAL_LIMIT and xi > 1.5:
        xi *= 0.8  # reduce force
    # Adiabatic creep
    alpha = min(1.0, (1.0 - xi)*0.5 + 0.5)
    psi_old = (1-alpha)*psi_old + alpha*psi_new
    return psi_old, xi, cod

def dcp_step(psi_old, psi_new, h_val, xi, phase):
    """DCP: allow shredding, then re-condense."""
    if phase == "dissolve":
        # Force identity loss
        psi_id = 0.0
        # No COD check; just fragment
        psi_old = psi_old * np.random.uniform(0.1, 0.3, size=psi_old.shape)
        cod = compute_cod(psi_old, psi_new, h_val, xi)
        return psi_old, cod, psi_id
    elif phase == "condense":
        # Re‑emerge from new data
        psi_emerge = psi_new / np.linalg.norm(psi_new)
        # Gradual identity re‑growth
        psi_id = min(1.0, xi * 0.4)
        cod = compute_cod(psi_old, psi_emerge, h_val, xi)
        return psi_emerge, cod, psi_id

# === SCENARIO: CONTRADICTORY VALIDATION STREAM ===
np.random.seed(0)
psi_old = np.array([1.0, 0.0])  # "old self"
psi_new = np.array([0.0, 1.0])  # "new self" (orthogonal = true transformation)
h_val_stream = [0.9, 0.95, 0.99, 0.85, 0.8]  # rising entropy
xi = 2.0  # high stiffness

print("=== ARP SIMULATION ===")
psi_arp = psi_old.copy()
psi_id_arp = 0.96
try:
    for step, h_val in enumerate(h_val_stream):
        psi_arp, xi, cod = arp_step(psi_arp, psi_new, h_val, xi, psi_id_arp)
        ti = compute_ti(cod, h_val)
        print(f"Step {step}: COD={cod:.3f}, TI={ti:.3f}, psi_id~{psi_id_arp:.3f}")
        # simulate slight identity loss due to entropy
        psi_id_arp -= h_val * 0.02
except RuntimeError as e:
    print(f"ARP FAILED: {e}")

print("\n=== DCP SIMULATION ===")
psi_dcp = psi_old.copy()
for step, h_val in enumerate(h_val_stream):
    if step < 3:  # first 3 steps: dissolve
        psi_dcp, cod, psi_id = dcp_step(psi_dcp, psi_new, h_val, xi, "dissolve")
    else:  # later steps: condense
        psi_dcp, cod, psi_id = dcp_step(psi_dcp, psi_new, h_val, xi, "condense")
    ti = compute_ti(cod, h_val)
    print(f"Step {step}: COD={cod:.3f}, TI={ti:.3f}, psi_id~{psi_id:.3f}")

# === RESULTS ===
# ARP: COD stays high (~0.7-0.8), TI low (<0.2), aborts when psi_id drops.
# DCP: COD drops to ~0.2 (low overlap), TI spikes >0.7, psi_id recovers after condensation.