# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator
----------------------------------
Checks source files for compliance with the three absolute rules:
  1. Covariant mode decomposition: explicit Φ_N and Φ_Δ symbols.
  2. Boundary awareness: presence of Shredding Event horizon constant Λ_shred.
  3. Entropy form: Shannon conditional entropy H(X|Y) used or derived.

If any rule fails, the script exits with non-zero status and prints a diagnostic.
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# ----------------------------------------------------------------------
# Configuration – adjust to your repo layout
# ----------------------------------------------------------------------
SOURCE_GLOBS = ["**/*.cpp", "**/*.hpp", "**/*.cc", "**/*.hh"]  # C++/HPP
REQUIRED_PATTERNS: List[Tuple[str, str]] = [
    (r"\bPhi_N\b", "Newtonian component Φ_N must appear explicitly"),
    (r"\bPhi_Delta\b", "Asymmetry component Φ_Δ must appear explicitly"),
    (r"\bLambda_shred\s*=\s*0\.82\b", "Shredding Event horizon Λ_shred = 0.82 must be defined"),
    (r"H\s*\(\s*[A-Za-z_]\s*\|\s*[A-Za-z_]\s*\)", "Shannon conditional entropy H(X|Y) must be used"),
]

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def find_source_files() -> List[Path]:
    files = []
    for pattern in SOURCE_GLOBS:
        files.extend(Path(".").rglob(pattern))
    return files

def grep_pattern(pattern: str, content: str) -> List[Tuple[int, str]]:
    """Return list of (line_number, line) where pattern matches."""
    matches = []
    for i, line in enumerate(content.splitlines(), start=1):
        if re.search(pattern, line, re.IGNORECASE):
            matches.append((i, line.rstrip()))
    return matches

def validate_file(path: Path) -> List[str]:
    """Return list of error messages for a single file."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [f"Could not read {path}: {e}"]

    errors = []
    for pattern, hint in REQUIRED_PATTERNS:
        if not grep_pattern(pattern, text):
            errors.append(f"{path}:{hint}")
    return errors

def main() -> int:
    all_errors = []
    for src in find_source_files():
        all_errors.extend(validate_file(src))

    if all_errors:
        print("Ω PROTOCOL VIOLATIONS DETECTED:", file=sys.stderr)
        for err in all_errors:
            print("  - " + err, file=sys.stderr)
        print("\nFix the above issues before proceeding.", file=sys.stderr)
        return 1
    else:
        print("✅ All Omega absolute invariants detected.")
        return 0

if __name__ == "__main__":
    sys.exit(main())