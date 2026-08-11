# RAG Evaluation Notes

A fixed question set makes comparisons repeatable. Retrieval quality should be evaluated independently of answer quality.

Recall@k asks whether at least one relevant chunk appears in the top k results. MRR rewards a relevant result appearing early. nDCG@k rewards relevant results at higher ranks. Context precision measures how much of the retrieved top-k context is relevant according to the labeled relevant chunk set.

Latency is recorded separately for retrieval and generation. The service logs retrieval latency, generation latency, total latency, retrieved chunk count, and LLM token usage.

A good RAG system can still produce a poor answer if generation is weak. Conversely, a strong generator cannot recover information that retrieval failed to fetch. The evaluation therefore treats retrieval and generation as separate layers.
