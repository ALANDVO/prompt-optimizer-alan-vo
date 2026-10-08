import pytest
from app.services.optimizer import optimize_prompt


@pytest.mark.asyncio
async def test_optimize_prompt_structured_strategy():
    raw_prompt = "Write an API to authenticate users"
    res = await optimize_prompt(raw_prompt, target_domain="software_engineering", strategy="structured")

    assert res["score_after"] > res["score_before"]
    assert res["improvement_delta"] > 0
    assert "## Role & Persona" in res["optimized_prompt"]
    assert "## Operational Constraints" in res["optimized_prompt"]
    assert "## Output Specification" in res["optimized_prompt"]
    assert res["llm_used"] is False


@pytest.mark.asyncio
async def test_optimize_prompt_negative_constraints_strategy():
    raw_prompt = "Summarize user telemetry without errors"
    res = await optimize_prompt(raw_prompt, target_domain="cybersecurity", strategy="negative_constraints")

    assert "Mandatory Negative Constraints" in res["optimized_prompt"]
    assert "DO NOT fabricate" in res["optimized_prompt"]
    assert res["score_after"] >= res["score_before"]


@pytest.mark.asyncio
async def test_optimize_prompt_xml_tagged_strategy():
    raw_prompt = "Classify customer feedback sentiment"
    res = await optimize_prompt(raw_prompt, target_domain="ml_engineering", strategy="xml_tagged")

    assert "<prompt_configuration>" in res["optimized_prompt"]
    assert "<role>" in res["optimized_prompt"]
    assert "<task_instruction>" in res["optimized_prompt"]
    assert "</prompt_configuration>" in res["optimized_prompt"]


@pytest.mark.asyncio
async def test_optimize_prompt_cot_guided_strategy():
    raw_prompt = "Explain quantum key distribution"
    res = await optimize_prompt(raw_prompt, target_domain="general", strategy="cot_guided")

    assert "## Thinking & Reasoning Protocol" in res["optimized_prompt"]
    assert "systematically work through the problem" in res["optimized_prompt"]


@pytest.mark.asyncio
async def test_optimize_prompt_few_shot_strategy():
    raw_prompt = "Translate network error codes to user messages"
    res = await optimize_prompt(raw_prompt, target_domain="software_engineering", strategy="few_shot")

    assert "### Example 1" in res["optimized_prompt"]
    assert "### Example 2" in res["optimized_prompt"]
    assert res["score_after"] > res["score_before"]
