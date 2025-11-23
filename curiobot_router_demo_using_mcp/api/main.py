import os
import asyncio
import pathlib
from typing import Any, Dict

from fastapi import FastAPI
from dotenv import load_dotenv

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from agents.agent_output import AgentOutputSchema

from models.schemas import QueryRequest, QueryResult
from utils.logging_utils import LoggerFactory
from core.direct_answer import make_direct_answer
from core.openai_config import DEFAULT_MODEL

LoggerFactory.configure()
log = LoggerFactory.get_logger("curiobot.api.main_agent")

load_dotenv(override=True)

app = FastAPI(title="CurioBot API (Agent-powered)", version="0.1.0")


class AppState:
    def __init__(self) -> None:
        self.server: MCPServerStdio | None = None
        self.lock = asyncio.Lock()
        self.model = DEFAULT_MODEL

        self.instructions = """You are CurioBot, a routing and summarising assistant.

You have access to a single external MCP tool called `query`.

Your job is to:
1. Understand the user's question.
2. Decide whether you need external data (news, weather, Wikipedia).
3. If external data is needed, CALL the `query` tool with the user’s question.
4. Build a **QueryResult** object as your final output.

The QueryResult schema (your final answer) has these fields:

- tool (string)
  - The name of the tool that was ultimately used for the answer.
  - If you called the MCP `query` tool and it returned a plan, set this to `plan.tool`
    (typically "get_news", "get_weather" or "get_wiki").
  - If you did not need any external tool, set this to "none".

- args (object)
  - The arguments that were passed to the chosen tool.
  - If you called `query`, set this to `plan.args` from the MCP response.
  - If no tool was used, set this to {}.

- summary (string)
  - A clear, user-friendly explanation of the final answer.
  - This will be shown directly to the end user in the UI.
  - It should contain the key information from the tool result when a tool is used
    (e.g. for news: titles, sources, important details).

- raw_tool_output (object | null)
  - Optional.
  - If you call the MCP `query` tool, you may include a compact subset of `result`
    (for example, a list of top articles with title/source/url),
    so that the caller can inspect the raw data programmatically.
  - If you did not use a tool or do not need to expose raw data, set this to null.

Behavior rules:

- For questions that clearly require external data (e.g. “What’s the latest news about X?”,
  “What’s the weather in Sydney tomorrow?”, “Give me a summary of Y from Wikipedia”),
  YOU SHOULD call the MCP `query` tool exactly once with the user’s question.

- After you receive the MCP `query` response:
  - Read `plan.tool` and `plan.args`, and map them to QueryResult.tool and QueryResult.args.
  - Read `result` and use it to craft a concise, helpful `summary`.
  - Optionally put a simplified subset of `result` into `raw_tool_output`.

- For purely conceptual questions that do not need external data, you MAY skip calling `query`.
  - In that case, set:
    - tool = "none"
    - args = {}
    - summary = your own direct answer
    - raw_tool_output = null

Very important:
- Your final output MUST be a valid QueryResult object and nothing else.
- Do NOT wrap the output in markdown code fences.
- Do NOT include any extra prose outside the fields of the QueryResult.
"""


state = AppState()


@app.on_event("startup")
async def on_startup():
    project_root = pathlib.Path(os.getcwd())
    child_env = dict(os.environ)
    child_env.setdefault("PYTHONUNBUFFERED", "1")
    child_env["PYTHONPATH"] = str(project_root) + (
        ":" + child_env["PYTHONPATH"] if "PYTHONPATH" in child_env else ""
    )

    child_env.setdefault("LOG_LEVEL", "INFO")
    child_env.setdefault("LOG_JSON", "false")
    child_env["LOG_FILE"] = str(project_root / "logs" / "curiobot_agent.log")
    child_env["OPENAI_LOG"] = "debug"

    params = {
        "command": os.environ.get("PYTHON") or os.sys.executable,
        "args": ["-m", "server.curiobot_server"],
        "env": child_env,
    }

    server = MCPServerStdio(params=params, client_session_timeout_seconds=120)
    await server.__aenter__()
    state.server = server
    log.info("[startup] MCP server started for FastAPI")


@app.on_event("shutdown")
async def on_shutdown():
    if state.server is not None:
        await state.server.__aexit__(None, None, None)
        state.server = None
        log.info("[shutdown] MCP server stopped")


@app.get("/health")
async def health():
    return {"ok": True, "model": state.model, "mcp": bool(state.server)}


@app.post("/query", response_model=QueryResult)
async def query(payload: Dict[str, Any]) -> QueryResult:
    question = (payload.get("question") or "").strip()
    log.info("Question=%s", question)

    if not question:
        return QueryResult(**make_direct_answer(
            summary="Please provide a question.",
            reason="empty_input",
            ok=False,
        ))

    if state.server is None:
        return QueryResult(**make_direct_answer(
            summary="MCP server not available",
            reason="mcp_server_unavailable",
            ok=False,
        ))

    log.info("Creating Agent")
    agent = Agent(
        name="curiobot_router_agent",
        instructions=state.instructions,
        model=state.model,
        mcp_servers=[state.server],
        output_type=AgentOutputSchema(QueryResult, strict_json_schema=False),
    )

    log.info("Running Agent")
    async with state.lock:
        run_result = await Runner.run(agent, input=question)
        result: QueryResult = run_result.final_output

    log.info("Agent tool=%s", result.tool)
    log.info("Agent args=%s", result.args)
    log.info("Agent summary=%s", result.summary)
    log.info(
        "Agent raw_tool_output keys=%s",
        list(result.raw_tool_output.keys()) if result.raw_tool_output else None,
    )

    return result
