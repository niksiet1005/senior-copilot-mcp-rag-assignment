from fastapi.testclient import TestClient

from apps.mcp_server.main import app, backend_client

client = TestClient(app)


def test_list_tools():
    response = client.get("/tools")
    assert response.status_code == 200
    payload = response.json()
    assert "tools" in payload
    assert any(tool["tool_id"] == "asset_search" for tool in payload["tools"])


def test_invoke_unknown_tool():
    response = client.post("/tools/unknown_tool/invoke", json={})
    assert response.status_code == 404


def test_invoke_asset_search_validates_input(monkeypatch):
    expected = {"query": "motor trip", "limit": 3, "results": []}

    def fake_asset_search(payload, trace_info=None):
        assert payload["query"] == "motor trip"
        assert payload["limit"] == 3
        return expected

    monkeypatch.setattr(backend_client, "asset_search", fake_asset_search)
    response = client.post("/tools/asset_search/invoke", json={"query": "motor trip", "limit": 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload["tool_id"] == "asset_search"
    assert payload["result"] == expected
