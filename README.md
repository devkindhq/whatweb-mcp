# WhatWeb MCP Server: web technology fingerprinting for AI agents

WhatWeb MCP server lets Claude Code, Cursor, and any MCP client fingerprint websites and identify their CMS, web server, frameworks, and analytics tools. It runs WhatWeb in a hardened Docker container and returns a structured report in one tool call.

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

### Install in your client

Requirements:

- Docker
- Claude Desktop, Claude Code, Cursor, VS Code, Windsurf, or any other MCP client
- No API keys

**Standard config** works in most MCP clients:

```json
{
  "mcpServers": {
    "whatweb": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--memory=512m",
        "--cpus=0.5",
        "--pids-limit=100",
        "devkind/whatweb-mcp:latest"
      ]
    }
  }
}
```

<details>
<summary>Claude Desktop</summary>

Follow the MCP install [guide](https://modelcontextprotocol.io/quickstart/user) and add the standard config above to your `claude_desktop_config.json`.

</details>

<details>
<summary>Claude Code</summary>

Run:

```bash
claude mcp add whatweb -- docker run -i --rm --memory=512m --cpus=0.5 --pids-limit=100 devkind/whatweb-mcp:latest
```

Or add the standard config above to `.mcp.json` in your project root.

</details>

<details>
<summary>Cursor</summary>

#### Click the button to install:

[<img src="https://cursor.com/deeplink/mcp-install-dark.svg" alt="Install in Cursor">](https://cursor.com/en/install-mcp?name=WhatWeb%20MCP&config=eyJjb21tYW5kIjoiZG9ja2VyIiwiYXJncyI6WyJydW4iLCItaSIsIi0tcm0iLCItLW1lbW9yeT01MTJtIiwiLS1jcHVzPTAuNSIsIi0tcGlkcy1saW1pdD0xMDAiLCJkZXZraW5kL3doYXR3ZWItbWNwOmxhdGVzdCJdfQ%3D%3D)

#### Or install manually:

Go to `Cursor Settings` -> `MCP` -> `Add new MCP Server`. Name it "WhatWeb MCP", use `command` type with the command `docker run -i --rm --memory=512m --cpus=0.5 --pids-limit=100 devkind/whatweb-mcp:latest`.

</details>

<details>
<summary>VS Code</summary>

Follow the MCP install [guide](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_add-an-mcp-server) and use the standard config above. You can also install with the VS Code CLI:

```bash
code --add-mcp '{"name":"whatweb","command":"docker","args":["run","-i","--rm","--memory=512m","--cpus=0.5","--pids-limit=100","devkind/whatweb-mcp:latest"]}'
```

</details>

<details>
<summary>Windsurf</summary>

Follow the Windsurf MCP [documentation](https://docs.windsurf.com/windsurf/cascade/mcp) and use the standard config above.

</details>

<details>
<summary>Goose</summary>

Go to `Advanced settings` -> `Extensions` -> `Add custom extension`. Name it "WhatWeb MCP", use type `STDIO`, and set the `command` to `docker run -i --rm --memory=512m --cpus=0.5 --pids-limit=100 devkind/whatweb-mcp:latest`. Click "Add Extension".

</details>

<details>
<summary>LM Studio</summary>

Go to `Program` in the right sidebar -> `Install` -> `Edit mcp.json`. Use the standard config above.

</details>

<details>
<summary>Warp</summary>

Go to `Settings` -> `AI` -> `Manage MCP Servers` -> `+ Add` to [add an MCP Server](https://docs.warp.dev/knowledge-and-collaboration/mcp#adding-an-mcp-server). Use the standard config above, or use the slash command `/add-mcp` in the Warp prompt and paste it.

</details>

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

## Claude Code skill

This repo ships a ready-made agent skill at [`skills/tech-detector/SKILL.md`](skills/tech-detector/SKILL.md). It teaches Claude Code (or any skill-aware agent) when to scan a site, how to call `whatweb_scan`, and how to turn the raw technology list into a structured stack summary, business interpretation, and analysis angles — useful for lead qualification and competitor research. To install, copy the `skills/tech-detector/` directory into your project's `.claude/skills/` (or `~/.claude/skills/`) directory.

## Roadmap

- [x] Official MCP Registry listing (`io.github.devkindhq/whatweb-mcp`)
- [ ] Docker MCP Registry listing
- [ ] Batch scanning (multiple targets in one call)
- [ ] Optional CSV/JSON export tool
- [ ] Scheduled re-scans with diffing (alert when a target's stack changes)

## Built by

Built by [Devkind](https://devkind.com.au). Maintained by Kazim Ali.

## License

[MIT](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). WhatWeb itself is licensed by its upstream authors. Scan only targets you are authorized to scan.

## Qualifying leads by their tech stack?

Once you know what a site runs, Devkind can help you build on it. We work with [Shopify](https://devkind.com.au/services/shopify), [Swell](https://devkind.com.au/services/swell) and [headless commerce](https://devkind.com.au/services/headless-ecommerce) stacks, and build custom MCP servers and AI agent workflows. [Talk to Devkind](https://devkind.com.au/services) or email [hello@devkind.com.au](mailto:hello@devkind.com.au).
