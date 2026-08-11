# Applied AI / ML Engineering — Take-Home Assignment

Problem 1: **Cost-Efficient RAG Application**
Problem 2: **LLM-as-Judge Evaluation Pipeline**

> Assignment source: `Gen AI_assignment.pdf`
> Assignment Submission: `Assignment Submission-Applied AIML Engineering.pdf`


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



                    GEN AI ASSIGNMENT
                           │
              ┌────────────┴────────────┐
              │                         │
         PROBLEM 1                 PROBLEM 2
              │                         │
        RAG Evaluation          Judge Evaluation
              │                         │
       ┌──────┴──────┐             A vs B
       │             │             B vs A
   Retrieval      Generation          │
       │             │                ↓
   ChromaDB       Llama          Judge Model
       │             │                │
       └──────┬──────┘                ↓
              ↓                 Bias Analysis
        DeepSeek Judge
               │
       Faithfulness
       Relevance
```
