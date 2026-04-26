# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import subprocess
import os

def check_hep_tool(tool_config_cmd):
    """Utility to extract build flags from HEP config tools."""
    print(f"Checking {tool_config_cmd}...")
    try:
        version = subprocess.check_output([tool_config_cmd, "--version"], text=True).strip()
        cxxflags = subprocess.check_output([tool_config_cmd, "--cxxflags"], text=True).strip()
        libs = subprocess.check_output([tool_config_cmd, "--libs"], text=True).strip()
        print(f"  ✅ Version: {version}")
        print(f"  ✅ CXX Flags: {cxxflags}")
        print(f"  ✅ Libs: {libs}\n")
        return {"version": version, "cxxflags": cxxflags, "libs": libs}
    except FileNotFoundError:
        print(f"  ❌ {tool_config_cmd} not found in PATH.\n")
        return None
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️ {tool_config_cmd} returned an error: {e}\n")
        return None

def main():
    print("🚀 [Omega Protocol] High Energy Physics (HEP) Tool Integrator\n")
    
    tools = [
        "fastjet-config",
        "root-config",
        "pythia8-config",
        "yoda-config",
        "clhep-config",
        "hepmc3-config"
    ]
    
    configs = {}
    for tool in tools:
        configs[tool] = check_hep_tool(tool)
        
    print("Integration Summary: These flags can now be dynamically pulled by the Omega CMake build system to link advanced topological analysis directly into libomega.so.")

if __name__ == "__main__":
    main()
