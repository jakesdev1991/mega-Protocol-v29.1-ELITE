# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import functools
import inspect
import json
import traceback

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.auditor = None  # Lazy init

    def get_auditor(self):
        if self.auditor is None:
            from .matrix_auditor import MatrixAuditor
            self.auditor = MatrixAuditor()
        return self.auditor

    def register(self, func):
        """Registers a function as a tool."""
        name = func.__name__
        doc = func.__doc__ or "No description provided."
        sig = inspect.signature(func)
        
        # Build parameters schema
        params = {}
        for param_name, param in sig.parameters.items():
            if param_name == "_agent_name":
                continue # Skip internal arg
            params[param_name] = {
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                "default": param.default if param.default != inspect.Parameter.empty else None,
                "required": param.default == inspect.Parameter.empty
            }

        self.tools[name] = {
            "func": func,
            "description": doc,
            "parameters": params,
            "signature": str(sig)
        }
        return func

    def list_tools(self):
        """Returns a list of all registered tools and their metadata."""
        manifest = {}
        for name, info in self.tools.items():
            manifest[name] = {
                "description": info["description"],
                "parameters": info["parameters"],
                "signature": info["signature"]
            }
        return manifest

    def invoke(self, name, **kwargs):
        """Safely invokes a tool by name, subject to Matrix Audit."""
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
            
        _agent_name = kwargs.pop("_agent_name", "Unknown Agent")
        
        # Run Matrix Audit before execution
        auditor = self.get_auditor()
        approved, reason = auditor.evaluate_action(_agent_name, name, kwargs)
        
        if not approved:
            error_msg = f"❌ [Matrix Auditor] Action blocked. Reason: {reason}"
            print(error_msg)
            return error_msg
        
        try:
            return self.tools[name]["func"](**kwargs)
        except Exception as e:
            error_msg = f"Error executing tool '{name}': {str(e)}\n{traceback.format_exc()}"
            print(f"❌ [Registry Safety] {error_msg}")
            return error_msg

# Global registry instance
registry = ToolRegistry()

def tool_link(func):
    """Decorator to register a function with the Agent Zero framework."""
    return registry.register(func)

@tool_link
def list_capabilities():
    """Returns a full JSON manifest of all tools available to the agent."""
    return json.dumps(registry.list_tools(), indent=2)
