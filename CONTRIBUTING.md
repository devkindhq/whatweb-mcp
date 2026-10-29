# Contributing to whatweb-mcp

Thanks for your interest in improving the WhatWeb MCP server.

## Ways to contribute

- Bug reports and feature ideas: open an issue with steps to reproduce.
- Tool output bugs: include the raw WhatWeb JSON log (redacted) and the parsed summary.
- Documentation: wording, examples, and registry listings all count.

## Development setup

```bash
git clone https://github.com/devkindhq/whatweb-mcp.git
cd whatweb-mcp
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt pytest
.venv/bin/python -m pytest
```

The test suite covers target validation, WhatWeb JSON parsing, the in-memory
result store, and a live MCP stdio JSON-RPC handshake. All tests must pass
before a PR is merged.

## Ground rules

- Keep changes minimal and focused; one concern per PR.
- New behavior needs a test first (TDD).
- Never commit client names, client domains, or secrets. Use `example.com` in
  every example.
- Scan only targets you own or are authorized to test.

## Pull requests

1. Fork, branch, commit with a clear message.
2. Ensure `pytest` passes.
3. Open the PR describing what changed and why.

## License

By contributing you agree your work is released under the MIT License.
