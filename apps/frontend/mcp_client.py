import requests
from typing import Any, Dict, List, Optional


class MCPClientError(Exception):
    pass


class MCPClient:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout

    def _request(self, method: str, path: str, json: Any = None) -> Any:
        url = self.base_url + path
        try:
            response = requests.request(method, url, headers=self.headers, json=json, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise MCPClientError(f"MCP request failed [{method} {url}]: {exc}")

    def discover_tools(self) -> List[Dict[str, Any]]:
        payload = self._request("GET", "/tools")
        return payload.get("tools", [])

    def invoke_tool(self, tool_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", f"/tools/{tool_id}/invoke", json=payload)
