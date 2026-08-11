import argparse
from pathlib import Path
from .config import settings
from .loaders import load_file, supported
from .chunking import chunk_text
from .store import VectorStore

def ingest(path: str):
    p = Path(path)
    paths = [p] if p.is_file() else [
        x for x in p.rglob("*") if x.is_file() and supported(x)
    ]

    store = VectorStore()
    total = 0

    for file_path in sorted(paths):
        text = load_file(str(file_path))
        chunks = chunk_text(
            text,
            str(file_path),
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        store.upsert(chunks)
        total += len(chunks)
        print(
            f"{file_path}: {len(chunks)} chunks | "
            f"dim={store.dimension}"
        )

    print(f"Indexed/upserted chunks: {total}")
    print(f"Collection count: {store.count()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    ingest(args.path)
