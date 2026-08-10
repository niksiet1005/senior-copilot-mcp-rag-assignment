from typing import List, Optional
from pydantic import BaseModel, Field


class TraceInfo(BaseModel):
    trace_id: Optional[str] = None
    x_client_id: Optional[str] = None
    x_metadata_tag: Optional[str] = None


class ResponseMeta(BaseModel):
    trace_info: Optional[TraceInfo] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class AssetItem(BaseModel):
    asset_id: str
    name: str
    location: str
    asset_type: str
    status: str


class AssetSearchResponse(ResponseMeta):
    query: str
    limit: int
    results: List[AssetItem] = []


class AssetMetadataResponse(ResponseMeta):
    asset_id: str
    name: str
    location: str
    asset_type: str
    manufacturer: str
    model: str
    criticality: str
    maintenance_group: str
    last_inspection: str
    description: str


class AlarmItem(BaseModel):
    alarm_id: str
    asset_id: str
    alarm_name: str
    severity: str
    category: str
    start_time: str
    end_time: Optional[str]
    status: str
    description: str
    source_asset: Optional[str] = None


class AlarmListResponse(ResponseMeta):
    total: int
    page: int
    page_size: int
    data: List[AlarmItem]


class GroupByField(str):
    pass


class AlarmSummaryRequest(BaseModel):
    asset_ids: List[str]
    time_range: dict
    severity: Optional[List[str]] = None
    group_by: Optional[List[str]] = None
    kpis: Optional[List[str]] = None


class AlarmSummaryItem(BaseModel):
    group_value: str
    alarm_count: int
    recurring_rate: float
    avg_ack_delay: float


class AlarmSummaryResponse(ResponseMeta):
    summary: List[AlarmSummaryItem]


class AlarmTrendsRequest(BaseModel):
    asset_ids: List[str]
    time_range: dict
    bucket: str
    metrics: List[str]


class AlarmTrendItem(BaseModel):
    timestamp: str
    alarm_count: int
    avg_ack_delay: float


class AlarmTrendsResponse(ResponseMeta):
    trends: List[AlarmTrendItem]


class AlarmCorrelationRequest(BaseModel):
    asset_ids: List[str]
    time_range: dict
    correlation_method: str
    lag_window_minutes: int
    severity_threshold: str
    min_support: int


class AlarmCorrelationItem(BaseModel):
    related_alarm_name: str
    confidence: float
    cooccurrence_count: int


class AlarmCorrelationResponse(ResponseMeta):
    correlations: List[AlarmCorrelationItem]


class FloodAnalysisRequest(BaseModel):
    unit: str
    time_range: dict
    threshold_count: int
    rolling_window_minutes: int


class FloodAnalysisResponse(ResponseMeta):
    unit: str
    window_start: str
    window_end: str
    alarm_count: int
    flood_detected: bool
    recommendations: List[str]


class RationalizationRequest(BaseModel):
    asset_ids: List[str]
    time_range: dict
    recurrence_threshold: int
    stale_minutes_threshold: int


class RationalizationCandidate(BaseModel):
    alarm_name: str
    occurrence_count: int
    suggested_action: str


class RationalizationResponse(ResponseMeta):
    candidates: List[RationalizationCandidate]


class PriorityScoreRequest(BaseModel):
    alarm_id: str


class PriorityScoreResponse(ResponseMeta):
    alarm_id: str
    priority_score: int
    priority_rank: str
    rationale: List[str]


class OperatorRecommendationsRequest(BaseModel):
    alarm_id: str
    include_related: bool = True
    include_asset_context: bool = True
    include_historical_pattern: bool = True


class OperatorRecommendationItem(BaseModel):
    step: int
    action: str
    rationale: Optional[str] = None


class OperatorRecommendationsResponse(ResponseMeta):
    alarm_id: str
    recommendations: List[OperatorRecommendationItem]
    summary: str


class KPIDefinition(BaseModel):
    kpi_name: str
    description: str
    calculation: str


class KPIDefinitionsResponse(ResponseMeta):
    kpis: List[KPIDefinition]


class RAGHit(BaseModel):
    source: str
    text: str
    score: float


class RAGSearchResponse(ResponseMeta):
    query: str
    results: List[RAGHit]
