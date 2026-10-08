import difflib
from typing import Any
from app.services.evaluator import evaluate_prompt_quality
from app.services.llm_adapter import LLMAdapter

DOMAIN_PERSONAS: dict[str, str] = {
    "cybersecurity": "You are a Principal Cybersecurity Analyst specializing in threat detection, secure system architecture, and incident response.",
    "ml_engineering": "You are a Senior Machine Learning Engineer and AI Alignment Researcher with deep expertise in LLM fine-tuning, evals, and agent workflows.",
    "software_engineering": "You are a Staff Software Architect specializing in clean architecture, type safety, and resilient distributed systems.",
    "data_analysis": "You are a Senior Quantitative Analyst skilled in statistical rigor, causal inference, and reproducible data pipelines.",
    "general": "You are an authoritative subject matter expert and senior technical advisor.",
}


def build_structured_prompt(prompt: str, domain: str) -> str:
    persona = DOMAIN_PERSONAS.get(domain.lower(), DOMAIN_PERSONAS["general"])
    clean_task = prompt.strip()
    return f"""## Role & Persona
{persona}

## Task & Primary Objective
{clean_task}

## Operational Constraints & Rules
- Provide accurate, factually grounded analysis without hallucination.
- Adhere strictly to the requested format and domain standards.
- Do not include conversational filler, meta-announcements, or conversational preambles.
- If information is insufficient or ambiguous, explicitly state assumptions or request clarification.

## Execution Steps
1. Carefully parse the objective and determine key requirements.
2. Formulate the response with domain rigor and precision.
3. Validate output against all specified constraints before concluding.

## Output Specification
- Format: Clean Markdown with clear section headers and bullet points.
- Detail: Concisely structured with high information density.
"""


def build_role_expert_prompt(prompt: str, domain: str) -> str:
    persona = DOMAIN_PERSONAS.get(domain.lower(), DOMAIN_PERSONAS["general"])
    clean_task = prompt.strip()
    return f"""{persona}

Your core operational stance is uncompromising precision, technical clarity, and rigorous adherence to specification.

Task Instruction:
{clean_task}

Verification Checklist:
- Accuracy: All statements must be factually verifiable.
- Tone: Professional, objective, and analytical.
- Constraints: Avoid unverified claims; cite or state concrete reasoning.
"""


def build_negative_constraints_prompt(prompt: str, domain: str) -> str:
    clean_task = prompt.strip()
    return f"""{clean_task}

Mandatory Negative Constraints (Strict Compliance Required):
1. DO NOT fabricate facts, data points, or API references.
2. DO NOT include pleasantries, introductory greetings, or concluding remarks (e.g. "Sure!", "Hope this helps!").
3. DO NOT exceed the necessary length; prioritize token efficiency and concise language.
4. DO NOT deviate from the requested domain context ({domain}).
5. If constraints conflict, prioritize safety, factual accuracy, and explicit instruction over style.
"""


def build_xml_tagged_prompt(prompt: str, domain: str) -> str:
    persona = DOMAIN_PERSONAS.get(domain.lower(), DOMAIN_PERSONAS["general"])
    clean_task = prompt.strip()
    return f"""<prompt_configuration>
  <role>
    {persona}
  </role>
  <domain_context>
    {domain}
  </domain_context>
  <task_instruction>
    {clean_task}
  </task_instruction>
  <constraints>
    <constraint>Maintain strict factual accuracy and avoid speculative claims.</constraint>
    <constraint>Format output in clean, structured Markdown or valid JSON where applicable.</constraint>
    <constraint>No conversational filler or unnecessary pleasantries.</constraint>
  </constraints>
  <output_format>
    Return structured, ready-to-use output adhering to the instructions above.
  </output_format>
</prompt_configuration>
"""


def build_cot_guided_prompt(prompt: str, domain: str) -> str:
    clean_task = prompt.strip()
    return f"""## Prompt Directive
{clean_task}

## Thinking & Reasoning Protocol
Before generating your final response, systematically work through the problem:
1. Deconstruct the prompt into atomic requirements.
2. Identify edge cases, boundary conditions, or domain-specific nuances in {domain}.
3. Draft the core response ensuring each requirement is addressed.
4. Review against all constraints and refine for clarity and conciseness.

## Final Output
Present your structured, final response below the reasoning steps.
"""


def build_few_shot_prompt(prompt: str, domain: str) -> str:
    clean_task = prompt.strip()
    return f"""## Task Description
{clean_task}

## Illustrative Demonstration (Few-Shot)
### Example 1
Input: "Summarize latency impact on microservice architecture"
Output:
- High latency cascades across downstream dependent services.
- Connection pool exhaustion can cause circuit breaker trips.
- Mitigate via caching, non-blocking I/O, and aggressive timeouts.

### Example 2
Input: "Explain principle of least privilege in role-based access control"
Output:
- Grant users only the minimum permissions necessary to perform authorized duties.
- Limits the attack blast radius in case of compromised credentials.
- Periodically audit access logs and revoke unneeded privileges.

## Your Execution
Apply the same direct, structured format shown above to the primary task.
"""


async def optimize_prompt(
    prompt: str,
    target_domain: str = "general",
    strategy: str = "structured",
    use_advisory_llm: bool = False,
) -> dict[str, Any]:
    strat = strategy.lower().strip()

    if strat == "role_expert":
        optimized = build_role_expert_prompt(prompt, target_domain)
    elif strat == "negative_constraints":
        optimized = build_negative_constraints_prompt(prompt, target_domain)
    elif strat == "xml_tagged":
        optimized = build_xml_tagged_prompt(prompt, target_domain)
    elif strat == "cot_guided":
        optimized = build_cot_guided_prompt(prompt, target_domain)
    elif strat == "few_shot":
        optimized = build_few_shot_prompt(prompt, target_domain)
    else:
        # Default structured strategy
        strat = "structured"
        optimized = build_structured_prompt(prompt, target_domain)

    # Score before and after using deterministic evaluator
    eval_before = evaluate_prompt_quality(prompt, target_domain)
    eval_after = evaluate_prompt_quality(optimized, target_domain)

    score_before = eval_before["overall_score"]
    score_after = eval_after["overall_score"]
    improvement_delta = round(score_after - score_before, 2)

    # Compute concise diff summary
    orig_lines = prompt.strip().splitlines()
    opt_lines = optimized.strip().splitlines()
    diff = list(difflib.unified_diff(orig_lines, opt_lines, lineterm=""))
    diff_summary = f"Added {len(opt_lines) - len(orig_lines)} structural lines across {strat} framework."

    advisory_notes = "Deterministic rule-based transformation applied."
    llm_used = False

    if use_advisory_llm:
        adapter = LLMAdapter()
        advisory_result = await adapter.generate_advisory_rewrite(prompt, target_domain)
        if advisory_result.get("available") and advisory_result.get("text"):
            advisory_notes = (
                f"[Advisory LLM Enhancement] {advisory_result.get('notes')}\n\n"
                f"Advisory Output:\n{advisory_result.get('text')}"
            )
            llm_used = True
        else:
            advisory_notes = f"[Advisory LLM Skipped] {advisory_result.get('notes')}"

    return {
        "original_prompt": prompt,
        "optimized_prompt": optimized,
        "strategy": strat,
        "target_domain": target_domain,
        "score_before": score_before,
        "score_after": score_after,
        "improvement_delta": improvement_delta,
        "diff_summary": diff_summary,
        "advisory_notes": advisory_notes,
        "llm_used": llm_used,
    }
