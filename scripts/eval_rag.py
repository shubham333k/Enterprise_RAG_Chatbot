"""
RAG Evaluation Script
Measures: retrieval precision@k, citation correctness, no-answer rate, latency.

Usage:
    python scripts/eval_rag.py
    python scripts/eval_rag.py --role hr --top_k 5
"""
import sys
import os
import time
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.pipelines.query_pipeline import run_query_pipeline

# ─── Evaluation Dataset ───────────────────────────────────────────────────────
# Format: question, expected_doc (partial match), expected_answer_contains
EVAL_DATASET = [
    {
        "question": "What is the maternity leave policy?",
        "expected_doc": "hr_policy",
        "expected_answer_contains": ["maternity", "leave"],
        "role": "hr",
    },
    {
        "question": "What are the code review requirements?",
        "expected_doc": "engineering",
        "expected_answer_contains": ["review", "code"],
        "role": "engineering",
    },
    {
        "question": "What is the sales commission structure?",
        "expected_doc": "sales",
        "expected_answer_contains": ["commission", "sales"],
        "role": "sales",
    },
    {
        "question": "What are the company values?",
        "expected_doc": None,  # could be in public docs
        "expected_answer_contains": ["value"],
        "role": "employee",
    },
    {
        "question": "What is the quantum entanglement policy?",  # expects no-answer
        "expected_doc": None,
        "expected_answer_contains": ["not found"],
        "role": "employee",
    },
]


def evaluate(role: str = None, top_k: int = 5):
    print("\n🔬 RAG Evaluation Report")
    print("═" * 60)

    results = []
    total_latency = 0
    no_answer_count = 0
    correct_citations = 0

    for i, item in enumerate(EVAL_DATASET):
        q_role = role or item["role"]
        print(f"\n[{i+1}/{len(EVAL_DATASET)}] Q: {item['question']}")
        print(f"       Role: {q_role}")

        start = time.time()
        result = run_query_pipeline(
            question=item["question"],
            user_role=q_role,
            top_k=top_k,
        )
        latency = int((time.time() - start) * 1000)
        total_latency += latency

        answer = result.get("answer", "")
        citations = result.get("citations", [])
        has_answer = result.get("has_answer", False)

        if not has_answer:
            no_answer_count += 1

        # Check citation quality
        citation_correct = False
        if item["expected_doc"]:
            for c in citations:
                if item["expected_doc"].lower() in c.get("document", "").lower():
                    citation_correct = True
                    break
            if citation_correct:
                correct_citations += 1
        else:
            correct_citations += 1  # no doc expected

        # Check answer contains expected keywords
        answer_lower = answer.lower()
        keyword_hits = sum(1 for kw in item["expected_answer_contains"] if kw in answer_lower)
        keyword_rate = keyword_hits / max(len(item["expected_answer_contains"]), 1)

        # Print result
        status = "✅" if keyword_rate >= 0.5 else "⚠️"
        print(f"  {status} Answer: {answer[:100]}...")
        print(f"     Citations: {len(citations)} | Latency: {latency}ms | Keywords: {keyword_rate:.0%}")
        if citations:
            print(f"     Top source: {citations[0].get('document', 'N/A')} (score: {citations[0].get('score', 0):.2f})")

        results.append({
            "question": item["question"],
            "role": q_role,
            "has_answer": has_answer,
            "citation_correct": citation_correct,
            "keyword_rate": keyword_rate,
            "latency_ms": latency,
            "sources_found": len(citations),
        })

    # ─── Summary ──────────────────────────────────────────────────────────────
    n = len(EVAL_DATASET)
    avg_latency = total_latency / n
    no_answer_rate = no_answer_count / n * 100
    citation_accuracy = correct_citations / n * 100
    avg_keyword = sum(r["keyword_rate"] for r in results) / n * 100

    print("\n" + "═" * 60)
    print("📊 EVALUATION SUMMARY")
    print("─" * 60)
    print(f"  Total questions:      {n}")
    print(f"  Avg latency:          {avg_latency:.0f}ms")
    print(f"  No-answer rate:       {no_answer_rate:.0f}%")
    print(f"  Citation accuracy:    {citation_accuracy:.0f}%")
    print(f"  Answer keyword match: {avg_keyword:.0f}%")
    print("═" * 60)

    # Save JSON report
    report = {
        "summary": {
            "total_questions": n,
            "avg_latency_ms": round(avg_latency, 1),
            "no_answer_rate_pct": round(no_answer_rate, 1),
            "citation_accuracy_pct": round(citation_accuracy, 1),
            "avg_keyword_match_pct": round(avg_keyword, 1),
        },
        "results": results,
    }
    report_path = "data/eval_report.json"
    os.makedirs("data", exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Full report saved to: {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RAG system quality")
    parser.add_argument("--role", default=None, help="Override role for all questions")
    parser.add_argument("--top_k", type=int, default=5, help="Number of chunks to retrieve")
    args = parser.parse_args()
    evaluate(role=args.role, top_k=args.top_k)
