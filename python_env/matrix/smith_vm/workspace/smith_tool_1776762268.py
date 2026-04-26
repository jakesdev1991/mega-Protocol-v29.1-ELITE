# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re

class Violation(Exception):
    """Raised when boilerplate is detected."""
    pass

def validate_no_boilerplate(text: str) -> None:
    """
    Checks text for patterns that violate the NO BOILERPLATE pillar.
    Raises Violation if any pattern is found.
    """
    # Patterns indicating explicit numbering or step labels
    step_pattern = re.compile(r'\*\*Step\s+\d+[^\n]*\*\*', re.IGNORECASE)
    # Bold headings (anything wrapped in ** that is not just emphasis)
    bold_heading_pattern = re.compile(r'\*\*[^*\n]{3,}\*\*')
    # Bullet points or enumerated lists at line start
    list_pattern = re.compile(r'^\s*[-*]\s+|\s*\d+\.\s+', re.MULTILINE)
    # Section‑like headings that are all caps or title case followed by a newline
    heading_pattern = re.compile(r'^[A-Z][A-Z\s]{2,}\n', re.MULTILINE)

    violations = []
    if step_pattern.search(text):
        violations.append("Numbered step labels detected.")
    if bold_heading_pattern.search(text):
        violations.append("Bold headings detected.")
    if list_pattern.search(text):
        violations.append("Bullet‑point or enumerated list detected.")
    if heading_pattern.search(text):
        violations.append("Section‑like heading detected.")

    if violations:
        raise Violation("Boilerplate violation: " + " ".join(violations))
    # If we reach here, the text passes the NO BOILERPLATE check.
    return True

# Example usage:
if __name__ == "__main__":
    sample_text = """Put the meta‑scrutiny text here."""
    try:
        validate_no_boilerplate(sample_text)
        print("COMPLIANT: No boilerplate detected.")
    except Violation as e:
        print(f"NON‑COMPLIANT: {e}")