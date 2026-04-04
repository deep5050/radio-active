"""Tests for radioactive.app.App (no network in normal paths)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from radioactive.app import App


def test_get_version_returns_non_empty_string():
    app = App()
    version = app.get_version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_is_update_available_false_when_remote_not_greater():
    app = App()
    app._App__VERSION__ = "3.0.3"
    payload = {"info": {"version": "3.0.3"}}
    mock_resp = MagicMock()
    mock_resp.content = json.dumps(payload).encode("utf-8")

    with patch("requests.get", return_value=mock_resp):
        assert app.is_update_available() is False
    assert app.get_remote_version() == "3.0.3"


def test_is_update_available_true_when_remote_is_newer():
    app = App()
    app._App__VERSION__ = "1.0.0"
    payload = {"info": {"version": "9.0.0"}}
    mock_resp = MagicMock()
    mock_resp.content = json.dumps(payload).encode("utf-8")

    with patch("requests.get", return_value=mock_resp):
        assert app.is_update_available() is True


def test_is_update_available_handles_request_errors():
    app = App()
    with patch("requests.get", side_effect=OSError("network down")):
        # On failure the implementation prints and falls through without returning False.
        assert not app.is_update_available()
