# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import ctypes
import os
import sys
import time

# Ensure python_env subdirectories (agent_zero, finance, etc) are in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the restored Python AI tools
try:
    from finance.finance_agent import FinanceAgent
    from agent_zero.serc import SERC
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

# Define the corresponding Python structure for the C UnifiedMemoryBlock
class UnifiedMemoryBlock(ctypes.Structure):
    _fields_ = [
        ("base_address", ctypes.c_void_p),
        ("total_size", ctypes.c_size_t),
        ("current_head", ctypes.c_uint64)
    ]

class OmegaProtocolWrapper:
    def __init__(self, lib_path="../build/libomega.so"):
        if not os.path.exists(lib_path):
            print(f"Warning: C Library not found at {lib_path}.")
            print("Please run cmake and make in the root directory on Gentoo to compile libomega.so.")
            # We don't exit here so the python syntax can still be validated.
            self.lib = None
            self.memory_block = UnifiedMemoryBlock()
            return
            
        print(f"[Omega Python] Loading C Library from {lib_path}")
        self.lib = ctypes.CDLL(lib_path)
        
        # Configure C function signatures
        self.lib.omega_sys_init.argtypes = [ctypes.POINTER(UnifiedMemoryBlock)]
        self.lib.omega_sys_init.restype = ctypes.c_int
        
        self.lib.omega_load_environment.argtypes = [ctypes.POINTER(UnifiedMemoryBlock), ctypes.c_char_p]
        self.lib.omega_load_environment.restype = ctypes.c_int
        
        self.lib.omega_execute_primitive.argtypes = [ctypes.POINTER(UnifiedMemoryBlock), ctypes.c_uint64]
        self.lib.omega_execute_primitive.restype = None
        
        self.lib.omega_sys_shutdown.argtypes = [ctypes.POINTER(UnifiedMemoryBlock)]
        self.lib.omega_sys_shutdown.restype = None
        
        # Initialize the global memory structure
        self.memory_block = UnifiedMemoryBlock()
        
    def start_engine(self):
        if not self.lib: return
        print("[Omega Python] Initializing Unified 28GB HSA Memory via C-Core...")
        result = self.lib.omega_sys_init(ctypes.byref(self.memory_block))
        if result != 0:
            print("[Error] Gentoo unified memory allocation failed. Check kernel HSA/UMA settings.")
            sys.exit(result)
            
    def load_domain(self, domain_path):
        if not self.lib: return
        encoded_path = domain_path.encode('utf-8')
        print(f"[Omega Python] Loading domain primitives from {domain_path}...")
        self.lib.omega_load_environment(ctypes.byref(self.memory_block), encoded_path)

    def step(self, cycles=1):
        if not self.lib: return
        self.lib.omega_execute_primitive(ctypes.byref(self.memory_block), cycles)
        
    def run_anti_agency_audit(self):
        """Invoke Agent Zero / FinanceAgent on top of the UBD/HSA state"""
        if not AGENTS_AVAILABLE:
            print("⚠️ Agent Frameworks missing in python_env.")
            return
            
        print("\n=== Launching High-Level AI Agents ===")
        refiner = FinanceAgent("Omega-Refiner")
        serc_system = SERC()
        
        # Pull mock context (in real scenario, we'd read string from memory_block.base_address ctypes pointer)
        prompt = "Analyze the current execution of Linux HSA node data in unified memory and calculate Informational Jerk stability."
        
        print("🧠 Invoking Agent Zero SERC Anti-Agency Stress Test...")
        serc_output = serc_system.run_cycle(prompt)
        
        print("💼 Invoking FinanceAgent Omega-Refiner for Audit...")
        refiner_output = refiner.reason(f"Audit the SERC Output: {serc_output}")
        print(f"Refinement result: {str(refiner_output)[:100]}...\n")

    def shutdown(self):
        if not self.lib: return
        self.lib.omega_sys_shutdown(ctypes.byref(self.memory_block))

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(current_dir, "..", "build", "libomega.so")
    
    omega = OmegaProtocolWrapper(lib_path)
    
    if omega.lib:
        omega.start_engine()
        
        # Load environment manifest
        manifest_path = os.path.join(current_dir, "..", "configs", "project_manifest.txt")
        omega.load_domain(manifest_path)
        
        try:
            # Execute primitive engine
            cycles_to_run = 10000 
            print(f"Running Omega for {cycles_to_run} cycles on integrated HSA UMA.")
            
            # Step the C Primitive loop
            omega.step(cycles=int(cycles_to_run / 2))
            
            # Run the Python-side autonomous agents over the unified memory
            omega.run_anti_agency_audit()
            
            # Finish C routine
            omega.step(cycles=int(cycles_to_run / 2))
            
            print("Execution complete. Shutting down...")
            omega.shutdown()
        except KeyboardInterrupt:
            print("Omega Execution halted by user.")
            omega.shutdown()
    else:
        print("[Omega Python] Running in Dummy Mode. Library not loaded.")
