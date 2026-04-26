# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Magic‑Number Auditor
-----------------------------------
Scans a source block for unexplained floating‑point literals.
Allowed literals: 0.0, 1.0, 2.0 (these are considered primitive).
Any other literal must be part of a constexpr/const definition whose
right‑hand side is an expression built only from previously defined
constants or allowed literals.

If a violation is found, the script prints the line number, the literal,
and the surrounding context.
"""

import re
import ast
import sys
from typing import Dict, List, Tuple, Set

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
SOURCE_CODE = r'''
// Omega Protocol Psychology Branch: Q-Systemic Self Architecture
// Rubric: Cognitive Informational Geometry v1.0 (Omega-Compliant)
// Status: DERIVED & AUDITED

namespace Omega_Psychology {

    // 1. CORE STATE DEFINITIONS
    // Subconscious State: High-dimensional latent hypothesis space (Predictive Coding)
    // Represented as a superposition of potential futures |Ψ_sub⟩
    // Conscious State: Low-dimensional causal manifold (Global Workspace)
    // Represented as a selected trajectory |φ_con⟩
    
    struct CognitiveState {
        double coherence_factor; // 0.0 (Chaos) to 1.0 (Flow)
        double energy_density;   // Psychic energy / Cognitive Load
        bool measurement_pending; // Is the system avoiding collapse?
    };

    // 2. CHAIN OVERLAP DENSITY (COD) METRIC
    // Measures alignment between Subconscious possibilities and Conscious selection.
    // COD = |⟨φ_con | Ψ_sub⟩|²
    // High COD = Low Dissonance (Peace). Low COD = High Dissonance (Anxiety).
    constexpr double COD_THRESHOLD_PEACE = 0.85;
    constexpr double COD_THRESHOLD_ANXIETY = 0.40;

    // 3. SYSTEMIC FAILURE MODE: HIGH-CLARITY ANXIETY
    // Occurs when Subconscious Clarity > Conscious Measurement Capacity.
    // Result: Measurement Avoidance Singularity (MAS).
    // Topological Effect: Information trapped in superposition -> "Black Hole" of rumination.
    struct FailureMode {
        enum Type {
            BLACK_HOLE_RUMINATION, // High input, zero output
            FRACTURE_DENIAL,       // Forced collapse without integration
            DIFFUSION_PARALYSIS    // Measurement spread too thin (Low COD)
        };
    };

    // 4. STABILIZATION OPERATOR: INTEGRATIVE RESONANCE (IRO)
    // Replaces "Forced Collapse" with "Compassionate Measurement".
    // Increases Informational Permeability to reduce Impedance.
    void Apply_Integrative_Resonance(CognitiveState& state) {
        // Step 1: Acknowledge Superposition (Validate Anxiety)
        // Reduces energy_density by converting "threat" to "data"
        state.energy_density *= 0.9; 
        
        // Step 2: Partial Collapse (Incremental Decision)
        // Prevents Binary Overload
        state.measurement_pending = false;
        
        // Step 3: Re-align COD
        // Ensures new state is within tolerance
        if (state.coherence_factor < COD_THRESHOLD_PEACE) {
            // Trigger "Repentance/Growth" loop to rebuild Stiffness
            state.coherence_factor += 0.15; 
        }
    }
}

// IMPLEMENTATION NOTES FOR PSYCHOLOGICAL ENGINEERING:
// 1. Subconscious (Quantum) = Unconscious Inference / Predictive Priors.
// 2. Conscious (Classical) = Attentional Bottleneck / Action Selection.
// 3. COD = Cognitive Dissonance Metric (Inverse relationship).
// 4. Failure Mode = Avoidance Coping leading to Emotional Burnout.
// 5. Operator = Mindfulness-Based Cognitive Therapy (MBCT) mechanics formalized.
'''

# ----------------------------------------------------------------------
# Helper regexes
# ----------------------------------------------------------------------
# Matches a floating point literal (including scientific notation)
FLOAT_LIT_RE = re.compile(
    r'(?<![\w.])'               # not preceded by alnum or dot
    r'(?:'                      # either
    r'\d+\.\d*'                 #   digits.dot[digits*]
    r'|\.\d+'                   #   .digits
    r'|\d+'                     #   digits (will be filtered later)
    r')'
    r'(?:[eE][+-]?\d+)?'        # optional exponent
    r'(?![\w.])'                # not followed by alnum or dot
)

# Matches a constexpr/const double definition:  constexpr double NAME = expr ;
CONST_DEF_RE = re.compile(
    r'^\s*(?:constexpr\s+|const\s+)?double\s+([A-Za-z_]\w*)\s*=\s*([^;]+)\s*;\s*$',
    re.MULTILINE
)

# ----------------------------------------------------------------------
# Parse constants and build a set of allowed names
# ----------------------------------------------------------------------
constant_values: Dict[str, ast.AST] = {}
allowed_names: Set[str] = set()

for m in CONST_DEF_RE.finditer(SOURCE_CODE):
    name, expr = m.group(1), m.group(2).strip()
    try:
        # Parse the initializer as a Python expression (safe because we only
        # allow numbers, previously defined names, and basic arithmetic).
        tree = ast.parse(expr, mode='eval')
        # Verify that the tree contains only Num, Name (if previously defined),
        # BinOp, UnaryOp, and the allowed operators.
        def _check(node):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return
                raise ValueError(f'Non-numeric constant {node.value}')
            if isinstance(node, ast.Name):
                if node.id not in allowed_names:
                    raise ValueError(f'Undefined constant {node.id}')
                return
            if isinstance(node, (ast.BinOp, ast.UnaryOp)):
                for child in ast.iter_child_nodes(node):
                    _check(child)
                return
            raise ValueError(f'Disallowed syntax {type(node).__name__}')
        _check(tree.body)
        constant_values[name] = tree
        allowed_names.add(name)
    except Exception as e:
        # If we cannot verify the expression, treat it as opaque – we will
        # not allow its use elsewhere (conservative).
        pass

# ----------------------------------------------------------------------
# Scan for floating point literals and validate them
# ----------------------------------------------------------------------
violations: List[Tuple[int, str, str]] = []  # (line, literal, context)

lines = SOURCE_CODE.splitlines()
for idx, line in enumerate(lines, start=1):
    for lit in FLOAT_LIT_RE.findall(line):
        # Ignore integer literals that are not part of a float (e.g., "0" in "0.9")
        # The regex also captures plain integers; we keep only those with a dot or exponent.
        if '.' not in lit and 'e' not in lit.lower():
            continue
        # Determine if the literal appears inside a constant definition RHS.
        # We approximate by checking if the line contains a constexpr/const double.
        is_in_const_def = bool(CONST_DEF_RE.search(line))
        # Allowed primitive literals
        if lit in {'0.0', '1.0', '2.0'}:
            continue
        # If it's inside a constant definition we still need to verify the RHS
        # uses only previously defined constants or allowed literals.
        if is_in_const_def:
            # Extract the RHS after the first '='.
            if '=' in line:
                rhs = line.split('=', 1)[1].rstrip('; ')
                # Replace known constant names with placeholders to allow eval.
                # We'll just trust the earlier parsing; if the name wasn't in
                # constant_values we flag it.
                # Simple approach: tokenise and check each token.
                tokens = re.findall(r'[A-Za-z_]\w*|\d+\.\d*|\.\d+|\d+|[+\-*/()]',
                                    rhs)
                ok = True
                for tok in tokens:
                    if re.match(r'\d+\.\d*|\.\d+|\d+', tok):
                        if tok not in {'0.0', '1.0', '2.0'}:
                            ok = False
                            break
                    elif re.match(r'[A-Za-z_]\w*', tok):
                        if tok not in allowed_names:
                            ok = False
                            break
                if not ok:
                    violations.append((idx, lit, line.strip()))
            continue
        # Otherwise it's a free-floating literal → violation.
        violations.append((idx, lit, line.strip()))

# ----------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------
if violations:
    print("Ω‑PROTOCOL VIOLATIONS DETECTED (magic numbers):")
    for line_no, lit, ctx in violations:
        print(f"  Line {line_no}: literal '{lit}' -> {ctx}")
    sys.exit(1)
else:
    print("✓ No unexplained floating‑point literals found. Code passes the magic‑number check.")
    sys.exit(0)