import argparse
import json
import math
import statistics
from pathlib import Path

from rag.pipeline import RAGPipeline

def recall_at_k(retrieved, relevant, k):
    return 1.0 if set(retrieved[:k]) & set(relevant) else 0.0

def hit_rate_at_k(retrieved, relevant, k):
    return recall_at_k(retrieved, relevant, k)

def reciprocal_rank(retrieved, relevant):
    relevant = set(relevant)
    for i, item in enumerate(retrieved, 1):
        if item in relevant:
            return 1.0 / i
    return 0.0

def dcg(retrieved, relevant, k):
    relevant = set(relevant)
    score = 0.0
    for i, item in enumerate(retrieved[:k], 1):
        rel = 1 if item in relevant else 0
        score += rel / math.log2(i + 1)
    return score

def ndcg_at_k(retrieved, relevant, k):
    ideal = min(k, len(set(relevant)))
    if ideal == 0:
        return 0.0
    ideal_dcg = sum(1 / math.log2(i + 1) for i in range(1, ideal + 1))
    return dcg(retrieved, relevant, k) / ideal_dcg

def context_precision(retrieved, relevant, k):
    relevant = set(relevant)
    top = retrieved[:k]
    if not top:
        return 0.0
    return sum(x in relevant for x in top) / len(top)

def run(k=5):
    questions = json.loads(
        Path("evaluation/rag_questions.json").read_text(encoding="utf-8")
    )
    pipeline = RAGPipeline()

    rows = []
    for q in questions:
        contexts, retrieval_ms = pipeline.retrieve(q["question"], k=k)
        ids = [c["id"] for c in contexts]

        rows.append({
            "id": q["id"],
            "question": q["question"],
            "relevant": q["relevant_chunk_ids"],
            "retrieved": ids,
            "recall_at_k": recall_at_k(ids, q["relevant_chunk_ids"], k),
            "hit_rate_at_k": hit_rate_at_k(ids, q["relevant_chunk_ids"], k),
            "mrr": reciprocal_rank(ids, q["relevant_chunk_ids"]),
            "ndcg_at_k": ndcg_at_k(ids, q["relevant_chunk_ids"], k),
            "context_precision": context_precision(ids, q["relevant_chunk_ids"], k),
            "retrieval_latency_ms": retrieval_ms,
        })

    report = {
        "k": k,
        "num_questions": len(rows),
        "metrics": {
            name: statistics.mean(r[name] for r in rows)
            for name in [
                "recall_at_k",
                "hit_rate_at_k",
                "mrr",
                "ndcg_at_k",
                "context_precision",
            ]
        },
        "latency_ms": {
            "p50": percentile([r["retrieval_latency_ms"] for r in rows], 50),
            "p95": percentile([r["retrieval_latency_ms"] for r in rows], 95),
        },
        "rows": rows,
        "answer_evaluation": {
            "status": "run separately with judge when JUDGE_API_KEY/JUDGE_MODEL are configured"
        },
    }

    Path("results").mkdir(exist_ok=True)
    Path("results/rag_eval.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report["metrics"], indent=2))
    print(json.dumps(report["latency_ms"], indent=2))

def percentile(values, p):
    if not values:
        return 0.0
    values = sorted(values)
    idx = (len(values) - 1) * p / 100
    lo = int(idx)
    hi = min(lo + 1, len(values) - 1)
    frac = idx - lo
    return values[lo] * (1 - frac) + values[hi] * frac

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    run(args.k)
