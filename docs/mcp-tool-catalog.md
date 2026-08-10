# MCP Tool Catalog

## asset_search
- Purpose: search assets by natural language or asset name
- Input schema: `AssetSearchToolRequest`
- Output schema: `AssetSearchResponse`
- Authentication: forwarded as trace metadata and optionally API bearer token
- Error behavior: returns HTTP 502 when the backend cannot be reached

## asset_metadata
- Purpose: fetch full metadata for an asset
- Input schema: `AssetMetadataToolRequest`
- Output schema: `AssetMetadataResponse`

## alarm_retrieval
- Purpose: retrieve alarms for an asset with pagination
- Input schema: `AlarmRetrievalToolRequest`
- Output schema: `AlarmListResponse`

## alarm_summary
- Purpose: summarize alarms across asset IDs and time range
- Input schema: `AlarmSummaryToolRequest`
- Output schema: `AlarmSummaryResponse`

## priority_score
- Purpose: compute a priority score and rationale for an alarm
- Input schema: `PriorityScoreToolRequest`
- Output schema: `PriorityScoreResponse`

## operator_recommendations
- Purpose: generate operator-recommended actions for an alarm
- Input schema: `OperatorRecommendationsToolRequest`
- Output schema: `OperatorRecommendationsResponse`
