from app.services.evaluator import evaluate_prompt_quality


def test_evaluator_vague_prompt():
    raw_prompt = "Do some stuff with data and things like that etc."
    res = evaluate_prompt_quality(raw_prompt)

    assert res["overall_score"] < 0.40
    assert res["grade"] == "F"
    assert res["clarity_score"] < 0.50
    assert len(res["weak_areas"]) > 0
    assert any("clarity" in w for w in res["weak_areas"])


def test_evaluator_structured_prompt():
    structured_prompt = """## Role
You are an expert systems engineer.

## Task
Design an event-driven architecture using RabbitMQ for async image processing.

## Constraints
- Do not use polling mechanisms.
- Must limit memory footprint to 512MB.
- Strictly return valid JSON schema.

## Output Format
Return only a JSON object containing keys 'services', 'queues', and 'exchange'.

## Example
Input: Image resize worker
Output: {"services": ["resize"], "queues": ["img.resize"], "exchange": "media"}
"""
    res = evaluate_prompt_quality(structured_prompt, domain="software_engineering")

    assert res["overall_score"] >= 0.75
    assert res["grade"] in ("A", "B")
    assert res["role_score"] >= 0.9
    assert res["constraints_score"] >= 0.7
    assert res["output_spec_score"] >= 0.9
    assert res["examples_score"] >= 0.9


def test_evaluator_empty_or_minimal_prompt():
    res = evaluate_prompt_quality("Hi")
    assert res["overall_score"] < 0.35
    assert res["grade"] == "F"
    assert len(res["dimensions"]) == 8


def test_evaluator_all_dimensions_present():
    prompt = "Summarize the quarterly financial report in 3 paragraphs. Focus on net margins."
    res = evaluate_prompt_quality(prompt, domain="data_analysis")

    dims = {d.dimension: d.score for d in res["dimensions"]}
    assert "clarity" in dims
    assert "specificity" in dims
    assert "structure" in dims
    assert "constraints" in dims
    assert "output_spec" in dims
    assert "role" in dims
    assert "examples" in dims
    assert "safety" in dims
    assert all(0.0 <= s <= 1.0 for s in dims.values())


def test_evaluator_domain_alignment_matched():
    prompt = "Conduct a STRIDE threat modeling analysis on cloud auth infrastructure."
    res = evaluate_prompt_quality(prompt, domain="cybersecurity")
    spec_dim = next(d for d in res["dimensions"] if d.dimension == "specificity")
    assert "Domain aligned" in spec_dim.notes
    assert "stride" in spec_dim.notes or "threat" in spec_dim.notes


def test_evaluator_domain_alignment_missing():
    prompt = "Write a quick greeting email for a team offsite event."
    res = evaluate_prompt_quality(prompt, domain="cybersecurity")
    assert any("Incorporate domain-specific terminology and context for 'cybersecurity'" in r for r in res["recommendations"])

