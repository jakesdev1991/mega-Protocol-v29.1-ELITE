from pathlib import Path
from tempfile import TemporaryDirectory

from agent_zero.framework.memory import SharedConsensusMemory
from agent_zero.framework.models import SanitizedPromotion
from LTM.omega_tensor import normalize_to_omega_tensor


def test_normalize_to_omega_tensor_strips_source_labels_and_scores_signals():
    tensor = normalize_to_omega_tensor(
        "Source: example.com | Claim remains stable.",
        {
            "confidence": 0.9,
            "verified": True,
            "access_count": 4,
            "domain": "example.com",
            "source_kind": "web",
        },
    )

    assert tensor["normalized_content"] == "Claim remains stable."
    assert tensor["domain_signature"] == "example.com"
    assert tensor["source_kind"] == "web"
    assert 0.0 <= tensor["stiffness_s"] <= 1.0
    assert 0.0 <= tensor["reverse_overlap_r"] <= 1.0
    assert 0.0 <= tensor["dissonance_delta"] <= 1.0


def test_shared_consensus_promotion_persists_omega_tensor_metadata():
    with TemporaryDirectory() as temp_dir:
        memory = SharedConsensusMemory(db_path=Path(temp_dir) / "memories.db")
        record = memory.promote(
            SanitizedPromotion(
                kind="constraint",
                title="Neutral memory",
                content="Domain: physics | Plasma remains stable for the tested interval.",
                metadata={"confidence": 0.8, "verified": "confirmed"},
            ),
            source="governor-test",
        )

        loaded = memory.read(limit=1)[0]

    assert record.normalized_content == "Plasma remains stable for the tested interval."
    assert loaded.normalized_content == record.normalized_content
    assert loaded.stiffness_s == record.stiffness_s
    assert loaded.metadata["normalized_content"] == record.normalized_content
