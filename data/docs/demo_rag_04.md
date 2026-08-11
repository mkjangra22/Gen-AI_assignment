# Demo RAG 04

The generation prompt requires the model to answer only from retrieved context and cite the exact source and chunk index. When no retrieved result passes the relevance threshold, the system returns an insufficient-context response instead of asking the model to guess. A citation identifies the source and chunk used to support the answer.
