import argparse
import json
import statistics
from pathlib import Path

from rag.pipeline import RAGPipeline
from rag.llm import LLMClient, parse_json_robust
from rag.config import settings

PROMPT = """You are evaluating a RAG answer.

Score:
1. faithfulness: Are the answer's claims supported by the supplied context?
2. answer_relevance: Does the answer directly answer the question?

Use 1-5:
1 = poor, 3 = acceptable/mixed, 5 = excellent.

Return ONLY JSON:
{
  "faithfulness": {"score": 1-5, "rationale": "..."},
  "answer_relevance": {"score": 1-5, "rationale": "..."}
}

Do not reward unsupported detail or verbosity.
"""

def evaluate_answer(client, question, answer, contexts):
    context = "\n\n".join(
        f"[{c['metadata']['source']}:{c['metadata']['chunk_index']}]\n{c['text']}"
        for c in contexts
    )
    response = client.chat([{
        "role": "user",
        "content": (
            PROMPT
            + f"\n\nQuestion:\n{question}"
            + f"\n\nAnswer:\n{answer}"
            + f"\n\nRetrieved context:\n{context}"
        )
    }], json_mode=True)
    data = parse_json_robust(response["text"])
    return data, response

def percentile(values, p):
    if not values:
        return 0.0
    values = sorted(values)
    idx = (len(values)-1) * p / 100
    lo = int(idx)
    hi = min(lo+1, len(values)-1)
    frac = idx-lo
    return values[lo]*(1-frac) + values[hi]*frac

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    if not settings.judge_api_key or not settings.judge_model:
        raise SystemExit(
            "Configure JUDGE_API_KEY and JUDGE_MODEL in .env before running "
            "answer evaluation."
        )

    questions = json.loads(
        Path("evaluation/rag_questions.json").read_text(encoding="utf-8")
    )
    pipeline = RAGPipeline()
    judge = LLMClient(
        settings.judge_base_url,
        settings.judge_api_key,
        settings.judge_model,
        settings.judge_temperature,
    )

    rows = []
    for q in questions:
        result = pipeline.answer(q["question"], k=args.k)
        data, raw = evaluate_answer(
            judge, q["question"], result["answer"], result["contexts"]
        )
        rows.append({
            "id": q["id"],
            "question": q["question"],
            "answer": result["answer"],
            "faithfulness": data["faithfulness"],
            "answer_relevance": data["answer_relevance"],
            "retrieval_latency_ms": result["retrieval_latency_ms"],
            "generation_latency_ms": result["generation_latency_ms"],
            "total_tokens": result["total_tokens"],
            "judge_tokens": raw["total_tokens"],
        })

    report = {
        "num_questions": len(rows),
        "mean_faithfulness": statistics.mean(
            r["faithfulness"]["score"] for r in rows
        ),
        "mean_answer_relevance": statistics.mean(
            r["answer_relevance"]["score"] for r in rows
        ),
        "latency_ms": {
            "retrieval_p50": percentile(
                [r["retrieval_latency_ms"] for r in rows], 50
            ),
            "retrieval_p95": percentile(
                [r["retrieval_latency_ms"] for r in rows], 95
            ),
            "total_p50": percentile(
                [r["retrieval_latency_ms"] + r["generation_latency_ms"] for r in rows], 50
            ),
            "total_p95": percentile(
                [r["retrieval_latency_ms"] + r["generation_latency_ms"] for r in rows], 95
            ),
        },
        "rows": rows,
        "judge_model": settings.judge_model,
    }

    Path("results").mkdir(exist_ok=True)
    Path("results/rag_answer_eval.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "mean_faithfulness": report["mean_faithfulness"],
        "mean_answer_relevance": report["mean_answer_relevance"],
        "latency_ms": report["latency_ms"],
    }, indent=2))

if __name__ == "__main__":
    main()
