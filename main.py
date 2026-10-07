#!/usr/bin/env python3
# prompt-optimizer — AI-powered prompt engineering tool that evaluates raw prompts, rewrites them for clarity and specificity, benchmarks across models, and generates A/B test harnesses for systematic prompt improvement.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_client import LLM
def evaluate(args):
    """Score a prompt across quality dimensions."""
    llm = LLM()
    prompt = args.prompt
    print(f"{'='*60}")
    print(f"EVALUATING PROMPT")
    print(f"{'='*60}")
    print(f"Prompt: {prompt[:200]}")
    print(f"{'='*60}\n")

    dimensions = [
        ("clarity", "Is the intent unambiguous? Could it be interpreted multiple ways?"),
        ("specificity", "Does it specify expected output format, length, and constraints?"),
        ("structure", "Is it well-organized with clear sections or logical flow?"),
        ("context", "Does it provide sufficient domain context for the LLM?"),
        ("constraints", "Are there explicit constraints on what NOT to do?"),
        ("output_spec", "Is the desired output format precisely specified?"),
        ("examples", "Does it include few-shot examples or reference outputs?"),
        ("role", "Does it assign a clear expert role to the LLM?"),
    ]

    scores = []
    for dim, question in dimensions:
        result = llm.classify(
            text=f"Prompt: {prompt}\n\nEvaluation question: {question}",
            categories=["strong", "adequate", "weak", "missing"],
            instructions=f"Rate this prompt on the dimension: {dim}. {question} Be strict — a score of 'strong' means production-ready quality."
        )
        score_map = {"strong": 1.0, "adequate": 0.6, "weak": 0.3, "missing": 0.0, "unknown": 0.0}
        score = score_map.get(result.get("category", "unknown"), 0.0)
        scores.append({"dimension": dim, "score": score, "rating": result.get("category", "unknown"), "notes": result.get("reasoning", "")[:200]})
        print(f"  {dim:<15} {result.get('category', 'unknown'):>10}  ({score:.2f})")

    total = sum(s["score"] for s in scores) / len(scores)
    print(f"\n{'='*60}")
    print(f"OVERALL SCORE: {total:.2f} / 1.00")
    grade = "A" if total >= 0.8 else "B" if total >= 0.6 else "C" if total >= 0.4 else "D"
    print(f"GRADE: {grade}")

    weak = [s for s in scores if s["score"] < 0.5]
    if weak:
        print(f"\nWEAK AREAS ({len(weak)}):")
        for w in weak:
            print(f"  - {w['dimension']}: {w['notes']}")

    if args.score:
        report = {"prompt": prompt, "scores": scores, "total": round(total, 3), "grade": grade, "evaluated_at": datetime.now().isoformat()}
        print(f"\nJSON report: {json.dumps(report, indent=2)}")
    return scores, total

def optimize(args):
    """Rewrite a prompt for maximum effectiveness."""
    llm = LLM()
    prompt = args.prompt
    target = args.target or "general"
    print(f"Optimizing prompt for: {target}")

    optimized = llm.generate(
        f"Original prompt: {prompt}\n\nTarget domain: {target}\n\n"
        "Rewrite this prompt to be maximally effective. Apply these principles:\n"
        "1. Assign a specific expert role\n"
        "2. Add explicit output format specification\n"
        "3. Include 2-3 few-shot examples if helpful\n"
        "4. Add constraints (what NOT to do)\n"
        "5. Structure with clear sections\n"
        "6. Make it specific — replace vague words with precise instructions\n\n"
        "Return ONLY the optimized prompt, no explanations.",
        system="You are a prompt engineering expert with 5+ years of LLM fine-tuning and prompt design experience. You produce prompts that consistently outperform the original by 30%+ in quality metrics."
    )

    print(f"\n{'='*60}")
    print(f"BEFORE")
    print(f"{'='*60}")
    print(prompt)
    print(f"\n{'='*60}")
    print(f"AFTER (optimized)")
    print(f"{'='*60}")
    print(optimized)

    comparison = llm.generate(
        f"Original: {prompt}\n\nOptimized: {optimized}\n\n"
        "Explain in 5 bullet points what specific improvements were made and why each one matters for LLM performance.",
        system="Be specific. Reference exact words/phrases that changed."
    )
    print(f"\nIMPROVEMENTS:")
    print(comparison)

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"# Optimized Prompt\n\n## Original\n{prompt}\n\n## Optimized\n{optimized}\n\n## Changes\n{comparison}\n")
        print(f"\nSaved to {args.output}")
    return optimized

def benchmark(args):
    """Benchmark a prompt across multiple models."""
    llm = LLM()
    prompt = args.prompt or (open(args.prompt_file).read() if args.prompt_file else "Write a function to validate email addresses")
    models = [m.strip() for m in args.models.split(",")]

    print(f"{'='*60}")
    print(f"BENCHMARKING across {len(models)} model(s)")
    print(f"{'='*60}")
    print(f"Prompt: {prompt[:100]}...\n")

    results = []
    for model in models:
        print(f"  Testing {model}...", end=" ", flush=True)
        start = time.time()
        try:
            llm.model = model
            response = llm.generate(prompt, system="You are a helpful assistant. Respond concisely.")
            elapsed = time.time() - start
            tokens_est = len(response) // 4
            result = {"model": model, "response": response[:500], "time": round(elapsed, 2), "tokens_est": tokens_est, "status": "ok"}
            print(f"OK ({elapsed:.1f}s, ~{tokens_est} tokens)")
        except Exception as e:
            elapsed = time.time() - start
            result = {"model": model, "response": "", "time": round(elapsed, 2), "tokens_est": 0, "status": f"error: {str(e)[:80]}"}
            print(f"FAIL ({str(e)[:50]})")
        results.append(result)

    # Score quality
    print(f"\nScoring responses...")
    quality = []
    for r in results:
        if r["status"] != "ok":
            quality.append({"model": r["model"], "quality": 0.0, "reason": "execution failed"})
            continue
        score = llm.classify(
            text=f"Prompt: {prompt}\n\nResponse: {r['response']}\n\nRate the quality of this response on a scale of 0-10. Consider: correctness, completeness, clarity, and usefulness.",
            categories=["excellent", "good", "adequate", "poor", "terrible"],
            instructions="Rate the response quality relative to the prompt requirements."
        )
        q_map = {"excellent": 10, "good": 7.5, "adequate": 5, "poor": 2.5, "terrible": 1}
        quality.append({"model": r["model"], "quality": q_map.get(score.get("category", "poor"), 3), "reason": score.get("reasoning", "")[:100]})

    # Report
    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"{'Model':<25} {'Quality':>8} {'Time':>8} {'Tokens':>8}  {'Status'}")
    print(f"{'-'*70}")
    for q in quality:
        r = next((x for x in results if x["model"] == q["model"]), {})
        print(f"{q['model']:<25} {q['quality']:>8.1f} {r.get('time',0):>7.1f}s {r.get('tokens_est',0):>8}  {r.get('status','?')}")

    if args.output:
        report = {"prompt": prompt, "results": results, "quality": quality, "benchmarked_at": datetime.now().isoformat()}
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to {args.output}")
    return results, quality

def ab_test(args):
    """Run A/B test between two prompt versions."""
    llm = LLM()
    with open(args.prompt_a) as f: prompt_a = f.read()
    with open(args.prompt_b) as f: prompt_b = f.read()
    with open(args.cases) as f: cases = json.load(f)

    print(f"A/B Test: {len(cases)} test cases")
    print(f"  A: {args.prompt_a} ({len(prompt_a)} chars)")
    print(f"  B: {args.prompt_b} ({len(prompt_b)} chars)\n")

    wins = {"a": 0, "b": 0, "tie": 0}
    details = []
    for i, case in enumerate(cases):
        input_data = case.get("input", case.get("prompt", str(case)))
        expected = case.get("expected", "")

        try:
            resp_a = llm.generate(input_data, system=prompt_a)
        except: resp_a = ""
        try:
            resp_b = llm.generate(input_data, system=prompt_b)
        except: resp_b = ""

        judge = llm.classify(
            text=f"Task: {input_data[:300]}\n\nExpected: {expected[:200]}\n\nResponse A: {resp_a[:500]}\n\nResponse B: {resp_b[:500]}\n\nWhich response better satisfies the task and matches the expected output?",
            categories=["A_better", "B_better", "tie"],
            instructions="Judge purely on task completion quality. If both are equally good or equally bad, say tie."
        )
        cat = judge.get("category", "tie")
        if cat == "A_better": wins["a"] += 1
        elif cat == "B_better": wins["b"] += 1
        else: wins["tie"] += 1
        print(f"  [{i+1}/{len(cases)}] {cat}")
        details.append({"case": i, "winner": cat, "reasoning": judge.get("reasoning", "")[:100]})

    total = len(cases)
    print(f"\n{'='*60}")
    print(f"A/B RESULTS: A={wins['a']} B={wins['b']} Tie={wins['tie']} (of {total})")
    winner = "A" if wins["a"] > wins["b"] else "B" if wins["b"] > wins["a"] else "TIE"
    print(f"WINNER: {winner}")
    print(f"{'='*60}")

    if args.output:
        report = {"wins": wins, "details": details, "total": total, "winner": winner, "date": datetime.now().isoformat()}
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nSaved to {args.output}")
    return wins

def library(args):
    """Manage a prompt template library."""
    lib_path = args.path or os.path.join(os.path.dirname(__file__), "prompt_library.json")
    if args.action == "add" and args.prompt:
        lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {}
        lib[args.name] = {"prompt": args.prompt, "created": datetime.now().isoformat(), "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()]}
        with open(lib_path, "w") as f: json.dump(lib, f, indent=2)
        print(f"Added '{args.name}' to library ({len(lib)} prompts total)")
    elif args.action == "list":
        lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {}
        print(f"Prompt Library ({len(lib)} prompts)")
        for name, entry in sorted(lib.items()):
            tags = " ".join(entry.get("tags", []))
            print(f"  {name:<30} {entry.get('created','')[:10]}  [{tags}]  {entry['prompt'][:60]}...")
    elif args.action == "get" and args.name:
        lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {}
        if args.name in lib: print(lib[args.name]["prompt"])
        else: print(f"Prompt '{args.name}' not found")
    elif args.action == "remove" and args.name:
        lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {}
        if args.name in lib:
            del lib[args.name]
            with open(lib_path, "w") as f: json.dump(lib, f, indent=2)
            print(f"Removed '{args.name}'")
    return None

def main():
    import argparse
    p = argparse.ArgumentParser(prog="prompt-optimizer", description="AI-powered prompt engineering tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("evaluate", help="Score a prompt on quality dimensions")
    e.add_argument("prompt"); e.add_argument("--score", action="store_true")
    e.set_defaults(fn=evaluate)

    o = sub.add_parser("optimize", help="Rewrite a prompt for maximum effectiveness")
    o.add_argument("prompt"); o.add_argument("--target", default=None); o.add_argument("--output", default=None)
    o.set_defaults(fn=optimize)

    b = sub.add_parser("benchmark", help="Benchmark across multiple models")
    b.add_argument("--prompt", default=None); b.add_argument("--prompt-file", default=None)
    b.add_argument("--models", default="gpt-4o"); b.add_argument("--output", default=None)
    b.set_defaults(fn=benchmark)

    a = sub.add_parser("ab-test", help="A/B test between two prompt versions")
    a.add_argument("--cases", required=True); a.add_argument("--prompt-a", required=True)
    a.add_argument("--prompt-b", required=True); a.add_argument("--output", default=None)
    a.set_defaults(fn=ab_test)

    l = sub.add_parser("library", help="Manage prompt template library")
    l.add_argument("--action", choices=["add", "list", "get", "remove"], default="list")
    l.add_argument("--name", default=None); l.add_argument("--prompt", default=None)
    l.add_argument("--tags", default=None); l.add_argument("--path", default=None)
    l.set_defaults(fn=library)

    args = p.parse_args()
    args.fn(args)

if __name__ == '__main__':
    main()
