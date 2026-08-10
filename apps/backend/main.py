from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional

from .schemas import (
    AlarmCorrelationRequest,
    AlarmCorrelationResponse,
    AlarmListResponse,
    PriorityScoreRequest,
    PriorityScoreResponse,
    AlarmSummaryRequest,
    AlarmSummaryResponse,
    AlarmTrendsRequest,
    AlarmTrendsResponse,
    AssetMetadataResponse,
    AssetSearchResponse,
    FloodAnalysisRequest,
    FloodAnalysisResponse,
    HealthResponse,
    KPIDefinitionsResponse,
    OperatorRecommendationsRequest,
    OperatorRecommendationsResponse,
    RationalizationRequest,
    RationalizationResponse,
    RAGSearchResponse,
    RAGHit,
    TraceInfo,
)
from . import data
from .rag import build_rag_index

app = FastAPI(
    title="Alarm Management API Simulator",
    description="A FastAPI-based simulator for alarm investigation, priority scoring, and operator guidance.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_index = build_rag_index()


def get_trace_info(request: Request) -> TraceInfo:
    return TraceInfo(
        trace_id=request.headers.get("trace_id"),
        x_client_id=request.headers.get("x-client-id"),
        x_metadata_tag=request.headers.get("x-metadata-tag"),
    )



@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    payload = {"error": exc.detail, "status_code": exc.status_code}
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="alarm-management-simulator", version="0.1.0")


@app.get("/assets/search", response_model=AssetSearchResponse)
def search_assets(
    request: Request,
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
) -> AssetSearchResponse:
    matches = data.search_assets(query, limit)
    return AssetSearchResponse(query=query, limit=limit, results=matches, trace_info=get_trace_info(request))


@app.get("/assets/{asset_id}/metadata", response_model=AssetMetadataResponse)
def get_asset_metadata(asset_id: str, request: Request) -> AssetMetadataResponse:
    asset = data.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetMetadataResponse(**asset, trace_info=get_trace_info(request))


@app.get("/alarms", response_model=AlarmListResponse)
def get_alarms(
    request: Request,
    asset_id: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("start_time"),
    sort_order: str = Query("desc"),
) -> AlarmListResponse:
    page_payload = data.list_alarms(asset_id, page, page_size, sort_by, sort_order)
    return AlarmListResponse(**page_payload, trace_info=get_trace_info(request))


@app.get("/alarms/{alarm_id}", response_model=AlarmListResponse)
def get_alarm_by_id(alarm_id: str, request: Request) -> AlarmListResponse:
    alarm = data.get_alarm(alarm_id)
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return AlarmListResponse(total=1, page=1, page_size=1, data=[alarm], trace_info=get_trace_info(request))


@app.post("/alarms/summary", response_model=AlarmSummaryResponse)
def alarm_summary(
    request: Request,
    payload: AlarmSummaryRequest,
) -> AlarmSummaryResponse:
    summary = data.calculate_alarm_summary(payload.asset_ids, severity=payload.severity)
    return AlarmSummaryResponse(summary=summary, trace_info=get_trace_info(request))


@app.post("/alarms/trends", response_model=AlarmTrendsResponse)
def alarm_trends(
    request: Request,
    payload: AlarmTrendsRequest,
) -> AlarmTrendsResponse:
    trends = data.calculate_alarm_trends(payload.asset_ids, payload.bucket)
    return AlarmTrendsResponse(trends=trends, trace_info=get_trace_info(request))


@app.post("/alarms/correlation", response_model=AlarmCorrelationResponse)
def alarm_correlation(
    request: Request,
    payload: AlarmCorrelationRequest,
) -> AlarmCorrelationResponse:
    correlations = data.calculate_correlation(payload.asset_ids, payload.min_support)
    return AlarmCorrelationResponse(correlations=correlations, trace_info=get_trace_info(request))


@app.post("/alarms/flood-analysis", response_model=FloodAnalysisResponse)
def flood_analysis(
    request: Request,
    payload: FloodAnalysisRequest,
) -> FloodAnalysisResponse:
    return FloodAnalysisResponse(
        unit=payload.unit,
        window_start=payload.time_range["start_time"],
        window_end=payload.time_range["end_time"],
        alarm_count=12,
        flood_detected=payload.threshold_count < 20,
        recommendations=[
            "Review the unit control logic for repeated alarm bursts.",
            "Consider a rolling alarm suppression window if alerts are spurious.",
        ],
        trace_info=get_trace_info(request),
    )


@app.post("/alarms/rationalization-candidates", response_model=RationalizationResponse)
def rationalization_candidates(
    request: Request,
    payload: RationalizationRequest,
) -> RationalizationResponse:
    candidates = [
        {"alarm_name": "Boiler Feed Pump 101 High Vibration", "occurrence_count": 4, "suggested_action": "Perform mechanical alignment check and bearing inspection."},
        {"alarm_name": "Compressor Discharge Pressure High", "occurrence_count": 3, "suggested_action": "Validate compressor control valve tuning and check for discharge restrictions."},
    ]
    return RationalizationResponse(candidates=candidates, trace_info=get_trace_info(request))


@app.post("/alarms/priority-score", response_model=PriorityScoreResponse)
def priority_score(
    request: Request,
    payload: PriorityScoreRequest,
) -> PriorityScoreResponse:
    score = data.calculate_priority_score(payload.alarm_id)
    if not score:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return PriorityScoreResponse(**score, trace_info=get_trace_info(request))


@app.post("/recommendations/operator-actions", response_model=OperatorRecommendationsResponse)
def operator_recommendations(
    request: Request,
    payload: OperatorRecommendationsRequest,
) -> OperatorRecommendationsResponse:
    rec = data.generate_recommendations(
        payload.alarm_id,
        include_related=payload.include_related,
        include_asset_context=payload.include_asset_context,
        include_historical_pattern=payload.include_historical_pattern,
    )
    return OperatorRecommendationsResponse(**rec, trace_info=get_trace_info(request))


@app.get("/analytics/kpi-definitions", response_model=KPIDefinitionsResponse)
def kpi_definitions(request: Request) -> KPIDefinitionsResponse:
    return KPIDefinitionsResponse(kpis=data.get_kpi_definitions(), trace_info=get_trace_info(request))


@app.get("/rag/search", response_model=RAGSearchResponse)
def rag_search(
    request: Request,
    query: str = Query(..., min_length=1),
    top_n: int = Query(3, ge=1, le=10),
) -> RAGSearchResponse:
    results = rag_index.search(query, top_n=top_n)
    hits = [RAGHit(**item) for item in results]
    return RAGSearchResponse(query=query, results=hits, trace_info=get_trace_info(request))
