"""Tests for the airport_board plugin."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from plugins.airport_board import AirportBoardPlugin
from src.plugins.base import PluginResult

MANIFEST = json.loads("""
{
    "id": "airport_board",
    "name": "Airport Board",
    "version": "0.1.0",
    "settings_schema": {
        "type": "object",
        "properties": {
            "enabled": {
                "type": "boolean",
                "title": "Enabled",
                "default": false
            },
            "latitude": {
                "type": "number",
                "title": "Airport Latitude",
                "description": "Latitude of the airport (decimal degrees).",
                "default": 37.6213
            },
            "longitude": {
                "type": "number",
                "title": "Airport Longitude",
                "description": "Longitude of the airport (decimal degrees).",
                "default": -122.379
            },
            "radius_deg": {
                "type": "number",
                "title": "Search Radius (degrees)",
                "description": "Search radius in degrees (\u22481\u00b0 = 111 km). Default 1.0.",
                "default": 1.0,
                "minimum": 0.1,
                "maximum": 5.0
            },
            "airport_name": {
                "type": "string",
                "title": "Airport Name",
                "description": "Display name shown on the board (e.g. SFO).",
                "default": "SFO"
            },
            "refresh_seconds": {
                "type": "integer",
                "title": "Refresh Interval (seconds)",
                "description": "How often to poll. Anonymous tier: keep \u2265300s to stay under 400 req/day.",
                "default": 300,
                "minimum": 120
            }
        },
        "required": [
            "latitude",
            "longitude"
        ]
    }
}
""")

SAMPLE_RESPONSE = json.loads("""
{
    "time": 1746000000,
    "states": [
        [
            "a1b2c3",
            "UAL123  ",
            "United States",
            1746000000,
            1746000000,
            -122.4,
            37.6,
            2591.0,
            false,
            220.0,
            180.0,
            null,
            null,
            2591.0,
            "0000",
            false,
            0
        ]
    ]
}
""")


@pytest.fixture
def plugin():
    return AirportBoardPlugin(MANIFEST)


@pytest.fixture
def configured_plugin():
    p = AirportBoardPlugin(MANIFEST)
    p.config = json.loads("""
{
    "latitude": 37.6213,
    "longitude": -122.379,
    "radius_deg": 1.0,
    "airport_name": "SFO"
}
""")
    return p


class TestAirportBoardPlugin:

    def test_plugin_id(self, plugin):
        assert plugin.plugin_id == "airport_board"

    def test_manifest_valid(self):
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        with open(manifest_path) as f:
            m = json.load(f)
        for field in ("id", "name", "version"):
            assert field in m

    @patch("plugins.airport_board.requests.get")
    def test_fetch_data_success(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.error is None
        assert result.data is not None
        assert "airport" in result.data, "missing variable: airport"
        assert "flight_count" in result.data, "missing variable: flight_count"
        assert "callsign" in result.data, "missing variable: callsign"
        assert "altitude_ft" in result.data, "missing variable: altitude_ft"
        assert "origin_country" in result.data, "missing variable: origin_country"

    @patch("plugins.airport_board.requests.get")
    def test_fetch_data_network_error(self, mock_get, configured_plugin):
        import requests as req_mod
        mock_get.side_effect = req_mod.exceptions.ConnectionError("network down")

        result = configured_plugin.fetch_data()

        assert result.available is False
        assert result.error is not None

    @patch("plugins.airport_board.requests.get")
    def test_fetch_data_bad_json(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("bad json")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is False

