run-backend:
	uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000

run-mcp:
	uvicorn apps.mcp_server.main:app --host 0.0.0.0 --port 9000

run-ui:
	streamlit run apps/frontend/app.py

test:
	python -m pytest -q
