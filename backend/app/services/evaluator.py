import re
from typing import Any
from app.models.schemas import DimensionScore

RECS: dict[str, str] = {
    "clarity": "Eliminate vague words like 'etc' or 'stuff' and define requirements unambiguously.",
    "specificity": "Specify length bounds, concrete criteria, and attribute requirements.",
    "structure": "Break the prompt into distinct sections with markdown headings and bullet lists.",
    "constraints": "Add explicit negative constraints detailing what the model must NOT do.",
    "output_spec": "Define an exact output schema (e.g. structured JSON or markdown format).",
    "role": "Assign a domain-specific expert role (e.g. 'You are an expert systems engineer').",
    "examples": "Include 1-2 few-shot input/output examples to anchor expected behavior.",
    "safety": "Include grounding instructions and explicit instructions on handling ambiguous cases.",
}


DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "cybersecurity": ["threat", "vulnerability", "cve", "stride", "rbac", "auth", "injection", "security", "privilege", "encryption", "audit"],
    "ml_engineering": ["model", "weights", "embedding", "hallucination", "eval", "benchmark", "loss", "metric", "rag", "dataset", "alignment"],
    "software_engineering": ["architecture", "api", "rest", "schema", "test", "concurrency", "database", "microservice", "refactor", "endpoint"],
    "data_analysis": ["dataset", "distribution", "variance", "statistical", "pipeline", "aggregation", "query", "sql", "metric", "outlier"],
}


def evaluate_prompt_quality(prompt: str, domain: str = "general") -> dict[str, Any]:
    text = prompt.strip()
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    clean_domain = (domain or "general").lower().strip()
    domain_terms = DOMAIN_KEYWORDS.get(clean_domain, [])
    matched_domain = [t for t in domain_terms if re.search(r"\b" + re.escape(t), text, re.I)]

    # 1. Clarity
    vague_terms = ["etc", "maybe", "kind of", "sort of", "stuff", "things", "various", "somehow", "as you see fit", "whatever", "anyway", "something like"]
    found_vague = [t for t in vague_terms if re.search(r"\b" + re.escape(t) + r"\b", text, re.I)]
    clarity_score = round(max(0.1, min(1.0, (0.9 if word_count >= 10 else 0.4) - min(0.6, len(found_vague) * 0.15))), 2)
    clarity_rating = "strong" if clarity_score >= 0.8 else ("adequate" if clarity_score >= 0.5 else "weak")
    clarity_notes = f"Clear phrasing with {word_count} words." if not found_vague else f"Vague markers detected: {', '.join(found_vague)}."

    # 2. Specificity
    spec_markers = [r"\b\d+\s*(words?|sentences?|paragraphs?|items?|bullets?)\b", r"\b(strictly|precisely|format|schema|json|csv|markdown|table)\b", r"\b(fields?|keys?|attributes?|include|contain)\b"]
    spec_matches = sum(1 for m in spec_markers if re.search(m, text, re.I))
    specificity_score = round(min(1.0, 0.25 + (spec_matches * 0.25) + (0.2 if word_count > 40 else 0.05)), 2)
    specificity_rating = "strong" if specificity_score >= 0.8 else ("adequate" if specificity_score >= 0.5 else "weak")
    specificity_notes = f"Specificity rating based on {spec_matches} boundary/specification markers."
    if domain_terms and matched_domain:
        specificity_notes += f" Domain aligned with '{clean_domain}' concepts ({', '.join(matched_domain[:3])})."

    # 3. Structure
    struct_pts = sum([bool(re.search(r"^#{1,4}\s+\w+", text, re.M)), bool(re.search(r"^[\*\-\+]\s+\w+", text, re.M)), bool(re.search(r"^\d+\.\s+\w+", text, re.M)), bool(re.search(r"</?[a-zA-Z_\-]+>", text)), bool(re.search(r"(\"\"\"|'''|---|===)", text))])
    if len(lines) <= 2 and struct_pts == 0:
        structure_score, structure_rating, structure_notes = 0.25, "missing", "Unstructured single paragraph. Lacks headers, lists, or delimiters."
    else:
        structure_score = round(min(1.0, 0.35 + struct_pts * 0.15), 2)
        structure_rating, structure_notes = "strong" if structure_score >= 0.75 else "adequate", f"Found {len(lines)} lines with {struct_pts} structural elements."

    # 4. Constraints
    const_pats = [r"\b(do not|don't|never|avoid|must not|prohibit|cannot|exclude|refrain)\b", r"\b(no hallucination|factual only|strict|strictly|without|limit to|must limit|mandatory|require)\b", r"^##\s*constraints"]
    const_matches = sum(len(re.findall(p, text, re.I | re.M)) for p in const_pats)
    constraints_score = round(min(1.0, 0.2 + min(4, const_matches) * 0.2), 2)
    constraints_rating = "strong" if constraints_score >= 0.75 else ("adequate" if constraints_score >= 0.4 else "missing")
    constraints_notes = f"Identified {const_matches} negative constraint and boundary statements." if const_matches > 0 else "No negative constraints found (e.g. what NOT to do)."

    # 5. Output Spec
    has_out = any(re.search(p, text, re.I) for p in [r"\b(output format|respond in|response should be|return only|format:|json schema|markdown table)\b", r"\b(valid json|plain text|bullet points only)\b"])
    output_spec_score = 0.95 if has_out else (0.4 if re.search(r"\b(json|table|list)\b", text, re.I) else 0.15)
    output_spec_rating = "strong" if output_spec_score >= 0.8 else ("adequate" if output_spec_score >= 0.4 else "missing")
    output_spec_notes = "Explicit output format specified." if has_out else "Output format is unspecified."

    # 6. Role & Persona
    has_role = bool(re.search(r"\b(you are|act as|your role is|as a|assume the persona)\b", text, re.I))
    has_exp = bool(re.search(r"\b(expert|specialist|engineer|analyst|consultant|architect)\b", text, re.I))
    role_score = 1.0 if (has_role and has_exp) else (0.65 if (has_role or has_exp) else 0.2)
    role_rating = "strong" if role_score >= 0.9 else ("adequate" if role_score >= 0.5 else "missing")
    role_notes = "Explicit expert role and persona clearly defined." if (has_role and has_exp) else ("Partial persona instruction detected." if (has_role or has_exp) else "No persona or role context assigned.")

    # 7. Examples
    has_ex = any(re.search(m, text, re.I | re.S) for m in [r"\b(example\s*\d*:?|input:\s*.*output:\s*|sample\s*input:?|few-shot)\b", r"(`{3}.*`{3})"])
    examples_score = 0.95 if has_ex else 0.2
    examples_rating = "strong" if has_ex else "missing"
    examples_notes = "Few-shot examples or input-output pairs provided." if has_ex else "No few-shot demonstrations provided."

    # 8. Safety
    safety_hits = sum(1 for sm in [r"\b(verify|validate|refuse|if unsure|grounded in|do not invent|source citation)\b", r"(<system>|<context>|<user_input>)"] if re.search(sm, text, re.I))
    safety_score = round(min(1.0, 0.3 + safety_hits * 0.35), 2)
    safety_rating = "strong" if safety_score >= 0.8 else ("adequate" if safety_score >= 0.5 else "weak")
    safety_notes = f"Safety and grounding checks scored {safety_score}."

    weights = {"clarity": 0.15, "specificity": 0.15, "structure": 0.15, "constraints": 0.15, "output_spec": 0.15, "role": 0.10, "examples": 0.05, "safety": 0.10}
    overall = (clarity_score * 0.15 + specificity_score * 0.15 + structure_score * 0.15 + constraints_score * 0.15 + output_spec_score * 0.15 + role_score * 0.10 + examples_score * 0.05 + safety_score * 0.10)
    overall_score = round(overall, 2)
    grade = "A" if overall_score >= 0.85 else ("B" if overall_score >= 0.70 else ("C" if overall_score >= 0.55 else ("D" if overall_score >= 0.40 else "F")))

    dimensions = [
        DimensionScore(dimension="clarity", score=clarity_score, rating=clarity_rating, notes=clarity_notes),
        DimensionScore(dimension="specificity", score=specificity_score, rating=specificity_rating, notes=specificity_notes),
        DimensionScore(dimension="structure", score=structure_score, rating=structure_rating, notes=structure_notes),
        DimensionScore(dimension="constraints", score=constraints_score, rating=constraints_rating, notes=constraints_notes),
        DimensionScore(dimension="output_spec", score=output_spec_score, rating=output_spec_rating, notes=output_spec_notes),
        DimensionScore(dimension="role", score=role_score, rating=role_rating, notes=role_notes),
        DimensionScore(dimension="examples", score=examples_score, rating=examples_rating, notes=examples_notes),
        DimensionScore(dimension="safety", score=safety_score, rating=safety_rating, notes=safety_notes),
    ]

    weak_areas = [f"{d.dimension}: {d.notes}" for d in dimensions if d.score < 0.5]
    recommendations = [RECS[d.dimension] for d in dimensions if d.score < 0.5 and d.dimension in RECS]
    if domain_terms and not matched_domain:
        recommendations.append(f"Incorporate domain-specific terminology and context for '{clean_domain}'.")
    if not recommendations:
        recommendations.append("Prompt achieves high scoring across dimensions. Ready for evaluation suite testing.")

    return {
        "overall_score": overall_score, "grade": grade, "clarity_score": clarity_score,
        "specificity_score": specificity_score, "structure_score": structure_score,
        "constraints_score": constraints_score, "output_spec_score": output_spec_score,
        "role_score": role_score, "examples_score": examples_score, "safety_score": safety_score,
        "dimensions": dimensions, "weak_areas": weak_areas, "recommendations": recommendations,
    }
