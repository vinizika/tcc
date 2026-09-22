from app.database.benchmark_retrieval_variants import reciprocal_rank, summarize


def test_reciprocal_rank():
    assert reciprocal_rank(["wrong", "right"], {"right"}) == 0.5
    assert reciprocal_rank(["wrong"], {"right"}) == 0.0


def test_summarize_reports_each_variant_and_threshold():
    variants = {}
    for name in ("vector_only", "rerank_only", "routing_only", "production"):
        variants[name] = {
            "hit_at_1": True,
            "hit_at_5": True,
            "reciprocal_rank": 1.0,
            "seconds": 0.01,
            "topics": ["right"],
            "context_scores": [0.72],
        }
    result = summarize([
        {"expected_topics": ["right"], "variants": variants}
    ], [0.70, 0.75])
    assert result["vector_only"]["precision_at_1"] == 1.0
    assert result["production"]["thresholds"]["0.7"]["cases_with_context"] == 1
    assert result["production"]["thresholds"]["0.75"]["cases_with_context"] == 0
