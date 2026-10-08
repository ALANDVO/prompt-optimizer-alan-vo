import time
import math
from typing import Any
from app.models.schemas import BenchmarkModelResult
from app.services.evaluator import evaluate_prompt_quality

# Reference latency and token multiplier profiles for models
MODEL_PROFILES: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {"base_latency": 0.42, "token_density": 1.15, "compliance": 0.94},
    "claude-3-5-sonnet": {"base_latency": 0.65, "token_density": 1.25, "compliance": 0.96},
    "gemini-1.5-pro": {"base_latency": 0.58, "token_density": 1.20, "compliance": 0.93},
    "ollama-llama3": {"base_latency": 0.35, "token_density": 1.10, "compliance": 0.88},
}


def run_model_benchmarking(
    prompt: str,
    models: list[str],
) -> dict[str, Any]:
    eval_data = evaluate_prompt_quality(prompt)
    overall_score = eval_data["overall_score"]
    char_count = len(prompt)
    estimated_base_tokens = max(15, int(char_count / 3.8))

    results: list[BenchmarkModelResult] = []

    for model_name in models:
        profile = MODEL_PROFILES.get(
            model_name.lower().strip(),
            {"base_latency": 0.50, "token_density": 1.15, "compliance": 0.90},
        )

        latency = round(profile["base_latency"] + (estimated_base_tokens * 0.0018), 3)
        tokens = int(estimated_base_tokens * profile["token_density"])
        compliance = round(profile["compliance"] * (0.8 + 0.2 * overall_score), 2)
        clarity_index = round(eval_data["clarity_score"] * 10, 1)

        quality = round((overall_score * 0.6 + compliance * 0.4) * 10, 1)

        results.append(
            BenchmarkModelResult(
                model=model_name,
                latency_seconds=latency,
                estimated_tokens=tokens,
                clarity_index=clarity_index,
                compliance_score=compliance,
                overall_quality=quality,
                status="completed",
            )
        )

    # Sort results by overall quality descending, then latency ascending
    sorted_results = sorted(
        results,
        key=lambda r: (r.overall_quality, -r.latency_seconds),
        reverse=True,
    )
    best_model = sorted_results[0].model if sorted_results else "None"

    return {
        "prompt": prompt,
        "results": results,
        "best_model": best_model,
    }
