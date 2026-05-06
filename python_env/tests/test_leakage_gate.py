from LTM.leakage_gate import ZScoreLeakageGate


def test_gate_rescores_and_exposes_modes():
    gate = ZScoreLeakageGate(window_size=4)
    gate.update_metrics(dissonance=0.1, failed_tool_calls=0.0, auditor_conflicts=0.0, retrieval_variance=0.02)
    gate.update_metrics(dissonance=0.2, failed_tool_calls=1.0, auditor_conflicts=0.0, retrieval_variance=0.04)

    results = gate.rescore_results(
        [
            {
                "content": "stable memory",
                "vector_similarity": 0.9,
                "reranker_score": 2.0,
                "metadata": {"stiffness_s": 0.8, "reverse_overlap_r": 0.1, "dissonance_delta": 0.05},
            },
            {
                "content": "noisy memory",
                "vector_similarity": 0.5,
                "reranker_score": -1.0,
                "metadata": {"stiffness_s": 0.2, "reverse_overlap_r": 0.9, "dissonance_delta": 0.6},
            },
        ],
        current_state=0.35,
    )

    assert results[0]["content"] == "stable memory"
    assert "leakage_score" in results[0]
    assert "current_z_score" in results[0]
    assert results[0]["retrieval_mode"] == "normal"
    assert gate.stats()["retrieval_mode"] == "normal"


def test_gate_reports_open_and_constricted_modes():
    gate = ZScoreLeakageGate()

    gate.z_score(0.20)
    assert gate.stats()["retrieval_mode"] == "open-leakage"

    gate.z_score(0.50)
    assert gate.stats()["retrieval_mode"] == "constricted"
