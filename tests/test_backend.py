from fastapi.testclient import TestClient
from apps.backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "alarm-management-simulator"



def test_asset_search_and_metadata():
    headers = {}
    response = client.get("/assets/search", params={"query": "Boiler", "limit": 5}, headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["results"]
    asset_id = payload["results"][0]["asset_id"]

    metadata_response = client.get(f"/assets/{asset_id}/metadata", headers=headers)
    assert metadata_response.status_code == 200
    assert metadata_response.json()["asset_id"] == asset_id


def test_alarm_priority_and_recommendations():
    headers = {}
    assets = client.get("/assets/search", params={"query": "Boiler"}, headers=headers).json()["results"]
    asset_id = assets[0]["asset_id"]
    alarms = client.get("/alarms", params={"asset_id": asset_id, "page": 1, "page_size": 10}, headers=headers).json()["data"]
    assert alarms
    alarm_id = alarms[0]["alarm_id"]

    priority = client.post("/alarms/priority-score", json={"alarm_id": alarm_id}, headers=headers)
    assert priority.status_code == 200
    assert priority.json()["alarm_id"] == alarm_id

    recommendations = client.post(
        "/recommendations/operator-actions",
        json={"alarm_id": alarm_id, "include_related": True, "include_asset_context": True, "include_historical_pattern": True},
        headers=headers,
    )
    assert recommendations.status_code == 200
    assert recommendations.json()["recommendations"]


def test_rag_search():
    headers = {}
    response = client.get("/rag/search", params={"query": "repair procedure", "top_n": 2}, headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "repair procedure"
    assert isinstance(payload["results"], list)


def test_asset_search_with_natural_language_query():
    headers = {}
    response = client.get(
        "/assets/search",
        params={"query": "What related assets should be inspected for this motor trip alarm?", "limit": 5},
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["results"], "Expected the natural language query to return asset results"
    assert any(item["asset_id"] == "asset-103" for item in payload["results"])
