# Alarm Investigation Copilot

This repository contains a working Python backend simulator and a Streamlit UI for alarm investigation and procedure guidance.

## Components

- `apps/backend/main.py` — FastAPI simulator exposing alarm management endpoints and a simple RAG search endpoint.
- `apps/frontend/app.py` — Streamlit UI that sends natural-language investigation requests to the backend.
- `rag/documents/` — Sample procedural documents used by the RAG search endpoint.
- `tests/test_backend.py` — Basic backend integration tests.

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the backend

```bash
uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Run the frontend

```bash
streamlit run apps/frontend/app.py
```

## Notes

- The backend currently does not require authentication.
- Use `http://localhost:8000/docs` to view the FastAPI API docs.

## Sample request

Use the UI to enter a natural-language request such as:

- "Show active critical alarms for Boiler Feed Pump 101 and recommend immediate actions."
- "Why are compressor discharge pressure alarms repeatedly occurring?"

## Tests

```bash
pytest tests/test_backend.py
```
