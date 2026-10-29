"""Tests for target validation (flag-injection and malformed-input guard)."""

import pytest

import server


@pytest.mark.parametrize(
    "target",
    [
        "https://example.com",
        "http://example.com/path",
        "example.com",
        "example.com/some/page",
        "  https://example.com  ",
    ],
)
def test_accepts_valid_targets(target):
    assert server._validate_target(target) is None


@pytest.mark.parametrize(
    "target",
    [
        "-evil",          # would be parsed as a whatweb flag
        "--log-json=x",   # explicit flag injection attempt
        "ftp://example.com",
        "javascript:alert(1)",
        "",
        "   ",
    ],
)
def test_rejects_invalid_targets(target):
    assert server._validate_target(target) is not None
