"""Display live flight information near a configurable airport."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
import requests

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

API_URL = "https://opensky-network.org/api/states/all"
USER_AGENT = "FiestaBoard Airport Board Plugin (https://github.com/Fiestaboard/fiestaboard-plugin--airport-board)"


class AirportBoardPlugin(PluginBase):
    """Airport Board plugin for FiestaBoard."""

    @property
    def plugin_id(self) -> str:
        return "airport_board"

    def fetch_data(self) -> PluginResult:
        try:
            lat = float(self.config.get("latitude") or 37.6213)
            lon = float(self.config.get("longitude") or -122.379)
            radius = float(self.config.get("radius_deg") or 1.0)
            airport_name = str(self.config.get("airport_name") or "SFO")[:10]

            response = requests.get(
                API_URL,
                params={
                    "lamin": lat - radius,
                    "lamax": lat + radius,
                    "lomin": lon - radius,
                    "lomax": lon + radius,
                },
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            states = data.get("states") or []
            flight_count = len(states)

            if not states:
                return PluginResult(
                    available=True,
                    data={
                        "airport": airport_name,
                        "flight_count": 0,
                        "callsign": "None",
                        "altitude_ft": 0,
                        "origin_country": "",
                    },
                )

            # Pick the first state (OpenSky doesn't sort by distance)
            first = states[0]
            callsign = str(first[1] or "").strip()[:10]
            origin_country = str(first[2] or "")[:15]
            # Index 13 = geo_altitude in meters
            alt_m = first[13] if first[13] is not None else 0
            altitude_ft = round(float(alt_m) * 3.28084)

            return PluginResult(
                available=True,
                data={
                    "airport": airport_name,
                    "flight_count": flight_count,
                    "callsign": callsign,
                    "altitude_ft": altitude_ft,
                    "origin_country": origin_country,
                },
            )
        except Exception as e:
            logger.exception("Error fetching airport board data")
            return PluginResult(available=False, error=str(e))

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        if config.get("latitude") is None:
            errors.append("latitude is required")
        if config.get("longitude") is None:
            errors.append("longitude is required")
        return errors

    def cleanup(self) -> None:
        pass
