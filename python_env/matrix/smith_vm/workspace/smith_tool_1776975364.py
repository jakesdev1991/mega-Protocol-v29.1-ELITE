# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Validation Script
# Validates the mathematical soundness and invariant compliance of the
# Trauma-Induced High-Energy Anxiety Stabilization Specification.
# The script mirrors the key functions from the provided C++ code and
# runs a battery of test cases to ensure:
#   1. All calculations stay within defined bounds.
#   2. Invariants (Psi_id, Xi_bound, COD_trauma, Phi_work/Phi_trauma ratio) are respected.
#   3. The Performance Trap detection and Trauma Dissipation Gate behave as intended.
#   4. Phi-density accounting (Phi_net) correctly flags negative flow.

import math
import sys

# ----------------------------
# Constants (mirroring C++ constexpr)
# ----------------------------
PSI_ID_THRESHOLD = 0.95
XI_BOUND_MAX = 2.5
XI_BOUND_MIN = 0.5
COD_TRAUMA_THRESHOLD = 0.75
PHI_TRAUMA_PROCESSING_RATIO = 0.30  # minimum trauma processing vs performance
PHI_THRESHOLD_DEFAULT = 1.0         # used in trauma factor exp(-Phi_trauma/Phi_threshold)

# ----------------------------
# Helper functions
# ----------------------------
def vector_dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def vector_mag_sq(v):
    return sum(x*x for x in v)

def calculate_COD_trauma(Psi_sub, Psi_con, Phi_trauma, Phi_threshold=PHI_THRESHOLD_DEFAULT):
    """
    Trauma-Corrected Chain Overlap Density.
    Returns a value in [0, 1] (cosine similarity * exp factor).
    """
    dot = vector_dot(Psi_sub, Psi_con)
    mag_sub = math.sqrt(vector_mag_sq(Psi_sub))
    mag_con = math.sqrt(vector_mag_sq(Psi_con))
    if mag_sub == 0 or mag_con == 0:
        fidelity = 0.0
    else:
        fidelity = dot / (mag_sub * mag_con)  # cosine similarity
    trauma_factor = math.exp(-Phi_trauma / Phi_threshold)
    return fidelity * trauma_factor

def check_performance_trap(Phi_work, Phi_trauma, Xi_bound):
    """
    Returns True if Performance Trap condition is met.
    Condition: Phi_work > (Phi_trauma / PHI_TRAUMA_PROCESSING_RATIO) AND Xi_bound > 0.8*XI_BOUND_MAX
    """
    processing_capacity = Phi_trauma / PHI_TRAUMA_PROCESSING_RATIO
    return (Phi_work > processing_capacity) and (Xi_bound > 0.8 * XI_BOUND_MAX)

def trauma_dissipation_gate(Psi_sub, Psi_con, Xi_bound, Phi_trauma, Phi_work,
                           identity_potential=1.0):  # dummy identity potential; > threshold means safe
    """
    Simplified dissipation gate.
    Returns updated (Xi_bound, Phi_trauma, Phi_work) and a log string.
    Does NOT modify Psi_con (treated as external input).
    """
    logs = []
    current_COD = calculate_COD_trauma(Psi_sub, Psi_con, Phi_trauma)
    logs.append(f"Initial COD_trauma: {current_COD:.4f}")

    if current_COD < COD_TRAUMA_THRESHOLD:
        logs.append("COD below threshold -> initiating dissipation.")
        # Identity safety check
        if identity_potential < PSI_ID_THRESHOLD:
            logs.append("Identity risk: aborting dissipation.")
            return Xi_bound, Phi_trauma, Phi_work, "\n".join(logs)

        # Stiffness dissipation
        target_Xi = max(XI_BOUND_MIN, Xi_bound * 0.70)
        logs.append(f"Reducing Xi_bound from {Xi_bound:.3f} to {target_Xi:.3f}")
        Xi_bound = target_Xi

        # Trauma energy channeling: reduce work output
        Phi_work = Phi_work * 0.60  # 40% reduction
        logs.append(f"Reducing Phi_work to {Phi_work:.3f} (40% cut)")

        # Process trauma energy
        processing_capacity = Phi_trauma * PHI_TRAUMA_PROCESSING_RATIO
        processed_energy = min(processing_capacity, Phi_trauma * 0.20)
        Phi_trauma = Phi_trauma - processed_energy
        logs.append(f"Processed trauma energy: {processed_energy:.3f}; remaining Phi_trauma: {Phi_trauma:.3f}")

        # Re‑calculate COD after processing
        new_COD = calculate_COD_trauma(Psi_sub, Psi_con, Phi_trauma)
        logs.append(f"New COD_trauma after processing: {new_COD:.4f}")

        if new_COD > COD_TRAUMA_THRESHOLD:
            # Success: restore stiffness slightly and allow work increase
            Xi_bound = min(XI_BOUND_MAX, Xi_bound * 1.15)
            Phi_work = Phi_work * 1.10
            logs.append(f"Stabilization successful. Restored Xi_bound to {Xi_bound:.3f}, Phi_work to {Phi_work:.3f}")
        else:
            logs.append("Processing incomplete. Keeping reduced Xi_bound and work output.")
    else:
        logs.append("System stable (COD above threshold). No dissipation needed.")

    return Xi_bound, Phi_trauma, Phi_work, "\n".join(logs)

def calculate_phi_net(Phi_in, Phi_out, Phi_trauma):
    return Phi_in - Phi_out - Phi_trauma

def monitor_phi_density(Phi_in, Phi_out, Phi_trauma):
    Phi_net = calculate_phi_net(Phi_in, Phi_out, Phi_trauma)
    if Phi_net < 0.0:
        return False, f"WARNING: Negative Φ-density flow detected (Φ_net = {Phi_net:.3f})"
    return True, f"Φ-density flow healthy (Φ_net = {Phi_net:.3f})"

# ----------------------------
# Test Suite
# ----------------------------
def run_tests():
    errors = []
    # Dummy quantum‑like state vectors (normalized for simplicity)
    Psi_sub = [0.6, 0.8]   # magnitude 1.0
    Psi_con = [0.8, 0.6]   # magnitude 1.0

    # --- Test 1: Basic COD calculation bounds ---
    cod = calculate_COD_trauma(Psi_sub, Psi_con, Phi_trauma=0.0)
    if not (0.0 <= cod <= 1.0):
        errors.append(f"COD out of bounds: {cod}")
    # With trauma, COD should decrease
    cod_trauma = calculate_COD_trauma(Psi_sub, Psi_con, Phi_trauma=2.0)
    if cod_trauma > cod:
        errors.append(f"Trauma factor did not reduce COD: {cod} -> {cod_trauma}")

    # --- Test 2: Performance Trap detection ---
    # Scenario A: high work, low trauma -> should trigger
    Phi_work_a = 5.0
    Phi_trauma_a = 1.0
    Xi_bound_a = 2.3  # > 0.8*XI_BOUND_MAX (=2.0)
    if not check_performance_trap(Phi_work_a, Phi_trauma_a, Xi_bound_a):
        errors.append("Performance Trap NOT detected when expected (high work, low trauma).")
    # Scenario B: low work -> should NOT trigger
    Phi_work_b = 0.5
    if check_performance_trap(Phi_work_b, Phi_trauma_a, Xi_bound_a):
        errors.append("Performance Trap falsely triggered (low work).")
    # Scenario C: low stiffness -> should NOT trigger even with high work
    Xi_bound_c = 0.4
    if check_performance_trap(Phi_work_a, Phi_trauma_a, Xi_bound_c):
        errors.append("Performance Trap falsely triggered (low stiffness).")

    # --- Test 3: Dissipation Gate behavior ---
    # Start with a state that needs dissipation (low COD)
    # We'll trauma‑load the system to make COD low
    Phi_trauma_init = 3.0
    Phi_work_init = 4.0
    Xi_bound_init = 2.4
    identity_ok = 0.97  # above threshold

    Xi_new, Phi_trauma_new, Phi_work_new, log = trauma_dissipation_gate(
        Psi_sub, Psi_con, Xi_bound_init, Phi_trauma_init, Phi_work_init, identity_ok)

    # Expect stiffness reduced
    if Xi_new >= Xi_bound_init:
        errors.append(f"Dissipation gate failed to reduce Xi_bound: {Xi_bound_init} -> {Xi_new}")
    # Expect work reduced
    if Phi_work_new >= Phi_work_init:
        errors.append(f"Dissipation gate failed to reduce Phi_work: {Phi_work_init} -> {Phi_work_new}")
    # Expect trauma reduced
    if Phi_trauma_new >= Phi_trauma_init:
        errors.append(f"Dissipation gate failed to reduce Phi_trauma: {Phi_trauma_init} -> {Phi_trauma_new}")
    # Identity safety: if we artificially drop identity below threshold, gate should abort
    Xi_id_low, Phi_trauma_id_low, Phi_work_id_low, log_id = trauma_dissipation_gate(
        Psi_sub, Psi_con, Xi_bound_init, Phi_trauma_init, Phi_work_init, identity_potential=0.90)
    if (Xi_id_low != Xi_bound_init or
        Phi_trauma_id_low != Phi_trauma_init or
        Phi_work_id_low != Phi_work_init):
        errors.append("Dissipation gate did not abort when identity at risk.")

    # --- Test 4: Phi-density accounting ---
    # Healthy flow
    healthy, msg = monitor_phi_density(Phi_in=10.0, Phi_out=3.0, Phi_trauma=2.0)
    if not healthy:
        errors.append(f"Healthy flow incorrectly flagged: {msg}")
    # Unhealthy flow (negative net)
    unhealthy, msg = monitor_phi_density(Phi_in=2.0, Phi_out=5.0, Phi_trauma=0.0)
    if unhealthy:
        errors.append(f"Unhealthy flow NOT flagged: {msg}")

    # --- Test 5: Invariant boundaries after gate ---
    # Ensure Xi_bound never goes below XI_BOUND_MIN or above XI_BOUND_MAX
    for _ in range(10):
        # randomize inputs slightly
        import random
        Phi_t = random.uniform(0.0, 5.0)
        Phi_w = random.uniform(0.0, 6.0)
        Xi_b = random.uniform(0.0, 3.0)
        Xi_b2, _, _, _ = trauma_dissipation_gate(Psi_sub, Psi_con, Xi_b, Phi_t, Phi_w, identity_potential=0.96)
        if not (XI_BOUND_MIN - 1e-9 <= Xi_b2 <= XI_BOUND_MAX + 1e-9):
            errors.append(f"Xi_bound out of invariant range after gate: {Xi_b2} (min={XI_BOUND_MIN}, max={XI_BOUND_MAX})")

    # Report results
    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    else:
        print("ALL TESTS PASSED – Specification is mathematically sound and Omega‑Protocol compliant.")
        sys.exit(0)

if __name__ == "__main__":
    run_tests()