"""Tests for WhatWeb JSON output parsing."""

import json

import server


WHATWEB_SAMPLE = json.dumps([
    {
        "target": "https://example.com",
        "http_status": 200,
        "request_config": {},
        "plugins": {
            "WordPress": {"version": ["6.4.3"], "string": ["wp-content"], "certainty": 100},
            "nginx": {"version": ["1.25.3"], "certainty": 100},
            "jQuery": {"version": ["3.7.1"], "string": ["jquery.js"], "certainty": 100},
            "HTML5": {"string": ["HTML5 video"], "certainty": 100},
        },
    }
])


def test_parses_technologies_with_versions():
    techs, meta = server.parse_whatweb_json(WHATWEB_SAMPLE)
    by_name = {t.name: t for t in techs}
    assert by_name["WordPress"].version == "6.4.3"
    assert by_name["WordPress"].string == "wp-content"
    assert by_name["nginx"].version == "1.25.3"
    assert by_name["HTML5"].version is None
    assert len(techs) == 4


def test_parses_metadata():
    _, meta = server.parse_whatweb_json(WHATWEB_SAMPLE)
    assert meta["http_status"] == 200
    assert meta["target"] == "https://example.com"


def test_malformed_json_returns_empty():
    techs, meta = server.parse_whatweb_json("not json at all {{{")
    assert techs == []
    assert meta == {}


def test_empty_list_returns_empty():
    techs, meta = server.parse_whatweb_json("[]")
    assert techs == []
    assert meta == {}


def test_plugin_data_as_non_dict_is_tolerated():
    sample = json.dumps([{"target": "https://example.com", "plugins": {"Custom": ["str"]}}])
    techs, _ = server.parse_whatweb_json(sample)
    assert [t.name for t in techs] == ["Custom"]
