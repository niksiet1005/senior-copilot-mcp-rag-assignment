from pathlib import Path
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RagIndex:
    def __init__(self, documents_path: Path):
        self.documents_path = documents_path
        self.chunks: List[Dict[str, str]] = []
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None
        self._load_documents()
        self._build_index()

    def _load_documents(self) -> None:
        self.chunks = []
        if not self.documents_path.exists():
            return
        for path in sorted(self.documents_path.glob("*.md")):
            source = path.name
            text = path.read_text(encoding="utf-8").strip()
            for paragraph in [p.strip() for p in text.split("\n\n") if p.strip()]:
                self.chunks.append({"source": source, "text": paragraph})

    def _build_index(self) -> None:
        if not self.chunks:
            self.matrix = None
            return
        texts = [chunk["text"] for chunk in self.chunks]
        self.matrix = self.vectorizer.fit_transform(texts)

    def search(self, query: str, top_n: int = 3) -> List[Dict[str, object]]:
        if self.matrix is None or not query.strip():
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        scored = sorted(
            [
                {"source": self.chunks[idx]["source"], "text": self.chunks[idx]["text"], "score": float(scores[idx])}
                for idx in range(len(scores))
            ],
            key=lambda item: item["score"],
            reverse=True,
        )
        return [item for item in scored if item["score"] > 0.0][:top_n]


def build_rag_index() -> RagIndex:
    root = Path(__file__).resolve().parents[2]
    documents_path = root / "rag" / "documents"
    return RagIndex(documents_path)
