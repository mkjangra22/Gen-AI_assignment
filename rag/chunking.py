from dataclasses import dataclass
import hashlib
from pathlib import Path

@dataclass
class Chunk:
    id: str
    document_id: str
    source: str
    chunk_index: int
    text: str
    metadata: dict

def deterministic_document_id(source: str, text: str) -> str:
    source = Path(source).as_posix()
    return hashlib.sha256((source + "\n" + text).encode("utf-8")).hexdigest()[:20]

def chunk_text(text: str, source: str, chunk_size: int = 800, overlap: int = 120):
    source = Path(source).as_posix()
    text = " ".join(text.split())
    if not text:
        return []

    document_id = deterministic_document_id(source, text)
    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = min(len(text), start + chunk_size)
        piece = text[start:end].strip()

        chunk_id = hashlib.sha256(
            f"{document_id}:{index}:{piece}".encode("utf-8")
        ).hexdigest()[:24]

        chunks.append(
            Chunk(
                id=chunk_id,
                document_id=document_id,
                source=source,
                chunk_index=index,
                text=piece,
                metadata={
                    "document_id": document_id,
                    "source": source,
                    "chunk_index": index,
                    "file_type": source.rsplit(".", 1)[-1].lower()
                    if "." in source else "unknown",
                },
            )
        )

        if end == len(text):
            break
        start = max(0, end - overlap)
        index += 1

    return chunks