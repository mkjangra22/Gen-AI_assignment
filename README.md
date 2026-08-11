# Applied AI / ML Engineering — Take-Home Assignment

This repository implements **both problems** from the assignment:

1. **Cost-Efficient RAG Application**
2. **LLM-as-Judge Evaluation Pipeline**

The implementation is intentionally designed to be runnable in a ~10-hour take-home window, while still exposing the evaluation, cost, latency, logging, and bias-analysis layers requested by the brief.

> Assignment source: `Gen AI_assignment.pdf`

## 1. Architecture

```text
                         ┌──────────────────────┐
 PDF / HTML / MD ───────►│  Ingestion + Chunker │
                         └──────────┬───────────┘
                                    │
                         deterministic chunk IDs
                                    │
                         ┌──────────▼───────────┐
                         │ SentenceTransformer  │
                         │ 384-d local vectors  │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ ChromaDB Persistent   │
                         │ vector + metadata     │
                         └──────────┬───────────┘
                                    │ top-k + filter
                                    ▼
                              Grounded context
                                    │
                         ┌──────────▼───────────┐
                         │ OpenAI-compatible LLM│
                         └──────────┬───────────┘
                                    │
                              cited answer
                                    │
                         ┌──────────▼───────────┐
                         │ FastAPI /query       │
                         │ latency/token logs   │
                         └──────────────────────┘
```

### Why ChromaDB?

I chose **ChromaDB in persistent embedded mode** because it removes the need for a separate vector database server during a small/medium workload. It supports vector similarity search, metadata filtering and deterministic IDs/upserts, while keeping the deployment simple.

The trade-off is that a single embedded process is not the right choice for every high-QPS or highly available production workload. At that point I would move to a managed vector service or a horizontally deployed database.

### Embedding model

Default:

- `sentence-transformers/all-MiniLM-L6-v2`
- 384 dimensions
- local inference, so no embedding API bill
- cosine similarity through Chroma's default distance behavior

Change it with `EMBEDDING_MODEL`.

### Chunking defaults

- chunk size: **800 characters**
- overlap: **120 characters**
- chunk IDs are deterministic: `sha256(document_id + chunk_index + chunk_text)`

Re-ingestion therefore uses the same IDs and `upsert`, preventing duplicate vectors.

---

# Problem 1 — RAG

## Run locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

copy .env.example .env
# edit .env and add an LLM API key if using a hosted model
```

Ingest the included demo corpus:

```bash
python -m rag.ingest --path data/docs
```

Start the service:

```bash
uvicorn rag.api:app --reload
```

Query:

```bash
curl -X POST http://127.0.0.1:8000/query ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is the purpose of the retrieval layer?\",\"top_k\":4}"
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### Environment

See `.env.example`.

Important settings:

```text
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=...
LLM_MODEL=...
JUDGE_BASE_URL=...
JUDGE_API_KEY=...
JUDGE_MODEL=...
```

The generator and judge are deliberately configurable independently.

---

# Problem 1 evaluation

The fixed evaluation set contains **15 questions** and explicit relevant chunk IDs.

Run:

```bash
python -m evaluation.rag_eval --k 5
```

It produces:

```text
results/rag_eval.json
```

The harness computes:

- Recall@k
- Hit Rate@k
- MRR
- nDCG@k
- context precision
- answer faithfulness / groundedness
- answer relevance
- p50/p95 retrieval latency
- token usage

The retrieval metrics are computed from the explicit relevant chunk IDs in `evaluation/rag_questions.json`.

LLM answer metrics use the judge configuration. If no judge API key is available, the retrieval portion still runs and the report clearly records that answer judging was skipped rather than inventing a score.

---

# Problem 1 cost comparison

Run:

```bash
python -m evaluation.cost_model
```

This writes:

```text
results/cost_comparison.csv
```

The calculation intentionally separates:

1. vector storage
2. vector DB operations
3. LLM generation
4. embeddings

The default embedding model is local, so its API cost is `$0`.

For the managed comparison, the README uses **Pinecone's current public plan structure as an external reference**, but the exact workload cost must be recomputed for the selected dimensions, metadata, query volume and region. The assignment asks for stated assumptions, so the generated table labels assumptions explicitly rather than pretending a universal managed-DB price exists.

Current Pinecone pricing reference:
https://www.pinecone.io/pricing/

---

# Problem 2 — LLM-as-Judge

The pipeline supports **pairwise A-vs-B judging**, which is a good fit for deciding between prompt/model configurations.

Input:

```text
evaluation/judge_suite.json
```

Run:

```bash
python -m judge.run
```

Output:

```text
results/judge_report.json
results/judge_raw.jsonl
results/judge_validation.json
```

The rubric scores:

- correctness
- faithfulness
- completeness
- instruction following
- tone
- safety

Each criterion contains:

- score
- rationale
- evidence

The judge returns structured JSON. Malformed output is handled by:

1. extracting a JSON object from surrounding text
2. validating against a schema
3. retrying once with a stricter repair prompt
4. recording failures in the audit log

## Bias handling

### Position bias

Every A/B case is judged twice:

```text
case: A vs B
case: B vs A
```

The report contains:

- original winner
- reversed-order winner
- final winner
- position flip rate
- agreement rate

### Verbosity bias

The rubric explicitly requires correctness and evidence rather than rewarding length.

The suite includes a `verbose_but_wrong` adversarial probe. A long answer with incorrect claims should lose to a concise correct answer.

### Self-enhancement bias

Use a judge from a different model family than the generator:

```text
LLM_MODEL=generator-model
JUDGE_MODEL=different-family-model
```

The report records the configured generator and judge model IDs.

### Sycophancy/style bias

The adversarial suite includes confidently wrong outputs. The judge is required to ground each criterion in the reference/evidence rather than rewarding confidence or stylistic polish.

### Score clustering

The rubric has anchored descriptions for 1/3/5. Pairwise judging is the primary decision mechanism, reducing dependence on an absolute score scale.

---

# Judge validation

`evaluation/judge_validation.json` contains:

- gold labels
- adversarial probes
- expected preferred answer

The pipeline reports:

- agreement rate with gold labels
- Cohen's kappa when possible
- adversarial accuracy
- position flip rate

For a production release gate, I would also run the suite multiple times with a fixed temperature and monitor test-retest consistency over time.

---

# Example results

The repository does **not fabricate evaluation results**. Run the commands above to populate `results/`.

This is important because latency, token usage and LLM-as-judge scores depend on the machine, model, network and API configuration.

---

# Engineering decisions / trade-offs

## Retrieval vs generation

The evaluation separates the two layers.

If retrieval metrics are strong but answer faithfulness/relevance is weak, generation/prompting is the weak link.

If retrieval recall/precision is weak, changing the generator alone is unlikely to fix the system.

## When would I switch back to managed?

I would switch when one or more of these become important:

- high concurrent QPS
- multi-region availability
- automated backups/HA
- strict operational SLAs
- large multi-tenant datasets
- operational cost of maintaining the local store exceeds managed pricing
- need for built-in distributed scaling

The embedded store wins primarily when the index is large but lightly queried and operational simplicity matters.

---

# Suggested 10-hour execution plan

| Time | Work |
|---|---|
| 0:00–0:45 | Read brief, choose ChromaDB, configure environment |
| 0:45–2:15 | Ingestion + chunking + deterministic IDs |
| 2:15–3:15 | Embeddings + vector store + metadata filter |
| 3:15–4:15 | RAG endpoint + grounded citations + no-context behavior |
| 4:15–5:15 | 15-question retrieval evaluation |
| 5:15–6:00 | Latency/cost model + README |
| 6:00–7:30 | LLM judge + structured parsing |
| 7:30–8:30 | A/B pairwise + position reversal |
| 8:30–9:15 | Bias probes + validation |
| 9:15–10:00 | Run tests, collect results, clean Git history |

#   G e n - A I _ a s s i g n m e n t  
 