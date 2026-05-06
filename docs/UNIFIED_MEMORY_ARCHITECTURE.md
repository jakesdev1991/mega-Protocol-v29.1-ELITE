# Unified Memory Architecture

This document defines the Omega Protocol memory stack used by the Long-Term
Memory (LTM), MCP, and Matrix auditing components. The architecture separates
fast semantic recall from durable archival history while preserving enough
metadata for Samson control, leakage gates, and historical MatrixAuditor review.

## 1. Memory tier map

| Tier | Store | Role | Mutability | Access pattern |
| --- | --- | --- | --- | --- |
| Microscopic working memory | Qdrant | Hot vector memory for current reasoning, recent task context, local semantic lookup, and short-horizon recall. | Mutable/upsertable; points may be refined or superseded. | Low-latency nearest-neighbor retrieval with optional reranking. |
| Macroscopic archive | Milvus | Long-range semantic archive for consolidated projects, historical traces, and cross-domain retrieval. | Append-mostly with controlled compaction. | Batch ingest, periodic consolidation, broad semantic replay. |
| Immutable root memory | Quantum Vault / Parquet | Auditable source-of-truth snapshots when immutable provenance is required. | Immutable once sealed; new roots are versioned rather than modified. | Offline validation, reproducibility, provenance recovery. |
| Transient compatibility | SQLite / JSONL | Legacy staging for scripts, import/export, queue drains, and migration compatibility. | Disposable or migratory; not authoritative. | Sequential processing, local CLI workflows, backfills into Qdrant/Milvus. |

## 2. Qdrant as microscopic working memory

Qdrant is the hot working-memory surface. It stores compact memory points for
near-real-time retrieval by `python_env/LTM/qdrant_memory.py`, using an embedding
model for first-pass recall and a cross-encoder reranker for precision.

Operational rules:

1. Qdrant contains current, task-adjacent, and frequently refreshed memories.
2. Each point payload carries `content`, `metadata`, and `created_at`.
3. Records may be updated when refiners deduplicate, summarize, or strengthen
   metadata.
4. Qdrant is not the final historical authority; sealed roots and Milvus archives
   remain the durable layers.
5. Qdrant records that influence controller decisions must include the required
   metadata fields in section 6.

Configured fields live in `configs.config.config`:

- `qdrant_path` / `OMEGA_QDRANT_PATH`: local embedded Qdrant storage path.
- `qdrant_url` / `OMEGA_QDRANT_URL`: remote Qdrant endpoint; takes precedence
  over `qdrant_path` when present.
- `qdrant_collection` / `OMEGA_QDRANT_COLLECTION`: collection name.
- `ltm_embedding` / `OMEGA_EMBEDDING_MODEL`: embedding model.
- `reranker_model` / `OMEGA_RERANKER_MODEL`: reranker model.

## 3. Milvus as macroscopic archive

Milvus is the macroscopic semantic archive. It holds consolidated, less volatile
memories that should survive local Qdrant rebuilds and provide a broad historical
search surface across projects, agents, and Matrix audits.

Milvus archive records should be promoted from Qdrant only after one of these
conditions is met:

- the memory has been referenced by a completed task or audit;
- the memory passed a refiner/deduplication cycle;
- the memory belongs to a sealed run, release, or MatrixAuditor decision;
- the memory is needed for cross-session or cross-agent replay.

Configured fields:

- `milvus_uri` / `OMEGA_MILVUS_URI`: Milvus endpoint.
- `milvus_token` / `OMEGA_MILVUS_TOKEN`: optional auth token.
- `milvus_collection` / `OMEGA_MILVUS_COLLECTION`: archive collection.

## 4. Quantum Vault / Parquet as immutable root memory

When applicable, Quantum Vault and Parquet stores are treated as immutable root
memory. They are not working queues and should not be edited in place. A sealed
root contains the raw or canonical record plus enough metadata to recreate the
vectorized layers.

Root-memory requirements:

1. Use append-only dataset partitions or content-addressed object names.
2. Store the original text or binary reference, normalized metadata, embedding
   model version, and checksum.
3. Record the promotion path: `source -> SQLite/JSONL -> Qdrant -> Milvus -> root`
   or direct root sealing when the source is already canonical.
4. Treat corrections as new root versions linked by `supersedes_root_id`.

## 5. SQLite / JSONL transient compatibility layers

SQLite databases and JSONL files are transient compatibility layers for legacy
scripts, command-line staging, migrations, and human-readable traces. They are
useful because many existing tools can append JSONL or query SQLite without a
vector dependency, but they are not authoritative memory after promotion.

Usage boundaries:

- SQLite is acceptable for local queues, pending migrations, and compatibility
  with existing `memories.db` workflows.
- JSONL is acceptable for append-only event logs, role-local memories, and batch
  import/export.
- A transient record should carry a `migration_state` such as `pending_qdrant`,
  `qdrant_indexed`, `milvus_archived`, or `root_sealed`.
- Downstream stores must not silently drop the Samson and leakage metadata fields.

## 6. Required metadata fields

Every memory record that can influence retrieval, control decisions, archival
promotion, or audits must include these metadata fields:

| Field | Type | Range | Meaning | Gate use |
| --- | --- | --- | --- | --- |
| `stiffness_s` | float | `[0.0, 1.0]` recommended | Control rigidity required for this memory. Higher values mean stricter invariants. | Samson raises damping when below/above thresholds depending on task class. |
| `reverse_overlap_r` | float | `[0.0, 1.0]` | Degree to which the memory overlaps with known counterexamples, reversals, or adversarial mirrors. | High values trigger contradiction checks before reuse. |
| `dissonance_delta` | float | `[0.0, 1.0]` recommended | Semantic or policy mismatch between the memory and current context. | High values reduce retrieval confidence or block promotion. |

Recommended base metadata schema:

```json
{
  "memory_id": "uuid-or-content-address",
  "source": "agent|cli|mcp|import|auditor",
  "branch": "tokamak|business|matrix|general",
  "created_at": "2026-05-06T00:00:00Z",
  "schema_version": "unified-memory-v1",
  "stiffness_s": 0.50,
  "reverse_overlap_r": 0.10,
  "dissonance_delta": 0.05,
  "migration_state": "qdrant_indexed",
  "embedding_model": "Alibaba-NLP/gte-large-en-v1.5",
  "reranker_model": "BAAI/bge-reranker-large"
}
```

## 7. MCP tool names and payload schemas

The current Omega MCP server exposes filesystem-oriented tools. These schemas are
also the minimum payload-contract style for future memory tools.

### `list_directory`

Request:

```json
{
  "path": "."
}
```

Response:

```json
[
  "relative-child-name"
]
```

### `read_file`

Request:

```json
{
  "path": "relative/path/from/workspace"
}
```

Response:

```json
"complete file contents or Error: message"
```

### `get_file_info`

Request:

```json
{
  "path": "relative/path/from/workspace"
}
```

Response:

```json
{
  "name": "file-or-directory-name",
  "path": "absolute-safe-path",
  "size_bytes": 1234,
  "is_dir": false,
  "is_file": true
}
```

### Proposed memory MCP extension schemas

The following names are reserved for unified memory services and should use the
same metadata requirements:

- `memory_add_qdrant`
- `memory_search_qdrant`
- `memory_promote_milvus`
- `memory_seal_root`
- `memory_audit_history`

`memory_add_qdrant` request:

```json
{
  "content": "memory text",
  "metadata": {
    "source": "mcp",
    "branch": "matrix",
    "schema_version": "unified-memory-v1",
    "stiffness_s": 0.50,
    "reverse_overlap_r": 0.10,
    "dissonance_delta": 0.05
  }
}
```

`memory_search_qdrant` request:

```json
{
  "query": "semantic query",
  "limit": 10,
  "rerank": true,
  "filters": {
    "branch": "matrix",
    "max_dissonance_delta": 0.18
  }
}
```

`memory_promote_milvus` request:

```json
{
  "memory_id": "uuid-or-content-address",
  "collection": "omega_archive",
  "promotion_reason": "completed MatrixAuditor decision"
}
```

`memory_seal_root` request:

```json
{
  "memory_id": "uuid-or-content-address",
  "root_store": "quantum_vault|parquet",
  "checksum": "sha256:...",
  "supersedes_root_id": null
}
```

The MCP transport is configured by `mcp_transport` / `OMEGA_MCP_TRANSPORT` and
currently supports `stdio` or `sse` in the server entrypoint.

## 8. Samson controller thresholds and PID gains

The Samson memory controller interprets required metadata before a memory can
shape reasoning or archival promotion. The central config exposes the following
initial thresholds and PID gains:

| Config field | Environment variable | Default | Behavior |
| --- | --- | --- | --- |
| `memory_controller.stiffness_min_s` | `OMEGA_STIFFNESS_MIN_S` | `0.35` | Below this, mark the record as too soft for high-stakes control unless corroborated. |
| `memory_controller.reverse_overlap_max_r` | `OMEGA_REVERSE_OVERLAP_MAX_R` | `0.62` | Above this, force reverse-overlap review before reuse. |
| `memory_controller.dissonance_delta_max` | `OMEGA_DISSONANCE_DELTA_MAX` | `0.18` | Above this, down-rank retrieval and block archival promotion. |
| `memory_controller.zscore_warn` | `OMEGA_ZSCORE_WARN` | `2.0` | Start warning and telemetry capture for leakage anomalies. |
| `memory_controller.zscore_block` | `OMEGA_ZSCORE_BLOCK` | `3.0` | Block use/promotion until audited. |
| `memory_controller.pid_kp` | `OMEGA_MEMORY_PID_KP` | `0.42` | Proportional correction for immediate metadata error. |
| `memory_controller.pid_ki` | `OMEGA_MEMORY_PID_KI` | `0.08` | Integral correction for persistent drift. |
| `memory_controller.pid_kd` | `OMEGA_MEMORY_PID_KD` | `0.21` | Derivative correction for sudden instability. |

Controller loop sketch:

```text
error = target_stability - observed_stability
correction = (Kp * error) + (Ki * accumulated_error) + (Kd * error_velocity)
retrieval_weight = base_weight * clamp(1.0 - correction, 0.0, 1.0)
```

## 9. Z-score leakage gate behavior

The z-score leakage gate compares a memory's current leakage signal against a
rolling baseline for its branch, source, and task class.

Behavior:

1. Compute `z = (current_signal - rolling_mean) / rolling_std` with a protected
   denominator floor for sparse histories.
2. If `abs(z) < zscore_warn`, allow normal retrieval.
3. If `zscore_warn <= abs(z) < zscore_block`, allow retrieval only with warning
   metadata, lower rank, and MatrixAuditor sampling.
4. If `abs(z) >= zscore_block`, block use and promotion until a MatrixAuditor or
   equivalent safety review clears the record.
5. Store the leakage decision alongside the memory event so later audits can
   reconstruct why a record was accepted, warned, or blocked.

The leakage gate should use `reverse_overlap_r` as a multiplier for adversarial
risk and `dissonance_delta` as a multiplier for context mismatch. A high z-score
with high reverse overlap should be treated as a stronger block candidate than a
high z-score in a well-corroborated branch.

## 10. MatrixAuditor historical-memory integration

MatrixAuditor is the bridge between action safety and historical memory. Its
decisions should be written back into the unified memory stack so future actions
can reuse the result instead of re-litigating identical risks.

Integration flow:

1. Before a moderate or extreme action, retrieve similar historical audit records
   from Qdrant and optionally Milvus.
2. Attach prior verdicts, constraints, and leakage outcomes to the audit prompt.
3. After the audit, write a new Qdrant working-memory record with the verdict,
   action descriptor, required metadata fields, and MCP/tool context.
4. Promote stable, repeated, or release-relevant decisions to Milvus.
5. Seal root-memory snapshots for audits that affect irreversible actions,
   published artifacts, or safety-critical controller thresholds.

Historical audit payload:

```json
{
  "audit_id": "uuid",
  "agent_name": "smith|neo|architect|omega-auditor",
  "tool_name": "run_shell",
  "tool_payload_hash": "sha256:...",
  "severity": "LOW|MODERATE|EXTREME",
  "verdict": "APPROVE|REJECT|APPROVE_WITH_MODIFICATIONS",
  "constraints": ["condition one", "condition two"],
  "stiffness_s": 0.75,
  "reverse_overlap_r": 0.30,
  "dissonance_delta": 0.08,
  "leakage_gate": {
    "zscore": 1.4,
    "decision": "allow"
  }
}
```
