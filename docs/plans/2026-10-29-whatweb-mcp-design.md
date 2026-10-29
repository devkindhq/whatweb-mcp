# whatweb-mcp — Design

Date: 2026-10-29
Repo: devkindhq/whatweb-mcp (new, standalone)
Upstream source: devkindhq/studio-marketplace `plugins/security/mcp/whatweb/` (untouched by this work)

## Problem

The WhatWeb MCP server currently lives as a subdirectory of the studio-marketplace
monorepo. It is not discoverable on GitHub for the query "whatweb mcp", and the
published Docker image `devkind/whatweb-mcp:latest` is linux/arm64 only, so amd64
users (the majority of Claude Code / Cursor desktop users) cannot pull and run it.
Ali wants a public, SEO-optimized standalone repo plus a multi-arch image.

## Goals

1. Standalone public repo `devkindhq/whatweb-mcp` with server.py, requirements.txt,
   multi-arch-capable Dockerfile, .dockerignore, MIT LICENSE, SEO README.
2. README follows the github-seo-skill 8-section template, 400-700 words, targeting
   "whatweb mcp".
3. Repo metadata: description, homepage (Docker Hub), 10 topics set via API.
4. Multi-arch image linux/amd64 + linux/arm64 built with buildx and pushed to
   devkind/whatweb-mcp (latest + date tag) — if Docker Hub credentials exist;
   otherwise prove both platforms build locally and report the blocker.
5. Safety pass before going public: no secrets, no client names/domains (LAW: anonymize
   with example.com).

## Non-goals

- No changes to devkindhq/studio-marketplace (another agent owns it).
- No new WhatWeb features; the server logic is carried over as-is apart from
  repo-specific fixes (labels, paths, metadata).
- No MCP registry submissions in this pass (separate distribution step).

## Approach

Carry the proven server.py from studio-marketplace (MCP stdio JSON-RPC over the
`mcp` Python SDK, three tools: whatweb_scan, get_scan_results, list_active_scans)
into a fresh repo with a clean single-purpose history. This is a publish/extract
task, not a rewrite: the code already works in production as part of the security
plugin. Changes to the code itself are limited to:

- Dockerfile OCI labels point at devkindhq/whatweb-mcp.
- Nothing else unless a test forces it.

### Architecture

```
Claude Code / Cursor  ──stdio JSON-RPC──▶  docker run -i --rm devkind/whatweb-mcp
                                              └─ python3 server.py  (MCP SDK)
                                                   └─ asyncio subprocess exec: whatweb <target>
                                                        └─ JSON log → parsed → ScanResult → tools/resources
```

### Testing (TDD)

server.py's pure logic is directly testable without Docker or network:

- `_validate_target`: rejects `-`-prefixed (flag-injection) targets, bad schemes,
  empty hosts; accepts bare domains and http(s) URLs.
- `parse_whatweb_json`: parses WhatWeb `--log-json` output into Technology lists
  and metadata; tolerates garbage.
- `format_scan_summary`: stable summary shape; caps technologies at 50.
- `_evict_if_needed`: result store bounded at MAX_RESULTS.
- Protocol test: spawn `python3 server.py` as a subprocess, speak MCP stdio
  JSON-RPC by hand (initialize → initialized → tools/list), assert the three tool
  names come back. No live scan in CI; the whatweb binary is not required for
  tools/list.

### Dockerfile

Same proven alpine recipe (ruby:3.2.8-alpine base — official image, multi-arch),
with corrected source label. Multi-arch is a build concern: `docker buildx build
--platform linux/amd64,linux/arm64`. Build both platforms locally even if push is
blocked, to prove the recipe compiles on both.

### SEO

- README from the 8-section template, 400-700 words, H1 contains "WhatWeb MCP
  server", quickstart uses `docker pull devkind/whatweb-mcp` + ready-paste
  .mcp.json, example tool call + output, roadmap, license.
- All examples use example.com. No client names anywhere.
- Description: "MCP server for WhatWeb — web technology fingerprinting for AI
  agents. Multi-arch Docker, works with Claude Code and Cursor."
- Homepage: https://hub.docker.com/r/devkind/whatweb-mcp
- Topics: whatweb, mcp, mcp-server, model-context-protocol, tech-detection,
  web-fingerprinting, recon, osint, claude, docker.
- Audit with github-seo-skill `scripts/check_repo_seo.py`.

## Release / publish sequence

1. Design doc committed.
2. Task-by-task plan committed.
3. Implement with tests; every task green before commit.
4. Safety scan of the full (new) history: gitleaks-style grep + client-name grep.
5. Push to main (repo is empty; direct push allowed).
6. Set description/homepage/topics via API. Run SEO audit.
7. Multi-arch build (+ push if creds).
8. PATCH visibility to public; verify with unauthenticated fetch.

## Risks

- No Docker Hub credentials on this host → push blocked. Mitigation: build both
  platforms locally without --push and report as blocker (never fake a push).
- arm64 build under qemu is slow (ruby native gems). Mitigation: background build
  with long timeout; it is a proof, not a release gate for the repo.
- `mcp==1.6.0` pip install needs to work on this host for tests. Mitigation: venv
  in the repo dir (gitignored).
