import json
import time
from pathlib import Path

from .config import settings
from .store import VectorStore
from .llm import LLMClient

SYSTEM_PROMPT = """You are a grounded retrieval-augmented QA assistant.
Answer only from the supplied context.
Every factual claim must be supported by one or more context citations.
Citations must use the exact format [source:chunk_index].
If the context is insufficient, say that the available documents do not contain enough information.
Do not invent facts, sources, citations, or URLs.
"""

class RAGPipeline:
    def __init__(self):
        self.store = VectorStore()
        self.llm = LLMClient(
            settings.llm_base_url,
            settings.llm_api_key,
            settings.llm_model,
            settings.generator_temperature,
        )

    def retrieve(self, question, k=None, source=None):
        k = k or settings.top_k
        started = time.perf_counter()
        result = self.store.search(question, k=k, source=source)
        latency_ms = (time.perf_counter() - started) * 1000

        docs = result.get("documents", [[]])[0]
        ids = result.get("ids", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        contexts = []
        for doc_id, text, meta, distance in zip(ids, docs, metas, distances):
            # Chroma cosine distance: lower is more similar.
            similarity = 1.0 - float(distance)
            contexts.append({
                "id": doc_id,
                "text": text,
                "metadata": meta,
                "distance": float(distance),
                "similarity": similarity,
            })

        return contexts, latency_ms

    def answer(self, question, k=None, source=None):
        contexts, retrieval_ms = self.retrieve(question, k, source)

        relevant = [
            c for c in contexts
            if c["similarity"] >= settings.relevance_threshold
        ]

        if not relevant:
            answer = (
                "I don't have enough relevant context in the indexed documents "
                "to answer this question reliably."
            )
            result = {
                "question": question,
                "answer": answer,
                "citations": [],
                "contexts": contexts,
                "retrieved_chunk_count": len(contexts),
                "retrieval_latency_ms": retrieval_ms,
                "generation_latency_ms": 0,
                "total_latency_ms": retrieval_ms,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }
            self._log(result)
            return result

        context_text = "\n\n".join(
            f"[{c['metadata']['source']}:{c['metadata']['chunk_index']}]\n{c['text']}"
            for c in relevant
        )

        response = self.llm.chat([
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\n"
                    f"Context:\n{context_text}\n\n"
                    "Return a concise, grounded answer with inline citations."
                ),
            },
        ])

        result = {
            "question": question,
            "answer": response["text"],
            "citations": [
                f"{c['metadata']['source']}:{c['metadata']['chunk_index']}"
                for c in relevant
            ],
            "contexts": contexts,
            "retrieved_chunk_count": len(contexts),
            "retrieval_latency_ms": retrieval_ms,
            "generation_latency_ms": response["latency_ms"],
            "total_latency_ms": retrieval_ms + response["latency_ms"],
            "prompt_tokens": response["prompt_tokens"],
            "completion_tokens": response["completion_tokens"],
            "total_tokens": response["total_tokens"],
        }
        self._log(result)
        return result

    def _log(self, record):
        path = Path(settings.log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
