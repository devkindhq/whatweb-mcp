# WhatWeb MCP Server: web technology fingerprinting for AI agents

WhatWeb MCP server lets Claude Code, Cursor, and any Model Context Protocol client fingerprint websites and identify the technologies behind them: CMS platforms, web servers, JavaScript frameworks, analytics tools, and more. It runs WhatWeb inside a hardened Docker container over stdio, turning a domain into a structured technology report in one tool call.

Sales and prospecting teams use it to qualify leads; security teams use it for recon.

The server publishes three tools: `whatweb_scan` (scan a target at five aggression levels), `get_scan_results` (fetch a previous scan by ID), and `list_active_scans` (see what is running). Scans run in a sandboxed container with a non-root user, memory and CPU limits, and flag-injection validation on every target.

## Quickstart (Docker)

The image is multi-arch (linux/amd64 and linux/arm64), so the same tag works on Apple Silicon, x86 servers, and ARM cloud instances.

```bash
docker pull devkind/whatweb-mcp:latest
```

Ready-paste config for Claude Code or Cursor, saved as `.mcp.json` in your project root (or `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "whatweb": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--memory=512m", "--cpus=0.5", "--pids-limit=100", "devkind/whatweb-mcp:latest"]
    }
  }
}
```

Then ask your agent: *"What technologies does example.com run?"*

## Example tool call and output

```json
{ "tool": "whatweb_scan", "arguments": { "target": "https://example.com", "aggression": "normal" } }
```

```json
{
  "scan_id": "a1b2c3d4",
  "target": "https://example.com",
  "status": "completed",
  "http_status": 200,
  "stats": { "total_technologies": 3 },
  "technologies": [
    { "name": "nginx", "version": "1.25.3", "string": null },
    { "name": "WordPress", "version": "6.4.3", "string": "wp-content" },
    { "name": "jQuery", "version": "3.7.1", "string": "jquery.js" }
  ],
  "error": null
}
```

Aggression levels map to WhatWeb's `-a` flag: `stealthy`/`passive` (1, one request), `polite` (2), `normal` (3), `aggressive` (4, potentially intrusive, so use only on targets you are authorized to test).

## How it works

The container installs WhatWeb from the official upstream repository on an Alpine Ruby base, then runs a Python MCP server (`mcp` SDK, stdio transport). Each scan shells out with an argument array (no shell interpolation), writes WhatWeb's JSON log to an ephemeral `/app/output`, and parses it into typed results. Up to 100 scan results are kept in memory for follow-up questions in the same session. Tests cover target validation, JSON parsing, result-store bounds, and a live MCP stdio JSON-RPC handshake. Run them with `pytest`. Also installable from source without Docker: `pip install -r requirements.txt && python3 server.py` (requires WhatWeb on your PATH).

## Roadmap

- [ ] Submit to the official MCP Registry and Smithery
- [ ] Batch scanning (multiple targets in one call)
- [ ] Optional CSV/JSON export tool
- [ ] Scheduled re-scans with diffing (alert when a target's stack changes)

## Built by

Built by [Devkind](https://devkind.com.au). Maintained by Kazim Ali.

## License

[MIT](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). WhatWeb itself is licensed by its upstream authors. Scan only targets you are authorized to scan.
