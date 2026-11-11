"""Tests for the aggression level map."""

import pytest

import server

# WhatWeb 0.6.4 exits with an error for every other -a value.
WHATWEB_LEVELS = {1, 3, 4}


@pytest.mark.parametrize("name", sorted(server.AGGRESSION_LEVELS))
def test_each_name_maps_to_a_level_whatweb_accepts(name):
    assert server.AGGRESSION_LEVELS[name] in WHATWEB_LEVELS
