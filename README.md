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

Or add the standard config above to `.mcp.json` in your project root, or install the [Claude Code plugin](#claude-code-plugin).

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

Aggression levels map to WhatWeb's `-a` flag: `stealthy`/`passive`/`polite` (1, one request), `normal` (3), `aggressive` (4, potentially intrusive, so use only on targets you are authorized to test).

## How it works

The container installs WhatWeb from the official upstream repository on an Alpine Ruby base, then runs a Python MCP server (`mcp` SDK, stdio transport). Each scan shells out with an argument array (no shell interpolation), writes WhatWeb's JSON log to an ephemeral `/app/output`, and parses it into typed results. Up to 100 scan results are kept in memory for follow-up questions in the same session. Tests cover target validation, JSON parsing, result-store bounds, and a live MCP stdio JSON-RPC handshake. Run them with `pytest`. Also installable from source without Docker: `pip install -r requirements.txt && python3 server.py` (requires WhatWeb on your PATH).

## Network access and data

- The plugin starts the server with `docker run`, so Docker downloads the `devkind/whatweb-mcp:latest` image from Docker Hub on first use. Later runs use the local copy until you run `docker pull devkind/whatweb-mcp:latest`. Docker must be installed and running.
- Each scan sends HTTP requests from your machine to the target you give, with the user agent `WhatWeb/0.6.4`. WhatWeb follows up to 10 redirects, also to other hosts. The `aggressive` level sends many more requests than `stealthy`.
- The tool result carries the target's HTTP status, the detected technologies, their versions and the matched strings.
- The server sends no telemetry and calls no other service. It writes logs to stderr only.
- The server keeps up to 100 scan results in memory and writes each WhatWeb JSON log inside the container. `--rm` deletes the container and its logs when the session ends.

## Claude Code plugin

The repository root is a Claude Code plugin. It adds the WhatWeb MCP server and the [`tech-detector`](skills/tech-detector/SKILL.md) skill. The skill teaches Claude when to scan a site, how to call `whatweb_scan`, and how to turn the technology list into a stack summary and analysis angles for lead qualification and competitor research.

Install it now (Claude Code 2.1.275 or later):

```
/plugin install whatweb --marketplace devkindhq/whatweb-mcp
```

On older Claude Code versions, use the `claude mcp add` command in [Install in your client](#install-in-your-client). To use only the skill in another agent, copy `skills/tech-detector/` into your project's `.claude/skills/` (or `~/.claude/skills/`) directory.

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
