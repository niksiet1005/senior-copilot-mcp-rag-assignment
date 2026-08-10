FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000 9000 8501
CMD ["bash", "-lc", "uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 & uvicorn apps.mcp_server.main:app --host 0.0.0.0 --port 9000 & streamlit run apps/frontend/app.py --server.port 8501 --server.address 0.0.0.0"]
