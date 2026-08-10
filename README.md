# Alarm Investigation and Procedure Guidance Copilot

This repository implements an evidence-backed alarm investigation workflow using:

- a FastAPI-based Alarm Management API simulator
- a candidate-developed MCP server exposing alarm operations as typed tools
- a Streamlit GUI that discovers and invokes MCP tools
- a document RAG workflow over alarm procedures and troubleshooting guides

## Main capabilities

- Natural-language alarm investigation requests
- MCP tool discovery and invocation for asset search, metadata lookup, alarm retrieval, summaries, priority scoring, and recommendations
- RAG-backed evidence using operating procedures and maintenance documents
- Tool trace and raw response inspection in the UI

## Technology stack

- Python 3.11+
- FastAPI
- Streamlit
- scikit-learn for TF-IDF retrieval
- pytest

## MCP server

The MCP server is implemented under [apps/mcp_server](apps/mcp_server) and exposes the following tools:

- `asset_search`
- `asset_metadata`
- `alarm_retrieval`
- `alarm_summary`
- `priority_score`
- `operator_recommendations`

Start the MCP server independently:

```bash
uvicorn apps.mcp_server.main:app --host 0.0.0.0 --port 9000
```

## Alarm API backend

Start the backend simulator:

```bash
uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000
```

## Streamlit UI

Start the GUI:

```bash
streamlit run apps/frontend/app.py
```

## RAG workflow

Documents are stored under [rag/documents](rag/documents) and ingested through the existing TF-IDF index in [apps/backend/rag.py](apps/backend/rag.py).

## Tests

```bash
python -m pytest -q
```

## Configuration

Copy [.env.example](.env.example) and adjust values as needed.

## Architecture summary

See [docs/architecture.md](docs/architecture.md) and [docs/architecture-diagram.svg](docs/architecture-diagram.svg).
