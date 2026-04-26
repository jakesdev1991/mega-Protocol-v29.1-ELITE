# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import numpy as np
from typing import Dict, Any, Tuple

class RCODMonitor:
    """
    Streaming curvature monitor for LLM training.
    Tracks novelty, drift, and fracture in representation space across multiple layers.
    Optimized leveraging pure PyTorch vectorization.

    Theoretical Foundation:
    In the Omega Protocol (Version 26.0), the single RCOD metric is replaced 
    by orthogonal modes: Phi_N (Newtonian mode) and Phi_Delta (Asymmetry mode).
    Phi_N represents the covariant diagonal baseline of the informational flux,
    while Phi_Delta captures the fracture/asymmetry across multi-timescale 
    EMA nodes. A high Phi_Delta score flags a breakdown in the forward/reverse 
    unitary handshake—an event defined as an "Informational Shock."
    """
    def __init__(self, num_nodes: int = 10, node_dim: int = 32, quantize_scale: float = 20.0, tol_bands: int = 1):
        self.num_nodes = num_nodes
        self.node_dim = node_dim
        self.quantize_scale = quantize_scale
        self.tol_bands = tol_bands
        
        self.layers: Dict[str, Dict[str, torch.Tensor]] = {}
        # Precompute alphas across nodes
        self.base_alphas = torch.tensor([1.0 - i * 0.07 for i in range(self.num_nodes)])

    def _init_layer(self, device: torch.device) -> Dict[str, torch.Tensor]:
        return {
            "alpha": self.base_alphas.to(device),
            "state": torch.zeros(self.num_nodes, device=device),
            "init": torch.zeros(self.num_nodes, dtype=torch.bool, device=device),
            "rings": torch.zeros(self.num_nodes, self.node_dim, dtype=torch.int32, device=device),
            "head": torch.zeros(self.num_nodes, dtype=torch.long, device=device),
            "count": torch.zeros(self.num_nodes, dtype=torch.long, device=device)
        }

    def ready(self, layer_id: str = None) -> bool:
        """Check if buffer is filled."""
        if layer_id:
            if layer_id not in self.layers: 
                return False
            return bool((self.layers[layer_id]["count"] == self.node_dim).all())
        if not self.layers:
            return False
        return all(bool((l["count"] == self.node_dim).all()) for l in self.layers.values())

    @torch.no_grad()
    def step(self, raw_value: float, layer_id: str = "default") -> Tuple[float, float]:
        """
        Processes a raw input value into the ring buffers, entirely vectorized.
        Returns (phi_n, phi_delta) in covariant diagonal formulation.
        """
        # Ensure we just have a python float or scalar tensor
        if isinstance(raw_value, torch.Tensor):
            raw_value = raw_value.detach()
            device = raw_value.device
        else:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            raw_value = torch.tensor(float(raw_value), device=device)
            
        if layer_id not in self.layers:
            self.layers[layer_id] = self._init_layer(device)
            
        l = self.layers[layer_id]
        
        # 1. Update State (Vectorized EMA)
        # For nodes not initialized, set directly to raw_value
        uninit_mask = ~l["init"]
        if uninit_mask.any():
            l["state"][uninit_mask] = raw_value
            l["init"][uninit_mask] = True
            
        # For nodes already initialized, apply EMA
        init_mask = l["init"] & ~uninit_mask
        if init_mask.any():
            alphas = l["alpha"][init_mask]
            l["state"][init_mask] = alphas * raw_value + (1.0 - alphas) * l["state"][init_mask]

        # 2. Quantize efficiently on tensor
        q_vals = torch.round(l["state"] * self.quantize_scale).to(torch.int32)
        
        # 3. Vectorized Push to Ring Buffer
        nodes_idx = torch.arange(self.num_nodes, device=device)
        heads = l["head"]
        
        l["rings"][nodes_idx, heads] = q_vals
        l["head"] = (heads + 1) % self.node_dim
        
        # Update counts
        l["count"] = torch.clamp(l["count"] + 1, max=self.node_dim)

        # 4. Compute Phi Metrics
        # Get latest pushed element across all nodes
        valid_mask = l["count"] > 0
        latest_vals = torch.zeros(self.num_nodes, dtype=torch.int32, device=device)
        if valid_mask.any():
            idx_to_read = (l["head"][valid_mask] - 1) % self.node_dim
            latest_vals[valid_mask] = l["rings"][valid_mask, idx_to_read]
            
        # Sort values
        slice_sorted, _ = torch.sort(latest_vals)
        
        # Calculate maximum cohesive banded sequence
        slice_sorted_cpu = slice_sorted.cpu().numpy()
        max_c = 1
        i = 0
        while i < self.num_nodes:
            j = i
            while j + 1 < self.num_nodes and (slice_sorted_cpu[j + 1] - slice_sorted_cpu[i]) <= self.tol_bands:
                j += 1
            max_c = max(max_c, j - i + 1)
            i += 1
            
        # 5. Dimensionless Refinement (v26.7): Normalized Informational Jerk (J*)
        # We define Jerk as the 3rd derivative of the state (diff-diff-diff).
        # Normalizing by state^2 gives a dimensionless flux ratio.
        # 4. Compute Phi Metrics (v28.0 Handshake)
        # Phi_ij = sqrt(phi+ * phi-) (Geometric Mean)
        # chi_delta = 0.5 * ln(phi+/phi-)
        phi_plus = max(1e-6, min(1.0, max_c / self.num_nodes))
        phi_minus = max(1e-6, min(1.0, float(l["state"].mean())))
        
        # Symmetric Overlap (Geometric Mean)
        phi_n = np.sqrt(phi_plus * phi_minus)
        
        # Unbounded Asymmetry Proxy
        phi_delta = 0.5 * abs(np.log(phi_plus / phi_minus))
        phi_delta = max(0.0, min(1.0, phi_delta)) # Cap for monitor signal
        # We compare the mean of the fast nodes vs slow nodes
        fast_mean = l["state"][:3].mean()
        slow_mean = l["state"][7:].mean()
        vel = float(fast_mean - slow_mean)
        
        # We track velocity history in a simple internal state for jerk
        if "prev_vel" not in l: l["prev_vel"] = vel
        accel = vel - l["prev_vel"]
        l["prev_vel"] = vel
        
        if "prev_accel" not in l: l["prev_accel"] = accel
        jerk = accel - l["prev_accel"]
        l["prev_accel"] = accel
        
        # J* is dimensionless: jerk / (phi_n^2 + epsilon)
        j_star = abs(jerk) / (phi_n**2 + 1e-6)
        
        # Boost Phi_Delta if J* is high (Dimensionless Pivot)
        if j_star > 1.5: 
            phi_delta = min(1.0, phi_delta * 1.25)
        
        return phi_n, phi_delta

