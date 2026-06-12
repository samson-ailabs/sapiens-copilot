# 0002 — Middleware stack: reuse built-ins, build only the gap

- **Status**: Accepted
- **Date**: 2026-06-12
- **Module**: M2 (Middleware Stack)

## Context

The agent loop needs cross-cutting behaviour — planning, context management, approval
gates, retries, defensive repair — layered around the model. LangChain v1 supplies the
primitive for this: subclass `AgentMiddleware` and pass an ordered list to `create_agent`.

Two facts reshape what M2 should actually contain:

1. **Most middleware are now first-class built-ins.** LangChain v1 ships `TodoListMiddleware`
   (planning), `SummarizationMiddleware`, `HumanInTheLoopMiddleware`, model/tool retry, model/
   tool call limits, and more. Reimplementing them would be busywork, not pattern mastery.
2. **The full filesystem/scratch-space middleware is a Deep Agents component**
   (`deepagents.middleware.filesystem`), and importing `deepagents` is forbidden. LangChain's
   own built-in only offers read-only file *search*, not a write/edit scratch space.

So the question is not "build the whole list from scratch" but "what does Sapiens genuinely
need now, and which parts have no built-in?"

## Alternatives considered

- **Rebuild everything from primitives** (the original blueprint reading). Reinvents
  middleware that now ship with the framework; high effort, little portfolio value, and a
  maintenance burden that drifts from upstream. Rejected.
- **Reuse built-ins and still ship a filesystem + backend abstraction.** Not possible
  cleanly: the only full filesystem middleware is Deep Agents', which we cannot import, so
  this would mean rebuilding it anyway for a feature that is not core to a BI copilot.
  Rejected.

## Decision

M2 ships exactly two things:

1. **A composition mechanism** — [`build_middleware`](../../src/sapiens/middleware/stack.py)
   returns the ordered `list[AgentMiddleware]` passed to `create_agent`. This is the seam every
   later module plugs its middleware into, in its execution-order slot.
2. **`PatchToolCallsMiddleware`** ([patch.py](../../src/sapiens/middleware/patch.py)) — the one
   behaviour with no built-in equivalent. It answers any dangling tool call with a synthetic
   reply so a resumed thread (after an approval interrupt or a crash) presents a valid history
   the model provider will accept. Built from LangChain/LangGraph primitives only.

Everything else is **reused, not rebuilt**, and added by the module that owns it when it is
actually needed: planning and call limits with the reasoning loop (M5), context loading (M4),
approval gates (M6), summarization (M8). Filesystem and a pluggable storage backend are
**dropped** from scope — not core to the copilot, and revisited only if a later module needs
to offload large context.

## Consequences

- ✅ Far less code, idiomatic v1, and the `no deepagents import` rule stays intact.
- ✅ The composition seam is the durable deliverable; modules append their middleware without
  touching the kernel.
- ✅ `PatchToolCallsMiddleware` is fully unit-testable now (craft a dangling call, assert the
  synthetic reply) — no live model needed.
- ⚠️ M2's from-scratch footprint is small. Accepted: the portfolio's depth comes from the BI
  stack (M3), reasoning (M5), and the closed cognitive loop — not from reimplementing
  framework middleware.
- ℹ️ No scratch filesystem or backend protocol. If M3/M5 need to offload large results, add a
  minimal version then, against a concrete need.
