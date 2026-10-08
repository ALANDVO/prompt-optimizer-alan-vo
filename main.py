#!/usr/bin/env python3
"""prompt-optimizer-alan-vo CLI interface."""
import sys, os, json, argparse, asyncio
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from app.services.evaluator import evaluate_prompt_quality
from app.services.optimizer import optimize_prompt
from app.services.benchmark import run_model_benchmarking
from app.services.ab_test import run_ab_test_suite
from app.models.schemas import TestCaseSchema


def evaluate_cli(args):
    prompt, domain = args.prompt, getattr(args, "domain", "general") or "general"
    print(f"EVALUATING PROMPT: {prompt[:120]}\n" + "=" * 50)
    res = evaluate_prompt_quality(prompt, domain)
    for d in res["dimensions"]:
        print(f"  {d.dimension:<16} {d.rating:>8} ({d.score:.2f}) - {d.notes}")
    print(f"\nOVERALL: {res['overall_score']:.2f} | GRADE: {res['grade']}")
    if getattr(args, "score", False):
        report = {
            "prompt": prompt, "overall_score": res["overall_score"], "grade": res["grade"],
            "dimensions": [d.model_dump() for d in res["dimensions"]], "recommendations": res["recommendations"],
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(report, indent=2))


def optimize_cli(args):
    target = args.target or "general"
    strategy = getattr(args, "strategy", "structured") or "structured"
    res = asyncio.run(optimize_prompt(args.prompt, target, strategy, use_advisory_llm=False))
    print(f"=== OPTIMIZED ({strategy}) ===\n{res['optimized_prompt']}\n")
    print(f"DELTA: {res['score_before']:.2f} -> {res['score_after']:.2f} (+{res['improvement_delta']:.2f})")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"# Optimized\n\n## Original\n{args.prompt}\n\n## Result\n{res['optimized_prompt']}\n")


def benchmark_cli(args):
    prompt = args.prompt or "Validate email address format and return valid JSON."
    models = [m.strip() for m in args.models.split(",")]
    res = run_model_benchmarking(prompt, models)
    print(f"{'Model':<20} {'Quality':>8} {'Latency':>10} {'Tokens':>8}")
    for r in res["results"]:
        print(f"{r.model:<20} {r.overall_quality:>8.1f} {r.latency_seconds:>9.2f}s {r.estimated_tokens:>8}")
    print(f"\nBEST MODEL: {res['best_model']}")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"prompt": prompt, "best_model": res["best_model"], "results": [r.model_dump() for r in res["results"]]}, f, indent=2)


def ab_test_cli(args):
    with open(args.prompt_a, "r", encoding="utf-8") as f: pa = f.read()
    with open(args.prompt_b, "r", encoding="utf-8") as f: pb = f.read()
    with open(args.cases, "r", encoding="utf-8") as f: raw = json.load(f)
    cases = [TestCaseSchema(input=c.get("input", str(c)), expected=c.get("expected", ""), assertion_type=c.get("assertion_type", "contains")) for c in raw]
    res = run_ab_test_suite(pa, pb, cases)
    print(f"A/B RESULT: A={res['wins_a']} B={res['wins_b']} Ties={res['ties']} | WINNER: {res['winner']} ({res['confidence']:.2f})")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"winner": res["winner"], "wins_a": res["wins_a"], "wins_b": res["wins_b"], "confidence": res["confidence"]}, f, indent=2)


def main():
    p = argparse.ArgumentParser(prog="prompt-optimizer")
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("evaluate")
    e.add_argument("prompt")
    e.add_argument("--score", action="store_true")
    e.add_argument("--domain", default="general")
    e.set_defaults(fn=evaluate_cli)
    o = sub.add_parser("optimize")
    o.add_argument("prompt")
    o.add_argument("--target", default="general")
    o.add_argument("--strategy", default="structured")
    o.add_argument("--output", default=None)
    o.set_defaults(fn=optimize_cli)
    b = sub.add_parser("benchmark")
    b.add_argument("--prompt", default=None)
    b.add_argument("--models", default="gpt-4o-mini,claude-3-5-sonnet,gemini-1.5-pro,ollama-llama3")
    b.add_argument("--output", default=None)
    b.set_defaults(fn=benchmark_cli)
    a = sub.add_parser("ab-test")
    a.add_argument("--cases", required=True)
    a.add_argument("--prompt-a", required=True)
    a.add_argument("--prompt-b", required=True)
    a.add_argument("--output", default=None)
    a.set_defaults(fn=ab_test_cli)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
