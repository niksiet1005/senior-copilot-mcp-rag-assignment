import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.frontend.mcp_client import MCPClient

st.set_page_config(page_title="Alarm Investigation Copilot", layout="wide")

DEFAULT_MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:9000")
DEFAULT_API_URL = os.getenv("ALARM_API_HOST", "http://localhost:8000")

st.title("Alarm Investigation and Procedure Guidance")

with st.sidebar:
    st.header("Settings")
    mcp_url = st.text_input("MCP Server URL", DEFAULT_MCP_URL)
    api_url = st.text_input("Alarm API Base URL", DEFAULT_API_URL)
    st.markdown("---")
    st.markdown("Enter an investigation request, then click **Submit**.")

query = st.text_area(
    "Investigation request",
    value="Show active critical alarms for Boiler Feed Pump 101 and recommend immediate actions.",
    height=140,
)

if st.button("Submit"):
    if not query.strip():
        st.warning("Please enter a request to start the investigation.")
    else:
        st.info("Discovering MCP tools...")
        mcp_client = MCPClient(base_url=mcp_url, headers={"trace_id": "ui-trace-001", "x-client-id": "streamlit-ui", "x-metadata-tag": "user-request"})
        tool_trace: List[Dict[str, Any]] = []
        errors: List[str] = []
        rag_response: Dict[str, Any] = {}

        try:
            tools = mcp_client.discover_tools()
            tool_trace.append({"step": "discover_tools", "status": "success", "tools": [tool["tool_id"] for tool in tools]})
        except Exception as exc:
            errors.append(f"Tool discovery failed: {exc}")
            tools = []

        if tools:
            with st.spinner("Executing MCP tool chain..."):
                try:
                    asset_search_result = mcp_client.invoke_tool("asset_search", {"query": query, "limit": 5})
                    tool_trace.append({"step": "asset_search", "tool_id": "asset_search", "status": "success", "result_count": len(asset_search_result.get("result", {}).get("results", []))})
                except Exception as exc:
                    errors.append(f"Asset search failed: {exc}")
                    asset_search_result = None

                asset_items = []
                if asset_search_result:
                    asset_items = asset_search_result.get("result", {}).get("results", [])

                if not asset_items:
                    tool_trace.append({"step": "asset_resolution", "status": "failed", "reason": "No assets found"})
                else:
                    asset = asset_items[0]
                    asset_id = asset.get("asset_id")

                    try:
                        metadata = mcp_client.invoke_tool("asset_metadata", {"asset_id": asset_id})
                        tool_trace.append({"step": "asset_metadata", "tool_id": "asset_metadata", "status": "success"})
                    except Exception as exc:
                        errors.append(f"Asset metadata failed: {exc}")
                        metadata = None

                    try:
                        alarms = mcp_client.invoke_tool("alarm_retrieval", {"asset_id": asset_id, "page": 1, "page_size": 10})
                        tool_trace.append({"step": "alarm_retrieval", "tool_id": "alarm_retrieval", "status": "success", "alarm_count": len(alarms.get("result", {}).get("data", []))})
                    except Exception as exc:
                        errors.append(f"Alarm retrieval failed: {exc}")
                        alarms = None

                    top_alarm = None
                    if alarms and alarms.get("result", {}).get("data"):
                        alarm_list = alarms["result"]["data"]
                        top_alarm = alarm_list[0]
                    else:
                        alarm_list = []

                    if top_alarm:
                        try:
                            priority = mcp_client.invoke_tool("priority_score", {"alarm_id": top_alarm["alarm_id"]})
                            tool_trace.append({"step": "priority_score", "tool_id": "priority_score", "status": "success"})
                        except Exception as exc:
                            errors.append(f"Priority scoring failed: {exc}")
                            priority = None

                        try:
                            recommendations = mcp_client.invoke_tool(
                                "operator_recommendations",
                                {
                                    "alarm_id": top_alarm["alarm_id"],
                                    "include_related": True,
                                    "include_asset_context": True,
                                    "include_historical_pattern": True,
                                },
                            )
                            tool_trace.append({"step": "operator_recommendations", "tool_id": "operator_recommendations", "status": "success"})
                        except Exception as exc:
                            errors.append(f"Recommendations failed: {exc}")
                            recommendations = None
                    else:
                        priority = None
                        recommendations = None

                    rag_url = api_url.rstrip("/") + "/rag/search"
                    try:
                        rag_response = requests.get(rag_url, params={"query": query, "top_n": 4}, timeout=10).json()
                    except Exception as exc:
                        errors.append(f"RAG lookup failed: {exc}")
                        rag_response = {}

                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("Investigation Overview")
                        st.markdown(f"**Query:** {query}")

                        if asset_items:
                            st.markdown(f"**Resolved asset:** {asset.get('name')} ({asset_id})")

                        if metadata and metadata.get("result"):
                            st.markdown("### Asset metadata")
                            st.write(metadata["result"])

                        if alarm_list:
                            st.markdown("### Active and recent alarms")
                            for alarm in alarm_list:
                                st.markdown(f"**{alarm['alarm_name']}** — {alarm['severity'].upper()} — {alarm['status']}")
                                st.caption(f"{alarm['start_time']} · {alarm['description']}")

                        if priority and priority.get("result"):
                            st.markdown("### Alarm priority scoring")
                            st.write(priority["result"])

                        if recommendations and recommendations.get("result"):
                            st.markdown("### Operator recommendations")
                            for rec in recommendations["result"].get("recommendations", []):
                                st.markdown(f"**Step {rec['step']}:** {rec['action']}")
                                if rec.get("rationale"):
                                    st.caption(rec["rationale"])

                    with col2:
                        st.subheader("Document Evidence")
                        if rag_response and rag_response.get("results"):
                            for hit in rag_response["results"]:
                                st.markdown(f"**{hit['source']}** — score {hit['score']:.2f}")
                                st.write(hit["text"])
                        else:
                            st.info("No document evidence returned for this query.")

        if errors:
            st.error("Errors occurred during execution:")
            for error in errors:
                st.write(error)

        with st.expander("MCP tool trace"):
            st.write(tool_trace)

        with st.expander("Raw API / MCP responses"):
            st.write(
                {
                    "asset_search": asset_search_result,
                    "asset_metadata": metadata if "metadata" in locals() else None,
                    "alarms": alarms if "alarms" in locals() else None,
                    "priority": priority if "priority" in locals() else None,
                    "recommendations": recommendations if "recommendations" in locals() else None,
                    "rag": rag_response,
                }
            )
