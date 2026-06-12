# 0001 — SQLite checkpointer connection lifecycle

- **Status**: Accepted
- **Date**: 2026-06-12
- **Module**: M1 (Foundation)

## Context

Sapiens has to remember a conversation across turns — and across restarts — so a user can
pick up where they left off. That history lives in a **checkpointer**, keyed by `thread_id`.

The library (`langgraph-checkpoint-sqlite`) gives us `SqliteSaver.from_conn_string(path)`: a
context manager that opens the SQLite connection — with `check_same_thread=False`, required
because LangGraph runs the graph on a worker thread — and closes it again on exit. Two things
it does *not* do for us:

1. It doesn't create the parent directory, so a default path like `data/threads.db` fails on
   a fresh checkout.
2. Every caller that wants durable storage has to wire up that `with` block itself.

And not every caller even *wants* a file: tests and library embeddings should run without
writing to disk. So the decision has to settle two questions — how to own the SQLite
connection cleanly, and what happens when no durable store is asked for.

## Alternatives considered

- **Open the connection by hand** (`sqlite3.connect(..., check_same_thread=False)` plus a
  `try/finally` to close it). This only reimplements what `from_conn_string` already does —
  same connection flags, same guaranteed close. Rejected: duplicating library code earns
  nothing and risks drifting from it.
- **A module-global singleton connection.** Convenient to call from anywhere, but it is hidden
  shared state: tests can't isolate it, ownership is unclear, and pointing at a different DB
  path is awkward. Rejected: trades testability for convenience.
- **The async saver, `AsyncSqliteSaver` (aiosqlite).** Only pays off on an async event loop;
  the M1 CLI is synchronous, so it adds machinery for no current benefit. Deferred until a
  module actually needs async persistence.

## Decision

Expose one project context manager, [`agent.open_checkpointer`](../../src/sapiens/agent.py),
that creates the parent directory and then delegates to `SqliteSaver.from_conn_string`. The
CLI holds it open for the whole REPL (`with open_checkpointer(...) as checkpointer:`), so the
connection lives exactly as long as the session and closes deterministically — no caller ever
touches the connection.

For the second question, `build_agent` defaults to an **in-memory** checkpointer when none is
injected. Library and test callers therefore never create a file by accident; durable storage
is opt-in, switched on by injecting an `open_checkpointer` saver — which is exactly what the
CLI does.

## Consequences

- ✅ We reuse the library's connection handling (right thread flag, guaranteed close) and add
  only the missing parent-directory step — no reimplementation, no reaching into internals.
- ✅ The default is in-memory, so there are no surprise files and nothing to leak; the durable
  path is explicit at the one call site that wants it.
- ✅ Tests follow those same two paths — `with open_checkpointer(...)` for durability, the
  default in-memory saver otherwise — and both clean themselves up.
- ✅ `check_same_thread=False` is safe, not a workaround: `sqlite3` is built in serialized mode
  (`threadsafety == 3`) and `SqliteSaver` serializes every access behind its own
  `threading.Lock`, so the connection is never used concurrently. This is the library's
  documented, recommended usage.
- ℹ️ Durability being opt-in means a caller that forgets to inject a saver silently gets
  in-memory. That is intended, and the CLI always injects — so the only durable consumer today
  can't get it wrong.

## Scope & scale-up

SQLite is the right backend for local, single-process development — the CLI, tests, demos:
zero setup, one file. It is not built for multi-user or production load, where its
single-writer model surfaces `database is locked` under concurrent writes.

When we serve concurrently (M9+), we swap to `langgraph-checkpoint-postgres` (`PostgresSaver`).
Because `build_agent` accepts any `BaseCheckpointSaver`, that is a one-line change at the
injection site, not a kernel change — which is the whole reason persistence is injected rather
than hardcoded.
