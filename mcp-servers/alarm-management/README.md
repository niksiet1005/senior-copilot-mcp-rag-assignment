# Alarm Management MCP Server

This server re-exports the MCP implementation in [apps/mcp_server](../../apps/mcp_server).

Run it with:

```bash
uvicorn apps.mcp_server.main:app --host 0.0.0.0 --port 9000
```
