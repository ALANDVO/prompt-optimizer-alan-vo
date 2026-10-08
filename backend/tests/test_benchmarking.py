from app.services.benchmark import run_model_benchmarking


def test_benchmark_multiple_models():
    prompt = "You are a senior security researcher. Identify 3 critical vulnerabilities in this smart contract."
    models = ["gpt-4o-mini", "claude-3-5-sonnet", "gemini-1.5-pro", "ollama-llama3"]

    res = run_model_benchmarking(prompt, models)

    assert len(res["results"]) == 4
    assert res["best_model"] in models
    for model_res in res["results"]:
        assert model_res.latency_seconds > 0
        assert model_res.estimated_tokens > 0
        assert 0.0 <= model_res.compliance_score <= 1.0
        assert model_res.status == "completed"
