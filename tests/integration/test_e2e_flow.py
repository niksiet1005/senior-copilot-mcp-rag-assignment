from fastapi.testclient import TestClient

from apps.backend.main import app as backend_app
from apps.mcp_server.main import app as mcp_app

backend_client = TestClient(backend_app)
mcp_client = TestClient(mcp_app)


def test_end_to_end_alarm_investigation_workflow():
    asset_response = backend_client.get("/assets/search", params={"query": "motor trip alarm", "limit": 5})
    assert asset_response.status_code == 200
    assets = asset_response.json()["results"]
    assert any(asset["asset_id"] == "asset-103" for asset in assets)

    mcp_response = mcp_client.post(
        "/tools/asset_search/invoke",
        json={"query": "motor trip alarm", "limit": 5},
    )
    assert mcp_response.status_code == 200
    assert any(result["asset_id"] == "asset-103" for result in mcp_response.json()["result"]["results"])

    rag_response = backend_client.get("/rag/search", params={"query": "motor trip", "top_n": 2})
    assert rag_response.status_code == 200
    assert rag_response.json()["results"]
