"""Tests for Last_station with an isolated path."""

import json
from unittest.mock import patch

from radioactive.last_station import Last_station


def test_last_station_save_and_get_info(tmp_path):
    path = tmp_path / "last_station.json"
    data = {"name": "Test FM", "stationuuid": "abc-123", "uuid_or_url": "abc-123"}

    with patch("radioactive.paths.get_last_station_path", return_value=str(path)):
        ls = Last_station()
        assert ls.get_info() == ""

        ls.save_info(data)

    with patch("radioactive.paths.get_last_station_path", return_value=str(path)):
        ls = Last_station()
        loaded = ls.get_info()

    assert loaded == data
    assert json.loads(path.read_text(encoding="utf-8")) == data
