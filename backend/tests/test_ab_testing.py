from app.models.schemas import TestCaseSchema
from app.services.ab_test import run_ab_test_suite


def test_ab_test_assertion_evaluation():
    prompt_a = "You are a database engineer. Return only valid JSON formatted as a list of table names."
    prompt_b = "Give me some tables for an ecommerce app."

    cases = [
        TestCaseSchema(input="Generate tables", expected="json", assertion_type="contains"),
        TestCaseSchema(input="Generate schema", expected="engineer", assertion_type="contains"),
        TestCaseSchema(input="Format check", expected="tables", assertion_type="contains"),
    ]

    res = run_ab_test_suite(prompt_a, prompt_b, cases)

    assert res["cases_count"] == 3
    assert res["winner"] == "A"
    assert res["wins_a"] >= 2
    assert res["confidence"] > 0.5
    assert len(res["details"]) == 3


def test_ab_test_ties():
    prompt_a = "Summarize the text in 3 sentences."
    prompt_b = "Summarize the text in 3 sentences."

    cases = [
        TestCaseSchema(input="Sample input text", expected="sentences", assertion_type="contains"),
    ]

    res = run_ab_test_suite(prompt_a, prompt_b, cases)
    assert res["winner"] == "TIE"
    assert res["ties"] == 1
