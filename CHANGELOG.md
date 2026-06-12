# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repo scaffold: `uv` package project (`src/sapiens`), baseline files, GitHub Actions CI
  (ruff + mypy + pytest).
- **M1 — Foundation**: `create_agent` kernel (`build_agent`), OpenRouter model wiring,
  process-wide tool registry, SQLite thread persistence, and a streaming CLI (`sapiens`).
  Documented in `docs/ARCHITECTURE.md`; SQLite lifecycle decision in ADR-0001.
