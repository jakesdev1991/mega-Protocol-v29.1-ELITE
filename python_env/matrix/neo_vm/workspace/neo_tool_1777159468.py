# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- UIPO v65.0 dynamics (deadlock regime) ---
def simulate_uipo(steps=1000, dt=1.0, inject_at=500):
    # Initial trauma state: high stiffness, low trust, high uncertainty
    Xi_perf = 0.98      # Performance stiffness
    Z_trust = 0.25      # Self‑trust impedance
    Z_env   = 0.90      # External demand
    H_super = 0.70      # Superposition entropy (uncertainty)

    gamma = 0.005       # Adiabatic decay rate (slow)
    alpha = 0.001       # Trust build‑up rate (even slower)
    kappa = lambda *args: 0.5  # Penalty coefficients (arbitrary)
    lam   = lambda *args: 0.5
    Lambda = lambda *args: 0.5

    history = []

    for t in range(steps):
        # Approximate fidelity as alignment between stiffness & trust
        fidelity = max(0.0, 1.0 - (Xi_perf - Z_trust)**2)

        # COD as defined in UIPO (product of exponentials)
        cod = fidelity * np.exp(-kappa() * Xi_perf) * np.exp(-lam() * Z_env) * np.exp(-Lambda() * H_super)

        # Silence Protocol: if COD < 0.85, *no* performance demand → trust builds slowly
        silence = cod < 0.85
        if silence:
            # No external demand, but also no feedback → trust creeps upward
            Z_trust += alpha * dt   # minuscule gain
            H_super -= 0.0005 * dt  # uncertainty slowly falls
        else:
            # Performance demand resumes → trust erodes slightly
            Z_trust -= 0.5 * alpha * dt
            H_super += 0.001 * dt

        # Adiabatic relaxation of stiffness toward current trust (too slow)
        Xi_perf += -gamma * (Xi_perf - Z_trust) * dt

        # Clamp values
        Xi_perf = np.clip(Xi_perf, 0.1, 1.0)
        Z_trust = np.clip(Z_trust, 0.1, 1.0)
        H_super = np.clip(H_super, 0.1, 1.0)

        # --- CHAOS INJECTION (break the invariants) ---
        if t == inject_at:
            # Violate Invariant 4 (stiffness‑trust match) & Invariant 1 (COD gate)
            # Artificially *shatter* the stiffness lock and *spike* trust
            Xi_perf = 0.50      # Instant drop (non‑adiabatic)
            Z_trust += 0.40     # Shock‑boost trust (external validation)
            H_super = 0.20      # Force uncertainty down (reality check)

        history.append((t, cod, silence, Xi_perf, Z_trust))

    return history

# Run simulation
hist = simulate_uipo(steps=800, inject_at=400)

# Print key snapshots
for t, cod, silence, xi, zt in hist[::100]:
    print(f"t={t:3d} | COD={cod:.3f} | silence={silence} | Ξ_perf={xi:.3f} | Z_trust={zt:.3f}")

# Show the deadlock before injection and the jump after
pre_inj = hist[350]
post_inj = hist[450]
print("\n--- DEADLOCK & UNLOCK ---")
print(f"Pre‑injection (t=350): COD={pre_inj[1]:.3f}, silence={pre_inj[2]}")
print(f"Post‑injection (t=450): COD={post_inj[1]:.3f}, silence={post_inj[2]}")