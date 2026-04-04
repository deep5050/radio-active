"""Tests for pure logic in radioactive.actions."""

import pytest

from radioactive.actions import check_sort_by_parameter


@pytest.mark.parametrize(
    "sort_by",
    [
        "name",
        "votes",
        "codec",
        "bitrate",
        "lastcheckok",
        "lastchecktime",
        "clickcount",
        "clicktrend",
        "random",
    ],
)
def test_check_sort_by_parameter_accepts_known_values(sort_by):
    assert check_sort_by_parameter(sort_by) == sort_by


def test_check_sort_by_parameter_unknown_falls_back_to_name():
    assert check_sort_by_parameter("not-a-real-sort-key") == "name"
