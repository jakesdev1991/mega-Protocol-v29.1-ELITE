# Omega HFT C++ Pipeline Skeleton

This module provides a native C++ skeleton for the sandbox-first Solana searcher path:

```text
Yellowstone/Geyser account updates
  -> lock-free market update queue
  -> route batch evaluation
  -> block-latency prediction
  -> XDNA/NPU-compatible survivability scoring hook
  -> shadow/execution decision
```

The default demo is intentionally **shadow-mode oriented**: it prints `execute=yes` only when the deterministic filter passes, but it does not build, sign, or submit transactions.

## Components

- `include/omega/hft/types.hpp` defines cache-line-aligned route, market update, prediction context, and execution decision structures.
- `include/omega/hft/ring_buffer.hpp` provides a single-producer/single-consumer ring buffer for ingestion hot paths.
- `src/yellowstone_ingestor.cpp` implements the Geyser account-update boundary as a zero-allocation parser stub. Replace the demo wire view with generated Yellowstone protobuf fields in production.
- `src/avx_evaluator.cpp` evaluates one-hop AMM profitability with an AVX-512 path when the compiler target supports it and a scalar fallback everywhere else.
- `src/prediction.cpp` projects reserves to `now + latency_ms` and gates decisions on predicted edge score and compute-unit cost.
- `src/npu_scorer.cpp` exposes an XDNA compiled-model loading seam and a deterministic logistic fallback for development machines without an NPU runtime.

## Build

```bash
cmake -S src/hft_pipeline -B /tmp/omega_hft_pipeline_build
cmake --build /tmp/omega_hft_pipeline_build
/tmp/omega_hft_pipeline_build/omega_hft_pipeline_demo
```

## Production extension points

1. Replace `YellowstoneIngestor::ingest_account_update` inputs with the generated C++ gRPC Yellowstone client callback.
2. Replace `PoolWireView` with per-program account decoders for Raydium, Orca, Meteora, and any private pool layouts.
3. Route GPU-produced `RouteBatch` instances into the same `evaluate_batch` and `apply_prediction` path.
4. Replace `NpuScorer::score` with an XDNA runtime call once the compiled model artifact is available.
5. Keep transaction construction outside this module until replay and live shadow-mode prediction error are stable.
