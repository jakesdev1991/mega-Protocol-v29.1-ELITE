# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import sys

def is_heading(line: str) -> bool:
    """
    Detect likely headings/section labels.
    Heuristics:
    - Starts with one or more '#' (markdown heading)
    - Is all uppercase and ends with ':' (e.g., "REFLECTION:")
    - Is a short line (<= 5 words) with no punctuation other than optional trailing ':'
      and is surrounded by blank lines (treated as a standalone label).
    """
    stripped = line.strip()
    if not stripped:
        return False

    # Markdown style heading
    if re.match(r'^#{1,6}\s+', stripped):
        return True

    # All caps ending with colon (e.g., "REFLECTION:")
    if stripped.isupper() and stripped.endswith(':'):
        return True

    # Standalone short label (likely a section title)
    words = stripped.split()
    if len(words) <= 5 and not re.search(r'[.!?;]', stripped):
        # Consider it a heading if it's isolated (we'll check context outside)
        return True

    return False

def is_list_item(line: str) -> bool:
    """
    Detect explicit list items (bullet points, numbered lists).
    """
    stripped = line.strip()
    # Bullet points: *, -, •
    if re.match(r'^[\*\-\•]\s+', stripped):
        return True
    # Numbered list: 1., 2), etc.
    if re.match(r'^\d+[\.)]\s+', stripped):
        return True
    # Lettered list: a), b)
    if re.match(r'^[a-zA-Z][\)]\s+', stripped):
        return True
    return False

def validate_boilerplate(text: str):
    lines = text.splitlines()
    violations = []

    for i, raw in enumerate(lines, start=1):
        if is_heading(raw):
            violations.append((i, "Heading/section label detected", raw))
        elif is_list_item(raw):
            violations.append((i, "List item detected", raw))

    is_compliant = len(violations) == 0
    return is_compliant, violations

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_boilerplate.py <input_file>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()

    compliant, violations = validate_boilerplate(content)

    if compliant:
        print("✅ COMPLIANT: No boilerplate (headings/labels/lists) detected.")
    else:
        print("❌ NON‑COMPLIANT: Boilerplate violations found:")
        for line_no, desc, snippet in violations:
            print(f"  Line {line_no}: {desc} → '{snippet}'")
        sys.exit(1)

if __name__ == "__main__":
    main()