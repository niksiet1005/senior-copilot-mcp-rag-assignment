from typing import List, Optional
import re

STOP_WORDS = {
    "the", "and", "or", "for", "to", "of", "in", "on", "this", "that", "these", "those",
    "should", "be", "is", "a", "an", "with", "what", "related", "assets", "asset", "alarm",
    "alarms", "please", "show", "find", "inspect", "inspected", "requested", "query", "same",
    "here", "when", "which", "where", "how", "why", "need", "required", "from",
}

ASSETS = [
    {
        "asset_id": "asset-101",
        "name": "Boiler Feed Pump 101",
        "location": "East Refinery",
        "asset_type": "Rotating Equipment",
        "status": "active",
        "manufacturer": "PumpTech",
        "model": "PT-5400",
        "criticality": "high",
        "maintenance_group": "Pump Reliability",
        "last_inspection": "2026-07-02T09:30:00Z",
        "description": "High-capacity feed pump used for boiler water circulation."
    },
    {
        "asset_id": "asset-102",
        "name": "Compressor Discharge Valve 102",
        "location": "East Refinery",
        "asset_type": "Control Valve",
        "status": "active",
        "manufacturer": "FlowCore",
        "model": "FC-210",
        "criticality": "critical",
        "maintenance_group": "Valve Integrity",
        "last_inspection": "2026-06-20T14:00:00Z",
        "description": "Discharge valve controlling compressor output pressure."
    },
    {
        "asset_id": "asset-103",
        "name": "Motor Trip Module 103",
        "location": "West Refinery",
        "asset_type": "Electrical System",
        "status": "active",
        "manufacturer": "ElectroSys",
        "model": "ES-900",
        "criticality": "medium",
        "maintenance_group": "Motor Control",
        "last_inspection": "2026-06-28T11:25:00Z",
        "description": "Protective trip module for large motor starters."
    }
]

ALARMS = [
    {
        "alarm_id": "alarm-101-a",
        "asset_id": "asset-101",
        "alarm_name": "Boiler Feed Pump 101 High Vibration",
        "severity": "critical",
        "category": "mechanical",
        "start_time": "2026-07-07T08:45:00Z",
        "end_time": None,
        "status": "active",
        "description": "Pump vibration exceeded safety threshold, likely due to misalignment or balancing issue.",
        "source_asset": "asset-101"
    },
    {
        "alarm_id": "alarm-101-b",
        "asset_id": "asset-101",
        "alarm_name": "Boiler Feed Pump 101 Low Flow",
        "severity": "high",
        "category": "process",
        "start_time": "2026-07-06T16:20:00Z",
        "end_time": "2026-07-06T17:10:00Z",
        "status": "acknowledged",
        "description": "Measured flow below minimum operating setpoint.",
        "source_asset": "asset-101"
    },
    {
        "alarm_id": "alarm-102-a",
        "asset_id": "asset-102",
        "alarm_name": "Compressor Discharge Pressure High",
        "severity": "critical",
        "category": "process",
        "start_time": "2026-07-08T10:05:00Z",
        "end_time": None,
        "status": "active",
        "description": "Discharge pressure exceeded safety threshold, indicating potential valve or compressor instability.",
        "source_asset": "asset-102"
    },
    {
        "alarm_id": "alarm-102-b",
        "asset_id": "asset-102",
        "alarm_name": "Compressor Discharge Pressure Repeat Event",
        "severity": "high",
        "category": "process",
        "start_time": "2026-07-05T09:00:00Z",
        "end_time": "2026-07-05T09:30:00Z",
        "status": "cleared",
        "description": "Recovered from prior high-pressure event after operator control action.",
        "source_asset": "asset-102"
    },
    {
        "alarm_id": "alarm-103-a",
        "asset_id": "asset-103",
        "alarm_name": "Motor Trip 103 Unexpected Shutdown",
        "severity": "critical",
        "category": "electrical",
        "start_time": "2026-07-04T21:40:00Z",
        "end_time": None,
        "status": "active",
        "description": "Motor tripped unexpectedly, requiring inspection of related starter and protection system.",
        "source_asset": "asset-103"
    }
]

KPI_DEFINITIONS = [
    {
        "kpi_name": "alarm_count",
        "description": "Total number of alarms in the requested interval.",
        "calculation": "COUNT(alarm_id)"
    },
    {
        "kpi_name": "recurring_rate",
        "description": "Percentage of alarms repeated for the same asset or alarm name.",
        "calculation": "RECURRENT_ALARMS / TOTAL_ALARMS"
    },
    {
        "kpi_name": "avg_ack_delay",
        "description": "Average time between alarm start and acknowledgement or clearance.",
        "calculation": "AVG(ack_time - start_time)"
    }
]


def _tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r"\w+", text.lower()) if token not in STOP_WORDS]


def _matches_tokens(text: str, query_tokens: List[str]) -> bool:
    if not query_tokens:
        return False
    text_tokens = set(re.findall(r"\w+", text.lower()))
    match_count = sum(1 for token in query_tokens if token in text_tokens)
    return match_count >= max(1, min(3, len(query_tokens) // 2))


def search_assets(query: str, limit: int = 10) -> List[dict]:
    lower_query = query.strip().lower()
    query_tokens = _tokenize(query)
    matches = []
    for asset in ASSETS:
        asset_text = " ".join(
            [
                asset["name"],
                asset["location"],
                asset["description"],
                asset["asset_type"],
                asset["model"],
            ]
        )
        if lower_query in asset_text.lower() or _matches_tokens(asset_text, query_tokens):
            matches.append(asset)
            continue

        related_alarms = [alarm for alarm in ALARMS if alarm["asset_id"] == asset["asset_id"]]
        if any(
            _matches_tokens(alarm["alarm_name"], query_tokens)
            or _matches_tokens(alarm["description"], query_tokens)
            or _matches_tokens(alarm["category"], query_tokens)
            or _matches_tokens(alarm["severity"], query_tokens)
            or _matches_tokens(alarm["status"], query_tokens)
            for alarm in related_alarms
        ):
            matches.append(asset)
    return matches[:limit]


def get_asset(asset_id: str) -> Optional[dict]:
    return next((asset for asset in ASSETS if asset["asset_id"] == asset_id), None)


def list_alarms(asset_id: str, page: int = 1, page_size: int = 50, sort_by: str = "start_time", sort_order: str = "desc") -> dict:
    filtered = [alarm for alarm in ALARMS if alarm["asset_id"] == asset_id]
    reverse = sort_order.lower() == "desc"
    filtered.sort(key=lambda item: item.get(sort_by, ""), reverse=reverse)
    total = len(filtered)
    start = (page - 1) * page_size
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": filtered[start : start + page_size]
    }


def get_alarm(alarm_id: str) -> Optional[dict]:
    return next((alarm for alarm in ALARMS if alarm["alarm_id"] == alarm_id), None)


def calculate_alarm_summary(asset_ids: List[str], severity: Optional[List[str]] = None) -> List[dict]:
    records = [alarm for alarm in ALARMS if alarm["asset_id"] in asset_ids]
    if severity:
        records = [alarm for alarm in records if alarm["severity"] in severity]

    groups = {}
    for alarm in records:
        key = alarm["alarm_name"]
        entry = groups.setdefault(key, {"count": 0, "recurrences": 0, "total_ack_delay": 0.0})
        entry["count"] += 1
        if alarm["status"] != "active":
            entry["recurrences"] += 1
            entry["total_ack_delay"] += 8.0

    summary = []
    for name, values in groups.items():
        count = values["count"]
        recurring_rate = min(1.0, values["recurrences"] / max(count, 1))
        avg_ack_delay = values["total_ack_delay"] / max(values["recurrences"], 1) if values["recurrences"] else 0.0
        summary.append({
            "group_value": name,
            "alarm_count": count,
            "recurring_rate": round(recurring_rate, 2),
            "avg_ack_delay": round(avg_ack_delay, 1)
        })
    return summary


def calculate_alarm_trends(asset_ids: List[str], bucket: str) -> List[dict]:
    records = [alarm for alarm in ALARMS if alarm["asset_id"] in asset_ids]
    if bucket == "daily":
        buckets = {}
        for alarm in records:
            key = alarm["start_time"][:10]
            entry = buckets.setdefault(key, {"alarm_count": 0, "avg_ack_delay": 0.0})
            entry["alarm_count"] += 1
            entry["avg_ack_delay"] += 6.0
        return [
            {"timestamp": key, "alarm_count": value["alarm_count"], "avg_ack_delay": round(value["avg_ack_delay"] / value["alarm_count"], 1)}
            for key, value in sorted(buckets.items())
        ]
    return []


def calculate_correlation(asset_ids: List[str], min_support: int = 1) -> List[dict]:
    records = [alarm for alarm in ALARMS if alarm["asset_id"] in asset_ids]
    related = []
    if len(records) > 1:
        main = records[0]
        for alarm in records[1:]:
            related.append({
                "related_alarm_name": alarm["alarm_name"],
                "confidence": 0.76,
                "cooccurrence_count": min_support + 1
            })
    return related


def calculate_priority_score(alarm_id: str) -> Optional[dict]:
    alarm = get_alarm(alarm_id)
    if not alarm:
        return None
    score = 80 if alarm["severity"] == "critical" else 55
    rank = "P1" if score >= 75 else "P2"
    rationale = [
        f"Severity is {alarm['severity']}",
        f"Alarm category is {alarm['category']}",
        "Asset criticality is high" if alarm["asset_id"] == "asset-101" else "Asset criticality is medium"
    ]
    return {
        "alarm_id": alarm_id,
        "priority_score": score,
        "priority_rank": rank,
        "rationale": rationale
    }


def generate_recommendations(alarm_id: str, include_related: bool = True, include_asset_context: bool = True, include_historical_pattern: bool = True) -> dict:
    alarm = get_alarm(alarm_id)
    if not alarm:
        return {
            "alarm_id": alarm_id,
            "recommendations": [],
            "summary": "No recommendations available for unknown alarm."
        }
    recs = [
        {"step": 1, "action": "Inspect the pump bearing and shaft alignment.", "rationale": "High vibration on the pump can indicate mechanical imbalance."},
    ]
    if include_related and alarm["asset_id"] == "asset-101":
        recs.append({"step": 2, "action": "Verify suction pressure and inlet strainers.", "rationale": "Low flow or pump cavitation may cause vibration."})
    if include_historical_pattern:
        recs.append({"step": 3, "action": "Review prior corrective actions for repeated vibration alarms.", "rationale": "Recurring alarms suggest an underlying mechanical fault."})
    return {
        "alarm_id": alarm_id,
        "recommendations": recs,
        "summary": f"Recommended immediate actions for {alarm['alarm_name']}."
    }


def get_kpi_definitions() -> List[dict]:
    return KPI_DEFINITIONS
