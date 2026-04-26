# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------
# Ω‑Protocol invariant helpers
# ------------------------------
def normalize(vec):
    """Return a normalized copy of a complex vector."""
    norm = np.linalg.norm(vec)
    if norm == 0:
        raise ValueError("Zero‑norm vector cannot be normalized.")
    return vec / norm

def compute_cod(psi_policy, psi_exec):
    """Chain Overlap Density = |<policy|exec>|^2 / (||policy||^2 ||exec||^2)"""
    # Assuming inputs are already normalized
    overlap = np.vdot(psi_policy, psi_exec)  # <policy|exec>
    cod = np.abs(overlap) ** 2
    return float(cod)  # should be in [0,1]

def stiffness_from_cod(cod, xi_c=0.3):
    """Proxy for Informational Stiffness – higher COD → higher stiffness."""
    return cod  # monotonic mapping; threshold applied externally

def rdi_damping(t, gamma0=0.2, tau=2.0):
    """Time‑dependent damping term Γ_RDI(t) ≥ 0."""
    return gamma0 * np.exp(-t / tau)

def apply_rdi_step(psi_exec, gamma, dt=0.1):
    """
    Non‑unitary evolution step:  |ψ'> = (1 - i γ dt) |ψ>
    followed by re‑normalization to preserve Φₙ (norm = 1).
    This mimics the effective Hamiltonian  H_eff = H_org - iγ.
    """
    # non‑unitary kick
    psi_kick = (1 - 1j * gamma * dt) * psi_exec
    # re‑normalize to keep Φₙ = 1 (Ω‑Protocol invariance)
    return normalize(psi_kick)

# ------------------------------
# Validation scenario
# ------------------------------
def validate_omega_protocol(
    n_steps=50,          # simulate ~5 weeks if dt=0.1 week per step
    dt=0.1,
    xi_c=0.3,
    cod_decohere_thresh=0.4,
    phi_dip_allowed=-0.05,   # -5 % dip allowed
    phi_dip_max_weeks=4,     # dip may last at most 4 weeks
    gamma0=0.2,
    tau=2.0,
):
    """
    Runs a synthetic bureaucracy simulation and asserts that all
    Ω‑Protocol invariants hold. Raises AssertionError on violation.
    """
    # 1. Initialise random policy and execution states (normalized)
    np.random.seed(42)  # reproducibility for audit
    psi_policy = normalize(np.random.randn(10) + 1j * np.random.randn(10))
    psi_exec   = normalize(np.random.randn(10) + 1j * np.random.randn(10))

    # Track Φ‑density (proxy: COD) over time
    cod_history = []
    phi_density_history = []  # we treat Φ ∝ COD for this audit
    gamma_history = []
    stiffness_history = []
    decoherence_flags = []

    # For transient dip accounting
    dip_start = None
    dip_duration = 0

    for step in range(n_steps):
        t = step * dt

        # ---- Compute COD & related quantities ----
        cod = compute_cod(psi_policy, psi_exec)
        cod_history.append(cod)

        # Φ‑density proxy (could be any monotonic function of COD)
        phi = cod  # assume Φ_density = COD for simplicity
        phi_density_history.append(phi)

        # ---- Informational Stiffness check ----
        xi = stiffness_from_cod(cod, xi_c=xi_c)
        stiffness_history.append(xi)
        assert xi >= xi_c, (
            f"Ω‑Protocol violation: Informational Stiffness ξ={xi:.3f} "
            f"fell below critical ξ_c={xi_c:.3f} at step {step} (t={t:.2f})."
        )

        # ---- COD bounds & decoherence flag ----
        assert 0.0 <= cod <= 1.0, (
            f"Ω‑Protocol violation: COD={cod:.3f} out of [0,1] at step {step}."
        )
        decoherence = cod < cod_decohere_thresh
        decoherence_flags.append(decoherence)

        # ---- RDI damping term (must be non‑negative) ----
        gamma = rdi_damping(t, gamma0=gamma0, tau=tau)
        gamma_history.append(gamma)
        assert gamma >= 0.0, (
            f"Ω‑Protocol violation: Γ_RDI(t)={gamma:.3f} < 0 at step {step}."
        )

        # ---- Apply RDI step to execution state ----
        psi_exec = apply_rdi_step(psi_exec, gamma, dt=dt)
        # Policy state remains unchanged (conscious layer static in this toy model)

        # ---- Φ‑density transient dip accounting ----
        # Baseline Φ is the initial COD (could also be a running average)
        baseline_phi = phi_density_history[0]
        delta_phi = phi - baseline_phi

        if delta_phi < phi_dip_allowed:  # entering a dip
            if dip_start is None:
                dip_start = step
            dip_duration = (step - dip_start + 1) * dt
            # Ensure dip does not exceed allowed duration
            assert dip_duration <= phi_dip_max_weeks, (
                f"Ω‑Protocol violation: Φ‑density dip lasted {dip_duration:.2f} weeks "
                f"(>{phi_dip_max_weeks} weeks) starting at step {dip_start}."
            )
        else:
            # Reset dip tracking when we recover
            dip_start = None
            dip_duration = 0

    # ---- Final Φ‑density net gain check ----
    final_phi = phi_density_history[-1]
    initial_phi = phi_density_history[0]
    net_gain = final_phi - initial_phi
    assert net_gain >= 0.0, (
        f"Ω‑Protocol violation: Net Φ‑density change = {net_gain:.3f} < 0 "
        f"(initial={initial_phi:.3f}, final={final_phi:.3f})."
    )

    # Optional: report summary
    print("Ω‑Protocol validation PASSED.")
    print(f"  Steps simulated          : {n_steps}")
    print(f"  Final COD                : {cod_history[-1]:.3f}")
    print(f"  Minimum COD observed     : {min(cod_history):.3f}")
    print(f"  Decoherence episodes     : {sum(decoherence_flags)}")
    print(f"  Net Φ‑density gain       : {net_gain*100:.1f}%")
    print(f"  Max Γ_RDI(t) used        : {max(gamma_history):.3f}")

    return {
        "cod_history": cod_history,
        "phi_history": phi_density_history,
        "gamma_history": gamma_history,
        "stiffness_history": stiffness_history,
        "decoherence_flags": decoherence_flags,
    }

# ------------------------------
# Run the validation (will raise AssertionError if any invariant broken)
# ------------------------------
if __name__ == "__main__":
    try:
        result = validate_omega_protocol()
    except AssertionError as e:
        print("Ω‑Protocol AUDIT FAILED:")
        print(e)
        raise  # re‑raise to halt execution in the VM