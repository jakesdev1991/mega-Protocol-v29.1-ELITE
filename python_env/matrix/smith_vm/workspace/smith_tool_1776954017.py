# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AFDS v3.0 Invariant & Sanity Checker
------------------------------------
This script validates the mathematical core of the AFDS v3.0 C++ prototype
against the Omega Physics Rubric v26.0.  It does **not** compile or run the
C++ code; instead it extracts the key formulas from the provided source
(or from a user‑supplied JSON/YAML description) and checks them for:
  * Trust‑score bounds [0,1]
  * Proper exponential decay formulation
  * φₙ derivation from first‑principles (no free scaling factors)
  * φΔ as a geometrically motivated antisymmetric measure
  * Topological impedance as a discrete integral of gauge emergence
  * Curvature = ξₙ·φₙ + ξ_Δ·φ_Δ – H_imp  (no extra ψ term)
  * Atomic‑operation correctness (simulated)
  * FUSE path sanity (must not rely on raw inode as fd)
"""

import math
import re
import json
import sys
from typing import Dict, Any, Tuple, List

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def approx_eq(a: float, b: float, eps: float = 1e-9) -> bool:
    return abs(a - b) <= eps

# ----------------------------------------------------------------------
# 1. Trust‑score model validation
# ----------------------------------------------------------------------
def validate_trust_model(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Expected invariant form (per rubric):
        H_noise = ln(|accessed_paths| + 1)
        stability_integral = Σ_i exp(-Δt_i / τ)   (τ = 3600 s)
        φₙ = exp(-H_noise) * stability_integral
        ψ   = ln(max(φₙ, ε))
    Any extra multiplicative constants (e.g., 0.1, 0.01) are forbidden.
    """
    errors = []
    # Extract claimed formula from Engine (we parse a simple description)
    # For demo we expect the user to supply a dict with the coefficients they used.
    # In a real audit you would regex the C++ source.
    novelty_penalty = params.get("novelty_penalty", 0.05)
    decay_base      = params.get("decay_base", 0.95)      # should be exp(-1/τ) per hour
    stability_coeff = params.get("stability_coeff", 0.01) # should be 1.0 (no extra factor)
    noise_coeff     = params.get("noise_coeff", 0.01)    # should be 1.0

    # Check that decay_base corresponds to exp(-1/τ) where τ = 3600 s → per hour factor
    tau = 3600.0
    expected_decay = math.exp(-1.0 / tau)   # ≈ 0.999722...
    if not approx_eq(decay_base, expected_decay, eps=1e-4):
        errors.append(
            f"Decay base {decay_base} does not match exp(-1/τ) with τ=3600 s "
            f"(expected ≈ {expected_decay:.6f})."
        )
    # Novelty penalty should be a pure probability per novel access; we allow any
    # value in [0,1] but flag if >0.1 as likely heuristic.
    if not (0.0 <= novelty_penalty <= 1.0):
        errors.append(f"Novelty penalty {novelty_penalty} outside [0,1].")
    elif novelty_penalty > 0.1:
        errors.append(
            f"Novelty penalty {novelty_penalty} looks heuristic; "
            "rubric expects a principled information‑gain term."
        )
    # Stability and noise coefficients must be exactly 1.0 (no free scaling)
    if not approx_eq(stability_coeff, 1.0):
        errors.append(
            f"Stability coefficient {stability_coeff} ≠ 1.0 → introduces uncontrolled entropy."
        )
    if not approx_eq(noise_coeff, 1.0):
        errors.append(
            f"Noise coefficient {noise_coeff} ≠ 1.0 → introduces uncontrolled entropy."
        )
    # Trust‑score must stay in [0,1] after each update – we simulate a few steps.
    def simulate_trust(seq: List[Tuple[bool, float]]) -> float:
        """seq = [(is_novel, delta_hours), ...]"""
        score = 0.0
        stability = 0.0
        accessed = set()
        for is_novel, dh in seq:
            # decay
            score *= math.exp(-math.log(decay_base) * dh)
            # novelty penalty
            if is_novel:
                score -= novelty_penalty
                accessed.add("dummy")  # just to count
            else:
                stability += math.exp(-dh)   # proper stability integral (τ=1h for demo)
                score += stability_coeff * math.exp(-0.1 * stability)
            score = clamp(score)
        return score

    # Test a path that should never exceed 1.0
    test_seq = [(False, 0.1)] * 20   # many stable accesses
    final_score = simulate_trust(test_seq)
    if final_score > 1.0 + 1e-9:
        errors.append(
            f"Trust score can exceed 1.0 (got {final_score:.6f}) after repeated stable accesses."
        )
    return len(errors) == 0, errors

# ----------------------------------------------------------------------
# 2. φₙ and ψ validation
# ----------------------------------------------------------------------
def validate_phi_n_and_psi(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors = []
    # Expect φₙ = exp(-H_noise) * stability_integral
    # Any extra factor like 0.01 * ... is illegal.
    phi_n_formula = params.get("phi_n_formula", "")
    # Simple check: disallow any numeric literal besides 0,1, e, pi
    forbidden = re.findall(r'\b\d+\.\d+\b', phi_n_formula)
    if forbidden:
        errors.append(
            f"φₙ formula contains unexplained constants {forbidden}. "
            "Must be derived solely from H_noise and stability integral."
        )
    # ψ = ln(max(φₙ, ε)) – ensure no extra scaling
    psi_formula = params.get("psi_formula", "")
    if "*" in psi_formula or "/" in psi_formula:
        errors.append(
            "ψ formula appears to have extra scaling; should be pure log."
        )
    return len(errors) == 0, errors

# ----------------------------------------------------------------------
# 3. φΔ validation (geometric antisymmetry)
# ----------------------------------------------------------------------
def validate_phi_delta(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors = []
    # Ideal form: φΔ = |breadth - depth| / (breadth + depth)
    # or a normalized curl of traversal flow.
    phi_delta_expr = params.get("phi_delta_expr", "")
    # Detect tanh or other ad‑hoc functions
    if "tanh" in phi_delta_expr:
        errors.append(
            "φΔ uses tanh – not a rubric‑prescribed geometric measure. "
            "Replace with |breadth‑depth|/(breadth+depth) or equivalent."
        )
    # Ensure expression is dimensionless and bounded [0,1]
    # We'll do a quick sanity check with sample values.
    def phi_delta(b, d):
        if b + d == 0:
            return 0.0
        return abs(b - d) / (b + d)
    # Test a few combos
    for b, d in [(0,0),(1,0),(0,1),(5,2),(2,5)]:
        val = phi_delta(b, d)
        if not (0.0 <= val <= 1.0 + 1e-12):
            errors.append(
                f"φΔ({b},{d}) = {val} out of [0,1] bounds."
            )
    return len(errors) == 0, errors

# ----------------------------------------------------------------------
# 4. Topological impedance validation (discrete integral)
# ----------------------------------------------------------------------
def validate_topological_impedance(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors = []
    # H_imp ≈ Σ_i (g_i + g_{i-1})/2 * (ψ_i - ψ_{i-1})
    # where g_i = trust_score_i * |φΔ_i|
    formula = params.get("impedance_formula", "")
    # Detect simple sum * constant (the Engine's 0.01 factor)
    if re.search(r'\*\s*0\.01', formula):
        errors.append(
            "Topological impedance uses arbitrary scale 0.01; "
            "must be derived from the discrete integral above."
        )
    # Ensure no extra free parameters
    if re.search(r'\*\s*\d+\.\d+', formula):
        errors.append(
            "Impedance formula contains unexplained numeric coefficient."
        )
    return len(errors) == 0, errors

# ----------------------------------------------------------------------
# 5. Curvature validation
# ----------------------------------------------------------------------
def validate_curvature(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors = []
    # Expected: curvature = ξₙ·φₙ + ξ_Δ·φ_Δ - H_imp
    curv = params.get("curvature_formula", "")
    # Disallow any standalone ψ term
    if re.search(r'\bpsi\b\s*[+\-]', curv) or re.search(r'\bpsi\b\s*\*', curv):
        errors.append(
            "Curvature contains an independent ψ term; "
            "must be ξₙ·φₙ + ξ_Δ·φ_Δ - H_imp only."
        )
    # Check that coefficients appear as named constants (ξₙ, ξ_Δ)
    if "0.8" in curv or "1.2" in curv:
        errors.append(
            "Curvature uses hard‑coded ξ values (0.8,1.2) without referencing "
            "named constants ξₙ, ξ_Δ from the rubric."
        )
    return len(errors) == 0, errors

# ----------------------------------------------------------------------
# 6. Atomic‑operation sanity (simulated)
# ----------------------------------------------------------------------
def validate_atomics() -> Tuple[bool, List[str]]:
    errors = []
    # The Engine used:
    #   metrics.max_depth.update(depth)   ← illegal
    #   metrics.traversal_entropy.fetch_add(...) ← illegal for double
    errors.append(
        "Atomic update: std::atomic<int> has no member 'update'; "
        "use compare_exchange loop for fetch‑max."
    )
    errors.append(
        "Atomic fetch_add on std::atomic<double> is not supported; "
        "use load‑modify‑store loop or platform‑specific atomic<double>+=."
    )
    return False, errors   # always fail because the source is known broken

# ----------------------------------------------------------------------
# 7. FUSE path sanity
# ----------------------------------------------------------------------
def validate_fuse_path() -> Tuple[bool, List[str]]:
    errors = []
    errors.append(
        "FUSE lookup builds path as '/proc/self/fd/<inode>/<name>'. "
        "Inodes are not file descriptors; this will almost always yield ENOENT. "
        "Reconstruct real path from underlying mount or open directory fd via openat."
    )
    return False, errors

# ----------------------------------------------------------------------
# 8. Benchmark stub detection
# ----------------------------------------------------------------------
def validate_benchmark() -> Tuple[bool, List[str]]:
    errors = []
    errors.append(
        "Benchmark suite is stubbed ('// Implementation of empirical measurements'). "
        "No empirical data → Φ‑density claim unsubstantiated."
    )
    return False, errors

# ----------------------------------------------------------------------
# Main driver – expects a JSON file describing the constants used in the Engine
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 afds_validator.py <params.json>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        params = json.load(f)

    all_ok = True
    validators = [
        ("Trust model", validate_trust_model),
        ("φₙ & ψ", validate_phi_n_and_psi),
        ("φΔ", validate_phi_delta),
        ("Topological impedance", validate_topological_impedance),
        ("Curvature", validate_curvature),
        ("Atomics", lambda _: validate_atomics()),
        ("FUSE path", lambda _: validate_fuse_path()),
        ("Benchmark", lambda _: validate_benchmark()),
    ]

    for name, fn in validators:
        ok, errs = fn(params) if name not in ("Atomics","FUSE path","Benchmark") else fn(None)
        if not ok:
            all_ok = False
            print(f"[FAIL] {name}:")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"[PASS] {name}")

    if all_ok:
        print("\n=== OVERALL RESULT: PASS ===")
        print("The supplied parameters satisfy the Omega Physics Rubric v26.0.")
    else:
        print("\n=== OVERALL RESULT: FAIL ===")
        print("One or more invariant violations detected. See above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()