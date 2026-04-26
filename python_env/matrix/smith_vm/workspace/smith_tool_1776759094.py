# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import re
import sys

def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def check_boilerplate(text: str) -> list:
    """Return list of violations."""
    violations = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        # markdown headings
        if re.match(r"^\s*#{1,6}\s", line):
            violations.append(f"Line {i}: Markdown heading detected → '{line.strip()}'")
        # list-like items (numbers, bullets) – rubric forbids explicit lists
        if re.match(r"^\s*[\d\-\*\+\.]\s+", line):
            violations.append(f"Line {i}: List‑like line detected → '{line.strip()}'")
    return violations

def check_entropy_observable(text: str) -> list:
    """Return list of missing entropy‑observable issues."""
    issues = []
    # Look for Shannon‑entropy keywords
    entropy_pat = re.compile(r'\b(entropy|Shannon|S_embed|-\s*\\sum|\blog\b|p_i)\b', re.I)
    if not entropy_pat.search(text):
        issues.append("No Shannon‑entropy terminology found.")
    else:
        # Verify it is tied to the Action/state/cost
        context_pat = re.compile(
            r'(Action|S\[|state\s*\[|x\[|cost\s*\[|J_\mu|\mathcal{A}_\mu)', re.I)
        # Grab a window around each entropy keyword and see if any context appears
        for m in entropy_pat.finditer(text):
            start, end = m.span()
            window = text[max(0, start-120):end+120]
            if not context_pat.search(window):
                issues.append(
                    f"Entropy term '{m.group()}' appears but is not clearly coupled to Action/state/cost "
                    f"(context window: ...{window.strip()}...)"
                )
                break
    return issues

def check_invariants(text: str) -> list:
    """Ensure ξ_N, ξ_Δ, ψ are defined somewhere."""
    required = [r'\\xi_N', r'\\xi_\Delta', r'\\psi']
    missing = []
    for pat in required:
        if not re.search(pat, text):
            missing.append(pat.strip('\\'))
    return [f"Missing invariant: {m}" for m in missing]

def check_dimensional_hint(text: str) -> list:
    """Very light check for dimensional consistency hints."""
    hints = []
    if re.search(r'\bdimensionless\b|\bħ=1\b|\bnatural units\b', text, re.I):
        hints.append("Dimensional consistency hint found.")
    else:
        hints.append("No explicit dimensional‑consistency hint (consider adding a note).")
    return hints

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_ncsm.py <path-to-proposal.txt>")
        sys.exit(1)

    text = load_text(sys.argv[1])

    print("=== Boilerplate Check ===")
    for v in check_boilerplate(text):
        print("❌", v)
    if not check_boilerplate(text):
        print("✅ No boilerplate detected.")

    print("\n=== Entropy Observable Check ===")
    for e in check_entropy_observable(text):
        print("❌", e)
    if not check_entropy_observable(text):
        print("✅ Entropy observable properly coupled.")

    print("\n=== Invariant Presence Check ===")
    for i in check_invariants(text):
        print("❌", i)
    if not check_invariants(text):
        print("✅ All required invariants (ξ_N, ξ_Δ, ψ) present.")

    print("\n=== Dimensional Consistency Hint ===")
    for d in check_dimensional_hint(text):
        print("ℹ️", d)

    # Overall verdict
    failures = (
        len(check_boilerplate(text)) +
        len(check_entropy_observable(text)) +
        len(check_invariants(text))
    )
    if failures == 0:
        print("\n🟢 OVERALL: PASS – proposal satisfies all checked rubric items.")
        sys.exit(0)
    else:
        print(f"\n🔴 OVERALL: FAIL – {failures} issue(s) detected. Fix before submission.")
        sys.exit(1)

if __name__ == "__main__":
    main()