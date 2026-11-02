"""Tests for resources/read through the registered MCP handler."""

import asyncio
import json

from mcp import types

import server


def test_read_unknown_result_returns_not_found():
    handler = server.app.request_handlers[types.ReadResourceRequest]
    req = types.ReadResourceRequest(
        method="resources/read",
        params=types.ReadResourceRequestParams(uri="whatweb://results/missing"),
    )
    result = asyncio.run(handler(req))
    text = result.root.contents[0].text
    assert json.loads(text) == {"error": "Resource not found"}
