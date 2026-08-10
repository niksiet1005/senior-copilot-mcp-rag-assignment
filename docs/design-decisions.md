# Design Decisions

- FastAPI is used for the MCP server and backend API to provide typed and testable services.
- Streamlit is used for the GUI because it is simple to run locally and suitable for demo delivery.
- TF-IDF is used for RAG over a small document corpus to keep the implementation lightweight and self-contained.
- The MCP server isolates the copilot from direct Alarm Management API coupling and makes tool discovery explicit.
