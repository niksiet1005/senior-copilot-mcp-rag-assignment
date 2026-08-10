from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TraceInfo(BaseModel):
    trace_id: Optional[str] = None
    x_client_id: Optional[str] = None
    x_metadata_tag: Optional[str] = None


class ResponseMeta(BaseModel):
    trace_info: Optional[TraceInfo] = None


class ToolInfo(BaseModel):
    tool_id: str
    name: str
    description: str
    input_schema: str
    output_schema: str


class ToolCatalogResponse(ResponseMeta):
    tools: List[ToolInfo]


class ToolInvocationResponse(ResponseMeta):
    tool_id: str
    result: Any


class AssetSearchToolRequest(BaseModel):
    query: str = Field(..., description="Natural-language or asset-based search query")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of matching assets to return")


class AssetMetadataToolRequest(BaseModel):
    asset_id: str = Field(..., description="Identifier of the asset to fetch metadata for")


class AlarmRetrievalToolRequest(BaseModel):
    asset_id: str = Field(..., description="Identifier of the asset whose alarms should be retrieved")
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class AlarmSummaryToolRequest(BaseModel):
    asset_ids: List[str] = Field(..., description="Asset identifiers to summarize alarms for")
    time_range: Dict[str, str] = Field(..., description="Time range for alarm summary with start_time and end_time")
    severity: Optional[List[str]] = Field(None, description="Optional severity filter")


class PriorityScoreToolRequest(BaseModel):
    alarm_id: str = Field(..., description="Identifier of the alarm to score")


class OperatorRecommendationsToolRequest(BaseModel):
    alarm_id: str = Field(..., description="Identifier of the alarm to generate recommendations for")
    include_related: bool = Field(True)
    include_asset_context: bool = Field(True)
    include_historical_pattern: bool = Field(True)
