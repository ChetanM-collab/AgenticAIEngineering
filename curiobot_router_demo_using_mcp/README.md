# CurioBot – AI Router + MCP Server + FastAPI + Gradio UI

CurioBot is an end-to-end AI system that demonstrates dynamic tool routing, external MCP tools, and a friendly Gradio UI, powered by:

- FastAPI – High-performance backend API
- OpenAI LLMs – Router/agent reasoning
- OpenAI MCP Server – Weather / News / Wikipedia tools
- Agents Framework – Schema-safe agent execution
- Gradio – Live interactive web UI
- Python 3.12 – Async-first backend
- httpx + asyncio – Efficient async API calls

This project serves as a production-ready reference for:
- Routing external tools via LLM
- Building and hosting MCP tools
- Running Agents over STDIO transports
- Building a rich UI with plan/summary/raw result panels
- Clean, extensible architecture

## What the Project Does

CurioBot accepts any natural language question and:
1. Routes it using an LLM Router.
2. Calls the appropriate MCP tool.
3. FastAPI Agent returns QueryResult with tool, args, summary, raw output.
4. Gradio UI displays plan/result/history + article details.

## Technologies Used

### Backend
- FastAPI
- Agents Framework
- Pydantic v2
- Uvicorn

### AI / LLM
- OpenAI GPT models (`gpt-4o-mini`)
- JSON mode output

### MCP Server
- openai-mcp / FastMCP
- Tools: get_weather, get_news, get_wiki, query

### UI
- Gradio 4.x
- Custom CSS theme

## Project Structure

```
curiobot_router_demo/
├── api/main.py
├── gradio_app/gradio_ui.py
├── server/curiobot_server.py
├── core/llm_router.py
├── models/schemas.py
├── utils/logging_utils.py
└── run.sh
```

## Installation

Clone repo:
```
git clone https://github.com/yourname/curiobot_router_demo.git
```

Create venv:
```
cd curiobot_router_demo_using_mcp

python3.12 -m venv .venv
source .venv/bin/activate
```

Install deps:
```
pip install -r requirements.txt
```

Create `.env`:
```
OPENAI_API_KEY=your_key_here
NEWSAPI_KEY=your_newsapi_key
MODEL_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
API_BASE=http://localhost:7421
```

## Run Everything

```
chmod +x run.sh
./run.sh
```

UI → http://127.0.0.1:7860  
API → http://127.0.0.1:7421

## API Usage

Health:
```
curl http://localhost:7421/health
```

Query:
```
curl -X POST http://localhost:7421/query -H "Content-Type: application/json" -d '{"question":"latest news about 3I/ATLAS"}'
```

## Extending

- Add new MCP tools → server/
- Extend router → core/llm_router.py
- Modify schemas → models/
- Modify UI → gradio_app/

### Acknowledgement

A huge thank you to **Ed Donner** and his amazing Udemy course **Agentic AI Engineering**.  
This **CurioBot MCP + Agentic AI** project was built while following and practising concepts from his lessons.  
Ed’s clear explanations and real-world demos made a big difference in understanding how to build real agent systems.