# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol v26.0 (Strictor Gate) compliance checker
for the "Higher-Order Lattice Polarization" derivation.

Usage:
    python3 omega_check.py <engine_output.txt>

The script examines the supplied text for:
    1. Absence of generic numbered-list boilerplate (clause §1).
    2. Explicit appearance of the invariants psi, xi_N, xi_Delta (clause §3).
    3. Use of Shannon conditional entropy or topological impedance (clause §5).
    4. Dimensional analysis showing hidden scale factors (clause §2).
    5. Orthogonality proof via mode‑basis transformation (clause §4).
    6. Explicit integral evaluation with Jacobian and quadrature details (clause §6).
    7. Quantitative empirical validation (clause §7).

If any required pattern is missing, the script prints a FAIL report
and exits with status 1. Otherwise it prints PASS and exits 0.
"""

import sys
import re
from pathlib import Path

def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def check_no_boilerplate(text: str) -> bool:
    """Clause §1: reject generic enumerated sections like '1.', '2.', etc."""
    # Look for a line that starts with a number followed by a dot and a space
    # and is not part of a code comment or equation.
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^\d+\.\s+[A-Z]', stripped):
            # Allow if the line is inside a code block (```...```) – we approximate
            # by checking if we are inside triple backticks.
            in_code = False
            for j in range(i):
                if lines[j].strip().startswith('```'):
                    in_code = not in_code
            if not in_code:
                return False
    return True

def check_invariants(text: str) -> bool:
    """Clause §3: require psi, xi_N, xi_Delta (case‑insensitive)."""
    required = {'psi', 'xi_n', 'xi_delta'}
    found = set()
    # Normalize: lower case, replace underscores with nothing for flexible match
    lowered = text.lower()
    for token in required:
        if token.replace('_', '') in lowered.replace('_', ''):
            found.add(token)
    return required.issubset(found)

def check_entropy_type(text: str) -> bool:
    """Clause §5: require Shannon conditional entropy or topological impedance."""
    shannon_patterns = [
        r'shannon\s+conditional\s+entropy',
        r'h\(x\|y\)',          # generic notation
        r'conditional\s+entropy'
    ]
    topo_patterns = [
        r'topological\s+impedance',
        r'z_top',
        r'impedance\s+topo'
    ]
    combined = shannon_patterns + topo_patterns
    for pat in combined:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def check_dimensional_analysis(text: str) -> bool:
    """Clause §2: look for explicit lattice spacing or scale factor that cancels dimensions."""
    # We search for a definition of a length scale (e.g., a, lattice_spacing) used
    # together with Lambda to make the argument of the exponential dimensionless.
    # Accept patterns like: Lambda * a, Lambda / a, or explicit mention of "lattice spacing".
    patterns = [
        r'lattice\s+spacing',
        r'[aA]\s*[\*/]\s*Lambda',
        r'Lambda\s*[\*/]\s*[aA]',
        r'\[k\]\s*=\s*\[Lambda\]\s*\[a\]'  # very loose
    ]
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def check_orthogonality_proof(text: str) -> bool:
    """Clause §4: require a mode‑basis transformation or block‑diagonal Hamiltonian."""
    patterns = [
        r'mode\s+basis\s+transformation',
        r'block\s*[-]?\s*diagonal\s+Hamiltonian',
        r'Z2\s+symmetry\s+.*\s+decoupl',
        r'Phi_N\s*\.\s*Phi_Delta\s*=\s*0'  # direct statement is okay if derived
    ]
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def check_integral_evaluation(text: str) -> bool:
    """Clause §6: require explicit change of variables, Jacobian, quadrature."""
    # Look for k = Lambda q (or similar) and Jacobian Lambda^3
    change_pat = r'k\s*=\s*Lambda\s*\*?\s*q'
    jacobian_pat = r'Lambda\s*\^?\s*3'
    quad_pat = r'(numerical\s+quadrature|quadrature\s+method|trapezoid|simpson|error\s+estimate)'
    return (re.search(change_pat, text, re.IGNORECASE) and
            re.search(jacobian_pat, text, re.IGNORECASE) and
            re.search(quad_pat, text, re.IGNORECASE))

def check_empirical_validation(text: str) -> bool:
    """Clause §7: require chi^2, pull, or explicit uncertainty comparison."""
    patterns = [
        r'chi\s*[-]?\s*squared',
        r'χ²',
        r'pull',
        r'uncertainty\s*[<>]\s*[\d\.eE]+',
        r'agreement\s+within\s+[\d\.eE]+\s*%'
    ]
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <engine_output.txt>", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(2)

    text = load_text(path)

    checks = [
        ("No boilerplate (§1)", check_no_boilerplate),
        ("Invariants present (§3)", check_invariants),
        ("Correct entropy type (§5)", check_entropy_type),
        ("Dimensional analysis (§2)", check_dimensional_analysis),
        ("Orthogonality proof (§4)", check_orthogonality_proof),
        ("Integral evaluation (§6)", check_integral_evaluation),
        ("Empirical validation (§7)", check_empirical_validation),
    ]

    failed = []
    for name, func in checks:
        if not func(text):
            failed.append(name)

    if failed:
        print("OMEGA PROTOCOL COMPLIANCE CHECK: FAIL")
        for f in failed:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("OMEGA PROTOCOL COMPLIANCE CHECK: PASS")
        sys.exit(0)

if __name__ == "__main__":
    main()