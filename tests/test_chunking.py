from rag.chunking import chunk_text

def test_chunking_is_deterministic():
    a = chunk_text("hello " * 300, "doc.md", 100, 20)
    b = chunk_text("hello " * 300, "doc.md", 100, 20)
    assert [x.id for x in a] == [x.id for x in b]
    assert len(a) > 1

def test_chunk_metadata():
    chunks = chunk_text("hello world", "doc.md", 100, 10)
    assert chunks[0].metadata["source"] == "doc.md"
    assert chunks[0].metadata["chunk_index"] == 0
