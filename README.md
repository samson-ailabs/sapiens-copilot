<div align="center">

# 🧠 Sapiens

### The embedded BI copilot for the apps your team already uses.

[![CI](https://github.com/samson-ailabs/sapiens-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/samson-ailabs/sapiens-copilot/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![LangChain v1](https://img.shields.io/badge/LangChain-v1-1C3C3C.svg)](https://python.langchain.com/)
[![LangGraph v1](https://img.shields.io/badge/LangGraph-v1-1C3C3C.svg)](https://langchain-ai.github.io/langgraph/)

</div>

---

Sapiens is a knowledge-worker copilot that lives **inside the host app your team is already
in** — a chat widget embedded in the UI, not yet another tab to switch to. Ask a question in
plain language and Sapiens retrieves across your **data and your documents**, reasons over
both, and takes action in the host app on your behalf — saving a report, scheduling an
alert, sharing a dashboard — pausing for your approval when an operation is sensitive.

It is built end-to-end from **LangChain / LangGraph v1 primitives** — no high-level agent
framework on top, so the patterns stay visible in the code. The codebase is a reusable
harness: swap the backend services it talks to and the same copilot embeds into analytics,
banking, ERP, CRM, or helpdesk.

### One question, end to end

> **You** — *"Why did revenue dip in Q2 — and alert me if it happens again."*

Sapiens answers in a single turn, without ever leaving the dashboard:

- 📊 &nbsp; **Queries** the database with Text-to-SQL **and** pulls the Q2 incident runbook via document RAG
- 🧩 &nbsp; **Explains** the dip by synthesizing data and docs together — with citations
- 🔔 &nbsp; **Offers** to schedule a recurring revenue-drop alert, and waits for your approval before acting

## Why embedded?

The dominant pattern in enterprise AI is the **embedded copilot** — Rovo in Jira, Notion AI
in Notion, Copilot in VS Code, Einstein in Salesforce. The assistant lives where the work
already happens instead of forcing a context switch. Sapiens demonstrates that pattern
end-to-end inside **Acme Analytics**, a minimal data dashboard built to host it, running
over a synthetic enterprise dataset — so every capability is shown in a realistic setting,
with zero real customer data.

## Five cognitive capabilities

| | Capability | What the copilot does |
|---|---|---|
| 🧭 | **Understand** | Parses intent, loads identity + current context (active dashboard, recent queries), scopes to who is asking. |
| 📚 | **Know** | Agentic BI stack — a semantic layer of business metrics, schema-aware **Text-to-SQL** with query validation, and **doc RAG** (hybrid retrieval + citations) over runbooks and policies. |
| 🧩 | **Reason** | Routes via tool-use (the model decides which Know tools to call and how to compose them), decomposes heavy work across isolated sub-agents, and synthesizes across data + docs. |
| ⚡ | **Act** | Calls host-app APIs over MCP — save reports, schedule alerts, share dashboards, annotate — each gated by a per-tool approval policy. |
| 🔁 | **Adapt** | Recalls relevant memory before reasoning, summarizes long context, and writes memory back across distinct categories with their own semantics. |

**Knowledge** (retrieval) and **Action** (execution) are commodity plumbing — any team can
wire up SQL or an MCP call. The defensible part is the **closed cognitive loop** around
them: decide what to do, combine across sources, remember across sessions, and gate
sensitive operations behind a human. That loop is what turns plumbing into a copilot.

## Status & roadmap

🚧 **Early development.** The foundation is in — a working `create_agent` kernel with a
streaming CLI and persistent conversations. The five capabilities land across three stages:

- **Ship 1 — Foundation, Middleware, Knowledge.** Answer data questions (Text-to-SQL) and
  explanation questions (doc RAG) inside the Acme Analytics shell, with cross-source
  synthesis and citations.
- **Ship 2 — Understand, Reason, HITL, Act.** Context-aware reasoning across docs + DB;
  calls host APIs to save reports and schedule alerts; approval gates on sensitive actions.
- **Ship 3 — Adapt, Integration, Eval & Deploy.** Memory, the signature end-to-end
  workflow, eval scores, and a hosted demo.

## Tech stack

- **Python 3.12+**, managed with [`uv`](https://docs.astral.sh/uv/).
- **LangChain v1** (`>=1.3,<2`) + **LangGraph v1** (`>=1.2,<2`) — primitives only.
- **OpenRouter** as the single LLM gateway (model chosen by string).

## Quickstart

```bash
uv sync                 # create .venv and install dependencies

uv run ruff check .     # lint
uv run ruff format .    # format
uv run mypy             # type-check
uv run pytest           # run tests
```

## License

[Apache-2.0](LICENSE). Synthetic data only — Sapiens ships with no real customer data.
