# Demo RAG 02

Idempotent ingestion means re-ingesting an unchanged source produces the same deterministic records instead of duplicate vectors. The default chunk size is 800 characters with 120 characters of overlap. Deterministic chunk IDs are derived from document identity, chunk position, and chunk text, and the vector store uses upsert semantics.
