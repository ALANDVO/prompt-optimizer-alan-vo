import json
import re
from typing import Any
from app.models.schemas import TestCaseSchema, ABCaseResult
from app.services.evaluator import evaluate_prompt_quality


def evaluate_case_assertion(
    prompt: str,
    test_case: TestCaseSchema,
) -> tuple[bool, str]:
    assertion = test_case.assertion_type
    expected = test_case.expected.strip()
    case_input = test_case.input.strip()

    combined = f"{prompt}\n{case_input}".lower()

    if assertion == "exact":
        passed = expected.lower() in combined
        reason = f"Exact phrase '{expected}' {'found' if passed else 'missing'}."
    elif assertion == "contains":
        terms = [t.strip().lower() for t in expected.split(",") if t.strip()]
        matched = [t for t in terms if t in combined]
        passed = len(matched) == len(terms) if terms else True
        reason = f"Terms matched: {len(matched)}/{len(terms)}."
    elif assertion == "regex":
        try:
            passed = bool(re.search(expected, combined, re.I))
            reason = f"Regex pattern {'matched' if passed else 'failed'}."
        except re.error:
            passed = False
            reason = "Invalid regex pattern in test case."
    elif assertion == "json_validity":
        has_json_spec = bool(re.search(r"\b(json|schema|keys|payload)\b", combined, re.I))
        passed = has_json_spec
        reason = "JSON structural requirement specified." if passed else "Lacks JSON specification."
    elif assertion == "min_length":
        try:
            min_len = int(expected) if expected.isdigit() else 20
        except ValueError:
            min_len = 20
        passed = len(combined) >= min_len
        reason = f"Length {len(combined)} vs minimum {min_len}."
    else:
        passed = True
        reason = "Default assertion passed."

    return passed, reason


def run_ab_test_suite(
    prompt_a: str,
    prompt_b: str,
    cases: list[TestCaseSchema],
) -> dict[str, Any]:
    eval_a = evaluate_prompt_quality(prompt_a)
    eval_b = evaluate_prompt_quality(prompt_b)

    wins_a = 0
    wins_b = 0
    ties = 0
    details: list[ABCaseResult] = []

    for idx, case in enumerate(cases):
        passed_a, reason_a = evaluate_case_assertion(prompt_a, case)
        passed_b, reason_b = evaluate_case_assertion(prompt_b, case)

        if passed_a and not passed_b:
            winner = "A"
            wins_a += 1
            reason = f"Prompt A satisfied assertion ('{case.assertion_type}'); Prompt B failed."
        elif passed_b and not passed_a:
            winner = "B"
            wins_b += 1
            reason = f"Prompt B satisfied assertion ('{case.assertion_type}'); Prompt A failed."
        else:
            # Both passed or both failed: break tie via deterministic quality score
            score_a = eval_a["overall_score"]
            score_b = eval_b["overall_score"]
            if score_a > score_b + 0.05:
                winner = "A"
                wins_a += 1
                reason = f"Both passed; Prompt A has higher quality rubric ({score_a:.2f} vs {score_b:.2f})."
            elif score_b > score_a + 0.05:
                winner = "B"
                wins_b += 1
                reason = f"Both passed; Prompt B has higher quality rubric ({score_b:.2f} vs {score_a:.2f})."
            else:
                winner = "TIE"
                ties += 1
                reason = f"Tie: comparable compliance and quality rubric ({score_a:.2f} vs {score_b:.2f})."

        preview = case.input[:60] + ("..." if len(case.input) > 60 else "")
        details.append(
            ABCaseResult(
                case_index=idx + 1,
                input_preview=preview,
                winner=winner,
                reason=reason,
                prompt_a_passed=passed_a,
                prompt_b_passed=passed_b,
            )
        )

    total = len(cases)
    if wins_a > wins_b:
        overall_winner = "A"
        confidence = round(wins_a / total, 2) if total else 0.0
    elif wins_b > wins_a:
        overall_winner = "B"
        confidence = round(wins_b / total, 2) if total else 0.0
    else:
        overall_winner = "TIE"
        confidence = 0.5

    return {
        "prompt_a": prompt_a,
        "prompt_b": prompt_b,
        "cases_count": total,
        "wins_a": wins_a,
        "wins_b": wins_b,
        "ties": ties,
        "winner": overall_winner,
        "confidence": confidence,
        "details": details,
    }
