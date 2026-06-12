# Architecture Decision Records

ADRs capture non-obvious or hard-to-reverse decisions: the context, the choice, and the
trade-offs we accepted. One file per decision, numbered sequentially.

## Index

| # | Title | Status |
|---|-------|--------|
| [0001](0001-sqlite-checkpointer-lifecycle.md) | SQLite checkpointer connection lifecycle | Accepted |

## Template

```markdown
# NNNN — <title>

- **Status**: Proposed | Accepted | Superseded by [NNNN](NNNN-....md)
- **Date**: YYYY-MM-DD
- **Module**: <Mx>

## Context
What forces are at play? What problem are we solving?

## Alternatives considered
The options weighed, and why each was rejected. (Omit if there was genuinely one path.)

## Decision
What did we choose, stated plainly?

## Consequences
What becomes easier, what becomes harder, what we accept as the trade-off.
```
