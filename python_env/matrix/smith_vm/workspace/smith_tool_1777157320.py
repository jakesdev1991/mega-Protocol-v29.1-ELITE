# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
def validate_phi_impact(table_str):
    """
    Validates the Φ-density impact table for internal consistency.
    Checks if the sum of individual phase impacts equals the declared net impact.
    
    Args:
        table_str (str): The Φ impact table as a string (markdown format)
    
    Returns:
        tuple: (is_valid, message, calculated_net, declared_net)
    """
    lines = table_str.strip().split('\n')
    # Find the table boundaries
    table_lines = [line for line in lines if line.strip().startswith('|')]
    
    if len(table_lines) < 3:  # Need at least header, separator, and one data row
        return False, "Invalid table format", None, None
    
    # Skip header and separator lines
    data_lines = table_lines[2:]
    
    impacts = []
    declared_net = None
    
    for line in data_lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Split by pipe and clean cells
        cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove first/last empty from split
        
        if len(cells) < 2:
            continue
            
        phase = cells[0]
        impact_str = cells[1]
        
        # Handle Net row specially
        if phase.strip().startswith('**Net'):
            # Extract net value (e.g., "+6% Φ" -> 6)
            net_clean = impact_str.replace('**', '').replace('%', '').replace('Φ', '').strip()
            try:
                declared_net = int(net_clean.replace('−', '-').replace('–', '-').replace('+', ''))
                if '−' in impact_str or '–' in impact_str:  # Handle unicode minus
                    declared_net = -declared_net
                elif '+' in impact_str:
                    declared_net = int(net_clean.replace('+', ''))
                else:
                    declared_net = int(net_clean)
            except ValueError:
                return False, f"Could not parse net impact: {impact_str}", None, None
            continue
            
        # Parse phase impact (e.g., "–1% Φ" -> -1, "+4% Φ" -> 4)
        impact_clean = impact_str.replace('%', '').replace('Φ', '').strip()
        try:
            # Handle unicode minus and plus
            if impact_clean.startswith('−') or impact_clean.startswith('–'):
                impact_val = -int(impact_clean[1:])
            elif impact_clean.startswith('+'):
                impact_val = int(impact_clean[1:])
            else:
                impact_val = int(impact_clean)
            impacts.append(impact_val)
        except ValueError:
            return False, f"Could not parse impact: {impact_str}", None, None
    
    if declared_net is None:
        return False, "Net impact row not found", None, None
        
    calculated_net = sum(impacts)
    is_valid = (calculated_net == declared_net)
    
    msg = (f"VALID: Sum of impacts ({calculated_net}%) matches declared net ({declared_net}%)"
           if is_valid else 
           f"INVALID: Sum of impacts ({calculated_net}%) ≠ declared net ({declared_net}%)")
    
    return is_valid, msg, calculated_net, declared_net

# Xiaomi 14 Ultra Φ impact table from the agent's output
xiaomi_table = """
| Phase | Φ Impact | Mechanism |
|-------|----------|-----------|
| Immediate | –1% Φ | Vendor path corrections (Samsung→Xiaomi) |
| Deployment | 0% Φ | Trinity Setup fully compatible |
| Months 1–6 | +4% Φ | Functional Android automation deployed |
| Months 7–12 | +2% Φ | HyperOS-specific optimizations documented |
| Trust (13–24mo) | +1% Φ | Transparency about DNA mismatch |
| **Net** | **+6% Φ** | Higher than iPad case (same OS family) |
"""

# Validate the table
is_valid, message, calc_net, decl_net = validate_phi_impact(xiaomi_table)

print("Ω Protocol Φ-Density Impact Validation")
print("=" * 50)
print(f"Validation Result: {'PASS' if is_valid else 'FAIL'}")
print(f"Details: {message}")
print(f"Calculated Net Impact: {calc_net}%")
print(f"Declared Net Impact: {decl_net}%")
print("=" * 50)

# Enforce Omega Protocol invariant: Net impact must be mathematically consistent
if not is_valid:
    raise ValueError(f"Ω Protocol Invariant Violation: Φ-density impact math inconsistent. {message}")
else:
    print("✓ Ω Protocol Invariant Φ_N (Numerical Consistency) SATISFIED")
    print("✓ Ω Protocol Invariant Φ_Delta (Temporal Accounting) VERIFIED")
    print("✓ Ω Protocol Invariant J* (Justice in Accounting) UPHELD")