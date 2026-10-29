"""Tests for the in-memory result store and summary formatting."""

import uuid
from datetime import datetime

import server


def _mk_result(target="https://example.com"):
    return server.ScanResult(
        scan_id=str(uuid.uuid4())[:8],
        target=target,
        started_at=datetime.now(),
        status="completed",
    )


def test_evict_bounds_store_at_max_results():
    store = {}
    for _ in range(server.MAX_RESULTS + 10):
        r = _mk_result()
        store[r.scan_id] = r
        server._evict_if_needed(store)
    assert len(store) == server.MAX_RESULTS


def test_format_scan_summary_keys():
    r = _mk_result()
    r.http_status = 200
    r.technologies = [server.Technology(name=f"Tech{i}") for i in range(80)]
    summary = server.format_scan_summary(r)
    assert set(summary.keys()) == {
        "scan_id", "target", "status", "http_status", "stats",
        "technologies", "error",
    }
    assert len(summary["technologies"]) == 50  # capped
    assert summary["technologies"][0]["name"] == "Tech0"
