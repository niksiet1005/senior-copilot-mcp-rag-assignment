# API Integration

The MCP server forwards requests to the Alarm Management API simulator using the configured `ALARM_API_HOST` environment variable. Trace metadata is propagated through headers so each tool call can be correlated across UI, MCP server, and backend logs.

## Supported operations
- asset search
- asset metadata
- alarm retrieval
- alarm summary
- priority scoring
- operator recommendations
