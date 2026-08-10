# RAG Design

## Document corpus
- Operating procedures
- Maintenance guides
- Troubleshooting documents

## Ingestion flow
1. Documents are stored under `rag/documents`.
2. The retrieval engine reads markdown text files and splits them into paragraphs.
3. Each chunk is indexed using a TF-IDF vectorizer.

## Retrieval behavior
- Query-based retrieval over document chunks
- Ranking by cosine similarity
- Source citations shown to the user

## Prompt-injection protections
- Only retrieved document content is shown to the UI.
- The system avoids treating retrieved text as instructions that modify tool behavior.
