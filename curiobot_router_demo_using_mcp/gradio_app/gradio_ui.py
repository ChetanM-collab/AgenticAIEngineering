import os
import json
import httpx
import gradio as gr

API_BASE = os.getenv("API_BASE", "http://localhost:7421")


async def api_health() -> dict:
    url = f"{API_BASE}/health"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()


async def api_query(question: str) -> dict:
    url = f"{API_BASE}/query"
    payload = {"question": (question or "").strip()}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()


async def check_health():
    try:
        data = await api_health()
        return f"✅ API healthy: {json.dumps(data)}"
    except Exception as e:
        return f"❌ API not reachable: {e}"


async def ask(question, history):
    question = (question or "").strip()
    # history will be a list of {"role": ..., "content": ...} dicts (messages format)
    history = history or []

    if not question:
        gr.Warning("Please enter a question.")
        return gr.update(), gr.update(), history

    try:
        data = await api_query(question)
        tool = data.get("tool", "none")
        args = data.get("args", {}) or {}
        summary = data.get("summary", "") or ""
        raw_tool_output = data.get("raw_tool_output") or {}
        plan_obj = {"tool": tool, "args": args}
        plan_md = (
            "### 🔎 Router Plan\n```json\n"
            + json.dumps(plan_obj, indent=2)[:4000]
            + "\n```"
        )

        articles_md = []
        if isinstance(raw_tool_output, dict):
            articles = raw_tool_output.get("articles") or []
            for art in articles:
                title = art.get("title", "Untitled")
                url = art.get("url") or ""

                header_line = f"**[{title}]({url})**" if url else f"**{title}**"
                parts = [header_line]
                articles_md.append("".join(parts))

        extended_summary = summary or "_(no summary)_"
        if articles_md:
            extended_summary += "\n\n---\n\n" + "\n\n---\n\n".join(articles_md)

        result_md_parts = ["### 📦 Result", extended_summary]
        if isinstance(raw_tool_output, dict) and raw_tool_output:
            result_md_parts.append(
                "\n<details><summary>Raw JSON</summary>\n\n```json\n"
                + json.dumps(raw_tool_output, indent=2)[:4000]
                + "\n```\n</details>"
            )

        result_md = "\n".join(result_md_parts)

        # 👉 Chatbot expects messages format: list of {"role", "content"} dicts
        history.append({"role": "user", "content": question})
        history.append(
            {
                "role": "assistant",
                "content": f"**Plan**\n\n{plan_md}\n\n**Result**\n\n{result_md}",
            }
        )

        return plan_md, result_md, history

    except httpx.HTTPStatusError as e:
        err_md = f"❌ Error {e.response.status_code}\n```\n{e.response.text}\n```"
        gr.Error(f"Server returned {e.response.status_code}")
        return err_md, err_md, history
    except Exception as e:
        err_md = f"❌ Request failed: {e}"
        gr.Error(str(e))
        return err_md, err_md, history


def clear_all():
    # history reset to empty messages list
    return "", [], "", ""


theme = gr.themes.Soft(primary_hue="green", neutral_hue="gray")

custom_css = """
:root {
  --bg: #F6FAF7;
  --text: #132019;
  --muted: #5B6B60;
  --card: #FFFFFF;
  --card-border: #DDE7E1;
  --shadow: 0 6px 22px rgba(16, 24, 20, 0.08);
  --accent: #10B981;
  --accent-strong: #0EA371;
  --accent-soft: #E6F5EE;
}

body {
  background: var(--bg) !important;
  color: var(--text) !important;
}

.gradio-container {
  max-width: 980px !important;
  margin: auto;
}

#header h1 {
  font-weight: 700;
  letter-spacing: 0.2px;
  margin: 0 0 6px 0;
  color: var(--text);
}
#header p {
  margin: 0;
  color: var(--muted);
}

.card {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 16px;
  box-shadow: var(--shadow);
}

.result md, .result markdown { line-height: 1.55; }

.footer { opacity: 0.85; font-size: 12px; color: var(--muted); }

button, .gr-button {
  border-radius: 10px !important;
}

button.primary, .gr-button-primary {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: white !important;
}
button.primary:hover, .gr-button-primary:hover {
  background: var(--accent-strong) !important;
  border-color: var(--accent-strong) !important;
}

button.secondary, .gr-button-secondary {
  background: var(--accent-soft) !important;
  border-color: var(--card-border) !important;
  color: var(--text) !important;
}
button.secondary:hover, .gr-button-secondary:hover {
  background: #DBF1E7 !important;
}

textarea, input, .gr-text-input, .gr-textbox {
  background: #FFFFFF !important;
  border-color: var(--card-border) !important;
  color: var(--text) !important;
}
"""


with gr.Blocks(title="CurioBot – Weather/News/Wiki") as demo:
    gr.HTML(
        """
        <div id="header" class="card">
          <h1>🌿 CurioBot — Router Demo</h1>
          <p>Ask questions about weather, news or wiki. The router will choose <code>get_weather</code>, <code>get_news</code>, or <code>get_wiki</code> via your FastAPI backend.</p>
        </div>
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            question = gr.Textbox(
                label="Your question",
                placeholder="e.g., What's the weather like in Sydney tomorrow?",
                lines=2,
                autofocus=True,
            )
        with gr.Column(min_width=180):
            ask_btn = gr.Button("Ask 🚀", variant="primary")
            health_btn = gr.Button("🩺 Check API", variant="secondary")
            clear_btn = gr.Button("🧹 Clear", variant="secondary")

    with gr.Row():
        with gr.Column():
            plan_panel = gr.Markdown(label="Plan", elem_classes=["result", "card"])
        with gr.Column():
            result_panel = gr.Markdown(label="Result", elem_classes=["result", "card"])

    with gr.Row():
        # No 'type' kwarg here – we use the default messages format
        chat_hist = gr.Chatbot(
            label="History",
            elem_classes=["card"],
            height=320,
        )

    gr.HTML(
        """
        <div class="footer" style="margin-top:10px;text-align:center;">
          Built with <b>FastAPI</b> + <b>Gradio</b>.
          <br>Set <code>API_BASE</code> if your API is on a different host/port.
        </div>
        """
    )

    question.submit(
        fn=ask,
        inputs=[question, chat_hist],
        outputs=[plan_panel, result_panel, chat_hist],
    )
    ask_btn.click(
        fn=ask,
        inputs=[question, chat_hist],
        outputs=[plan_panel, result_panel, chat_hist],
    )
    health_btn.click(fn=check_health, outputs=[result_panel])
    clear_btn.click(
        fn=clear_all,
        outputs=[question, chat_hist, plan_panel, result_panel],
    )

if __name__ == "__main__":
    demo.queue().launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=False,   # set True if you want auto-open; ignore gio warning if any
        theme=theme,
        css=custom_css,
    )
