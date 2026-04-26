# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------

import ctypes
import os
import numpy as np

# Locate the compiled C-Core shared library
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/c_core/libomega_metrics.so'))

if os.path.exists(lib_path):
    omega_lib = ctypes.CDLL(lib_path)
    
    # Signature: void calculate_rcod_c(const float* tensor_a, const float* tensor_b, int length, float* out_cod, float* out_rcod)
    omega_lib.calculate_rcod_c.argtypes = [
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_float)
    ]
    
    # Signature: void calculate_wick_rotated_lr(float base_lr, float shred_invariant, float* out_real, float* out_imag)
    omega_lib.calculate_wick_rotated_lr.argtypes = [
        ctypes.c_float, ctypes.c_float,
        ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)
    ]
else:
    print(f"⚠️ [C-Translator] Core library not found at {lib_path}. Please compile src/c_core/omega_metrics.c.")
    omega_lib = None

def calculate_rcod_fast(tensor_a: np.ndarray, tensor_b: np.ndarray):
    """
    Translates Python numpy arrays to the highly-optimized C-Core for COD/RCOD calculation.
    """
    if omega_lib is None:
        raise RuntimeError("C library not compiled. Cannot route task to C-Core.")
        
    a_flat = np.ascontiguousarray(tensor_a.flatten(), dtype=np.float32)
    b_flat = np.ascontiguousarray(tensor_b.flatten(), dtype=np.float32)
    
    if len(a_flat) != len(b_flat):
        raise ValueError("Tensors must possess identical topologies.")
        
    out_cod = ctypes.c_float()
    out_rcod = ctypes.c_float()
    
    omega_lib.calculate_rcod_c(a_flat, b_flat, len(a_flat), ctypes.byref(out_cod), ctypes.byref(out_rcod))
    return out_cod.value, out_rcod.value

def get_wick_rotated_lr(base_lr: float, shred_invariant: float):
    """
    Translates the Chaos Injection math to the C-Core layer.
    """
    if omega_lib is None:
        raise RuntimeError("C library not compiled. Cannot route task to C-Core.")
        
    out_real = ctypes.c_float()
    out_imag = ctypes.c_float()
    
    omega_lib.calculate_wick_rotated_lr(base_lr, shred_invariant, ctypes.byref(out_real), ctypes.byref(out_imag))
    return out_real.value, out_imag.value
