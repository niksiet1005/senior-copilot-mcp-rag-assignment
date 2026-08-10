import logging
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from .client import MCPBackendClient, BackendClientError
from .schemas import (
    AlarmRetrievalToolRequest,
    AlarmSummaryToolRequest,
    AssetMetadataToolRequest,
    AssetSearchToolRequest,
    OperatorRecommendationsToolRequest,
    PriorityScoreToolRequest,
    ToolCatalogResponse,
    ToolInfo,
    ToolInvocationResponse,
    TraceInfo,
)

LOGGER = logging.getLogger("mcp_server")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Alarm Management MCP Server",
    description="A MCP server that exposes Alarm Management API operations as typed tools.",
    version="0.1.0",
)

backend_client = MCPBackendClient.from_env()

TOOL_CATALOG: List[ToolInfo] = [
    ToolInfo(
        tool_id="asset_search",
        name="Asset Search",
        description="Search for assets using a natural-language or asset-specific query.",
        input_schema="AssetSearchToolRequest",
        output_schema="AssetSearchResponse",
    ),
    ToolInfo(
        tool_id="asset_metadata",
        name="Asset Metadata Lookup",
        description="Retrieve detailed metadata for a selected asset.",
        input_schema="AssetMetadataToolRequest",
        output_schema="AssetMetadataResponse",
    ),
    ToolInfo(
        tool_id="alarm_retrieval",
        name="Alarm Retrieval",
        description="Retrieve active or recent alarms for a given asset.",
        input_schema="AlarmRetrievalToolRequest",
        output_schema="AlarmListResponse",
    ),
    ToolInfo(
        tool_id="alarm_summary",
        name="Alarm Summary",
        description="Summarize alarms for one or more assets over a time range.",
        input_schema="AlarmSummaryToolRequest",
        output_schema="AlarmSummaryResponse",
    ),
    ToolInfo(
        tool_id="priority_score",
        name="Alarm Priority Scoring",
        description="Compute a priority score for a specified alarm.",
        input_schema="PriorityScoreToolRequest",
        output_schema="PriorityScoreResponse",
    ),
    ToolInfo(
        tool_id="operator_recommendations",
        name="Operator Recommendations",
        description="Generate recommended actions for a specified alarm.",
        input_schema="OperatorRecommendationsToolRequest",
        output_schema="OperatorRecommendationsResponse",
    ),
]


def get_trace_info(request: Request) -> TraceInfo:
    return TraceInfo(
        trace_id=request.headers.get("trace_id"),
        x_client_id=request.headers.get("x-client-id"),
        x_metadata_tag=request.headers.get("x-metadata-tag"),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    LOGGER.exception("Unhandled exception in MCP server")
    return JSONResponse(status_code=500, content={"error": "Internal MCP server error"})


@app.get("/tools", response_model=ToolCatalogResponse)
def list_tools(request: Request) -> ToolCatalogResponse:
    return ToolCatalogResponse(tools=TOOL_CATALOG, trace_info=get_trace_info(request))


@app.post("/tools/{tool_id}/invoke", response_model=ToolInvocationResponse)
def invoke_tool(tool_id: str, request: Request, payload: Dict[str, Any]) -> ToolInvocationResponse:
    trace_info = get_trace_info(request)
    try:
        if tool_id == "asset_search":
            parsed = AssetSearchToolRequest(**payload)
            result = backend_client.asset_search(parsed.dict(), trace_info=trace_info.dict())
        elif tool_id == "asset_metadata":
            parsed = AssetMetadataToolRequest(**payload)
            result = backend_client.asset_metadata(parsed.dict(), trace_info=trace_info.dict())
        elif tool_id == "alarm_retrieval":
            parsed = AlarmRetrievalToolRequest(**payload)
            result = backend_client.alarm_retrieval(parsed.dict(), trace_info=trace_info.dict())
        elif tool_id == "alarm_summary":
            parsed = AlarmSummaryToolRequest(**payload)
            result = backend_client.alarm_summary(parsed.dict(), trace_info=trace_info.dict())
        elif tool_id == "priority_score":
            parsed = PriorityScoreToolRequest(**payload)
            result = backend_client.priority_score(parsed.dict(), trace_info=trace_info.dict())
        elif tool_id == "operator_recommendations":
            parsed = OperatorRecommendationsToolRequest(**payload)
            result = backend_client.operator_recommendations(parsed.dict(), trace_info=trace_info.dict())
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
    except BackendClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return ToolInvocationResponse(tool_id=tool_id, result=result, trace_info=trace_info)
