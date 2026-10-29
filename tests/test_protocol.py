"""Protocol test: speak MCP stdio JSON-RPC to a spawned server.py.

Does not require the whatweb binary — only initialize + tools/list, no scans.
"""

import json
import os
import subprocess
import sys
import textwrap

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# server.py hard-creates WHATWEB_OUTPUT_DIR on startup; point it somewhere writable.
ENV = dict(
    os.environ,
    WHATWEB_OUTPUT_DIR=os.path.join(REPO_ROOT, "output"),
)


def _read_message(proc, timeout=15.0):
    import selectors

    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)
    try:
        while True:
            events = sel.select(timeout)
            if not events:
                raise TimeoutError("no message from server within timeout")
            line = proc.stdout.readline()
            if not line:
                raise EOFError("server closed stdout")
            line = line.strip()
            if not line.startswith(b"{"):
                continue  # skip any log lines
            return json.loads(line)
    finally:
        sel.close()


def test_stdio_initialize_and_list_tools():
    proc = subprocess.Popen(
        [sys.executable, os.path.join(REPO_ROOT, "server.py")],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=ENV,
    )
    try:
        # 1. initialize
        proc.stdin.write(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "0.0.0"},
            },
        }).encode() + b"\n")
        proc.stdin.flush()
        init = _read_message(proc)
        assert init["id"] == 1
        assert "result" in init, f"initialize failed: {init}"
        assert "serverInfo" in init["result"]
        assert init["result"]["serverInfo"]["name"] == "whatweb-mcp"

        # 2. initialized notification
        proc.stdin.write(json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }).encode() + b"\n")
        proc.stdin.flush()

        # 3. tools/list
        proc.stdin.write(json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
        }).encode() + b"\n")
        proc.stdin.flush()
        listing = _read_message(proc)
        assert listing["id"] == 2
        tool_names = {t["name"] for t in listing["result"]["tools"]}
        assert tool_names == {
            "whatweb_scan",
            "get_scan_results",
            "list_active_scans",
        }

        # 4. clean shutdown
        proc.stdin.write(json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "ping",
        }).encode() + b"\n")
        proc.stdin.flush()
        pong = _read_message(proc)
        assert pong["id"] == 3 and "result" in pong
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait(timeout=10)
    # 0 = clean EOF exit; -15 = we had to SIGTERM it. Both mean no crash.
    assert proc.returncode in (0, -15), proc.returncode
