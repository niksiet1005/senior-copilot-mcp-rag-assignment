# Architecture

The solution is organized into a layered architecture:

1. UI layer: Streamlit-based copilot that accepts natural-language investigation requests.
2. Orchestration layer: the frontend client discovers MCP tools and chains them together.
3. MCP layer: an independently runnable FastAPI server that exposes typed Alarm Management API tools.
4. Backend layer: the Alarm Management API simulator that provides asset metadata, alarm retrieval, summaries, priorities, and recommendations.
5. RAG layer: a TF-IDF-based retrieval index over operating procedures and maintenance documents.

## Request flow

1. The user enters a natural-language investigation request in the GUI.
2. The GUI discovers available MCP tools from the MCP server.
3. The client invokes tool(s) such as asset search and alarm retrieval.
4. The MCP server forwards requests to the Alarm Management API simulator with trace metadata.
5. The UI performs RAG retrieval on the document corpus to gather evidence.
6. The final response is shown with structured results, citations, and MCP execution trace.
