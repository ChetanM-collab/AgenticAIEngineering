from __future__ import annotations

import os
import datetime as dt
from typing import Any, Dict, Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.logging_utils import LoggerFactory, TraceContext
from core.llm_router import LLMRouter

LoggerFactory.configure()
log = LoggerFactory.get_logger("curiobot.curiobot_server")

router = LLMRouter()
mcp = FastMCP("curiobot_server")


@mcp.tool(
    name="get_weather",
    description="Weather via Open-Meteo for a location. 'when' accepts 'today'/'tomorrow'.",
)
async def get_weather(location: str, when: Optional[str] = None) -> Dict[str, Any]:
    log.info("curio Bot MCP Sever - get_weather invoked, location=%s, when=%s", location, when)

    async with httpx.AsyncClient(timeout=20) as client:
        geo = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1},
        )
        geo.raise_for_status()
        g = geo.json()

        if not g.get("results"):
            return {"ok": False, "error": "location_not_found"}

        r = g["results"][0]
        lat, lon = r["latitude"], r["longitude"]

        target_date = dt.date.today()
        if when and "tomorrow" in when.lower():
            target_date += dt.timedelta(days=1)

        weather = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "hourly": "temperature_2m,precipitation_probability,weathercode",
                "timezone": "auto",
                "forecast_days": 2,
            },
        )
        weather.raise_for_status()

        return {
            "ok": True,
            "location": r,
            "forecast": weather.json(),
            "target_date": str(target_date),
        }


@mcp.tool(name="get_news", description="Topical news via NewsAPI. Requires NEWSAPI_KEY env var.")
async def get_news(query: str| None = None, freshness_days: int = 3, topic: str | None = None) -> Dict[str, Any]:
    if not query and topic:
        query = topic

    if not query:
        return {"ok": False, "error": "query_missing", "received_args": {"topic": topic}}

    log.info("curio Bot MCP Sever - get_news invoked, query=%s, freshness_days=%s", query, freshness_days)

    key = os.getenv("NEWSAPI_KEY")
    if not key:
        return {"ok": False, "error": "NEWSAPI_KEY missing"}

    from_dt = (dt.datetime.utcnow() - dt.timedelta(days=freshness_days)).date().isoformat()

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "from": from_dt,
                "sortBy": "publishedAt",
                "pageSize": 5,
                "language": "en",
                "apiKey": key,
            },
        )

        if resp.status_code != 200:
            return {"ok": False, "status": resp.status_code, "text": resp.text}

        return {"ok": True, **resp.json()}


@mcp.tool(name="get_wiki", description="Wikipedia summary for a topic.")
async def get_wiki(topic: str) -> Dict[str, Any]:
    log.info("curio Bot MCP Sever - get_wiki invoked, topic=%s", topic)

    async with httpx.AsyncClient(timeout=20) as client:
        s = await client.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": topic,
                "format": "json",
            },
        )
        s.raise_for_status()

        items = s.json().get("query", {}).get("search", [])
        if not items:
            return {"ok": False, "error": "not_found"}

        title = items[0]["title"]
        e = await client.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + title
        )

        if e.status_code != 200:
            return {"ok": False, "status": e.status_code, "text": e.text}

        return {"ok": True, **e.json()}


@mcp.tool(
    name="query",
    description="Natural language router: decides among get_weather/get_news/get_wiki, or replies directly.",
)
async def query(question: str) -> Dict[str, Any]:
    """LLMRouter → plan = {"tool": ..., "args": {...}, "reason": ...}

    This MCP tool:
      - interprets the plan
      - calls the underlying tool (or does a direct answer)
      - returns:
        {
          "plan":   <plan dict>,
          "result": <tool_result_json | direct_answer_json>
        }
    """
    log.info("curio Bot MCP Sever - query tool invoked for question=%s", question)

    raw_plan = router.route(question)

    if hasattr(raw_plan, "model_dump"):
        plan = raw_plan.model_dump()
    elif isinstance(raw_plan, dict):
        plan = raw_plan
    else:
        plan = {"tool": "direct_answer", "args": {"answer": str(raw_plan)}, "reason": "non-dict plan from router"}

    toolname = plan.get("tool") or "direct_answer"
    args = plan.get("args") or {}

    log.info("query.plan.toolname=%s", toolname)
    log.info("query.plan.args=%s", args)

    if toolname == "get_weather":
        log.info("query: dispatching to get_weather")
        result = await get_weather(**args)

    elif toolname == "get_news":
        log.info("query: dispatching to get_news")
        result = await get_news(**args)

    elif toolname == "get_wiki":
        log.info("query: dispatching to get_wiki")
        result = await get_wiki(**args)

    elif toolname == "direct_answer":
        answer_text = args.get("answer") or "No answer provided by router."
        result = {"ok": True, "answer": answer_text}
        log.info("query: direct_answer used")

    else:
        log.warning("query: unknown tool '%s'; returning error result", toolname)
        result = {
            "ok": False,
            "error": "unknown_tool",
            "tool": toolname,
            "args": args,
        }

    return {"plan": plan, "result": result}


if __name__ == "__main__":
    log.info("MCP CurioBot server starting…")
    mcp.run(transport="stdio")
