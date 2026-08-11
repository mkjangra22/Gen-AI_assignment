# Cost-Efficient RAG Design

## Low-cost vector store

An embedded low-cost vector store is useful when an index is large but lightly queried because the application can avoid paying for dedicated always-on vector database infrastructure. The main operational advantage is simple deployment: the index can live with the application rather than requiring a separate database service.

The trade-off is that a single embedded process is not the best architecture for high-QPS, multi-region, or high-availability requirements.

## Ingestion and idempotency

The ingestion pipeline uses deterministic document and chunk identifiers. A chunk ID is derived from the document identity, chunk position, and chunk text. The vector store uses upsert semantics. Re-ingesting an unchanged document therefore updates the existing record instead of creating another vector.

The default chunk size is 800 characters with 120 characters of overlap.

## Metadata

Each vector stores metadata including document_id, source, chunk_index, and file_type. Retrieval can optionally filter by source metadata.

## Grounded answers

The generation prompt instructs the model to answer only from retrieved context and cite the exact source and chunk index. If no retrieved result passes the relevance threshold, the system returns an insufficient-context response instead of asking the model to guess.

## Evaluation

The retrieval evaluation uses a fixed set of 15 questions. It computes Recall@k, Hit Rate@k, MRR, nDCG@k, and context precision. Retrieval latency is measured per query and summarized with p50 and p95.

Answer quality is evaluated separately with an LLM judge for faithfulness/groundedness and answer relevance. Keeping retrieval and generation evaluation separate makes it possible to determine which layer is the weak link.

## Cost

The default embedding model runs locally, so embedding API spend is zero. The main variable GenAI cost is generation.

For a managed comparison, the assignment uses a clearly stated pricing assumption rather than pretending there is a single universal price. Actual managed vector database cost depends on vector count, dimensions, metadata, read/write volume, region and service tier.

## Switching back to managed

A managed service becomes more attractive when availability, concurrency, multi-region operation, automated backups, or operational burden outweigh the cost savings of the embedded design.
