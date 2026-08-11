from fastapi import FastAPI
from pydantic import BaseModel, Field

from .pipeline import RAGPipeline

app = FastAPI(title="Cost-Efficient RAG API", version="1.0.0")
pipeline = RAGPipeline()

class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    source: str | None = None

@app.get("/health")
def health():
    return {
        "status": "ok",
        "vectors": pipeline.store.count(),
        "embedding_dimension": pipeline.store.dimension,
    }

@app.post("/query")
def query(request: QueryRequest):
    return pipeline.answer(
        request.question,
        k=request.top_k,
        source=request.source,
    )
