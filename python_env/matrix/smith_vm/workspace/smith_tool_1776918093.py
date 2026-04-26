# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# Omega Protocol Invariant Validator – AFDS v3.0 (Engine pleading review)
# =============================================================================
# This script is to be run against the *revised* C++ source file supplied by
# the Engine after addressing the pleading. It checks for the minimal
# structural evidence that the six Omega Physics Rubric invariants are
# present and that empirical audit‑cost measurement, bounded memory, and
# a realistic benchmark are implemented.
#
# Usage:  python3 validate_afds.py /path/to/afds_v3.cpp
#
# The script returns a non‑zero exit code if any invariant check fails,
# signalling a META-FAIL to the Matrix Guardian.
# =============================================================================

import sys
import re
import subprocess
from pathlib import Path

def fail(msg):
    print(f"[META-FAIL] {msg}", file=sys.stderr)
    sys.exit(1)

def warn(msg):
    print(f"[WARN] {msg}", file=sys.stderr)

def info(msg):
    print(f"[INFO] {msg}")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <afds_source.cpp>", file=sys.stderr)
        sys.exit(2)

    src_path = Path(sys.argv[1])
    if not src_path.is_file():
        fail(f"Source file not found: {src_path}")

    src = src_path.read_text(errors="ignore")

    # -----------------------------------------------------------------
    # 1. Covariant modes – explicit split into phi_N and phi_Delta
    # -----------------------------------------------------------------
    phi_n_pattern = re.compile(r"\bphi[_-]?N\b")
    phi_delta_pattern = re.compile(r"\bphi[_-]?Delta\b")
    if not (phi_n_pattern.search(src) and phi_delta_pattern.search(src)):
        fail("Missing explicit covariant mode variables (phi_N, phi_Delta).")

    # -----------------------------------------------------------------
    # 2. ψ‑invariants – usage of psi = ln(phi_n + ε) in gauge term
    # -----------------------------------------------------------------
    psi_pattern = re.compile(r"\bpsi\s*=\s*log\s*\(\s*phi[_-]?n\s*\+\s*[0-9.eE+\-]+\s*\)")
    if not psi_pattern.search(src):
        fail("ψ‑invariant (psi = ln(phi_n + ε)) not found or not used in gauge term.")

    # -----------------------------------------------------------------
    # 3. Stiffness terms – XI_N and XI_Delta derived from time constants
    # -----------------------------------------------------------------
    xi_n_pattern = re.compile(r"\bXI[_-]?N\s*=")
    xi_delta_pattern = re.compile(r"\bXI[_-]?Delta\s*=")
    if not (xi_n_pattern.search(src) and xi_delta_pattern.search(src)):
        fail("Stiffness terms XI_N and/or XI_Delta not defined.")

    # -----------------------------------------------------------------
    # 4. Shannon entropy – conditional entropy H[Ψ | Φ] estimated from window
    # -----------------------------------------------------------------
    shannon_pattern = re.compile(r"\bH\s*\[\s*Psi\s*\|\s*Phi\s*\]\b|conditional.*entropy")
    if not shannon_pattern.search(src):
        fail("Shannon conditional entropy term not present in gauge emergence.")

    # -----------------------------------------------------------------
    # 5. Diagonal Omega‑Action derivation – action integral shown
    # -----------------------------------------------------------------
    action_pattern = re.compile(r'action.*integral|S\s*=\s*∫|∫.*dt', re.IGNORECASE)
    if not action_pattern.search(src):
        fail("No diagonal Omega‑Action derivation (action integral) found.")

    # -----------------------------------------------------------------
    # 6. Empirical audit‑cost measurement – cycle‑count based
    # -----------------------------------------------------------------
    # Look for rdtsc, __builtin_ia32_rdtsc, or perf event usage around trust/
    # forensic/topology updates.
    audit_cycle_pattern = re.compile(
        r'(rdtsc|__builtin_ia32_rdtsc|perf_event_open|clock_gettime\s*\(\s*CLOCK_MONOTONIC_RAW)',
        re.IGNORECASE)
    if not audit_cycle_pattern.search(src):
        fail("Audit‑cost not measured via empirical cycle/performance counters.")

    # -----------------------------------------------------------------
    # 7. Inode‑mapper bootstrap – InitializeRoot called in fuse init
    # -----------------------------------------------------------------
    init_root_pattern = re.compile(r'inode_mapper\.InitializeRoot\s*\(')
    fuse_init_pattern = re.compile(r'\.init\s*=\s*[&]?[a-zA-Z_][a-zA-Z0-9_]*\s*\(', re.IGNORECASE)
    if not (init_root_pattern.search(src) and fuse_init_pattern.search(src)):
        fail("inode_mapper.InitializeRoot not invoked from FUSE init operation.")

    # -----------------------------------------------------------------
    # 8. Bounded memory – LRU or fixed‑size containers for growing sets
    # -----------------------------------------------------------------
    lru_pattern = re.compile(
        r'(boost::circular_buffer|std::list\s*<\s*std::pair|LRU\s*Cache|'
        r'std::unordered_map\s*<[^>]*>\s*[^;]*\;\s*//.*LRU)', re.IGNORECASE)
    if not lru_pattern.search(src):
        fail("No evidence of bounded memory (LRU/fixed‑size) for accessed_paths, log_entries, or unique_paths.")

    # -----------------------------------------------------------------
    # 9. Realistic benchmark – actual syscalls exercised
    # -----------------------------------------------------------------
    bench_pattern = re.compile(
        r'(stat\(|readdir\(|open\(|read\(|close\()', re.IGNORECASE)
    if not bench_pattern.search(src):
        fail("Benchmark suite does not invoke real filesystem syscalls (stat, readdir, open, read, close).")

    # -----------------------------------------------------------------
    # 10. Shredding threshold derived from manifold curvature (dynamic)
    # -----------------------------------------------------------------
    # Look for a computation that sets a threshold variable from phi_N,
    # XI_N, XI_DELTA, and h_imp (or similar), not a plain literal >0.9.
    threshold_pattern = re.compile(
        r'phi[_-]?Delta[_\s]*[>=<!]+\s*[^0-9.]|'   # comparison with expression
        r'threshold\s*=\s*[^;]*'                   # assignment of threshold
        , re.IGNORECASE)
    # We'll accept if threshold is not a plain literal 0.95
    literal_threshold = re.compile(r'0\.95\s*[;}]')
    if literal_threshold.search(src) and not threshold_pattern.search(src):
        fail("Shredding threshold appears as hard‑coded literal 0.95 without derivation.")

    # -----------------------------------------------------------------
    # If we reach here, all invariant checks passed.
    # -----------------------------------------------------------------
    info("All Omega Protocol invariant checks passed.")
    print("RESULT: META-PASS (invariant compliance verified)")
    sys.exit(0)

if __name__ == "__main__":
    main()