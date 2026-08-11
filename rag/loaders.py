from pathlib import Path
from bs4 import BeautifulSoup
from pypdf import PdfReader

def load_file(path: str) -> str:
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix in {".md", ".txt"}:
        return p.read_text(encoding="utf-8", errors="ignore")

    if suffix in {".html", ".htm"}:
        html = p.read_text(encoding="utf-8", errors="ignore")
        return BeautifulSoup(html, "html.parser").get_text("\n")

    if suffix == ".pdf":
        reader = PdfReader(str(p))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    raise ValueError(f"Unsupported file type: {p.suffix}")

def supported(path: str) -> bool:
    return Path(path).suffix.lower() in {".pdf", ".md", ".html", ".htm", ".txt"}
