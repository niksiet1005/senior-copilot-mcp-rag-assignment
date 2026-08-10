import logging
import os
import time
from typing import Any, Dict, Optional

import requests


LOGGER = logging.getLogger("mcp_server")


class BackendClientError(Exception):
    pass


class MCPBackendClient:
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 2,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def _build_headers(self, trace_info: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if trace_info:
            if trace_info.get("trace_id"):
                headers["trace_id"] = trace_info["trace_id"]
            if trace_info.get("x_client_id"):
                headers["x-client-id"] = trace_info["x_client_id"]
            if trace_info.get("x_metadata_tag"):
                headers["x-metadata-tag"] = trace_info["x_metadata_tag"]
        return headers

    def request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, trace_info: Optional[Dict[str, str]] = None) -> Any:
        url = self.base_url + path
        headers = self._build_headers(trace_info)
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=json,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                LOGGER.warning("Request failed, retrying (%s/%s): %s", attempt + 1, self.max_retries, exc)
                time.sleep(0.5)

        raise BackendClientError(f"Backend request failed for {url}: {last_error}")

    def asset_search(self, payload: Dict[str, Any], trace_info: Optional[Dict[str, str]] = None) -> Any:
        return self.request("GET", "/assets/search", params=payload, trace_info=trace_info)

    def asset_metadata(self, payload: Dict[str, Any], trace_info: Optional[Dict[str, str]] = None) -> Any:
        asset_id = payload.get("asset_id")
        path = f"/assets/{asset_id}/metadata"
        return self.request("GET", path, trace_info=trace_info)

    def alarm_retrieval(self, payload: Dict[str, Any], trace_info: Optional[Dict[str, str]] = None) -> Any:
        return self.request("GET", "/alarms", params=payload, trace_info=trace_info)

    def alarm_summary(self, payload: Dict[str, Any], trace_info: Optional[Dict[str, str]] = None) -> Any:
        return self.request("POST", "/alarms/summary", json=payload, trace_info=trace_info)

    def priority_score(self, payload: Dict[str, Any], trace_info: Optional[Dict[str, str]] = None) -> Any:
        return self.request("POST", "/alarms/priority-score", json=payload, trace_info=trace_info)

    def operator_recommendations(self, payload: Dict[str, Any], trace_info: Optional[Dict[str, str]] = None) -> Any:
        return self.request("POST", "/recommendations/operator-actions", json=payload, trace_info=trace_info)

    @classmethod
    def from_env(cls) -> "MCPBackendClient":
        base_url = os.getenv("ALARM_API_HOST", "http://localhost:8000")
        api_key = os.getenv("MCP_API_KEY")
        timeout = int(os.getenv("MCP_BACKEND_TIMEOUT", "10"))
        max_retries = int(os.getenv("MCP_BACKEND_RETRIES", "2"))
        return cls(base_url=base_url, api_key=api_key, timeout=timeout, max_retries=max_retries)
