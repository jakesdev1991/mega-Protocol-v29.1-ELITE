# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator
---------------------------------
Checks any mathematical statements in a text for compliance with:
    Φₙ ≥ 0
    Φ_Δ ≥ 0
    J* ≤ J_baseline   (i.e., J* is not greater than the allowed baseline)

The validator is deliberately conservative: if it cannot parse a statement,
it treats it as non‑mathematical and ignores it.
"""

import re
import ast
import operator as op

# ---- Configuration ---------------------------------------------------------
# Set the baseline for J* according to your domain specification.
J_BASELINE = 0.0   # Example: J* must not exceed 0 (i.e., must be minimized to 0 or below)

# Allowed names in the expression evaluator
ALLOWED_NAMES = {"Phi_N": None, "Phi_Delta": None, "J_star": None}

# Safe AST node types we permit
_ALLOWED_NODES = {
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare,
    ast.Num, ast.Constant, ast.Name,
    ast.Add, ast.Sub, ast.MatMult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.And, ast.Or,  # for chained comparisons like 0 <= Phi_N <= 10
}
# ---------------------------------------------------------------------------

def _safe_eval(node):
    """Recursively evaluate an AST node using only safe operations."""
    if isinstance(node, ast.Num):          # <number>
        return node.n
    if isinstance(node, ast.Constant):    # <number> or <string> (Python 3.8+)
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Disallowed constant: {node.value!r}")

    if isinstance(node, ast.Name):
        if node.id not in ALLOWED_NAMES:
            raise ValueError(f"Disallowed name: {node.id}")
        # Names are treated as variables; they must be supplied in the env.
        return None  # placeholder; will be replaced later

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        operand = _safe_eval(node.operand)
        return +operand if isinstance(node.op, ast.UAdd) else -operand

    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub,
                                                          ast.Mult, ast.Div,
                                                          ast.FloorDiv, ast.Mod,
                                                          ast.Pow)):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        if left is None or right is None:
            return None   # cannot compute with unknown vars yet
        return {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.FloorDiv: op.floordiv,
            ast.Mod: op.mod,
            ast.Pow: op.pow,
        }[type(node.op)](left, right)

    if isinstance(node, ast.Compare):
        left = _safe_eval(node.left)
        # Chain comparisons: e.g., 0 <= Phi_N <= 5
        results = []
        for op_node, comparator in zip(node.ops, node.comparators):
            right = _safe_eval(comparator)
            if left is None or right is None:
                results.append(None)  # unknown -> treat as undecided
                continue
            cmp_result = {
                ast.Eq: op.eq,
                ast.NotEq: op.ne,
                ast.Lt: op.lt,
                ast.LtE: op.le,
                ast.Gt: op.gt,
                ast.GtE: op.ge,
            }[type(op_node)](left, right)
            results.append(cmp_result)
            left = right  # for chaining
        # All must be True; if any is False -> violation; if any None -> undecided
        if any(r is False for r in results):
            return False
        if all(r is True for r in results):
            return True
        return None   # undecided due to unknowns

    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)

    raise ValueError(f"Unsupported expression: {ast.dump(node)}")

def extract_math_statements(text):
    """
    Very simple regex‑based extractor for assignments and comparisons.
    Returns a list of strings that look like:
        Phi_N = 3
        Phi_Delta >= 0
        J_star <= 2
    """
    # Pattern: optional whitespace, allowed name, whitespace, (=|>=|<=|>|<), whitespace, number or name
    pattern = re.compile(
        r'\b(Phi_N|Phi_Delta|J_star)\s*([=<>]=?)\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?|Phi_N|Phi_Delta|J_star)\b'
    )
    return pattern.findall(text)

def validate_invariants(statements, env):
    """
    Evaluate each statement against the invariants.
    `env` should provide concrete values for Phi_N, Phi_Delta, J_star.
    Returns True if all checks pass, False otherwise.
    """
    for lhs, op_str, rhs in statements:
        expr = f"{lhs}{op_str}{rhs}"
        try:
            tree = ast.parse(expr, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Could not parse expression '{expr}': {e}")

        # Evaluate the expression using the provided environment
        def _eval_with_env(node):
            if isinstance(node, ast.Name):
                if node.id not in env:
                    raise ValueError(f"Unknown variable '{node.id}' in expression '{expr}'")
                return env[node.id]
            return _safe_eval(node)   # reuse the safe eval for literals/ops

        # Replace the node evaluator inside _safe_eval with env‑aware version
        # (We monkey‑patch the inner helper for simplicity.)
        original_safe = _safe_eval
        def _patched_safe(node):
            if isinstance(node, ast.Name):
                return env.get(node.id, None)
            return original_safe(node)
        # Temporarily swap
        globals()['_safe_eval'] = _patched_safe
        try:
            result = _eval_with_env(tree.body)
        finally:
            globals()['_safe_eval'] = original_safe

        if result is False:
            raise ValueError(f"Invariant violation: {expr} evaluated to False")
        # If result is None (undecided due to missing vars), we skip – caller must supply env.

    return True

def omega_validator(text, phi_n_val, phi_delta_val, j_star_val):
    """
    Top‑level validation function.
    Returns True if the text complies with the Omega Protocol invariants,
    raises ValueError with details if not.
    """
    statements = extract_math_statements(text)
    if not statements:
        # No math to check – trivially compliant
        return True

    env = {
        "Phi_N": phi_n_val,
        "Phi_Delta": phi_delta_val,
        "J_star": j_star_val,
    }
    return validate_invariants(statements, env)


# ------------------- Example Usage -----------------------------------------
if __name__ == "__main__":
    sample_reflection = """
    ### 1. METHODS: Reasoning Patterns Applied  
    Despite the task and response being explicitly "None" (indicating no substantive input or output was provided), I engaged in **meta-cognitive null-task analysis**...
    """
    # Example invariant values (replace with actual measured/required values)
    phi_n = 5.0          # must be >= 0
    phi_delta = 2.0      # must be >= 0
    j_star = -1.0        # must be <= J_BASELINE (0)

    try:
        if omega_validator(sample_reflection, phi_n, phi_delta, j_star):
            print("✅ Reflection complies with Omega Protocol invariants.")
        else:
            print("❌ Reflection violates invariants.")
    except ValueError as e:
        print(f"🚨 Invariant check failed: {e}")