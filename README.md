# Applied AI / ML Engineering — Take-Home Assignment

1. **Cost-Efficient RAG Application**
2. **LLM-as-Judge Evaluation Pipeline**

> Assignment source: `Gen AI_assignment.pdf`

## Architecture

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
