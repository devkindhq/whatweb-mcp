# whatweb-mcp — Implementation Plan

Date: 2026-10-29
Design: docs/plans/2026-10-29-whatweb-mcp-design.md

Each task: write test → watch fail → implement → watch pass → commit.

## Task 1 — Project scaffold + test harness

- Files: `.gitignore`, `requirements.txt`, `tests/__init__.py` (empty), `tests/conftest.py`
  (sys.path bootstrap), `tests/test_validate_target.py`.
- Test first: `_validate_target` accepts `https://example.com`, `example.com`,
  `http://example.com/path`; rejects `-evil`, `ftp://x`, `''`, `'   '`.
- Implement: copy `server.py` from studio-marketplace as the module under test
  (importable; main() only runs under `__main__`).
- Commit.

## Task 2 — parse_whatweb_json tests

- `tests/test_parse.py`: real-shaped WhatWeb log-json (WordPress, nginx, jQuery
  with versions); malformed JSON → empty list, no raise; empty list input.
- Should pass against carried-over code; if a bug surfaces, fix minimally.
- Commit.

## Task 3 — store + summary tests

- `tests/test_store.py`: `_evict_if_needed` bounds at 100; `format_scan_summary`
  returns stable keys and caps technologies at 50.
- Commit.

## Task 4 — MCP stdio protocol test

- `tests/test_protocol.py`: spawn `python3 server.py` subprocess, JSON-RPC
  initialize (protocolVersion 2024-11-05) → notifications/initialized →
  tools/list → assert tools contain whatweb_scan, get_scan_results,
  list_active_scans; then shutdown cleanly.
- Needs mcp deps installed in a local venv (gitignored).
- Commit.

## Task 5 — Docker artifacts

- `Dockerfile`: carried-over alpine recipe, OCI source label →
  github.com/devkindhq/whatweb-mcp, .docker-annotations via buildx; `HEALTHCHECK` dropped
  (pgrep in stdio container is wrong layer? — keep as-is: it is proven upstream;
  decide: KEEP, don't redesign).
- `.dockerignore`: .git, tests, venv, docs, output.
- Commit.

## Task 6 — LICENSE, README, repo files

- MIT LICENSE, copyright Devkind.
- README.md per 8-section template, 400-700 words, example.com only.
- Commit.

## Task 7 — Full test run + safety pass

- Run pytest; all green.
- Secret scan of full history (grep per publish-safety.md) + client-name scan
  (no real client domains; every example uses example.com).
- Commit any fixes.

## Task 8 — Push + metadata + SEO audit

- Mint fresh GitHub token; push main.
- PATCH description + homepage; PUT topics.
- Run github-seo-skill scripts/check_repo_seo.py; fix failures.

## Task 9 — Multi-arch Docker build

- `docker buildx build --platform linux/amd64,linux/arm64` both tags
  (`latest`, `2026-10-29`); push if creds found, else local proof build.
- Verify on Docker Hub API (both arches) if pushed.

## Task 10 — Make public + verify

- PATCH visibility=public.
- Unauthenticated GET repo → confirm "private": false.
