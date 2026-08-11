import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    chroma_path: str = os.getenv("CHROMA_PATH", "./storage/chroma")
    collection_name: str = os.getenv("COLLECTION_NAME", "rag_chunks")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    relevance_threshold: float = float(os.getenv("RELEVANCE_THRESHOLD", "0.35"))
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "")
    judge_base_url: str = os.getenv("JUDGE_BASE_URL", "https://api.openai.com/v1")
    judge_api_key: str = os.getenv("JUDGE_API_KEY", "")
    judge_model: str = os.getenv("JUDGE_MODEL", "")
    generator_temperature: float = float(os.getenv("GENERATOR_TEMPERATURE", "0"))
    judge_temperature: float = float(os.getenv("JUDGE_TEMPERATURE", "0"))
    log_path: str = os.getenv("LOG_PATH", "./results/rag_queries.jsonl")

settings = Settings()
