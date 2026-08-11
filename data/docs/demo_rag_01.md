# Demo RAG 01

An embedded low-cost vector store is useful when an index is large but lightly queried because the application can avoid paying for dedicated always-on vector database infrastructure. The main operational advantage is simple deployment because the index can live with the application rather than requiring a separate database service. A trade-off is that a single embedded process is not the best architecture for high-QPS, multi-region, or high-availability requirements.
