from pathlib import Path

from apps.backend.rag import build_rag_index


def main() -> None:
    index = build_rag_index()
    print(f"Loaded {len(index.chunks)} document chunks from {index.documents_path}")


if __name__ == "__main__":
    main()
